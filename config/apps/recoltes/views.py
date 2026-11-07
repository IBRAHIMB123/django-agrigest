from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q

from apps.accounts.models import get_or_create_farm_profile

from .forms import RecolteForm
from .models import Recolte


@login_required
def recolte_list(request):
    farm = get_or_create_farm_profile(request.user, request=request)
    recoltes = Recolte.objects.filter(farm=farm).select_related('culture', 'parcelle', 'campaign').order_by('-harvested_date')
    query = request.GET.get('q', '').strip()
    if query:
        recoltes = recoltes.filter(Q(culture__name__icontains=query) | Q(parcelle__name__icontains=query) | Q(campaign__name__icontains=query))
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')
    if date_from:
        recoltes = recoltes.filter(harvested_date__gte=date_from)
    if date_to:
        recoltes = recoltes.filter(harvested_date__lte=date_to)
    if request.method == 'POST':
        form = RecolteForm(request.POST, farm=farm)
        if form.is_valid():
            recolte = form.save(commit=False)
            recolte.farm = farm
            recolte.save()
            messages.success(request, 'Récolte enregistrée.')
            return redirect('recoltes:list')
    else:
        form = RecolteForm(farm=farm)
    total_tonnes = recoltes.filter(unit='tonnes').aggregate(total=Sum('quantity'))['total'] or 0
    return render(request, 'recoltes/recoltes.html', {'recoltes': recoltes, 'form': form, 'total_tonnes': total_tonnes, 'query': query, 'date_from': date_from, 'date_to': date_to})


@login_required
def recolte_edit(request, pk):
    farm = get_or_create_farm_profile(request.user, request=request)
    recolte = get_object_or_404(Recolte, pk=pk, farm=farm)
    if request.method == 'POST':
        form = RecolteForm(request.POST, instance=recolte, farm=farm)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recolte mise a jour.')
            return redirect('recoltes:list')
    else:
        form = RecolteForm(instance=recolte, farm=farm)
    return render(request, 'recoltes/edit.html', {'recolte': recolte, 'form': form})


@login_required
def recolte_delete(request, pk):
    farm = get_or_create_farm_profile(request.user, request=request)
    recolte = get_object_or_404(Recolte, pk=pk, farm=farm)
    if request.method == 'POST':
        recolte.delete()
        messages.success(request, 'Recolte supprimee.')
        return redirect('recoltes:list')
    return render(request, 'recoltes/delete.html', {'recolte': recolte})
