from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import FarmProfile
from apps.parcelles.models import Parcelle

User = get_user_model()


class ParcelleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ibrahim', password='TestPass123!')
        self.farm = FarmProfile.objects.create(user=self.user, name='Exploitation Test')
        self.client.login(username='ibrahim', password='TestPass123!')

    def test_parcelle_list_page(self):
        Parcelle.objects.create(farm=self.farm, name='Nord', location='Bouaké', area=12.5, status='active')
        response = self.client.get(reverse('parcelles:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nord')
