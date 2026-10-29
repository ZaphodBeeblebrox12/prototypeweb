"""Course Builder pricing helpers.

Pricing is configured while authoring, then synchronized into the existing
CourseOffer / PlanPrice / GeoPlanPrice commerce records only when a reviewed
course revision is published. PaymentIntent rows keep their own amount snapshot.
"""

import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify

from apps.subscriptions.models import GeoPlanPrice, Plan, PlanPrice, Product
from apps.subscriptions.services import COUNTRY_TO_REGION, format_price, resolve_plan_price
from .models import Course, CourseOffer


SUPPORTED_CURRENCIES = {"INR", "USD", "EUR", "GBP"}
_AMOUNT_RE = re.compile(r"^\d{1,8}(?:\.\d{1,2})?$")
_CURRENCY_SYMBOLS = {"₹": "INR", "$": "USD", "€": "EUR", "£": "GBP"}


def _amount_to_minor_units(value: Any, *, label: str) -> int | None:
    raw = str(value if value is not None else "").strip().replace(",", "")
    if not raw:
        return None
    if not _AMOUNT_RE.fullmatch(raw):
        raise ValidationError(f"{label} must be a positive amount with up to two decimal places.")
    try:
        amount = Decimal(raw)
    except InvalidOperation as exc:
        raise ValidationError(f"{label} is not a valid amount.") from exc
    if amount <= 0:
        raise ValidationError(f"{label} must be greater than zero. Use the Free access model for a free course.")
    return int((amount * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _legacy_amount(state: dict[str, Any]) -> tuple[str, str]:
    """Read a historical display-only price when reopening an older draft."""
    display = str(state.get("price") or "").strip()
    match = re.search(r"\d{1,8}(?:\.\d{1,2})?", display.replace(",", ""))
    if not match:
        return "", "INR"
    currency = next(
        (code for symbol, code in _CURRENCY_SYMBOLS.items() if symbol in display),
        "INR",
    )
    return match.group(0), currency


def parse_course_pricing(state: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize the Course Builder's base price and geo overrides.

    Override lines use either 'IN 499 INR' or 'region APAC 9.99 USD'.
    Amounts are expressed in major currency units; stored commerce prices are
    integer minor units.
    """
    raw_amount = state.get("priceAmount", "")
    raw_currency = str(state.get("priceCurrency") or "").strip().upper()
    if "priceAmount" not in state and not raw_currency:
        raw_amount, raw_currency = _legacy_amount(state)
    currency = raw_currency or "INR"
    if currency not in SUPPORTED_CURRENCIES:
        raise ValidationError("Choose INR, USD, EUR or GBP as the course price currency.")
    price_cents = _amount_to_minor_units(raw_amount, label="Course price")

    overrides_text = str(state.get("geoPriceOverrides") or "")
    geo_prices = []
    seen_scopes = set()
    allowed_regions = set(COUNTRY_TO_REGION.values())
    for line_number, raw_line in enumerate(overrides_text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) == 3:
            code, amount_text, override_currency = parts
            scope = "country"
        elif len(parts) == 4 and parts[0].lower() == "region":
            _, code, amount_text, override_currency = parts
            scope = "region"
        else:
            raise ValidationError(
                f"Regional price line {line_number} must be 'IN 499 INR' or 'region APAC 9.99 USD'."
            )
        code = code.upper()
        override_currency = override_currency.upper()
        if override_currency not in SUPPORTED_CURRENCIES:
            raise ValidationError(
                f"Regional price line {line_number}: currency must be INR, USD, EUR or GBP."
            )
        if scope == "country":
            if not re.fullmatch(r"[A-Z]{2}", code) or code in {"XX", "ZZ"}:
                raise ValidationError(
                    f"Regional price line {line_number}: use a valid two-letter country code."
                )
            key = ("country", code)
            geo_row = {"country": code, "region": None}
        else:
            if code not in allowed_regions:
                region_list = ", ".join(sorted(allowed_regions))
                raise ValidationError(
                    f"Regional price line {line_number}: unknown region '{code}'. Use one of: {region_list}."
                )
            key = ("region", code)
            geo_row = {"country": None, "region": code}
        if key in seen_scopes:
            raise ValidationError(f"Regional price line {line_number}: {scope} {code} is listed more than once.")
        seen_scopes.add(key)
        geo_row.update(
            {
                "price_cents": _amount_to_minor_units(
                    amount_text, label=f"Regional price line {line_number}"
                ),
                "currency": override_currency,
            }
        )
        geo_prices.append(geo_row)

    return {"price_cents": price_cents, "currency": currency, "geo_prices": geo_prices}


def _format_major_units(amount_cents: int) -> str:
    amount = Decimal(amount_cents) / Decimal("100")
    return format(amount.quantize(Decimal("0.01")).normalize(), "f")


def pricing_fields_for_builder(course: Course) -> dict[str, Any]:
    """Return the active offer's persisted price configuration for course editing."""
    offer = (
        CourseOffer.objects.filter(course=course)
        .select_related("plan")
        .order_by("-is_active", "position", "created_at")
        .first()
    )
    if not offer or not offer.plan_id:
        return {
            "priceAmount": "",
            "priceCurrency": "INR",
            "geoPriceOverrides": "",
            "price": "",
            "priceNote": "Set a course price here. Checkout is enabled only after review and publication.",
        }

    plan = offer.plan
    base = PlanPrice.objects.filter(
        plan=plan, interval=PlanPrice.Interval.ONE_TIME, is_active=True
    ).first()
    overrides = GeoPlanPrice.objects.filter(
        plan=plan, interval=GeoPlanPrice.Interval.ONE_TIME, is_active=True
    ).order_by("country", "region")
    lines = []
    for row in overrides:
        amount = _format_major_units(row.price_cents)
        if row.country:
            lines.append(f"{row.country} {amount} {row.currency}")
        elif row.region:
            lines.append(f"region {row.region} {amount} {row.currency}")
    first_override = overrides.first()
    amount_text = _format_major_units(base.price_cents) if base else ""
    currency = base.currency if base else (first_override.currency if first_override else "INR")
    price = format_price(base.price_cents, currency) if base else ""
    return {
        "priceAmount": amount_text,
        "priceCurrency": currency if currency in SUPPORTED_CURRENCIES else "INR",
        "geoPriceOverrides": "\n".join(lines),
        "price": price,
        "priceNote": "One-time purchase. Existing completed payments retain their recorded amount.",
    }


@transaction.atomic
def sync_course_purchase_offer(course: Course, pricing: dict[str, Any]) -> CourseOffer | None:
    """Apply an approved course's price to the existing one-time commerce system."""
    offer = (
        CourseOffer.objects.select_for_update()
        .filter(course=course)
        .select_related("plan")
        .order_by("position", "created_at")
        .first()
    )
    price_cents = pricing.get("price_cents")
    currency = str(pricing.get("currency") or "INR").upper()
    geo_prices = pricing.get("geo_prices") if isinstance(pricing.get("geo_prices"), list) else []
    has_price = price_cents is not None or bool(geo_prices)
    allowed_access = course.access_type in (Course.AccessType.PAID, Course.AccessType.MIXED)

    if not allowed_access or not has_price:
        if offer:
            offer.is_active = False
            offer.save(update_fields=["is_active", "updated_at"])
            if offer.plan_id:
                PlanPrice.objects.filter(
                    plan_id=offer.plan_id, interval=PlanPrice.Interval.ONE_TIME
                ).update(is_active=False)
                GeoPlanPrice.objects.filter(
                    plan_id=offer.plan_id, interval=GeoPlanPrice.Interval.ONE_TIME
                ).update(is_active=False)
        return offer

    if offer and offer.plan_id and offer.plan is not None:
        plan = offer.plan
    else:
        product_slug = f"course-{course.pk.hex[:32]}"
        product, _ = Product.objects.get_or_create(
            slug=product_slug,
            defaults={
                "name": f"{course.title[:85]} course sales",
                "is_active": True,
                "display_order": 100,
            },
        )
        if not product.is_active:
            product.is_active = True
            product.save(update_fields=["is_active", "updated_at"])
        plan, _ = Plan.objects.get_or_create(
            product=product,
            tier=Plan.Tier.PRO,
            is_trial=False,
            defaults={
                "name": f"{course.title[:72]} purchase",
                "description": f"One-time purchase for {course.title}"[:2000],
                "is_active": True,
                "is_hidden": True,
            },
        )

    # Course checkout plans are deliberately hidden from subscription listings.
    plan_updates = []
    if not plan.is_active:
        plan.is_active = True
        plan_updates.append("is_active")
    if not plan.is_hidden:
        plan.is_hidden = True
        plan_updates.append("is_hidden")
    if plan_updates:
        plan.save(update_fields=plan_updates + ["updated_at"])

    if offer is None:
        offer_slug = f"{slugify(course.slug)[:145]}-{course.pk.hex[:8]}"
        offer = CourseOffer(
            course=course,
            name=f"{course.title[:150]} course offer",
            slug=offer_slug,
            plan=plan,
            is_active=False,
            position=course.position,
        )
    elif offer.plan_id is None:
        offer.plan = plan

    base_rows = PlanPrice.objects.filter(
        plan=plan, interval=PlanPrice.Interval.ONE_TIME
    )
    base_rows.update(is_active=False)
    if price_cents is not None:
        base_price = base_rows.filter(currency=currency).first()
        if base_price:
            base_price.price_cents = int(price_cents)
            base_price.is_active = True
            base_price.save(update_fields=["price_cents", "is_active", "updated_at"])
        else:
            PlanPrice.objects.create(
                plan=plan,
                interval=PlanPrice.Interval.ONE_TIME,
                price_cents=int(price_cents),
                currency=currency,
                is_active=True,
            )

    geo_rows = GeoPlanPrice.objects.filter(
        plan=plan, interval=GeoPlanPrice.Interval.ONE_TIME
    )
    geo_rows.update(is_active=False)
    for item in geo_prices:
        country = item.get("country")
        region = item.get("region")
        query = GeoPlanPrice.objects.filter(
            plan=plan,
            interval=GeoPlanPrice.Interval.ONE_TIME,
            country=country,
            region=region,
        )
        geo_row = query.first()
        if geo_row:
            geo_row.price_cents = int(item["price_cents"])
            geo_row.currency = str(item["currency"]).upper()
            geo_row.is_active = True
            geo_row.save(update_fields=["price_cents", "currency", "is_active", "updated_at"])
        else:
            GeoPlanPrice.objects.create(
                plan=plan,
                interval=GeoPlanPrice.Interval.ONE_TIME,
                price_cents=int(item["price_cents"]),
                currency=str(item["currency"]).upper(),
                country=country,
                region=region,
                is_active=True,
            )

    offer.is_active = True
    offer.name = f"{course.title[:150]} course offer"
    offer.position = course.position
    offer.full_clean()
    offer.save()
    return offer


def resolved_course_offer_price(offer: CourseOffer, request) -> tuple[str, str] | None:
    """Resolve the price for the visitor's market without creating checkout state."""
    if not offer or not offer.is_saleable or not offer.plan_id:
        return None
    try:
        price = resolve_plan_price(offer.plan, PlanPrice.Interval.ONE_TIME, request)
    except PlanPrice.DoesNotExist:
        return None
    return format_price(price.price_cents, price.currency), price.currency
