from django import forms

from .models import Parcelle


class ParcelleForm(forms.ModelForm):
    class Meta:
        model = Parcelle
        fields = ['name', 'location', 'area', 'soil_type', 'description', 'status']
        labels = {
            'name': 'Nom',
            'location': 'Localisation',
            'area': 'Superficie',
            'soil_type': 'Type de sol',
            'description': 'Description',
            'status': 'Statut',
        }
        help_texts = {'area': 'Exprimée en hectares.'}
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex. Parcelle nord'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Village, commune ou repère'}),
            'area': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': '0,00', 'inputmode': 'decimal'}),
            'soil_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Accès, irrigation, particularités du terrain'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
