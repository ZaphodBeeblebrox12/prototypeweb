"""
Admin configuration for accounts app with complete member-name capture.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import TradeThesisAdminUserCreationForm
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """User admin with required names on creation and nickname support."""

    add_form = TradeThesisAdminUserCreationForm

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Profile", {"fields": ("nickname",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
        (
            "Profile",
            {
                "classes": ("wide",),
                "fields": ("nickname",),
            },
        ),
    )

    list_display = ("username", "email", "nickname", "first_name", "last_name", "is_staff")
    list_editable = ("nickname",)
    search_fields = ("username", "first_name", "last_name", "email", "nickname")
