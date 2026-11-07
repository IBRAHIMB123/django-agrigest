from django.urls import path

from .views import parcelle_delete, parcelle_detail, parcelle_edit, parcelle_list

urlpatterns = [
    path('', parcelle_list, name='list'),
    path('new/', parcelle_list, name='new'),
    path('<int:pk>/', parcelle_detail, name='detail'),
    path('<int:pk>/edit/', parcelle_edit, name='edit'),
    path('<int:pk>/delete/', parcelle_delete, name='delete'),
]
