"""Support tickets: member access, billing, and technical support."""
import os
import uuid
from datetime import timedelta

from PIL import Image, UnidentifiedImageError
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from apps.subscriptions.models import Plan

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
MAX_ATTACHMENTS_PER_TICKET = 5
MAX_ATTACHMENT_BYTES = 5 * 1024 * 1024  # 5 MB
IMAGE_FORMATS_BY_EXTENSION = {
    ".png": {"PNG"},
    ".jpg": {"JPEG"},
    ".jpeg": {"JPEG"},
    ".gif": {"GIF"},
    ".webp": {"WEBP"},
}


def ticket_attachment_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f"support/tickets/{instance.ticket_id}/{uuid.uuid4()}{ext}"


class AffiliateLink(models.Model):
    """One of the owner's referral/affiliate links."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text=_('Label shown to users, e.g. "Exness" or "IC Markets VIP"'))
    url = models.URLField(help_text=_("Your referral link for this broker/code"))
    referral_code = models.CharField(
        max_length=100,
        help_text=_("The code the broker gave you - used to verify screenshots"))
    plan = models.ForeignKey(
        Plan, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={"is_hidden": True},
        related_name="affiliate_links",
        help_text=_("Optional hidden plan assigned by default to access requests "
                    "using this link; an authorized reviewer can override it"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def clean(self):
        super().clean()
        if self.plan_id and not self.plan.is_hidden:
            raise ValidationError({"plan": _("Referral links can map only to hidden plans.")})

    def __str__(self):
        return self.name


class SupportTicket(models.Model):
    """A user-raised access request, billing issue, or technical issue."""

    class Category(models.TextChoices):
        ACCESS = "access_request", _("Access request (referral verification)")
        BILLING = "billing", _("Billing / payment issue")
        TECHNICAL = "technical", _("Technical issue (Telegram access, etc.)")

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        IN_PROGRESS = "in_progress", _("In progress")
        AWAITING_MEMBER = "awaiting_member", _("Awaiting member")
        APPROVED = "approved", _("Approved / Resolved")
        REJECTED = "rejected", _("Rejected / Closed")
        WITHDRAWN = "withdrawn", _("Withdrawn by user")

    class Priority(models.TextChoices):
        LOW = "low", _("Low")
        NORMAL = "normal", _("Normal")
        HIGH = "high", _("High")
        URGENT = "urgent", _("Urgent")

    SLA_TARGET_HOURS = {
        Priority.URGENT: 2,
        Priority.HIGH: 8,
        Priority.NORMAL: 24,
        Priority.LOW: 72,
    }

    ACTIVE_STATUSES = (
        Status.PENDING,
        Status.IN_PROGRESS,
        Status.AWAITING_MEMBER,
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="support_tickets",
        help_text=_("User who raised the ticket"))
    category = models.CharField(max_length=20, choices=Category.choices,
                                default=Category.ACCESS)
    affiliate_link = models.ForeignKey(
        AffiliateLink, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="tickets",
        help_text=_("Referral link used (access requests only)"))
    plan = models.ForeignKey(
        Plan, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="support_tickets",
        help_text=_("Default plan from the referral link, or plan selected by reviewer"))
    message = models.TextField(help_text=_("Describe the request or issue"))
    status = models.CharField(max_length=20, choices=Status.choices,
                              default=Status.PENDING)
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.NORMAL,
        help_text=_("Target first-response time: urgent 2h, high 8h, normal 24h, low 72h."),
    )
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_support_tickets",
        limit_choices_to={"is_staff": True},
        help_text=_("Staff member responsible for the next action."),
    )
    first_response_due_at = models.DateTimeField(
        null=True, blank=True, db_index=True,
        help_text=_("First-response SLA deadline; recalculated when priority changes before a reply."),
    )
    first_response_at = models.DateTimeField(
        null=True, blank=True,
        help_text=_("Timestamp of the first public support response or review."),
    )
    admin_notes = models.TextField(
        blank=True, default="",
        help_text=_("Reviewer summary shown to the member"))
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="reviewed_support_tickets")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("support ticket")
        verbose_name_plural = _("support tickets")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "category"],
                condition=models.Q(status__in=["pending", "in_progress", "awaiting_member"]),
                name="uniq_one_open_ticket_per_user_category",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "first_response_due_at"],
                         name="support_status_sla_due_idx"),
            models.Index(fields=["assigned_to", "status"],
                         name="support_assignee_status_idx"),
        ]

    def __str__(self):
        return f"Ticket {self.short_id} ({self.user}) - {self.get_category_display()} [{self.status}]"

    @property
    def short_id(self):
        return str(self.id)[:8]

    @property
    def is_access_request(self):
        return self.category == self.Category.ACCESS

    @property
    def review_plan(self):
        """Resolve the plan whose reviewer list governs this ticket."""
        if self.plan_id:
            return self.plan
        if self.affiliate_link_id and self.affiliate_link.plan_id:
            return self.affiliate_link.plan
        return None

    def clean(self):
        super().clean()
        if self.category == self.Category.ACCESS and self.affiliate_link_id is None:
            raise ValidationError({
                "affiliate_link": _("Select the referral link you used.")
            })
        if self.is_access_request and self.plan_id and not self.plan.is_hidden:
            raise ValidationError({"plan": _("Access requests may use only hidden plans.")})
        if self.assigned_to_id and not self.assigned_to.is_staff:
            raise ValidationError({"assigned_to": _("Tickets can only be assigned to staff members.")})

    def save(self, *args, **kwargs):
        priority_hours = self.SLA_TARGET_HOURS.get(self.priority, self.SLA_TARGET_HOURS[self.Priority.NORMAL])
        if self._state.adding:
            if self.first_response_due_at is None:
                self.first_response_due_at = timezone.now() + timedelta(hours=priority_hours)
        else:
            previous = type(self).objects.filter(pk=self.pk).values(
                "priority", "first_response_at"
            ).first()
            if (previous and previous["priority"] != self.priority
                    and previous["first_response_at"] is None):
                self.first_response_due_at = timezone.now() + timedelta(hours=priority_hours)
                update_fields = kwargs.get("update_fields")
                if update_fields is not None:
                    kwargs["update_fields"] = set(update_fields) | {"first_response_due_at"}
        super().save(*args, **kwargs)

    @property
    def is_open(self):
        return self.status in self.ACTIVE_STATUSES

    @property
    def is_sla_overdue(self):
        return (
            self.first_response_at is None
            and self.first_response_due_at is not None
            and self.first_response_due_at < timezone.now()
            and self.is_open
        )

    def can_be_reviewed_by(self, user, plan=None):
        """Superusers always may review; mapped-plan approvers govern access tickets."""
        if not getattr(user, "is_authenticated", False) or not getattr(user, "is_staff", False):
            return False
        if user.is_superuser:
            return True

        effective_plan = plan or self.review_plan
        if effective_plan and effective_plan.ticket_approvers.exists():
            return effective_plan.ticket_approvers.filter(pk=user.pk).exists()
        # An empty approver list keeps the existing "any staff" behavior.
        return True


class TicketAttachment(models.Model):
    """A private screenshot attached to a SupportTicket."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        SupportTicket, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to=ticket_attachment_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        verbose_name = _("ticket attachment")
        verbose_name_plural = _("ticket attachments")

    def __str__(self):
        return f"Attachment for ticket {self.ticket_id}"

    def clean(self):
        super().clean()
        if not self.file:
            return

        name = getattr(self.file, "name", "") or ""
        ext = os.path.splitext(name)[1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise ValidationError({
                "file": _("Only image files are allowed (PNG, JPG, JPEG, GIF, WEBP).")
            })

        size = getattr(self.file, "size", 0) or 0
        if size > MAX_ATTACHMENT_BYTES:
            raise ValidationError({"file": _("File is too large (max 5 MB).")})

        if self.ticket_id and self._state.adding:
            count = TicketAttachment.objects.filter(ticket_id=self.ticket_id).count()
            if count >= MAX_ATTACHMENTS_PER_TICKET:
                raise ValidationError({
                    "ticket": _(f"A ticket can have at most {MAX_ATTACHMENTS_PER_TICKET} screenshots.")
                })

        stream = self.file.file
        try:
            original_position = stream.tell()
        except (AttributeError, OSError):
            original_position = 0
        try:
            image = Image.open(stream)
            image_format = image.format
            image.verify()
            if image_format not in IMAGE_FORMATS_BY_EXTENSION[ext]:
                raise ValidationError({
                    "file": _("The file contents do not match its image extension.")
                })
        except ValidationError:
            raise
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
            raise ValidationError({"file": _("This file is not a valid supported image.")})
        finally:
            try:
                stream.seek(original_position)
            except (AttributeError, OSError):
                pass

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class TicketMessage(models.Model):
    """Append-only public reply or staff-only internal note."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        SupportTicket, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        help_text=_("Null = deleted account; body retained, author shown as former user."))
    body = models.TextField()
    is_internal = models.BooleanField(
        default=False, help_text=_("Staff-only note; never shown to the member."))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        verbose_name = _("ticket message")
        verbose_name_plural = _("ticket messages")
        indexes = [models.Index(fields=["ticket", "created_at"])]

    def save(self, *args, **kwargs):
        # UUID defaults assign the primary key before first save. _state.adding
        # is the correct discriminator; checking pk made every new message fail.
        if not self._state.adding:
            raise RuntimeError("TicketMessage is append-only.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message on ticket {self.ticket_id} by {self.author}"
