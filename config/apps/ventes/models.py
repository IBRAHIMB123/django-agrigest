from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.accounts.models import FarmProfile
from apps.campaigns.models import Campaign


class HarvestListing(models.Model):
    FULFILLMENT_PICKUP = 'pickup'
    FULFILLMENT_DELIVERY = 'delivery'
    FULFILLMENT_CHOICES = [
        (FULFILLMENT_PICKUP, 'Retrait chez le vendeur'),
        (FULFILLMENT_DELIVERY, 'Livraison à convenir'),
    ]

    farm = models.ForeignKey(FarmProfile, on_delete=models.CASCADE, related_name='harvest_listings')
    title = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='marketplace/harvests/')
    price_per_kg = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('1.00'))])
    quantity_kg = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    fulfillment = models.CharField(max_length=12, choices=FULFILLMENT_CHOICES, default=FULFILLMENT_PICKUP)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def available_kg(self):
        return self.quantity_kg

    def __str__(self):
        return self.title


class HarvestOrder(models.Model):
    FULFILLMENT_PICKUP = HarvestListing.FULFILLMENT_PICKUP
    FULFILLMENT_DELIVERY = HarvestListing.FULFILLMENT_DELIVERY
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_REJECTED = 'rejected'
    STATUS_CANCELLED = 'cancelled'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'En attente'),
        (STATUS_CONFIRMED, 'Confirmée'),
        (STATUS_REJECTED, 'Refusée'),
        (STATUS_CANCELLED, 'Annulée'),
        (STATUS_COMPLETED, 'Terminée'),
    ]
    listing = models.ForeignKey(HarvestListing, on_delete=models.PROTECT, related_name='orders')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='harvest_orders')
    quantity_kg = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    price_per_kg = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=26, decimal_places=2)
    fulfillment = models.CharField(max_length=12, choices=HarvestListing.FULFILLMENT_CHOICES)
    delivery_address = models.CharField(max_length=240, blank=True)
    phone = models.CharField(max_length=40)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.listing.title} - {self.quantity_kg} kg'


class Client(models.Model):
    farm = models.ForeignKey(FarmProfile, on_delete=models.CASCADE, related_name='clients')
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Vente(models.Model):
    farm = models.ForeignKey(FarmProfile, on_delete=models.CASCADE, related_name='ventes')
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventes')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventes')
    product_name = models.CharField(max_length=120)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sale_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-sale_date']

    def __str__(self):
        return f'{self.product_name} - {self.total_amount} FCFA'
