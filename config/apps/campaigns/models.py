from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.accounts.models import FarmProfile
from apps.cultures.models import Culture
from apps.parcelles.models import Parcelle


class Campaign(models.Model):
    STATUS_CHOICES = [
        ('preparation', 'En preparation'),
        ('active', 'En cours'),
        ('completed', 'Terminee'),
        ('cancelled', 'Annulee'),
    ]

    farm = models.ForeignKey(FarmProfile, on_delete=models.CASCADE, related_name='campaigns')
    name = models.CharField(max_length=120)
    parcelle = models.ForeignKey(Parcelle, on_delete=models.PROTECT, related_name='campaigns')
    culture = models.ForeignKey(Culture, on_delete=models.PROTECT, related_name='campaigns')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='preparation')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date', 'name']
        constraints = [
            models.CheckConstraint(condition=models.Q(end_date__gte=models.F('start_date')), name='campaign_end_not_before_start'),
        ]

    def clean(self):
        errors = {}
        if self.farm_id and self.parcelle_id and self.parcelle.farm_id != self.farm_id:
            errors['parcelle'] = 'Choisissez une parcelle de cette exploitation.'
        if self.farm_id and self.culture_id and self.culture.farm_id != self.farm_id:
            errors['culture'] = 'Choisissez une culture de cette exploitation.'
        if self.parcelle_id and self.culture_id and self.culture.parcelle_id != self.parcelle_id:
            errors['culture'] = 'La culture ne correspond pas a cette parcelle.'
        if self.parcelle_id and self.culture_id and self.parcelle.farm_id != self.culture.farm_id:
            errors['culture'] = 'La parcelle et la culture doivent appartenir a la meme exploitation.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def progress(self):
        if self.status == 'completed':
            return 100
        if self.status in {'preparation', 'cancelled'}:
            return 0
        today = timezone.localdate()
        total_days = max((self.end_date - self.start_date).days, 1)
        elapsed = (today - self.start_date).days
        return max(0, min(100, round(elapsed * 100 / total_days)))

    def __str__(self):
        return self.name

