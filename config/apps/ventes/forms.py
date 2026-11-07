from django import forms

from .models import Client, Vente
from apps.campaigns.models import Campaign


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class VenteForm(forms.ModelForm):
    quantity = forms.DecimalField(min_value=0.01, max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    unit_price = forms.DecimalField(min_value=0, max_digits=12, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))

    def __init__(self, *args, farm=None, **kwargs):
        self.farm = farm
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.filter(farm=farm) if farm else Client.objects.none()
        self.fields['campaign'].required = False
        self.fields['campaign'].queryset = Campaign.objects.filter(farm=farm) if farm else Campaign.objects.none()

    def clean(self):
        cleaned = super().clean()
        campaign = cleaned.get('campaign')
        client = cleaned.get('client')
        sale_date = cleaned.get('sale_date')
        if client and self.farm and client.farm_id != self.farm.pk:
            self.add_error('client', 'Choisissez un client de cette exploitation.')
        if campaign and self.farm and campaign.farm_id != self.farm.pk:
            self.add_error('campaign', 'Choisissez une campagne de cette exploitation.')
        if campaign and sale_date and not (campaign.start_date <= sale_date <= campaign.end_date):
            self.add_error('sale_date', 'La date de vente doit etre comprise dans les dates de la campagne.')
        return cleaned

    class Meta:
        model = Vente
        fields = ['campaign', 'client', 'product_name', 'quantity', 'unit_price', 'sale_date', 'notes']
        widgets = {
            'campaign': forms.Select(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sale_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
