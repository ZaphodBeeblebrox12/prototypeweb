"""P3d: lightweight operational dashboard on the Django admin index.

Purpose: when an admin opens Django Admin, immediately see whether anything
needs attention.  Read-only, based entirely on existing models, one aggregate
query per metric (no N+1, no caching layer, no new persistence).  Metrics the
current user lacks model permission for are omitted.  Rendered into the admin
index via templates/admin/dashboard.html.
"""
import datetime
from urllib.parse import urlencode

from django.conf import settings
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
    if isinstance(query, dict):
        query = urlencode(query, doseq=True)
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

    # Customer counts are separate from course-content permissions. Only show
    # them when the current staff member can view the user changelist.
    from django.contrib.auth import get_user_model

    user_model = get_user_model()
    if _has_model_perm(request, "accounts", "user"):
        user_admin = admin.site._registry.get(user_model)
        if user_admin and user_admin.has_view_permission(request):
            ctx["accounts"] = {
                # Exclude staff accounts so this represents learner/customer
                # accounts, not the administrators themselves.
                "active_learners": user_model.objects.filter(
                    is_active=True, is_staff=False,
                ).count(),
                "links": {
                    "users": reverse("admin:accounts_user_changelist"),
                },
            }

    if _has_model_perm(request, "subscriptions", "subscription"):
        ctx["subscriptions"] = {
            "active": Subscription.objects.filter(
                is_active=True, status=Subscription.Status.ACTIVE).count(),
            "expiring_soon": Subscription.objects.filter(
                is_active=True, status=Subscription.Status.ACTIVE,
                expires_at__gt=now, expires_at__lte=soon).count(),
            "recently_expired": Subscription.objects.filter(
                status=Subscription.Status.EXPIRED,
                expires_at__gte=recent, expires_at__lte=now).count(),
            "recently_canceled": Subscription.objects.filter(
                canceled_at__gte=recent).count(),
            "links": {
                "all": _changelist("subscriptions", "subscription"),
                "expiring_soon": _changelist(
                    "subscriptions", "subscription",
                    {
                        "is_active__exact": "1",
                        "status__exact": Subscription.Status.ACTIVE,
                        "expires_at__gt": now.isoformat(),
                        "expires_at__lte": soon.isoformat(),
                    }),
                "recently_expired": _changelist(
                    "subscriptions", "subscription",
                    {
                        "status__exact": Subscription.Status.EXPIRED,
                        "expires_at__gte": recent.isoformat(),
                        "expires_at__lte": now.isoformat(),
                    }),
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

    if _has_model_perm(request, "policies", "policyversion"):
        from apps.policies.models import PolicyVersion
        policy_admin = admin.site._registry.get(PolicyVersion)
        if policy_admin and policy_admin.has_view_permission(request):
            from apps.policies.services import sales_policy_readiness

            readiness = sales_policy_readiness()
            readiness["url"] = reverse("admin:policies_policyversion_changelist")
            ctx["policy_readiness"] = readiness

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

    can_view_invoices = _has_model_perm(request, "payments", "invoice")
    can_edit_billing_settings = _has_model_perm(
        request, "payments", "billingsettings", "change"
    )
    if can_view_invoices or can_edit_billing_settings:
        from apps.payments.models import Invoice
        ctx["invoicing"] = {
            "count": Invoice.objects.count() if can_view_invoices else None,
            "links": {
                "invoices": (
                    reverse("admin:payments_invoice_changelist")
                    if can_view_invoices else ""
                ),
                "settings": (
                    reverse("admin:payments_billingsettings_changelist")
                    if can_edit_billing_settings else ""
                ),
            },
        }

    if can_edit_billing_settings:
        from apps.payments.models import BillingSettings

        billing = BillingSettings.get_solo()
        business_fields = (
            ("legal_name", "Legal seller name", billing.legal_name.strip()),
            ("address", "Business address", billing.address.strip()),
            ("country", "Seller country (ISO code)", billing.country.strip()),
            ("support_email", "Customer support email", billing.support_email.strip()),
            ("invoice_prefix", "Invoice number prefix", billing.invoice_prefix.strip()),
        )
        missing_business = [
            {"field": field, "label": label}
            for field, label, value in business_fields if not value
        ]
        ctx["business_readiness"] = {
            "ready": not missing_business,
            "items": missing_business,
            "url": reverse("admin:payments_billingsettings_changelist"),
        }

        database_engine = settings.DATABASES.get("default", {}).get("ENGINE", "")
        site_base_url = (getattr(settings, "SITE_BASE_URL", "") or "").strip()
        email_backend = getattr(settings, "EMAIL_BACKEND", "")
        default_from_email = (getattr(settings, "DEFAULT_FROM_EMAIL", "") or "").strip()
        smtp_ready = (
            "console.EmailBackend" not in email_backend
            and bool(getattr(settings, "EMAIL_HOST", "").strip())
            and bool(default_from_email)
            and "example.com" not in default_from_email.casefold()
        )
        razorpay_ready = all((
            bool(getattr(settings, "RAZORPAY_KEY_ID", "")),
            bool(getattr(settings, "RAZORPAY_KEY_SECRET", "")),
            bool(getattr(settings, "RAZORPAY_WEBHOOK_SECRET", "")),
        ))
        stripe_ready = all((
            bool(getattr(settings, "STRIPE_SECRET_KEY", "")),
            bool(getattr(settings, "STRIPE_PUBLISHABLE_KEY", "")),
            bool(getattr(settings, "STRIPE_WEBHOOK_SECRET", "")),
        ))
        ctx["runtime_readiness"] = {
            "items": [
                {
                    "label": "Database engine",
                    "ready": "sqlite3" not in database_engine.casefold(),
                    "reason": (
                        "Uses a server database engine; backup and restore still require a separate check."
                        if "sqlite3" not in database_engine.casefold()
                        else "SQLite is configured. Confirm a durable production database before accepting sales."
                    ),
                    "required": True,
                },
                {
                    "label": "Public HTTPS base URL",
                    "ready": site_base_url.startswith("https://"),
                    "reason": (
                        "HTTPS base URL is configured."
                        if site_base_url.startswith("https://")
                        else "Set SITE_BASE_URL to the deployed public HTTPS URL."
                    ),
                    "required": True,
                },
                {
                    "label": "Transactional email",
                    "ready": smtp_ready,
                    "reason": (
                        "Email settings appear configured; send a real delivery test."
                        if smtp_ready
                        else "Configure a real email backend, SMTP host and sender address."
                    ),
                    "required": True,
                },
                {
                    "label": "Razorpay + webhook",
                    "ready": razorpay_ready,
                    "reason": (
                        "Credentials are present; confirm test/live mode and webhook events."
                        if razorpay_ready
                        else "Set the Razorpay key ID, API secret and webhook secret in Render."
                    ),
                    "required": True,
                },
                {
                    "label": "Stripe + webhook (international pricing)",
                    "ready": stripe_ready,
                    "reason": (
                        "Credentials are present; complete a Stripe test purchase."
                        if stripe_ready
                        else "Required only for non-India pricing; set Stripe API, publishable and webhook keys if in scope."
                    ),
                    "required": False,
                },
            ],
            "url": reverse("admin:payments_billingsettings_changelist"),
        }

    if _has_model_perm(request, "bot_integration", "botaccessaudit"):
        ctx["telegram"] = {
            "recent_failed": BotAccessAudit.objects.filter(
                status="failed", created_at__gte=recent).count(),
            "links": {
                "failed": _changelist(
                    "bot_integration", "botaccessaudit",
                    {
                        "status__exact": "failed",
                        "created_at__gte": recent.isoformat(),
                    }),
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
                "pending": _changelist(
                    "jobs", "job", {"status__exact": Job.STATUS_PENDING}),
                "failed": _changelist(
                    "jobs", "job",
                    {
                        "status__exact": Job.STATUS_FAILED,
                        "updated_at__gte": recent.isoformat(),
                    }),
                "stalled": _changelist(
                    "jobs", "job", {"queue_state": "stalled"}),
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
