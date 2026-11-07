from django.urls import path

from .views import dashboard_index, search_global

app_name = 'dashboard'

urlpatterns = [
    path('', dashboard_index, name='index'),
    path('search/', search_global, name='search'),
]
