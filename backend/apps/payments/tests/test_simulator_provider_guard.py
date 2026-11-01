from types import SimpleNamespace

from django.test import SimpleTestCase

from apps.payments.providers import (
    ProviderConfigurationError,
    create_hosted_checkout,
    verify_provider_payment,
)


class SimulatorProviderGuardTests(SimpleTestCase):
    def setUp(self):
        self.intent = SimpleNamespace(provider="razorpay", is_simulated=True)

    def test_simulator_cannot_create_external_checkout(self):
        with self.assertRaises(ProviderConfigurationError):
            create_hosted_checkout(
                self.intent,
                success_url="https://staging.example/success/",
                cancel_url="https://staging.example/cancel/",
            )

    def test_simulator_cannot_be_verified_against_real_provider(self):
        with self.assertRaises(ProviderConfigurationError):
            verify_provider_payment(self.intent)
