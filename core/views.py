from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from products.models import Product


class HomePageView(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        featured_slugs = [
            'bleaching-powder-25kg-packaging',
            'medicore-m-100ml-bottle',
            'sodium-hypochlorite-liquid-chemical-can',
        ]
        products_by_slug = {
            product.slug: product
            for product in Product.objects.filter(is_active=True, slug__in=featured_slugs)
        }
        context['featured_products'] = [
            products_by_slug[slug] for slug in featured_slugs if slug in products_by_slug
        ]
        return context


class AboutPageView(TemplateView):
    template_name = 'core/about.html'


class ContactPageView(TemplateView):
    template_name = 'core/contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_phone'] = '+91-90000-00000'
        context['contact_email'] = 'info@shivshaktitraders.com'
        context['contact_address'] = 'Pune, Maharashtra'
        context['map_embed_url'] = (
            'https://www.google.com/maps/embed?pb='
            '!1m18!1m12!1m3!1d13352.995528094265!2d73.86131251258942!3d18.301449336281188!'
            '2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!'
            '1s0x3bc2f29ffb4e2b07%3A0x5327723760e91d31!2sVarve%20Bk%2C%20Varve%20Budruk%'
            '2C%20Maharashtra%20412205!5e0!3m2!1sen!2sin!4v1771267612508!5m2!1sen!2sin'
        )
        return context


class RobotsTxtView(TemplateView):
    template_name = 'robots.txt'
    content_type = 'text/plain'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sitemap_url'] = self.request.build_absolute_uri(reverse('sitemap'))
        return context


def custom_404_view(request, exception):
    return render(request, 'errors/404.html', status=404)


def custom_500_view(request):
    return render(request, 'errors/500.html', status=500)
