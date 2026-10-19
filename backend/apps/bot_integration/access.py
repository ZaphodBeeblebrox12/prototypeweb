"""Desired-access computation (pure reads, no platform calls).

The entitlement source of truth is every currently active subscription. A user
may have one active subscription per product, so access must be the UNION of
all mapped channels/roles rather than the mappings for only the newest plan.
"""
from dataclasses import dataclass, field

from .models import PlanChannelMapping
from apps.subscriptions.models import Subscription


@dataclass
class AccessTarget:
    has_plan: bool = False
    telegram_ids: set = field(default_factory=set)
    discord_ids: set = field(default_factory=set)


def get_active_plans(user_id):
    """Return all active subscriptions, not just the latest product purchase."""
    return (
        Subscription.objects.filter(
            user_id=user_id,
            is_active=True,
            status=Subscription.Status.ACTIVE,
        )
        .select_related("plan")
        .order_by("-created_at")
    )


def get_active_plan(user_id):
    """Legacy convenience helper for callers that genuinely need one plan."""
    return get_active_plans(user_id).first()


def compute_target_access(user_id) -> AccessTarget:
    subscriptions = list(get_active_plans(user_id))
    target = AccessTarget(has_plan=bool(subscriptions))
    if not subscriptions:
        return target

    plan_ids = {subscription.plan_id for subscription in subscriptions}
    mappings = PlanChannelMapping.objects.filter(
        plan_id__in=plan_ids
    ).values_list("platform", "external_id")

    for platform, external_id in mappings:
        if platform == "telegram":
            target.telegram_ids.add(external_id)
        elif platform == "discord":
            target.discord_ids.add(external_id)

    return target
