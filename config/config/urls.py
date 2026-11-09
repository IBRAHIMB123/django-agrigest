from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('apps.dashboard.urls', 'dashboard'), namespace='dashboard')),
    path('accounts/', include(('apps.accounts.urls', 'accounts'), namespace='accounts')),
    path('parcelles/', include(('apps.parcelles.urls', 'parcelles'), namespace='parcelles')),
    path('campagnes/', include(('apps.campaigns.urls', 'campaigns'), namespace='campaigns')),
    path('cultures/', include(('apps.cultures.urls', 'cultures'), namespace='cultures')),
    path('intrants/', include(('apps.intrants.urls', 'intrants'), namespace='intrants')),
    path('recoltes/', include(('apps.recoltes.urls', 'recoltes'), namespace='recoltes')),
    path('depenses/', include(('apps.depenses.urls', 'depenses'), namespace='depenses')),
    path('ventes/', include(('apps.ventes.urls', 'ventes'), namespace='ventes')),
    path('rapports/', include(('apps.rapports.urls', 'rapports'), namespace='rapports')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
