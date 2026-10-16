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


    def test_vpa_mobile_pilot_figures_resolve_from_the_approved_static_folder(self):
        names = (
            "academy/vpa/vpa-m01-l01-stage1-spot-volume-mobile.svg",
            "academy/vpa/vpa-m01-l01-candle-context-compare-mobile.svg",
        )
        for name in names:
            with self.subTest(name=name):
                self.assertEqual(static(name), f"/static/{name}")
                discovered = finders.find(name)
                self.assertIsNotNone(discovered)
                self.assertTrue(Path(discovered).is_file())

    def test_vpa_later_outcome_figures_are_not_public_static_assets(self):
        names = (
            "academy/vpa/vpa-m01-l01-stage3-outcome-continuation-mobile.svg",
            "academy/vpa/vpa-m01-l01-stage3-outcome-failure-mobile.svg",
        )
        for name in names:
            with self.subTest(name=name):
                self.assertIsNone(finders.find(name))
