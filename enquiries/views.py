import logging
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, TemplateView
from products.models import Product
from .forms import GeneralEnquiryForm, ProductEnquiryForm

logger = logging.getLogger('enquiries')


def _admin_recipient_list():
    admin_email = getattr(settings, 'ADMIN_NOTIFICATION_EMAIL', '')
    if admin_email:
        return [admin_email]
    if getattr(settings, 'ADMINS', None):
        return [email for _, email in settings.ADMINS]
    return []


def _send_enquiry_email(subject, body):
    recipients = _admin_recipient_list()
    if not recipients:
        return

    send_mail(
        subject=subject,
        message=body,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@shivshaktitraders.com'),
        recipient_list=recipients,
        fail_silently=True,
    )


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

        selected_products = ', '.join(form.instance.products.values_list('name', flat=True)) or 'None selected'
        _send_enquiry_email(
            subject='New General Enquiry Submitted',
            body=(
                f'Time: {timezone.now()}\n'
                f'Name: {form.instance.name}\n'
                f'Email: {form.instance.email}\n'
                f'Phone: {form.instance.phone or "N/A"}\n'
                f'Products: {selected_products}\n\n'
                f'Message:\n{form.instance.message}'
            ),
        )
        logger.info('General enquiry submitted by %s (%s)', form.instance.name, form.instance.email)
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

        _send_enquiry_email(
            subject=f'New Product Enquiry: {self.product.name}',
            body=(
                f'Time: {timezone.now()}\n'
                f'Product: {self.product.name}\n'
                f'Name: {form.instance.name}\n'
                f'Email: {form.instance.email}\n'
                f'Phone: {form.instance.phone or "N/A"}\n\n'
                f'Message:\n{form.instance.message}'
            ),
        )
        logger.info('Product enquiry submitted for %s by %s', self.product.slug, form.instance.email)
        messages.success(self.request, f'Product enquiry for {self.product.name} submitted successfully.')

        next_url = self.request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return response


class EnquirySuccessView(TemplateView):
    template_name = 'enquiries/enquiry_success.html'
