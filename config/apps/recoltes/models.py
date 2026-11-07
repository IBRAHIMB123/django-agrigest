from django.db import models

from apps.accounts.models import FarmProfile
from apps.campaigns.models import Campaign
from apps.cultures.models import Culture
from apps.parcelles.models import Parcelle


class Recolte(models.Model):
    UNIT_CHOICES = [
        ('kg', 'kg'),
        ('tonnes', 'tonnes'),
        ('sacs', 'sacs'),
    ]

    farm = models.ForeignKey(FarmProfile, on_delete=models.CASCADE, related_name='recoltes')
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True, related_name='recoltes')
    culture = models.ForeignKey(Culture, on_delete=models.SET_NULL, null=True, blank=True, related_name='recoltes')
    parcelle = models.ForeignKey(Parcelle, on_delete=models.SET_NULL, null=True, blank=True, related_name='recoltes')
    harvested_date = models.DateField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='tonnes')
    yield_per_ha = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-harvested_date']

    def __str__(self):
        return f'{self.culture or "Récolte"} — {self.quantity} {self.unit}'
