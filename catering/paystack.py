"""Minimal Paystack client (standard library only)."""
import hashlib
import hmac
import json
import urllib.error
import urllib.request

from django.conf import settings

API = "https://api.paystack.co"


class PaystackError(Exception):
    pass


def _call(path, payload=None):
    if not settings.PAYSTACK_SECRET_KEY:
        raise PaystackError("PAYSTACK_SECRET_KEY is not set")
    req = urllib.request.Request(
        API + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                 "Content-Type": "application/json"},
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.load(resp)
    except (urllib.error.URLError, ValueError) as exc:
        raise PaystackError(str(exc))
    if not body.get("status"):
        raise PaystackError(body.get("message", "Paystack error"))
    return body["data"]


def to_kobo(amount):
    return int(amount * 100)


def initialize(payment, callback_url):
    data = _call("/transaction/initialize", {
        "email": payment.enquiry.email,
        "amount": to_kobo(payment.amount),
        "currency": "NGN",
        "reference": payment.reference,
        "callback_url": callback_url,
        "metadata": {"order": payment.enquiry.reference, "name": payment.enquiry.name},
    })
    return data["authorization_url"]


def valid_signature(raw_body, signature):
    expected = hmac.new(settings.PAYSTACK_SECRET_KEY.encode(), raw_body, hashlib.sha512).hexdigest()
    return bool(signature) and hmac.compare_digest(expected, signature)


def settle(reference):
    """Verify a transaction with Paystack and mark our Payment successful if everything matches."""
    from .models import Payment
    payment = Payment.objects.filter(reference=reference, method=Payment.PAYSTACK).first()
    if payment is None:
        return None
    try:
        data = _call(f"/transaction/verify/{reference}")
    except PaystackError:
        return payment
    if (data.get("status") == "success" and data.get("currency") == "NGN"
            and data.get("amount") == to_kobo(payment.amount)):
        payment.mark_success()
    elif data.get("status") in ("failed", "abandoned") and payment.status == Payment.PENDING:
        payment.status = Payment.FAILED
        payment.save(update_fields=["status"])
    return payment
