import apps.academy.models
import apps.academy.video_storage
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("academy", "0016_course_import_video"),
    ]

    operations = [
        migrations.AlterField(
            model_name="protectedlessonvideo",
            name="source_file",
            field=models.FileField(
                blank=True,
                max_length=512,
                storage=apps.academy.video_storage.PrivateLessonVideoStorage(),
                upload_to=apps.academy.models.protected_lesson_video_upload_to,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["mp4", "mov", "mkv", "webm"]
                    )
                ],
            ),
        ),
    ]
