"""Plan feature cards remain data-driven without a Django landing page."""
from django.test import RequestFactory, TestCase

from apps.subscriptions.services.plan_catalogue_pricing import PlanCataloguePricing
from apps.subscriptions.models import Plan, PlanFeature, PlanPrice


class PlanFeatureLandingTests(TestCase):
    def _paid_plan(self, name="Basic"):
        plan = Plan.objects.create(tier=Plan.Tier.BASIC, name=name,
                                   display_order=1)
        PlanPrice.objects.create(plan=plan, interval=PlanPrice.Interval.MONTHLY,
                                 price_cents=2000, currency="USD")
        return plan

    def _card(self, plan, request=None):
        request = request or RequestFactory().get("/")
        tiers = PlanCataloguePricing()._get_tiered_plans(request)
        return next(t for t in tiers if t["plan"].pk == plan.pk)

    def test_db_features_render_in_position_order(self):
        plan = self._paid_plan()
        PlanFeature.objects.create(plan=plan, text="Second", position=2)
        PlanFeature.objects.create(plan=plan, text="First", position=1)
        card = self._card(plan)
        self.assertEqual([f["text"] for f in card["features"]],
                         ["First", "Second"])
        self.assertTrue(all(f["disabled"] is False for f in card["features"]))

    def test_plan_without_features_falls_back_to_tier_defaults(self):
        plan = self._paid_plan()
        card = self._card(plan)
        self.assertEqual(card["features"],
                         PlanCataloguePricing()._get_features_for_tier("basic"))

    def test_db_features_replace_fallback_entirely(self):
        plan = self._paid_plan()
        PlanFeature.objects.create(plan=plan, text="Only real feature",
                                   position=1)
        card = self._card(plan)
        self.assertEqual([f["text"] for f in card["features"]],
                         ["Only real feature"])
