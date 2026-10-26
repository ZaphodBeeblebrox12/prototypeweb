"""Transactional support-ticket workflow and durable notification records."""
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from apps.bot_integration.transactional import TransactionalTelegramService
from apps.jobs.enqueue import enqueue_reconcile
from apps.notifications.models import EmailLog, Notification
from apps.subscriptions.services import grant_subscription_by_admin

logger = logging.getLogger(__name__)


def _ticket_url(ticket, staff=False):
    if staff:
        path = f"/admin/support/supportticket/{ticket.pk}/change/"
    else:
        path = reverse("support:ticket_detail", kwargs={"pk": ticket.pk})
    # SITE_BASE_URL is the authenticated Academy origin. Its development
    # default must not leak into production notifications, and the public
    # marketing origin may not host the private ticket routes.
    base = (getattr(settings, "SITE_BASE_URL", "") or "").rstrip("/")
    if base.startswith(("http://127.0.0.1", "http://localhost")):
        base = ""
    return f"{base}{path}" if base else path


def _record_notification(user, subject, text, link):
    try:
        return Notification.objects.create(
            user=user,
            notification_type=Notification.NotificationType.SYSTEM,
            title=subject[:255],
            message=text,
            link=link,
            metadata={"source": "support_ticket"},
        )
    except Exception:
        # Notifications must not roll back a ticket decision. The error remains
        # visible in application logs and email/Telegram delivery is independent.
        logger.exception("could not persist support notification user=%s", user.pk)
        return None


def _send_email(user, email, subject, text, template):
    """Send one transactional email and record its outcome in EmailLog."""
    if not email:
        return False
    log = None
    try:
        log = EmailLog.objects.create(
            user=user,
            email=email,
            template=template[:100],
            subject=subject[:255],
            status="queued",
            metadata={"source": "support_ticket"},
        )
    except Exception:
        # A tracking-table problem must not prevent the actual user/staff alert.
        logger.exception("could not create support email log recipient=%s", email)

    try:
        sent_count = send_mail(subject, text, None, [email], fail_silently=False)
    except Exception as exc:
        if log is not None:
            log.status = "failed"
            log.error_message = str(exc)[:4000]
            log.save(update_fields=["status", "error_message"])
        logger.exception("support email failed recipient=%s template=%s", email, template)
        return False

    if sent_count:
        if log is not None:
            log.status = "sent"
            log.sent_at = timezone.now()
            log.save(update_fields=["status", "sent_at"])
        return True

    if log is not None:
        log.status = "failed"
        log.error_message = "Email backend reported that no message was sent."
        log.save(update_fields=["status", "error_message"])
    logger.error("support email was not sent recipient=%s template=%s", email, template)
    return False


def _send_telegram(user, text, ticket_id, kind):
    try:
        TransactionalTelegramService.send_text(user, text)
        return True
    except Exception:
        logger.exception("support Telegram delivery failed ticket=%s kind=%s", ticket_id, kind)
        return False


def notify_user(ticket, subject, text):
    """Record an in-app notice and attempt the plan's configured channels.

    Failed email deliveries are persisted in EmailLog. Telegram exceptions are
    logged; the ticket decision is not rolled back because a channel is down.
    """
    channel = "both"
    if ticket.plan_id:
        channel = ticket.plan.notice_channel

    _record_notification(ticket.user, subject, text, _ticket_url(ticket))
    if channel in ("telegram", "both"):
        _send_telegram(ticket.user, text, ticket.pk, "notice")
    if channel in ("email", "both"):
        _send_email(ticket.user, ticket.user.email, subject, text, "support_ticket_notice")


def send_ticket_confirmation(ticket):
    """Confirm ticket creation to the member in-app, via Telegram and email."""
    text = (f"We received your ticket ({ticket.get_category_display()}). "
            "We'll review it and get back to you shortly.")
    _record_notification(
        ticket.user, f"Ticket received - {ticket.short_id}", text, _ticket_url(ticket)
    )
    _send_telegram(ticket.user, text, ticket.pk, "confirmation")
    _send_email(ticket.user, ticket.user.email,
                f"Ticket received - {ticket.short_id}", text,
                "support_ticket_confirmation")


def notify_staff_about_ticket(ticket, subject=None, body=None, message_id=None):
    """Create an in-app staff alert and email active staff members.

    There is no mandatory hard-coded inbox address: staff alerts are visible in
    each staff member's existing notification feed, and individual email
    delivery is tracked in EmailLog.
    """
    User = get_user_model()
    staff_queryset = User.objects.filter(is_staff=True, is_active=True).exclude(
        pk=ticket.user_id
    )
    review_plan = ticket.review_plan
    if review_plan and review_plan.ticket_approvers.exists():
        # Do not leak ticket contents to staff who cannot open this ticket.
        staff_queryset = staff_queryset.filter(
            Q(is_superuser=True) | Q(pk__in=review_plan.ticket_approvers.values_list("pk", flat=True))
        )
    staff = list(staff_queryset)
    event_subject = subject or f"New support ticket {ticket.short_id}"
    event_body = body or (
        f"{ticket.user} submitted {ticket.get_category_display()}: "
        f"{ticket.message[:500]}"
    )
    link = _ticket_url(ticket, staff=True)
    for member in staff:
        _record_notification(member, event_subject, event_body, link)
        if member.email:
            _send_email(member, member.email, event_subject, event_body,
                        "support_ticket_staff_alert")


@transaction.atomic
def approve_ticket(ticket, plan, admin, notes=None):
    """Approve an access request or resolve a billing/technical ticket.

    Access approvals grant the hidden plan and enqueue reconciliation in the
    same database transaction. If enqueue fails, the grant and ticket update
    both roll back so the queue cannot falsely claim that access was granted.
    """
    from .models import SupportTicket

    if not ticket.is_open:
        raise ValueError("Only open tickets can be approved.")
    if ticket.is_access_request:
        if plan is None:
            raise ValueError("Assign a plan before approving an access request.")
        if not plan.is_hidden:
            raise ValueError("Access requests can only grant a hidden plan.")
    if not ticket.can_be_reviewed_by(admin, plan=plan if ticket.is_access_request else None):
        raise PermissionError("You are not allowed to review this ticket.")

    grant = None
    if ticket.is_access_request:
        grant = grant_subscription_by_admin(
            ticket.user, plan, granted_by=admin,
            duration_days=plan.grant_duration_days,
            reason=f"Access request {ticket.short_id} approved",
        )
        # Do not swallow this error: it must roll back the subscription grant
        # and leave the ticket pending for a safe retry.
        enqueue_reconcile(ticket.user_id, reason="support_ticket_approved")
        ticket.plan = plan

    if notes is not None:
        ticket.admin_notes = notes.strip()
    ticket.status = SupportTicket.Status.APPROVED
    ticket.reviewed_by = admin
    ticket.reviewed_at = timezone.now()
    if ticket.first_response_at is None:
        ticket.first_response_at = ticket.reviewed_at
    update_fields = [
        "status", "reviewed_by", "reviewed_at", "updated_at", "admin_notes",
        "first_response_at",
    ]
    if ticket.is_access_request:
        update_fields.append("plan")
    ticket.save(update_fields=update_fields)

    if ticket.is_access_request:
        duration = (f"{plan.grant_duration_days} day(s)" if plan.grant_duration_days
                    else "no expiry")
        subject = f"Your access request was approved - {plan.name}"
        text = (f"Your request was approved. You now have access to {plan.name} "
                f"({duration}). If a Telegram group is linked to this plan you will "
                f"be added shortly.")
    else:
        subject = "Your ticket has been resolved"
        text = (f"Your ticket ({ticket.get_category_display()}) has been resolved. "
                f"{ticket.admin_notes}".strip())
    transaction.on_commit(lambda: notify_user(ticket, subject, text))
    return grant


@transaction.atomic
def reject_ticket(ticket, admin, notes):
    """Reject/close a pending ticket and notify the member with the reason."""
    from .models import SupportTicket

    notes = (notes or "").strip()
    if not ticket.is_open:
        raise ValueError("Only open tickets can be rejected.")
    if not notes:
        raise ValueError("A reason (admin notes) is required.")
    if not ticket.can_be_reviewed_by(admin):
        raise PermissionError("You are not allowed to review this ticket.")

    ticket.status = SupportTicket.Status.REJECTED
    ticket.admin_notes = notes
    ticket.reviewed_by = admin
    ticket.reviewed_at = timezone.now()
    if ticket.first_response_at is None:
        ticket.first_response_at = ticket.reviewed_at
    ticket.save(update_fields=["status", "admin_notes", "reviewed_by",
                               "reviewed_at", "first_response_at", "updated_at"])
    subject = "Your ticket was not approved"
    text = (f"Your ticket ({ticket.get_category_display()}) was reviewed and not "
            f"approved. Reason: {notes}")
    transaction.on_commit(lambda: notify_user(ticket, subject, text))
    return ticket


@transaction.atomic
def set_ticket_status(ticket, admin, status):
    """Move a ticket between active work states or reopen a closed ticket."""
    from .models import SupportTicket, TicketMessage

    if not ticket.can_be_reviewed_by(admin):
        raise PermissionError("You are not allowed to review this ticket.")
    if status not in {
        SupportTicket.Status.IN_PROGRESS,
        SupportTicket.Status.AWAITING_MEMBER,
    }:
        raise ValueError("Unsupported ticket status transition.")
    if not ticket.is_open:
        raise ValueError("Reopen a closed ticket before changing its work status.")

    ticket.status = status
    ticket.assigned_to = ticket.assigned_to or admin
    ticket.save(update_fields=["status", "assigned_to", "updated_at"])
    TicketMessage.objects.create(
        ticket=ticket, author=admin,
        body=f"Ticket status changed to: {ticket.get_status_display()}.",
        is_internal=True,
    )
    return ticket


@transaction.atomic
def reopen_ticket(ticket, admin):
    """Reopen a resolved/closed ticket while preserving its previous review note."""
    from .models import SupportTicket, TicketMessage

    if not ticket.can_be_reviewed_by(admin):
        raise PermissionError("You are not allowed to review this ticket.")
    if ticket.status not in {SupportTicket.Status.APPROVED, SupportTicket.Status.REJECTED}:
        raise ValueError("Only resolved or closed tickets can be reopened.")
    another_open = SupportTicket.objects.filter(
        user_id=ticket.user_id,
        category=ticket.category,
        status__in=SupportTicket.ACTIVE_STATUSES,
    ).exclude(pk=ticket.pk).exists()
    if another_open:
        raise ValueError(
            "This member already has an open ticket in this category. Resolve it before reopening this one."
        )

    if ticket.admin_notes:
        TicketMessage.objects.create(
            ticket=ticket, author=admin, body=f"Previous review note: {ticket.admin_notes}",
            is_internal=True,
        )
    ticket.admin_notes = ""
    ticket.status = SupportTicket.Status.IN_PROGRESS
    ticket.reviewed_by = None
    ticket.reviewed_at = None
    ticket.save(update_fields=[
        "admin_notes", "status", "reviewed_by", "reviewed_at", "updated_at",
    ])
    subject = f"Your support ticket {ticket.short_id} has been reopened"
    text = "Support has reopened your ticket and will continue working on it."
    transaction.on_commit(lambda: notify_user(ticket, subject, text))
    return ticket


@transaction.atomic
def add_ticket_message(ticket, author, body, is_internal=False):
    """Append a public reply or staff-only note without allowing edits in place."""
    from .models import SupportTicket, TicketMessage

    body = (body or "").strip()
    if not body:
        raise ValueError("Enter a message before sending.")
    if len(body) > 10000:
        raise ValueError("Messages must be 10,000 characters or fewer.")
    is_staff_author = bool(getattr(author, "is_staff", False))
    if is_staff_author:
        if not ticket.can_be_reviewed_by(author):
            raise PermissionError("You are not allowed to reply to this ticket.")
        if ticket.status == SupportTicket.Status.WITHDRAWN:
            raise ValueError("A withdrawn ticket cannot receive replies.")
        if not is_internal and not ticket.is_open:
            raise ValueError("Reopen the ticket before sending a public reply.")
    else:
        if ticket.user_id != author.pk:
            raise PermissionError("You can reply only to your own ticket.")
        if is_internal:
            raise PermissionError("Members cannot create internal notes.")
        if not ticket.is_open:
            raise ValueError("Replies are available only while a ticket is open.")

    message = TicketMessage.objects.create(
        ticket=ticket, author=author, body=body, is_internal=is_internal
    )
    if is_internal:
        return message

    if is_staff_author:
        ticket.status = SupportTicket.Status.AWAITING_MEMBER
        if ticket.first_response_at is None:
            ticket.first_response_at = timezone.now()
        ticket.save(update_fields=["status", "first_response_at", "updated_at"])
        subject = f"New reply on support ticket {ticket.short_id}"
        text = f"Support replied to your ticket:\n\n{body}"
        transaction.on_commit(lambda: notify_user(ticket, subject, text))
    else:
        # A member reply answers a staff question and returns the ticket to
        # active work. Pending tickets are also promoted to in-progress.
        ticket.status = SupportTicket.Status.IN_PROGRESS
        ticket.save(update_fields=["status", "updated_at"])
        subject = f"Member reply on support ticket {ticket.short_id}"
        text = f"{ticket.user} replied to ticket {ticket.short_id}:\n\n{body[:1500]}"
        transaction.on_commit(
            lambda: notify_staff_about_ticket(ticket, subject=subject, body=text,
                                               message_id=message.pk)
        )
    return message
