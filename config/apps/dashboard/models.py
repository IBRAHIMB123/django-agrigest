from django.db import models

from apps.accounts.models import FarmProfile


class DashboardSnapshot(models.Model):
    farm = models.ForeignKey(FarmProfile, on_delete=models.CASCADE, related_name='dashboard_snapshots')
    month = models.CharField(max_length=12)
    revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    expense = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    harvest = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.month} - {self.farm}'
