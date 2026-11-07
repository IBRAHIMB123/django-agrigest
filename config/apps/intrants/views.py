from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from apps.accounts.models import get_or_create_farm_profile

from .forms import IntrantForm, MouvementStockForm
from .models import Intrant, MouvementStock


@login_required
def intrant_list(request):
    farm = get_or_create_farm_profile(request.user, request=request)
    intrants = Intrant.objects.filter(farm=farm).order_by('-created_at')
    movements = MouvementStock.objects.filter(intrant__farm=farm).select_related('intrant').order_by('-created_at')[:10]
    if request.method == 'POST':
        form = IntrantForm(request.POST)
        if form.is_valid():
            intrant = form.save(commit=False)
            intrant.farm = farm
            intrant.save()
            messages.success(request, 'Stock mis a jour.')
            return redirect('intrants:list')
    else:
        form = IntrantForm()
    return render(request, 'intrants/intrants.html', {
        'intrants': intrants,
        'movements': movements,
        'form': form,
        'movement_form': MouvementStockForm(farm=farm),
    })


@login_required
def movement_record(request):
    farm = get_or_create_farm_profile(request.user, request=request)
    if request.method != 'POST':
        return redirect('intrants:list')

    form = MouvementStockForm(request.POST, farm=farm)
    if not form.is_valid():
        messages.error(request, 'Mouvement invalide : verifiez le produit, la quantite et le stock disponible.')
        return redirect('intrants:list')

    movement = form.save(commit=False)
    with transaction.atomic():
        intrant = Intrant.objects.select_for_update().get(pk=movement.intrant_id, farm=farm)
        if movement.movement_type == 'entree':
            intrant.quantity += movement.quantity
        elif movement.movement_type == 'sortie':
            intrant.quantity -= movement.quantity
            if intrant.quantity < 0:
                messages.error(request, 'La sortie depasse le stock disponible.')
                return redirect('intrants:list')
        elif movement.movement_type == 'ajustement':
            intrant.quantity = movement.quantity
        intrant.save()
        movement.save()

    messages.success(request, 'Mouvement enregistre.')
    return redirect('intrants:list')
