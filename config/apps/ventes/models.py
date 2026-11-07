from django.db import models

from apps.accounts.models import FarmProfile
from apps.campaigns.models import Campaign


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
