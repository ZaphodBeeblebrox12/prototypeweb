"""Django email backend for Resend's HTTPS API.

Render Free blocks outbound SMTP ports. This backend sends over HTTPS and records
provider acceptance in apps.emailing.Delivery. Resend webhooks later refine the
state to delivered, bounced, complained, or suppressed.
"""

import base64
import hashlib
import logging
import re
import uuid
from email.message import Message
from typing import Any

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend
from django.utils import timezone

logger = logging.getLogger(__name__)


class ResendEmailBackend(BaseEmailBackend):
    """Send Django email messages through the Resend Email API."""

    api_url = "https://api.resend.com/emails"

    def send_messages(self, email_messages: list[Any]) -> int:
        if not email_messages:
            return 0

        sent_count = 0
        for message in email_messages:
            if self._send(message):
                sent_count += 1
        return sent_count

    def _send(self, message: Any) -> bool:
        deliveries = []
        try:
            api_key = getattr(settings, "RESEND_API_KEY", "")
            if not api_key:
                raise ImproperlyConfigured(
                    "RESEND_API_KEY is required when using ResendEmailBackend."
                )

            payload = self._build_payload(message)
            idempotency_key = getattr(message, "_tradethesis_idempotency_key", None)
            if not idempotency_key:
                idempotency_key = uuid.uuid4().hex
                message._tradethesis_idempotency_key = idempotency_key
            if len(idempotency_key) > 256:
                raise ValueError("Email idempotency key must be 256 characters or fewer.")

            # Persist the attempt before calling the provider. If the request
            # times out after Resend accepted it, a retry can reuse the same
            # key on the same EmailMessage instance without sending twice.
            deliveries = self._start_delivery_records(message, idempotency_key)
            if deliveries and all(
                item.state in {"sent", "delivered", "delayed", "bounced", "complained", "suppressed"}
                for item in deliveries
            ):
                return True

            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "Idempotency-Key": idempotency_key,
                },
                json=payload,
                timeout=float(getattr(settings, "RESEND_API_TIMEOUT", 10)),
            )
            response.raise_for_status()
            try:
                response_data = response.json()
            except (ValueError, requests.exceptions.JSONDecodeError) as exc:
                raise RuntimeError("Resend returned a non-JSON success response.") from exc

            provider_message_id = (
                response_data.get("id") if isinstance(response_data, dict) else None
            )
            if not provider_message_id:
                raise RuntimeError("Resend response did not include an email id.")

            if deliveries:
                from apps.emailing.models import Delivery

                delivery_ids = [item.pk for item in deliveries]
                delivery_qs = Delivery.objects.filter(pk__in=delivery_ids)
                accepted_at = timezone.now()
                # The webhook can arrive before this API request returns. Save
                # the provider ID/time for every recipient, but do not downgrade
                # a delivery outcome already written by that webhook.
                delivery_qs.update(
                    provider_message_id=str(provider_message_id),
                    sent_at=accepted_at,
                )
                delivery_qs.exclude(
                    state__in=[
                        Delivery.State.DELIVERED,
                        Delivery.State.DELAYED,
                        Delivery.State.FAILED,
                        Delivery.State.BOUNCED,
                        Delivery.State.COMPLAINED,
                        Delivery.State.SUPPRESSED,
                    ]
                ).update(state=Delivery.State.SENT, error="")
            return True

        except Exception as exc:
            self._mark_failed(deliveries, exc)
            if self.fail_silently:
                logger.warning("Resend email delivery failed (%s).", type(exc).__name__)
                return False
            if isinstance(exc, (ImproperlyConfigured, ValueError)):
                raise
            raise RuntimeError(
                f"Resend email delivery failed ({type(exc).__name__})."
            ) from exc

    @staticmethod
    def _normalise_subject(subject: Any) -> str:
        """Replace Django Sites' default example.com prefix before provider send."""
        value = str(subject or "")
        return re.sub(
            r"^\s*\[example\.com\]\s*",
            "[TradeThesis] ",
            value,
            count=1,
            flags=re.IGNORECASE,
        )

    @staticmethod
    def _start_delivery_records(message: Any, idempotency_key: str) -> list[Any]:
        """Create one audit row per recipient without storing message contents."""
        from apps.emailing.models import Delivery, Template

        user_model = get_user_model()
        deliveries = []
        for recipient in message.to:
            recipient_digest = hashlib.sha256(
                recipient.strip().lower().encode("utf-8")
            ).hexdigest()[:16]
            request_digest = hashlib.sha256(
                idempotency_key.encode("utf-8")
            ).hexdigest()
            delivery_key = f"resend:{request_digest}:{recipient_digest}"
            user_id = getattr(message, "_tradethesis_user_id", None)
            if user_id is None:
                user_id = (
                    user_model.objects.filter(email__iexact=recipient)
                    .values_list("pk", flat=True)
                    .first()
                )

            delivery, created = Delivery.objects.get_or_create(
                idempotency_key=delivery_key,
                defaults={
                    "user_id": user_id,
                    "to_email": recipient,
                    "kind": getattr(message, "_tradethesis_kind", Template.Kind.TRANSACTIONAL),
                    "subject": ResendEmailBackend._normalise_subject(message.subject),
                    "state": Delivery.State.SENDING,
                    "provider": "resend",
                },
            )
            if not created and delivery.state in {
                Delivery.State.QUEUED,
                Delivery.State.FAILED,
            }:
                Delivery.objects.filter(
                    pk=delivery.pk,
                    state__in=[Delivery.State.QUEUED, Delivery.State.FAILED],
                ).update(state=Delivery.State.SENDING, error="")
                delivery.refresh_from_db(fields=["state", "error"])
            deliveries.append(delivery)
        return deliveries

    @staticmethod
    def _mark_failed(deliveries: list[Any], exc: Exception) -> None:
        """Store a safe error code; never persist message bodies or API credentials."""
        if not deliveries:
            return
        from apps.emailing.models import Delivery

        status_code = getattr(getattr(exc, "response", None), "status_code", None)
        error_code = (
            f"resend_http_{status_code}"
            if status_code
            else f"resend_{type(exc).__name__.lower()}"
        )
        Delivery.objects.filter(pk__in=[item.pk for item in deliveries]).exclude(
            state__in=[
                Delivery.State.DELIVERED,
                Delivery.State.DELAYED,
                Delivery.State.BOUNCED,
                Delivery.State.COMPLAINED,
                Delivery.State.SUPPRESSED,
            ]
        ).update(state=Delivery.State.FAILED, error=error_code)

    @staticmethod
    def _build_payload(message: Any) -> dict[str, Any]:
        """Translate Django's EmailMessage fields to the Resend API payload."""
        if not message.to:
            raise ValueError("Resend requires at least one To recipient.")

        payload: dict[str, Any] = {
            "from": message.from_email or settings.DEFAULT_FROM_EMAIL,
            "to": list(message.to),
            "subject": ResendEmailBackend._normalise_subject(message.subject),
        }

        if message.cc:
            payload["cc"] = list(message.cc)
        if message.bcc:
            payload["bcc"] = list(message.bcc)
        if getattr(message, "reply_to", None):
            payload["reply_to"] = list(message.reply_to)
        if getattr(message, "extra_headers", None):
            payload["headers"] = {
                str(name): str(value) for name, value in message.extra_headers.items()
            }

        if getattr(message, "content_subtype", "plain") == "html":
            payload["html"] = message.body
        else:
            payload["text"] = message.body

        for alternative in getattr(message, "alternatives", []):
            content, mimetype = alternative
            if mimetype == "text/html":
                payload["html"] = content
            elif mimetype == "text/plain":
                payload["text"] = content

        attachments = getattr(message, "attachments", [])
        if attachments:
            payload["attachments"] = [
                ResendEmailBackend._build_attachment(attachment) for attachment in attachments
            ]

        return payload

    @staticmethod
    def _build_attachment(attachment: Any) -> dict[str, str]:
        """Encode common Django attachment formats for the Resend API."""
        content_id = None
        content_disposition = None

        if isinstance(attachment, Message):
            filename = attachment.get_filename() or "attachment"
            content = attachment.get_payload(decode=True) or b""
            content_type = attachment.get_content_type()
            content_id = attachment.get("Content-ID")
            content_disposition = attachment.get_content_disposition()
        elif isinstance(attachment, (tuple, list)) and len(attachment) == 3:
            filename, content, content_type = attachment
        else:
            raise ValueError("Unsupported Django email attachment format.")

        if isinstance(content, str):
            content = content.encode("utf-8")
        if not isinstance(content, bytes):
            raise ValueError("Email attachment content must be text or bytes.")

        result = {
            "filename": str(filename),
            "content": base64.b64encode(content).decode("ascii"),
        }
        if content_type:
            result["content_type"] = str(content_type)
        if content_id:
            result["content_id"] = str(content_id).strip("<>")
        if content_disposition in {"attachment", "inline"}:
            result["content_disposition"] = content_disposition
        return result
