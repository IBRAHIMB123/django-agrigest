from django.contrib import admin

from .models import Parcelle


@admin.register(Parcelle)
class ParcelleAdmin(admin.ModelAdmin):
    list_display = ('name', 'farm', 'location', 'area', 'status')
    list_filter = ('status', 'soil_type')
    search_fields = ('name', 'location')
