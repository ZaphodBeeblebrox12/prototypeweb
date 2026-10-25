import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("academy", "0003_course_asset_original_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="courseimport",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Builder draft"),
                    ("review", "Awaiting review"),
                    ("published", "Published"),
                    ("rejected", "Rejected"),
                    ("superseded", "Superseded by a newer import"),
                ],
                default="review",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="courseimport",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
