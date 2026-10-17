"""P3d: lightweight operational dashboard on the Django admin index.

Purpose: when an admin opens Django Admin, immediately see whether anything
needs attention.  Read-only, based entirely on existing models, one aggregate
query per metric (no N+1, no caching layer, no new persistence).  Metrics the
current user lacks model permission for are omitted.  Rendered into the admin
index via templates/admin/dashboard.html.
"""
import datetime

from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone



def _has_model_perm(request, app_label, model_name, perm="view"):
    return request.user.has_perm(f"{app_label}.{perm}_{model_name}")


def _changelist(app_label, model_name, query=""):
    base = reverse(f"admin:{app_label}_{model_name}_changelist")
    return f"{base}?{query}" if query else base


def _subscription_dashboard_context(request):
    from apps.bot_integration.models import BotAccessAudit
    from apps.jobs.models import Job
    from apps.payments.models import PaymentIntent
    from apps.subscriptions.models import Subscription
    """Permission-filtered metrics; each is one COUNT/aggregate query."""
    ctx = {}
    now = timezone.now()
    soon = now + datetime.timedelta(days=7)
    recent = now - datetime.timedelta(days=7)

    if _has_model_perm(request, "subscriptions", "subscription"):
        ctx["subscriptions"] = {
            "active": Subscription.objects.filter(
                is_active=True, status=Subscription.Status.ACTIVE).count(),
            "expiring_soon": Subscription.objects.filter(
                is_active=True, status=Subscription.Status.ACTIVE,
                expires_at__gt=now, expires_at__lte=soon).count(),
            "recently_expired": Subscription.objects.filter(
                status=Subscription.Status.EXPIRED,
                expires_at__gte=recent).count(),
            "recently_canceled": Subscription.objects.filter(
                canceled_at__gte=recent).count(),
            "links": {
                "expiring_soon": _changelist(
                    "subscriptions", "subscription",
                    "is_active__exact=1&status__exact=active"
                    "&expires_at__gte=&expires_at__lte="),
            },
        }
        # Trend: signups per day for the last 14 days (single grouped query).
        trend = (
            Subscription.objects.filter(
                started_at__gte=now - datetime.timedelta(days=14))
            .annotate(day=TruncDate("started_at"))
            .values("day").annotate(total=Count("id")).order_by("day")
        )
        ctx["recent_signups"] = list(trend)

    if _has_model_perm(request, "payments", "paymentintent"):
        ctx["payments"] = {
            "pending": PaymentIntent.objects.filter(
                status=PaymentIntent.Status.PENDING).count(),
            "failed": PaymentIntent.objects.filter(
                status=PaymentIntent.Status.FAILED).count(),
            "recent_success": PaymentIntent.objects.filter(
                status=PaymentIntent.Status.SUCCESS,
                created_at__gte=recent).count(),
            "links": {
                "pending": _changelist("payments", "paymentintent",
                                       "status__exact=pending"),
                "failed": _changelist("payments", "paymentintent",
                                      "status__exact=failed"),
            },
        }

    if _has_model_perm(request, "bot_integration", "botaccessaudit"):
        ctx["telegram"] = {
            "recent_failed": BotAccessAudit.objects.filter(
                status="failed", created_at__gte=recent).count(),
            "links": {
                "failed": _changelist("bot_integration", "botaccessaudit",
                                      "status__exact=failed"),
            },
        }

    if _has_model_perm(request, "jobs", "job"):
        ctx["jobs"] = {
            "pending": Job.objects.filter(status=Job.STATUS_PENDING).count(),
            "failed": Job.objects.filter(
                status=Job.STATUS_FAILED,
                updated_at__gte=recent).count(),
            "stalled": Job.objects.filter(
                attempts__gte=3,
                status__in=[Job.STATUS_RUNNING, Job.STATUS_PENDING]).count(),
            "links": {
                "failed": _changelist("jobs", "job", "status__exact=failed"),
            },
        }
    return ctx


def operational_dashboard(request):
    # Model imports are deferred to request time: this module is imported
    # from apps/__init__.py during app loading, before the registry is ready.
    return render(request, "admin/dashboard.html",
                  _subscription_dashboard_context(request))


@login_required
def staff_admin_desk(request):
    """Read-only, permission-aware operational desk for Django staff users."""
    if not request.user.is_active or not request.user.is_staff:
        raise PermissionDenied

    from apps.academy.permissions import is_course_content_admin

    context = _subscription_dashboard_context(request)
    context["django_admin_url"] = reverse("admin:index")
    context["can_manage_course_content"] = is_course_content_admin(request.user)

    if context["can_manage_course_content"]:
        from django.contrib.auth import get_user_model
        from apps.academy.models import (
            Course, CourseEntitlement, CourseImport, CourseModule, CourseOffer,
            Lesson, LessonProgress,
        )

        now = timezone.now()
        course_counts = Course.objects.aggregate(
            courses_total=Count("id"),
            draft_courses=Count("id", filter=Q(status=Course.Status.DRAFT)),
            published_courses=Count("id", filter=Q(status=Course.Status.PUBLISHED)),
            archived_courses=Count("id", filter=Q(status=Course.Status.ARCHIVED)),
        )
        course_counts.update({
            "published_lessons": Lesson.objects.filter(
                is_published=True,
                module__is_published=True,
                module__course__status=Course.Status.PUBLISHED,
            ).count(),
            "active_offers": CourseOffer.objects.filter(
                is_active=True,
                course__status=Course.Status.PUBLISHED,
                plan__isnull=False,
                plan__is_active=True,
            ).count(),
            "imports_awaiting_review": CourseImport.objects.filter(
                status=CourseImport.Status.REVIEW,
            ).count(),
            "active_entitlements": CourseEntitlement.objects.filter(
                status=CourseEntitlement.Status.ACTIVE, starts_at__lte=now,
            ).filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now)).count(),
            "completed_lessons": LessonProgress.objects.filter(
                status=LessonProgress.Status.COMPLETED,
                lesson__is_published=True,
                lesson__module__is_published=True,
                lesson__module__course__status=Course.Status.PUBLISHED,
            ).count(),
            "active_learners": get_user_model().objects.filter(
                is_active=True, is_staff=False,
            ).count(),
        })
        context["course_metrics"] = course_counts
        link_models = {
            "courses": Course,
            "modules": CourseModule,
            "lessons": Lesson,
            "offers": CourseOffer,
            "imports": CourseImport,
            "entitlements": CourseEntitlement,
        }
        course_links = {}
        for key, model in link_models.items():
            model_admin = admin.site._registry.get(model)
            if model_admin and model_admin.has_view_permission(request):
                course_links[key] = reverse(
                    f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist"
                )
        context["course_links"] = course_links

    return render(request, "admin/desk.html", context)
