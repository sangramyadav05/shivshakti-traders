from django.contrib import admin
from django.utils.html import format_html

from .models import Product, ProductCategory


admin.site.site_header = 'Shivshakti Traders Control Panel'
admin.site.site_title = 'Shivshakti Traders Admin'
admin.site.index_title = 'Administration Dashboard'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    ordering = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'category', 'is_featured', 'created_at')
    list_filter = ('category', 'is_featured', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
    list_editable = ('is_featured',)
    readonly_fields = ('image_preview', 'created_at', 'updated_at')

    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'slug', 'category', 'is_active', 'is_featured'),
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
