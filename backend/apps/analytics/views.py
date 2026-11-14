from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.growth.permissions import has_growth_permission

from .services import report


class CanViewGrowthAnalytics(BasePermission):
    """Require explicit read access to every domain included in this report."""

    required_permissions = (
        "events.view_event",
        "emailing.view_delivery",
        "campaigns.view_campaign",
        "promotions.view_couponredemption",
        "growth.view_referralreward",
    )

    def has_permission(self, request, view):
        return has_growth_permission(request.user, self.required_permissions)


class AnalyticsOverviewView(APIView):
    """Read-only marketing analytics over the durable Event store."""

    permission_classes = [CanViewGrowthAnalytics]

    def get(self, request):
        return Response({
            "signups": report.signup_analytics(),
            "email": report.email_performance(),
            "campaigns": report.campaign_performance(),
            "promotions": report.promotion_performance(),
            "referrals": report.referral_performance(),
        })
