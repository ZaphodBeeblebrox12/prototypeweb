"""Replace Django Sites' example.com seed with TradeThesis identity."""

from urllib.parse import urlsplit

from django.conf import settings
from django.db import migrations


def set_trade_thesis_site_identity(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    database = schema_editor.connection.alias
    site_id = getattr(settings, "SITE_ID", 1)

    base_url = str(getattr(settings, "SITE_BASE_URL", "") or "").strip()
    public_url = str(
        getattr(settings, "TRADETHESIS_PUBLIC_SITE_URL", "") or ""
    ).strip()

    domain = urlsplit(base_url).hostname if base_url else None
    if not domain or domain.lower() in {"localhost", "127.0.0.1"}:
        domain = urlsplit(public_url).hostname if public_url else None
    if not domain:
        domain = "tradethesis.onrender.com"

    Site.objects.using(database).update_or_create(
        pk=site_id,
        defaults={
            "domain": domain[:100],
            "name": "TradeThesis",
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_delete_landingpage"),
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [
        migrations.RunPython(
            set_trade_thesis_site_identity,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
