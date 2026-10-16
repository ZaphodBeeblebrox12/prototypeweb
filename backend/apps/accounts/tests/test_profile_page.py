from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import UserPreference
from apps.bot_integration.models import DiscordAccount, TelegramAccount

User = get_user_model()


class ProfilePageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="profile-learner",
            email="profile@example.test",
            password="test-password-123!",
        )
        EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            primary=True,
            verified=True,
        )
        self.client.force_login(self.user)

    def test_profile_uses_member_area_layout_and_exposes_account_controls(self):
        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account &amp; security")
        self.assertContains(response, "Personal details")
        self.assertContains(response, "Community connections")
        self.assertContains(response, "Change password")
        self.assertContains(response, "Connect Telegram")
        self.assertContains(response, "Connect Discord")
        self.assertContains(response, 'name="timezone"')
        self.assertContains(response, 'name="language"')

    def test_connection_status_uses_active_bot_link_records(self):
        TelegramAccount.objects.create(
            user=self.user,
            chat_id=7654321,
            telegram_user_id=7654321,
            username="chartlearner",
        )
        DiscordAccount.objects.create(
            user=self.user,
            discord_user_id="discord-profile-123",
            username="chart-learner",
        )

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Connected · @chartlearner")
        self.assertContains(response, "Connected · chart-learner")
        self.assertContains(response, "Disconnect Telegram")
        self.assertContains(response, "Disconnect")
        self.assertNotContains(response, "Connect Telegram")
        self.assertNotContains(response, "Connect Discord")

    def test_profile_update_persists_personal_details_and_preferences(self):
        response = self.client.post(
            reverse("profile"),
            {
                "first_name": "Course",
                "last_name": "Learner",
                "email": "learner@example.test",
                "bio": "Learning to build a repeatable process.",
                "timezone": "Asia/Kolkata",
                "language": "en",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Course")
        self.assertEqual(self.user.last_name, "Learner")
        self.assertEqual(self.user.email, "learner@example.test")
        self.assertEqual(self.user.bio, "Learning to build a repeatable process.")

        preferences = UserPreference.objects.get(user=self.user)
        self.assertEqual(preferences.timezone, "Asia/Kolkata")
        self.assertEqual(preferences.language, "en")
