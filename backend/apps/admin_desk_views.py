"""Creator-facing Admin Desk workflows; model imports stay inside request handlers."""
from datetime import timedelta

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
from django.views.decorators.http import require_POST


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
            **build_course_import_review_data(record, request, allow_asset_edits=False),
            "publish_url": reverse("staff_admin_desk_course_approve", args=[record.pk]),
            "reject_url": reverse("staff_admin_desk_course_reject", args=[record.pk]),
            "changelist_url": reverse("staff_admin_desk_course_reviews"),
            "back_url": reverse("staff_admin_desk_course_reviews"),
            "back_label": "Back to course approvals",
            "desk_url": reverse("staff_admin_desk"),
            "desk_review": True,
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
