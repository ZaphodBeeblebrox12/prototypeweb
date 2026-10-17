"""Regression tests for authentication page rendering and cache headers."""
from django.test import TestCase


class AuthPageCacheHeadersTest(TestCase):
    def assert_auth_page_not_cached(self, path):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        cache_control = response.headers.get("Cache-Control", "").lower()
        self.assertIn("no-store", cache_control)
        self.assertIn("no-cache", cache_control)
        self.assertIn("private", cache_control)

    def test_login_page_is_not_cached(self):
        self.assert_auth_page_not_cached("/accounts/login/")

    def test_signup_page_is_not_cached(self):
        self.assert_auth_page_not_cached("/accounts/signup/")
