from decimal import Decimal
from unittest import mock

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.payments.invoicing import calculate_price_breakdown, issue_invoice
from apps.payments.models import BillingSettings, Invoice, PaymentIntent
from apps.subscriptions.models import Plan, PlanPrice


User = get_user_model()


class PriceBreakdownTests(TestCase):
    def setUp(self):
        self.settings = BillingSettings.get_solo()
        self.settings.tax_enabled = False
        self.settings.tax_rate_percentage = Decimal("18.00")
        self.settings.tax_label = "GST"
        self.settings.tax_inclusive = False
        self.settings.save()

    def test_tax_disabled_does_not_change_checkout_amount(self):
        self.settings.tax_enabled = False
        result = calculate_price_breakdown(10000, self.settings)
        self.assertEqual(result["subtotal_cents"], 10000)
        self.assertEqual(result["tax_amount_cents"], 0)
        self.assertEqual(result["total_cents"], 10000)
        self.assertFalse(result["tax_enabled"])

    def test_exclusive_tax_is_added_to_checkout_total(self):
        self.settings.tax_enabled = True
        self.settings.tax_inclusive = False
        result = calculate_price_breakdown(10000, self.settings)
        self.assertEqual(result["subtotal_cents"], 10000)
        self.assertEqual(result["tax_amount_cents"], 1800)
        self.assertEqual(result["total_cents"], 11800)
        self.assertEqual(result["tax_rate_percentage"], Decimal("18.00"))

    def test_inclusive_tax_is_extracted_without_changing_total(self):
        self.settings.tax_enabled = True
        self.settings.tax_inclusive = True
        result = calculate_price_breakdown(11800, self.settings)
        self.assertEqual(result["subtotal_cents"], 10000)
        self.assertEqual(result["tax_amount_cents"], 1800)
        self.assertEqual(result["total_cents"], 11800)


class InvoiceIssueTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="invoice-buyer", email="buyer@example.test", password="test-password"
        )
        EmailAddress.objects.create(
            user=self.user, email=self.user.email, verified=True, primary=True
        )
        self.plan = Plan.objects.create(
            name="Support & Resistance", tier="basic", is_active=True, display_order=1
        )
        self.price = PlanPrice.objects.create(
            plan=self.plan, interval="monthly", price_cents=10000,
            currency="INR", is_active=True,
        )
        self.settings = BillingSettings.get_solo()
        self.settings.seller_name = "TradeThesis"
        self.settings.legal_name = "TradeThesis Learning"
        self.settings.address = "Gurugram, Haryana, India"
        self.settings.country = "IN"
        self.settings.invoice_prefix = "TT"
        self.settings.tax_enabled = False
        self.settings.tax_rate_percentage = Decimal("0.00")
        self.settings.save()

    def make_paid_intent(self):
        return PaymentIntent.objects.create(
            user=self.user,
            plan=self.plan,
            plan_price=self.price,
            base_amount_cents=10000,
            subtotal_cents=10000,
            amount=10000,
            currency="INR",
            provider=PaymentIntent.Provider.RAZORPAY,
            status=PaymentIntent.Status.SUCCESS,
            provider_reference="order_invoice_test",
            provider_payment_id="pay_invoice_test",
        )

    def test_invoice_is_idempotent_and_snapshots_business_details(self):
        intent = self.make_paid_intent()
        first = issue_invoice(intent)
        self.assertIsNotNone(first)
        self.assertTrue(first.invoice_number.startswith("TT-"))
        self.assertEqual(first.total_cents, 10000)
        self.assertEqual(first.seller_legal_name, "TradeThesis Learning")
        self.assertEqual(first.customer_email, "buyer@example.test")

        self.settings.legal_name = "Changed later"
        self.settings.save()
        second = issue_invoice(intent)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(second.seller_legal_name, "TradeThesis Learning")
        self.assertEqual(Invoice.objects.count(), 1)

    def test_invoice_is_not_issued_for_unverified_payment(self):
        intent = self.make_paid_intent()
        intent.status = PaymentIntent.Status.PENDING
        intent.save(update_fields=["status"])
        self.assertIsNone(issue_invoice(intent))
        self.assertEqual(Invoice.objects.count(), 0)

    def test_receipt_only_displays_invoice_to_owning_customer(self):
        intent = self.make_paid_intent()
        issue_invoice(intent)
        self.client.force_login(self.user)
        response = self.client.get(reverse("payment-receipt", args=[intent.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TT-")
        self.assertContains(response, "TradeThesis Learning")

        stranger = User.objects.create_user(username="stranger", password="test-password")
        EmailAddress.objects.create(
            user=stranger, email="stranger@example.test", verified=True, primary=True
        )
        self.client.force_login(stranger)
        response = self.client.get(reverse("payment-receipt", args=[intent.pk]))
        self.assertEqual(response.status_code, 404)

    @mock.patch("apps.payments.views.get_pricing_country", return_value="IN")
    def test_checkout_snapshots_enabled_tax_before_provider_handoff(self, _country):
        self.settings.tax_enabled = True
        self.settings.tax_rate_percentage = Decimal("18.00")
        self.settings.tax_inclusive = False
        self.settings.save()
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("payment-start"),
            {"plan_id": str(self.plan.pk), "interval": "monthly"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        intent = PaymentIntent.objects.get(user=self.user)
        self.assertEqual(intent.subtotal_cents, 10000)
        self.assertEqual(intent.tax_amount_cents, 1800)
        self.assertEqual(intent.amount, 11800)
        self.assertTrue(intent.tax_enabled)
