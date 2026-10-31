"""Package uploaded lesson videos as private AES-128 HLS VOD."""
import secrets
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.academy.models import ProtectedLessonVideo
from apps.academy.video_storage import lesson_video_storage


class Command(BaseCommand):
    help = "Convert uploaded lesson videos to private AES-128 HLS using Drive or durable local storage."

    def add_arguments(self, parser):
        parser.add_argument("--lesson", help="Process one lesson UUID.")
        parser.add_argument("--all", action="store_true", help="Process all pending/failed uploads.")
        parser.add_argument("--force", action="store_true", help="Rebuild already-ready streams.")

    def handle(self, *args, **options):
        if (
            not settings.DEBUG
            and getattr(settings, "ACADEMY_REQUIRE_DURABLE_VIDEO_STORAGE", True)
            and not lesson_video_storage.is_durable
        ):
            raise CommandError(
                "Refusing to process videos without durable storage. Connect Google Drive "
                "(using the Academy asset folder) or mount a persistent disk."
            )

        configured_binary = str(getattr(settings, "ACADEMY_FFMPEG_BINARY", "ffmpeg") or "ffmpeg")
        ffmpeg = shutil.which(configured_binary) or (
            configured_binary if Path(configured_binary).is_file() else ""
        )
        if not ffmpeg:
            try:
                from imageio_ffmpeg import get_ffmpeg_exe
                ffmpeg = get_ffmpeg_exe()
            except (ImportError, RuntimeError):
                ffmpeg = ""
        if not ffmpeg:
            raise CommandError(
                "FFmpeg was not found. Install FFmpeg in the service image, install "
                "the imageio-ffmpeg wheel, or set ACADEMY_FFMPEG_BINARY."
            )

        videos = ProtectedLessonVideo.objects.select_related("lesson").order_by("created_at")
        if options["lesson"]:
            videos = videos.filter(lesson_id=options["lesson"])
        elif not options["all"]:
            videos = videos.filter(
                status__in=(ProtectedLessonVideo.Status.PENDING, ProtectedLessonVideo.Status.FAILED)
            )
        if not options["force"]:
            videos = videos.exclude(status=ProtectedLessonVideo.Status.READY)
        videos = list(videos)
        if not videos:
            self.stdout.write("No lesson videos require processing.")
            return

        for video in videos:
            self._process_one(video, ffmpeg)

    def _process_one(self, video, ffmpeg):
        if not video.source_file:
            self._fail(video, "No source video file is attached.")
            return

        previous_status = video.status
        previous_prefix = video.stream_directory
        previous_processed_at = video.processed_at
        output_prefix = f"streams/{video.pk}/{uuid.uuid4().hex}"
        uploaded_names = []
        video.status = ProtectedLessonVideo.Status.PROCESSING
        video.processing_error = ""
        video.processed_at = None
        video.save(update_fields=("status", "processing_error", "processed_at", "updated_at"))

        try:
            # FFmpeg needs local seekable files. Download the private Drive source
            # to a short-lived worker directory, then upload each encrypted output.
            with tempfile.TemporaryDirectory(prefix="academy-video-") as work:
                work_dir = Path(work)
                source_path = work_dir / f"source{Path(video.source_file.name).suffix or '.mp4'}"
                with video.source_file.open("rb") as source, source_path.open("wb") as target:
                    shutil.copyfileobj(source, target, length=1024 * 1024)

                output_dir = work_dir / "hls"
                output_dir.mkdir()
                key = secrets.token_bytes(16)
                iv = secrets.token_hex(16)
                key_path = output_dir / "encryption.key"
                key_path.write_bytes(key)
                key_path.chmod(0o600)
                key_info_path = work_dir / "key-info.txt"
                key_info_path.write_text(
                    f"protected-key\n{key_path}\n0x{iv}\n", encoding="utf-8"
                )
                manifest_path = output_dir / "index.m3u8"
                command = [
                    ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(source_path),
                    "-map", "0:v:0", "-map", "0:a:0?",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                    "-profile:v", "main", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "128k",
                    "-f", "hls", "-hls_time", "6", "-hls_playlist_type", "vod",
                    "-hls_flags", "independent_segments",
                    "-hls_segment_filename", str(output_dir / "segment_%05d.ts"),
                    "-hls_key_info_file", str(key_info_path), str(manifest_path),
                ]
                subprocess.run(
                    command, check=True, capture_output=True, text=True,
                    timeout=int(getattr(settings, "ACADEMY_VIDEO_FFMPEG_TIMEOUT", 14400)),
                )

                segments = sorted(output_dir.glob("segment_*.ts"))
                if not manifest_path.is_file() or not segments or len(key) != 16:
                    raise RuntimeError("FFmpeg did not create a valid encrypted HLS rendition.")

                objects = [(f"{output_prefix}/encryption.key", key_path),
                           (f"{output_prefix}/index.m3u8", manifest_path)]
                objects.extend((f"{output_prefix}/{segment.name}", segment) for segment in segments)
                for logical_name, local_path in objects:
                    with local_path.open("rb") as handle:
                        lesson_video_storage.save(logical_name, File(handle, name=local_path.name))
                    uploaded_names.append(logical_name)

            video.status = ProtectedLessonVideo.Status.READY
            video.processing_error = ""
            video.stream_directory = output_prefix
            video.processed_at = timezone.now()
            video.save(update_fields=("status", "processing_error", "stream_directory", "processed_at", "updated_at"))
            if previous_prefix and previous_prefix != output_prefix:
                try:
                    self._delete_rendition(previous_prefix)
                except OSError:
                    self.stderr.write("The previous Drive rendition could not be cleaned up; the new stream is active.")
            self.stdout.write(self.style.SUCCESS(
                f"Protected stream ready: {video.lesson.title} ({len(segments)} segments)."
            ))
        except (OSError, subprocess.SubprocessError, RuntimeError, ValueError) as exc:
            for name in uploaded_names:
                try:
                    lesson_video_storage.delete(name)
                except OSError:
                    self.stderr.write(f"Could not clean up incomplete Drive object: {name}")
            if previous_status == ProtectedLessonVideo.Status.READY and previous_prefix:
                video.status = ProtectedLessonVideo.Status.READY
                video.stream_directory = previous_prefix
                video.processed_at = previous_processed_at
                video.processing_error = f"Rebuild failed; previous stream retained: {exc}"[-1200:]
            else:
                video.status = ProtectedLessonVideo.Status.FAILED
                video.stream_directory = ""
                video.processing_error = str(exc)[-1200:]
            video.save(update_fields=("status", "stream_directory", "processed_at", "processing_error", "updated_at"))
            raise CommandError(f"Processing failed for lesson {video.lesson_id}: {exc}") from exc

    @staticmethod
    def _delete_rendition(prefix):
        # Read the old playlist before deleting it so its segment keys remain discoverable.
        try:
            with lesson_video_storage.open(f"{prefix}/index.m3u8", "rb") as handle:
                playlist = handle.read().decode("utf-8")
        except (OSError, FileNotFoundError):
            playlist = ""
        for line in playlist.splitlines():
            segment = line.strip()
            if segment and not segment.startswith("#") and "/" not in segment:
                lesson_video_storage.delete(f"{prefix}/{segment}")
        lesson_video_storage.delete(f"{prefix}/index.m3u8")
        lesson_video_storage.delete(f"{prefix}/encryption.key")

    @staticmethod
    def _fail(video, message):
        video.status = ProtectedLessonVideo.Status.FAILED
        video.processing_error = message
        video.save(update_fields=("status", "processing_error", "updated_at"))
