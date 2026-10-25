"""Tests for normalizing and displaying provider-reported payment methods."""
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from apps.payments.models import PaymentIntent
from apps.payments.notifications import _capture_payment_method
from apps.payments.providers import fetch_payment_method, normalize_payment_method
from apps.subscriptions.models import Plan

User = get_user_model()


class NormalizePaymentMethodTests(SimpleTestCase):
    def test_known_provider_types_map_to_clear_labels(self):
        cases = {
            "card": "card",
            "upi": "upi",
            "netbanking": "netbanking",
            "net banking": "netbanking",
            "wallet": "wallet",
            "cardless_emi": "emi",
            "paylater": "pay_later",
            "bank_transfer": "bank_transfer",
            "sepa_debit": "bank_debit",
            "ideal": "bank_redirect",
            "some_future_method": "other",
            "": "",
            None: "",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(normalize_payment_method(raw), expected)

    def test_wallet_used_through_card_is_recorded_as_wallet(self):
        details = {"card": {"wallet": {"type": "google_pay"}}}
        self.assertEqual(normalize_payment_method("card", details), "wallet")


class ProviderPaymentMethodTests(SimpleTestCase):
    @patch("apps.payments.providers._razorpay_client")
    def test_razorpay_uses_captured_payment_not_failed_retry(self, client_factory):
        client = Mock()
        client.order.payments.return_value = {"items": [
            {"status": "failed", "method": "card", "created_at": 100},
            {"status": "captured", "method": "upi", "created_at": 200},
        ]}
        client_factory.return_value = client
        intent = SimpleNamespace(
            provider=PaymentIntent.Provider.RAZORPAY,
            provider_reference="order_test_123",
        )

        self.assertEqual(fetch_payment_method(intent), "upi")
        client.order.payments.assert_called_once_with("order_test_123")

    @patch("apps.payments.providers._stripe")
    def test_stripe_reads_actual_charge_payment_method(self, stripe_factory):
        stripe = Mock()
        stripe.checkout.Session.retrieve.return_value = {
            "payment_intent": "pi_test_123",
        }
        charges = Mock()
        charges.auto_paging_iter.return_value = iter([{
            "paid": True,
            "payment_method_details": {"type": "upi"},
        }])
        stripe.Charge.list.return_value = charges
        stripe_factory.return_value = stripe
        intent = SimpleNamespace(
            provider=PaymentIntent.Provider.STRIPE,
            provider_reference="cs_test_123",
        )

        self.assertEqual(fetch_payment_method(intent), "upi")
        stripe.Charge.list.assert_called_once_with(
            payment_intent="pi_test_123", limit=10,
        )


class PaymentMethodPersistenceTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username="payment-method-learner",
            email="payment-method-learner@example.test",
            password="test-password-123!",
        )
        self.plan = Plan.objects.create(
            name="Payment Method Plan",
            tier=Plan.Tier.BASIC,
            is_active=True,
        )
        self.payment = PaymentIntent.objects.create(
            user=self.customer,
            plan=self.plan,
            amount=99900,
            subtotal_cents=99900,
            currency="INR",
            provider=PaymentIntent.Provider.RAZORPAY,
            provider_reference="order_test_method",
            status=PaymentIntent.Status.SUCCESS,
        )

    @patch("apps.payments.providers.fetch_payment_method", return_value="netbanking")
    def test_successful_payment_persists_provider_method(self, fetch):
        _capture_payment_method(self.payment)

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.payment_method, "netbanking")
        fetch.assert_called_once_with(self.payment)

    @patch("apps.payments.providers.fetch_payment_method", side_effect=RuntimeError("provider unavailable"))
    def test_method_lookup_failure_does_not_fail_payment_processing(self, fetch):
        _capture_payment_method(self.payment)

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, PaymentIntent.Status.SUCCESS)
        self.assertEqual(self.payment.payment_method, "")
        fetch.assert_called_once_with(self.payment)

    @patch("apps.payments.providers.fetch_payment_method")
    def test_already_recorded_method_is_not_looked_up_again(self, fetch):
        self.payment.payment_method = PaymentIntent.PaymentMethod.UPI
        self.payment.save(update_fields=["payment_method"])

        _capture_payment_method(self.payment)

        fetch.assert_not_called()

    def test_customer_profile_displays_method_separately_from_provider(self):
        owner = User.objects.create_superuser(
            username="payment-method-owner",
            email="payment-method-owner@example.test",
            password="test-password-123!",
        )
        self.payment.payment_method = PaymentIntent.PaymentMethod.UPI
        self.payment.save(update_fields=["payment_method"])
        self.client.force_login(owner)

        response = self.client.get(
            reverse("staff_admin_desk_account_detail", args=[self.customer.pk]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "UPI")
        self.assertContains(response, "Razorpay")
        self.assertContains(response, "Payment method")
