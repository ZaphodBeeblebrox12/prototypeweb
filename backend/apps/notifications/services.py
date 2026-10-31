"""
Notifications service for email delivery.

This module provides the interface for sending emails and tracking delivery.
Other apps (like growth) should use this instead of sending email directly.
"""
import logging
from typing import Dict, Any, Optional

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.utils import timezone

from apps.core.email_branding import (
    ensure_branded_plain_text,
    normalise_email_subject,
    normalise_from_email,
)

from .models import EmailLog

logger = logging.getLogger(__name__)


class NotificationServiceError(Exception):
    """Base exception for notification errors."""
    pass


class NotificationService:
    """
    Service for sending notifications and emails.

    This is the central point for all email delivery in the application.
    Apps should never send email directly using django.core.mail.
    """

    @classmethod
    def send_email(
        cls,
        to_email: str,
        template: str,
        subject: str,
        context: Dict[str, Any],
        from_email: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user=None,
        log_template: Optional[str] = None,
    ) -> bool:
        """
        Send an email using a template.

        Args:
            to_email: Recipient email address
            template: Template path (e.g., 'growth/gift_invite')
            subject: Email subject
            context: Template context dictionary
            from_email: Sender email (defaults to DEFAULT_FROM_EMAIL)
            metadata: Additional metadata for tracking

        Returns:
            True if email was sent successfully

        Raises:
            NotificationServiceError: If email fails to send
        """
        from_email = normalise_from_email(from_email, settings.DEFAULT_FROM_EMAIL)
        context = dict(context or {})

        # Add site to context
        try:
            site = Site.objects.get_current()
            context['site'] = site
        except Site.DoesNotExist:
            pass

        # Keep customer-facing branding stable even if the Django Site row is legacy.
        context["site_name"] = "TradeThesis"
        context.setdefault("logo_url", getattr(settings, "EMAIL_LOGO_URL", ""))

        # Several transactional templates share these links. Explicit caller values win.
        site_base_url = str(getattr(settings, "SITE_BASE_URL", "") or "").rstrip("/")
        if site_base_url:
            context.setdefault("dashboard_url", f"{site_base_url}/dashboard/")
            context.setdefault("support_url", f"{site_base_url}/support/")

        # Render templates
        try:
            # Subject template (optional override)
            subject_template = f"{template}_subject.txt"
            try:
                subject = render_to_string(subject_template, context).strip()
            except Exception:
                # Use provided subject if template doesn't exist
                pass

            # Body templates
            text_body = render_to_string(f"{template}_body.txt", context)

            # Try HTML version
            html_body = None
            try:
                html_body = render_to_string(f"{template}_body.html", context)
            except Exception:
                pass  # HTML is optional

        except Exception as e:
            logger.error(f"Failed to render email templates for {template}: {e}")
            raise NotificationServiceError(f"Template rendering failed: {e}")

        # A consistent subject brand is visible even when a mail client hides
        # the sender name or strips HTML. Keep support's event-specific log tags.
        subject = normalise_email_subject(subject)
        text_body = ensure_branded_plain_text(text_body)
        if not html_body or "tradethesis-email-shell-v1" not in html_body.lower():
            html_body = render_to_string(
                "emails/provider_fallback.html",
                {
                    "subject": subject,
                    "body_html": html_body or "",
                    "body_text": text_body,
                    "logo_url": context.get("logo_url", ""),
                    "dashboard_url": context.get("dashboard_url", ""),
                    "support_url": context.get("support_url", ""),
                },
            )

        # Logging is best-effort: a temporary audit-table issue must not block
        # a transactional message from reaching its recipient.
        email_log = None
        try:
            email_log = EmailLog.objects.create(
                user=user,
                email=to_email,
                template=(log_template or template)[:100],
                subject=subject,
                status="queued",
                metadata=metadata or {},
            )
        except Exception:
            logger.exception("could not create EmailLog for recipient=%s", to_email)

        try:
            # Send the email
            sent_count = send_mail(
                subject=subject,
                message=text_body,
                from_email=from_email,
                recipient_list=[to_email],
                html_message=html_body,
                fail_silently=False,
            )
            if not sent_count:
                raise NotificationServiceError("Email backend reported that no message was sent.")

            # Update the audit row when available; provider acceptance is the
            # delivery result and must not be turned into a retry by log failure.
            if email_log is not None:
                try:
                    email_log.status = "sent"
                    email_log.sent_at = timezone.now()
                    email_log.save(update_fields=['status', 'sent_at'])
                except Exception:
                    logger.exception("could not mark EmailLog sent id=%s", email_log.pk)

            logger.info(f"Email sent to {to_email} using template {template}")
            return True

        except Exception as e:
            # Update the audit row when available; preserve the original send error.
            if email_log is not None:
                try:
                    email_log.status = "failed"
                    email_log.error_message = str(e)
                    email_log.save(update_fields=['status', 'error_message'])
                except Exception:
                    logger.exception("could not mark EmailLog failed id=%s", email_log.pk)

            logger.error(f"Failed to send email to {to_email}: {e}")
            raise NotificationServiceError(f"Email sending failed: {e}")

    @classmethod
    def send_simple_email(
        cls,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        html_body: Optional[str] = None,
    ) -> bool:
        """
        Send a simple email without templates.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            from_email: Sender email
            html_body: Optional HTML body

        Returns:
            True if sent successfully
        """
        from_email = normalise_from_email(from_email, settings.DEFAULT_FROM_EMAIL)
        subject = normalise_email_subject(subject)
        body = ensure_branded_plain_text(body)
        if not html_body or "tradethesis-email-shell-v1" not in html_body.lower():
            base_url = str(getattr(settings, "SITE_BASE_URL", "") or "").rstrip("/")
            html_body = render_to_string(
                "emails/provider_fallback.html",
                {
                    "subject": subject,
                    "body_html": html_body or "",
                    "body_text": body,
                    "logo_url": getattr(settings, "EMAIL_LOGO_URL", ""),
                    "dashboard_url": f"{base_url}/dashboard/" if base_url else "",
                    "support_url": f"{base_url}/support/" if base_url else "",
                },
            )

        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=from_email,
                recipient_list=[to_email],
                html_message=html_body,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send simple email to {to_email}: {e}")
            return False
