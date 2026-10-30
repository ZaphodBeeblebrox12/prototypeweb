"""Package uploaded lesson videos as private AES-128-encrypted HLS VOD."""
import os
import secrets
import shutil
import subprocess
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.academy.models import ProtectedLessonVideo


class Command(BaseCommand):
    help = (
        "Convert uploaded lesson videos to private AES-128 HLS. "
        "Requires FFmpeg and durable private video storage."
    )

    def add_arguments(self, parser):
        parser.add_argument("--lesson", help="Process one lesson UUID.")
        parser.add_argument("--all", action="store_true", help="Process all pending/failed uploads.")
        parser.add_argument("--force", action="store_true", help="Rebuild already-ready streams.")

    def handle(self, *args, **options):
        if (
            not settings.DEBUG
            and getattr(settings, "ACADEMY_REQUIRE_DURABLE_VIDEO_STORAGE", True)
            and not getattr(settings, "ACADEMY_VIDEO_STORAGE_DURABLE", False)
        ):
            raise CommandError(
                "Refusing to process videos on ephemeral storage. Mount a persistent disk, "
                "set ACADEMY_VIDEO_STORAGE_ROOT to its mount path, and set "
                "ACADEMY_VIDEO_STORAGE_DURABLE=true."
            )

        configured_binary = str(getattr(settings, "ACADEMY_FFMPEG_BINARY", "ffmpeg") or "ffmpeg")
        ffmpeg = shutil.which(configured_binary) or (
            configured_binary if Path(configured_binary).is_file() else ""
        )
        if not ffmpeg:
            raise CommandError(
                "FFmpeg was not found. Install FFmpeg in the service image or set "
                "ACADEMY_FFMPEG_BINARY to its executable path."
            )

        videos = ProtectedLessonVideo.objects.select_related("lesson").order_by("created_at")
        if options["lesson"]:
            videos = videos.filter(lesson_id=options["lesson"])
        elif not options["all"]:
            videos = videos.filter(
                status__in=(
                    ProtectedLessonVideo.Status.PENDING,
                    ProtectedLessonVideo.Status.FAILED,
                )
            )
        if not options["force"]:
            videos = videos.exclude(status=ProtectedLessonVideo.Status.READY)

        videos = list(videos)
        if not videos:
            self.stdout.write("No lesson videos require processing.")
            return

        root = Path(settings.ACADEMY_VIDEO_STORAGE_ROOT).resolve()
        root.mkdir(parents=True, exist_ok=True)
        for video in videos:
            self._process_one(video, ffmpeg, root, force=options["force"])

    def _process_one(self, video, ffmpeg, root, force=False):
        if not video.source_file:
            video.status = ProtectedLessonVideo.Status.FAILED
            video.processing_error = "No source video file is attached."
            video.save(update_fields=["status", "processing_error", "updated_at"])
            self.stderr.write(f"Skipped {video.lesson_id}: source file is missing.")
            return

        try:
            source = Path(video.source_file.path).resolve()
        except (NotImplementedError, ValueError) as exc:
            raise CommandError(
                f"Video {video.lesson_id} is not on local filesystem storage; "
                "the FFmpeg worker requires a mounted local source volume."
            ) from exc
        if not source.is_file():
            raise CommandError(f"Source file for lesson {video.lesson_id} is missing.")

        output_dir = (root / "streams" / str(video.pk)).resolve()
        if root not in output_dir.parents:
            raise CommandError("Resolved HLS output directory is outside private video storage.")
        if output_dir.exists():
            if not force and video.status == ProtectedLessonVideo.Status.READY:
                return
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        key = secrets.token_bytes(16)
        iv = secrets.token_hex(16)
        key_path = output_dir / "encryption.key"
        key_path.write_bytes(key)
        key_path.chmod(0o600)
        key_info_path = None

        video.status = ProtectedLessonVideo.Status.PROCESSING
        video.processing_error = ""
        video.stream_directory = str(output_dir.relative_to(root))
        video.processed_at = None
        video.save(
            update_fields=(
                "status",
                "processing_error",
                "stream_directory",
                "processed_at",
                "updated_at",
            )
        )

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                prefix="academy-hls-key-",
                suffix=".txt",
                dir=str(root),
                delete=False,
            ) as key_info:
                key_info_path = key_info.name
                key_info.write(f"protected-key\n{key_path}\n0x{iv}\n")

            command = [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(source),
                "-map",
                "0:v:0",
                "-map",
                "0:a:0?",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "22",
                "-profile:v",
                "main",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-f",
                "hls",
                "-hls_time",
                "6",
                "-hls_playlist_type",
                "vod",
                "-hls_flags",
                "independent_segments",
                "-hls_segment_filename",
                str(output_dir / "segment_%05d.ts"),
                "-hls_key_info_file",
                key_info_path,
                str(output_dir / "index.m3u8"),
            ]
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=int(getattr(settings, "ACADEMY_VIDEO_FFMPEG_TIMEOUT", 14400)),
            )

            manifest = output_dir / "index.m3u8"
            segments = list(output_dir.glob("segment_*.ts"))
            if not manifest.is_file() or not segments:
                raise RuntimeError("FFmpeg finished without creating a valid HLS playlist.")
            if key_path.stat().st_size != 16:
                raise RuntimeError("The HLS encryption key is invalid.")

            video.status = ProtectedLessonVideo.Status.READY
            video.processing_error = ""
            video.processed_at = timezone.now()
            video.save(
                update_fields=("status", "processing_error", "processed_at", "updated_at")
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Protected stream ready: {video.lesson.title} ({len(segments)} segments)."
                )
            )
        except (OSError, subprocess.SubprocessError, RuntimeError) as exc:
            if output_dir.exists():
                shutil.rmtree(output_dir, ignore_errors=True)
            video.status = ProtectedLessonVideo.Status.FAILED
            video.stream_directory = ""
            video.processing_error = str(exc)[-1200:]
            video.save(
                update_fields=("status", "stream_directory", "processing_error", "updated_at")
            )
            raise CommandError(f"Processing failed for lesson {video.lesson_id}: {exc}") from exc
        finally:
            if key_info_path and os.path.exists(key_info_path):
                os.unlink(key_info_path)
