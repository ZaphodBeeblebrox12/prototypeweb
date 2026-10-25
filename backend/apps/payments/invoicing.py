"""Small creator-friendly invoice helpers; no general accounting ledger."""
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.utils import timezone

from .models import BillingSettings, Invoice, PaymentIntent


def _round_cents(value):
    return int(Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def calculate_price_breakdown(discounted_amount_cents, billing_settings):
    """Apply one fixed percentage only when the owner explicitly enables tax.

    This does not infer jurisdiction, tax registration or applicability.
    """
    listed_amount = max(int(discounted_amount_cents), 0)
    rate = Decimal(billing_settings.tax_rate_percentage or "0.00")
    enabled = bool(billing_settings.tax_enabled and rate > 0)
    label = billing_settings.tax_label or "Tax"

    if not enabled:
        return {
            "subtotal_cents": listed_amount,
            "tax_enabled": False,
            "tax_rate_percentage": Decimal("0.00"),
            "tax_label": label,
            "tax_amount_cents": 0,
            "tax_inclusive": False,
            "total_cents": listed_amount,
        }

    if billing_settings.tax_inclusive:
        tax = _round_cents(Decimal(listed_amount) * rate / (Decimal("100") + rate))
        subtotal = listed_amount - tax
        total = listed_amount
    else:
        subtotal = listed_amount
        tax = _round_cents(Decimal(subtotal) * rate / Decimal("100"))
        total = subtotal + tax

    return {
        "subtotal_cents": subtotal,
        "tax_enabled": True,
        "tax_rate_percentage": rate,
        "tax_label": label,
        "tax_amount_cents": tax,
        "tax_inclusive": bool(billing_settings.tax_inclusive),
        "total_cents": total,
    }


def issue_invoice(payment_intent):
    """Create exactly one invoice snapshot for a verified successful payment."""
    if payment_intent.status != PaymentIntent.Status.SUCCESS:
        return None

    with transaction.atomic():
        # The settings row serializes invoice-number allocation on PostgreSQL.
        BillingSettings.objects.get_or_create(pk=1)
        business = BillingSettings.objects.select_for_update().get(pk=1)
        existing = Invoice.objects.filter(payment_intent=payment_intent).first()
        if existing:
            return existing

        issue_date = timezone.localdate()
        sequence = Invoice.objects.filter(issue_date__year=issue_date.year).count() + 1
        prefix = (business.invoice_prefix or "TT").strip().rstrip("-") or "TT"

        from apps.academy.models import CourseOffer
        offer = (
            CourseOffer.objects.filter(plan_id=payment_intent.plan_id)
            .select_related("course")
            .first()
        )
        description = offer.course.title if offer else payment_intent.plan.name
        full_name = getattr(payment_intent.user, "full_name", "") or payment_intent.user.username
        subtotal = payment_intent.subtotal_cents or max(
            payment_intent.amount - payment_intent.tax_amount_cents, 0
        )

        return Invoice.objects.create(
            invoice_number=f"{prefix}-{issue_date.year}-{sequence:06d}",
            payment_intent=payment_intent,
            issue_date=issue_date,
            currency=payment_intent.currency,
            seller_name=business.seller_name or "TradeThesis",
            seller_legal_name=business.legal_name,
            seller_address=business.address,
            seller_country=business.country,
            seller_support_email=business.support_email,
            seller_tax_registration_number=business.tax_registration_number,
            customer_name=full_name,
            customer_email=payment_intent.user.email or "",
            description=description,
            subtotal_cents=subtotal,
            tax_enabled=payment_intent.tax_enabled,
            tax_rate_percentage=payment_intent.tax_rate_percentage,
            tax_label=payment_intent.tax_label,
            tax_amount_cents=payment_intent.tax_amount_cents,
            tax_inclusive=payment_intent.tax_inclusive,
            total_cents=payment_intent.amount,
            transaction_reference=payment_intent.provider_payment_id or payment_intent.provider_reference,
        )
