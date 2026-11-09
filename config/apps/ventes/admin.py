from django.contrib import admin

from .models import Client, HarvestListing, HarvestOrder, Vente


@admin.register(HarvestListing)
class HarvestListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'farm', 'price_per_kg', 'quantity_kg', 'is_active')
    list_filter = ('is_active',)


@admin.register(HarvestOrder)
class HarvestOrderAdmin(admin.ModelAdmin):
    list_display = ('listing', 'buyer', 'quantity_kg', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'fulfillment')
    readonly_fields = ('listing', 'buyer', 'quantity_kg', 'price_per_kg', 'total_amount', 'created_at')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')


@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'client', 'quantity', 'unit_price', 'total_amount', 'sale_date')
