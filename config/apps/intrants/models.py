from django.db import models

from apps.accounts.models import FarmProfile


class Intrant(models.Model):
    CATEGORY_CHOICES = [
        ('semence', 'Semence'),
        ('engrais', 'Engrais'),
        ('phytosanitaire', 'Produit phytosanitaire'),
        ('materiel', 'Matériel agricole'),
    ]

    farm = models.ForeignKey(FarmProfile, on_delete=models.CASCADE, related_name='intrants')
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    unit = models.CharField(max_length=20, default='kg')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    min_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    supplier = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def stock_alert(self):
        return self.quantity <= self.min_stock

    def __str__(self):
        return self.name


class MouvementStock(models.Model):
    TYPE_CHOICES = [('entree', 'Entrée'), ('sortie', 'Sortie'), ('ajustement', 'Ajustement')]
    intrant = models.ForeignKey(Intrant, on_delete=models.CASCADE, related_name='mouvements')
    movement_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.intrant.name} — {self.movement_type}'
