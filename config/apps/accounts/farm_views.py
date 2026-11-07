from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .farm_forms import FarmProfileForm
from .models import FarmProfile, get_or_create_farm_profile


@login_required
def farm_list(request):
    if request.method == 'POST':
        form = FarmProfileForm(request.POST)
        if form.is_valid():
            farm = form.save(commit=False)
            farm.user = request.user
            farm.save()
            request.session['active_farm_id'] = farm.pk
            messages.success(request, 'Exploitation creee.')
            return redirect('accounts:farms')
    else:
        form = FarmProfileForm()

    farms = FarmProfile.objects.filter(user=request.user).annotate(
        parcel_count=Count('parcelles', distinct=True),
        total_area=Sum('parcelles__area'),
    ).order_by('created_at', 'pk')
    return render(request, 'accounts/farms.html', {'farms': farms, 'form': form, 'active_farm': get_or_create_farm_profile(request.user, request=request)})


@login_required
def farm_detail(request, pk):
    farm = get_object_or_404(FarmProfile.objects.filter(user=request.user).annotate(
        parcel_count=Count('parcelles', distinct=True), total_area=Sum('parcelles__area')
    ), pk=pk)
    return render(request, 'accounts/farm_detail.html', {'farm': farm, 'parcelles': farm.parcelles.all(), 'active_farm': get_or_create_farm_profile(request.user, request=request)})


@login_required
def farm_edit(request, pk):
    farm = get_object_or_404(FarmProfile, pk=pk, user=request.user)
    if request.method == 'POST':
        form = FarmProfileForm(request.POST, instance=farm)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exploitation mise a jour.')
            return redirect('accounts:farm_detail', pk=farm.pk)
    else:
        form = FarmProfileForm(instance=farm)
    return render(request, 'accounts/farm_edit.html', {'form': form, 'farm': farm})


@login_required
def farm_delete(request, pk):
    farm = get_object_or_404(FarmProfile, pk=pk, user=request.user)
    if request.method == 'POST':
        if FarmProfile.objects.filter(user=request.user).count() == 1:
            messages.error(request, 'Conservez au moins une exploitation sur ce compte.')
            return redirect('accounts:farms')
        was_active = request.session.get('active_farm_id') == farm.pk
        farm.delete()
        if was_active:
            fallback = FarmProfile.objects.filter(user=request.user).order_by('created_at', 'pk').first()
            if fallback:
                request.session['active_farm_id'] = fallback.pk
            else:
                request.session.pop('active_farm_id', None)
        messages.success(request, 'Exploitation supprimee.')
        return redirect('accounts:farms')
    return render(request, 'accounts/farm_delete.html', {'farm': farm})


@login_required
def farm_activate(request, pk):
    farm = get_object_or_404(FarmProfile, pk=pk, user=request.user)
    if request.method == 'POST':
        request.session['active_farm_id'] = farm.pk
        messages.success(request, f"Exploitation active : {farm.name}.")
        return redirect('dashboard:index')
    return redirect('accounts:farms')

