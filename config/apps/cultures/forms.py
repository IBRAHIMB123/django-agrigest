from django import forms

from .models import Culture
from apps.parcelles.models import Parcelle


class CultureForm(forms.ModelForm):
    def __init__(self, *args, farm=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parcelle'].queryset = Parcelle.objects.filter(farm=farm) if farm else Parcelle.objects.none()

    class Meta:
        model = Culture
        fields = ['parcelle', 'name', 'variety', 'planted_date', 'expected_harvest_date', 'stage', 'status', 'health_score', 'notes']
        labels = {
            'parcelle': 'Parcelle',
            'name': 'Culture',
            'variety': 'Variété',
            'planted_date': 'Date de plantation',
            'expected_harvest_date': 'Récolte prévue',
            'stage': 'Stade',
            'status': 'Statut',
            'health_score': 'État sanitaire',
            'notes': 'Notes',
        }
        help_texts = {'health_score': 'Indice de 0 à 100.'}
        widgets = {
            'parcelle': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Riz, maïs, maraîchage…'}),
            'variety': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Variété ou cultivar'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Observations de terrain'}),
            'planted_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_harvest_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'stage': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'health_score': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100', 'placeholder': '80'}),
        }
