"""Add provider-confirmed delivery outcomes to email audit records."""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("emailing", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="delivery",
            name="state",
            field=models.CharField(
                choices=[
                    ("queued", "Queued"),
                    ("sending", "Sending"),
                    ("sent", "Sent"),
                    ("delivered", "Delivered"),
                    ("delayed", "Delivery delayed"),
                    ("failed", "Failed"),
                    ("bounced", "Bounced"),
                    ("complained", "Complained"),
                    ("suppressed", "Suppressed"),
                ],
                default="queued",
                max_length=20,
            ),
        ),
    ]
