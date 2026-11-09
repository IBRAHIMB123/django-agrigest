def farm_context(request):
    if not request.user.is_authenticated:
        return {}
    from .models import get_or_create_farm_profile
    farms = request.user.farm_profiles.all().order_by('created_at', 'pk')
    active_farm = get_or_create_farm_profile(request.user, request=request)
    return {
        'farms': farms,
        'active_farm': active_farm,
        'user_role': active_farm.role,
        'user_role_label': active_farm.role_label,
    }
