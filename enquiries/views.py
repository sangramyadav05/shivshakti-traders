import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from products.models import Product

from .forms import GeneralEnquiryForm, ProductEnquiryForm
from .services import queue_enquiry_notification

logger = logging.getLogger('enquiries')


class EnquiryRateLimitMixin:
    rate_limit_scope = 'enquiry'

    def _client_ip(self):
        forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR', '')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return self.request.META.get('REMOTE_ADDR', 'unknown')

    def _rate_limit_key(self):
        return f"{self.rate_limit_scope}:{self._client_ip()}"

    def is_rate_limited(self):
        if settings.DEBUG:
            return False
        key = self._rate_limit_key()
        count = cache.get(key, 0)
        return count >= settings.ENQUIRY_RATE_LIMIT_MAX_REQUESTS

    def bump_rate_limit(self):
        if settings.DEBUG:
            return
        key = self._rate_limit_key()
        timeout = settings.ENQUIRY_RATE_LIMIT_WINDOW_SECONDS
        if cache.get(key) is None:
            cache.set(key, 1, timeout=timeout)
        else:
            try:
                cache.incr(key)
            except ValueError:
                cache.set(key, 1, timeout=timeout)


class GeneralEnquiryCreateView(EnquiryRateLimitMixin, CreateView):
    form_class = GeneralEnquiryForm
    template_name = 'enquiries/enquiry.html'
    success_url = reverse_lazy('enquiries:enquiry_success')
    rate_limit_scope = 'general-enquiry'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.setdefault('initial', {})['request_obj'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recaptcha_enabled'] = settings.RECAPTCHA_ENABLED
        context['recaptcha_site_key'] = settings.RECAPTCHA_SITE_KEY
        return context

    def form_valid(self, form):
        if self.is_rate_limited():
            form.add_error(None, 'Too many requests. Please wait and try again later.')
            messages.error(self.request, 'Rate limit exceeded. Try again later.')
            return self.form_invalid(form)

        response = super().form_valid(form)
        self.bump_rate_limit()

        queue_enquiry_notification(form.instance)
        logger.info('General enquiry submitted and email task queued: %s', form.instance.id)
        messages.success(self.request, 'General enquiry submitted successfully.')
        return response


class ProductEnquiryCreateView(EnquiryRateLimitMixin, CreateView):
    form_class = ProductEnquiryForm
    template_name = 'enquiries/product_enquiry.html'
    success_url = reverse_lazy('enquiries:enquiry_success')
    rate_limit_scope = 'product-enquiry'

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, slug=kwargs['slug'], is_active=True)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.setdefault('initial', {})['request_obj'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        context['recaptcha_enabled'] = settings.RECAPTCHA_ENABLED
        context['recaptcha_site_key'] = settings.RECAPTCHA_SITE_KEY
        return context

    def form_valid(self, form):
        if self.is_rate_limited():
            form.add_error(None, 'Too many requests. Please wait and try again later.')
            messages.error(self.request, 'Rate limit exceeded. Try again later.')
            return self.form_invalid(form)

        form.instance.product = self.product
        response = super().form_valid(form)
        self.bump_rate_limit()

        queue_enquiry_notification(form.instance)
        logger.info('Product enquiry submitted and email task queued: %s', form.instance.id)
        messages.success(self.request, f'Product enquiry for {self.product.name} submitted successfully.')

        next_url = self.request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return response


class EnquirySuccessView(TemplateView):
    template_name = 'enquiries/enquiry_success.html'
