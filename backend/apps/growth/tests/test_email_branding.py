"""Regression tests for TradeThesis-branded gift invitation emails."""
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase
from django.template.loader import render_to_string
from django.utils import timezone

from apps.growth.services.gifts import GiftEmailService, GiftService


class GiftInvitationBrandingTests(SimpleTestCase):
    def _template_context(self):
        return {
            "sender_name": "Asha",
            "plan_name": "Foundations",
            "duration_days": 30,
            "message": "Enjoy the course.",
            "claim_url": "https://academy.example.test/gifts/claim/token/",
            "expires_at": timezone.now() + timedelta(days=30),
            "logo_url": "https://cdn.example.test/tradethesis-logo.png",
            "dashboard_url": "https://academy.example.test/dashboard/",
            "support_url": "https://academy.example.test/support/",
        }

    def test_gift_invitation_uses_the_shared_branded_template_family(self):
        sender = SimpleNamespace(
            nickname="", first_name="Asha", username="asha",
            email="asha@example.test",
        )
        gift_subscription = SimpleNamespace(
            id="gift-subscription-test",
            from_user=sender,
            plan=SimpleNamespace(name="Foundations"),
            duration_days=30,
            message="Enjoy the course.",
        )
        invite = SimpleNamespace(
            id="gift-invite-test",
            recipient_email="learner@example.test",
            expires_at=timezone.now() + timedelta(days=30),
            gift_subscription=gift_subscription,
        )

        with (
            patch("apps.notifications.services.NotificationService.send_email") as send,
            patch.object(GiftService, "record_email_sent"),
        ):
            self.assertTrue(GiftEmailService.send_gift_email(
                invite, "https://academy.example.test/gifts/claim/token/"
            ))

        send.assert_called_once()
        self.assertEqual(
            send.call_args.kwargs["template"],
            "growth/email/gift_invite",
        )

    def test_active_and_legacy_gift_invite_templates_both_render_trade_thesis_branding(self):
        context = self._template_context()

        active_html = render_to_string("growth/email/gift_invite_body.html", context)
        legacy_html = render_to_string("growth/gift_invite_body.html", context)

        for html in (active_html, legacy_html):
            self.assertIn("TradeThesis", html)
            self.assertIn("tradethesis-logo.png", html)
            self.assertIn("Claim your gift", html)
            self.assertIn("cdn.example.test", html)
            self.assertNotIn("You've Received a Gift!", html)
