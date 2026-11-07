from django.contrib import admin

from .models import Culture


@admin.register(Culture)
class CultureAdmin(admin.ModelAdmin):
    list_display = ('name', 'parcelle', 'variety', 'stage', 'health_score')
    list_filter = ('stage', 'status')
    search_fields = ('name', 'variety')
