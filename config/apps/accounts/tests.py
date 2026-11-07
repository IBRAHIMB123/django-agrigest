from django.test import TestCase
from django.urls import reverse


class AccountsAuthTests(TestCase):
    def test_login_page_loads(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
