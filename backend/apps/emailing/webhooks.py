"""Authenticated Resend webhook endpoint for email delivery outcomes."""

import base64
import binascii
import hashlib
import hmac
import json
import time

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


def _verify_resend_signature(request) -> bool:
    """Verify Svix-style Resend webhook signatures against the raw request body."""
    secret = str(getattr(settings, "RESEND_WEBHOOK_SECRET", "") or "").strip()
    message_id = request.headers.get("svix-id", "").strip()
    timestamp = request.headers.get("svix-timestamp", "").strip()
    signature_header = request.headers.get("svix-signature", "").strip()
    if not (secret and message_id and timestamp and signature_header):
        return False

    try:
        timestamp_number = int(timestamp)
        if abs(time.time() - timestamp_number) > 300:
            return False
        encoded_secret = secret.removeprefix("whsec_")
        secret_bytes = base64.b64decode(encoded_secret, validate=True)
    except (ValueError, binascii.Error):
        return False

    signed_payload = (
        message_id.encode("utf-8")
        + b"."
        + timestamp.encode("ascii")
        + b"."
        + request.body
    )
    expected = base64.b64encode(
        hmac.new(secret_bytes, signed_payload, hashlib.sha256).digest()
    ).decode("ascii")

    for item in signature_header.split():
        version, separator, candidate = item.partition(",")
        if separator and version == "v1" and hmac.compare_digest(expected, candidate):
            return True
    return False


@csrf_exempt
@require_POST
def resend_webhook(request):
    """Apply signed Resend lifecycle events to matching Delivery rows."""
    if not getattr(settings, "RESEND_WEBHOOK_SECRET", ""):
        return JsonResponse({"error": "Webhook secret is not configured."}, status=503)
    if not _verify_resend_signature(request):
        return JsonResponse({"error": "Invalid webhook signature."}, status=401)

    try:
        event = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    if not isinstance(event, dict):
        return JsonResponse({"error": "Invalid event payload."}, status=400)

    event_type = event.get("type")
    state_by_event = {
        "email.sent": "sent",
        "email.delivered": "delivered",
        "email.delivery_delayed": "delayed",
        "email.bounced": "bounced",
        "email.complained": "complained",
        "email.suppressed": "suppressed",
    }
    target_state = state_by_event.get(event_type)
    if target_state is None:
        return JsonResponse({"ok": True, "ignored": True})

    data = event.get("data")
    email_id = data.get("email_id") if isinstance(data, dict) else None
    if not email_id:
        return JsonResponse({"error": "Event is missing data.email_id."}, status=400)

    from apps.emailing.models import Delivery

    updated = Delivery.objects.filter(
        provider="resend",
        provider_message_id=email_id,
    ).update(state=target_state)
    if not updated:
        # Resend retries non-2xx webhook deliveries. This also covers the very
        # small race where the webhook arrives before the send response is saved.
        return JsonResponse({"error": "Email delivery record is not available yet."}, status=503)

    return JsonResponse({"ok": True, "updated": updated})
