from django.test import TestCase
from django.urls import reverse
from .models import Product, ProductCategory


class ProductViewTests(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(name='Chemical', slug='chemical')
        self.active_product = Product.objects.create(
            name='Active Product',
            slug='active-product',
            category=self.category,
            short_description='Active short',
            full_description='Active full description',
            uses='Active uses',
            is_active=True,
        )
        Product.objects.create(
            name='Inactive Product',
            slug='inactive-product',
            category=self.category,
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

    def test_product_list_search_filters_results(self):
        response = self.client.get(reverse('products:product_list'), {'q': 'Active'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Active Product')
        self.assertNotContains(response, 'Inactive Product')

    def test_product_list_ordering_desc(self):
        Product.objects.create(
            name='Zulu Product',
            slug='zulu-product',
            category=self.category,
            short_description='zulu short',
            full_description='zulu full',
            uses='zulu uses',
            is_active=True,
        )
        response = self.client.get(reverse('products:product_list'), {'ordering': '-name'})
        self.assertEqual(response.status_code, 200)
        products = list(response.context['products'])
        self.assertEqual(products[0].name, 'Zulu Product')
