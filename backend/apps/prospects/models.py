import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class ProspectEnquiry(models.Model):
    class Programme(models.TextChoices):
        CONSTRUCT = "construct", "CONSTRUCT"
        LIVE_CLASSROOM = "live_classroom", "Trade Construction & Management — Live Classroom"

    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        QUALIFIED = "qualified", "Qualified"
        ENROLLED = "enrolled", "Enrolled"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    programme = models.CharField(max_length=24, choices=Programme.choices)
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    starting_point = models.CharField(max_length=80, blank=True)
    question = models.TextField(blank=True)
    contact_consent = models.BooleanField(default=False)
    marketing_opt_in = models.BooleanField(default=False)
    source_path = models.CharField(max_length=255, blank=True)
    # HMAC fingerprint only: never persist a raw visitor IP address.
    ip_fingerprint = models.CharField(max_length=64, blank=True, db_index=True)

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.NEW)
    staff_notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_prospect_enquiries",
    )
    last_contacted_at = models.DateTimeField(null=True, blank=True)
    staff_notification_sent_at = models.DateTimeField(null=True, blank=True)
    customer_confirmation_sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"], name="pros_status_created_idx"),
            models.Index(fields=["programme", "-created_at"], name="pros_prog_created_idx"),
        ]
        permissions = [
            ("export_prospectenquiry", "Can export prospect enquiries"),
        ]

    def __str__(self):
        return f"{self.get_programme_display()} enquiry · {self.name}"

    @property
    def short_reference(self):
        return str(self.pk).split("-")[0].upper()
