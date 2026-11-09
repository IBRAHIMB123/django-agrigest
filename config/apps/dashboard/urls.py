from django.urls import path

from .views import admin_dashboard, client_dashboard, dashboard_index, home, search_global, worker_dashboard

app_name = 'dashboard'

urlpatterns = [
    path('', home, name='home'),
    path('dashboard/', dashboard_index, name='index'),
    path('supervision/', admin_dashboard, name='supervision'),
    path('terrain/', worker_dashboard, name='terrain'),
    path('client/', client_dashboard, name='client'),
    path('search/', search_global, name='search'),
]
