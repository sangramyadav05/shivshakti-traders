import threading


_thread_locals = threading.local()


def set_current_request(request):
    _thread_locals.request = request


def get_current_request():
    return getattr(_thread_locals, 'request', None)


def clear_current_request():
    if hasattr(_thread_locals, 'request'):
        del _thread_locals.request


def get_current_user():
    request = get_current_request()
    if not request:
        return None
    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        return user
    return None


def get_current_ip():
    request = get_current_request()
    if not request:
        return None
    return getattr(request, '_audit_ip', None)
