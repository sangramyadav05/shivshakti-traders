from ipaddress import ip_address

from django.conf import settings
from django.http import HttpResponseForbidden


class ContentSecurityPolicyMiddleware:
    """
    Lightweight CSP middleware using Django settings values.
    Keeps policy centralized without external dependencies.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        policy_parts = []
        policy_map = {
            'default-src': 'CSP_DEFAULT_SRC',
            'script-src': 'CSP_SCRIPT_SRC',
            'style-src': 'CSP_STYLE_SRC',
            'font-src': 'CSP_FONT_SRC',
            'img-src': 'CSP_IMG_SRC',
            'connect-src': 'CSP_CONNECT_SRC',
            'frame-src': 'CSP_FRAME_SRC',
            'object-src': 'CSP_OBJECT_SRC',
            'base-uri': 'CSP_BASE_URI',
            'frame-ancestors': 'CSP_FRAME_ANCESTORS',
        }

        for directive, setting_name in policy_map.items():
            sources = getattr(settings, setting_name, None)
            if not sources:
                continue
            policy_parts.append(f"{directive} {' '.join(sources)}")

        if policy_parts:
            response['Content-Security-Policy'] = '; '.join(policy_parts)

        return response


class AdminIPAllowlistMiddleware:
    """
    Restrict sensitive business/admin routes to allowed source IPs.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._is_protected_path(request.path):
            allowed_ips = set(getattr(settings, 'ALLOWED_ADMIN_IPS', []))
            if not allowed_ips:
                return HttpResponseForbidden('Admin access is not configured for this source.')

            client_ip = self._get_client_ip(request)
            if not client_ip or client_ip not in allowed_ips:
                return HttpResponseForbidden('Forbidden')

        return self.get_response(request)

    def _is_protected_path(self, path):
        admin_url = '/' + getattr(settings, 'ADMIN_URL', 'secure-control-panel/').lstrip('/')
        if not admin_url.endswith('/'):
            admin_url = f'{admin_url}/'
        return path.startswith(admin_url) or path.startswith('/business-dashboard/') or path == '/business-dashboard'

    def _get_client_ip(self, request):
        remote_addr = (request.META.get('REMOTE_ADDR') or '').strip()

        # Trust X-Forwarded-For only when explicitly enabled in settings.
        if getattr(settings, 'USE_X_FORWARDED_FOR', False):
            xff = (request.META.get('HTTP_X_FORWARDED_FOR') or '').strip()
            if xff:
                forwarded_chain = [part.strip() for part in xff.split(',') if part.strip()]
                if forwarded_chain:
                    candidate = forwarded_chain[0]
                    return self._normalize_ip(candidate)

        return self._normalize_ip(remote_addr)

    def _normalize_ip(self, raw_ip):
        try:
            return str(ip_address(raw_ip))
        except ValueError:
            return None

