from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from apps.accounts.decorators import roles_required
from apps.accounts.models import FarmProfile, get_or_create_farm_profile
from apps.cultures.models import Culture
from apps.depenses.models import Depense
from apps.parcelles.models import Parcelle
from apps.recoltes.models import Recolte
from apps.ventes.models import HarvestListing, HarvestOrder, Vente
from apps.intrants.models import Intrant
from apps.campaigns.models import Campaign


ROLE_DASHBOARD_TEMPLATES = {
    FarmProfile.ROLE_ADMIN: 'dashboard/roles/admin.html',
    FarmProfile.ROLE_WORKER: 'dashboard/roles/worker.html',
    FarmProfile.ROLE_CLIENT: 'dashboard/roles/client.html',
}


def _dashboard_context(request, farm):
    is_client = farm.role == FarmProfile.ROLE_CLIENT
    parcels = Parcelle.objects.filter(farm=farm)
    cultures = Culture.objects.filter(farm=farm)
    total_area = parcels.aggregate(total=Sum('area'))['total'] or 0
    active_crops = cultures.filter(status__in=['en_croissance', 'floraison', 'maturite']).count()
    today = timezone.localdate()
    harvest_this_month = Recolte.objects.filter(farm=farm, harvested_date__year=today.year, harvested_date__month=today.month, unit='tonnes').aggregate(total=Sum('quantity'))['total'] or 0
    total_expenses = 0 if is_client else Depense.objects.filter(farm=farm).aggregate(total=Sum('amount'))['total'] or 0
    total_revenue = 0 if is_client else Vente.objects.filter(farm=farm).aggregate(total=Sum('total_amount'))['total'] or 0
    result_estimate = total_revenue - total_expenses

    recent_harvests = [] if is_client else Recolte.objects.filter(farm=farm).select_related('culture', 'parcelle').order_by('-harvested_date')[:5]
    recent_sales = [] if is_client else Vente.objects.filter(farm=farm).select_related('client').order_by('-sale_date')[:5]
    recent_expenses = [] if is_client else Depense.objects.filter(farm=farm).select_related('campaign').order_by('-date')[:5]
    active_campaigns = Campaign.objects.none() if is_client else Campaign.objects.filter(farm=farm, status='active').select_related('parcelle', 'culture')
    client_orders = HarvestOrder.objects.filter(buyer=request.user).select_related('listing').order_by('-created_at')[:5] if is_client else []
    low_stock = [
        {'name': item.name, 'quantity': item.quantity, 'unit': item.unit}
        for item in Intrant.objects.filter(farm=farm, quantity__lte=F('min_stock'))[:5]
    ]
    top_parcel = None if is_client else parcels.order_by('-area').first()
    strongest_harvest = None if is_client else Recolte.objects.filter(farm=farm).select_related('culture', 'parcelle').order_by('-quantity').first()
    revenue_per_ha = (total_revenue / total_area) if total_area else 0
    field_watch = 'Aucune alerte' if not low_stock else f'{len(low_stock)} produit(s) à surveiller'

    chart_revenue = []
    for offset in range(6, -1, -1) if not is_client else []:
        month_index = today.month - 1 - offset
        year = today.year + month_index // 12
        month = month_index % 12 + 1
        month_sales = Vente.objects.filter(farm=farm, sale_date__year=year, sale_date__month=month).aggregate(total=Sum('total_amount'))['total'] or 0
        month_expenses = Depense.objects.filter(farm=farm, date__year=year, date__month=month).aggregate(total=Sum('amount'))['total'] or 0
        chart_revenue.append({'month': date(year, month, 1).strftime('%b'), 'revenus': float(month_sales), 'depenses': float(month_expenses)})

    crop_production = [] if is_client else list(
        Recolte.objects.filter(farm=farm, unit='tonnes', culture__isnull=False)
        .values('culture__name').annotate(quantity=Sum('quantity')).order_by('-quantity')
    )
    production_total = sum((row['quantity'] for row in crop_production), 0)
    crop_chart = []
    segment_offset = 0
    for row in crop_production[:5]:
        quantity = float(row['quantity'])
        segment_length = (quantity / float(production_total) * 276.46) if production_total else 0
        crop_chart.append({
            'name': row['culture__name'],
            'quantity': quantity,
            'share': round((quantity / float(production_total) * 100), 1) if production_total else 0,
            'segment_length': round(segment_length, 2),
            'segment_offset': round(segment_offset, 2),
        })
        segment_offset += segment_length
    crop_colors = ['#d4ec70', '#9cce5a', '#53b17c', '#f0be65', '#d98956']
    for index, item in enumerate(crop_chart):
        item['color'] = crop_colors[index]
    parcel_chart = [] if is_client else [
        {'name': row['name'], 'area': float(row['area'])}
        for row in parcels.values('name', 'area').order_by('-area')[:5]
    ]

    role_label_map = {
        FarmProfile.ROLE_ADMIN: 'Administrateur',
        FarmProfile.ROLE_WORKER: 'Agent de terrain',
        FarmProfile.ROLE_CLIENT: 'Client',
    }

    role_summary = {
        FarmProfile.ROLE_ADMIN: {
            'header': 'Pilotage stratégique du champ',
            'description': 'Suivez en direct les performances, les dépenses et la rentabilité globale.',
            'accent': 'admin',
        },
        FarmProfile.ROLE_WORKER: {
            'header': 'Coordination terrain',
            'description': 'Planifiez les interventions, suivez les cultures et gardez la production en mouvement.',
            'accent': 'worker',
        },
        FarmProfile.ROLE_CLIENT: {
            'header': 'Suivi client et achats',
            'description': 'Consultez les récoltes, les volumes livrés et les transactions associées.',
            'accent': 'client',
        },
    }

    return {
        'farm': farm,
        'role': farm.role,
        'dashboard_template': ROLE_DASHBOARD_TEMPLATES.get(
            farm.role, ROLE_DASHBOARD_TEMPLATES[FarmProfile.ROLE_ADMIN]
        ),
        'role_label': role_label_map.get(farm.role, role_label_map[FarmProfile.ROLE_ADMIN]),
        'role_summary': role_summary.get(farm.role, role_summary[FarmProfile.ROLE_ADMIN]),
        'today': today,
        'parcels': parcels,
        'cultures': cultures,
        'total_area': total_area,
        'active_crops': active_crops,
        'harvest_this_month': harvest_this_month,
        'production_total': production_total,
        'sales_count': 0 if is_client else Vente.objects.filter(farm=farm).count(),
        'client_orders': client_orders,
        'client_order_count': HarvestOrder.objects.filter(buyer=request.user).count() if is_client else 0,
        'marketplace_count': HarvestListing.objects.filter(is_active=True).count() if is_client else 0,
        'culture_count': cultures.count(),
        'active_campaign_count': active_campaigns.count(),
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


def _render_dashboard(request, farm):
    return render(request, 'dashboard/dashboard.html', _dashboard_context(request, farm))


def home(request):
    return render(request, 'landing.html', {'is_public_page': True})


@login_required
def dashboard_index(request):
    farm = get_or_create_farm_profile(request.user, request=request)
    return _render_dashboard(request, farm)


@login_required
def admin_dashboard(request):
    farm = get_or_create_farm_profile(request.user, request=request)
    if farm.role != FarmProfile.ROLE_ADMIN:
        return redirect('dashboard:index')
    return _render_dashboard(request, farm)


@login_required
def worker_dashboard(request):
    farm = get_or_create_farm_profile(request.user, request=request)
    if farm.role != FarmProfile.ROLE_WORKER:
        return redirect('dashboard:index')
    return _render_dashboard(request, farm)


@login_required
def client_dashboard(request):
    farm = get_or_create_farm_profile(request.user, request=request)
    if farm.role != FarmProfile.ROLE_CLIENT:
        return redirect('dashboard:index')
    return _render_dashboard(request, farm)


@login_required
@roles_required(FarmProfile.ROLE_ADMIN, FarmProfile.ROLE_WORKER)
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
