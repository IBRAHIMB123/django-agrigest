import csv
from datetime import timedelta
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from apps.accounts.decorators import roles_required
from apps.accounts.models import FarmProfile
from apps.accounts.models import get_or_create_farm_profile
from apps.depenses.models import Depense
from apps.ventes.models import Vente

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
except Exception:  # pragma: no cover
    A4 = None
    getSampleStyleSheet = None
    Paragraph = None
    SimpleDocTemplate = None
    Spacer = None


@login_required
@roles_required(FarmProfile.ROLE_ADMIN)
def rapport_index(request):
    farm = get_or_create_farm_profile(request.user, request=request)
    period = request.GET.get('period', '30')
    if period not in {'7', '30', '90', '365'}:
        period = '30'
    days = int(period)
    until = timezone.localdate()
    since = until - timedelta(days=days - 1)
    ventes = Vente.objects.filter(farm=farm, sale_date__gte=since, sale_date__lte=until).select_related('client', 'campaign')
    depenses = Depense.objects.filter(farm=farm, date__gte=since, date__lte=until).select_related('campaign')
    revenue = ventes.aggregate(total=Sum('total_amount'))['total'] or 0
    expense = depenses.aggregate(total=Sum('amount'))['total'] or 0
    profit = revenue - expense
    context = {
        'period': period,
        'since': since,
        'until': until,
        'revenue': revenue,
        'expense': expense,
        'profit': profit,
        'ventes': ventes.order_by('-sale_date')[:10],
        'depenses': depenses.order_by('-date')[:10],
    }
    return render(request, 'rapports/rapports.html', context)


@login_required
@roles_required(FarmProfile.ROLE_ADMIN)
def export_csv(request):
    farm = get_or_create_farm_profile(request.user, request=request)
    period = request.GET.get('period', '30')
    if period not in {'7', '30', '90', '365'}:
        period = '30'
    until = timezone.localdate()
    since = until - timedelta(days=int(period) - 1)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="agristat.csv"'
    writer = csv.writer(response)
    writer.writerow(['Type', 'Date', 'Montant', 'Description'])
    for vente in Vente.objects.filter(farm=farm, sale_date__gte=since, sale_date__lte=until):
        writer.writerow(['Vente', vente.sale_date, str(vente.total_amount), vente.product_name])
    for depense in Depense.objects.filter(farm=farm, date__gte=since, date__lte=until):
        writer.writerow(['Dépense', depense.date, str(depense.amount), depense.description])
    return response


@login_required
@roles_required(FarmProfile.ROLE_ADMIN)
def export_pdf(request):
    farm = get_or_create_farm_profile(request.user, request=request)
    period = request.GET.get('period', '30')
    if period not in {'7', '30', '90', '365'}:
        period = '30'
    until = timezone.localdate()
    since = until - timedelta(days=int(period) - 1)
    buffer = BytesIO()
    if not SimpleDocTemplate:
        response = HttpResponse('ReportLab n\'est pas disponible dans cet environnement.', content_type='text/plain')
        return response
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph('Rapport AgriGest', styles['Title']),
        Paragraph(f'Exploitation: {farm.name}', styles['Heading2']),
        Paragraph(f'Periode: {since.strftime("%d/%m/%Y")} au {until.strftime("%d/%m/%Y")}', styles['BodyText']),
        Spacer(1, 12),
    ]
    for vente in Vente.objects.filter(farm=farm, sale_date__gte=since, sale_date__lte=until)[:10]:
        elements.append(Paragraph(f'- Vente: {vente.product_name} — {vente.total_amount} FCFA', styles['BodyText']))
    for depense in Depense.objects.filter(farm=farm, date__gte=since, date__lte=until)[:10]:
        elements.append(Paragraph(f'- Dépense: {depense.category} — {depense.amount} FCFA', styles['BodyText']))
    doc.build(elements)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="agri-rapport.pdf"'
    return response
