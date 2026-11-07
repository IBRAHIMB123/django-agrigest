from django.urls import path

from .views import culture_delete, culture_edit, culture_list

app_name = 'cultures'

urlpatterns = [
    path('', culture_list, name='list'),
    path('new/', culture_list, name='new'),
    path('<int:pk>/edit/', culture_edit, name='edit'),
    path('<int:pk>/delete/', culture_delete, name='delete'),
]
