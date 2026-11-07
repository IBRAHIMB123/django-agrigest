from django.urls import path
from .farm_views import farm_activate, farm_delete, farm_detail, farm_edit, farm_list

app_name = 'farms'
urlpatterns = [
    path('', farm_list, name='list'),
    path('<int:pk>/', farm_detail, name='detail'),
    path('<int:pk>/edit/', farm_edit, name='edit'),
    path('<int:pk>/delete/', farm_delete, name='delete'),
    path('<int:pk>/activate/', farm_activate, name='activate'),
]
