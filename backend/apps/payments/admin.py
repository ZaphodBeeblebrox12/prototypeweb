"""
Payment admin configuration.
"""
from django.contrib import admin

import uuid

from django.contrib import admin
from django.utils.html import format_html

from .models import BillingSettings, Invoice, PaymentIntent, Refund, WebhookEvent


class RefundInline(admin.TabularInline):
    """Refund evidence against a payment: read-only, no add/delete."""
    model = Refund
    extra = 0
    can_delete = False
    readonly_fields = [f.name for f in Refund._meta.fields]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(PaymentIntent)
class PaymentIntentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "plan",
        "amount_display",
        "currency",
        "provider",
        "status",
        "country",
        "created_at",
        "refund_display",
        "chargeback_display",
    ]
    list_filter = ["status", "provider", "currency", "country", "created_at",
                   "chargeback", "chargeback_confirmed"]
    list_select_related = ["user", "plan"]
    autocomplete_fields = ["user", "plan"]
    search_fields = ["user__username", "user__email", "plan__name",
                   "provider_reference", "provider_payment_id", "chargeback_reference"]
    # PaymentIntent is financial/audit data: ALL fields read-only.  Payment
    # state is set only by the provider-verification flow (P1); an admin must
    # never mark paid/failed or edit amount/provider/snapshots by hand.
    readonly_fields = [f.name for f in PaymentIntent._meta.fields]
    inlines = [RefundInline]
    @admin.action(description="Export selected payments as CSV")
    def export_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="payment_intents.csv"'
        w = csv.writer(resp)
        w.writerow(["date", "user", "plan", "amount_cents", "currency",
                    "provider", "status", "refunded_cents", "chargeback",
                    "provider_reference"])
        for pi in queryset.select_related("user", "plan"):
            w.writerow([pi.created_at.isoformat(), pi.user.username, pi.plan.name,
                        pi.amount, pi.currency, pi.provider, pi.status,
                        pi.refunded_cents, pi.chargeback_confirmed,
                        pi.provider_reference])
        return resp

    actions = ["mark_charged_back", "record_manual_refund", "export_csv"]

    def has_delete_permission(self, request, obj=None):
        # Financial evidence; never delete.
        return False

    def amount_display(self, obj):
        return f"{obj.currency} {obj.amount_dollars:.2f}"
    amount_display.short_description = "Amount"

    def refund_display(self, obj):
        if obj.refunded_cents <= 0:
            return ""
        state = "fully" if obj.is_fully_refunded else "partially"
        color = "#b91c1c" if obj.is_fully_refunded else "#b45309"
        return format_html('<span style="color:{};font-weight:600">{} refunded {}</span>',
                           color, obj.currency, state)
    refund_display.short_description = "Refunded"

    def chargeback_display(self, obj):
        if obj.chargeback_confirmed:
            return format_html('<span style="color:#b91c1c;font-weight:600">CONFIRMED{}</span>',
                               " ({})".format(obj.chargeback_reference) if obj.chargeback_reference else "")
        if obj.chargeback:
            return format_html('<span style="color:#b45309;font-weight:600">Disputed{}</span>',
                               " ({})".format(obj.chargeback_reference) if obj.chargeback_reference else "")
        return ""
    chargeback_display.short_description = "Chargeback"

    # ── audited, idempotent manual billing actions ─────────────────────
    # These exist for provider cases with no webhook (e.g. Razorpay
    # disputes). Both reuse the same claiming services as the webhook path;
    # the original amount/status remain read-only above.
    @admin.action(description="Mark selected payments as CHARGED BACK (manual: cancels subscription + revokes access)")
    def mark_charged_back(self, request, queryset):
        from .services import confirm_chargeback
        from .notifications import notify_chargedback
        performed = 0
        for intent in queryset:
            if confirm_chargeback(
                    intent, dispute_reference=f"manual:{request.user.pk}",
                    source="manual", actor=request.user):
                performed += 1
                notify_chargedback(intent)
        self.message_user(
            request,
            f"{performed} payment(s) confirmed as charged back: subscription(s) "
            f"canceled and access revoked. Already-confirmed rows were skipped.")

    @admin.action(description="Record FULL manual refund (use after refunding in the provider dashboard)")
    def record_manual_refund(self, request, queryset):
        from .services import apply_refund_policy, record_refund
        from .notifications import notify_refunded
        from apps.audit.models import AuditLog
        recorded = 0
        for intent in queryset:
            intent.refresh_from_db()
            remainder = intent.amount - intent.refunded_cents
            if remainder <= 0:
                continue
            refund, created = record_refund(
                intent, provider=intent.provider,
                provider_refund_id=f"manual:{uuid.uuid4()}",
                amount_cents=remainder, currency=intent.currency,
                source="manual", metadata={"admin_id": str(request.user.pk)})
            if not created:
                continue
            recorded += 1
            AuditLog.log(
                action="payment.refund.manual",
                user=request.user,
                object_type="payment_intent", object_id=intent.pk,
                metadata={"refund_id": str(refund.pk),
                          "amount_cents": remainder, "currency": intent.currency,
                          "affected_user_id": str(intent.user_id)})
            apply_refund_policy(intent)
            notify_refunded(intent)
        self.message_user(
            request,
            f"{recorded} manual refund(s) recorded. Full refunds cancel the "
            f"affected subscription automatically.")

@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    """Received provider webhook events: read-only audit, no add/delete."""
    list_display = ["provider", "event_type", "status", "provider_event_id", "received_at", "processed_at"]
    list_filter = ["provider", "status", "event_type"]
    search_fields = ["provider_event_id", "event_type"]
    readonly_fields = [f.name for f in WebhookEvent._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ["payment_intent", "provider", "provider_refund_id",
                    "amount_display", "currency", "source", "refunded_at", "created_at"]
    list_filter = ["provider", "source", "currency"]
    search_fields = ["provider_refund_id", "payment_intent__user__username",
                     "payment_intent__user__email", "payment_intent__provider_reference"]
    readonly_fields = [f.name for f in Refund._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def amount_display(self, obj):
        return f"{obj.currency} {obj.amount_dollars:.2f}"
    amount_display.short_description = "Amount"


@admin.register(BillingSettings)
class BillingSettingsAdmin(admin.ModelAdmin):
    """One editable settings row; financial snapshots remain read-only."""
    list_display = [
        "seller_name", "country", "tax_enabled", "tax_label",
        "tax_rate_percentage", "tax_inclusive", "updated_at",
    ]
    fieldsets = [
        ("Business identity", {
            "fields": (
                "seller_name", "legal_name", "address", "country",
                "support_email", "tax_registration_number", "invoice_prefix",
            ),
        }),
        ("Tax configuration", {
            "fields": ("tax_enabled", "tax_label", "tax_rate_percentage", "tax_inclusive"),
            "description": (
                "Tax is disabled by default. Enable it only after confirming "
                "the applicable rate and treatment with your accountant. The "
                "current implementation applies one fixed percentage to all "
                "new checkouts; it is not a jurisdiction-aware tax engine."
            ),
        }),
        ("System", {"fields": ("updated_at",)}),
    ]
    readonly_fields = ["updated_at"]

    def has_add_permission(self, request):
        return not BillingSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        "invoice_number", "issue_date", "customer_name", "description",
        "currency", "total_display", "tax_amount_cents", "tax_enabled",
    ]
    list_filter = ["issue_date", "currency", "tax_enabled", "tax_label"]
    search_fields = [
        "invoice_number", "customer_name", "customer_email", "description",
        "transaction_reference", "payment_intent__provider_reference",
    ]
    readonly_fields = [field.name for field in Invoice._meta.fields]
    list_select_related = ["payment_intent"]
    date_hierarchy = "issue_date"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
