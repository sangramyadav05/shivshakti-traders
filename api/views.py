from django.db.models import Q
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

from products.models import Product
from .serializers import ProductEnquirySerializer, ProductSerializer


@extend_schema(
    summary='List products',
    description='Public endpoint returning active products with optional search and ordering.',
    parameters=[
        OpenApiParameter(name='q', description='Search term', required=False, type=str),
        OpenApiParameter(name='category', description='Category slug filter', required=False, type=str),
        OpenApiParameter(name='ordering', description='name, -name, created_at, -created_at', required=False, type=str),
    ],
)
class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'products'

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category')
        category_slug = self.request.query_params.get('category', '').strip()
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        q = self.request.query_params.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q)
                | Q(short_description__icontains=q)
                | Q(full_description__icontains=q)
                | Q(uses__icontains=q)
            )

        ordering = self.request.query_params.get('ordering', 'name')
        allowed = {'name', '-name', 'created_at', '-created_at'}
        if ordering not in allowed:
            ordering = 'name'
        return queryset.order_by(ordering)


@extend_schema(summary='Get product details', description='Public endpoint to fetch one active product by slug.')
class ProductDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'products'
    lookup_field = 'slug'
    queryset = Product.objects.filter(is_active=True).select_related('category')


@extend_schema(
    summary='Create product enquiry',
    description='Protected endpoint. Requires JWT Bearer token in Authorization header.',
    examples=[
        OpenApiExample(
            'Enquiry payload',
            value={
                'product': 'bleaching-powder-25kg-packaging',
                'name': 'John Doe',
                'email': 'john@example.com',
                'phone': '+919999999999',
                'message': 'Need wholesale rates and lead time for monthly supply.',
            },
            request_only=True,
        )
    ],
)
class ProductEnquiryCreateAPIView(generics.CreateAPIView):
    serializer_class = ProductEnquirySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = 'enquiries'
