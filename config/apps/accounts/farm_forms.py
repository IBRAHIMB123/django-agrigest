from django import forms
from .models import FarmProfile


class FarmProfileForm(forms.ModelForm):
    class Meta:
        model = FarmProfile
        fields = ['name', 'location']
        labels = {'name': "Nom de l'exploitation", 'location': 'Localisation'}
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom de l'exploitation"}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ville, region'}),
        }
