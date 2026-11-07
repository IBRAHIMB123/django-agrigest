from django import forms

from .models import Parcelle


class ParcelleForm(forms.ModelForm):
    class Meta:
        model = Parcelle
        fields = ['name', 'location', 'area', 'soil_type', 'description', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la parcelle'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Localisation'}),
            'area': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'soil_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
