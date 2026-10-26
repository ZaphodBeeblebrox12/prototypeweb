from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("academy", "0011_course_catalogue_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="googledrivecredential",
            name="support_attachment_folder_id",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
