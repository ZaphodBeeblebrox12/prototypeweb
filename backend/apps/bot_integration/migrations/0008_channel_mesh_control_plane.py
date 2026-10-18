"""Channel Mesh inventory, plan mappings, and member spawn assignments."""

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bot_integration", "0007_community_channels"),
        ("subscriptions", "0019_alter_geoplanprice_interval_alter_planprice_interval"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ChannelMesh",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.SlugField(help_text="Stable internal key, e.g. forex-mesh-a.", max_length=64, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("source_chat_id", models.CharField(help_text="Canonical Telegram source chat ID. Members are not assigned here.", max_length=255, unique=True)),
                ("source_name", models.CharField(blank=True, max_length=255)),
                ("is_active", models.BooleanField(default=False, help_text="Enable only after source/destinations and bot permissions have been verified.")),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Channel Mesh",
                "verbose_name_plural": "Channel Meshes",
                "ordering": ["name", "key"],
            },
        ),
        migrations.CreateModel(
            name="ChannelMeshDestination",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("external_id", models.CharField(help_text="Telegram chat ID for this spawn. Keep each spawn in exactly one Mesh.", max_length=255, unique=True)),
                ("name", models.CharField(blank=True, max_length=255)),
                ("chat_type", models.CharField(choices=[("channel", "Channel"), ("group", "Group / supergroup")], default="channel", max_length=16)),
                ("is_active", models.BooleanField(default=False, help_text="Only enable after the bot's rights and destination are verified.")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("mesh", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="destinations", to="bot_integration.channelmesh")),
            ],
            options={
                "verbose_name": "Channel Mesh Spawn",
                "verbose_name_plural": "Channel Mesh Spawns",
                "ordering": ["mesh__name", "name", "external_id"],
            },
        ),
        migrations.CreateModel(
            name="PlanMeshMapping",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("mesh", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="plan_mappings", to="bot_integration.channelmesh")),
                ("plan", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mesh_mappings", to="subscriptions.plan")),
            ],
            options={
                "verbose_name": "Plan Channel Mesh Mapping",
                "verbose_name_plural": "Plan Channel Mesh Mappings",
                "ordering": ["plan__name", "mesh__name"],
                "constraints": [
                    models.UniqueConstraint(fields=("plan", "mesh"), name="plan_mesh_mapping_unique"),
                ],
            },
        ),
        migrations.CreateModel(
            name="UserMeshAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_active", models.BooleanField(default=True)),
                ("assigned_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("destination", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="member_assignments", to="bot_integration.channelmeshdestination")),
                ("mesh", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="member_assignments", to="bot_integration.channelmesh")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="channel_mesh_assignments", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "User Channel Mesh Assignment",
                "verbose_name_plural": "User Channel Mesh Assignments",
                "ordering": ["mesh__name", "user_id"],
                "constraints": [
                    models.UniqueConstraint(fields=("user", "mesh"), name="mesh_assignment_user_mesh_unique"),
                ],
            },
        ),
    ]
