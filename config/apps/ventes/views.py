from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.decorators import roles_required
from apps.accounts.models import FarmProfile
from apps.accounts.models import get_or_create_farm_profile

from .forms import ClientForm, HarvestListingForm, HarvestOrderForm, VenteForm
from .models import Client, HarvestListing, HarvestOrder, Vente


@login_required
@roles_required(FarmProfile.ROLE_ADMIN)
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
@roles_required(FarmProfile.ROLE_ADMIN)
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
@roles_required(FarmProfile.ROLE_ADMIN)
def vente_delete(request, pk):
    farm = get_or_create_farm_profile(request.user, request=request)
    vente = get_object_or_404(Vente, pk=pk, farm=farm)
    if request.method == 'POST':
        vente.delete()
        messages.success(request, 'Vente supprimee.')
        return redirect('ventes:list')
    return render(request, 'ventes/delete.html', {'vente': vente})


@login_required
@roles_required(FarmProfile.ROLE_ADMIN)
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


@login_required
@roles_required(FarmProfile.ROLE_CLIENT)
def marketplace(request):
    listings = HarvestListing.objects.filter(is_active=True).select_related('farm').order_by('-created_at')
    query = request.GET.get('q', '').strip()
    if query:
        listings = listings.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(farm__name__icontains=query))
    return render(request, 'ventes/marketplace.html', {'listings': listings[:100], 'query': query})


@login_required
@roles_required(FarmProfile.ROLE_ADMIN)
def listing_list(request):
    farm = get_or_create_farm_profile(request.user, request=request)
    listings = HarvestListing.objects.filter(farm=farm)
    if request.method == 'POST':
        form = HarvestListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.farm = farm
            listing.save()
            messages.success(request, 'Votre annonce de récolte est publiée.')
            return redirect('ventes:listings')
    else:
        form = HarvestListingForm()
    return render(request, 'ventes/listings.html', {'listings': listings, 'form': form})


@login_required
@roles_required(FarmProfile.ROLE_ADMIN)
def listing_edit(request, pk):
    farm = get_or_create_farm_profile(request.user, request=request)
    listing = get_object_or_404(HarvestListing, pk=pk, farm=farm)
    if request.method == 'POST':
        form = HarvestListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Annonce mise à jour.')
            return redirect('ventes:listings')
    else:
        form = HarvestListingForm(instance=listing)
    return render(request, 'ventes/listing_form.html', {'form': form, 'listing': listing})


@login_required
@roles_required(FarmProfile.ROLE_CLIENT)
def order_create(request, listing_id):
    listing = get_object_or_404(HarvestListing, pk=listing_id, is_active=True)
    if request.method != 'POST':
        return redirect('ventes:marketplace')
    form = HarvestOrderForm(request.POST, listing=listing)
    if not form.is_valid():
        errors = '; '.join(str(error) for field_errors in form.errors.values() for error in field_errors)
        messages.error(request, f'Commande invalide : {errors}')
        return redirect('ventes:marketplace')
    order = form.save(commit=False)
    order.listing = listing
    order.buyer = request.user
    order.fulfillment = listing.fulfillment
    order.price_per_kg = listing.price_per_kg
    order.total_amount = order.quantity_kg * listing.price_per_kg
    order.save()
    messages.success(request, 'Demande envoyée au vendeur. Elle sera réservée après confirmation.')
    return redirect('ventes:orders')


@login_required
def order_list(request):
    farm = get_or_create_farm_profile(request.user, request=request)
    if farm.role == FarmProfile.ROLE_ADMIN:
        orders = HarvestOrder.objects.filter(listing__farm=farm).select_related('listing', 'buyer')
        is_seller = True
    elif farm.role == FarmProfile.ROLE_CLIENT:
        orders = HarvestOrder.objects.filter(buyer=request.user).select_related('listing', 'listing__farm')
        is_seller = False
    else:
        messages.error(request, "Cette fonctionnalité n'est pas accessible avec votre rôle.")
        return redirect('dashboard:index')
    return render(request, 'ventes/orders.html', {'orders': orders, 'is_seller': is_seller})


@login_required
def order_update(request, pk):
    if request.method != 'POST':
        return redirect('ventes:orders')
    farm = get_or_create_farm_profile(request.user, request=request)
    if farm.role not in (FarmProfile.ROLE_ADMIN, FarmProfile.ROLE_CLIENT):
        messages.error(request, "Cette fonctionnalité n'est pas accessible avec votre rôle.")
        return redirect('dashboard:index')

    action = request.POST.get('action')
    with transaction.atomic():
        order = get_object_or_404(
            HarvestOrder.objects.select_for_update().select_related('listing'),
            pk=pk,
            **({'listing__farm': farm} if farm.role == FarmProfile.ROLE_ADMIN else {'buyer': request.user}),
        )
        if farm.role == FarmProfile.ROLE_ADMIN and action in ('confirm', 'reject', 'complete'):
            if action == 'confirm' and order.status == HarvestOrder.STATUS_PENDING:
                transitioned = HarvestOrder.objects.filter(
                    pk=order.pk, status=HarvestOrder.STATUS_PENDING,
                ).update(status=HarvestOrder.STATUS_CONFIRMED, updated_at=timezone.now())
                if not transitioned:
                    messages.error(request, "Cette commande a déjà été traitée.")
                    return redirect('ventes:orders')
                reserved = HarvestListing.objects.filter(
                    pk=order.listing_id,
                    quantity_kg__gte=order.quantity_kg,
                ).update(
                    quantity_kg=F('quantity_kg') - order.quantity_kg,
                    updated_at=timezone.now(),
                )
                if not reserved:
                    transaction.set_rollback(True)
                    messages.error(request, 'Stock insuffisant : cette commande ne peut pas être confirmée.')
                    return redirect('ventes:orders')
                order.status = HarvestOrder.STATUS_CONFIRMED
            elif action == 'reject' and order.status == HarvestOrder.STATUS_PENDING:
                transitioned = HarvestOrder.objects.filter(
                    pk=order.pk, status=HarvestOrder.STATUS_PENDING,
                ).update(status=HarvestOrder.STATUS_REJECTED, updated_at=timezone.now())
                if not transitioned:
                    messages.error(request, "Cette commande a déjà été traitée.")
                    return redirect('ventes:orders')
                order.status = HarvestOrder.STATUS_REJECTED
            elif action == 'complete' and order.status == HarvestOrder.STATUS_CONFIRMED:
                transitioned = HarvestOrder.objects.filter(
                    pk=order.pk, status=HarvestOrder.STATUS_CONFIRMED,
                ).update(status=HarvestOrder.STATUS_COMPLETED, updated_at=timezone.now())
                if not transitioned:
                    messages.error(request, "Cette commande a déjà été mise à jour.")
                    return redirect('ventes:orders')
                order.status = HarvestOrder.STATUS_COMPLETED
            else:
                messages.error(request, "Cette action n'est pas possible pour l'état actuel de la commande.")
                return redirect('ventes:orders')
        elif farm.role == FarmProfile.ROLE_CLIENT and action == 'cancel':
            if order.status not in (HarvestOrder.STATUS_PENDING, HarvestOrder.STATUS_CONFIRMED):
                messages.error(request, "Cette commande ne peut plus être annulée.")
                return redirect('ventes:orders')
            previous_status = order.status
            transitioned = HarvestOrder.objects.filter(
                pk=order.pk,
                status__in=[HarvestOrder.STATUS_PENDING, HarvestOrder.STATUS_CONFIRMED],
            ).update(status=HarvestOrder.STATUS_CANCELLED, updated_at=timezone.now())
            if not transitioned:
                messages.error(request, "Cette commande a déjà été traitée.")
                return redirect('ventes:orders')
            if previous_status == HarvestOrder.STATUS_CONFIRMED:
                HarvestListing.objects.filter(pk=order.listing_id).update(
                    quantity_kg=F('quantity_kg') + order.quantity_kg,
                    updated_at=timezone.now(),
                )
            order.status = HarvestOrder.STATUS_CANCELLED
        else:
            messages.error(request, "Cette action n'est pas autorisée.")
            return redirect('ventes:orders')

    messages.success(request, 'Statut de la commande mis à jour.')
    return redirect('ventes:orders')
