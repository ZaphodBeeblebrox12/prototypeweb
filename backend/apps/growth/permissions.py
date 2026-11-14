"""Permission helpers for privileged Growth workflows."""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


def has_growth_permission(user, permissions):
    """Allow the application Admin/superuser or active staff with every grant.

    A Django is_staff flag is only an entry-point marker. Departmental Growth
    access must come from explicit model permissions assigned to the user or
    one of their Groups.
    """
    if not getattr(user, "is_authenticated", False) or not getattr(user, "is_active", False):
        return False
    if getattr(user, "is_superuser", False) or getattr(user, "role", None) == "admin":
        return True
    if not getattr(user, "is_staff", False):
        return False
    if isinstance(permissions, str):
        permissions = (permissions,)
    return bool(permissions) and user.has_perms(tuple(permissions))


class GrowthPermissionRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Login gate plus explicit Growth-domain permission gate."""

    permission_required = ()
    login_url = "/accounts/login/"
    raise_exception = False

    def test_func(self):
        return has_growth_permission(
            self.request.user,
            self.permission_required,
        )
