"""P1: hosted-checkout purchase flow (providers mocked; no live calls).

NOTE (chargeback implementation): the flow is now CONSENT-FIRST.
payment_start only creates the PaymentIntent and returns consent_url.
The provider session is created on the consent step (POST agree), which
records the write-once CheckoutEvidence BEFORE any money moves. These
tests exercise exactly that sequence.
"""
import datetime
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.payments import providers
from apps.payments.models import PaymentIntent
from apps.academy.models import Course, CourseOffer
from apps.subscriptions.models import (
    Plan, PlanPrice, Subscription, SubscriptionHistory)


def _ensure_checkout_test_policies():
    """Publish clearly test-only non-placeholder policy versions for consent tests."""
    from django.utils import timezone
    from apps.policies.models import PolicyVersion
    from apps.policies.services import (
        CHECKOUT_POLICY_TYPES, is_placeholder_policy, publish,
    )

    titles = dict(PolicyVersion.PolicyType.choices)
    for policy_type in CHECKOUT_POLICY_TYPES:
        active = PolicyVersion.active(policy_type)
        if active is not None and not is_placeholder_policy(active):
            continue
        test_version = PolicyVersion.objects.create(
            policy_type=policy_type,
            version="test-2.0",
            title=titles[policy_type],
            content_html=(
                f"<p>Automated test policy for {policy_type}. "
                "Not production legal copy.</p>"
            ),
            status=PolicyVersion.Status.DRAFT,
            effective_from=timezone.now(),
        )
        publish(test_version)

User = get_user_model()


def make_plan(interval="monthly", price_cents=999, currency="USD"):
    plan = Plan.objects.create(
        name=f"Pro-{interval}", tier=f"pro-{interval}",
        description="d", display_order=1, is_active=True)
    pp = PlanPrice.objects.create(
        plan=plan, interval=interval, price_cents=price_cents, currency=currency)
    return plan, pp


def _post_test_consent(client, intent):
    _ensure_checkout_test_policies()
    return client.post(
        reverse("checkout-consent", args=[intent.id]), {"agree": "on"})


@mock.patch("apps.payments.views.providers")
@mock.patch("apps.payments.views.get_pricing_country", return_value="US")
class StripeCheckoutBillingDisclosureTests(TestCase):
    @override_settings(STRIPE_SECRET_KEY="sk_test_checkout_mode")
    @mock.patch("stripe.checkout.Session.create")
    def test_stripe_session_is_single_charge_and_labels_fixed_access(self, create_session):
        user = User.objects.create_user(username="stripe-buyer", password="pw")
        plan, price = make_plan("monthly", price_cents=999, currency="USD")
        intent = PaymentIntent.objects.create(
            user=user,
            plan=plan,
            plan_price=price,
            amount=price.price_cents,
            currency=price.currency,
            provider="stripe",
            status=PaymentIntent.Status.PENDING,
        )
        create_session.return_value = {
            "id": "cs_test_one_time",
            "url": "https://checkout.stripe.com/test",
        }

        providers.create_stripe_checkout(
            intent,
            success_url="https://example.com/confirm/",
            cancel_url="https://example.com/cancel/",
        )

        kwargs = create_session.call_args.kwargs
        self.assertEqual(kwargs["mode"], "payment")
        product = kwargs["line_items"][0]["price_data"]["product_data"]
        self.assertIn("One-time payment for 30 days", product["description"])
        self.assertIn("no automatic renewal", product["description"])


@mock.patch("apps.payments.views.providers")
@mock.patch("apps.payments.views.get_pricing_country", return_value="US")
class PurchaseFlowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pw")
        self.client.force_authenticate(self.user)

    def _start(self, plan_id, interval):
        return self.client.post(reverse("payment-start"), {
            "plan_id": str(plan_id), "interval": interval}, format="json")

    def _consent(self, intent):
        """The agreement moment: ONE checkbox -> evidence -> provider handoff."""
        return _post_test_consent(self.client, intent)

    def _confirm(self, intent_id):
        return self.client.post(reverse("payment-confirm"), {
            "payment_intent_id": str(intent_id)}, format="json")

    def _saleable_course_offer(self, slug="trading-path"):
        course = Course.objects.create(
            title="TradeThesis Trading Path", slug=slug,
            status=Course.Status.PUBLISHED,
        )
        plan, _price = make_plan("one_time", price_cents=99900, currency="INR")
        plan.is_hidden = True
        plan.save(update_fields=["is_hidden"])
        return CourseOffer.objects.create(
            course=course, name="TradeThesis Trading Path", slug=slug,
            plan=plan, is_active=True, access_duration_days=None,
        )

    def test_course_purchase_page_requires_saleable_offer_and_has_no_side_effect(self, _geo, prov):
        self.client.force_login(self.user)
        unavailable = self.client.get(reverse(
            "course-purchase-start", kwargs={"offer_slug": "not-published"}))
        self.assertEqual(unavailable.status_code, 404)
        self.assertContains(unavailable, "not available yet", status_code=404)
        self.assertEqual(PaymentIntent.objects.count(), 0)

        offer = self._saleable_course_offer()
        response = self.client.get(reverse(
            "course-purchase-start", kwargs={"offer_slug": offer.slug}))
        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, "TradeThesis Trading Path")
        self.assertContains(response, "one-time payment")
        self.assertContains(response, "Lifetime course access")
        self.assertContains(response, "₹999")
        self.assertEqual(PaymentIntent.objects.count(), 0)

    def test_course_offer_payment_start_resolves_one_time_product(self, _geo, prov):
        offer = self._saleable_course_offer()
        response = self.client.get(reverse("payment-start"), {
            "plan_id": str(offer.plan_id), "interval": "one_time",
        })
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["product_type"], "course")
        self.assertEqual(response.data["course_slug"], "trading-path")
        self.assertTrue(response.data["consent_url"].startswith("/checkout/consent/"))
        intent = PaymentIntent.objects.get()
        self.assertEqual(intent.plan_price.interval, "one_time")
        self.assertEqual(intent.amount, 99900)
        self.assertEqual(intent.provider_reference, "")

    def test_monthly_checkout_discloses_one_time_charge_and_fixed_access(self, _geo, prov):
        plan, _ = make_plan("monthly")
        started = self._start(plan.id, "monthly")
        self.assertEqual(started.status_code, 200, started.data)
        intent = PaymentIntent.objects.get()
        response = self.client.get(reverse("checkout-consent", args=[intent.id]))

        self.assertContains(response, "One-time payment for 30 days of access")
        self.assertContains(response, "No automatic renewal")

    def test_trial_conversion_plan_is_rejected_by_paid_checkout(self, _geo, prov):
        plan, _ = make_plan("monthly")
        plan.is_trial = True
        plan.trial_duration_days = 7
        plan.save(update_fields=["is_trial", "trial_duration_days"])

        response = self._start(plan.id, "monthly")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Trial-to-renewal checkout is disabled", response.data["detail"])
        self.assertFalse(PaymentIntent.objects.filter(plan=plan).exists())
        prov.create_hosted_checkout.assert_not_called()

    def test_legacy_trial_intent_cannot_reach_provider_checkout(self, _geo, prov):
        plan, price = make_plan("monthly")
        plan.is_trial = True
        plan.trial_duration_days = 7
        plan.save(update_fields=["is_trial", "trial_duration_days"])
        intent = PaymentIntent.objects.create(
            user=self.user,
            plan=plan,
            plan_price=price,
            amount=price.price_cents,
            currency=price.currency,
            provider="stripe",
            provider_reference="cs_legacy_trial",
            status=PaymentIntent.Status.PENDING,
        )

        response = self.client.get(reverse("checkout-page", args=[intent.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Trial-to-renewal checkout is disabled")
        prov.get_stripe_checkout_url.assert_not_called()

    def test_checkout_refuses_placeholder_policy_content(self, _geo, prov):
        plan, _ = make_plan("monthly")
        self._start(plan.id, "monthly")
        intent = PaymentIntent.objects.get()

        response = self.client.post(
            reverse("checkout-consent", args=[intent.id]), {"agree": "on"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "launch placeholders")
        prov.create_hosted_checkout.assert_not_called()
        intent.refresh_from_db()
        self.assertEqual(intent.provider_reference, "")

    def test_monthly_purchase_expires_in_30_days(self, _geo, prov):
        plan, _ = make_plan("monthly")
        prov.create_hosted_checkout.return_value = providers.CreatedCheckout(
            provider_reference="cs_test_123", checkout_url="https://pay.example")
        prov.verify_provider_payment.return_value = True
        r = self._start(plan.id, "monthly")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertIn("consent_url", r.data)          # consent-first handoff
        intent = PaymentIntent.objects.get()
        self.assertEqual(intent.provider_reference, "")  # provider NOT called yet
        c = self._consent(intent)
        self.assertEqual(c.status_code, 302)           # -> checkout bridge
        intent.refresh_from_db()
        self.assertEqual(intent.provider_reference, "cs_test_123")
        self.assertEqual(intent.plan_price.interval, "monthly")
        # Evidence captured BEFORE provider handoff:
        self.assertTrue(hasattr(intent, "checkout_evidence"))
        from apps.policies.models import PolicyAcceptance
        self.assertEqual(PolicyAcceptance.objects.filter(
            user=self.user, checkout_evidence__payment_intent=intent
        ).count(), 3)  # terms + refund&cancellation + risk disclosure
        c2 = self._confirm(intent.id)
        self.assertEqual(c2.data["status"], "success")
        sub = Subscription.objects.get(user=self.user)
        self.assertEqual((sub.expires_at - sub.started_at).days, 30)
        self.assertEqual(sub.price_cents, intent.amount)
        self.assertEqual(sub.payment_provider, intent.provider)
        self.assertTrue(SubscriptionHistory.objects.filter(
            subscription=sub, event_type=SubscriptionHistory.EventType.CREATED).exists())

    def test_quarterly_purchase_expires_in_90_days(self, _geo, prov):
        plan, _ = make_plan("quarterly", 2499)
        prov.create_hosted_checkout.return_value = providers.CreatedCheckout(
            provider_reference="cs_q", checkout_url="https://pay.example")
        prov.verify_provider_payment.return_value = True
        self._start(plan.id, "quarterly")
        intent = PaymentIntent.objects.get()
        self.assertEqual(intent.amount, 2499)
        self._consent(intent)
        c = self._confirm(intent.id)
        self.assertEqual(c.data["status"], "success")
        self.assertEqual((Subscription.objects.get().expires_at
                          - Subscription.objects.get().started_at).days, 90)

    def test_yearly_purchase_expires_in_365_days(self, _geo, prov):
        plan, _ = make_plan("yearly", 7999)
        prov.create_hosted_checkout.return_value = providers.CreatedCheckout(
            provider_reference="cs_y", checkout_url="https://pay.example")
        prov.verify_provider_payment.return_value = True
        self._start(plan.id, "yearly")
        intent = PaymentIntent.objects.get()
        self._consent(intent)
        c = self._confirm(intent.id)
        self.assertEqual(c.data["status"], "success")
        self.assertEqual((Subscription.objects.get().expires_at
                          - Subscription.objects.get().started_at).days, 365)

    def test_stripe_routing_and_snapshot_amount(self, _geo, prov):
        plan, pp = make_plan("monthly", 999, "USD")
        prov.create_hosted_checkout.return_value = providers.CreatedCheckout(
            provider_reference="cs_us", checkout_url="https://pay.example")
        self._start(plan.id, "monthly")
        intent = PaymentIntent.objects.get()
        self.assertEqual(intent.provider, "stripe")
        self._consent(intent)
        kwargs = prov.create_hosted_checkout.call_args
        self.assertEqual(kwargs[0][0].amount, pp.price_cents)
        self.assertEqual(kwargs[0][0].currency, "USD")

    def test_razorpay_routing_for_india(self, geo, prov):
        geo.return_value = "IN"
        plan, _ = make_plan("monthly", 99900, "INR")
        prov.create_hosted_checkout.return_value = providers.CreatedCheckout(
            provider_reference="order_in", checkout_url=None)
        self._start(plan.id, "monthly")
        intent = PaymentIntent.objects.get()
        self.assertEqual(intent.provider, "razorpay")
        self.assertEqual(intent.provider_reference, "")
        self._consent(intent)
        intent.refresh_from_db()
        self.assertEqual(intent.provider_reference, "order_in")

    def test_razorpay_checkout_offers_upi_and_prefills_customer(self, geo, prov):
        """India's Razorpay checkout should leave UPI available with other methods."""
        geo.return_value = "IN"
        self.user.email = "buyer@example.test"
        self.user.first_name = "Asha"
        self.user.last_name = "Buyer"
        self.user.save(update_fields=["email", "first_name", "last_name"])
        plan, _ = make_plan("monthly", 99900, "INR")
        prov.create_hosted_checkout.return_value = providers.CreatedCheckout(
            provider_reference="order_upi_test", checkout_url=None)

        started = self._start(plan.id, "monthly")
        self.assertEqual(started.status_code, 200, started.data)
        intent = PaymentIntent.objects.get(user=self.user)
        consent = self._consent(intent)
        self.assertEqual(consent.status_code, 302)
        response = self.client.get(reverse("checkout-page", args=[intent.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Choose UPI or another payment method")
        self.assertContains(response, "Choose UPI, a supported UPI app or ID")
        self.assertContains(response, 'name: "Asha Buyer"')
        self.assertContains(response, 'email: "buyer@example.test"')
        self.assertContains(response, 'order_id: "order_upi_test"')
        # No checkout method allow-list is passed, so Razorpay can show every
        # payment type enabled in the merchant dashboard, including UPI.
        self.assertNotContains(response, "method:")

    def test_failed_verification_does_not_activate(self, _geo, prov):
        plan, _ = make_plan()
        prov.create_hosted_checkout.return_value = providers.CreatedCheckout(
            provider_reference="cs_f", checkout_url="https://pay.example")
        prov.verify_provider_payment.return_value = False
        self._start(plan.id, "monthly")
        intent = PaymentIntent.objects.get()
        self._consent(intent)
        c = self._confirm(intent.id)
        self.assertEqual(c.data["status"], "failed")
        self.assertFalse(Subscription.objects.exists())
        self.assertEqual(PaymentIntent.objects.get().status,
                         PaymentIntent.Status.FAILED)

    def test_pending_verification_does_not_activate(self, _geo, prov):
        plan, _ = make_plan()
        prov.create_hosted_checkout.return_value = providers.CreatedCheckout(
            provider_reference="cs_p", checkout_url="https://pay.example")
        prov.verify_provider_payment.return_value = None
        self._start(plan.id, "monthly")
        intent = PaymentIntent.objects.get()
        self._consent(intent)
        c = self._confirm(intent.id)
        self.assertEqual(c.data["status"], "pending")
        self.assertFalse(Subscription.objects.exists())
        self.assertEqual(PaymentIntent.objects.get().status,
                         PaymentIntent.Status.PENDING)

    def test_repeated_confirmation_creates_one_subscription(self, _geo, prov):
        plan, _ = make_plan()
        prov.create_hosted_checkout.return_value = providers.CreatedCheckout(
            provider_reference="cs_r", checkout_url="https://pay.example")
        prov.verify_provider_payment.return_value = True
        self._start(plan.id, "monthly")
        intent = PaymentIntent.objects.get()
        self._consent(intent)
        intent_id = intent.id
        first = self._confirm(intent_id)
        second = self._confirm(intent_id)
        self.assertEqual(first.data["status"], "success")
        self.assertEqual(second.data["status"], "success")
        self.assertTrue(second.data.get("already_processed"))
        self.assertEqual(Subscription.objects.count(), 1)
        self.assertEqual(SubscriptionHistory.objects.count(), 1)

    def test_checkout_page_renders(self, _geo, prov):
        plan, _ = make_plan()
        prov.create_hosted_checkout.return_value = providers.CreatedCheckout(
            provider_reference="cs_c", checkout_url="https://pay.example")
        prov.get_stripe_checkout_url.return_value = "https://pay.example"
        self._start(plan.id, "monthly")
        intent = PaymentIntent.objects.get()
        # Evidence-first: the bridge redirects to consent until the agreement
        # moment is captured.
        r = self.client.get(reverse("checkout-page", args=[intent.id]))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("checkout-consent", args=[intent.id]),
                      r["Location"])
        self._consent(intent)
        r = self.client.get(reverse("checkout-page", args=[intent.id]))
        self.assertEqual(r.status_code, 200)

    def test_confirm_page_success(self, _geo, prov):
        plan, _ = make_plan()
        prov.create_hosted_checkout.return_value = providers.CreatedCheckout(
            provider_reference="cs_cp", checkout_url="https://pay.example")
        prov.verify_provider_payment.return_value = True
        self._start(plan.id, "monthly")
        intent = PaymentIntent.objects.get()
        r = self.client.get(reverse("confirm-page", args=[intent.id]))
        self.assertEqual(r.status_code, 200)
        intent.refresh_from_db()
        self.assertEqual(intent.status, PaymentIntent.Status.SUCCESS)

    def test_provider_error_at_consent_keeps_intent_and_shows_error(self, _geo, prov):
        """Provider failure now happens on the consent step, not at start.
        The intent stays PENDING (retryable) and the user sees the error."""
        plan, _ = make_plan()
        from apps.payments import providers as real_providers
        prov.ProviderError = real_providers.ProviderError
        prov.create_hosted_checkout.side_effect = real_providers.ProviderError("down")
        r = self._start(plan.id, "monthly")
        self.assertEqual(r.status_code, 200, r.data)   # start itself succeeds
        intent = PaymentIntent.objects.get()
        c = self._consent(intent)
        self.assertEqual(c.status_code, 200)           # consent re-rendered w/ error
        self.assertIn(b"Payment provider error", c.content)
        intent.refresh_from_db()
        self.assertEqual(intent.status, PaymentIntent.Status.PENDING)
        # Retry succeeds once provider recovers:
        prov.create_hosted_checkout.side_effect = None
        prov.create_hosted_checkout.return_value = providers.CreatedCheckout(
            provider_reference="cs_retry", checkout_url="https://pay.example")
        c2 = self._consent(intent)
        self.assertEqual(c2.status_code, 302)
        intent.refresh_from_db()
        self.assertEqual(intent.provider_reference, "cs_retry")


@mock.patch("apps.subscriptions.views.get_pricing_country", return_value="US")
@mock.patch("apps.subscriptions.services.get_pricing_country", return_value="US")
class PurchaseBypassTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bp", password="pw")
        self.client.force_authenticate(self.user)

    def test_paid_purchase_routes_to_payment_flow(self, _sgeo, _vgeo):
        plan, _ = make_plan("monthly")
        r = self.client.post(reverse("subscriptions:purchase-plan"), {"plan_id": str(plan.id)},
                             format="json")
        self.assertEqual(r.status_code, 402)
        self.assertTrue(r.data["requires_payment"])
        self.assertEqual(r.data["payment_start_url"], reverse("payment-start"))
        self.assertFalse(Subscription.objects.exists())

    def test_trial_purchase_still_activates(self, _sgeo, _vgeo):
        plan = Plan.objects.create(
            name="Trial-bypass", tier="trial-bypass", is_trial=True,
            trial_duration_days=7,
            description="t", display_order=2, is_active=True)
        from apps.subscriptions.models import GeoPlanPrice
        GeoPlanPrice.objects.create(
            plan=plan, country="US", price_cents=0, currency="USD",
            is_active=True, interval="monthly")
        r = self.client.post(reverse("subscriptions:purchase-plan"), {"plan_id": str(plan.id)},
                             format="json")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertTrue(Subscription.objects.filter(user=self.user, is_trial=True).exists())

    def test_paid_direct_service_call_raises(self, _sgeo, _vgeo):
        from apps.subscriptions.services import purchase_plan
        from django.core.exceptions import PermissionDenied
        plan, _ = make_plan("monthly")
        with self.assertRaises(PermissionDenied):
            purchase_plan(self.user, plan)
        self.assertFalse(Subscription.objects.exists())


@mock.patch("apps.payments.views.providers")
@mock.patch("apps.payments.views.get_pricing_country", return_value="US")
class CtaFlowTests(APITestCase):
    """Landing CTA: plan + selected interval must reach payment_start."""

    def setUp(self):
        self.user = User.objects.create_user(username="cta", password="pw")
        self.client.force_authenticate(self.user)

    def _consent(self, intent):
        return _post_test_consent(self.client, intent)

    def test_get_start_carries_plan_and_interval(self, _geo, prov):
        plan, _ = make_plan("quarterly")
        prov.create_hosted_checkout.return_value = providers.CreatedCheckout(
            provider_reference="cs_cta", checkout_url="https://pay.example")
        r = self.client.get(reverse("payment-start"),
                            {"plan_id": str(plan.id), "interval": "quarterly"})
        self.assertEqual(r.status_code, 200, r.data)
        intent = PaymentIntent.objects.get()
        self.assertEqual(intent.plan_price.interval, "quarterly")
        self.assertEqual(intent.provider_reference, "")  # consent-first
        self._consent(intent)
        intent.refresh_from_db()
        self.assertEqual(intent.provider_reference, "cs_cta")

    def test_get_start_defaults_to_monthly(self, _geo, prov):
        plan, _ = make_plan("monthly")
        prov.create_hosted_checkout.return_value = providers.CreatedCheckout(
            provider_reference="cs_m", checkout_url="https://pay.example")
        r = self.client.get(reverse("payment-start"), {"plan_id": str(plan.id)})
        self.assertEqual(r.status_code, 200, r.data)
        intent = PaymentIntent.objects.get()
        self.assertEqual(intent.plan_price.interval, "monthly")
        self._consent(intent)
        intent.refresh_from_db()
        self.assertEqual(intent.provider_reference, "cs_m")

    def test_get_start_without_plan_id_is_400(self, _geo, prov):
        r = self.client.get(reverse("payment-start"))
        self.assertEqual(r.status_code, 400)
