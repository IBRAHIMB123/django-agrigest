from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import get_or_create_farm_profile
from .forms import CampaignForm
from .models import Campaign


@login_required
def campaign_list(request):
    farm = get_or_create_farm_profile(request.user, request=request)
    campaigns = Campaign.objects.filter(farm=farm).select_related('parcelle', 'culture')
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    if query:
        campaigns = campaigns.filter(Q(name__icontains=query) | Q(culture__name__icontains=query) | Q(parcelle__name__icontains=query))
    if status in dict(Campaign.STATUS_CHOICES):
        campaigns = campaigns.filter(status=status)
    if request.method == 'POST':
        form = CampaignForm(request.POST, farm=farm)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.farm = farm
            campaign.save()
            messages.success(request, 'Campagne enregistree.')
            return redirect('campaigns:list')
    else:
        form = CampaignForm(farm=farm)
    return render(request, 'campaigns/list.html', {'campaigns': campaigns, 'form': form, 'query': query, 'status': status, 'status_choices': Campaign.STATUS_CHOICES})


@login_required
def campaign_edit(request, pk):
    farm = get_or_create_farm_profile(request.user, request=request)
    campaign = get_object_or_404(Campaign, pk=pk, farm=farm)
    if request.method == 'POST':
        form = CampaignForm(request.POST, instance=campaign, farm=farm)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campagne mise a jour.')
            return redirect('campaigns:list')
    else:
        form = CampaignForm(instance=campaign, farm=farm)
    return render(request, 'campaigns/edit.html', {'campaign': campaign, 'form': form})


@login_required
def campaign_delete(request, pk):
    farm = get_or_create_farm_profile(request.user, request=request)
    campaign = get_object_or_404(Campaign, pk=pk, farm=farm)
    if request.method == 'POST':
        campaign.delete()
        messages.success(request, 'Campagne supprimee.')
        return redirect('campaigns:list')
    return render(request, 'campaigns/delete.html', {'campaign': campaign})
