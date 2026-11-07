from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import get_or_create_farm_profile

from .forms import CultureForm
from .models import Culture


@login_required
def culture_list(request):
    farm = get_or_create_farm_profile(request.user, request=request)
    cultures = Culture.objects.filter(farm=farm).select_related('parcelle').order_by('-created_at')
    if request.method == 'POST':
        form = CultureForm(request.POST, farm=farm)
        if form.is_valid():
            culture = form.save(commit=False)
            culture.farm = farm
            culture.save()
            messages.success(request, 'Culture enregistrée.')
            return redirect('cultures:list')
    else:
        form = CultureForm(initial={'parcelle': cultures.first().parcelle.id if cultures.exists() else None}, farm=farm)
    average_health = cultures.aggregate(value=Avg('health_score'))['value'] or 0
    return render(request, 'cultures/cultures.html', {'cultures': cultures, 'form': form, 'average_health': average_health})


@login_required
def culture_delete(request, pk):
    farm = get_or_create_farm_profile(request.user, request=request)
    culture = get_object_or_404(Culture, pk=pk, farm=farm)
    if request.method == 'POST':
        if culture.campaigns.exists() or culture.recoltes.exists():
            messages.error(request, 'Cette culture est liee a une campagne. Terminez ou supprimez la campagne avant de supprimer la culture.')
            return redirect('cultures:list')
        culture.delete()
        messages.success(request, 'Culture supprimée.')
        return redirect('cultures:list')
    return render(request, 'cultures/delete.html', {'culture': culture, 'can_delete': not culture.campaigns.exists() and not culture.recoltes.exists()})


@login_required
def culture_edit(request, pk):
    farm = get_or_create_farm_profile(request.user, request=request)
    culture = get_object_or_404(Culture, pk=pk, farm=farm)
    if request.method == 'POST':
        form = CultureForm(request.POST, instance=culture, farm=farm)
        if form.is_valid():
            form.save()
            messages.success(request, 'Culture mise a jour.')
            return redirect('cultures:list')
    else:
        form = CultureForm(instance=culture, farm=farm)
    return render(request, 'cultures/edit.html', {'form': form, 'culture': culture})
