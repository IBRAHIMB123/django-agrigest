from django.urls import path
from .views import campaign_delete, campaign_edit, campaign_list

app_name = 'campaigns'
urlpatterns = [
    path('', campaign_list, name='list'),
    path('<int:pk>/edit/', campaign_edit, name='edit'),
    path('<int:pk>/delete/', campaign_delete, name='delete'),
]
