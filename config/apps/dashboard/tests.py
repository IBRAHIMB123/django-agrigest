from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import FarmProfile, get_or_create_farm_profile

User = get_user_model()


class DashboardTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ibrahim', password='S3cur3Pass!')
        self.client.login(username='ibrahim', password='S3cur3Pass!')

    def test_homepage_is_public_and_links_to_signup_and_login(self):
        self.client.logout()
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing.html')
        self.assertContains(response, reverse('accounts:signup'))
        self.assertContains(response, reverse('accounts:login'))
        self.assertContains(response, 'href="#acces"')
        self.assertContains(response, 'id="acces"')
        self.assertContains(response, 'Ouvrir mon dashboard')
        self.assertContains(response, 'id="approche"')
        self.assertContains(response, 'id="solutions"')
        self.assertContains(response, 'id="parcours"')

    def test_homepage_shows_landing_page_even_when_authenticated(self):
        response = self.client.get(reverse('dashboard:home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing.html')
        self.assertContains(response, reverse('dashboard:index'))
        self.assertContains(response, 'Ouvrir mon dashboard')
        self.assertContains(response, 'href="/dashboard/"')

    def test_dashboard_page_loads_after_login(self):
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

    def test_dashboard_interface_matches_each_role(self):
        farm = get_or_create_farm_profile(self.user)
        role_interfaces = (
            (FarmProfile.ROLE_ADMIN, 'dashboard/roles/admin.html', 'Résultat estimé'),
            (FarmProfile.ROLE_WORKER, 'dashboard/roles/worker.html', 'Interventions en cours'),
            (FarmProfile.ROLE_CLIENT, 'dashboard/roles/client.html', 'Mes commandes récentes'),
        )

        for role, template, heading in role_interfaces:
            with self.subTest(role=role):
                farm.role = role
                farm.save(update_fields=['role'])

                response = self.client.get(reverse('dashboard:index'))

                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, template)
                self.assertContains(response, heading)

    def test_role_dashboard_routes_reject_other_roles(self):
        response = self.client.get(reverse('dashboard:terrain'))

        self.assertRedirects(response, reverse('dashboard:index'))

    def test_worker_dashboard_shows_operational_navigation_only(self):
        farm = get_or_create_farm_profile(self.user)
        farm.role = FarmProfile.ROLE_WORKER
        farm.save(update_fields=['role'])

        response = self.client.get(reverse('dashboard:index'))

        self.assertContains(response, 'Intrants et stock')
        self.assertNotContains(response, 'Dépenses')
        self.assertNotContains(response, 'Ventes')

    def test_client_dashboard_shows_client_navigation_only(self):
        farm = get_or_create_farm_profile(self.user)
        farm.role = FarmProfile.ROLE_CLIENT
        farm.save(update_fields=['role'])

        response = self.client.get(reverse('dashboard:index'))

        self.assertContains(response, 'Boutique agricole')
        self.assertContains(response, 'Mes commandes')
        self.assertNotContains(response, 'Rapports')
        self.assertNotContains(response, f'href="{reverse("parcelles:list")}"')
        self.assertNotContains(response, f'href="{reverse("depenses:list")}"')

    def test_module_pages_create_farm_profile_when_missing(self):
        user = User.objects.create_user(username='newfarmer', password='S3cur3Pass!')
        self.client.login(username='newfarmer', password='S3cur3Pass!')

        response = self.client.get(reverse('parcelles:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(FarmProfile.objects.filter(user=user).exists())
