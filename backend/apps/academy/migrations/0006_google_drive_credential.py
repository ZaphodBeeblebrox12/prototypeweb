from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("academy", "0005_course_learning_metadata")]

    operations = [
        migrations.CreateModel(
            name="GoogleDriveCredential",
            fields=[
                ("id", models.PositiveSmallIntegerField(default=1, editable=False, primary_key=True, serialize=False)),
                ("encrypted_refresh_token", models.TextField(blank=True)),
                ("asset_folder_id", models.CharField(blank=True, max_length=255)),
                ("source_folder_id", models.CharField(blank=True, max_length=255)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Google Drive credential",
                "verbose_name_plural": "Google Drive credentials",
            },
        ),
    ]
