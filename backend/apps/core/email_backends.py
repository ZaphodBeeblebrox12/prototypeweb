"""Django email backend that sends through Resend's HTTPS API.

Render Free blocks outbound SMTP ports, but permits HTTPS requests. Keeping this
as a normal Django backend lets django-allauth verification and password-reset
emails use the existing templates and delivery calls without auth-flow changes.
"""

import base64
import logging
from email.message import Message
from typing import Any

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend

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
        try:
            api_key = getattr(settings, "RESEND_API_KEY", "")
            if not api_key:
                raise ImproperlyConfigured(
                    "RESEND_API_KEY is required when using ResendEmailBackend."
                )

            payload = self._build_payload(message)
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=float(getattr(settings, "RESEND_API_TIMEOUT", 10)),
            )
            response.raise_for_status()
            return True
        except Exception as exc:
            if self.fail_silently:
                logger.warning("Resend email delivery failed (%s).", type(exc).__name__)
                return False
            if isinstance(exc, (ImproperlyConfigured, ValueError)):
                raise
            raise RuntimeError(f"Resend email delivery failed ({type(exc).__name__}).") from exc

    @staticmethod
    def _build_payload(message: Any) -> dict[str, Any]:
        """Translate Django's EmailMessage fields to the Resend API payload."""
        if not message.to:
            raise ValueError("Resend requires at least one To recipient.")

        payload: dict[str, Any] = {
            "from": message.from_email or settings.DEFAULT_FROM_EMAIL,
            "to": list(message.to),
            "subject": message.subject or "",
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
