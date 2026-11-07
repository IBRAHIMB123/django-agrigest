from django.urls import path

from .views import intrant_list, movement_record

app_name = 'intrants'

urlpatterns = [
    path('', intrant_list, name='list'),
    path('mouvement/', movement_record, name='movement'),
]
