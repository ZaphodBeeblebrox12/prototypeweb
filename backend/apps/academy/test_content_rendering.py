from pathlib import Path

from django.test import SimpleTestCase

from .content_rendering import build_lesson_sections, render_safe_markdown


class SharedLessonRenderingTests(SimpleTestCase):
    ASSET_ID = "8c0f08ab-c9be-45d2-9cde-1f5a0a1c9031"

    def test_authored_heading_levels_are_not_flattened(self):
        source = (
            "# Lesson title\n\n"
            "Introduction.\n\n"
            "## Main section\n\n"
            "Main text.\n\n"
            "#### Detail heading\n\n"
            "Detail text."
        )
        rendered = build_lesson_sections(source)["idea_html"]
        self.assertIn("<h1>Lesson title</h1>", rendered)
        self.assertIn("<h2>Main section</h2>", rendered)
        self.assertIn("<h4>Detail heading</h4>", rendered)

    def test_structured_figure_renders_in_place_with_title_alt_and_caption(self):
        caption = "Compare one setting at a time before making a judgement."
        source = (
            "Text before the figure.\n\n"
            f"![Band comparison](asset://{self.ASSET_ID})\n\n"
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
            module_label="Module 5 · Build and trade setups",
        )
        self.assertLess(rendered.index("Text before the figure."), rendered.index('class="tt-purpose-figure"'))
        self.assertLess(rendered.index('class="tt-purpose-figure"'), rendered.index("Text after the figure."))
        self.assertIn("What changing the settings changes", rendered)
        self.assertIn("MODULE 5 · Build and trade setups", rendered)
        self.assertIn("TRADETHESIS · LEARNING ROOM", rendered)
        self.assertNotIn("Figure 2.2 ·", rendered)
        self.assertNotIn("Purpose-built teaching aid", rendered)
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
        self.assertIn('alt="diagram&quot; onerror=&quot;alert(1)"', rendered)
        self.assertNotIn('<img src=x onerror=alert(1)>', rendered)
        self.assertIn("&lt;script&gt;bad&lt;/script&gt;", rendered)

    def test_legacy_image_and_adjacent_caption_still_render_as_figure(self):
        source = (
            f"![Legacy image](asset://{self.ASSET_ID})\n\n"
            "Legacy caption stays with the image."
        )
        rendered = render_safe_markdown(
            source,
            asset_urls={self.ASSET_ID: "/media/legacy.png"},
        )
        self.assertIn('<figure class="tt-course-figure">', rendered)
        self.assertIn("Legacy caption stays with the image.", rendered)


    def test_native_comparison_figure_renders_editable_cards_in_place(self):
        figure_id = "figure-block-01"
        source = (
            "Text before the figure.\n\n"
            f"[[teaching-figure:{figure_id}]]\n\n"
            "Text after the figure."
        )
        rendered = render_safe_markdown(
            source,
            figure_metadata={
                figure_id: {
                    "type": "comparison-cards",
                    "title": "What changing the settings changes",
                    "cards": [
                        {
                            "kicker": "SHORTER WINDOW",
                            "title": "More responsive",
                            "body": "The bands react to fewer recent bars.",
                        },
                        {
                            "kicker": "20 PERIODS · 2 DEVIATIONS",
                            "title": "Common baseline",
                            "body": "A reference setting, not a law.",
                        },
                        {
                            "kicker": "LONGER WINDOW",
                            "title": "More smoothed",
                            "body": "The frame usually reacts more slowly.",
                        },
                    ],
                    "note": "Compare one setting at a time.",
                }
            },
            figure_prefix="2.2",
            module_label="Module 5 · Build and trade setups",
        )
        self.assertLess(rendered.index("Text before the figure."), rendered.index('class="tt-purpose-figure'))
        self.assertLess(rendered.index('class="tt-purpose-figure'), rendered.index("Text after the figure."))
        self.assertIn("What changing the settings changes", rendered)
        self.assertIn("MODULE 5 · Build and trade setups", rendered)
        self.assertIn("TRADETHESIS · LEARNING ROOM", rendered)
        self.assertNotIn("Figure 2.2 ·", rendered)
        self.assertNotIn("Purpose-built teaching aid", rendered)
        self.assertIn("SHORTER WINDOW", rendered)
        self.assertIn("More responsive", rendered)
        self.assertIn("Common baseline", rendered)
        self.assertIn("LONGER WINDOW", rendered)
        self.assertIn("Compare one setting at a time.", rendered)

    def test_course_builder_preview_keeps_each_figure_at_its_markdown_position(self):
        preview = (Path(__file__).resolve().parent / "course_builder_preview.html").read_text()
        # Placeholder separators must be actual Markdown blank lines, not literal
        # backslash-n text, or headings and figure tokens leak into the preview.
        self.assertIn(r"return '\n\n' + token + '\n\n';", preview)
        # A placed asset may use either its builder ID or its stable asset UUID.
        # It should not also be appended to the end of the preview as unplaced.
        self.assertIn("[image.id, image.assetUuid]", preview)
        self.assertIn("authoredContent.includes('asset://' + id)", preview)
        self.assertIn('data-action="add-image-group"', preview)
        self.assertIn('data-action="insert-image-group"', preview)
        self.assertIn('data-image-group-member', preview)
        self.assertIn(r"[[image-group:", preview)
        self.assertIn("TRADETHESIS · LEARNING ROOM", preview)
        self.assertIn("tt-purpose-figure-module", preview)


    def test_titled_image_group_renders_multiple_images_with_module_heading_in_place(self):
        group_id = "image-group-method-two"
        first_id = "6a51e8ac-35e2-489c-9a18-48221818e5d9"
        second_id = "7b62f9bd-46f3-4ae0-8b13-59332929f6ea"
        source = (
            "Text before the group.\n\n"
            f"[[image-group:{group_id}]]\n\n"
            "Text after the group."
        )
        rendered = render_safe_markdown(
            source,
            asset_urls={
                first_id: "/media/long-candidate.png",
                second_id: "/media/near-miss.png",
            },
            figure_metadata={
                group_id: {
                    "type": "image-group",
                    "title": "Method II: price position and money flow",
                    "image_ids": [first_id, second_id],
                    "note": "Both conditions must hold.",
                },
                first_id: {
                    "title": "Long candidate",
                    "alt": "Price rises along the upper band.",
                    "caption": "Both conditions must hold.",
                },
                second_id: {
                    "title": "Near miss",
                    "alt": "Price moves sideways while one condition fails.",
                    "caption": "One condition is not met.",
                },
            },
            module_label="Module 5 · Build and trade setups",
        )
        figure_index = rendered.index('class="tt-image-group-figure"')
        self.assertLess(rendered.index("Text before the group."), figure_index)
        self.assertLess(figure_index, rendered.index("Text after the group."))
        self.assertIn("Method II: price position and money flow", rendered)
        self.assertIn("MODULE 5 · Build and trade setups", rendered)
        self.assertIn("Long candidate", rendered)
        self.assertIn("Near miss", rendered)
        self.assertIn('src="/media/long-candidate.png"', rendered)
        self.assertIn('src="/media/near-miss.png"', rendered)
        self.assertIn("Both conditions must hold.", rendered)
        self.assertIn("One condition is not met.", rendered)
        self.assertNotIn("Purpose-built teaching aid", rendered)
        self.assertNotIn("Figure 2.2 ·", rendered)
        self.assertEqual(rendered.count('class="tt-image-group-item"'), 2)

    def test_filename_is_not_used_as_a_figure_title(self):
        rendered = render_safe_markdown(
            f"![Chart](asset://{self.ASSET_ID})",
            asset_urls={self.ASSET_ID: "/media/banknifty.png"},
            figure_metadata={
                self.ASSET_ID: {
                    "title": "BANKNIFTY_2023-08-06_16-51-56_bd975.png",
                    "alt": "BANKNIFTY price chart",
                    "caption": "Price tested the level twice.",
                }
            },
            module_label="Module 5 · Build and trade setups",
        )
        self.assertIn('<strong class="tt-purpose-figure-title">Chart</strong>', rendered)
        self.assertNotIn("BANKNIFTY_2023-08-06_16-51-56_bd975.png", rendered)
