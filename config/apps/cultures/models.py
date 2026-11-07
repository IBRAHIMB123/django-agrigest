from django.db import models

from apps.accounts.models import FarmProfile
from apps.parcelles.models import Parcelle


class Culture(models.Model):
    STAGE_CHOICES = [
        ('plantation', 'Plantation'),
        ('levée', 'Levée'),
        ('croissance', 'Croissance'),
        ('floraison', 'Floraison'),
        ('maturite', 'Maturité'),
        ('recolte', 'Récolte'),
    ]

    farm = models.ForeignKey(FarmProfile, on_delete=models.CASCADE, related_name='cultures')
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE, related_name='cultures')
    name = models.CharField(max_length=80)
    variety = models.CharField(max_length=80, blank=True)
    planted_date = models.DateField()
    expected_harvest_date = models.DateField()
    stage = models.CharField(max_length=30, choices=STAGE_CHOICES, default='croissance')
    status = models.CharField(max_length=30, default='en_croissance', choices=[('en_croissance', 'En croissance'), ('floraison', 'Floraison'), ('maturite', 'Maturité')])
    health_score = models.PositiveSmallIntegerField(default=80)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-planted_date']

    def __str__(self):
        return f'{self.name} - {self.parcelle}'
