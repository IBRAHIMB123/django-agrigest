from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import SignupForm
from .models import FarmProfile, get_or_create_farm_profile


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Compte créé avec succès. Bienvenue dans AgriGest.')
            return redirect('dashboard:index')
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


@login_required
def profile_view(request):
    farm = get_or_create_farm_profile(request.user, request=request)

    if request.method == 'POST' and 'role' in request.POST:
        selected_role = request.POST.get('role', farm.role)
        if selected_role in dict(FarmProfile.ROLE_CHOICES):
            farm.role = selected_role
            farm.save(update_fields=['role'])
            messages.success(request, 'Votre interface a été mise à jour.')
        else:
            messages.error(request, 'Rôle invalide.')
        return redirect('accounts:profile')

    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'farm': farm,
        'role_choices': FarmProfile.ROLE_CHOICES,
    })
