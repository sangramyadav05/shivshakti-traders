from collections import defaultdict
from datetime import datetime

from django import forms
from django.contrib import messages
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import FormView, TemplateView

from enquiries.models import GeneralEnquiry, ProductEnquiry
from products.models import Product

from .decorators import DASHBOARD_SESSION_KEY, dashboard_login_required, dashboard_no_cache
from .models import DashboardUser


class DashboardLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        css = (
            'w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 '
            'text-slate-800 focus:border-sky-500 focus:outline-none focus:ring-2 '
            'focus:ring-sky-200'
        )
        for field in self.fields.values():
            field.widget.attrs['class'] = css


@method_decorator(dashboard_no_cache, name='dispatch')
class DashboardLoginView(FormView):
    template_name = 'dashboard/login.html'
    form_class = DashboardLoginForm
    success_url = reverse_lazy('dashboard:dashboard_home')

    def dispatch(self, request, *args, **kwargs):
        if request.session.get(DASHBOARD_SESSION_KEY):
            return redirect('dashboard:dashboard_home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        username = form.cleaned_data['username'].strip()
        password = form.cleaned_data['password']

        dashboard_user = DashboardUser.objects.filter(username=username, is_active=True).first()
        if dashboard_user is None or not dashboard_user.check_password(password):
            form.add_error(None, 'Invalid username or password.')
            return self.form_invalid(form)

        self.request.session.cycle_key()
        self.request.session[DASHBOARD_SESSION_KEY] = dashboard_user.id
        messages.success(self.request, 'Dashboard login successful.')
        return super().form_valid(form)


@method_decorator(dashboard_no_cache, name='dispatch')
@method_decorator(dashboard_login_required, name='dispatch')
class DashboardHomeView(TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_products = Product.objects.count()
        total_general_enquiries = GeneralEnquiry.objects.count()
        total_product_enquiries = ProductEnquiry.objects.count()
        total_enquiries = total_general_enquiries + total_product_enquiries

        recent_general = list(
            GeneralEnquiry.objects.values('name', 'email', 'resolved', 'created_at')
            .order_by('-created_at')[:5]
        )
        for item in recent_general:
            item['enquiry_type'] = 'General'
            item['product_name'] = '-'

        recent_product = list(
            ProductEnquiry.objects.values('name', 'email', 'resolved', 'created_at', 'product__name')
            .order_by('-created_at')[:5]
        )
        for item in recent_product:
            item['enquiry_type'] = 'Product'
            item['product_name'] = item.pop('product__name')

        recent_enquiries = sorted(
            recent_general + recent_product,
            key=lambda entry: entry['created_at'],
            reverse=True,
        )[:5]

        enquiries_per_product = list(
            ProductEnquiry.objects.values('product__name')
            .annotate(total=Count('id'))
            .order_by('-total', 'product__name')
        )

        month_totals = defaultdict(int)

        general_by_month = (
            GeneralEnquiry.objects.annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Count('id'))
        )
        for row in general_by_month:
            if row['month']:
                month_totals[row['month']] += row['total']

        product_by_month = (
            ProductEnquiry.objects.annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Count('id'))
        )
        for row in product_by_month:
            if row['month']:
                month_totals[row['month']] += row['total']

        enquiries_per_month = [
            {'month': datetime(month.year, month.month, 1), 'total': total}
            for month, total in sorted(month_totals.items())
        ]

        context.update(
            {
                'dashboard_user': getattr(self.request, 'dashboard_user', None),
                'sidebar_active': 'overview',
                'total_products': total_products,
                'total_enquiries': total_enquiries,
                'total_general_enquiries': total_general_enquiries,
                'total_product_enquiries': total_product_enquiries,
                'recent_enquiries': recent_enquiries,
                'enquiries_per_product': enquiries_per_product,
                'enquiries_per_month': enquiries_per_month,
            }
        )
        return context


@method_decorator(dashboard_no_cache, name='dispatch')
@method_decorator(dashboard_login_required, name='dispatch')
class DashboardProductsView(TemplateView):
    template_name = 'dashboard/products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.select_related('category').order_by('name')
        context.update(
            {
                'dashboard_user': getattr(self.request, 'dashboard_user', None),
                'sidebar_active': 'products',
                'products': products,
                'total_products': products.count(),
                'featured_products': products.filter(is_featured=True).count(),
                'active_products': products.filter(is_active=True).count(),
            }
        )
        return context


@method_decorator(dashboard_no_cache, name='dispatch')
@method_decorator(dashboard_login_required, name='dispatch')
class DashboardEnquiriesView(TemplateView):
    template_name = 'dashboard/enquiries.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        general_enquiries = GeneralEnquiry.objects.order_by('-created_at')
        product_enquiries = ProductEnquiry.objects.select_related('product').order_by('-created_at')
        context.update(
            {
                'dashboard_user': getattr(self.request, 'dashboard_user', None),
                'sidebar_active': 'enquiries',
                'general_enquiries': general_enquiries[:25],
                'product_enquiries': product_enquiries[:25],
                'total_general_enquiries': general_enquiries.count(),
                'total_product_enquiries': product_enquiries.count(),
                'total_open_enquiries': general_enquiries.filter(resolved=False).count()
                + product_enquiries.filter(resolved=False).count(),
            }
        )
        return context


@method_decorator(dashboard_no_cache, name='dispatch')
class DashboardLogoutView(View):
    def get(self, request, *args, **kwargs):
        return self._logout(request)

    def post(self, request, *args, **kwargs):
        return self._logout(request)

    def _logout(self, request):
        request.session.pop(DASHBOARD_SESSION_KEY, None)
        request.session.cycle_key()
        messages.warning(request, 'Please login again to access dashboard.')
        return redirect('dashboard:dashboard_login')
