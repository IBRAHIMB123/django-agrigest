from django import forms
from django.core.exceptions import ValidationError

from apps.cultures.models import Culture
from apps.parcelles.models import Parcelle
from .models import Campaign


class CampaignForm(forms.ModelForm):
    def __init__(self, *args, farm=None, **kwargs):
        self.farm = farm
        super().__init__(*args, **kwargs)
        self.fields['parcelle'].queryset = Parcelle.objects.filter(farm=farm) if farm else Parcelle.objects.none()
        self.fields['culture'].queryset = Culture.objects.filter(farm=farm) if farm else Culture.objects.none()

    def clean(self):
        cleaned = super().clean()
        parcelle = cleaned.get('parcelle')
        culture = cleaned.get('culture')
        if parcelle and self.farm and parcelle.farm_id != self.farm.pk:
            self.add_error('parcelle', 'Choisissez une parcelle de cette exploitation.')
        if culture and self.farm and culture.farm_id != self.farm.pk:
            self.add_error('culture', 'Choisissez une culture de cette exploitation.')
        if parcelle and culture and culture.parcelle_id != parcelle.pk:
            self.add_error('culture', 'Choisissez une culture associee a la parcelle.')
        if cleaned.get('start_date') and cleaned.get('end_date') and cleaned['end_date'] < cleaned['start_date']:
            self.add_error('end_date', 'La date de fin doit suivre la date de debut.')
        return cleaned

    class Meta:
        model = Campaign
        fields = ['name', 'parcelle', 'culture', 'start_date', 'end_date', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'parcelle': forms.Select(attrs={'class': 'form-control'}),
            'culture': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
