"""P3d: lightweight operational dashboard on the Django admin index.

Purpose: when an admin opens Django Admin, immediately see whether anything
needs attention.  Read-only, based entirely on existing models, one aggregate
query per metric (no N+1, no caching layer, no new persistence).  Metrics the
current user lacks model permission for are omitted.  Rendered into the admin
index via templates/admin/dashboard.html.
"""
import datetime

from django.contrib import admin
from django.db.models import Count, Q, Sum
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



def _growth_dashboard_context(request):
    """Build the staff-facing business overview from existing database records.

    This remains deliberately read-only. Metrics are permission-filtered and
    financial amounts are kept grouped by currency; no analytics tables or
    background jobs are required.
    """
    from decimal import Decimal

    from django.contrib.auth import get_user_model
    from apps.academy.models import Course, CourseEntitlement
    from apps.payments.models import PaymentIntent
    from apps.subscriptions.models import Subscription

    period_options = [
        {"value": 7, "label": "Last 7 days"},
        {"value": 30, "label": "Last 30 days"},
        {"value": 90, "label": "Last 90 days"},
        {"value": 365, "label": "Last 12 months"},
    ]
    try:
        period_days = int(request.GET.get("range", "30"))
    except (TypeError, ValueError):
        period_days = 30
    if period_days not in {7, 30, 90, 365}:
        period_days = 30

    now = timezone.now()
    today = timezone.localdate()
    start_day = today - datetime.timedelta(days=period_days - 1)
    end_day = today + datetime.timedelta(days=1)
    previous_start_day = start_day - datetime.timedelta(days=period_days)
    current_tz = timezone.get_current_timezone()

    def _midnight(day):
        return timezone.make_aware(
            datetime.datetime.combine(day, datetime.time.min),
            current_tz,
        )

    start_at = _midnight(start_day)
    end_at = _midnight(end_day)
    previous_start_at = _midnight(previous_start_day)
    day_buckets = [
        start_day + datetime.timedelta(days=offset)
        for offset in range(period_days)
    ]
    labels = [
        day.strftime("%d %b") if period_days <= 90 else day.strftime("%b %y")
        for day in day_buckets
    ]

    context = {
        "selected_range": period_days,
        "range_options": period_options,
        "growth_chart_data": {"labels": labels, "series": []},
        "quick_links": [],
        "recent_members": [],
        "recent_payments": [],
        "mrr_by_currency": [],
        "payment_metrics": None,
        "member_metrics": None,
        "growth_subscriptions": None,
        "course_metrics": None,
        "active_enrollment_count": None,
    }

    chart_series = []
    User = get_user_model()
    can_view_users = _has_model_perm(request, "accounts", "user")
    if can_view_users:
        members = User.objects.filter(is_staff=False)
        new_members = members.filter(date_joined__gte=start_at, date_joined__lt=end_at).count()
        previous_members = members.filter(
            date_joined__gte=previous_start_at, date_joined__lt=start_at
        ).count()
        context["member_metrics"] = {
            "total": members.count(),
            "new": new_members,
            "delta": new_members - previous_members,
            "previous": previous_members,
        }

        member_trend = (
            members.filter(date_joined__gte=start_at, date_joined__lt=end_at)
            .annotate(day=TruncDate("date_joined"))
            .values("day")
            .annotate(total=Count("id"))
            .order_by("day")
        )
        counts_by_day = {row["day"]: row["total"] for row in member_trend}
        chart_series.append({
            "name": "New members",
            "values": [counts_by_day.get(day, 0) for day in day_buckets],
        })
        context["recent_members"] = list(members.order_by("-date_joined")[:6])

    can_view_subscriptions = _has_model_perm(request, "subscriptions", "subscription")
    if can_view_subscriptions:
        active_subscriptions = (
            Subscription.objects.filter(
                is_active=True,
                status=Subscription.Status.ACTIVE,
            )
            .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
        )
        active_count = active_subscriptions.count()
        started_this_period = Subscription.objects.filter(
            started_at__gte=start_at, started_at__lt=end_at
        )
        new_subscriptions = started_this_period.count()
        previous_subscriptions = Subscription.objects.filter(
            started_at__gte=previous_start_at, started_at__lt=start_at
        ).count()
        context["growth_subscriptions"] = {
            "active": active_count,
            "new": new_subscriptions,
            "delta": new_subscriptions - previous_subscriptions,
            "previous": previous_subscriptions,
        }

        subscription_trend = (
            started_this_period.annotate(day=TruncDate("started_at"))
            .values("day")
            .annotate(total=Count("id"))
            .order_by("day")
        )
        counts_by_day = {row["day"]: row["total"] for row in subscription_trend}
        chart_series.append({
            "name": "Subscription records",
            "values": [counts_by_day.get(day, 0) for day in day_buckets],
        })

        # Estimate monthly recurring value only where the subscription has a
        # saved price/currency snapshot and a recurring billing interval.
        monthly_totals = {}
        month_divisors = {"monthly": 1, "quarterly": 3, "yearly": 12}
        for subscription in active_subscriptions.exclude(
            is_gift=True,
        ).exclude(
            is_admin_grant=True,
        ).exclude(
            plan__is_trial=True,
        ).select_related(
            "plan", "plan_price", "geo_plan_price"
        ):
            price_cents = subscription.price_cents
            interval = (
                subscription.plan_price.interval
                if subscription.plan_price_id
                else (
                    subscription.geo_plan_price.interval
                    if subscription.geo_plan_price_id
                    else None
                )
            )
            currency = (
                subscription.price_currency
                or (
                    subscription.plan_price.currency
                    if subscription.plan_price_id
                    else ""
                )
                or (
                    subscription.geo_plan_price.currency
                    if subscription.geo_plan_price_id
                    else ""
                )
            ).upper()
            divisor = month_divisors.get(interval)
            if price_cents is None or not currency or not divisor:
                continue
            monthly_totals[currency] = (
                monthly_totals.get(currency, Decimal("0"))
                + (Decimal(price_cents) / Decimal(divisor))
            )
        context["mrr_by_currency"] = [
            {
                "currency": currency,
                "amount": f"{(minor_units / Decimal('100')).quantize(Decimal('0.01')):,.2f}",
            }
            for currency, minor_units in sorted(monthly_totals.items())
        ]

    if _has_model_perm(request, "payments", "paymentintent"):
        successful_in_period = PaymentIntent.objects.filter(
            status=PaymentIntent.Status.SUCCESS,
            created_at__gte=start_at,
            created_at__lt=end_at,
        )
        grouped_revenue = (
            successful_in_period.values("currency")
            .annotate(total=Sum("amount"), transactions=Count("id"))
            .order_by("currency")
        )
        gross_by_currency = [
            {
                "currency": row["currency"],
                "amount": f"{(Decimal(row['total'] or 0) / Decimal('100')).quantize(Decimal('0.01')):,.2f}",
                "transactions": row["transactions"],
            }
            for row in grouped_revenue
        ]
        context["payment_metrics"] = {
            "successful_count": successful_in_period.count(),
            "gross_by_currency": gross_by_currency,
        }
        recent_payments = list(
            PaymentIntent.objects.select_related("user", "plan").order_by("-created_at")[:6]
        )
        for payment in recent_payments:
            payment.dashboard_amount = (
                f"{payment.currency} {payment.amount / 100:,.2f}"
            )
        context["recent_payments"] = recent_payments

    if _has_model_perm(request, "academy", "course"):
        context["course_metrics"] = {
            "total": Course.objects.count(),
            "published": Course.objects.filter(status=Course.Status.PUBLISHED).count(),
            "draft": Course.objects.filter(status=Course.Status.DRAFT).count(),
        }

    if _has_model_perm(request, "academy", "courseentitlement"):
        context["active_enrollment_count"] = (
            CourseEntitlement.objects.filter(
                status=CourseEntitlement.Status.ACTIVE,
                revoked_at__isnull=True,
                starts_at__lte=now,
            )
            .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
            .count()
        )

    quick_link_options = [
        ("accounts", "user", "Members", ""),
        ("academy", "course", "Courses", ""),
        ("academy", "courseentitlement", "Course access", ""),
        ("subscriptions", "subscription", "Subscriptions", ""),
        ("payments", "paymentintent", "Payments", ""),
        ("bot_integration", "botaccessaudit", "Community access events", "status__exact=failed"),
        ("jobs", "job", "Background jobs", ""),
    ]
    for app_label, model_name, label, query in quick_link_options:
        if _has_model_perm(request, app_label, model_name):
            context["quick_links"].append({
                "label": label,
                "url": _changelist(app_label, model_name, query),
            })

    context["growth_chart_data"] = {
        "labels": labels,
        "series": chart_series,
    }
    return context


def operational_dashboard(request):
    """Render the branded staff workspace; Django Admin remains at /admin/."""
    context = admin.site.each_context(request)
    context.update(_subscription_dashboard_context(request))
    context.update(_growth_dashboard_context(request))
    return render(request, "admin/operational_dashboard.html", context)
