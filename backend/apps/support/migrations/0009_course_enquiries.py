import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("support", "0008_ticketattachment_private_drive_storage"),
    ]

    operations = [
        migrations.CreateModel(
            name="CourseEnquiry",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("programme", models.CharField(choices=[("construct", "CONSTRUCT"), ("live_classroom", "Trade Construction & Management — Live Classroom")], max_length=24)),
                ("name", models.CharField(max_length=120)),
                ("email", models.EmailField(db_index=True, max_length=254)),
                ("starting_point", models.CharField(blank=True, choices=[("learning_charts", "Learning to read charts"), ("connected_plan", "Know some patterns, need a connected plan"), ("risk_management", "Working on risk and trade management"), ("review_process", "Want a more consistent review process"), ("other", "Something else")], default="", max_length=32)),
                ("message", models.TextField(blank=True, default="", max_length=2000)),
                ("consent_at", models.DateTimeField(help_text="Explicit consent to use these details to respond to this enquiry.")),
                ("status", models.CharField(choices=[("new", "New"), ("in_progress", "In progress"), ("replied", "Replied"), ("closed", "Closed")], db_index=True, default="new", max_length=16)),
                ("internal_notes", models.TextField(blank=True, default="")),
                ("responded_at", models.DateTimeField(blank=True, null=True)),
                ("confirmation_email_status", models.CharField(choices=[("pending", "Pending"), ("accepted", "Accepted by email backend"), ("failed", "Failed")], default="pending", max_length=12)),
                ("confirmation_email_sent_at", models.DateTimeField(blank=True, null=True)),
                ("confirmation_email_error", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("assigned_to", models.ForeignKey(blank=True, limit_choices_to={"is_staff": True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assigned_course_enquiries", to=settings.AUTH_USER_MODEL)),
                ("responded_by", models.ForeignKey(blank=True, limit_choices_to={"is_staff": True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="responded_course_enquiries", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "course enquiry",
                "verbose_name_plural": "course enquiries",
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["programme", "status", "created_at"], name="support_enq_program_status_idx"),
                    models.Index(fields=["email", "created_at"], name="support_enq_email_created_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="CourseEnquiryReply",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("subject", models.CharField(max_length=255)),
                ("body", models.TextField(max_length=10000)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("accepted", "Accepted by email backend"), ("failed", "Failed")], default="pending", max_length=12)),
                ("error_message", models.TextField(blank=True, default="")),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("author", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="course_enquiry_replies", to=settings.AUTH_USER_MODEL)),
                ("enquiry", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="replies", to="support.courseenquiry")),
            ],
            options={
                "verbose_name": "course enquiry reply",
                "verbose_name_plural": "course enquiry replies",
                "ordering": ["created_at", "id"],
            },
        ),
    ]
