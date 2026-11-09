from django.urls import path

from .views import (
    client_create, listing_edit, listing_list, marketplace, order_create,
    order_list, order_update, vente_delete, vente_edit, vente_list,
)

app_name = 'ventes'

urlpatterns = [
    path('boutique/', marketplace, name='marketplace'),
    path('annonces/', listing_list, name='listings'),
    path('annonces/<int:pk>/modifier/', listing_edit, name='listing_edit'),
    path('boutique/<int:listing_id>/commander/', order_create, name='order_create'),
    path('commandes/', order_list, name='orders'),
    path('commandes/<int:pk>/action/', order_update, name='order_update'),
    path('', vente_list, name='list'),
    path('client/', client_create, name='client_create'),
    path('new/', vente_list, name='new'),
    path('<int:pk>/edit/', vente_edit, name='edit'),
    path('<int:pk>/delete/', vente_delete, name='delete'),
]
