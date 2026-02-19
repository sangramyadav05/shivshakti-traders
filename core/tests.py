from django.test import TestCase
from django.urls import reverse
from products.models import Product, ProductCategory


class CoreViewTests(TestCase):
    def test_home_page_renders(self):
        category = ProductCategory.objects.create(name='Chemical', slug='chemical')
        Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=category,
            short_description='Short description',
            full_description='Full description',
            uses='Use case',
            is_active=True,
        )
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')
        self.assertContains(response, 'Test Product')

    def test_about_page_renders(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/about.html')

    def test_contact_page_renders(self):
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/contact.html')

    def test_robots_txt_renders(self):
        response = self.client.get(reverse('robots_txt'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sitemap:')

    def test_sitemap_xml_renders(self):
        response = self.client.get(reverse('sitemap'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<urlset')
