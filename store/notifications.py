from __future__ import annotations

from typing import Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from django.conf import settings
from django.core.mail import send_mail


def send_admin_order_email(*, subject: str, message: str, html_message: Optional[str] = None) -> bool:
    admin_email = getattr(settings, 'ADMIN_EMAIL', None) or 'admin@example.com'
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'noreply@example.com'
    try:
        send_mail(subject, message, from_email, [admin_email], html_message=html_message)
        return True
    except Exception:
        return False


def send_sms_via_africastalking(*, phone_number: str, message: str) -> bool:
    """Send SMS using Africa's Talking sandbox REST API.

    Expects settings:
      - AFRICASTALKING_USERNAME (default: 'sandbox')
      - AFRICASTALKING_API_KEY (no default; if missing, function no-ops)
      - AFRICASTALKING_SENDER_ID (optional)
    """
    api_key = getattr(settings, 'AFRICASTALKING_API_KEY', None)
    username = getattr(settings, 'AFRICASTALKING_USERNAME', 'sandbox')
    sender_id = getattr(settings, 'AFRICASTALKING_SENDER_ID', None)

    if not api_key:
        # Not configured; skip sending gracefully
        return False

    endpoint = 'https://api.sandbox.africastalking.com/version1/messaging'
    headers = {
        'apiKey': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    payload = {
        'username': username,
        'to': phone_number,
        'message': message,
    }
    if sender_id:
        payload['from'] = sender_id

    data = urlencode(payload).encode('utf-8')
    request = Request(endpoint, data=data, headers=headers, method='POST')
    try:
        with urlopen(request, timeout=10) as response:
            return 200 <= response.status < 300
    except (HTTPError, URLError):
        return False


