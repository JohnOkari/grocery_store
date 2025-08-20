from django.core import mail
from django.test import override_settings
from django.core.mail import EmailMessage
from typing import List, cast

from store.notifications import send_admin_order_email, send_sms_via_africastalking


def test_send_admin_order_email_uses_locmem_backend(settings):
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    settings.ADMIN_EMAIL = 'admin@example.com'
    ok = send_admin_order_email(subject="Hello", message="World")
    assert ok is True
    outbox = cast(List[EmailMessage], getattr(mail, "outbox", []))
    assert len(outbox) == 1
    assert outbox[0].subject == "Hello"


def test_send_sms_via_africastalking_requires_api_key(settings, monkeypatch):
    settings.AFRICASTALKING_API_KEY = ''
    assert send_sms_via_africastalking(phone_number='0700000000', message='Hi') is False

    settings.AFRICASTALKING_API_KEY = 'key'

    class FakeResponse:
        status = 201

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_urlopen(req, timeout=10):  # noqa: ANN001
        return FakeResponse()

    monkeypatch.setattr('store.notifications.urlopen', fake_urlopen)
    assert send_sms_via_africastalking(phone_number='0700000000', message='Hi') is True


