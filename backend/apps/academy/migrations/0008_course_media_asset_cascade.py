"""Allow course deletion to remove only the media records owned by that course."""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("academy", "0007_alter_courseimportasset_file_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="coursemediaasset",
            name="course",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="media_assets",
                to="academy.course",
            ),
        ),
    ]
