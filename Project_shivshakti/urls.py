from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import Http404
from django.urls import include, path

from accounts.views import StaffAdminLoginView
from core.sitemaps import ProductSitemap, StaticViewSitemap
from core.views import RobotsTxtView, custom_404_view, custom_500_view


sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
}

handler404 = 'core.views.custom_404_view'
handler500 = 'core.views.custom_500_view'


def hidden_admin_view(request, *args, **kwargs):
    raise Http404('Not found')


admin_url = settings.ADMIN_URL.lstrip('/')
if not admin_url.endswith('/'):
    admin_url = f'{admin_url}/'

urlpatterns = [
    path('admin/', hidden_admin_view, name='hidden_admin'),
    path(f'{admin_url}login/', StaffAdminLoginView.as_view(), name='hardened_admin_login'),
    path(settings.ADMIN_URL, admin.site.urls),
    path(settings.ADMIN_LOGIN_URL, StaffAdminLoginView.as_view(), name='custom_admin_login'),
    path('api/', include('api.urls')),
    path('', include('core.urls')),
    path('products/', include('products.urls')),
    path('enquiries/', include('enquiries.urls')),
    path('accounts/', include('accounts.urls')),
    path('business-dashboard/', include('dashboard.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', RobotsTxtView.as_view(), name='robots_txt'),
]

if settings.DEBUG or getattr(settings, 'SERVE_MEDIA', False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

