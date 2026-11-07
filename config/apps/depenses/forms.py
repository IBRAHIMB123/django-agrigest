from django import forms

from .models import Depense
from apps.campaigns.models import Campaign


class DepenseForm(forms.ModelForm):
    amount = forms.DecimalField(min_value=0.01, max_digits=12, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))

    def __init__(self, *args, farm=None, **kwargs):
        self.farm = farm
        super().__init__(*args, **kwargs)
        self.fields['campaign'].required = False
        self.fields['campaign'].queryset = Campaign.objects.filter(farm=farm) if farm else Campaign.objects.none()

    def clean(self):
        cleaned = super().clean()
        campaign = cleaned.get('campaign')
        expense_date = cleaned.get('date')
        if campaign and self.farm and campaign.farm_id != self.farm.pk:
            self.add_error('campaign', 'Choisissez une campagne de cette exploitation.')
        if campaign and expense_date and not (campaign.start_date <= expense_date <= campaign.end_date):
            self.add_error('date', 'La date de depense doit etre comprise dans les dates de la campagne.')
        return cleaned

    class Meta:
        model = Depense
        fields = ['campaign', 'category', 'amount', 'date', 'description']
        labels = {
            'campaign': 'Campagne',
            'category': 'Catégorie',
            'amount': 'Montant',
            'date': 'Date',
            'description': 'Description',
        }
        help_texts = {'amount': 'Montant en FCFA.'}
        widgets = {
            'campaign': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'inputmode': 'decimal', 'placeholder': '0'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'À quoi correspond cette dépense ?'}),
        }
