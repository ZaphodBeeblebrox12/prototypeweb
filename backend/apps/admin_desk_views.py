"""Creator-facing Admin Desk workflows; model imports stay inside request handlers."""
from datetime import timedelta
import logging

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Count, Max, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST


logger = logging.getLogger(__name__)


def _allowed(user, permission):
    return bool(user.is_superuser or user.has_perm(permission))


def _guard(request, permission=None):
    if not request.user.is_authenticated or not request.user.is_active or not request.user.is_staff:
        raise PermissionDenied
    if permission and not _allowed(request.user, permission):
        raise PermissionDenied


def _audit(action, actor, object_type, object_id, metadata=None):
    from apps.audit.models import AuditLog
    AuditLog.log(
        action=action, user=actor, object_type=object_type,
        object_id=object_id, metadata=metadata or {},
    )


@login_required
def admin_desk_course_reviews(request):
    """List course submissions awaiting administrator approval."""
    _guard(request)
    from apps.academy.permissions import is_course_content_admin

    if not is_course_content_admin(request.user):
        raise PermissionDenied
    from apps.academy.models import CourseImport

    queryset = (
        CourseImport.objects.filter(status=CourseImport.Status.REVIEW)
        .select_related("imported_by", "target_course")
        .order_by("-imported_at", "title")
    )
    page = Paginator(queryset, 25).get_page(request.GET.get("page"))
    return render(
        request,
        "admin/desk_course_reviews.html",
        {
            "review_page": page,
            "pending_count": queryset.count(),
            "desk_nav": _nav(request),
        },
    )


@login_required
@require_GET
def admin_desk_course_asset(request, import_id, asset_id):
    """Serve private review figures without navigating through Django Admin."""
    _guard(request)
    from django.contrib import admin
    from apps.academy.models import CourseImport
    from apps.academy.permissions import is_course_content_admin

    if not is_course_content_admin(request.user):
        raise PermissionDenied
    model_admin = admin.site._registry.get(CourseImport)
    if model_admin is None:
        raise PermissionDenied
    return model_admin.asset_view(request, str(import_id), str(asset_id))


@login_required
def admin_desk_course_review(request, import_id):
    """Render a complete course submission preview inside the TradeThesis Admin Desk."""
    _guard(request)
    from apps.academy.models import CourseImport
    from apps.academy.permissions import is_course_content_admin
    from apps.academy.review_context import build_course_import_review_data

    if not is_course_content_admin(request.user):
        raise PermissionDenied
    record = get_object_or_404(
        CourseImport.objects.select_related("imported_by", "target_course"),
        pk=import_id,
        status=CourseImport.Status.REVIEW,
    )
    return render(
        request,
        "academy/course_review.html",
        {
            "title": "Review course submission",
            "import_record": record,
            **build_course_import_review_data(
                record,
                request,
                allow_asset_edits=False,
                asset_url_builder=lambda asset_id: reverse(
                    "staff_admin_desk_course_asset", args=[record.pk, asset_id]
                ),
            ),
            "publish_url": reverse("staff_admin_desk_course_approve", args=[record.pk]),
            "reject_url": reverse("staff_admin_desk_course_reject", args=[record.pk]),
            "changelist_url": reverse("staff_admin_desk_course_reviews"),
            "back_url": reverse("staff_admin_desk_course_reviews"),
            "back_label": "Back to course approvals",
            "desk_url": reverse("staff_admin_desk"),
            "desk_review": True,
            "purge_allowed": _can_permanently_delete_test_import(record),
            "purge_url": reverse("staff_admin_desk_course_import_delete", args=[record.pk]),
            "desk_nav": _nav(request),
        },
    )


@login_required
@require_POST
def admin_desk_course_approve(request, import_id):
    """Approve and publish a reviewed course using the canonical atomic publisher."""
    _guard(request)
    from apps.academy.importing import publish_course_import
    from apps.academy.models import CourseImport
    from apps.academy.permissions import is_course_content_admin

    if not is_course_content_admin(request.user):
        raise PermissionDenied
    record = get_object_or_404(CourseImport, pk=import_id)
    try:
        course = publish_course_import(record, user=request.user)
    except ValidationError as exc:
        for message in exc.messages:
            messages.error(request, message)
        return redirect("staff_admin_desk_course_review", import_id=record.pk)
    messages.success(request, f"{course.title} has been approved and published.")
    return redirect("staff_admin_desk_course_reviews")


@login_required
@require_POST
def admin_desk_course_reject(request, import_id):
    """Return a submission to its author with mandatory reviewer feedback."""
    _guard(request)
    from apps.academy.models import CourseImport
    from apps.academy.permissions import is_course_content_admin

    if not is_course_content_admin(request.user):
        raise PermissionDenied
    feedback = str(request.POST.get("feedback") or "").strip()[:2000]
    if not feedback:
        messages.error(request, "Add feedback explaining what needs to change before returning this course.")
        return redirect("staff_admin_desk_course_review", import_id=import_id)

    with transaction.atomic():
        record = get_object_or_404(
            CourseImport.objects.select_for_update(),
            pk=import_id,
            status=CourseImport.Status.REVIEW,
        )
        payload = dict(record.payload or {})
        payload["review_feedback"] = feedback
        record.payload = payload
        record.status = CourseImport.Status.REJECTED
        record.reviewed_by = request.user
        record.save(update_fields=["payload", "status", "reviewed_by", "updated_at"])
        _audit(
            "academy.course_import.returned_for_changes",
            request.user,
            "course_import",
            record.pk,
            {"course_slug": record.course_slug, "feedback": feedback},
        )
    messages.warning(request, f"{record.title} was returned to the Course Builder with your feedback.")
    return redirect("staff_admin_desk_course_reviews")


def _can_permanently_delete_test_import(record):
    """Only purge unlinked, unpublished imports that cannot represent a live course."""
    from apps.academy.models import Course, CourseImport

    if record.target_course_id or record.status not in {
        CourseImport.Status.DRAFT,
        CourseImport.Status.REVIEW,
        CourseImport.Status.REJECTED,
        CourseImport.Status.SUPERSEDED,
        CourseImport.Status.DELETED,
    }:
        return False
    # Older imports may not have target_course set. A matching Course row still
    # means this import may be history for real learner-facing content.
    return not Course.objects.filter(slug=record.course_slug).exists()


@login_required
@require_GET
def admin_desk_course_import_cleanup(request):
    """List unpublished imports that are safe candidates for permanent test-data cleanup."""
    _guard(request)
    from apps.academy.models import Course, CourseImport
    from apps.academy.permissions import is_course_content_admin

    if not is_course_content_admin(request.user):
        raise PermissionDenied
    candidates = (
        CourseImport.objects.filter(
            status__in=[
                CourseImport.Status.DRAFT,
                CourseImport.Status.REVIEW,
                CourseImport.Status.REJECTED,
                CourseImport.Status.SUPERSEDED,
                CourseImport.Status.DELETED,
            ],
            target_course__isnull=True,
        )
        .exclude(course_slug__in=Course.objects.values("slug"))
        .select_related("imported_by")
        .order_by("-updated_at", "title")
    )
    return render(
        request,
        "admin/desk_course_import_cleanup.html",
        {
            "imports": candidates,
            "candidate_count": candidates.count(),
            "desk_nav": _nav(request),
        },
    )


@login_required
@require_POST
def admin_desk_course_import_delete(request, import_id):
    """Permanently purge a standalone, unpublished test import and its staged files."""
    _guard(request)
    from apps.academy.models import CourseImport
    from apps.academy.permissions import is_course_content_admin

    if not is_course_content_admin(request.user):
        raise PermissionDenied
    if str(request.POST.get("confirmation") or "").strip().upper() != "DELETE":
        messages.error(request, "Type DELETE to confirm permanent removal.")
        return redirect("staff_admin_desk_course_import_cleanup")

    deleted_id = str(import_id)
    with transaction.atomic():
        record = get_object_or_404(
            CourseImport.objects.select_for_update().prefetch_related("assets"),
            pk=import_id,
        )
        if not _can_permanently_delete_test_import(record):
            messages.error(
                request,
                "This import is linked to a course or is not eligible for permanent test-data cleanup. No records were deleted.",
            )
            return redirect("staff_admin_desk_course_import_cleanup")
        title = record.title
        slug = record.course_slug
        status = record.status
        for asset in record.assets.all():
            if asset.file:
                storage = asset.file.storage
                name = asset.file.name
                transaction.on_commit(
                    lambda storage=storage, name=name: storage.delete(name),
                    robust=True,
                )
        record.delete()
        _audit(
            "academy.course_import.permanently_deleted",
            request.user,
            "course_import",
            deleted_id,
            {"course_slug": slug, "title": title, "previous_status": status},
        )
    messages.success(request, f"{title} and its staged import files were permanently deleted.")
    return redirect("staff_admin_desk_course_import_cleanup")


@login_required
@require_GET
def admin_desk_support_tickets(request):
    """Permission-filtered support queue in the TradeThesis Admin Desk."""
    _guard(request)
    from apps.support.models import SupportTicket
    from apps.support.services import reviewable_ticket_queryset

    queryset = reviewable_ticket_queryset(
        request.user,
        SupportTicket.objects.select_related(
            "user", "plan", "affiliate_link", "assigned_to"
        ),
    )
    query = request.GET.get("q", "").strip()[:160]
    status = request.GET.get("status", "").strip()
    category = request.GET.get("category", "").strip()
    priority = request.GET.get("priority", "").strip()
    assignment = request.GET.get("assignment", "").strip()

    if query:
        search_filter = (
            Q(user__username__icontains=query)
            | Q(user__email__icontains=query)
            | Q(message__icontains=query)
            | Q(admin_notes__icontains=query)
        )
        # Permit an exact UUID search without making partial UUID casts unsafe.
        # Keep it in one WHERE clause so later status/category filters remain valid.
        try:
            from uuid import UUID
            ticket_uuid = UUID(query)
        except (TypeError, ValueError, AttributeError):
            ticket_uuid = None
        if ticket_uuid:
            search_filter |= Q(pk=ticket_uuid)
        queryset = queryset.filter(search_filter)

    if status in {value for value, _label in SupportTicket.Status.choices}:
        queryset = queryset.filter(status=status)
    elif status == "active":
        queryset = queryset.filter(status__in=SupportTicket.ACTIVE_STATUSES)
    if category in {value for value, _label in SupportTicket.Category.choices}:
        queryset = queryset.filter(category=category)
    if priority in {value for value, _label in SupportTicket.Priority.choices}:
        queryset = queryset.filter(priority=priority)
    if assignment == "mine":
        queryset = queryset.filter(assigned_to=request.user)
    elif assignment == "unassigned":
        queryset = queryset.filter(assigned_to__isnull=True)

    base_queryset = reviewable_ticket_queryset(request.user, SupportTicket.objects.all())
    now = timezone.now()
    stats = {
        "pending": base_queryset.filter(status=SupportTicket.Status.PENDING).count(),
        "open": base_queryset.filter(status__in=SupportTicket.ACTIVE_STATUSES).count(),
        "overdue": base_queryset.filter(
            status__in=SupportTicket.ACTIVE_STATUSES,
            first_response_at__isnull=True,
            first_response_due_at__lt=now,
        ).count(),
        "resolved": base_queryset.filter(
            status__in=[SupportTicket.Status.APPROVED, SupportTicket.Status.REJECTED]
        ).count(),
    }
    page = Paginator(queryset.order_by("-created_at"), 25).get_page(
        request.GET.get("page")
    )
    return render(
        request,
        "admin/desk_support_tickets.html",
        {
            "ticket_page": page,
            "query": query,
            "status_filter": status,
            "category_filter": category,
            "priority_filter": priority,
            "assignment_filter": assignment,
            "status_choices": SupportTicket.Status.choices,
            "category_choices": SupportTicket.Category.choices,
            "priority_choices": SupportTicket.Priority.choices,
            "stats": stats,
            "desk_nav": _nav(request),
        },
    )


@login_required
@require_GET
def admin_desk_support_ticket(request, ticket_id):
    """Read and manage one support conversation inside the Admin Desk."""
    _guard(request)
    from apps.support.models import SupportTicket
    from apps.support.services import reviewable_ticket_queryset

    ticket = get_object_or_404(
        reviewable_ticket_queryset(
            request.user,
            SupportTicket.objects.select_related(
                "user", "plan", "affiliate_link", "assigned_to", "reviewed_by"
            ).prefetch_related("attachments", "messages__author"),
        ),
        pk=ticket_id,
    )
    conversation = ticket.messages.select_related("author").order_by(
        "created_at", "pk"
    )
    try:
        requested_count = int(request.GET.get("show_messages", "50"))
    except (TypeError, ValueError):
        requested_count = 50
    visible_count = min(conversation.count(), max(20, min(requested_count, 200)))
    total_messages = conversation.count()
    messages_page = list(conversation.order_by("-created_at", "-pk")[:visible_count])
    messages_page.reverse()

    from apps.subscriptions.models import Plan

    plan_options = []
    if ticket.is_access_request:
        plan_options = [
            plan for plan in Plan.objects.filter(is_hidden=True).order_by("name")
            if ticket.can_be_reviewed_by(request.user, plan=plan)
        ]
    staff_options = [
        staff for staff in get_user_model().objects.filter(
            is_staff=True, is_active=True
        ).order_by("username")
        if ticket.can_be_reviewed_by(staff)
    ]
    return render(
        request,
        "admin/desk_support_ticket.html",
        {
            "ticket": ticket,
            "conversation_messages": messages_page,
            "total_message_count": total_messages,
            "has_earlier_messages": total_messages > visible_count,
            "messages_to_load": min(50, total_messages - visible_count),
            "next_message_limit": min(total_messages, visible_count + 50),
            "plan_options": plan_options,
            "staff_options": staff_options,
            "priority_choices": SupportTicket.Priority.choices,
            "can_approve": ticket.is_open,
            "can_reply": ticket.status != SupportTicket.Status.WITHDRAWN,
            "desk_nav": _nav(request),
            "queue_url": reverse("staff_admin_desk_support_tickets"),
        },
    )


@login_required
@require_GET
def admin_desk_customer_360(request, user_id):
    """Read-only, permission-scoped customer profile opened from a support ticket."""
    _guard(request)
    User = get_user_model()
    from apps.support.models import SupportTicket, TicketMessage
    from apps.support.services import reviewable_ticket_queryset

    # Resolve a profile through a ticket the reviewer is explicitly allowed
    # to see before applying the learner-only fallback. Some legacy/support
    # accounts have is_staff=True; excluding them before checking the ticket
    # made valid ticket-to-profile links return a misleading 404.
    visible_tickets = reviewable_ticket_queryset(
        request.user,
        SupportTicket.objects.filter(user_id=user_id).select_related(
            "user", "assigned_to", "plan", "affiliate_link"
        ),
    )
    visible_ticket = visible_tickets.order_by("-created_at").first()
    can_view_all_learners = _allowed(request.user, "accounts.view_user")
    if visible_ticket is not None:
        # Internal staff/admin requesters are allowed only through a ticket
        # visible to this reviewer; their profile is restricted below.
        account = visible_ticket.user
    elif can_view_all_learners:
        account = get_object_or_404(
            User.objects.filter(is_staff=False, is_superuser=False),
            pk=user_id,
        )
        visible_tickets = reviewable_ticket_queryset(
            request.user,
            SupportTicket.objects.filter(user=account).select_related(
                "assigned_to", "plan", "affiliate_link"
            ),
        )
    else:
        raise PermissionDenied

    is_internal_account = bool(account.is_staff or account.is_superuser)
    # Community membership is owned by bot_integration, not the legacy
    # Telegram/Discord login fields on User. Keep internal staff profiles
    # support-only and avoid exposing their personal community identities.
    telegram_community_account = None
    discord_community_account = None
    telegram_community_status = "Not linked"
    discord_community_status = "Not linked"
    if not is_internal_account:
        from apps.bot_integration.models import TelegramAccount, DiscordAccount

        telegram_community_account = TelegramAccount.objects.filter(
            user_id=account.pk
        ).only("id", "is_active").first()
        discord_community_account = DiscordAccount.objects.filter(
            user_id=account.pk
        ).only("id", "is_active").first()

        if telegram_community_account is not None:
            telegram_community_status = (
                "Linked" if telegram_community_account.is_active
                else "Disconnect pending"
            )
        elif account.telegram_verified or account.telegram_id:
            # Telegram login verification is not the same as linking the bot
            # chat used for community access and transactional notifications.
            telegram_community_status = "Login only"

        if discord_community_account is not None:
            discord_community_status = (
                "Linked" if discord_community_account.is_active
                else "Disconnect pending"
            )
        elif account.discord_verified or account.discord_id:
            discord_community_status = "Legacy identity only"
    # Staff accounts may submit support requests, but their internal profile
    # is deliberately limited to identity + reviewer-visible support history.
    can_view_subscriptions = (
        not is_internal_account
        and _allowed(request.user, "subscriptions.view_subscription")
    )
    can_view_payments = (
        not is_internal_account
        and _allowed(request.user, "payments.view_paymentintent")
    )
    can_view_invoices = (
        not is_internal_account
        and _allowed(request.user, "payments.view_invoice")
    )
    can_view_academy_records = (
        not is_internal_account
        and _allowed(request.user, "academy.view_courseentitlement")
        and _allowed(request.user, "academy.view_lessonprogress")
    )
    can_view_security_events = (
        not is_internal_account
        and _allowed(request.user, "accounts.view_securityevent")
    )

    subscriptions = []
    subscription_history = []
    if can_view_subscriptions:
        from apps.subscriptions.models import Subscription, SubscriptionHistory

        subscriptions = list(
            Subscription.objects.filter(user=account)
            .select_related("plan", "product")
            .order_by("-created_at")[:30]
        )
        subscription_history = list(
            SubscriptionHistory.objects.filter(user=account)
            .select_related("subscription", "subscription__plan")
            .order_by("-created_at")[:25]
        )

    payments = []
    if can_view_payments:
        from apps.payments.models import PaymentIntent

        payments = list(
            PaymentIntent.objects.filter(user=account)
            .select_related("plan")
            .prefetch_related("refunds")
            .order_by("-created_at")[:30]
        )
        for payment in payments:
            payment.refund_count = len(payment._prefetched_objects_cache.get("refunds", []))
            if payment.chargeback_confirmed:
                payment.financial_state_label = "Chargeback confirmed"
            elif payment.chargeback:
                payment.financial_state_label = "Dispute open"
            elif payment.refunded_cents:
                payment.financial_state_label = (
                    f"Refunded {payment.currency} {payment.refunded_cents / 100:,.2f}"
                )
            else:
                payment.financial_state_label = "No refund recorded"

    invoices = []
    if can_view_invoices:
        from apps.payments.models import Invoice

        invoices = list(
            Invoice.objects.filter(payment_intent__user=account)
            .select_related("payment_intent")
            .order_by("-issued_at")[:25]
        )

    course_entitlements = []
    course_progress = []
    entitlement_events = []
    if can_view_academy_records:
        from apps.academy.models import (
            Course,
            CourseEntitlement,
            CourseEntitlementEvent,
            LessonProgress,
        )

        now = timezone.now()
        course_entitlements = list(
            CourseEntitlement.objects.filter(user=account)
            .select_related("course", "offer", "granted_by")
            .order_by("-created_at")[:40]
        )
        for entitlement in course_entitlements:
            if entitlement.status == CourseEntitlement.Status.REVOKED:
                entitlement.access_state = "Revoked"
            elif entitlement.starts_at > now:
                entitlement.access_state = "Scheduled"
            elif entitlement.expires_at is not None and entitlement.expires_at <= now:
                entitlement.access_state = "Expired"
            else:
                entitlement.access_state = "Active"

        progress_course_ids = set(
            CourseEntitlement.objects.filter(
                user=account,
                course__status=Course.Status.PUBLISHED,
            ).values_list("course_id", flat=True)
        )
        progress_course_ids.update(
            LessonProgress.objects.filter(
                user=account,
                lesson__is_published=True,
                lesson__module__is_published=True,
                lesson__module__course__status=Course.Status.PUBLISHED,
            )
            .values_list("lesson__module__course_id", flat=True)
            .distinct()
        )
        course_progress = list(
            Course.objects.filter(
                pk__in=progress_course_ids,
                status=Course.Status.PUBLISHED,
            )
            .annotate(
                total_lessons=Count(
                    "modules__lessons",
                    filter=Q(
                        modules__is_published=True,
                        modules__lessons__is_published=True,
                    ),
                    distinct=True,
                ),
                completed_lessons=Count(
                    "modules__lessons",
                    filter=Q(
                        modules__is_published=True,
                        modules__lessons__is_published=True,
                        modules__lessons__learner_progress__user=account,
                        modules__lessons__learner_progress__status=LessonProgress.Status.COMPLETED,
                    ),
                    distinct=True,
                ),
                time_spent_seconds=Sum(
                    "modules__lessons__learner_progress__time_spent_seconds",
                    filter=Q(
                        modules__is_published=True,
                        modules__lessons__is_published=True,
                        modules__lessons__learner_progress__user=account,
                    ),
                ),
                last_activity=Max(
                    "modules__lessons__learner_progress__last_seen_at",
                    filter=Q(
                        modules__is_published=True,
                        modules__lessons__is_published=True,
                        modules__lessons__learner_progress__user=account,
                    ),
                ),
            )
            .order_by("-last_activity", "title")
        )
        for item in course_progress:
            item.progress_percent = (
                round(item.completed_lessons * 100 / item.total_lessons)
                if item.total_lessons
                else 0
            )
            item.time_spent_minutes = round((item.time_spent_seconds or 0) / 60)
        entitlement_events = list(
            CourseEntitlementEvent.objects.filter(entitlement__user=account)
            .select_related("entitlement", "entitlement__course")
            .order_by("-created_at")[:25]
        )

    open_ticket_count = visible_tickets.filter(
        status__in=SupportTicket.ACTIVE_STATUSES
    ).count()
    ticket_rows = list(visible_tickets.order_by("-created_at")[:40])
    ticket_ids = [ticket.pk for ticket in ticket_rows]
    public_messages = list(
        TicketMessage.objects.filter(
            ticket_id__in=ticket_ids,
            is_internal=False,
        )
        .select_related("ticket", "author")
        .order_by("-created_at")[:25]
    )

    # A single, chronological, read-only operational timeline. It contains
    # only records the current reviewer is allowed to see; internal support
    # notes, raw security identifiers and payment-provider IDs are excluded.
    activity = []

    def add_activity(occurred_at, kind, title, description="", url=""):
        if occurred_at:
            activity.append(
                {
                    "occurred_at": occurred_at,
                    "kind": kind,
                    "title": title,
                    "description": description,
                    "url": url,
                }
            )

    for ticket in ticket_rows:
        add_activity(
            ticket.created_at,
            "Support",
            f"Ticket #{ticket.short_id} opened",
            f"{ticket.get_category_display()} · {ticket.get_status_display()}",
            reverse("staff_admin_desk_support_ticket", args=[ticket.pk]),
        )
    for message in public_messages:
        author = "Member" if message.author_id == account.pk else "Support reply"
        add_activity(
            message.created_at,
            "Conversation",
            author,
            message.body[:180],
            reverse("staff_admin_desk_support_ticket", args=[message.ticket_id]),
        )
    for item in subscription_history:
        add_activity(
            item.created_at,
            "Subscription",
            item.get_event_type_display(),
            item.subscription.plan.name,
            reverse("staff_admin_desk_subscriptions"),
        )
    for payment in payments:
        add_activity(
            payment.created_at,
            "Payment",
            f"Payment {payment.get_status_display().lower()}",
            f"{payment.plan.name} · {payment.currency} {payment.amount_dollars:,.2f}",
            "",
        )
        for refund in payment.refunds.all():
            add_activity(
                refund.refunded_at,
                "Refund",
                "Refund processed",
                f"{refund.currency} {refund.amount_cents / 100:,.2f} · {payment.plan.name}",
                "",
            )
        if payment.chargeback_at:
            add_activity(
                payment.chargeback_at,
                "Dispute",
                "Payment dispute opened",
                payment.plan.name,
                "",
            )
    for event in entitlement_events:
        add_activity(
            event.created_at,
            "Course access",
            event.get_event_type_display(),
            event.entitlement.course.title,
            "",
        )
    if can_view_security_events:
        from apps.accounts.models import SecurityEvent

        security_events = SecurityEvent.objects.filter(user=account).order_by(
            "-occurred_at"
        )[:20]
        for event in security_events:
            add_activity(
                event.occurred_at,
                "Security",
                event.get_event_type_display(),
                "Security event recorded",
                "",
            )

    activity.sort(key=lambda item: item["occurred_at"], reverse=True)
    active_subscription_count = sum(
        subscription.is_active
        and subscription.status == subscription.Status.ACTIVE
        for subscription in subscriptions
    )
    successful_payment_count = sum(
        payment.status == payment.Status.SUCCESS for payment in payments
    )
    active_course_count = sum(
        entitlement.access_state == "Active" for entitlement in course_entitlements
    )

    return render(
        request,
        "admin/desk_customer_360.html",
        {
            "account": account,
            "is_internal_account": is_internal_account,
            "telegram_community_status": telegram_community_status,
            "discord_community_status": discord_community_status,
            "subscriptions": subscriptions,
            "subscription_history": subscription_history,
            "payments": payments,
            "invoices": invoices,
            "course_entitlements": course_entitlements,
            "course_progress": course_progress,
            "support_tickets": ticket_rows,
            "activity": activity[:40],
            "stats": {
                "open_tickets": open_ticket_count,
                "active_subscriptions": active_subscription_count,
                "successful_payments": successful_payment_count,
                "active_courses": active_course_count,
            },
            "can_view_subscriptions": can_view_subscriptions,
            "can_view_payments": can_view_payments,
            "can_view_invoices": can_view_invoices,
            "can_view_academy_records": can_view_academy_records,
            "can_view_security_events": can_view_security_events,
            "desk_nav": _nav(request),
            "support_queue_url": reverse("staff_admin_desk_support_tickets"),
            "accounts_url": reverse("staff_admin_desk_accounts"),
        },
    )


@login_required
@require_GET
def admin_desk_operations_timeline(request):
    """Cross-customer support signals and application-operational timeline."""
    _guard(request)
    from apps.support.models import SupportTicket
    from apps.support.services import reviewable_ticket_queryset
    from apps.support.operational_signals import build_support_issue_clusters

    now = timezone.now()
    window = request.GET.get("window", "7d").strip()
    if window not in {"24h", "7d"}:
        window = "7d"
    since = now - timedelta(hours=24 if window == "24h" else 24 * 7)

    visible_tickets = reviewable_ticket_queryset(
        request.user,
        SupportTicket.objects.filter(created_at__gte=since),
    )
    # Bound clustering work and all event feeds; summaries are limited to
    # the current reviewer-visible queue and the selected time window.
    cluster_tickets = list(
        visible_tickets.select_related("user", "plan", "affiliate_link")
        .order_by("-created_at")[:250]
    )
    issue_clusters = build_support_issue_clusters(cluster_tickets)
    category_rows = list(
        visible_tickets.values("category")
        .annotate(
            ticket_count=Count("id"),
            customer_count=Count("user_id", distinct=True),
            open_count=Count("id", filter=Q(status__in=SupportTicket.ACTIVE_STATUSES)),
            urgent_count=Count("id", filter=Q(priority=SupportTicket.Priority.URGENT)),
        )
        .order_by("-ticket_count", "category")
    )
    for item in category_rows:
        item["label"] = dict(SupportTicket.Category.choices).get(
            item["category"], item["category"]
        )
    recent_tickets = cluster_tickets[:30]

    can_view_jobs = _allowed(request.user, "jobs.view_job")
    can_view_provisioning = _allowed(request.user, "jobs.view_provisioningoperation")
    can_view_periodic_jobs = _allowed(request.user, "jobs.view_periodicjob")
    can_view_domain_events = _allowed(request.user, "events.view_event")
    can_view_audit = _allowed(request.user, "audit.view_auditlog")
    can_view_security = _allowed(request.user, "accounts.view_securityevent")

    job_incidents = []
    if can_view_jobs:
        from apps.jobs.models import Job

        job_incidents = list(
            Job.objects.filter(
                Q(status=Job.STATUS_FAILED, updated_at__gte=since)
                | Q(status__in=Job.OPEN_STATUSES, attempts__gte=3)
                | Q(
                    status=Job.STATUS_RUNNING,
                    locked_at__lt=now - timedelta(minutes=15),
                )
            )
            .only(
                "kind", "status", "attempts", "max_attempts", "created_at",
                "updated_at", "next_attempt_at", "locked_at",
            )
            .order_by("-updated_at")[:40]
        )

    provisioning_incidents = []
    if can_view_provisioning:
        from apps.jobs.models import ProvisioningOperation

        provisioning_incidents = list(
            ProvisioningOperation.objects.filter(
                state__in=[
                    ProvisioningOperation.ST_FAILED,
                    ProvisioningOperation.ST_UNKNOWN,
                ],
                updated_at__gte=since,
            )
            .only("operation", "state", "attempts", "created_at", "updated_at")
            .order_by("-updated_at")[:30]
        )

    periodic_errors = []
    if can_view_periodic_jobs:
        from apps.jobs.models import PeriodicJob

        periodic_errors = list(
            PeriodicJob.objects.filter(
                last_status=PeriodicJob.Status.ERROR,
                last_run_at__gte=since,
            )
            .only("name", "enabled", "last_run_at", "last_status")
            .order_by("name")[:30]
        )

    domain_events = []
    if can_view_domain_events:
        from apps.events.models import Event

        domain_events = list(
            Event.objects.filter(occurred_at__gte=since)
            .order_by("-occurred_at")[:60]
        )

    audit_events = []
    if can_view_audit:
        from apps.audit.models import AuditLog

        audit_events = list(
            AuditLog.objects.filter(created_at__gte=since)
            .only("action", "object_type", "created_at")
            .order_by("-created_at")[:40]
        )

    security_summary = []
    if can_view_security:
        from apps.accounts.models import SecurityEvent

        security_summary = list(
            SecurityEvent.objects.filter(occurred_at__gte=since)
            .values("event_type")
            .annotate(total=Count("id"))
            .order_by("-total", "event_type")
        )
        for item in security_summary:
            item["label"] = dict(SecurityEvent.EventType.choices).get(
                item["event_type"], item["event_type"]
            )

    activity = []

    def add_activity(occurred_at, kind, title, description="", level="info", url=""):
        if occurred_at:
            activity.append({
                "occurred_at": occurred_at,
                "kind": kind,
                "title": title,
                "description": description,
                "level": level,
                "url": url,
            })

    for ticket in recent_tickets:
        add_activity(
            ticket.created_at,
            "Support",
            f"Ticket #{ticket.short_id} opened",
            f"{ticket.get_category_display()} · {ticket.get_priority_display()} priority · {ticket.get_status_display()}",
            "warning" if ticket.priority in {
                SupportTicket.Priority.HIGH, SupportTicket.Priority.URGENT
            } else "info",
            reverse("staff_admin_desk_support_ticket", args=[ticket.pk]),
        )
    for job in job_incidents:
        failed = job.status == Job.STATUS_FAILED
        job_state = "failed" if failed else "stalled / retrying"
        add_activity(
            job.updated_at,
            "Worker",
            f"{job.kind} {job_state}",
            f"Status {job.status} · {job.attempts}/{job.max_attempts} attempts",
            "critical" if failed else "warning",
            reverse("staff_admin_desk_operations_job", args=[job.pk]),
        )
    for operation in provisioning_incidents:
        add_activity(
            operation.updated_at,
            "Provisioning",
            f"External {operation.operation} {operation.state.replace('_', ' ')}",
            f"{operation.attempts} attempts · external state requires review",
            "critical" if operation.state == operation.ST_FAILED else "warning",
            reverse("staff_admin_desk_operations_provisioning", args=[operation.pk]),
        )
    for periodic in periodic_errors:
        add_activity(
            periodic.last_run_at or since,
            "Scheduler",
            f"Scheduled task {periodic.name} reported an error",
            "Enabled" if periodic.enabled else "Disabled",
            "warning",
        )
    for event in domain_events:
        add_activity(
            event.occurred_at,
            "Domain event",
            event.get_event_type_display(),
            "Business event recorded",
            "critical" if event.event_type in {
                "payment.failed", "payment.chargeback"
            } else "info",
        )
    for event in audit_events:
        add_activity(
            event.created_at,
            "Audit",
            event.action.replace(".", " · "),
            f"Record type: {event.object_type or 'system'}",
            "info",
        )

    activity.sort(key=lambda item: item["occurred_at"], reverse=True)
    failed_job_count = sum(job.status == "failed" for job in job_incidents)
    stalled_job_count = sum(
        job.status in {"pending", "running"} for job in job_incidents
    )
    visible_open_count = visible_tickets.filter(
        status__in=SupportTicket.ACTIVE_STATUSES
    ).count()

    return render(
        request,
        "admin/desk_operations_timeline.html",
        {
            "window": window,
            "window_label": "Last 24 hours" if window == "24h" else "Last 7 days",
            "since": since,
            "issue_clusters": issue_clusters,
            "category_rows": category_rows,
            "recent_tickets": recent_tickets,
            "activity": activity[:100],
            "job_incidents": job_incidents,
            "provisioning_incidents": provisioning_incidents,
            "periodic_errors": periodic_errors,
            "security_summary": security_summary,
            "stats": {
                "open_tickets": visible_open_count,
                "potential_patterns": len(issue_clusters),
                "failed_jobs": failed_job_count,
                "stalled_jobs": stalled_job_count,
                "provisioning_issues": len(provisioning_incidents),
                "scheduler_errors": len(periodic_errors),
            },
            "can_view_jobs": can_view_jobs,
            "can_view_provisioning": can_view_provisioning,
            "can_view_periodic_jobs": can_view_periodic_jobs,
            "can_view_domain_events": can_view_domain_events,
            "can_view_audit": can_view_audit,
            "can_view_security": can_view_security,
            "support_queue_url": reverse("staff_admin_desk_support_tickets"),
            "desk_url": reverse("staff_admin_desk"),
            "desk_nav": _nav(request),
        },
    )


@login_required
@require_GET
def admin_desk_operations_job(request, job_id):
    """Read-only, safe worker-job detail inside the Admin Desk."""
    _guard(request, "jobs.view_job")
    from apps.jobs.models import Job

    job = get_object_or_404(
        Job.objects.only(
            "id", "kind", "status", "attempts", "max_attempts",
            "created_at", "updated_at", "next_attempt_at", "locked_at",
        ),
        pk=job_id,
    )
    return render(
        request,
        "admin/desk_operations_job.html",
        {
            "job": job,
            "desk_nav": _nav(request),
            "timeline_url": reverse("staff_admin_desk_operations_timeline"),
        },
    )


@login_required
@require_GET
def admin_desk_operations_provisioning(request, operation_id):
    """Read-only provisioning-operation detail without external IDs or payloads."""
    _guard(request, "jobs.view_provisioningoperation")
    from apps.jobs.models import ProvisioningOperation

    operation = get_object_or_404(
        ProvisioningOperation.objects.only(
            "id", "operation", "state", "attempts", "created_at", "updated_at",
        ),
        pk=operation_id,
    )
    return render(
        request,
        "admin/desk_operations_provisioning.html",
        {
            "operation": operation,
            "desk_nav": _nav(request),
            "timeline_url": reverse("staff_admin_desk_operations_timeline"),
        },
    )


@login_required
@require_POST
def admin_desk_support_ticket_action(request, ticket_id):
    """Apply the existing support-ticket workflow from a dashboard POST."""
    _guard(request)
    from apps.support.models import SupportTicket
    from apps.support.services import (
        add_ticket_message,
        approve_ticket,
        reject_ticket,
        reopen_ticket,
        reviewable_ticket_queryset,
        set_ticket_status,
    )
    from apps.subscriptions.models import Plan

    ticket = get_object_or_404(
        reviewable_ticket_queryset(
            request.user,
            SupportTicket.objects.select_related("user", "plan", "affiliate_link"),
        ),
        pk=ticket_id,
    )
    action = (request.POST.get("action") or "").strip()

    if action in {"public_reply", "internal_note"}:
        try:
            add_ticket_message(
                ticket,
                request.user,
                request.POST.get("body", ""),
                is_internal=(action == "internal_note"),
            )
        except (ValueError, PermissionError) as exc:
            messages.error(request, str(exc))
        else:
            _audit(
                "support.ticket.internal_note" if action == "internal_note"
                else "support.ticket.replied",
                request.user,
                "support_ticket",
                ticket.pk,
                {"message_visibility": action},
            )
            messages.success(
                request,
                "Internal note saved." if action == "internal_note"
                else "Reply sent to the member.",
            )
        return redirect("staff_admin_desk_support_ticket", ticket_id=ticket.pk)

    if action in {"start_review", "awaiting_member"}:
        target_status = (
            SupportTicket.Status.IN_PROGRESS
            if action == "start_review"
            else SupportTicket.Status.AWAITING_MEMBER
        )
        try:
            set_ticket_status(ticket, request.user, target_status)
        except (ValueError, PermissionError) as exc:
            messages.error(request, str(exc))
        else:
            _audit(
                "support.ticket.status_changed",
                request.user,
                "support_ticket",
                ticket.pk,
                {"status": target_status},
            )
            messages.success(request, f"Ticket moved to {ticket.get_status_display().lower()}.")
        return redirect("staff_admin_desk_support_ticket", ticket_id=ticket.pk)

    if action == "reopen":
        try:
            reopen_ticket(ticket, request.user)
        except (ValueError, PermissionError) as exc:
            messages.error(request, str(exc))
        else:
            _audit("support.ticket.reopened", request.user, "support_ticket", ticket.pk)
            messages.success(request, "Ticket reopened and returned to active work.")
        return redirect("staff_admin_desk_support_ticket", ticket_id=ticket.pk)

    if action == "approve":
        raw_plan_id = (request.POST.get("plan") or "").strip()
        if raw_plan_id:
            plan = Plan.objects.filter(pk=raw_plan_id, is_hidden=True).first()
            if plan is None:
                messages.error(request, "Choose a valid hidden access plan.")
                return redirect("staff_admin_desk_support_ticket", ticket_id=ticket.pk)
        else:
            plan = ticket.plan or (
                ticket.affiliate_link.plan
                if ticket.affiliate_link_id and ticket.affiliate_link.plan_id
                else None
            )
        if ticket.is_access_request and plan is None:
            messages.error(request, "Assign a hidden plan before approving this access request.")
            return redirect("staff_admin_desk_support_ticket", ticket_id=ticket.pk)
        notes = request.POST.get("admin_notes", ticket.admin_notes)
        try:
            approve_ticket(ticket, plan, request.user, notes=notes)
        except (ValueError, PermissionError) as exc:
            messages.error(request, str(exc))
        except Exception:
            logger.exception("Admin Desk support approval failed ticket=%s", ticket.pk)
            messages.error(
                request,
                "Approval failed and no changes were committed. Check the logs and retry.",
            )
        else:
            _audit(
                "support.ticket.approved",
                request.user,
                "support_ticket",
                ticket.pk,
                {"plan_id": str(plan.pk) if plan else None},
            )
            messages.success(
                request,
                f"Approved — {ticket.user} granted {plan.name}."
                if ticket.is_access_request and plan
                else "Ticket marked resolved; the member was notified.",
            )
        return redirect("staff_admin_desk_support_ticket", ticket_id=ticket.pk)

    if action == "reject":
        notes = request.POST.get("admin_notes", ticket.admin_notes).strip()
        plan = ticket.review_plan if ticket.is_access_request else None
        raw_plan_id = (request.POST.get("plan") or "").strip()
        if ticket.is_access_request and raw_plan_id:
            plan = Plan.objects.filter(pk=raw_plan_id, is_hidden=True).first()
            if plan is None:
                messages.error(request, "Choose a valid hidden access plan.")
                return redirect("staff_admin_desk_support_ticket", ticket_id=ticket.pk)
        try:
            reject_ticket(ticket, request.user, notes, plan=plan)
        except (ValueError, PermissionError) as exc:
            messages.error(request, str(exc))
        else:
            _audit("support.ticket.rejected", request.user, "support_ticket", ticket.pk)
            messages.success(request, "Ticket rejected and the member was notified.")
        return redirect("staff_admin_desk_support_ticket", ticket_id=ticket.pk)

    if action == "update_details":
        raw_assignee = (request.POST.get("assigned_to") or "").strip()
        assignee = None
        if raw_assignee:
            assignee = get_user_model().objects.filter(
                pk=raw_assignee, is_staff=True, is_active=True
            ).first()
            if assignee is None or not ticket.can_be_reviewed_by(assignee):
                messages.error(request, "Choose an active reviewer who is allowed to access this ticket.")
                return redirect("staff_admin_desk_support_ticket", ticket_id=ticket.pk)
        priority = (request.POST.get("priority") or "").strip()
        if priority not in {value for value, _label in SupportTicket.Priority.choices}:
            messages.error(request, "Choose a valid ticket priority.")
            return redirect("staff_admin_desk_support_ticket", ticket_id=ticket.pk)
        ticket.assigned_to = assignee
        ticket.priority = priority
        ticket.save(update_fields=["assigned_to", "priority", "first_response_due_at", "updated_at"])
        _audit(
            "support.ticket.details_updated",
            request.user,
            "support_ticket",
            ticket.pk,
            {
                "assigned_to": str(assignee.pk) if assignee else None,
                "priority": priority,
            },
        )
        messages.success(request, "Ticket assignment and priority updated.")
        return redirect("staff_admin_desk_support_ticket", ticket_id=ticket.pk)

    messages.error(request, "Choose a valid support-ticket action.")
    return redirect("staff_admin_desk_support_ticket", ticket_id=ticket.pk)


def _nav(request):
    from apps.payments.models import BillingSettings

    settings_exist = BillingSettings.objects.filter(pk=1).exists()
    business_allowed = (
        _allowed(request.user, "payments.change_billingsettings")
        if settings_exist
        else _allowed(request.user, "payments.add_billingsettings")
    )
    return {
        "accounts": _allowed(request.user, "accounts.view_user"),
        "subscriptions": _allowed(request.user, "subscriptions.view_subscription"),
        "finance": (
            _allowed(request.user, "payments.view_paymentintent")
            or _allowed(request.user, "payments.view_invoice")
        ),
        "business": business_allowed,
    }


@login_required
def admin_desk_accounts(request):
    """Search learner accounts without exposing staff/admin accounts."""
    _guard(request, "accounts.view_user")
    User = get_user_model()
    query = request.GET.get("q", "").strip()[:120]
    state = request.GET.get("state", "").strip().lower()
    qs = User.objects.filter(is_staff=False, is_superuser=False)
    if query:
        qs = qs.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
            | Q(first_name__icontains=query) | Q(last_name__icontains=query)
            | Q(nickname__icontains=query)
        )
    if state == "active":
        qs = qs.filter(is_active=True, is_banned=False)
    elif state == "inactive":
        qs = qs.filter(is_active=False)
    elif state == "banned":
        qs = qs.filter(is_banned=True)
    can_view_subscriptions = _allowed(request.user, "subscriptions.view_subscription")
    if can_view_subscriptions:
        qs = qs.annotate(active_subscription_count=Count(
            "subscriptions",
            filter=Q(subscriptions__status="active", subscriptions__is_active=True),
            distinct=True,
        ))
    qs = qs.order_by("-date_joined")
    return render(request, "admin/desk_accounts.html", {
        "accounts_page": Paginator(qs, 25).get_page(request.GET.get("page")),
        "query": query, "state": state,
        "can_change_accounts": _allowed(request.user, "accounts.change_user"),
        "can_view_account_subscriptions": can_view_subscriptions,
        "desk_nav": _nav(request),
    })


@login_required
def admin_desk_account_detail(request, user_id):
    """Show a learner's account, course progress, access and permitted finance records."""
    _guard(request, "accounts.view_user")
    User = get_user_model()
    account = get_object_or_404(User, pk=user_id, is_staff=False, is_superuser=False)

    from apps.academy.models import Course, CourseEntitlement, LessonProgress
    from apps.payments.models import Invoice, PaymentIntent
    from apps.subscriptions.models import Subscription, SubscriptionHistory

    can_view_subscriptions = _allowed(request.user, "subscriptions.view_subscription")
    can_view_payments = _allowed(request.user, "payments.view_paymentintent")
    can_view_invoices = _allowed(request.user, "payments.view_invoice")
    can_view_academy_records = (
        _allowed(request.user, "academy.view_courseentitlement")
        and _allowed(request.user, "academy.view_lessonprogress")
    )

    subscriptions = (
        Subscription.objects.filter(user=account)
        .select_related("plan")
        .order_by("-created_at")[:30]
        if can_view_subscriptions else []
    )
    history = (
        SubscriptionHistory.objects.filter(user=account)
        .select_related("subscription", "subscription__plan")
        .order_by("-created_at")[:20]
        if can_view_subscriptions else []
    )
    payments = (
        PaymentIntent.objects.filter(user=account)
        .select_related("plan")
        .order_by("-created_at")[:20]
        if can_view_payments else []
    )
    invoices = (
        Invoice.objects.filter(payment_intent__user=account)
        .select_related("payment_intent")
        .order_by("-issued_at")[:30]
        if can_view_invoices else []
    )

    course_entitlements = []
    course_progress = []
    if can_view_academy_records:
        now = timezone.now()
        course_entitlements = list(
            CourseEntitlement.objects.filter(user=account)
            .select_related("course", "offer", "payment_intent", "granted_by")
            .order_by("-created_at")[:30]
        )
        for entitlement in course_entitlements:
            if entitlement.status == CourseEntitlement.Status.REVOKED:
                entitlement.access_state = "Revoked"
            elif entitlement.starts_at > now:
                entitlement.access_state = "Scheduled"
            elif entitlement.expires_at is not None and entitlement.expires_at <= now:
                entitlement.access_state = "Expired"
            else:
                entitlement.access_state = "Active"

        # Include entitled courses even before the learner opens their first
        # lesson, plus any public preview courses where we have tracked activity.
        progress_course_ids = set(
            CourseEntitlement.objects.filter(
                user=account, course__status=Course.Status.PUBLISHED,
            ).values_list("course_id", flat=True)
        )
        progress_course_ids.update(
            LessonProgress.objects.filter(
                user=account,
                lesson__is_published=True,
                lesson__module__is_published=True,
                lesson__module__course__status=Course.Status.PUBLISHED,
            )
            .values_list("lesson__module__course_id", flat=True)
            .distinct()
        )
        course_progress = list(
            Course.objects.filter(
                pk__in=progress_course_ids,
                status=Course.Status.PUBLISHED,
            )
            .annotate(
                total_lessons=Count(
                    "modules__lessons",
                    filter=Q(
                        modules__is_published=True,
                        modules__lessons__is_published=True,
                    ),
                    distinct=True,
                ),
                completed_lessons=Count(
                    "modules__lessons",
                    filter=Q(
                        modules__is_published=True,
                        modules__lessons__is_published=True,
                        modules__lessons__learner_progress__user=account,
                        modules__lessons__learner_progress__status=LessonProgress.Status.COMPLETED,
                    ),
                    distinct=True,
                ),
                time_spent_seconds=Sum(
                    "modules__lessons__learner_progress__time_spent_seconds",
                    filter=Q(
                        modules__is_published=True,
                        modules__lessons__is_published=True,
                        modules__lessons__learner_progress__user=account,
                    ),
                ),
                last_activity=Max(
                    "modules__lessons__learner_progress__last_seen_at",
                    filter=Q(
                        modules__is_published=True,
                        modules__lessons__is_published=True,
                        modules__lessons__learner_progress__user=account,
                    ),
                ),
            )
            .order_by("-last_activity", "title")
        )
        for item in course_progress:
            item.progress_percent = (
                round(item.completed_lessons * 100 / item.total_lessons)
                if item.total_lessons else 0
            )
            item.time_spent_minutes = round((item.time_spent_seconds or 0) / 60)

    return render(request, "admin/desk_accounts.html", {
        "account": account,
        "subscriptions": subscriptions,
        "payments": payments,
        "history": history,
        "invoices": invoices,
        "course_entitlements": course_entitlements,
        "course_progress": course_progress,
        "can_change_accounts": _allowed(request.user, "accounts.change_user"),
        "can_view_account_subscriptions": can_view_subscriptions,
        "can_view_account_payments": can_view_payments,
        "can_view_account_invoices": can_view_invoices,
        "can_view_academy_records": can_view_academy_records,
        "desk_nav": _nav(request),
    })

@login_required
@require_POST
def admin_desk_account_action(request, user_id):
    _guard(request, "accounts.change_user")
    User = get_user_model()
    account = get_object_or_404(User, pk=user_id, is_staff=False, is_superuser=False)
    action = request.POST.get("action", "").strip()
    reason = request.POST.get("reason", "").strip()

    if action == "password_reset":
        if not account.email:
            messages.error(request, "This learner has no email address on the account.")
        else:
            form = PasswordResetForm({"email": account.email})
            if form.is_valid():
                form.save(request=request, use_https=request.is_secure())
                _audit("admin.account.password_reset_sent", request.user, "user", account.pk,
                       {"target_user_id": str(account.pk)})
                messages.success(request, "Password-reset instructions were submitted to the email service if the address is eligible.")
            else:
                messages.error(request, "Password-reset instructions could not be sent. Check the account email and transactional email configuration.")
        return redirect("staff_admin_desk_account_detail", user_id=account.pk)

    if action not in {"ban", "unban", "activate", "deactivate"}:
        messages.error(request, "Choose a valid account action.")
        return redirect("staff_admin_desk_account_detail", user_id=account.pk)
    if action in {"ban", "deactivate"} and len(reason) < 5:
        messages.error(request, "Add a short reason of at least five characters.")
        return redirect("staff_admin_desk_account_detail", user_id=account.pk)

    before = {"is_active": account.is_active, "is_banned": account.is_banned}
    with transaction.atomic():
        if action == "ban":
            if account.is_banned:
                messages.info(request, "This account is already banned.")
                return redirect("staff_admin_desk_account_detail", user_id=account.pk)
            account.ban(reason=reason)
        elif action == "unban":
            if not account.is_banned:
                messages.info(request, "This account is not banned.")
                return redirect("staff_admin_desk_account_detail", user_id=account.pk)
            account.unban()
        elif action == "deactivate":
            if not account.is_active:
                messages.info(request, "This account is already inactive.")
                return redirect("staff_admin_desk_account_detail", user_id=account.pk)
            account.is_active = False
            account.save(update_fields=["is_active"])
        else:
            if account.is_active:
                messages.info(request, "This account is already active.")
                return redirect("staff_admin_desk_account_detail", user_id=account.pk)
            account.is_active = True
            account.save(update_fields=["is_active"])

        from apps.jobs.enqueue import enqueue_reconcile
        enqueue_reconcile(account.pk, reason=f"admin_account_{action}")
        _audit(f"admin.account.{action}", request.user, "user", account.pk, {
            "target_user_id": str(account.pk), "reason": reason, "before": before,
            "after": {"is_active": account.is_active, "is_banned": account.is_banned},
        })
    messages.success(request, "Learner account updated.")
    return redirect("staff_admin_desk_account_detail", user_id=account.pk)


def _grant_form_class(user_model, plan_model):
    class GrantAccessForm(forms.Form):
        user = forms.ModelChoiceField(
            label="Learner",
            queryset=user_model.objects.filter(is_active=True, is_staff=False, is_superuser=False, is_banned=False).order_by("username"),
        )
        plan = forms.ModelChoiceField(
            label="Complimentary access plan",
            queryset=plan_model.objects.filter(is_active=True, is_hidden=True, is_trial=False).order_by("name"),
            help_text="Only active hidden plans appear here.",
        )
        duration_days = forms.IntegerField(min_value=1, max_value=365, initial=30, label="Access duration (days)")
        reason = forms.CharField(min_length=5, max_length=500, widget=forms.Textarea(attrs={"rows": 3}))
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields.values():
                field.widget.attrs.setdefault(
                    "class", "form-select" if isinstance(field.widget, forms.Select) else "form-control"
                )
    return GrantAccessForm


@login_required
def admin_desk_subscriptions(request):
    """Search access records and provide auditable grants, extensions and cancellations."""
    _guard(request, "subscriptions.view_subscription")
    from apps.subscriptions.models import Plan, Subscription
    from apps.subscriptions.services import grant_subscription_by_admin

    User = get_user_model()
    can_change = _allowed(request.user, "subscriptions.change_subscription")
    can_grant = _allowed(request.user, "subscriptions.add_subscription")
    GrantForm = _grant_form_class(User, Plan)
    grant_post = request.method == "POST" and request.POST.get("action") == "grant"
    grant_form = GrantForm(request.POST if grant_post else None) if can_grant else None
    if grant_post:
        _guard(request, "subscriptions.add_subscription")
        if grant_form.is_valid():
            learner = grant_form.cleaned_data["user"]
            plan = grant_form.cleaned_data["plan"]
            days = grant_form.cleaned_data["duration_days"]
            reason = grant_form.cleaned_data["reason"].strip()
            active = Subscription.objects.filter(user=learner, status=Subscription.Status.ACTIVE, is_active=True)
            active = active.filter(product__isnull=True) if plan.product_id is None else active.filter(product_id=plan.product_id)
            if active.exists():
                grant_form.add_error("plan", "This learner already has active access to this product. Review or end that access before granting a replacement.")
            else:
                sub = grant_subscription_by_admin(
                    user=learner, plan=plan, granted_by=request.user,
                    duration_days=days, reason=reason, request=request,
                )
                _audit("admin.subscription.granted", request.user, "subscription", sub.pk, {
                    "learner_id": str(learner.pk), "plan_id": str(plan.pk),
                    "duration_days": days, "reason": reason,
                })
                messages.success(request, f"Granted {days} days of {plan.name} access to {learner.username}.")
                return redirect(f"{reverse('staff_admin_desk_subscriptions')}?status=active")

    query = request.GET.get("q", "").strip()[:120]
    state = request.GET.get("status", "").strip().lower()
    now = timezone.now()
    soon = now + timedelta(days=7)
    qs = Subscription.objects.select_related("user", "plan")
    if query:
        qs = qs.filter(Q(user__username__icontains=query) | Q(user__email__icontains=query) | Q(plan__name__icontains=query))
    if state in {x[0] for x in Subscription.Status.choices}:
        qs = qs.filter(status=state)
    if request.GET.get("expiring") == "1":
        qs = qs.filter(status="active", is_active=True, expires_at__gt=now, expires_at__lte=soon)
    if request.GET.get("recent") == "1":
        qs = qs.filter(status="expired", expires_at__gte=now - timedelta(days=7), expires_at__lte=now)
    stats = {
        "active": Subscription.objects.filter(status="active", is_active=True).count(),
        "expiring": Subscription.objects.filter(status="active", is_active=True, expires_at__gt=now, expires_at__lte=soon).count(),
        "expired": Subscription.objects.filter(status="expired").count(),
        "canceled": Subscription.objects.filter(status="canceled").count(),
    }
    return render(request, "admin/desk_subscriptions.html", {
        "subscriptions_page": Paginator(qs.order_by("-created_at"), 30).get_page(request.GET.get("page")),
        "query": query, "state": state, "stats": stats,
        "can_change_subscriptions": can_change, "can_grant_subscriptions": can_grant,
        "grant_form": grant_form, "desk_nav": _nav(request),
    })


@login_required
@require_POST
def admin_desk_subscription_action(request, subscription_id):
    _guard(request, "subscriptions.change_subscription")
    from apps.subscriptions.models import Subscription
    from apps.subscriptions.services import cancel_subscription, extend_subscription

    sub = get_object_or_404(Subscription.objects.select_related("user", "plan"), pk=subscription_id)
    action = request.POST.get("action", "").strip()
    reason = request.POST.get("reason", "").strip()
    if len(reason) < 5:
        messages.error(request, "Add a short reason of at least five characters.")
        return redirect("staff_admin_desk_subscriptions")
    if action == "extend":
        try:
            days = forms.IntegerField(min_value=1, max_value=365).clean(request.POST.get("days", ""))
        except ValidationError:
            messages.error(request, "Enter an extension between 1 and 365 days.")
            return redirect("staff_admin_desk_subscriptions")
        changed = extend_subscription(sub, days=days, actor=f"{request.user.username}: {reason}")
    elif action == "cancel":
        days = None
        changed = cancel_subscription(sub, actor=f"{request.user.username}: {reason}")
    else:
        messages.error(request, "Choose a valid subscription action.")
        return redirect("staff_admin_desk_subscriptions")
    if not changed:
        messages.info(request, "No change was made. Only active access can be extended or canceled.")
        return redirect("staff_admin_desk_subscriptions")
    _audit(f"admin.subscription.{action}", request.user, "subscription", sub.pk, {
        "learner_id": str(sub.user_id), "plan_id": str(sub.plan_id),
        "reason": reason, "days": days,
    })
    messages.success(request, "Access period extended." if action == "extend" else "Access canceled immediately; community reconciliation was queued.")
    return redirect("staff_admin_desk_subscriptions")


class BusinessSettingsForm(forms.Form):
    seller_name = forms.CharField(max_length=150, label="Public seller name")
    legal_name = forms.CharField(max_length=255, required=False, label="Legal seller name")
    address = forms.CharField(max_length=4000, required=False, widget=forms.Textarea(attrs={"rows": 3}), label="Business address")
    country = forms.CharField(max_length=2, required=False, label="Seller country (ISO code)")
    support_email = forms.EmailField(max_length=254, required=False, label="Customer support email")
    tax_registration_number = forms.CharField(max_length=100, required=False, label="Tax registration number")
    invoice_prefix = forms.CharField(max_length=20, label="Invoice prefix")
    tax_enabled = forms.BooleanField(required=False, label="Apply configured tax rate to new sales")
    tax_label = forms.CharField(max_length=30, label="Tax label on invoices")
    tax_rate_percentage = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100, label="Tax rate (%)")
    tax_inclusive = forms.BooleanField(required=False, label="Treat displayed prices as tax-inclusive")
    confirm_tax_enable = forms.BooleanField(required=False, label="I have confirmed the tax rate and treatment with my accountant")
    SETTING_FIELDS = (
        "seller_name", "legal_name", "address", "country", "support_email",
        "tax_registration_number", "invoice_prefix", "tax_enabled", "tax_label",
        "tax_rate_percentage", "tax_inclusive",
    )

    def __init__(self, *args, instance, **kwargs):
        self.instance = instance
        initial = dict(kwargs.pop("initial", {}))
        for name in self.SETTING_FIELDS:
            initial.setdefault(name, getattr(instance, name))
        super().__init__(*args, initial=initial, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class", "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            )

    def clean_country(self):
        value = self.cleaned_data.get("country", "").strip().upper()
        if value and len(value) != 2:
            raise forms.ValidationError("Enter a two-letter ISO country code, such as IN.")
        return value

    def clean_invoice_prefix(self):
        value = self.cleaned_data.get("invoice_prefix", "").strip()
        if not value:
            raise forms.ValidationError("Enter an invoice prefix.")
        return value

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("tax_enabled") and not self.instance.tax_enabled and not cleaned.get("confirm_tax_enable"):
            self.add_error("confirm_tax_enable", "Confirm the applicable tax treatment before enabling tax for new sales.")
        return cleaned

    def save(self):
        for name in self.SETTING_FIELDS:
            setattr(self.instance, name, self.cleaned_data[name])
        self.instance.save()
        return self.instance


@login_required
def admin_desk_business(request):
    _guard(request)
    from apps.payments.models import BillingSettings, Invoice

    instance = BillingSettings.objects.filter(pk=1).first()
    if instance is None:
        if not _allowed(request.user, "payments.add_billingsettings"):
            raise PermissionDenied
        instance = BillingSettings(pk=1)
    elif not _allowed(request.user, "payments.change_billingsettings"):
        raise PermissionDenied
    form = BusinessSettingsForm(request.POST if request.method == "POST" else None, instance=instance)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            saved = form.save()
            _audit("admin.business_settings.updated", request.user, "billing_settings", saved.pk, {
                "tax_enabled": bool(saved.tax_enabled),
            })
        messages.success(request, "Business and invoice settings saved.")
        return redirect("staff_admin_desk_business")
    invoices = Invoice.objects.order_by("-issue_date", "-issued_at")[:8] if _allowed(request.user, "payments.view_invoice") else []
    return render(request, "admin/desk_business.html", {
        "form": form, "settings_obj": instance, "invoices": invoices,
        "can_view_invoices": _allowed(request.user, "payments.view_invoice"),
        "desk_nav": _nav(request),
    })


@login_required
def admin_desk_finance(request):
    _guard(request)
    can_pay = _allowed(request.user, "payments.view_paymentintent")
    can_invoice = _allowed(request.user, "payments.view_invoice")
    if not (can_pay or can_invoice):
        raise PermissionDenied
    from apps.payments.models import Invoice, PaymentIntent

    query = request.GET.get("q", "").strip()[:120]
    status_filter = request.GET.get("payment_status", "").strip().lower()
    tab = request.GET.get("tab", "payments").strip().lower()
    if tab not in {"payments", "invoices"}:
        tab = "payments"
    payment_page = invoice_page = None
    counts = {}
    if can_pay:
        qs = PaymentIntent.objects.select_related("user", "plan")
        if status_filter in {x[0] for x in PaymentIntent.Status.choices}:
            qs = qs.filter(status=status_filter)
        if query:
            qs = qs.filter(
                Q(user__username__icontains=query) | Q(user__email__icontains=query)
                | Q(plan__name__icontains=query) | Q(provider_reference__icontains=query)
                | Q(provider_payment_id__icontains=query)
            )
        payment_page = Paginator(qs.order_by("-created_at"), 30).get_page(request.GET.get("payment_page"))
        counts = {value: PaymentIntent.objects.filter(status=value).count() for value, _ in PaymentIntent.Status.choices}
    if can_invoice:
        qs = Invoice.objects.select_related("payment_intent")
        if query:
            qs = qs.filter(
                Q(invoice_number__icontains=query) | Q(customer_name__icontains=query)
                | Q(customer_email__icontains=query) | Q(description__icontains=query)
                | Q(transaction_reference__icontains=query)
                | Q(payment_intent__provider_reference__icontains=query)
            )
        invoice_page = Paginator(qs.order_by("-issue_date", "-issued_at"), 30).get_page(request.GET.get("invoice_page"))
    return render(request, "admin/desk_finance.html", {
        "query": query, "payment_status": status_filter, "tab": tab,
        "payment_page": payment_page, "invoice_page": invoice_page,
        "payment_counts": counts, "can_view_payments": can_pay, "can_view_invoices": can_invoice,
        "payment_status_choices": PaymentIntent.Status.choices,
        "csv_url": reverse("ops-payments-csv") if can_pay else "",
        "desk_nav": _nav(request),
    })


@login_required
def admin_desk_invoice_detail(request, invoice_id):
    _guard(request, "payments.view_invoice")
    from apps.payments.models import Invoice
    invoice = get_object_or_404(Invoice.objects.select_related("payment_intent"), pk=invoice_id)
    return render(request, "admin/desk_invoice_detail.html", {
        "invoice": invoice,
        "back_url": f"{reverse('staff_admin_desk_finance')}?tab=invoices",
        "desk_nav": _nav(request),
    })
