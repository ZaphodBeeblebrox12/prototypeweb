import apps.support.models
import apps.support.storage
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("academy", "0012_google_drive_support_attachment_folder"),
        ("support", "0007_ticket_workflow_sla_assignment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ticketattachment",
            name="file",
            field=models.FileField(
                storage=apps.support.storage.SupportAttachmentStorage(),
                upload_to=apps.support.models.ticket_attachment_upload_path,
            ),
        ),
    ]
