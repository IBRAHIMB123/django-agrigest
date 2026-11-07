from django.urls import path

from .views import depense_list

app_name = 'depenses'

urlpatterns = [
    path('', depense_list, name='list'),
    path('new/', depense_list, name='new'),
]
