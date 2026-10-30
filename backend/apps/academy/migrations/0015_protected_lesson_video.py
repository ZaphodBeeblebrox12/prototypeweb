import apps.academy.video_storage
import django.conf
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("academy", "0014_make_trading_path_free"),
        migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ProtectedLessonVideo",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False,
                        serialize=False,
                    ),
                ),
                (
                    "source_file",
                    models.FileField(
                        blank=True,
                        storage=apps.academy.video_storage.PrivateLessonVideoStorage(),
                        upload_to="apps.academy.models.protected_lesson_video_upload_to",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=["mp4", "mov", "mkv", "webm"]
                            )
                        ],
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending processing"),
                            ("processing", "Processing"),
                            ("ready", "Protected stream ready"),
                            ("failed", "Processing failed"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("stream_directory", models.CharField(blank=True, max_length=512)),
                ("processing_error", models.TextField(blank=True)),
                ("processed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="academy_protected_videos_created",
                        to=django.conf.settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "lesson",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="protected_video",
                        to="academy.lesson",
                    ),
                ),
            ],
            options={
                "ordering": ["lesson__module__course__title", "lesson__title"],
            },
        ),
    ]
