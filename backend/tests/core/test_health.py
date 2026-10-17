"""Regression tests for the public Render health/readiness endpoint."""

from django.test import TestCase


class HealthCheckTests(TestCase):
    def test_health_check_returns_ok_when_database_is_available(self):
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
