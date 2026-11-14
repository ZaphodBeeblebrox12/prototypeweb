"""Permission tests for staff-only Growth administration pages."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from apps.growth.models import GiftInvite

User = get_user_model()


def make_user(username, *, is_staff=False, role=None):
    user = User.objects.create_user(username=username, password="pw")
    user.is_staff = is_staff
    if role is not None:
        user.role = role
    user.save(update_fields=["is_staff", "role"])
    return user


def grant(user, model, *codenames):
    content_type = ContentType.objects.get_for_model(model)
    permissions = list(
        Permission.objects.filter(
            content_type=content_type,
            codename__in=codenames,
        )
    )
    assert {permission.codename for permission in permissions} == set(codenames)
    user.user_permissions.add(*permissions)


class ReferralRewardsOverviewAccessTests(TestCase):
    def test_authenticated_learner_is_denied(self):
        learner = make_user("learner")
        self.client.force_login(learner)
        response = self.client.get("/growth/admin/referral-rewards/")
        self.assertEqual(response.status_code, 403)

    def test_generic_staff_without_growth_permissions_is_denied(self):
        staff = make_user("generic-staff", is_staff=True)
        self.client.force_login(staff)
        response = self.client.get("/growth/admin/referral-rewards/")
        self.assertEqual(response.status_code, 403)

    def test_growth_staff_with_both_read_permissions_is_allowed(self):
        staff = make_user("growth-staff", is_staff=True)
        from apps.growth.models import ReferralReward, ReferralSettings

        grant(staff, ReferralReward, "view_referralreward")
        grant(staff, ReferralSettings, "view_referralsettings")
        self.client.force_login(staff)
        response = self.client.get("/growth/admin/referral-rewards/")
        self.assertEqual(response.status_code, 200)

    def test_application_admin_is_allowed(self):
        admin = make_user("growth-admin", role=User.Role.ADMIN)
        self.client.force_login(admin)
        response = self.client.get("/growth/admin/referral-rewards/")
        self.assertEqual(response.status_code, 200)


class GiftWorkflowAccessTests(TestCase):
    def test_generic_staff_cannot_open_or_submit_gift_form(self):
        staff = make_user("gift-generic-staff", is_staff=True)
        self.client.force_login(staff)

        get_response = self.client.get("/admin/growth/send-gift/")
        post_response = self.client.post(
            "/admin/growth/send-gift/",
            {"recipient_email": "nobody@example.test"},
        )

        self.assertEqual(get_response.status_code, 403)
        self.assertEqual(post_response.status_code, 403)
        self.assertEqual(GiftInvite.objects.count(), 0)

    def test_growth_staff_with_add_permission_can_open_gift_form(self):
        staff = make_user("gift-growth-staff", is_staff=True)
        grant(staff, GiftInvite, "add_giftinvite")
        self.client.force_login(staff)
        response = self.client.get("/admin/growth/send-gift/")
        self.assertEqual(response.status_code, 200)

    def test_application_admin_can_open_gift_form(self):
        admin = make_user("gift-admin", role=User.Role.ADMIN)
        self.client.force_login(admin)
        response = self.client.get("/admin/growth/send-gift/")
        self.assertEqual(response.status_code, 200)
