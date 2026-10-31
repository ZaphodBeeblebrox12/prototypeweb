import base64
import hashlib
import hmac
import json
import time

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.emailing.models import Delivery


@override_settings(RESEND_WEBHOOK_SECRET="whsec_c2VjcmV0X3NpZ25pbmdfa2V5")
class ResendWebhookTests(TestCase):
    def _signed_post(self, event, *, timestamp=None, signature_override=None):
        # Resend now scopes email lifecycle events to recipient(s) in data.to.
        if event.get("type", "").startswith("email.") and isinstance(event.get("data"), dict):
            event["data"].setdefault("to", ["learner@example.com"])
        timestamp = str(timestamp or int(time.time()))
        message_id = "msg_resend_test_001"
        body = json.dumps(event, separators=(",", ":")).encode("utf-8")
        secret = base64.b64decode("c2VjcmV0X3NpZ25pbmdfa2V5")
        signed = (
            message_id.encode("utf-8")
            + b"."
            + timestamp.encode("ascii")
            + b"."
            + body
        )
        signature = base64.b64encode(
            hmac.new(secret, signed, hashlib.sha256).digest()
        ).decode("ascii")
        if signature_override is not None:
            signature = signature_override
        return self.client.post(
            reverse("resend_email_webhook"),
            data=body,
            content_type="application/json",
            HTTP_SVIX_ID=message_id,
            HTTP_SVIX_TIMESTAMP=timestamp,
            HTTP_SVIX_SIGNATURE=f"v1,{signature}",
        )

    def _delivery(self, email_id="re_webhook_test_id"):
        return Delivery.objects.create(
            idempotency_key=f"webhook-test-{email_id}",
            to_email="learner@example.com",
            state=Delivery.State.SENT,
            provider="resend",
            provider_message_id=email_id,
        )

    def test_delivered_event_updates_existing_delivery(self):
        delivery = self._delivery()
        response = self._signed_post({
            "type": "email.delivered",
            "created_at": "2026-10-31T10:00:00.000Z",
            "data": {"email_id": "re_webhook_test_id", "to": ["learner@example.com"]},
        })

        self.assertEqual(response.status_code, 200)
        delivery.refresh_from_db()
        self.assertEqual(delivery.state, Delivery.State.DELIVERED)

    def test_bounced_complained_and_delayed_events_update_state(self):
        cases = [
            ("email.bounced", "re_bounced", Delivery.State.BOUNCED),
            ("email.complained", "re_complained", Delivery.State.COMPLAINED),
            ("email.delivery_delayed", "re_delayed", Delivery.State.DELAYED),
            ("email.failed", "re_failed", Delivery.State.FAILED),
            ("email.suppressed", "re_suppressed", Delivery.State.SUPPRESSED),
        ]
        for event_type, email_id, expected_state in cases:
            with self.subTest(event_type=event_type):
                delivery = self._delivery(email_id)
                response = self._signed_post({
                    "type": event_type,
                    "data": {"email_id": email_id},
                })
                self.assertEqual(response.status_code, 200)
                delivery.refresh_from_db()
                self.assertEqual(delivery.state, expected_state)

    def test_late_sent_event_does_not_downgrade_delivered_state(self):
        delivery = self._delivery()
        delivery.state = Delivery.State.DELIVERED
        delivery.save(update_fields=["state"])

        response = self._signed_post({
            "type": "email.sent",
            "data": {"email_id": "re_webhook_test_id"},
        })

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            "ok": True,
            "updated": 0,
            "ignored": True,
        })
        delivery.refresh_from_db()
        self.assertEqual(delivery.state, Delivery.State.DELIVERED)

    def test_late_delayed_event_does_not_downgrade_delivered_state(self):
        delivery = self._delivery()
        delivery.state = Delivery.State.DELIVERED
        delivery.save(update_fields=["state"])

        response = self._signed_post({
            "type": "email.delivery_delayed",
            "data": {"email_id": "re_webhook_test_id"},
        })

        self.assertEqual(response.status_code, 200)
        delivery.refresh_from_db()
        self.assertEqual(delivery.state, Delivery.State.DELIVERED)

    def test_recipient_scoped_bounce_does_not_mark_other_recipients(self):
        first = Delivery.objects.create(
            idempotency_key="webhook-multi-a",
            to_email="first@example.com",
            state=Delivery.State.SENT,
            provider="resend",
            provider_message_id="re_multi_recipient",
        )
        second = Delivery.objects.create(
            idempotency_key="webhook-multi-b",
            to_email="second@example.com",
            state=Delivery.State.SENT,
            provider="resend",
            provider_message_id="re_multi_recipient",
        )

        response = self._signed_post({
            "type": "email.bounced",
            "data": {
                "email_id": "re_multi_recipient",
                "to": ["first@example.com"],
            },
        })

        self.assertEqual(response.status_code, 200)
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual(first.state, Delivery.State.BOUNCED)
        self.assertEqual(second.state, Delivery.State.SENT)

    def test_missing_recipient_list_is_rejected(self):
        response = self._signed_post({
            "type": "email.delivered",
            "data": {"email_id": "re_not_found"},
        })
        # _signed_post adds the default single recipient for email events.
        self.assertEqual(response.status_code, 503)

    def test_invalid_signature_is_rejected(self):
        self._delivery()
        response = self._signed_post(
            {
                "type": "email.delivered",
                "data": {"email_id": "re_webhook_test_id"},
            },
            signature_override="invalid-signature",
        )
        self.assertEqual(response.status_code, 401)

    def test_stale_timestamp_is_rejected(self):
        self._delivery()
        response = self._signed_post(
            {
                "type": "email.delivered",
                "data": {"email_id": "re_webhook_test_id"},
            },
            timestamp=int(time.time()) - 600,
        )
        self.assertEqual(response.status_code, 401)

    def test_unmatched_email_is_not_acknowledged_so_resend_can_retry(self):
        response = self._signed_post({
            "type": "email.delivered",
            "data": {"email_id": "re_not_recorded_yet"},
        })
        self.assertEqual(response.status_code, 503)

    def test_unhandled_event_is_acknowledged_without_mutation(self):
        delivery = self._delivery()
        response = self._signed_post({
            "type": "contact.created",
            "data": {"id": "contact_123"},
        })
        self.assertEqual(response.status_code, 200)
        delivery.refresh_from_db()
        self.assertEqual(delivery.state, Delivery.State.SENT)

    @override_settings(RESEND_WEBHOOK_SECRET="")
    def test_missing_webhook_secret_fails_closed(self):
        response = self.client.post(
            reverse("resend_email_webhook"),
            data=b'{"type":"email.delivered","data":{"email_id":"x"}}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 503)
