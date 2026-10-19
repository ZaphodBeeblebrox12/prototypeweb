"""Remove Channel Mesh schema after retiring the feature.

Back up the database and confirm mesh-specific rows are no longer needed
before applying this migration to a persistent database. It drops only the
four mesh tables; direct-channel mappings, accounts, assignments, and audit
history are preserved.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bot_integration", "0008_channel_mesh_control_plane"),
    ]

    operations = [
        migrations.DeleteModel(name="UserMeshAssignment"),
        migrations.DeleteModel(name="PlanMeshMapping"),
        migrations.DeleteModel(name="ChannelMeshDestination"),
        migrations.DeleteModel(name="ChannelMesh"),
    ]
