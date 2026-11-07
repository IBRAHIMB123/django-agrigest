from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import get_or_create_farm_profile

from .forms import ClientForm, VenteForm
from .models import Client, Vente


@login_required
def vente_list(request):
    farm = get_or_create_farm_profile(request.user, request=request)
    clients = Client.objects.filter(farm=farm)
    ventes = Vente.objects.filter(farm=farm).select_related('client', 'campaign').order_by('-sale_date')
    query = request.GET.get('q', '').strip()
    client_query = request.GET.get('client', '').strip()
    if query:
        ventes = ventes.filter(Q(product_name__icontains=query) | Q(client__name__icontains=query) | Q(campaign__name__icontains=query))
    if client_query:
        clients = clients.filter(Q(name__icontains=client_query) | Q(email__icontains=client_query) | Q(phone__icontains=client_query))
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')
    if date_from:
        ventes = ventes.filter(sale_date__gte=date_from)
    if date_to:
        ventes = ventes.filter(sale_date__lte=date_to)
    if request.method == 'POST':
        form = VenteForm(request.POST, farm=farm)
        if form.is_valid():
            vente = form.save(commit=False)
            vente.farm = farm
            vente.save()
            messages.success(request, 'Vente enregistrée.')
            return redirect('ventes:list')
    else:
        form = VenteForm(farm=farm)
    total_revenue = ventes.aggregate(total=Sum('total_amount'))['total'] or 0
    return render(request, 'ventes/ventes.html', {'ventes': ventes, 'clients': clients, 'form': form, 'client_form': ClientForm(), 'total_revenue': total_revenue, 'query': query, 'client_query': client_query, 'date_from': date_from, 'date_to': date_to})


@login_required
def vente_edit(request, pk):
    farm = get_or_create_farm_profile(request.user, request=request)
    vente = get_object_or_404(Vente, pk=pk, farm=farm)
    if request.method == 'POST':
        form = VenteForm(request.POST, instance=vente, farm=farm)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vente mise a jour.')
            return redirect('ventes:list')
    else:
        form = VenteForm(instance=vente, farm=farm)
    return render(request, 'ventes/edit.html', {'vente': vente, 'form': form})


@login_required
def vente_delete(request, pk):
    farm = get_or_create_farm_profile(request.user, request=request)
    vente = get_object_or_404(Vente, pk=pk, farm=farm)
    if request.method == 'POST':
        vente.delete()
        messages.success(request, 'Vente supprimee.')
        return redirect('ventes:list')
    return render(request, 'ventes/delete.html', {'vente': vente})


@login_required
def client_create(request):
    farm = get_or_create_farm_profile(request.user, request=request)
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.farm = farm
            client.save()
            messages.success(request, 'Client ajouté.')
            return redirect('ventes:list')
    return redirect('ventes:list')
