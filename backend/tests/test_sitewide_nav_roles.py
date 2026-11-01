from types import SimpleNamespace

from django.template.loader import get_template
from django.test import RequestFactory, SimpleTestCase


class SitewideNavbarRoleTests(SimpleTestCase):
    def render_nav(self, *, is_admin=False, is_staff=False):
        user = SimpleNamespace(
            is_authenticated=True,
            is_admin=is_admin,
            is_staff=is_staff,
            username="test-account",
            first_name="",
        )
        request = RequestFactory().get("/")
        return get_template("partials/sitewide_nav.html").render({
            "user": user,
            "request": request,
            "public_site_url": "https://tradethesis.example",
        })

    def test_regular_member_gets_dashboard_entry_without_account_dropdown(self):
        rendered = self.render_nav()

        self.assertIn("Member Area ↗", rendered)
        self.assertNotIn("Open member dashboard", rendered)
        self.assertNotIn('class="tt-account-menu"', rendered)
        self.assertNotIn("Profile &amp; security", rendered)
        self.assertNotIn("Referral credits", rendered)
        self.assertNotIn("Sign out", rendered)

    def test_admin_gets_account_dropdown_and_account_actions(self):
        rendered = self.render_nav(is_admin=True, is_staff=True)

        self.assertIn('class="tt-account-menu"', rendered)
        self.assertIn("Admin Desk", rendered)
        self.assertIn("Profile &amp; security", rendered)
        self.assertIn("Referral credits", rendered)
        self.assertIn("Sign out", rendered)

    def test_member_dashboard_keeps_signout_inside_profile_security(self):
        source = get_template("accounts/member_desk.html").template.source

        self.assertIn('action="{% url \'account_logout\' %}"', source)
        self.assertIn('class="inline-form"', source)
        self.assertIn("{% csrf_token %}", source)
        self.assertIn(">Sign out</button>", source)

    def test_staff_account_keeps_privileged_navigation(self):
        rendered = self.render_nav(is_staff=True)

        self.assertIn('class="tt-account-menu"', rendered)
        self.assertIn("Admin Desk", rendered)
