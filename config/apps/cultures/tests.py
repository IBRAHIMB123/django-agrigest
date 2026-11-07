from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import FarmProfile
from apps.parcelles.models import Parcelle

User = get_user_model()


class CultureTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ibrahim', password='TestPass123!')
        self.farm = FarmProfile.objects.create(user=self.user, name='Exploitation Test')
        self.parcelle = Parcelle.objects.create(farm=self.farm, name='Parcelle Test', location='Bouaké', area=8.5)
        self.client.login(username='ibrahim', password='TestPass123!')

    def test_culture_list_page(self):
        response = self.client.get(reverse('cultures:list'))
        self.assertEqual(response.status_code, 200)
