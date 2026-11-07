from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import FarmProfile

User = get_user_model()


class DashboardTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ibrahim', password='S3cur3Pass!')
        self.client.login(username='ibrahim', password='S3cur3Pass!')

    def test_dashboard_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_page_loads_after_login(self):
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)

    def test_module_pages_create_farm_profile_when_missing(self):
        user = User.objects.create_user(username='newfarmer', password='S3cur3Pass!')
        self.client.login(username='newfarmer', password='S3cur3Pass!')

        response = self.client.get(reverse('parcelles:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(FarmProfile.objects.filter(user=user).exists())
