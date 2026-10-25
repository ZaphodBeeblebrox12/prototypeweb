from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("academy", "0008_course_media_asset_cascade"),
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
                    ("deleted", "Deleted by an administrator"),
                ],
                default="review",
                max_length=16,
            ),
        ),
    ]
