"""Provision access on subscription activation/deactivation transitions only.

The old post_save fired a full reconcile on EVERY save of an active
subscription (including the expiry task's routine touches). This version
stashes the pre-save status and reconciles only on the activation or
deactivation edge, so routine field updates no longer trigger platform calls.
"""
import logging

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from apps.subscriptions.models import Subscription
from .models import PlanChannelMapping, TelegramAccount
from apps.jobs.enqueue import enqueue_reconcile

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Subscription)
def _stash_old_status(sender, instance, **kwargs):
    instance._old_status = None
    instance._old_is_active = False
    instance._old_plan_id = None
    if instance.pk:
        previous = Subscription.objects.filter(pk=instance.pk).values(
            "status", "is_active", "plan_id"
        ).first()
        if previous:
            instance._old_status = previous["status"]
            instance._old_is_active = previous["is_active"]
            instance._old_plan_id = previous["plan_id"]


def _queue_reconcile_after_commit(user_id, reason):
    """Queue only after the surrounding write commits and the user still exists."""
    from django.contrib.auth import get_user_model
    from django.db import transaction

    def enqueue_if_user_exists():
        if get_user_model().objects.filter(pk=user_id).exists():
            enqueue_reconcile(user_id, reason=reason)

    transaction.on_commit(enqueue_if_user_exists)


@receiver(post_save, sender=Subscription)
def provision_on_transition(sender, instance, created, **kwargs):
    now_active = instance.status == Subscription.Status.ACTIVE and instance.is_active
    old_status = getattr(instance, "_old_status", None)
    old_is_active = getattr(instance, "_old_is_active", False)
    was_active = old_status == Subscription.Status.ACTIVE and old_is_active
    plan_changed = (
        getattr(instance, "_old_plan_id", None) is not None
        and getattr(instance, "_old_plan_id", None) != instance.plan_id
    )

    if now_active != was_active or (now_active and was_active and plan_changed):
        _queue_reconcile_after_commit(
            instance.user_id, reason="subscription_transition"
        )


@receiver(post_delete, sender=Subscription)
def provision_after_subscription_delete(sender, instance, **kwargs):
    _queue_reconcile_after_commit(
        instance.user_id, reason="subscription_deleted"
    )


@receiver(pre_save, sender=PlanChannelMapping)
def _stash_old_mapping_plan(sender, instance, **kwargs):
    instance._old_plan_id = None
    if instance.pk:
        instance._old_plan_id = PlanChannelMapping.objects.filter(
            pk=instance.pk
        ).values_list("plan_id", flat=True).first()


def _queue_plan_mapping_users(plan_ids):
    plan_ids = {plan_id for plan_id in plan_ids if plan_id}
    if not plan_ids:
        return
    user_ids = (
        Subscription.objects.filter(
            plan_id__in=plan_ids,
            status=Subscription.Status.ACTIVE,
            is_active=True,
        )
        .values_list("user_id", flat=True)
        .distinct()
    )
    for user_id in user_ids:
        _queue_reconcile_after_commit(
            user_id, reason="community_role_mapping_changed"
        )


@receiver(post_save, sender=PlanChannelMapping)
def provision_after_mapping_change(sender, instance, **kwargs):
    _queue_plan_mapping_users((
        getattr(instance, "_old_plan_id", None),
        instance.plan_id,
    ))


@receiver(post_delete, sender=PlanChannelMapping)
def provision_after_mapping_delete(sender, instance, **kwargs):
    _queue_plan_mapping_users((instance.plan_id,))


# ── Stage 2: transactional/system messages on the same durable edges ──────
# Reuses the _old_status stash above. TRANSACTIONAL, not marketing: no
# consent gate is (or may be) applied to these messages. Sends run via
# transaction.on_commit so they never fire for rolled-back payments.


@receiver(post_save, sender=TelegramAccount)
def transactional_welcome_on_link(sender, instance, created, **kwargs):
    """Welcome DM when a user links their Telegram account. Transactional."""
    if not created:
        return
    from django.db import transaction as _tx
    from .transactional import TransactionalTelegramService
    _tx.on_commit(lambda: TransactionalTelegramService.send_welcome(instance.user))


def _plan_label(subscription) -> str:
    plan = getattr(subscription, "plan", None)
    for attr in ("display_name", "name", "title"):
        value = getattr(plan, attr, None)
        if value:
            return str(value)
    return "your plan"


@receiver(post_save, sender=Subscription)
def transactional_message_on_transition(sender, instance, created, **kwargs):
    """Activation/expiry edge messages. Mirrors the activation semantics of
    provision_on_transition (status == active AND is_active). Routine saves
    and renewals (status stays active) do not message."""
    old_status = getattr(instance, "_old_status", None)
    new_status = instance.status
    now_active = new_status == "active" and instance.is_active
    was_active = old_status == "active" and getattr(instance, "_old_is_active", False)
    if now_active == was_active and not created:
        return
    from django.db import transaction as _tx
    from .transactional import TransactionalTelegramService
    if now_active and not was_active:
        label = _plan_label(instance)
        _tx.on_commit(
            lambda: TransactionalTelegramService.send_subscription_activated(
                instance.user, plan_name=label))
    elif new_status == "expired" and was_active:
        label = _plan_label(instance)
        _tx.on_commit(
            lambda: TransactionalTelegramService.send_subscription_expired(
                instance.user, plan_name=label))
