"""Desired-access computation (pure reads, no platform calls).

Single source of truth for what a user SHOULD have. Used by the reconcile
engine to diff against current assignments."""
from dataclasses import dataclass, field

from django.db.models import Q
from django.utils import timezone

from .models import PlanChannelMapping
from apps.subscriptions.models import Subscription


@dataclass
class AccessTarget:
    has_plan: bool = False
    telegram_ids: set = field(default_factory=set)
    discord_ids: set = field(default_factory=set)


def get_active_plan(user_id):
    return (Subscription.objects
            .filter(user_id=user_id, is_active=True, status="active")
            .select_related("plan")
            .order_by("-created_at")
            .first())


def get_active_access_plan_ids(user_id, at=None):
    """Return all commerce plans that currently grant paid community access."""
    at = at or timezone.now()
    plan_ids = set(
        Subscription.objects.filter(
            user_id=user_id, is_active=True, status="active"
        ).values_list("plan_id", flat=True)
    )

    from apps.academy.models import CourseEntitlement
    community_plan_ids = CourseEntitlement.objects.filter(
        user_id=user_id,
        status=CourseEntitlement.Status.ACTIVE,
        revoked_at__isnull=True,
        starts_at__lte=at,
        community_access_granted_at__isnull=False,
        community_access_granted_at__lte=at,
        offer__plan_id__isnull=False,
    ).filter(
        Q(community_access_expires_at__isnull=True)
        | Q(community_access_expires_at__gt=at)
    ).values_list("offer__plan_id", flat=True)
    plan_ids.update(community_plan_ids)
    return plan_ids


def compute_target_access(user_id) -> AccessTarget:
    # A learner can hold independent products at the same time. Union their
    # subscription plans with any separate community term included in a course.
    plan_ids = get_active_access_plan_ids(user_id)
    target = AccessTarget(has_plan=bool(plan_ids))
    if plan_ids:
        # PlanChannelMapping points to commerce Plans. A course offer uses its
        # dedicated hidden Plan only as the map to included community channels.
        for platform, external_id in PlanChannelMapping.objects.filter(
            plan_id__in=plan_ids
        ).values_list("platform", "external_id"):
            if platform == "telegram":
                target.telegram_ids.add(external_id)
            elif platform == "discord":
                target.discord_ids.add(external_id)
    return target
