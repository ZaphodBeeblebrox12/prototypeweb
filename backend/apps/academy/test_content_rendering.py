from django.test import SimpleTestCase

from .content_rendering import build_lesson_sections, render_safe_markdown


class SharedLessonRenderingTests(SimpleTestCase):
    ASSET_ID = "8c0f08ab-c9be-45d2-9cde-1f5a0a1c9031"

    def test_authored_heading_levels_are_not_flattened(self):
        source = (
            "# Lesson title\\n\\n"
            "Introduction.\\n\\n"
            "## Main section\\n\\n"
            "Main text.\\n\\n"
            "#### Detail heading\\n\\n"
            "Detail text."
        )
        rendered = build_lesson_sections(source)["idea_html"]
        self.assertIn("<h1>Lesson title</h1>", rendered)
        self.assertIn("<h2>Main section</h2>", rendered)
        self.assertIn("<h4>Detail heading</h4>", rendered)

    def test_structured_figure_renders_in_place_with_title_alt_and_caption(self):
        caption = "Compare one setting at a time before making a judgement."
        source = (
            "Text before the figure.\\n\\n"
            f"![Band comparison](asset://{self.ASSET_ID})\\n\\n"
            "Text after the figure."
        )
        rendered = render_safe_markdown(
            source,
            asset_urls={self.ASSET_ID: "/media/band-comparison.png"},
            figure_metadata={
                self.ASSET_ID: {
                    "title": "What changing the settings changes",
                    "alt": "Three cards compare shorter, baseline and longer windows.",
                    "caption": caption,
                }
            },
            figure_prefix="2.2",
        )
        self.assertLess(rendered.index("Text before the figure."), rendered.index('class="tt-purpose-figure"'))
        self.assertLess(rendered.index('class="tt-purpose-figure"'), rendered.index("Text after the figure."))
        self.assertIn("Figure 2.2 · What changing the settings changes", rendered)
        self.assertIn("Purpose-built teaching aid", rendered)
        self.assertIn('alt="Three cards compare shorter, baseline and longer windows."', rendered)
        self.assertIn(caption, rendered)
        self.assertIn('src="/media/band-comparison.png"', rendered)

    def test_figure_metadata_is_escaped_before_rendering(self):
        rendered = render_safe_markdown(
            f"![Safe alt](asset://{self.ASSET_ID})",
            asset_urls={self.ASSET_ID: "/media/image.png"},
            figure_metadata={
                self.ASSET_ID: {
                    "title": "<script>bad</script>",
                    "alt": 'diagram" onerror="alert(1)',
                    "caption": "<img src=x onerror=alert(1)>",
                }
            },
        )
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("onerror=", rendered)
        self.assertIn("&lt;script&gt;bad&lt;/script&gt;", rendered)

    def test_legacy_image_and_adjacent_caption_still_render_as_figure(self):
        source = (
            f"![Legacy image](asset://{self.ASSET_ID})\\n\\n"
            "Legacy caption stays with the image."
        )
        rendered = render_safe_markdown(
            source,
            asset_urls={self.ASSET_ID: "/media/legacy.png"},
        )
        self.assertIn('<figure class="tt-course-figure">', rendered)
        self.assertIn("Legacy caption stays with the image.", rendered)
