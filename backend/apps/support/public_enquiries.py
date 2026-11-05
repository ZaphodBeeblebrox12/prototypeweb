"""Anonymous prospect enquiries for the public TradeThesis programme pages.

The marketing site is hosted separately from Django. The endpoint therefore
uses a deliberately narrow Origin allowlist instead of a session/CSRF token:
it accepts only urlencoded POSTs from the configured public-site origin(s),
does not read or mutate an authenticated user's state, and applies validation,
a honeypot and a per-email submission limit.
"""
import logging
from datetime import timedelta
from urllib.parse import urlsplit

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.accounts.models import User
from apps.notifications.models import Notification

from .models import CourseEnquiry

logger = logging.getLogger(__name__)

PROGRAMME_RETURN_PATHS = {
    CourseEnquiry.Programme.CONSTRUCT: "construct.html",
    CourseEnquiry.Programme.LIVE_CLASSROOM: "live-class.html",
}
MAX_ENQUIRIES_PER_EMAIL_PER_PROGRAMME_PER_HOUR = 2


def _origin(value):
    """Return a strict http(s) origin, rejecting paths and user-info."""
    if not value:
        return ""
    try:
        parsed = urlsplit(value.strip())
        if (
            parsed.scheme.lower() not in {"http", "https"}
            or not parsed.netloc
            or parsed.username
            or parsed.password
            or parsed.path not in {"", "/"}
            or parsed.query
            or parsed.fragment
        ):
            return ""
        return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}"
    except (TypeError, ValueError):
        return ""


def _request_public_origin(request):
    """Use Origin where supplied; otherwise derive the origin from Referer."""
    candidate = request.headers.get("Origin", "").strip()
    if not candidate:
        referer = request.headers.get("Referer", "").strip()
        try:
            parsed = urlsplit(referer)
            candidate = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else ""
        except (TypeError, ValueError):
            candidate = ""
    normalized = _origin(candidate)
    allowed = {
        item for item in (
            _origin(value)
            for value in getattr(settings, "TRADETHESIS_PUBLIC_SITE_ORIGINS", [])
        ) if item
    }
    return normalized if normalized and normalized in allowed else ""


def _return_to_public_page(origin, programme, result):
    page = PROGRAMME_RETURN_PATHS.get(programme, "courses.html")
    return HttpResponseRedirect(f"{origin}/{page}?enquiry={result}#enquiry-form")


def _notify_authorized_staff(enquiry, request):
    """Alert only active staff who can open and work public prospect records."""
    staff = [
        user for user in User.objects.filter(is_staff=True, is_active=True).order_by("pk")
        if (
            user.has_perm("support.view_courseenquiry")
            and user.has_perm("support.change_courseenquiry")
        )
    ]
    if not staff:
        logger.error(
            "Course enquiry %s was stored, but no active staff account has "
            "support.change_courseenquiry permission.", enquiry.pk,
        )
        return

    detail_url = request.build_absolute_uri(
        reverse("staff_admin_desk_course_enquiry", args=[enquiry.pk])
    )
    subject = f"New {enquiry.get_programme_display()} enquiry · {enquiry.short_id}"
    message = (
        f"{enquiry.name} ({enquiry.email}) submitted a programme enquiry.\n\n"
        f"Starting point: {enquiry.get_starting_point_display() if enquiry.starting_point else 'Not specified'}\n"
        f"Question: {enquiry.message[:1200] or 'No additional question supplied.'}\n\n"
        f"Open the enquiry in Admin Desk: {detail_url}"
    )
    for member in staff:
        try:
            Notification.objects.create(
                user=member,
                notification_type=Notification.NotificationType.SYSTEM,
                title=subject[:255],
                message=message[:4000],
                link=reverse("staff_admin_desk_course_enquiry", args=[enquiry.pk]),
                metadata={
                    "source": "course_enquiry",
                    "enquiry_id": str(enquiry.pk),
                },
            )
        except Exception:
            logger.exception(
                "Could not create course-enquiry notification for staff user=%s enquiry=%s",
                member.pk, enquiry.pk,
            )
        if member.email:
            try:
                send_mail(subject, message, None, [member.email], fail_silently=False)
            except Exception:
                # Saving the enquiry and the staff in-app alert are independent
                # of the configured outbound email service.
                logger.exception(
                    "Course-enquiry staff email failed user=%s enquiry=%s",
                    member.pk, enquiry.pk,
                )


def _send_receipt(enquiry):
    """Attempt a transactional receipt; the saved enquiry remains authoritative."""
    subject = "We received your TradeThesis enquiry"
    message = (
        f"Hello {enquiry.name},\n\n"
        f"We have received your enquiry about {enquiry.get_programme_display()}. "
        "A member of the TradeThesis team will use this email address to follow up.\n\n"
        "This message confirms receipt only; it is not a course enrolment or payment confirmation.\n\n"
        "TradeThesis"
    )
    try:
        sent = send_mail(subject, message, None, [enquiry.email], fail_silently=False)
    except Exception as exc:
        enquiry.confirmation_email_status = "failed"
        enquiry.confirmation_email_error = type(exc).__name__[:200]
        enquiry.save(update_fields=[
            "confirmation_email_status", "confirmation_email_error", "updated_at",
        ])
        logger.exception("Course-enquiry receipt email failed enquiry=%s", enquiry.pk)
        return

    if sent:
        enquiry.confirmation_email_status = "accepted"
        enquiry.confirmation_email_sent_at = timezone.now()
        enquiry.confirmation_email_error = ""
    else:
        enquiry.confirmation_email_status = "failed"
        enquiry.confirmation_email_error = "Email backend did not accept the message."
    enquiry.save(update_fields=[
        "confirmation_email_status", "confirmation_email_sent_at",
        "confirmation_email_error", "updated_at",
    ])


@csrf_exempt
@require_POST
def create_course_enquiry(request):
    """Accept a public programme enquiry without creating a member support ticket."""
    origin = _request_public_origin(request)
    if not origin:
        return HttpResponseForbidden(
            "This form can only be submitted from the configured TradeThesis website."
        )

    content_type = request.content_type or ""
    if content_type not in {"application/x-www-form-urlencoded", "multipart/form-data"}:
        return HttpResponseForbidden("Unsupported form submission.")

    try:
        content_length = int(request.META.get("CONTENT_LENGTH") or 0)
    except (TypeError, ValueError):
        return HttpResponse("Invalid form size.", status=400)
    if content_length > 16 * 1024:
        return HttpResponse("This enquiry is too large. Please shorten your message.", status=413)

    # Honeypot fields are hidden from real users. Treat a bot hit as a quiet
    # no-op so the endpoint does not become a useful spam-response oracle.
    if (request.POST.get("company_website") or "").strip():
        return _return_to_public_page(origin, request.POST.get("programme", ""), "received")

    programme = (request.POST.get("programme") or "").strip()
    if programme not in PROGRAMME_RETURN_PATHS:
        return _return_to_public_page(origin, CourseEnquiry.Programme.CONSTRUCT, "invalid")

    name = " ".join((request.POST.get("name") or "").split())
    email = (request.POST.get("email") or "").strip().lower()
    starting_point = (request.POST.get("starting_point") or "").strip()
    message = (request.POST.get("message") or "").strip()
    consent = (request.POST.get("consent") or "").strip().lower() in {"1", "yes", "on", "true"}

    errors = []
    if len(name) < 2 or len(name) > 120:
        errors.append("name")
    try:
        validate_email(email)
    except ValidationError:
        errors.append("email")
    if len(email) > 254:
        errors.append("email")
    if starting_point and starting_point not in CourseEnquiry.StartingPoint.values:
        errors.append("starting_point")
    if len(message) > 2000:
        errors.append("message")
    if not consent:
        errors.append("consent")
    if errors:
        return _return_to_public_page(origin, programme, "invalid")

    now = timezone.now()
    recent_count = CourseEnquiry.objects.filter(
        programme=programme,
        email__iexact=email,
        created_at__gte=now - timedelta(hours=1),
    ).count()
    if recent_count >= MAX_ENQUIRIES_PER_EMAIL_PER_PROGRAMME_PER_HOUR:
        return _return_to_public_page(origin, programme, "recent")

    enquiry = CourseEnquiry.objects.create(
        programme=programme,
        name=name,
        email=email,
        starting_point=starting_point,
        message=message,
        consent_at=now,
    )
    _send_receipt(enquiry)
    _notify_authorized_staff(enquiry, request)
    return _return_to_public_page(origin, programme, "received")
