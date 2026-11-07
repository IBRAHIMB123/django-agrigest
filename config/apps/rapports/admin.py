from django.contrib import admin

from .models import Rapport


@admin.register(Rapport)
class RapportAdmin(admin.ModelAdmin):
    list_display = ('farm', 'period_label', 'revenue', 'expense', 'profit')
