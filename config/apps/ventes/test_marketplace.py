from io import BytesIO
from tempfile import TemporaryDirectory
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.accounts.models import FarmProfile

from .models import HarvestListing, HarvestOrder

User = get_user_model()


class MarketplaceTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(username='seller', password='StrongPass123!')
        self.seller_farm = FarmProfile.objects.create(user=self.seller, name='Ferme A', location='Sikasso')
        self.other_seller = User.objects.create_user(username='other-seller', password='StrongPass123!')
        self.other_farm = FarmProfile.objects.create(user=self.other_seller, name='Ferme B')
        self.buyer = User.objects.create_user(username='buyer', password='StrongPass123!')
        self.buyer_farm = FarmProfile.objects.create(user=self.buyer, name='Compte client', role=FarmProfile.ROLE_CLIENT)
        self.other_buyer = User.objects.create_user(username='other-buyer', password='StrongPass123!')
        FarmProfile.objects.create(user=self.other_buyer, name='Autre client', role=FarmProfile.ROLE_CLIENT)

        self.listing = self.make_listing(self.seller_farm, title='Mangues', quantity='10.00', price='500.00')
        self.other_listing = self.make_listing(self.other_farm, title='Riz local', quantity='5.00', price='300.00')

    def make_listing(self, farm, title, quantity, price, fulfillment=HarvestListing.FULFILLMENT_PICKUP):
        return HarvestListing.objects.create(
            farm=farm,
            title=title,
            photo='marketplace/test.png',
            quantity_kg=Decimal(quantity),
            price_per_kg=Decimal(price),
            fulfillment=fulfillment,
        )

    def make_order(self, listing, buyer, quantity, status=HarvestOrder.STATUS_PENDING):
        return HarvestOrder.objects.create(
            listing=listing,
            buyer=buyer,
            quantity_kg=Decimal(quantity),
            price_per_kg=listing.price_per_kg,
            total_amount=Decimal(quantity) * listing.price_per_kg,
            fulfillment=listing.fulfillment,
            phone='70000000',
            status=status,
        )

    def login_seller(self):
        self.client.login(username='seller', password='StrongPass123!')

    def login_buyer(self):
        self.client.login(username='buyer', password='StrongPass123!')

    def test_clients_see_cross_farm_listings_and_submit_orders_with_price_snapshot(self):
        self.login_buyer()
        response = self.client.get(reverse('ventes:marketplace'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mangues')
        self.assertContains(response, 'Riz local')

        response = self.client.post(reverse('ventes:order_create', args=[self.listing.pk]), {
            'quantity_kg': '2.50',
            'phone': '70123456',
        })

        self.assertRedirects(response, reverse('ventes:orders'))
        order = HarvestOrder.objects.get(buyer=self.buyer)
        self.assertEqual(order.listing.farm, self.seller_farm)
        self.assertEqual(order.price_per_kg, Decimal('500.00'))
        self.assertEqual(order.total_amount, Decimal('1250.00'))
        self.assertEqual(order.status, HarvestOrder.STATUS_PENDING)

        self.listing.price_per_kg = Decimal('900.00')
        self.listing.save()
        order.refresh_from_db()
        self.assertEqual(order.total_amount, Decimal('1250.00'))

    def test_seller_confirmation_reserves_stock_and_rejects_overbooking(self):
        first = self.make_order(self.listing, self.buyer, '6.00')
        second = self.make_order(self.listing, self.other_buyer, '6.00')
        self.login_seller()

        response = self.client.post(reverse('ventes:order_update', args=[first.pk]), {'action': 'confirm'})
        self.assertRedirects(response, reverse('ventes:orders'))
        first.refresh_from_db()
        self.listing.refresh_from_db()
        self.assertEqual(first.status, HarvestOrder.STATUS_CONFIRMED)
        self.assertEqual(self.listing.available_kg, Decimal('4.00'))

        response = self.client.post(reverse('ventes:order_update', args=[second.pk]), {'action': 'confirm'})
        self.assertRedirects(response, reverse('ventes:orders'))
        second.refresh_from_db()
        self.listing.refresh_from_db()
        self.assertEqual(second.status, HarvestOrder.STATUS_PENDING)
        self.assertEqual(self.listing.available_kg, Decimal('4.00'))

    def test_cancelling_confirmed_order_releases_reserved_stock(self):
        order = self.make_order(self.listing, self.buyer, '4.00')
        self.login_seller()
        self.client.post(reverse('ventes:order_update', args=[order.pk]), {'action': 'confirm'})
        self.client.logout()
        self.login_buyer()

        response = self.client.post(reverse('ventes:order_update', args=[order.pk]), {'action': 'cancel'})

        self.assertRedirects(response, reverse('ventes:orders'))
        order.refresh_from_db()
        self.listing.refresh_from_db()
        self.assertEqual(order.status, HarvestOrder.STATUS_CANCELLED)
        self.assertEqual(self.listing.available_kg, Decimal('10.00'))

    def test_buyer_cannot_access_seller_or_other_buyer_order_data(self):
        owned = self.make_order(self.listing, self.buyer, '1.00')
        foreign = self.make_order(self.other_listing, self.other_buyer, '1.00')
        self.login_buyer()

        response = self.client.get(reverse('ventes:orders'))
        self.assertEqual(list(response.context['orders']), [owned])

        response = self.client.post(reverse('ventes:order_update', args=[foreign.pk]), {'action': 'cancel'})
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('ventes:listings'))
        self.assertRedirects(response, reverse('dashboard:index'))

    def test_seller_cannot_manage_another_farm_listing(self):
        self.login_seller()
        response = self.client.get(reverse('ventes:listing_edit', args=[self.other_listing.pk]))
        self.assertEqual(response.status_code, 404)

    def test_delivery_listing_requires_address_and_order_inherits_seller_fulfillment(self):
        listing = self.make_listing(
            self.seller_farm, 'Tomates', '8.00', '250.00', HarvestListing.FULFILLMENT_DELIVERY,
        )
        self.login_buyer()

        response = self.client.post(reverse('ventes:order_create', args=[listing.pk]), {
            'quantity_kg': '1.00',
            'phone': '70123456',
        })
        self.assertRedirects(response, reverse('ventes:marketplace'))
        self.assertFalse(HarvestOrder.objects.filter(listing=listing).exists())

        self.client.post(reverse('ventes:order_create', args=[listing.pk]), {
            'quantity_kg': '1.00',
            'phone': '70123456',
            'delivery_address': 'Sikasso, centre-ville',
        })
        order = HarvestOrder.objects.get(listing=listing)
        self.assertEqual(order.fulfillment, HarvestOrder.FULFILLMENT_DELIVERY)
        self.assertEqual(order.delivery_address, 'Sikasso, centre-ville')

    def test_listing_creation_requires_an_image_and_seller_role(self):
        self.login_seller()
        image = SimpleUploadedFile('mangue.png', b'not-a-real-image', content_type='image/png')
        response = self.client.post(reverse('ventes:listings'), {
            'title': 'Nouvelle récolte',
            'price_per_kg': '200',
            'quantity_kg': '20',
            'fulfillment': HarvestListing.FULFILLMENT_PICKUP,
            'is_active': 'on',
            'photo': image,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(HarvestListing.objects.filter(title='Nouvelle récolte').exists())

        self.login_buyer()
        response = self.client.post(reverse('ventes:listings'), {})
        self.assertRedirects(response, reverse('dashboard:index'))

    def test_seller_can_publish_a_real_photo_and_serve_it_in_development(self):
        self.login_seller()
        image_buffer = BytesIO()
        Image.new('RGB', (2, 2), color='green').save(image_buffer, format='PNG')
        image = SimpleUploadedFile('mangue.png', image_buffer.getvalue(), content_type='image/png')

        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            response = self.client.post(reverse('ventes:listings'), {
                'title': 'Mangues fraîches',
                'description': 'Récolte du jour',
                'price_per_kg': '400',
                'quantity_kg': '12',
                'fulfillment': HarvestListing.FULFILLMENT_PICKUP,
                'is_active': 'on',
                'photo': image,
            })

            self.assertRedirects(response, reverse('ventes:listings'))
            listing = HarvestListing.objects.get(title='Mangues fraîches')
            self.assertTrue(listing.photo.storage.exists(listing.photo.name))
            with listing.photo.storage.open(listing.photo.name, 'rb') as saved_image:
                self.assertTrue(saved_image.read().startswith(b'\x89PNG'))
