from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from enquiries.models import ProductEnquiry
from products.models import Product


class ProductApiTests(TestCase):
    def setUp(self):
        self.active = Product.objects.create(
            name='Filter Product',
            slug='filter-product',
            short_description='Filter short',
            full_description='Filter full',
            uses='Filter uses',
            is_active=True,
        )
        Product.objects.create(
            name='Hidden Product',
            slug='hidden-product',
            short_description='Hidden short',
            full_description='Hidden full',
            uses='Hidden uses',
            is_active=False,
        )
        self.user = get_user_model().objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='StrongPass123!',
        )

    def test_product_list_api_returns_active_only(self):
        response = self.client.get(reverse('api:product-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Filter Product')
        self.assertNotContains(response, 'Hidden Product')

    def test_product_list_api_search(self):
        response = self.client.get(reverse('api:product-list'), {'q': 'Filter'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Filter Product')

    def test_product_detail_api_by_slug(self):
        response = self.client.get(reverse('api:product-detail', kwargs={'slug': self.active.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['slug'], 'filter-product')

    def test_product_enquiry_create_api_requires_jwt(self):
        payload = {
            'product': self.active.slug,
            'name': 'API User',
            'email': 'api@example.com',
            'phone': '9999999999',
            'message': 'Need product details and supply timeline.',
        }
        response = self.client.post(reverse('api:product-enquiry-create'), data=payload)
        self.assertEqual(response.status_code, 401)

    def test_product_enquiry_create_api_with_jwt(self):
        token_response = self.client.post(
            reverse('api:token_obtain_pair'),
            data={'username': 'apiuser', 'password': 'StrongPass123!'},
        )
        self.assertEqual(token_response.status_code, 200)
        access = token_response.json()['access']

        payload = {
            'product': self.active.slug,
            'name': 'API User',
            'email': 'api@example.com',
            'phone': '9999999999',
            'message': 'Need product details and supply timeline.',
        }
        response = self.client.post(
            reverse('api:product-enquiry-create'),
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access}',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProductEnquiry.objects.count(), 1)
        self.assertEqual(ProductEnquiry.objects.first().product.slug, self.active.slug)
