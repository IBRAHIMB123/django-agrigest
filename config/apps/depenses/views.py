from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models import Q
from django.shortcuts import redirect, render

from apps.accounts.models import get_or_create_farm_profile

from .forms import DepenseForm
from .models import Depense


@login_required
def depense_list(request):
    farm = get_or_create_farm_profile(request.user, request=request)
    depenses = Depense.objects.filter(farm=farm).order_by('-date')
    query = request.GET.get('q', '').strip()
    if query:
        depenses = depenses.filter(Q(description__icontains=query) | Q(campaign__name__icontains=query) | Q(category__icontains=query))
    if request.method == 'POST':
        form = DepenseForm(request.POST, farm=farm)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.farm = farm
            expense.save()
            messages.success(request, 'Dépense enregistrée.')
            return redirect('depenses:list')
    else:
        form = DepenseForm(farm=farm)
    total_amount = depenses.aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'depenses/depenses.html', {'depenses': depenses, 'form': form, 'total_amount': total_amount, 'query': query})
