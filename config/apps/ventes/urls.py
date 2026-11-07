from django.urls import path

from .views import client_create, vente_delete, vente_edit, vente_list

app_name = 'ventes'

urlpatterns = [
    path('', vente_list, name='list'),
    path('client/', client_create, name='client_create'),
    path('new/', vente_list, name='new'),
    path('<int:pk>/edit/', vente_edit, name='edit'),
    path('<int:pk>/delete/', vente_delete, name='delete'),
]
