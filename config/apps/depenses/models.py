from django.db import models

from apps.accounts.models import FarmProfile
from apps.campaigns.models import Campaign


class Depense(models.Model):
    CATEGORY_CHOICES = [
        ('intrants', 'Intrants'),
        ('main_oeuvre', 'Main d’œuvre'),
        ('transport', 'Transport'),
        ('materiel', 'Matériel'),
        ('entretien', 'Entretien'),
        ('autres', 'Autres'),
    ]

    farm = models.ForeignKey(FarmProfile, on_delete=models.CASCADE, related_name='depenses')
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True, related_name='depenses')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='intrants')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date = models.DateField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.category} - {self.amount} FCFA'
