from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AccountViewTests(TestCase):
    def test_login_page_renders(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_custom_admin_login_page_renders(self):
        response = self.client.get(reverse('custom_admin_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/admin_login.html')

    def test_custom_admin_login_rejects_non_staff(self):
        User = get_user_model()
        User.objects.create_user(username='user1', password='pass123456')
        response = self.client.post(
            reverse('custom_admin_login'),
            {'username': 'user1', 'password': 'pass123456'},
        )
        self.assertEqual(response.status_code, 403)
