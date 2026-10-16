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


def compute_target_access(user_id) -> AccessTarget:
    now = timezone.now()
    # A learner can hold independent products at the same time. Include every
    # active subscription plan, then union any current community term granted
    # separately through a course offer (for example, CONSTRUCT's 12 months).
    plan_ids = set(
        Subscription.objects.filter(
            user_id=user_id, is_active=True, status="active"
        ).values_list("plan_id", flat=True)
    )

    from apps.academy.models import CourseEntitlement
    community_plan_ids = CourseEntitlement.objects.filter(
        user_id=user_id,
        status=CourseEntitlement.Status.ACTIVE,
        starts_at__lte=now,
        community_access_granted_at__isnull=False,
        community_access_granted_at__lte=now,
        offer__plan_id__isnull=False,
    ).filter(
        Q(community_access_expires_at__isnull=True)
        | Q(community_access_expires_at__gt=now)
    ).values_list("offer__plan_id", flat=True)
    plan_ids.update(community_plan_ids)

    target = AccessTarget(has_plan=bool(plan_ids))
    if plan_ids:
        # PlanChannelMapping.plan points to commerce Plan records. A bundled
        # course entitlement uses its dedicated hidden Plan only as the map
        # from the paid course offer to the included community channels.
        for platform, external_id in PlanChannelMapping.objects.filter(
                plan_id__in=plan_ids).values_list("platform", "external_id"):
            if platform == "telegram":
                target.telegram_ids.add(external_id)
            elif platform == "discord":
                target.discord_ids.add(external_id)
    return target
