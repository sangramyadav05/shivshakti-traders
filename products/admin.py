from django.contrib import admin
from django.utils.html import format_html

from .models import Product


admin.site.site_header = 'Shivshakti Traders Control Panel'
admin.site.site_title = 'Shivshakti Traders Admin'
admin.site.index_title = 'Administration Dashboard'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'slug', 'is_active', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'slug', 'short_description', 'full_description', 'uses')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
    readonly_fields = ('image_preview', 'created_at', 'updated_at')

    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'slug', 'is_active'),
        }),
        ('Media', {
            'fields': ('image', 'image_preview'),
        }),
        ('Content', {
            'fields': ('short_description', 'full_description', 'uses'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    @admin.display(description='Image')
    def image_preview(self, obj):
        if not obj.pk or not obj.image:
            return '-'
        return format_html(
            '<img src="{}" alt="{}" style="width:56px;height:56px;object-fit:cover;border-radius:6px;" />',
            obj.image.url,
            obj.name,
        )
