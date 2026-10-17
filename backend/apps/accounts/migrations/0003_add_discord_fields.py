# Historical duplicate migration retained to preserve the dependency path.
#
# The Discord fields are already introduced by 0002_add_discord_fields.
# Repeating those AddField operations here causes fresh PostgreSQL deployments
# to fail with DuplicateColumn. Keep this migration as a no-op so downstream
# 0004_merge_20260316_2048 can continue to depend on this historical node.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_add_discord_fields"),
    ]

    operations = []
