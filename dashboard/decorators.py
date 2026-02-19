from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import DashboardUser

DASHBOARD_SESSION_KEY = 'dashboard_user_id'


def _apply_no_cache_headers(response):
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


def dashboard_no_cache(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        return _apply_no_cache_headers(response)

    return _wrapped


def dashboard_login_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        dashboard_user_id = request.session.get(DASHBOARD_SESSION_KEY)

        if not dashboard_user_id:
            messages.warning(request, 'Please login again to access dashboard.')
            return redirect('dashboard:dashboard_login')

        dashboard_user = (
            DashboardUser.objects.filter(id=dashboard_user_id, is_active=True)
            .only('id', 'username')
            .first()
        )
        if dashboard_user is None:
            request.session.pop(DASHBOARD_SESSION_KEY, None)
            messages.warning(request, 'Please login again to access dashboard.')
            return redirect('dashboard:dashboard_login')

        request.dashboard_user = dashboard_user
        return view_func(request, *args, **kwargs)

    return _wrapped
