from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import Profile


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            profile = getattr(request.user, 'profile', None)
            if not profile:
                profile = Profile.objects.create(user=request.user)
            if profile.role not in roles:
                messages.error(request, 'У вас нет прав для просмотра этого раздела.')
                return redirect('booking:dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
