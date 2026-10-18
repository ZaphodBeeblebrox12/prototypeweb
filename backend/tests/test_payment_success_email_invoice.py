"""Regression tests for invoice identifiers in payment confirmation emails."""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse

from apps.payments.models import Invoice, PaymentIntent
from apps.payments.notifications import notify_payment_succeeded
from apps.subscriptions.models import Plan

User = get_user_model()


class PaymentSuccessEmailInvoiceTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username="invoice-email-learner",
            email="invoice-email-learner@example.test",
            password="test-password-123!",
        )
        self.plan = Plan.objects.create(
            name="Email Test Plan",
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
            status=PaymentIntent.Status.SUCCESS,
            provider_reference="order_test_reference",
            provider_payment_id="pay_test_transaction",
        )

    def test_success_email_includes_invoice_number_link_and_distinct_references(self):
        # Reproduce the production path: fulfilment updates the database row,
        # while the PaymentIntent instance passed to notifications is stale.
        PaymentIntent.objects.filter(pk=self.payment.pk).update(
            status=PaymentIntent.Status.SUCCESS,
        )
        self.assertEqual(self.payment.status, PaymentIntent.Status.PENDING)

        # Keep the test focused on email preparation, not external delivery.
        with patch("apps.payments.notifications._send") as send:
            notify_payment_succeeded(self.payment)

        self.assertEqual(self.payment.status, PaymentIntent.Status.SUCCESS)
        invoice = Invoice.objects.get(payment_intent=self.payment)
        context = send.call_args.args[3]

        self.assertEqual(context["invoice_number"], invoice.invoice_number)
        self.assertTrue(context["invoice_url"])
        self.assertEqual(context["provider_payment_id"], "pay_test_transaction")
        self.assertEqual(context["provider_reference"], "order_test_reference")

        html = render_to_string("payments/email/payment_success_body.html", context)
        plain = render_to_string("payments/email/payment_success_body.txt", context)

        for body in (html, plain):
            with self.subTest(body="html" if body is html else "plain-text"):
                self.assertIn(invoice.invoice_number, body)
                self.assertIn(context["invoice_url"], body)
                self.assertIn("pay_test_transaction", body)
                self.assertIn("order_test_reference", body)

        self.assertIn("Payment transaction ID", html)
        self.assertIn("Order / checkout reference", html)
        self.assertIn("Invoice number", html)

    def test_admin_customer_profile_displays_stable_customer_id(self):
        owner = User.objects.create_superuser(
            username="invoice-email-owner",
            email="invoice-email-owner@example.test",
            password="test-password-123!",
        )
        self.client.force_login(owner)

        response = self.client.get(
            reverse("staff_admin_desk_account_detail", args=[self.customer.pk]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Customer ID")
        self.assertContains(response, str(self.customer.pk))
