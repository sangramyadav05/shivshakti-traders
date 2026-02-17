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

        from django.conf import settings

        for directive, setting_name in policy_map.items():
            sources = getattr(settings, setting_name, None)
            if not sources:
                continue
            policy_parts.append(f"{directive} {' '.join(sources)}")

        if policy_parts:
            response['Content-Security-Policy'] = '; '.join(policy_parts)

        return response
