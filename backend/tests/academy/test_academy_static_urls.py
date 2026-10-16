from pathlib import Path

from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.test import SimpleTestCase


class StaticAssetUrlTests(SimpleTestCase):
    def test_static_asset_urls_are_root_absolute_for_nested_learning_routes(self):
        self.assertEqual(
            static("css/image-inspector.css"),
            "/static/css/image-inspector.css",
        )


    def test_vpa_pilot_figures_resolve_from_the_canonical_export_folder(self):
        name = "academy/vpa/vpa-m01-l01-stage1-spot-volume.svg"
        self.assertEqual(static(name), "/static/academy/vpa/vpa-m01-l01-stage1-spot-volume.svg")
        discovered = finders.find(name)
        self.assertIsNotNone(discovered)
        self.assertTrue(Path(discovered).is_file())
