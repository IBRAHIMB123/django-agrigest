from django.db import models

from apps.accounts.models import FarmProfile


class Parcelle(models.Model):
    SOIL_CHOICES = [
        ('argilo_limoneux', 'Argilo-limoneux'),
        ('limoneux', 'Limoneux fertile'),
        ('sablo_argileux', 'Sablo-argileux'),
        ('sableux', 'Sableux profond'),
        ('alluvionnaire', 'Alluvionnaire'),
    ]
    STATUS_CHOICES = [
        ('active', 'En croissance'),
        ('harvest', 'Récolte proche'),
        ('planted', 'Planté'),
        ('fallow', 'Jachère'),
    ]

    farm = models.ForeignKey(FarmProfile, on_delete=models.CASCADE, related_name='parcelles')
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=200)
    area = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    soil_type = models.CharField(max_length=40, choices=SOIL_CHOICES, default='argilo_limoneux')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
