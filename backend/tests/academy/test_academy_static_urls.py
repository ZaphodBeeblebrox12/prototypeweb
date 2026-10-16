from django.templatetags.static import static
from django.test import SimpleTestCase


class StaticAssetUrlTests(SimpleTestCase):
    def test_static_asset_urls_are_root_absolute_for_nested_learning_routes(self):
        self.assertEqual(
            static("css/image-inspector.css"),
            "/static/css/image-inspector.css",
        )
