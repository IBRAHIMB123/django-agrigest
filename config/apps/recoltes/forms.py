from django import forms

from .models import Recolte
from apps.cultures.models import Culture
from apps.parcelles.models import Parcelle
from apps.campaigns.models import Campaign


class RecolteForm(forms.ModelForm):
    quantity = forms.DecimalField(min_value=0.01, max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    yield_per_ha = forms.DecimalField(min_value=0, max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))

    def __init__(self, *args, farm=None, **kwargs):
        self.farm = farm
        super().__init__(*args, **kwargs)
        self.fields['culture'].queryset = Culture.objects.filter(farm=farm) if farm else Culture.objects.none()
        self.fields['parcelle'].queryset = Parcelle.objects.filter(farm=farm) if farm else Parcelle.objects.none()
        self.fields['campaign'].required = False
        self.fields['campaign'].queryset = Campaign.objects.filter(farm=farm) if farm else Campaign.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        if self.farm:
            campaign = cleaned_data.get('campaign')
            culture = cleaned_data.get('culture')
            parcelle = cleaned_data.get('parcelle')
            if campaign and campaign.farm_id != self.farm.pk:
                self.add_error('campaign', 'Choisissez une campagne de cette exploitation.')
            if culture and culture.farm_id != self.farm.pk:
                self.add_error('culture', 'Choisissez une culture de cette exploitation.')
            if parcelle and parcelle.farm_id != self.farm.pk:
                self.add_error('parcelle', 'Choisissez une parcelle de cette exploitation.')
        culture = cleaned_data.get('culture')
        parcelle = cleaned_data.get('parcelle')
        if culture and parcelle and culture.parcelle_id != parcelle.pk:
            self.add_error('parcelle', 'La parcelle doit correspondre à celle de la culture sélectionnée.')
        campaign = cleaned_data.get('campaign')
        if campaign and (campaign.parcelle_id != (parcelle.pk if parcelle else None) or campaign.culture_id != (culture.pk if culture else None)):
            self.add_error('campaign', 'La campagne ne correspond pas a la culture et a la parcelle.')
        if campaign and cleaned_data.get('harvested_date') and not (campaign.start_date <= cleaned_data['harvested_date'] <= campaign.end_date):
            self.add_error('harvested_date', 'La date de recolte doit etre comprise dans les dates de la campagne.')
        return cleaned_data

    class Meta:
        model = Recolte
        fields = ['campaign', 'culture', 'parcelle', 'harvested_date', 'quantity', 'unit', 'yield_per_ha', 'notes']
        widgets = {
            'campaign': forms.Select(attrs={'class': 'form-control'}),
            'culture': forms.Select(attrs={'class': 'form-control'}),
            'parcelle': forms.Select(attrs={'class': 'form-control'}),
            'harvested_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'yield_per_ha': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
