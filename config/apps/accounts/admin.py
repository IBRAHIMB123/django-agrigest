from django.contrib import admin

from .models import FarmProfile


@admin.register(FarmProfile)
class FarmProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'location', 'created_at')
    search_fields = ('name', 'location', 'user__username')
