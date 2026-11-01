"""Build one paid learner's encrypted HLS rendition with a burned-in identity mark."""
import hashlib
import random
import secrets
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.academy.models import (
    CourseEntitlement,
    PersonalizedProtectedVideo,
    ProtectedLessonVideo,
)
from apps.academy.services import get_active_entitlement
from apps.academy.video_storage import lesson_video_storage


def _ffmpeg_binary():
    configured = shutil.which("ffmpeg")
    if configured:
        return configured
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        return get_ffmpeg_exe()
    except (ImportError, RuntimeError):
        return ""


def _position_expression(rng, interval, duration):
    count = max(2, int(duration // interval) + 2)
    points = [rng.uniform(0.06, 0.78) for _ in range(count)]
    expression = f"{points[-1]:.6f}"
    for index in reversed(range(count - 1)):
        start = index * interval
        end = (index + 1) * interval
        a, b = points[index], points[index + 1]
        blend = (
            f"({a:.6f}+({b-a:.6f})*"
            f"min(1,max(0,(t-{start:.3f})/{interval:.3f})))"
        )
        expression = f"if(lt(t,{end:.3f}),{blend},{expression})"
    return expression


def _delete_rendition(prefix):
    if not prefix:
        return
    try:
        with lesson_video_storage.open(f"{prefix}/index.m3u8", "rb") as handle:
            playlist = handle.read().decode("utf-8")
    except (OSError, FileNotFoundError, UnicodeDecodeError):
        playlist = ""
    for line in playlist.splitlines():
        name = line.strip()
        if name and not name.startswith("#") and "/" not in name:
            lesson_video_storage.delete(f"{prefix}/{name}")
    lesson_video_storage.delete(f"{prefix}/index.m3u8")
    lesson_video_storage.delete(f"{prefix}/encryption.key")


class Command(BaseCommand):
    help = "Create one purchaser-specific, burned-watermark encrypted HLS rendition."

    def add_arguments(self, parser):
        parser.add_argument("--rendition", required=True, help="PersonalizedProtectedVideo UUID.")
        parser.add_argument("--force", action="store_true", help="Rebuild an already-ready rendition.")

    def handle(self, *args, **options):
        try:
            rendition_id = uuid.UUID(str(options["rendition"]))
        except (TypeError, ValueError) as exc:
            raise CommandError("--rendition must be a valid UUID.") from exc

        rendition = (
            PersonalizedProtectedVideo.objects
            .select_related("user", "protected_video__lesson__module__course")
            .filter(pk=rendition_id)
            .first()
        )
        if rendition is None:
            raise CommandError(f"No personalised video rendition found with ID {rendition_id}.")
        if rendition.status == PersonalizedProtectedVideo.Status.READY and rendition.stream_directory and not options["force"]:
            self.stdout.write("Personalised rendition is already ready.")
            return

        ffmpeg = _ffmpeg_binary()
        if not ffmpeg:
            self._fail(rendition, "FFmpeg was not found; install imageio-ffmpeg or configure ACADEMY_FFMPEG_BINARY.")
            raise CommandError("FFmpeg was not found.")

        video = rendition.protected_video
        entitlement = get_active_entitlement(rendition.user, video.lesson.module.course)
        if (
            entitlement is None
            or entitlement.source != CourseEntitlement.Source.PURCHASE
            or not entitlement.has_access_at()
        ):
            rendition.status = PersonalizedProtectedVideo.Status.REVOKED
            rendition.processing_error = "Paid course entitlement is no longer active."
            rendition.save(update_fields=["status", "processing_error", "updated_at"])
            if rendition.stream_directory:
                _delete_rendition(rendition.stream_directory)
                rendition.stream_directory = ""
                rendition.save(update_fields=["stream_directory", "updated_at"])
            self.stdout.write("Skipped: learner does not have an active paid entitlement.")
            return
        if video.status != ProtectedLessonVideo.Status.READY or not video.source_file:
            self._fail(rendition, "The original protected source video is not ready.")
            raise CommandError("The original protected source video is not ready.")

        previous_prefix = rendition.stream_directory
        output_prefix = f"personalized/{video.pk}/{rendition.user_id}/{uuid.uuid4().hex}"
        uploaded_names = []
        rendition.status = PersonalizedProtectedVideo.Status.PROCESSING
        rendition.processing_error = ""
        if not rendition.tracking_code:
            rendition.tracking_code = secrets.token_hex(5).upper()
        rendition.save(update_fields=["status", "processing_error", "tracking_code", "updated_at"])

        try:
            with tempfile.TemporaryDirectory(prefix="academy-personal-video-") as work:
                work_dir = Path(work)
                source_suffix = Path(video.source_file.name).suffix or ".mp4"
                source_path = work_dir / f"source{source_suffix}"
                with video.source_file.open("rb") as source, source_path.open("wb") as target:
                    shutil.copyfileobj(source, target, length=1024 * 1024)

                output_dir = work_dir / "hls"
                output_dir.mkdir()
                key = secrets.token_bytes(16)
                key_path = output_dir / "encryption.key"
                key_path.write_bytes(key)
                key_path.chmod(0o600)
                key_info_path = work_dir / "key-info.txt"
                key_info_path.write_text(
                    f"protected-key\n{key_path}\n", encoding="utf-8"
                )
                manifest_path = output_dir / "index.m3u8"
                text_path = work_dir / "viewer-watermark.txt"

                display_name = str(getattr(rendition.user, "full_name", "") or "").strip()
                email = str(rendition.user.email or "").strip()
                first_line = f"{display_name}  |  {email}" if display_name else email
                text_path.write_text(
                    f"{first_line}\nTradeThesis viewer ID: {rendition.tracking_code}\n",
                    encoding="utf-8",
                )

                # Stable, pseudo-random smooth movement per viewer/video pair.
                seed = int(hashlib.sha256(
                    f"{rendition.user_id}:{video.pk}:{rendition.tracking_code}".encode()
                ).hexdigest()[:16], 16)
                rng = random.Random(seed)
                duration = max(float(video.lesson.duration_minutes or 1) * 60, 60.0)
                x_expr = _position_expression(rng, 4.0, duration)
                y_expr = _position_expression(rng, 4.0, duration)
                drawtext = (
                    f"drawtext=textfile='{text_path.as_posix()}':reload=0:"
                    "font='DejaVu Sans':fontsize='max(18,min(34,h*0.030))':"
                    "fontcolor=white@0.90:line_spacing=5:box=1:boxborderw=12:"
                    "boxcolor=black@0.50:borderw=1:bordercolor=white@0.25:"
                    f"x='12+(w-text_w-24)*({x_expr})':"
                    f"y='12+(h-text_h-24)*({y_expr})':"
                    "shadowcolor=black@0.75:shadowx=1:shadowy=1"
                )
                command = [
                    ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(source_path),
                    "-map", "0:v:0", "-map", "0:a:0?",
                    "-vf", drawtext,
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                    "-profile:v", "main", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "128k",
                    "-f", "hls", "-hls_time", "6", "-hls_playlist_type", "vod",
                    "-hls_flags", "independent_segments",
                    "-hls_segment_filename", str(output_dir / "segment_%05d.ts"),
                    "-hls_key_info_file", str(key_info_path), str(manifest_path),
                ]
                subprocess.run(
                    command,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=14400,
                )

                segments = sorted(output_dir.glob("segment_*.ts"))
                playlist = manifest_path.read_text(encoding="utf-8") if manifest_path.is_file() else ""
                if (
                    not segments
                    or "#EXT-X-KEY:METHOD=AES-128" not in playlist
                    or len(key) != 16
                ):
                    raise RuntimeError("FFmpeg did not create a valid encrypted personalised HLS rendition.")

                objects = [
                    (f"{output_prefix}/encryption.key", key_path),
                    (f"{output_prefix}/index.m3u8", manifest_path),
                ]
                objects.extend(
                    (f"{output_prefix}/{segment.name}", segment)
                    for segment in segments
                )
                for logical_name, local_path in objects:
                    with local_path.open("rb") as handle:
                        lesson_video_storage.save(
                            logical_name,
                            File(handle, name=local_path.name),
                        )
                    uploaded_names.append(logical_name)

            # Re-check entitlement after the expensive transcode and upload.
            # A refund/chargeback during processing must not publish a rendition.
            current_entitlement = get_active_entitlement(
                rendition.user, video.lesson.module.course
            )
            if (
                current_entitlement is None
                or current_entitlement.source != CourseEntitlement.Source.PURCHASE
                or not current_entitlement.has_access_at()
            ):
                for name in uploaded_names:
                    lesson_video_storage.delete(name)
                rendition.status = PersonalizedProtectedVideo.Status.REVOKED
                rendition.processing_error = "Paid course entitlement was revoked during video preparation."
                rendition.save(update_fields=["status", "processing_error", "updated_at"])
                self.stdout.write("Discarded personalised rendition because paid access was revoked.")
                return

            rendition.stream_directory = output_prefix
            rendition.status = PersonalizedProtectedVideo.Status.READY
            rendition.processing_error = ""
            rendition.processed_at = timezone.now()
            rendition.save(update_fields=[
                "stream_directory", "status", "processing_error", "processed_at", "updated_at"
            ])
            if previous_prefix and previous_prefix != output_prefix:
                _delete_rendition(previous_prefix)
            self.stdout.write(self.style.SUCCESS(
                f"Personalised protected video ready for user {rendition.user_id} "
                f"({len(segments)} segments, viewer ID {rendition.tracking_code})."
            ))
        except (OSError, subprocess.SubprocessError, RuntimeError, ValueError) as exc:
            for name in uploaded_names:
                try:
                    lesson_video_storage.delete(name)
                except OSError:
                    self.stderr.write(f"Could not clean up incomplete personalised object: {name}")
            self._fail(rendition, str(exc))
            raise CommandError(
                f"Personalised video processing failed for rendition {rendition.pk}: {exc}"
            ) from exc

    @staticmethod
    def _fail(rendition, message):
        rendition.status = PersonalizedProtectedVideo.Status.FAILED
        rendition.processing_error = str(message)[-1200:]
        rendition.save(update_fields=["status", "processing_error", "updated_at"])
