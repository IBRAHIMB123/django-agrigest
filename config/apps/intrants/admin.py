from django.contrib import admin

from .models import Intrant, MouvementStock


@admin.register(Intrant)
class IntrantAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', 'min_stock', 'supplier')


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ('intrant', 'movement_type', 'quantity', 'created_at')
