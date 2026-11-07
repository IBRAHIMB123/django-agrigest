from django.db import models

from apps.accounts.models import FarmProfile


class Rapport(models.Model):
    farm = models.ForeignKey(FarmProfile, on_delete=models.CASCADE, related_name='rapports')
    period_label = models.CharField(max_length=30)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expense = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.period_label} - {self.farm}'
