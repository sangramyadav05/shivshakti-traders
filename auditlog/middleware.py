from ipaddress import ip_address

from django.conf import settings

from .context import clear_current_request, set_current_request
from .signals import dashboard_accessed


class AuditRequestContextMiddleware:
    """
    Stores request context (user + client IP) for signal-based audit logging.
    Also emits dashboard access audit signal.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request._audit_ip = self._get_client_ip(request)
        set_current_request(request)

        if self._is_dashboard_path(request.path):
            dashboard_accessed.send(sender=self.__class__, request=request)

        try:
            response = self.get_response(request)
        finally:
            clear_current_request()

        return response

    def _is_dashboard_path(self, path):
        return path == '/business-dashboard/' or path == '/business-dashboard'

    def _get_client_ip(self, request):
        remote_addr = (request.META.get('REMOTE_ADDR') or '').strip()

        # Trust X-Forwarded-For only when explicitly enabled.
        if getattr(settings, 'USE_X_FORWARDED_FOR', False):
            forwarded_for = (request.META.get('HTTP_X_FORWARDED_FOR') or '').strip()
            if forwarded_for:
                forwarded_chain = [part.strip() for part in forwarded_for.split(',') if part.strip()]
                if forwarded_chain:
                    return self._normalize_ip(forwarded_chain[0])

        return self._normalize_ip(remote_addr)

    def _normalize_ip(self, raw_ip):
        try:
            return str(ip_address(raw_ip))
        except ValueError:
            return None
