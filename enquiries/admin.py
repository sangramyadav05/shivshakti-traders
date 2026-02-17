from django.contrib import admin
from .models import GeneralEnquiry, ProductEnquiry


@admin.register(GeneralEnquiry)
class GeneralEnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'resolved', 'created_at')
    list_filter = ('resolved', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message')
    date_hierarchy = 'created_at'
    filter_horizontal = ('products',)


@admin.register(ProductEnquiry)
class ProductEnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'product', 'resolved', 'created_at')
    list_filter = ('resolved', 'created_at', 'product')
    search_fields = ('name', 'email', 'phone', 'message', 'product__name')
    date_hierarchy = 'created_at'
