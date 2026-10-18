"""Channel Mesh entitlement-assignment helpers.

This module deliberately records a spawn chosen by the existing allocation
policy. It does not implement a second allocation/placement algorithm.
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.subscriptions.models import Subscription
from ..models import (
    ChannelMesh,
    ChannelMeshDestination,
    UserChannelAssignment,
    UserMeshAssignment,
)


def _pk(value):
    return getattr(value, "pk", value)


@transaction.atomic
def assign_user_to_mesh_spawn(user, mesh, destination):
    """Persist the spawn selected by the existing allocator and queue reconcile.

    The member must hold an active subscription to a plan mapped to this Mesh.
    The supplied destination is the allocator's decision; this function never
    picks a spawn itself.
    """
    user_id = _pk(user)
    mesh_id = _pk(mesh)
    destination_id = _pk(destination)

    mesh_obj = ChannelMesh.objects.select_for_update().filter(
        pk=mesh_id, is_active=True
    ).first()
    if mesh_obj is None:
        raise ValidationError("The selected Channel Mesh does not exist or is inactive.")

    destination_obj = ChannelMeshDestination.objects.select_for_update().filter(
        pk=destination_id
    ).first()
    if destination_obj is None or destination_obj.mesh_id != mesh_obj.pk:
        raise ValidationError("The selected spawn must belong to the selected Mesh.")
    if not destination_obj.is_active:
        raise ValidationError("The selected spawn is inactive.")

    entitled = Subscription.objects.filter(
        user_id=user_id,
        is_active=True,
        status=Subscription.Status.ACTIVE,
        plan__mesh_mappings__mesh_id=mesh_obj.pk,
        plan__mesh_mappings__is_active=True,
    ).exists()
    if not entitled:
        raise ValidationError(
            "The user has no active subscription to a plan configured for this Mesh."
        )

    assignment, created = UserMeshAssignment.objects.select_for_update().get_or_create(
        user_id=user_id,
        mesh_id=mesh_obj.pk,
        defaults={
            "destination": destination_obj,
            "is_active": True,
            "assigned_at": timezone.now(),
            "revoked_at": None,
        },
    )
    if not created:
        if (
            assignment.destination_id == destination_obj.pk
            and assignment.is_active
            and assignment.revoked_at is None
        ):
            return assignment
        assignment.destination = destination_obj
        assignment.is_active = True
        assignment.assigned_at = timezone.now()
        assignment.revoked_at = None

    assignment.full_clean()
    assignment.save()
    return assignment


@transaction.atomic
def deactivate_user_mesh_assignment(user, mesh):
    """Release a user's recorded spawn assignment; reconciliation revokes access."""
    assignment = UserMeshAssignment.objects.select_for_update().filter(
        user_id=_pk(user), mesh_id=_pk(mesh), is_active=True
    ).first()
    if assignment is None:
        return None
    assignment.is_active = False
    assignment.revoked_at = timezone.now()
    assignment.save(update_fields=["is_active", "revoked_at", "updated_at"])
    return assignment


def deactivate_revoked_mesh_assignments(user_id, target):
    """Release stale allocator assignments only after spawn access is revoked.

    The active UserChannelAssignment is the durable provisioning ledger. If a
    revoke failed, keep the assignment active so the allocator does not
    mistakenly consider that capacity free.
    """
    assignments = UserMeshAssignment.objects.filter(
        user_id=user_id, is_active=True
    ).select_related("destination")
    for assignment in assignments:
        destination_id = assignment.destination.external_id
        if destination_id in target.telegram_ids:
            continue
        still_provisioned = UserChannelAssignment.objects.filter(
            user_id=user_id, platform="telegram",
            external_id=destination_id, is_active=True,
        ).exists()
        if not still_provisioned:
            UserMeshAssignment.objects.filter(
                pk=assignment.pk, is_active=True
            ).update(is_active=False, revoked_at=timezone.now())
