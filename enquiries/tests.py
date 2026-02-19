from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache
from products.models import Product, ProductCategory
from .models import GeneralEnquiry, ProductEnquiry


class EnquiryViewTests(TestCase):
    def setUp(self):
        cache.clear()
        self.category = ProductCategory.objects.create(name='Chemical', slug='chemical')
        self.product = Product.objects.create(
            name='Product A',
            slug='product-a',
            category=self.category,
            short_description='Short',
            full_description='Full',
            uses='Uses',
            is_active=True,
        )

    def test_general_contact_page_renders(self):
        response = self.client.get(reverse('enquiries:enquiry'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'enquiries/enquiry.html')

    def test_general_enquiry_post_creates_record(self):
        response = self.client.post(
            reverse('enquiries:enquiry'),
            {
                'products': [self.product.id],
                'name': 'Rahul',
                'email': 'rahul@example.com',
                'phone': '1234567890',
                'message': 'Need pricing details for selected products',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(GeneralEnquiry.objects.count(), 1)
        self.assertEqual(GeneralEnquiry.objects.first().products.count(), 1)
        self.assertTemplateUsed(response, 'enquiries/enquiry_success.html')

    def test_product_enquiry_post_creates_record(self):
        response = self.client.post(
            reverse('enquiries:product_enquiry', kwargs={'slug': self.product.slug}),
            {
                'name': 'Amit',
                'email': 'amit@example.com',
                'phone': '9876543210',
                'message': 'Need bulk quantity price and lead time',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductEnquiry.objects.count(), 1)
        self.assertEqual(ProductEnquiry.objects.first().product, self.product)
        self.assertTemplateUsed(response, 'enquiries/enquiry_success.html')

    def test_product_enquiry_requires_valid_message(self):
        response = self.client.post(
            reverse('enquiries:product_enquiry', kwargs={'slug': self.product.slug}),
            {
                'name': 'Amit',
                'email': 'amit@example.com',
                'phone': '9876543210',
                'message': 'short',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertIn('message', response.context['form'].errors)

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        ADMIN_NOTIFICATION_EMAIL='admin@example.com',
    )
    def test_general_enquiry_sends_admin_email_notification(self):
        from django.core import mail

        self.client.post(
            reverse('enquiries:enquiry'),
            {
                'products': [self.product.id],
                'name': 'Rahul',
                'email': 'rahul@example.com',
                'phone': '1234567890',
                'message': 'Need pricing details for selected products',
            },
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('New General Enquiry Submitted', mail.outbox[0].subject)

    @override_settings(ENQUIRY_RATE_LIMIT_MAX_REQUESTS=1, ENQUIRY_RATE_LIMIT_WINDOW_SECONDS=300)
    def test_rate_limit_blocks_second_submission(self):
        payload = {
            'products': [self.product.id],
            'name': 'Rahul',
            'email': 'rahul@example.com',
            'phone': '1234567890',
            'message': 'Need pricing details for selected products',
        }

        first = self.client.post(reverse('enquiries:enquiry'), payload)
        self.assertEqual(first.status_code, 302)

        second = self.client.post(reverse('enquiries:enquiry'), payload)
        self.assertEqual(second.status_code, 200)
        self.assertContains(second, 'Too many requests. Please wait and try again later.')
