from django.conf import settings
from django.db.models import Q
from django.views.generic import DetailView, ListView
from enquiries.forms import ProductEnquiryForm
from .models import Product, ProductCategory


class ProductListView(ListView):
    model = Product
    template_name = 'products/products.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category')
        category_slug = self.request.GET.get('category', '').strip()
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q)
                | Q(short_description__icontains=q)
                | Q(full_description__icontains=q)
                | Q(uses__icontains=q)
            )

        ordering = self.request.GET.get('ordering', 'name')
        allowed = {'name', '-name', 'created_at', '-created_at'}
        if ordering not in allowed:
            ordering = 'name'
        return queryset.order_by(ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProductCategory.objects.order_by('name')
        context['current_category'] = self.request.GET.get('category', '').strip()
        context['current_q'] = self.request.GET.get('q', '').strip()
        context['current_ordering'] = self.request.GET.get('ordering', 'name')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_enquiry_form'] = ProductEnquiryForm(initial={'request_obj': self.request})
        context['recaptcha_enabled'] = settings.RECAPTCHA_ENABLED
        context['recaptcha_site_key'] = settings.RECAPTCHA_SITE_KEY
        return context
