import hashlib
import hmac
import logging
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.notifications.services import NotificationService

from .forms import ProspectEnquiryForm
from .models import ProspectEnquiry

logger = logging.getLogger(__name__)

PROGRAMMES = {
    ProspectEnquiry.Programme.CONSTRUCT: {
        "title": "CONSTRUCT · Trade Construction & Management",
        "description": "Ask about the 70-day guided programme, its assignments, review clinics, instructor support and included community access.",
        "submit_label": "Send my CONSTRUCT enquiry",
    },
    ProspectEnquiry.Programme.LIVE_CLASSROOM: {
        "title": "Trade Construction & Management · Live Classroom",
        "description": "Ask about the next six-week live classroom intake, confirmed dates, fees, format and session details.",
        "submit_label": "Ask about the next live class",
    },
}


def _email_fingerprint(email):
    """Return a keyed fingerprint for a normalised email address."""
    normalised = email.strip().lower()
    return hmac.new(
        str(settings.SECRET_KEY).encode("utf-8"),
        normalised.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _send_enquiry_notifications(enquiry):
    """Send best-effort notifications after the enquiry record has committed."""
    # The console backend writes to server logs only; it is not customer delivery.
    if "console.EmailBackend" in str(getattr(settings, "EMAIL_BACKEND", "")):
        logger.warning("Prospect enquiry email skipped because the console backend is configured enquiry=%s", enquiry.pk)
        return
    staff_recipients = [
        str(value).strip()
        for value in (getattr(settings, "PROSPECT_ENQUIRY_RECIPIENTS", []) or [])
        if str(value).strip()
    ]
    staff_subject = f"New TradeThesis enquiry · {enquiry.get_programme_display()}"
    site_base_url = str(getattr(settings, "SITE_BASE_URL", "") or "").rstrip("/")
    queue_path = reverse("staff_admin_desk_prospect_enquiries")
    queue_url = f"{site_base_url}{queue_path}" if site_base_url else queue_path
    staff_body = (
        "A new prospect enquiry has been saved in the TradeThesis Admin Desk.\n\n"
        f"Reference: {enquiry.short_reference}\n"
        f"Programme: {enquiry.get_programme_display()}\n"
        f"Name: {enquiry.name}\n"
        f"Email: {enquiry.email}\n"
        f"Phone: {enquiry.phone or 'Not provided'}\n"
        f"Starting point: {enquiry.get_starting_point_display()}\n"
        f"Question: {enquiry.question or 'No additional question'}\n\n"
        f"Open the prospect queue: {queue_url}"
    )
    staff_ok = bool(staff_recipients)
    for recipient in staff_recipients:
        try:
            sent = NotificationService.send_simple_email(
                recipient,
                staff_subject,
                staff_body,
            )
            staff_ok = sent and staff_ok
        except Exception:
            logger.exception("Prospect staff notification failed enquiry=%s", enquiry.pk)
            staff_ok = False

    customer_subject = "We received your TradeThesis enquiry"
    customer_body = (
        f"Hello {enquiry.name},\n\n"
        f"Thank you for asking about {enquiry.get_programme_display()}. "
        "Your enquiry has been recorded. The TradeThesis team will review it and "
        "contact you using the details you provided.\n\n"
        f"Reference: {enquiry.short_reference}\n\n"
        "This message confirms receipt only; it is not an enrolment or payment confirmation.\n\n"
        "TradeThesis · Conviction before execution"
    )
    try:
        customer_ok = NotificationService.send_simple_email(
            enquiry.email,
            customer_subject,
            customer_body,
        )
    except Exception:
        logger.exception("Prospect customer confirmation failed enquiry=%s", enquiry.pk)
        customer_ok = False

    update_fields = []
    if staff_ok:
        enquiry.staff_notification_sent_at = timezone.now()
        update_fields.append("staff_notification_sent_at")
    if customer_ok:
        enquiry.customer_confirmation_sent_at = timezone.now()
        update_fields.append("customer_confirmation_sent_at")
    if update_fields:
        enquiry.save(update_fields=update_fields)


@require_http_methods(["GET", "POST"])
def enquiry(request, programme):
    if programme not in PROGRAMMES:
        from django.http import Http404

        raise Http404("This enquiry route is not available.")

    programme_context = PROGRAMMES[programme]
    form = ProspectEnquiryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        # Honeypot submissions receive the same public confirmation but are not stored.
        if form.cleaned_data.get("website"):
            return redirect("prospects:received")

        fingerprint = _email_fingerprint(form.cleaned_data["email"])
        if fingerprint:
            recent_count = ProspectEnquiry.objects.filter(
                email_fingerprint=fingerprint,
                created_at__gte=timezone.now() - timedelta(hours=1),
            ).count()
            if recent_count >= 5:
                form.add_error(
                    None,
                    "We have received several requests from this connection recently. "
                    "Please try again later or contact us through the details on the website.",
                )
                return render(
                    request,
                    "prospects/enquiry_form.html",
                    {"form": form, "programme": programme_context},
                    status=429,
                )

        with transaction.atomic():
            enquiry_record = ProspectEnquiry.objects.create(
                programme=programme,
                name=form.cleaned_data["name"],
                email=form.cleaned_data["email"],
                phone=form.cleaned_data["phone"].strip(),
                starting_point=form.cleaned_data["starting_point"],
                question=form.cleaned_data["question"].strip(),
                contact_consent=form.cleaned_data["contact_consent"],
                marketing_opt_in=form.cleaned_data["marketing_opt_in"],
                source_path=request.path[:255],
                email_fingerprint=fingerprint,
            )

        _send_enquiry_notifications(enquiry_record)
        return redirect("prospects:received")

    return render(
        request,
        "prospects/enquiry_form.html",
        {"form": form, "programme": programme_context},
    )


def received(request):
    return render(
        request,
        "prospects/enquiry_received.html",
        {"programme": None, "reference": ""},
    )
