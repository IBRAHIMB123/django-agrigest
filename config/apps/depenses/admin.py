from django.contrib import admin

from .models import Depense


@admin.register(Depense)
class DepenseAdmin(admin.ModelAdmin):
    list_display = ('farm', 'category', 'amount', 'date')
    list_filter = ('category',)
