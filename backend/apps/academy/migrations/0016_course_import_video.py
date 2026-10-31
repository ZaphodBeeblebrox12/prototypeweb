import apps.academy.models
import apps.academy.video_storage
import django.conf
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("academy", "0015_protected_lesson_video"),
        migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CourseImportVideo",
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
                ("lesson_id", models.CharField(max_length=120)),
                (
                    "source_file",
                    models.FileField(
                        blank=True,
                        max_length=512,
                        storage=apps.academy.video_storage.PrivateLessonVideoStorage(),
                        upload_to=apps.academy.models.course_import_video_upload_to,
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=["mp4", "mov", "mkv", "webm"]
                            )
                        ],
                    ),
                ),
                ("original_filename", models.CharField(blank=True, max_length=255)),
                ("size_bytes", models.PositiveBigIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "course_import",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="videos",
                        to="academy.courseimport",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="academy_course_import_videos_uploaded",
                        to=django.conf.settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["course_import_id", "lesson_id"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("course_import", "lesson_id"),
                        name="academy_import_video_lesson_uq",
                    )
                ],
            },
        ),
    ]
