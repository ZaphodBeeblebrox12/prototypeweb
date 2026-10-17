"""The Django service root must defer to the canonical TradeThesis website.

Legacy TradeAdmin pricing is no longer the public landing page. The static
TradeThesis site owns marketing and pricing; Django owns account and learning
routes. Keep this routing contract explicit so obsolete landing-page tests do
not accidentally restore the legacy homepage.
"""
from django.conf import settings
from django.test import TestCase


class PublicSiteRoutingTests(TestCase):
    def test_root_redirects_to_canonical_public_trade_thesis_site(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], f"{settings.PUBLIC_SITE_URL}/")

    def test_health_endpoint_remains_available(self):
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")
