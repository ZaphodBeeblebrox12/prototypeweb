from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class DashboardSeparationTests(TestCase):
    def test_learner_and_admin_dashboards_have_separate_audiences(self):
        learner = User.objects.create_user(username="dashboard_learner")
        self.client.force_login(learner)

        learning = self.client.get(reverse("academy:home"))
        self.assertEqual(learning.status_code, 200)
        self.assertContains(learning, "Your TradeThesis desk")
        self.assertNotContains(learning, "Operational overview")

        account = self.client.get(reverse("dashboard"))
        self.assertEqual(account.status_code, 200)
        self.assertContains(account, "Account Status")
        self.assertNotContains(account, "Operational overview")

        admin_as_learner = self.client.get(reverse("admin:index"))
        self.assertIn(admin_as_learner.status_code, (302, 403))

        staff = User.objects.create_user(username="dashboard_admin")
        staff.is_staff = True
        staff.is_superuser = True
        staff.set_password("test-only-password")
        staff.save()
        self.client.force_login(staff)

        admin = self.client.get(reverse("admin:index"))
        self.assertEqual(admin.status_code, 200)
        self.assertContains(admin, "Operational overview")
        self.assertNotContains(admin, "Your TradeThesis desk")
