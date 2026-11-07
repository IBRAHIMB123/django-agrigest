from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import FarmProfile

User = get_user_model()


class IntrantTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ibrahim', password='TestPass123!')
        self.farm = FarmProfile.objects.create(user=self.user, name='Exploitation Test')
        self.client.login(username='ibrahim', password='TestPass123!')

    def test_intrant_page_loads(self):
        response = self.client.get(reverse('intrants:list'))
        self.assertEqual(response.status_code, 200)
