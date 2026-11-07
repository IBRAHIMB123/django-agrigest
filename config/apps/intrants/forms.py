from django import forms
from django.core.exceptions import ValidationError

from .models import Intrant, MouvementStock


class IntrantForm(forms.ModelForm):
    quantity = forms.DecimalField(min_value=0, max_digits=12, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    min_stock = forms.DecimalField(min_value=0, max_digits=12, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    unit_price = forms.DecimalField(min_value=0, max_digits=12, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))

    class Meta:
        model = Intrant
        fields = ['name', 'category', 'unit', 'quantity', 'min_stock', 'unit_price', 'supplier']
        labels = {
            'name': 'Intrant',
            'category': 'Catégorie',
            'unit': 'Unité',
            'quantity': 'Quantité en stock',
            'min_stock': 'Seuil d’alerte',
            'unit_price': 'Prix unitaire',
            'supplier': 'Fournisseur',
        }
        help_texts = {
            'unit': 'kg, L, sacs…',
            'unit_price': 'Montant en FCFA.',
            'min_stock': 'Une alerte apparaît lorsque le stock passe sous ce seuil.',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du produit'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'kg'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'inputmode': 'decimal'}),
            'min_stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'inputmode': 'decimal'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'inputmode': 'decimal'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du fournisseur'}),
        }


class MouvementStockForm(forms.ModelForm):
    def __init__(self, *args, farm=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['intrant'].queryset = Intrant.objects.filter(farm=farm) if farm else Intrant.objects.none()

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        movement_type = self.cleaned_data.get('movement_type')
        if quantity < 0 or (quantity == 0 and movement_type != 'ajustement'):
            raise ValidationError('La quantite doit etre positive, sauf pour un ajustement a zero.')
        intrant = self.cleaned_data.get('intrant')
        if movement_type == 'sortie' and intrant and quantity > intrant.quantity:
            raise ValidationError('La sortie depasse le stock disponible.')
        return quantity

    class Meta:
        model = MouvementStock
        fields = ['intrant', 'movement_type', 'quantity', 'note']
        labels = {
            'intrant': 'Intrant',
            'movement_type': 'Type de mouvement',
            'quantity': 'Quantité',
            'note': 'Note',
        }
        widgets = {
            'intrant': forms.Select(attrs={'class': 'form-control'}),
            'movement_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'inputmode': 'decimal'}),
            'note': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Motif du mouvement'}),
        }
