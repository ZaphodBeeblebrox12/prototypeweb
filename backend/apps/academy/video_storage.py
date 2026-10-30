"""Private filesystem storage for original lesson videos.

Unlike image/course-asset storage, video sources must remain on a filesystem
that FFmpeg can read and that is never exposed through MEDIA_URL or a public CDN.
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class PrivateLessonVideoStorage(FileSystemStorage):
    """Store source videos outside Django's public media/static directories."""

    def __init__(self):
        location = getattr(settings, "ACADEMY_VIDEO_STORAGE_ROOT", "")
        if not location:
            raise ImproperlyConfigured("ACADEMY_VIDEO_STORAGE_ROOT must be configured.")
        super().__init__(location=str(location), base_url=None)

    def url(self, name):
        raise ValueError("Protected lesson videos do not have public file URLs.")


lesson_video_storage = PrivateLessonVideoStorage()
