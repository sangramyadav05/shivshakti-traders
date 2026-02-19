from django.contrib import admin

from .models import GeneralEnquiry, ProductEnquiry


@admin.action(description='Mark selected enquiries as resolved')
def mark_resolved(modeladmin, request, queryset):
    queryset.update(resolved=True)


@admin.register(GeneralEnquiry)
class GeneralEnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'resolved', 'created_at')
    list_filter = ('resolved', ('created_at', admin.DateFieldListFilter))
    search_fields = ('name', 'email', 'phone')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    filter_horizontal = ('products',)
    actions = (mark_resolved,)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Enquiry Details', {
            'fields': ('products', 'name', 'email', 'phone', 'message', 'resolved'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(ProductEnquiry)
class ProductEnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'product', 'resolved', 'created_at')
    list_filter = ('resolved', ('created_at', admin.DateFieldListFilter), 'product')
    search_fields = ('name', 'email', 'phone', 'product__name')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    actions = (mark_resolved,)
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('product',)

    fieldsets = (
        ('Enquiry Details', {
            'fields': ('product', 'name', 'email', 'phone', 'message', 'resolved'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
