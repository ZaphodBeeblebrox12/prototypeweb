"""Authenticated delivery for encrypted HLS lesson videos.

AES-128 HLS plus session-bound tickets protects origin files and discourages
casual link sharing. It is not standards-based DRM: an entitled viewer's
browser must receive the HLS key to play the video.
"""
import re
from pathlib import PurePosixPath
from urllib.parse import quote

from django.conf import settings
from django.core import signing
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_GET

from .models import ProtectedLessonVideo
from .permissions import is_course_content_admin
from .services import can_access_lesson
from .video_storage import lesson_video_storage

_TICKET_SALT = "tradethesis.academy.protected-video.v1"
_SEGMENT_RE = re.compile(r"^segment_\d{5}\.ts$")


def _stream_object_name(video, filename):
    prefix = PurePosixPath(str(video.stream_directory or ""))
    if (
        prefix.is_absolute()
        or not prefix.parts
        or any(part in {"", ".", ".."} for part in prefix.parts)
        or len(prefix.parts) > 4
    ):
        raise Http404
    return str(prefix / filename)


def _assert_video_access(request, video):
    if is_course_content_admin(request.user):
        return
    if not can_access_lesson(request.user, video.lesson):
        raise Http404


def _make_ticket(request, video):
    if not request.session.session_key:
        request.session.save()
    return signing.dumps(
        {
            "video": str(video.pk),
            "user": str(request.user.pk),
            "session": request.session.session_key,
        },
        salt=_TICKET_SALT,
        compress=True,
    )


def _verify_ticket(request, video, ticket):
    try:
        payload = signing.loads(
            ticket,
            salt=_TICKET_SALT,
            max_age=int(getattr(settings, "ACADEMY_VIDEO_TICKET_MAX_AGE", 14400)),
        )
    except (signing.BadSignature, signing.SignatureExpired, TypeError, ValueError):
        raise Http404 from None
    if (
        payload.get("video") != str(video.pk)
        or payload.get("user") != str(request.user.pk)
        or payload.get("session") != request.session.session_key
    ):
        raise Http404
    _assert_video_access(request, video)


def _private_response_headers(response):
    response["Cache-Control"] = "private, no-store, no-cache, max-age=0, must-revalidate"
    response["Pragma"] = "no-cache"
    response["X-Content-Type-Options"] = "nosniff"
    response["Referrer-Policy"] = "no-referrer"
    response["Cross-Origin-Resource-Policy"] = "same-origin"
    return response


@require_GET
def protected_video_manifest(request, video_id):
    """Return a per-viewer playlist with session-bound URLs for every resource."""
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())

    video = get_object_or_404(
        ProtectedLessonVideo.objects.select_related("lesson__module__course"),
        pk=video_id,
        status=ProtectedLessonVideo.Status.READY,
    )
    _assert_video_access(request, video)

    try:
        with lesson_video_storage.open(_stream_object_name(video, "index.m3u8"), "rb") as source:
            playlist = source.read().decode("utf-8")
        with lesson_video_storage.open(_stream_object_name(video, "encryption.key"), "rb") as key_file:
            key_valid = len(key_file.read()) == 16
    except (OSError, UnicodeDecodeError, NotImplementedError):
        raise Http404 from None
    if not key_valid:
        raise Http404

    ticket = quote(_make_ticket(request, video), safe="")
    key_url = f"{reverse('academy:protected-video-key', args=[video.pk])}?ticket={ticket}"
    segment_url = reverse("academy:protected-video-segment", args=[video.pk, "PLACEHOLDER"])
    rewritten_lines = []
    has_aes128_key = False
    for line in playlist.splitlines():
        stripped = line.strip()
        if stripped.startswith("#EXT-X-KEY:"):
            if "METHOD=AES-128" not in stripped or "URI=" not in stripped:
                raise Http404
            line = re.sub(r'URI="[^"]+"', f'URI="{key_url}"', line)
            has_aes128_key = True
        elif stripped and not stripped.startswith("#"):
            name = PurePosixPath(stripped).name
            if name != stripped or not _SEGMENT_RE.fullmatch(name):
                raise Http404
            line = segment_url.replace("PLACEHOLDER", quote(name, safe="")) + f"?ticket={ticket}"
        rewritten_lines.append(line)

    if not has_aes128_key:
        raise Http404
    response = HttpResponse(
        "\n".join(rewritten_lines) + "\n",
        content_type="application/vnd.apple.mpegurl",
    )
    return _private_response_headers(response)


@require_GET
def protected_video_key(request, video_id):
    if not request.user.is_authenticated:
        raise Http404
    video = get_object_or_404(
        ProtectedLessonVideo.objects.select_related("lesson__module__course"),
        pk=video_id,
        status=ProtectedLessonVideo.Status.READY,
    )
    _verify_ticket(request, video, request.GET.get("ticket", ""))
    try:
        with lesson_video_storage.open(_stream_object_name(video, "encryption.key"), "rb") as key_file:
            key = key_file.read()
    except (OSError, NotImplementedError):
        raise Http404 from None
    if len(key) != 16:
        raise Http404
    return _private_response_headers(HttpResponse(key, content_type="application/octet-stream"))


@require_GET
def protected_video_segment(request, video_id, segment_name):
    if not request.user.is_authenticated or not _SEGMENT_RE.fullmatch(segment_name):
        raise Http404
    video = get_object_or_404(
        ProtectedLessonVideo.objects.select_related("lesson__module__course"),
        pk=video_id,
        status=ProtectedLessonVideo.Status.READY,
    )
    _verify_ticket(request, video, request.GET.get("ticket", ""))
    try:
        segment = lesson_video_storage.open(_stream_object_name(video, segment_name), "rb")
    except (OSError, FileNotFoundError, NotImplementedError):
        raise Http404 from None
    response = FileResponse(segment, content_type="video/mp2t")
    return _private_response_headers(response)
