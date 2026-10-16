from django.test import TestCase


class HealthCheckTests(TestCase):
    def test_health_endpoint_returns_plain_ok(self):
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")
        self.assertEqual(response["Content-Type"], "text/plain")
