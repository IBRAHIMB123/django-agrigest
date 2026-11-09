from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import FarmProfile


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

    def test_signup_creates_separate_farms_for_selected_roles(self):
        first_response = self.client.post(reverse('accounts:signup'), {
            'username': 'farmer-one',
            'email': 'farmer-one@example.test',
            'first_name': 'Aminata',
            'last_name': 'Traore',
            'farm_name': 'Ferme Aminata',
            'farm_location': 'Sikasso',
            'role': FarmProfile.ROLE_WORKER,
            'password1': 'Aminata-farm-2026!strong',
            'password2': 'Aminata-farm-2026!strong',
        })

        self.assertRedirects(first_response, reverse('dashboard:index'))
        first_user = get_user_model().objects.get(username='farmer-one')
        first_farm = FarmProfile.objects.get(user=first_user)
        self.assertEqual(first_farm.name, 'Ferme Aminata')
        self.assertEqual(first_farm.role, FarmProfile.ROLE_WORKER)

        self.client.logout()
        second_response = self.client.post(reverse('accounts:signup'), {
            'username': 'farmer-two',
            'email': 'farmer-two@example.test',
            'first_name': 'Moussa',
            'last_name': 'Diallo',
            'farm_name': 'Ferme Moussa',
            'farm_location': 'Segou',
            'role': FarmProfile.ROLE_CLIENT,
            'password1': 'Moussa-farm-2026!strong',
            'password2': 'Moussa-farm-2026!strong',
        })

        self.assertRedirects(second_response, reverse('dashboard:index'))
        second_user = get_user_model().objects.get(username='farmer-two')
        second_farm = FarmProfile.objects.get(user=second_user)
        self.assertEqual(second_farm.name, 'Ferme Moussa')
        self.assertEqual(second_farm.role, FarmProfile.ROLE_CLIENT)
        self.assertNotEqual(first_farm.pk, second_farm.pk)

        farms_response = self.client.get(reverse('accounts:farms'))
        self.assertEqual(list(farms_response.context['farms']), [second_farm])

        self.client.login(username='logout-user', password='StrongPass123!')
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:login'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
