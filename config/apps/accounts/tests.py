from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AccountsAuthTests(TestCase):
    def test_login_page_loads(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_logout_redirects_user_to_login(self):
        user = get_user_model().objects.create_user(username='logout-user', password='StrongPass123!')
        self.client.login(username='logout-user', password='StrongPass123!')

        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:login'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        self.client.login(username='logout-user', password='StrongPass123!')
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:login'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
