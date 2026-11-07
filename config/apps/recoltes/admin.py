from django.contrib import admin

from .models import Recolte


@admin.register(Recolte)
class RecolteAdmin(admin.ModelAdmin):
    list_display = ('culture', 'parcelle', 'harvested_date', 'quantity', 'yield_per_ha')
