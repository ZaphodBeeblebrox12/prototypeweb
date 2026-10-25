import os
from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import reverse


class PublicFrontDoorTests(SimpleTestCase):
    def test_academy_root_redirects_to_trade_thesis_public_site(self):
        with patch.dict(
            os.environ,
            {"TRADETHESIS_PUBLIC_SITE_URL": "https://tradethesis-public-staging.onrender.com/"},
        ):
            response = self.client.get("/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"], "https://tradethesis-public-staging.onrender.com/"
        )

    def test_invalid_non_https_destination_uses_safe_staging_default(self):
        with patch.dict(os.environ, {"TRADETHESIS_PUBLIC_SITE_URL": "//other-site.invalid/"}):
            response = self.client.get("/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"], "https://tradethesis-public-staging.onrender.com/"
        )
