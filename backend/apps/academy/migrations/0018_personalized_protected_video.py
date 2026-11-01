import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("academy", "0017_protected_lesson_video_source_path_length"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PersonalizedProtectedVideo",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("status", models.CharField(choices=[("pending", "Waiting to prepare"), ("processing", "Preparing personalised video"), ("ready", "Personalised video ready"), ("failed", "Personalised video preparation failed"), ("revoked", "Access revoked")], default="pending", max_length=16)),
                ("stream_directory", models.CharField(blank=True, max_length=512)),
                ("tracking_code", models.CharField(blank=True, max_length=16)),
                ("processing_error", models.TextField(blank=True)),
                ("processed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("protected_video", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="personalized_renditions", to="academy.protectedlessonvideo")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="academy_personalized_videos", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["protected_video__lesson__module__course__title", "protected_video__lesson__title"],
            },
        ),
        migrations.AddConstraint(
            model_name="personalizedprotectedvideo",
            constraint=models.UniqueConstraint(fields=("user", "protected_video"), name="acad_pvid_user_src_uniq"),
        ),
        migrations.AddIndex(
            model_name="personalizedprotectedvideo",
            index=models.Index(fields=["user", "status"], name="acad_pvid_user_stat_idx"),
        ),
    ]
