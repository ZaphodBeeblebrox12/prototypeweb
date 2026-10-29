import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from apps.payments.models import PaymentIntent
from apps.subscriptions.models import GeoPlanPrice, PlanPrice

from .course_pricing import parse_course_pricing, sync_course_purchase_offer
from .models import Course

User = get_user_model()


class CourseBuilderPricingTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="pricing-author",
            password="test-password",
            role="admin",
        )
        self.client.force_login(self.admin)
        self.course = Course.objects.create(
            title="Pricing Test Course",
            slug="pricing-test-course",
            summary="A practical course summary.",
            description="A course description.",
            status=Course.Status.PUBLISHED,
            access_type=Course.AccessType.PAID,
        )

    def test_pricing_parser_normalizes_minor_units_and_geo_overrides(self):
        pricing = parse_course_pricing(
            {
                "priceAmount": "999.50",
                "priceCurrency": "INR",
                "geoPriceOverrides": "IN 499 INR\nregion EU 7.99 EUR\nregion NA 12 USD",
            }
        )

        self.assertEqual(pricing["price_cents"], 99950)
        self.assertEqual(pricing["currency"], "INR")
        self.assertEqual(
            pricing["geo_prices"],
            [
                {"country": "IN", "region": None, "price_cents": 49900, "currency": "INR"},
                {"country": None, "region": "EU", "price_cents": 799, "currency": "EUR"},
                {"country": None, "region": "NA", "price_cents": 1200, "currency": "USD"},
            ],
        )

    def test_pricing_parser_rejects_duplicate_and_invalid_overrides(self):
        with self.assertRaises(ValidationError):
            parse_course_pricing(
                {
                    "priceAmount": "999",
                    "priceCurrency": "INR",
                    "geoPriceOverrides": "IN 499 INR\nIN 399 INR",
                }
            )
        with self.assertRaises(ValidationError):
            parse_course_pricing(
                {"priceAmount": "999", "priceCurrency": "INR", "geoPriceOverrides": "region UNKNOWN 9 USD"}
            )
        with self.assertRaises(ValidationError):
            parse_course_pricing({"priceAmount": "0", "priceCurrency": "INR"})

    def test_published_course_pricing_creates_and_updates_hidden_one_time_offer(self):
        first = parse_course_pricing(
            {"priceAmount": "999", "priceCurrency": "INR", "geoPriceOverrides": "IN 499 INR\nregion EU 7.99 EUR"}
        )
        offer = sync_course_purchase_offer(self.course, first)

        self.assertIsNotNone(offer)
        self.assertTrue(offer.is_active)
        self.assertTrue(offer.is_saleable)
        self.assertTrue(offer.plan.is_hidden)
        self.assertEqual(
            PlanPrice.objects.get(plan=offer.plan, interval=PlanPrice.Interval.ONE_TIME, is_active=True).price_cents,
            99900,
        )
        self.assertEqual(
            GeoPlanPrice.objects.get(
                plan=offer.plan, interval=GeoPlanPrice.Interval.ONE_TIME, country="IN", is_active=True
            ).price_cents,
            49900,
        )
        self.assertEqual(
            GeoPlanPrice.objects.get(
                plan=offer.plan, interval=GeoPlanPrice.Interval.ONE_TIME, region="EU", is_active=True
            ).currency,
            "EUR",
        )

        payment = PaymentIntent.objects.create(
            user=self.admin,
            plan=offer.plan,
            amount=99900,
            currency="INR",
            provider=PaymentIntent.Provider.RAZORPAY,
        )
        second = parse_course_pricing(
            {"priceAmount": "1299.50", "priceCurrency": "INR", "geoPriceOverrides": "IN 699 INR"}
        )
        updated_offer = sync_course_purchase_offer(self.course, second)

        self.assertEqual(updated_offer.pk, offer.pk)
        self.assertEqual(
            PlanPrice.objects.get(plan=offer.plan, interval=PlanPrice.Interval.ONE_TIME, is_active=True).price_cents,
            129950,
        )
        self.assertEqual(
            GeoPlanPrice.objects.get(
                plan=offer.plan, interval=GeoPlanPrice.Interval.ONE_TIME, country="IN", is_active=True
            ).price_cents,
            69900,
        )
        self.assertFalse(
            GeoPlanPrice.objects.filter(
                plan=offer.plan, interval=GeoPlanPrice.Interval.ONE_TIME, region="EU", is_active=True
            ).exists()
        )
        payment.refresh_from_db()
        self.assertEqual(payment.amount, 99900)
        self.assertEqual(payment.currency, "INR")

    def test_non_purchasable_access_model_deactivates_individual_checkout(self):
        offer = sync_course_purchase_offer(
            self.course,
            parse_course_pricing({"priceAmount": "499", "priceCurrency": "INR"}),
        )
        self.assertTrue(offer.is_active)

        self.course.access_type = Course.AccessType.FREE
        self.course.save(update_fields=["access_type", "updated_at"])
        sync_course_purchase_offer(self.course, parse_course_pricing({"priceAmount": "", "priceCurrency": "INR"}))

        offer.refresh_from_db()
        self.assertFalse(offer.is_active)
        self.assertFalse(
            PlanPrice.objects.filter(
                plan=offer.plan, interval=PlanPrice.Interval.ONE_TIME, is_active=True
            ).exists()
        )

    def test_builder_saves_numeric_price_and_published_editor_reloads_commerce_price(self):
        from .course_builder_api import _build_import_payload

        payload, _images = _build_import_payload(
            {
                "title": "Builder Pricing Course",
                "summary": "A practical course summary.",
                "description": "A course description.",
                "accessType": "paid",
                "priceAmount": "799.50",
                "priceCurrency": "INR",
                "geoPriceOverrides": "IN 599 INR",
                "modules": [],
            },
            "builder-pricing-course",
        )
        self.assertEqual(payload["course"]["pricing"]["price_cents"], 79950)
        self.assertEqual(payload["course"]["pricing"]["geo_prices"][0]["price_cents"], 59900)

        sync_course_purchase_offer(
            self.course,
            parse_course_pricing({"priceAmount": "899", "priceCurrency": "INR", "geoPriceOverrides": "IN 699 INR"}),
        )
        response = self.client.post(
            reverse("staff_course_builder_api"),
            data=json.dumps({"action": "begin_edit_published_course", "courseId": str(self.course.pk)}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        state = response.json()["course"]
        self.assertEqual(state["priceAmount"], "899")
        self.assertEqual(state["priceCurrency"], "INR")
        self.assertEqual(state["geoPriceOverrides"], "IN 699 INR")

    def test_builder_exposes_real_pricing_fields(self):
        response = self.client.get(reverse("staff_course_builder_preview"))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, 'id="coursePriceAmount"')
        self.assertContains(response, 'id="coursePriceCurrency"')
        self.assertContains(response, 'id="courseGeoPriceOverrides"')
        self.assertContains(response, "Country and regional prices")
        self.assertNotContains(response, "Display text only. It does not create or activate checkout.")
