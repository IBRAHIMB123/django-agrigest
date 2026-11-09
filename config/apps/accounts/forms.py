from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import FarmProfile

User = get_user_model()


class StyledAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}))


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'vous@exemple.com', 'autocomplete': 'email'}))
    first_name = forms.CharField(max_length=50, required=True, label='Prénom', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'given-name'}))
    last_name = forms.CharField(max_length=50, required=True, label='Nom', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'family-name'}))
    farm_name = forms.CharField(max_length=120, required=True, label="Nom de l'exploitation", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la ferme'}))
    farm_location = forms.CharField(max_length=150, required=False, label='Localisation', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ville ou région'}))
    role = forms.ChoiceField(
        choices=FarmProfile.ROLE_CHOICES,
        initial=FarmProfile.ROLE_ADMIN,
        label='Interface principale',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {'username': "Nom d'utilisateur"}
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'username', 'placeholder': 'Identifiant de connexion'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Mot de passe'
        self.fields['password2'].label = 'Confirmation'
        self.fields['password1'].help_text = 'Au moins 8 caractères, différents de votre nom.'
        self.fields['password2'].help_text = ''

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            FarmProfile.objects.create(
                user=user,
                name=self.cleaned_data['farm_name'],
                location=self.cleaned_data['farm_location'],
                role=self.cleaned_data.get('role', FarmProfile.ROLE_ADMIN),
            )
        return user
