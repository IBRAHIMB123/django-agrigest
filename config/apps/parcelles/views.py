from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import get_or_create_farm_profile

from .forms import ParcelleForm
from .models import Parcelle


@login_required
def parcelle_list(request):
    farm = get_or_create_farm_profile(request.user, request=request)
    parcels = Parcelle.objects.filter(farm=farm).prefetch_related('cultures').order_by('-created_at')
    if request.method == 'POST':
        form = ParcelleForm(request.POST)
        if form.is_valid():
            parcel = form.save(commit=False)
            parcel.farm = farm
            parcel.save()
            messages.success(request, 'Parcelle créée avec succès.')
            return redirect('parcelles:list')
    else:
        form = ParcelleForm()
    total_area = parcels.aggregate(total=Sum('area'))['total'] or 0
    return render(request, 'parcelles/parcelles.html', {'parcelles': parcels, 'form': form, 'total_area': total_area})


@login_required
def parcelle_detail(request, pk):
    farm = get_or_create_farm_profile(request.user, request=request)
    parcel = get_object_or_404(Parcelle, pk=pk, farm=farm)
    return render(request, 'parcelles/detail.html', {'parcelle': parcel})


@login_required
def parcelle_edit(request, pk):
    farm = get_or_create_farm_profile(request.user, request=request)
    parcel = get_object_or_404(Parcelle, pk=pk, farm=farm)
    if request.method == 'POST':
        form = ParcelleForm(request.POST, instance=parcel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Parcelle mise à jour.')
            return redirect('parcelles:detail', pk=parcel.pk)
    else:
        form = ParcelleForm(instance=parcel)
    return render(request, 'parcelles/edit.html', {'form': form, 'parcelle': parcel})


@login_required
def parcelle_delete(request, pk):
    farm = get_or_create_farm_profile(request.user, request=request)
    parcel = get_object_or_404(Parcelle, pk=pk, farm=farm)
    if request.method == 'POST':
        if parcel.cultures.exists() or parcel.recoltes.exists():
            messages.error(request, 'Cette parcelle contient des cultures ou des recoltes. Supprimez ou reaffectez-les avant la parcelle.')
            return redirect('parcelles:detail', pk=parcel.pk)
        if parcel.campaigns.exists():
            messages.error(request, 'Cette parcelle est liee a une campagne. Terminez ou supprimez la campagne avant de supprimer la parcelle.')
            return redirect('parcelles:detail', pk=parcel.pk)
        parcel.delete()
        messages.success(request, 'Parcelle supprimée.')
        return redirect('parcelles:list')
    return render(request, 'parcelles/delete.html', {'parcelle': parcel, 'can_delete': not parcel.cultures.exists() and not parcel.recoltes.exists() and not parcel.campaigns.exists()})
