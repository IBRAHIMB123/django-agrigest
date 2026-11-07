from django.conf import settings
from django.db import models


class FarmProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farm_profiles')
    name = models.CharField(max_length=120, default='Exploitation')
    location = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Exploitation'
        verbose_name_plural = 'Exploitations'

    def __str__(self):
        return self.name


def get_or_create_farm_profile(user, request=None):
    farms = FarmProfile.objects.filter(user=user).order_by('created_at', 'pk')
    if request is not None:
        selected_id = request.session.get('active_farm_id')
        if selected_id:
            selected_farm = farms.filter(pk=selected_id).first()
            if selected_farm:
                return selected_farm

    farm = farms.first()
    if farm:
        if request is not None:
            request.session['active_farm_id'] = farm.pk
        return farm

    default_name = f"{user.get_full_name().strip() or user.username} - Exploitation"
    farm = FarmProfile.objects.create(user=user, name=default_name)
    if request is not None:
        request.session['active_farm_id'] = farm.pk
    return farm
