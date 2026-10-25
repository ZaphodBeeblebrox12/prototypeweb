from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("academy", "0004_course_builder_draft_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="category",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="course",
            name="level",
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name="course",
            name="estimated_duration",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="course",
            name="learning_outcomes",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
