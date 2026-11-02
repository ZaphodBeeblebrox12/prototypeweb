from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("academy", "0018_personalized_protected_video"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="share_title",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="course",
            name="share_message",
            field=models.TextField(blank=True),
        ),
    ]
