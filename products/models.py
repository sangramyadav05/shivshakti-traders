from django.db import models
from django.urls import reverse
from .validators import image_extension_validator, validate_image_size


class Product(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    short_description = models.CharField(max_length=220)
    full_description = models.TextField()
    uses = models.TextField(help_text='Describe usage and application details for this product.')
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        validators=[image_extension_validator, validate_image_size],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})

