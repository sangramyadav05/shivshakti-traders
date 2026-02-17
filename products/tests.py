from django.test import TestCase
from django.urls import reverse
from .models import Product


class ProductViewTests(TestCase):
    def setUp(self):
        self.active_product = Product.objects.create(
            name='Active Product',
            slug='active-product',
            short_description='Active short',
            full_description='Active full description',
            uses='Active uses',
            is_active=True,
        )
        Product.objects.create(
            name='Inactive Product',
            slug='inactive-product',
            short_description='Inactive short',
            full_description='Inactive full description',
            uses='Inactive uses',
            is_active=False,
        )

    def test_product_list_shows_only_active_products(self):
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Active Product')
        self.assertNotContains(response, 'Inactive Product')

    def test_product_detail_by_slug(self):
        response = self.client.get(reverse('products:product_detail', kwargs={'slug': self.active_product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Active full description')
        self.assertContains(response, 'Product Specific Enquiry')

    def test_get_absolute_url(self):
        self.assertEqual(self.active_product.get_absolute_url(), '/products/active-product/')
