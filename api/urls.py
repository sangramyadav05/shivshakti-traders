from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import ProductDetailAPIView, ProductEnquiryCreateAPIView, ProductListAPIView

app_name = 'api'

urlpatterns = [
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('products/<slug:slug>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('enquiries/', ProductEnquiryCreateAPIView.as_view(), name='product-enquiry-create'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += [
        path('schema/', SpectacularAPIView.as_view(), name='schema'),
        path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger-ui'),
        path('redoc/', SpectacularRedocView.as_view(url_name='api:schema'), name='redoc'),
    ]
else:
    urlpatterns += [
        path('schema/', staff_member_required(SpectacularAPIView.as_view(), login_url='custom_admin_login'), name='schema'),
        path(
            'docs/',
            staff_member_required(SpectacularSwaggerView.as_view(url_name='api:schema'), login_url='custom_admin_login'),
            name='swagger-ui',
        ),
        path(
            'redoc/',
            staff_member_required(SpectacularRedocView.as_view(url_name='api:schema'), login_url='custom_admin_login'),
            name='redoc',
        ),
    ]
