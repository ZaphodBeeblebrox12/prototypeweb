"""
URL configuration for community platform.
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.cache import never_cache

# Use allauth's views for login and signup
from allauth.account.views import LoginView, SignupView
from apps.accounts import views as accounts_views
from apps.accounts.telegram_views import TelegramCallbackView
from apps.admin_dashboard import staff_admin_desk
from apps.admin_desk_views import (
    admin_desk_accounts, admin_desk_account_detail, admin_desk_account_action,
    admin_desk_subscriptions, admin_desk_subscription_action,
    admin_desk_business, admin_desk_finance, admin_desk_invoice_detail,
)
from apps.core.views import health_check

urlpatterns = [
    # Render readiness probe: confirm Django and its primary database respond.
    path("health/", health_check, name="health_check"),
    path("staff/admin-desk/", staff_admin_desk, name="staff_admin_desk"),
    path("staff/admin-desk/accounts/", admin_desk_accounts, name="staff_admin_desk_accounts"),
    path("staff/admin-desk/accounts/<uuid:user_id>/", admin_desk_account_detail, name="staff_admin_desk_account_detail"),
    path("staff/admin-desk/accounts/<uuid:user_id>/action/", admin_desk_account_action, name="staff_admin_desk_account_action"),
    path("staff/admin-desk/subscriptions/", admin_desk_subscriptions, name="staff_admin_desk_subscriptions"),
    path("staff/admin-desk/subscriptions/<uuid:subscription_id>/action/", admin_desk_subscription_action, name="staff_admin_desk_subscription_action"),
    path("staff/admin-desk/business/", admin_desk_business, name="staff_admin_desk_business"),
    path("staff/admin-desk/finance/", admin_desk_finance, name="staff_admin_desk_finance"),
    path("staff/admin-desk/invoices/<uuid:invoice_id>/", admin_desk_invoice_detail, name="staff_admin_desk_invoice_detail"),
    # Growth admin views - MUST be first to avoid catch_all_view interception
    path("admin/", include("apps.growth.admin_urls", namespace="growth_admin")),

    # Django admin (default) - comes after so growth URLs take precedence
    path("admin/", admin.site.urls),
    # Academy routes are explicit and must be resolved before public catch-all routes.
    path("learn/", include("apps.academy.urls")),
    path('', include('apps.public_views.urls')),

    # Custom auth views using your templates. Never cache auth pages: stale
    # HTML can carry a CSRF token that no longer matches the browser's cookie.
    path("accounts/login/", never_cache(LoginView.as_view(
        template_name="auth/tradethesis_login.html",
    )), name="account_login"),

    path("accounts/signup/", never_cache(SignupView.as_view(
        template_name="auth/tradethesis_signup.html",
    )), name="account_signup"),

    path("accounts/", include("allauth.urls")),
    path("api/auth/telegram/", TelegramCallbackView.as_view(), name="api_telegram_auth"),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/admin/", include("apps.accounts.admin_urls")),
    path("auth/telegram/", include("apps.accounts.telegram_urls")),
    path("auth/discord/", include("apps.accounts.discord_urls")),

    # Subscriptions API
    path("api/subscriptions/", include("apps.subscriptions.urls")),

    path("api/analytics/", include("apps.analytics.urls")),
    path("api/", include("apps.api.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("", include("apps.core.urls")),
    path("dashboard/", accounts_views.DashboardView.as_view(), name="dashboard"),
    path("", include("apps.accounts.profile_urls")),
    path("", include("apps.payments.urls")),
    path("growth/", include("apps.growth.urls")),

    # NEW: Bot integration app (Telegram deep link, Discord OAuth, channel sync)
    path("bot/", include("apps.bot_integration.urls")),
    path("bot-admin/", include("apps.bot_integration.integration_admin")),
    path("support/", include("apps.support.urls")),

    # ---- Chargeback implementation (NEW) ----
    path("policies/", include("apps.policies.urls")),           # versioned policy pages + historical versions
    path("admin-disputes/", include("apps.disputes.urls", namespace="disputes")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
