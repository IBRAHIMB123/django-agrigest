from django.contrib import admin

from .models import Client, Vente


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')


@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'client', 'quantity', 'unit_price', 'total_amount', 'sale_date')
