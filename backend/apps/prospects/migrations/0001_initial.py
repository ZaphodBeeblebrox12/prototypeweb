import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ProspectEnquiry",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("programme", models.CharField(choices=[("construct", "CONSTRUCT"), ("live_classroom", "Trade Construction & Management — Live Classroom")], max_length=24)),
                ("name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=40)),
                ("starting_point", models.CharField(blank=True, max_length=80)),
                ("question", models.TextField(blank=True)),
                ("contact_consent", models.BooleanField(default=False)),
                ("marketing_opt_in", models.BooleanField(default=False)),
                ("source_path", models.CharField(blank=True, max_length=255)),
                ("ip_fingerprint", models.CharField(blank=True, db_index=True, max_length=64)),
                ("status", models.CharField(choices=[("new", "New"), ("contacted", "Contacted"), ("qualified", "Qualified"), ("enrolled", "Enrolled"), ("closed", "Closed")], default="new", max_length=16)),
                ("staff_notes", models.TextField(blank=True)),
                ("last_contacted_at", models.DateTimeField(blank=True, null=True)),
                ("staff_notification_sent_at", models.DateTimeField(blank=True, null=True)),
                ("customer_confirmation_sent_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("assigned_to", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assigned_prospect_enquiries", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
                "permissions": [("export_prospectenquiry", "Can export prospect enquiries")],
                "indexes": [
                    models.Index(fields=["status", "-created_at"], name="pros_status_created_idx"),
                    models.Index(fields=["programme", "-created_at"], name="pros_prog_created_idx"),
                ],
            },
        ),
    ]
