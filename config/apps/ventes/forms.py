from decimal import Decimal

from django import forms

from .models import Client, HarvestListing, HarvestOrder, Vente
from apps.campaigns.models import Campaign


class HarvestListingForm(forms.ModelForm):
    class Meta:
        model = HarvestListing
        fields = ['title', 'description', 'photo', 'price_per_kg', 'quantity_kg', 'fulfillment', 'is_active']
        labels = {
            'title': 'Récolte',
            'description': 'Description',
            'photo': 'Photo',
            'price_per_kg': 'Prix par kilo (FCFA)',
            'quantity_kg': 'Quantité disponible (kg)',
            'fulfillment': 'Mode de remise proposé',
            'is_active': 'Publier l’annonce',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex. Mangues fraîches'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price_per_kg': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '0.01'}),
            'quantity_kg': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'fulfillment': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['photo'].required = True
        else:
            self.fields['photo'].required = False

class HarvestOrderForm(forms.ModelForm):
    quantity_kg = forms.DecimalField(
        min_value=Decimal('0.01'),
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
    )

    class Meta:
        model = HarvestOrder
        fields = ['quantity_kg', 'delivery_address', 'phone']
        labels = {
            'quantity_kg': 'Quantité souhaitée (kg)',
            'delivery_address': 'Adresse de livraison',
            'phone': 'Téléphone pour vous joindre',
        }
        widgets = {
            'delivery_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quartier, ville, indications'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel', 'required': True}),
        }

    def __init__(self, *args, listing, **kwargs):
        self.listing = listing
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        if self.listing.fulfillment == HarvestListing.FULFILLMENT_DELIVERY and not cleaned.get('delivery_address'):
            self.add_error('delivery_address', 'Indiquez une adresse pour la livraison.')
        quantity = cleaned.get('quantity_kg')
        if quantity and quantity > self.listing.available_kg:
            self.add_error('quantity_kg', 'Cette quantité dépasse le stock actuellement disponible.')
        return cleaned


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'phone', 'email']
        labels = {'name': 'Nom', 'phone': 'Téléphone', 'email': 'Email'}
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du client'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+223 …', 'inputmode': 'tel'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'client@exemple.com'}),
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
        labels = {
            'campaign': 'Campagne',
            'client': 'Client',
            'product_name': 'Produit',
            'quantity': 'Quantité',
            'unit_price': 'Prix unitaire',
            'sale_date': 'Date de vente',
            'notes': 'Notes',
        }
        help_texts = {'unit_price': 'Prix en FCFA. Le total est calculé automatiquement.'}
        widgets = {
            'campaign': forms.Select(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Produit vendu'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'inputmode': 'decimal'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'inputmode': 'decimal'}),
            'sale_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Conditions de vente, acompte, livraison'}),
        }
