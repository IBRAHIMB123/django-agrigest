from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import get_or_create_farm_profile
from apps.cultures.models import Culture
from apps.depenses.models import Depense
from apps.parcelles.models import Parcelle
from apps.recoltes.models import Recolte
from apps.ventes.models import Vente
from apps.intrants.models import Intrant
from apps.campaigns.models import Campaign


@login_required
def dashboard_index(request):
    farm = get_or_create_farm_profile(request.user, request=request)

    parcels = Parcelle.objects.filter(farm=farm)
    cultures = Culture.objects.filter(farm=farm)
    total_area = parcels.aggregate(total=Sum('area'))['total'] or 0
    active_crops = cultures.filter(status__in=['en_croissance', 'floraison', 'maturite']).count()
    today = timezone.localdate()
    harvest_this_month = Recolte.objects.filter(farm=farm, harvested_date__year=today.year, harvested_date__month=today.month, unit='tonnes').aggregate(total=Sum('quantity'))['total'] or 0
    total_expenses = Depense.objects.filter(farm=farm).aggregate(total=Sum('amount'))['total'] or 0
    total_revenue = Vente.objects.filter(farm=farm).aggregate(total=Sum('total_amount'))['total'] or 0
    result_estimate = total_revenue - total_expenses

    recent_harvests = Recolte.objects.filter(farm=farm).select_related('culture', 'parcelle').order_by('-harvested_date')[:5]
    recent_sales = Vente.objects.filter(farm=farm).select_related('client').order_by('-sale_date')[:5]
    recent_expenses = Depense.objects.filter(farm=farm).select_related('campaign').order_by('-date')[:5]
    active_campaigns = Campaign.objects.filter(farm=farm, status='active').select_related('parcelle', 'culture')
    low_stock = [
        {'name': item.name, 'quantity': item.quantity, 'unit': item.unit}
        for item in Intrant.objects.filter(farm=farm, quantity__lte=F('min_stock'))[:5]
    ]
    top_parcel = parcels.order_by('-area').first()
    strongest_harvest = Recolte.objects.filter(farm=farm).select_related('culture', 'parcelle').order_by('-quantity').first()
    revenue_per_ha = (total_revenue / total_area) if total_area else 0
    field_watch = 'Aucune alerte' if not low_stock else f'{len(low_stock)} produit(s) à surveiller'

    chart_revenue = []
    for offset in range(6, -1, -1):
        month_index = today.month - 1 - offset
        year = today.year + month_index // 12
        month = month_index % 12 + 1
        month_sales = Vente.objects.filter(farm=farm, sale_date__year=year, sale_date__month=month).aggregate(total=Sum('total_amount'))['total'] or 0
        month_expenses = Depense.objects.filter(farm=farm, date__year=year, date__month=month).aggregate(total=Sum('amount'))['total'] or 0
        chart_revenue.append({'month': date(year, month, 1).strftime('%b'), 'revenus': float(month_sales), 'depenses': float(month_expenses)})

    crop_chart = [
        {'name': row['culture__name'], 'quantity': float(row['quantity'])}
        for row in Recolte.objects.filter(farm=farm, unit='tonnes', culture__isnull=False)
        .values('culture__name').annotate(quantity=Sum('quantity')).order_by('-quantity')[:5]
    ]
    parcel_chart = [
        {'name': row['name'], 'area': float(row['area'])}
        for row in parcels.values('name', 'area').order_by('-area')[:5]
    ]

    context = {
        'farm': farm,
        'today': today,
        'parcels': parcels,
        'cultures': cultures,
        'total_area': total_area,
        'active_crops': active_crops,
        'harvest_this_month': harvest_this_month,
        'total_expenses': total_expenses,
        'total_revenue': total_revenue,
        'result_estimate': result_estimate,
        'recent_harvests': recent_harvests,
        'recent_sales': recent_sales,
        'recent_expenses': recent_expenses,
        'active_campaigns': active_campaigns,
        'farm_count': request.user.farm_profiles.count(),
        'low_stock': low_stock,
        'top_parcel': top_parcel,
        'strongest_harvest': strongest_harvest,
        'revenue_per_ha': revenue_per_ha,
        'field_watch': field_watch,
        'revenue_chart': chart_revenue,
        'crop_chart': crop_chart,
        'parcel_chart': parcel_chart,
        'title': 'Tableau de bord',
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def search_global(request):
    farm = get_or_create_farm_profile(request.user, request=request)
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        results.extend(
            {'type': 'Parcelle', 'name': parcel.name, 'location': parcel.location, 'url': reverse('parcelles:detail', args=[parcel.pk])}
            for parcel in Parcelle.objects.filter(farm=farm, name__icontains=query)[:5]
        )
        results.extend(
            {'type': 'Culture', 'name': culture.name, 'location': culture.parcelle.name, 'url': reverse('cultures:list')}
            for culture in Culture.objects.filter(farm=farm, name__icontains=query).select_related('parcelle')[:5]
        )
        results.extend(
            {'type': 'Récolte', 'name': harvest.culture.name if harvest.culture else 'Récolte', 'location': harvest.parcelle.name if harvest.parcelle else '', 'url': reverse('recoltes:list')}
            for harvest in Recolte.objects.filter(farm=farm, culture__name__icontains=query).select_related('culture', 'parcelle')[:5]
        )
    return render(request, 'dashboard/search_results.html', {'query': query, 'results': results})
