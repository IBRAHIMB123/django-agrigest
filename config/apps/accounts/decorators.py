from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import get_or_create_farm_profile


def roles_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            farm = get_or_create_farm_profile(request.user, request=request)
            if farm.role not in roles:
                messages.error(request, "Cette fonctionnalité n'est pas accessible avec votre rôle.")
                return redirect('dashboard:index')
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator
