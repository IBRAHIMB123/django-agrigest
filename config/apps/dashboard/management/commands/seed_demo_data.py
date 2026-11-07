from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.accounts.models import FarmProfile
from apps.cultures.models import Culture
from apps.depenses.models import Depense
from apps.intrants.models import Intrant
from apps.parcelles.models import Parcelle
from apps.recoltes.models import Recolte
from apps.ventes.models import Client, Vente

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed demo AgriGest data for a sample farm.'

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username='ibrahim',
            defaults={'first_name': 'Ibrahim', 'last_name': 'Coulibaly', 'email': 'ibrahim@example.com', 'is_staff': True}
        )
        if created:
            user.set_password('AgriGest2026!')
            user.save()

        farm = FarmProfile.objects.filter(user=user, name='Exploitation Coulibaly').first() or FarmProfile.objects.filter(user=user).first()
        if not farm:
            farm = FarmProfile.objects.create(user=user, name='Exploitation Coulibaly', location='Bouake')
        user.refresh_from_db()

        parcels = [
            Parcelle.objects.get_or_create(farm=farm, name='Parcelle Nord', location='Mankono', area=28.5, soil_type='argilo_limoneux', status='active')[0],
            Parcelle.objects.get_or_create(farm=farm, name='Parcelle Est', location='Bouaké', area=18.0, soil_type='limoneux', status='harvest')[0],
            Parcelle.objects.get_or_create(farm=farm, name='Parcelle Sud', location='Korhogo', area=34.2, soil_type='sablo_argileux', status='active')[0],
        ]

        if not Culture.objects.filter(farm=farm).exists():
            cultures = [
                Culture.objects.create(farm=farm, parcelle=parcels[0], name='Maïs', variety='EVDT97', planted_date=date.today() - timedelta(days=120), expected_harvest_date=date.today() + timedelta(days=30), stage='floraison', status='en_croissance', health_score=88),
                Culture.objects.create(farm=farm, parcelle=parcels[1], name='Riz', variety='WITA4', planted_date=date.today() - timedelta(days=180), expected_harvest_date=date.today() + timedelta(days=15), stage='maturite', status='maturite', health_score=95),
                Culture.objects.create(farm=farm, parcelle=parcels[2], name='Coton', variety='ISA205', planted_date=date.today() - timedelta(days=100), expected_harvest_date=date.today() + timedelta(days=60), stage='croissance', status='en_croissance', health_score=80),
            ]
        else:
            cultures = list(Culture.objects.filter(farm=farm))

        if not Intrant.objects.filter(farm=farm).exists():
            Intrant.objects.create(farm=farm, name='Semences maïs', category='semence', unit='kg', quantity=480, min_stock=200, unit_price=1200, supplier='AGRIDEV CI')
            Intrant.objects.create(farm=farm, name='Engrais NPK', category='engrais', unit='kg', quantity=180, min_stock=150, unit_price=1300, supplier='AGRIPRO')

        if not Client.objects.filter(farm=farm).exists():
            client = Client.objects.create(farm=farm, name='Mali Agro', phone='+223 00 00 00 00', email='maliagro@example.com')
        else:
            client = Client.objects.filter(farm=farm).first()

        if not Vente.objects.filter(farm=farm).exists():
            Vente.objects.create(farm=farm, client=client, product_name='Maïs local', quantity=120, unit_price=1800, sale_date=date.today() - timedelta(days=5))
            Vente.objects.create(farm=farm, client=client, product_name='Riz paddy', quantity=90, unit_price=2200, sale_date=date.today() - timedelta(days=12))

        if not Depense.objects.filter(farm=farm).exists():
            Depense.objects.create(farm=farm, category='intrants', amount=750000, date=date.today() - timedelta(days=3), description='Achat engrais')
            Depense.objects.create(farm=farm, category='transport', amount=350000, date=date.today() - timedelta(days=10), description='Transport récoltes')

        if not Recolte.objects.filter(farm=farm).exists():
            Recolte.objects.create(farm=farm, culture=cultures[0], parcelle=parcels[0], harvested_date=date.today() - timedelta(days=14), quantity=34, unit='tonnes', yield_per_ha=8.2)
            Recolte.objects.create(farm=farm, culture=cultures[1], parcelle=parcels[1], harvested_date=date.today() - timedelta(days=7), quantity=18, unit='tonnes', yield_per_ha=5.8)

        self.stdout.write(self.style.SUCCESS('Demo data ready for ibrahim / AgriGest2026!'))
