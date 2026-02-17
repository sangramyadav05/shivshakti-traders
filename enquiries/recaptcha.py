import json
import logging
import urllib.parse
import urllib.request
from django.conf import settings

logger = logging.getLogger('enquiries')


def verify_recaptcha(token, remote_ip=None):
    if not settings.RECAPTCHA_ENABLED:
        return True

    if not token:
        return False

    payload = {
        'secret': settings.RECAPTCHA_SECRET_KEY,
        'response': token,
    }
    if remote_ip:
        payload['remoteip'] = remote_ip

    data = urllib.parse.urlencode(payload).encode('utf-8')
    request = urllib.request.Request(settings.RECAPTCHA_VERIFY_URL, data=data)

    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            result = json.loads(response.read().decode('utf-8'))
    except Exception:
        logger.exception('reCAPTCHA verification failed due to request error')
        return False

    return bool(result.get('success'))
