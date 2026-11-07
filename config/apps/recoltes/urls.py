from django.urls import path

from .views import recolte_delete, recolte_edit, recolte_list

app_name = 'recoltes'

urlpatterns = [
    path('', recolte_list, name='list'),
    path('new/', recolte_list, name='new'),
    path('<int:pk>/edit/', recolte_edit, name='edit'),
    path('<int:pk>/delete/', recolte_delete, name='delete'),
]
