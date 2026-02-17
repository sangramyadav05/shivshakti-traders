from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView


def _apply_auth_widget_classes(form):
    css = 'w-full rounded-lg border border-slate-300 bg-slate-50 px-3 py-2.5 text-slate-800 focus:border-brand-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-300/40'
    for field in form.fields.values():
        existing = field.widget.attrs.get('class', '')
        field.widget.attrs['class'] = f'{existing} {css}'.strip()
    return form


class LoginRateLimitMixin:
    rate_limit_scope = 'login'

    def _client_ip(self):
        forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR', '')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return self.request.META.get('REMOTE_ADDR', 'unknown')

    def _rate_limit_key(self):
        return f'{self.rate_limit_scope}:{self._client_ip()}'

    def is_rate_limited(self):
        if settings.DEBUG:
            return False
        return cache.get(self._rate_limit_key(), 0) >= settings.LOGIN_RATE_LIMIT_MAX_ATTEMPTS

    def bump_rate_limit(self):
        if settings.DEBUG:
            return
        key = self._rate_limit_key()
        timeout = settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS
        if cache.get(key) is None:
            cache.set(key, 1, timeout=timeout)
        else:
            try:
                cache.incr(key)
            except ValueError:
                cache.set(key, 1, timeout=timeout)

    def clear_rate_limit(self):
        cache.delete(self._rate_limit_key())


class AccountLoginView(LoginRateLimitMixin, LoginView):
    template_name = 'accounts/login.html'
    next_page = reverse_lazy('core:home')
    rate_limit_scope = 'account-login'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return _apply_auth_widget_classes(form)

    def form_valid(self, form):
        self.clear_rate_limit()
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.is_rate_limited():
            messages.error(self.request, 'Too many login attempts. Please wait and try again.')
            return self.render_to_response(self.get_context_data(form=form))
        self.bump_rate_limit()
        return super().form_invalid(form)


class AccountLogoutView(LogoutView):
    next_page = reverse_lazy('core:home')


class AccountDashboardView(TemplateView):
    template_name = 'accounts/dashboard.html'


class StaffAdminLoginView(LoginRateLimitMixin, FormView):
    template_name = 'accounts/admin_login.html'
    form_class = AuthenticationForm
    rate_limit_scope = 'admin-login'

    def get_success_url(self):
        return reverse('admin:index')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return _apply_auth_widget_classes(form)

    def form_valid(self, form):
        if self.is_rate_limited():
            messages.error(self.request, 'Too many login attempts. Please wait and try again.')
            return self.form_invalid(form)

        user = form.get_user()
        if not user.is_staff:
            self.bump_rate_limit()
            return HttpResponseForbidden('Only staff users can access admin.')

        login(self.request, user)
        self.clear_rate_limit()
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        if not self.is_rate_limited():
            self.bump_rate_limit()
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['admin_url'] = '/' + settings.ADMIN_URL.lstrip('/')
        return context
