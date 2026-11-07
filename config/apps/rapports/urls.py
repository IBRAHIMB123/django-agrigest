from django.urls import path

from .views import export_csv, export_pdf, rapport_index

app_name = 'rapports'

urlpatterns = [
    path('', rapport_index, name='index'),
    path('export/csv/', export_csv, name='export_csv'),
    path('export/pdf/', export_pdf, name='export_pdf'),
]
