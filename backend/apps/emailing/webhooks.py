"""Authenticated Resend webhook endpoint for email delivery outcomes."""

import base64
import binascii
import hashlib
import hmac
import json
import time

from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
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
    """Apply signed Resend lifecycle events to matching recipient delivery rows."""
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
        "email.failed": "failed",
        "email.bounced": "bounced",
        "email.complained": "complained",
        "email.suppressed": "suppressed",
    }
    target_state = state_by_event.get(event_type)
    if target_state is None:
        return JsonResponse({"ok": True, "ignored": True})

    data = event.get("data")
    if not isinstance(data, dict):
        return JsonResponse({"error": "Invalid event data."}, status=400)

    email_id = data.get("email_id")
    recipients = data.get("to")
    if not email_id:
        return JsonResponse({"error": "Event is missing data.email_id."}, status=400)
    if (
        not isinstance(recipients, list)
        or not recipients
        or any(not isinstance(item, str) or not item.strip() for item in recipients)
    ):
        return JsonResponse({"error": "Event is missing valid data.to recipients."}, status=400)

    from apps.emailing.models import Delivery

    matching_email = Delivery.objects.filter(
        provider="resend",
        provider_message_id=email_id,
    )
    if not matching_email.exists():
        # Resend retries non-2xx webhook deliveries. This also covers the very
        # small race where the webhook arrives before the send response is saved.
        return JsonResponse({"error": "Email delivery record is not available yet."}, status=503)

    # Resend now emits recipient-scoped lifecycle events. Match data.to as well
    # as email_id, because one recipient can bounce while another delivers.
    recipient_filter = Q()
    for recipient in recipients:
        recipient_filter |= Q(to_email__iexact=recipient.strip())
    delivery_qs = matching_email.filter(recipient_filter)

    # Webhooks can be retried or arrive out of order. A late "sent" or
    # "delivery delayed" event must never downgrade a confirmed delivery,
    # bounce, complaint, failure, or suppression outcome.
    protected_states_by_event = {
        "email.sent": [
            Delivery.State.DELIVERED,
            Delivery.State.DELAYED,
            Delivery.State.FAILED,
            Delivery.State.BOUNCED,
            Delivery.State.COMPLAINED,
            Delivery.State.SUPPRESSED,
        ],
        "email.delivery_delayed": [
            Delivery.State.DELIVERED,
            Delivery.State.FAILED,
            Delivery.State.BOUNCED,
            Delivery.State.COMPLAINED,
            Delivery.State.SUPPRESSED,
        ],
        "email.failed": [
            Delivery.State.DELIVERED,
            Delivery.State.BOUNCED,
            Delivery.State.COMPLAINED,
            Delivery.State.SUPPRESSED,
        ],
        "email.delivered": [
            Delivery.State.FAILED,
            Delivery.State.BOUNCED,
            Delivery.State.COMPLAINED,
            Delivery.State.SUPPRESSED,
        ],
        "email.bounced": [
            Delivery.State.DELIVERED,
            Delivery.State.COMPLAINED,
            Delivery.State.SUPPRESSED,
        ],
        "email.complained": [
            Delivery.State.BOUNCED,
            Delivery.State.SUPPRESSED,
        ],
        "email.suppressed": [
            Delivery.State.DELIVERED,
            Delivery.State.BOUNCED,
            Delivery.State.COMPLAINED,
        ],
    }
    protected_states = protected_states_by_event.get(event_type, [])
    if protected_states:
        delivery_qs = delivery_qs.exclude(state__in=protected_states)

    updated = delivery_qs.update(state=target_state)
    return JsonResponse({
        "ok": True,
        "updated": updated,
        "ignored": not bool(updated),
    })
