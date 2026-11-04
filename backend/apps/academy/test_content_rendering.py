import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from apps.subscriptions.services import COUNTRY_TO_REGION

from .content_rendering import (
    _deduplicate_course_card_refs,
    build_lesson_sections,
    render_safe_markdown,
)
from .regional_content import (
    CONTENT_COUNTRY_TO_REGION,
    get_content_region_for_country,
    regional_lesson_content_asset_ids,
)
from .views import _notebook_for_course_display


class SharedLessonRenderingTests(SimpleTestCase):
    ASSET_ID = "8c0f08ab-c9be-45d2-9cde-1f5a0a1c9031"

    def test_inline_underline_survives_safe_markdown_rendering(self):
        rendered = render_safe_markdown("This is <u>underlined</u> text.")
        self.assertIn("<u>underlined</u>", rendered)

    def test_whole_lesson_body_uses_country_then_region_then_main_fallback(self):
        source = "Main lesson body."
        overrides = {
            "country:IN": "India lesson body.\n\n| Market | Example |\n|---|---|\n| India | NIFTY |",
            "region:APAC": "APAC lesson body.",
        }

        india = build_lesson_sections(
            source,
            regional_content=overrides,
            country_code="IN",
            region_code="APAC",
        )
        australia = build_lesson_sections(
            source,
            regional_content=overrides,
            country_code="AU",
            region_code="APAC",
        )
        unknown = build_lesson_sections(
            source,
            regional_content=overrides,
            country_code="ZZ",
            region_code=None,
        )
        self.assertIn("India lesson body.", india["idea_html"])
        self.assertIn("NIFTY", india["idea_html"])
        self.assertNotIn("APAC lesson body.", india["idea_html"])
        self.assertIn("APAC lesson body.", australia["idea_html"])
        self.assertIn("Main lesson body.", unknown["idea_html"])

    def test_regional_block_country_override_precedes_region_and_global_fallback(self):
        source = "## Disclosure\n\n[[regional-block:risk-note]]"
        blocks = {
            "risk-note": {
                "id": "risk-note",
                "base_content": "Global disclosure.",
                "variants": [
                    {
                        "scope": "region",
                        "code": "APAC",
                        "content": "APAC disclosure.",
                        "hidden": False,
                    },
                    {
                        "scope": "country",
                        "code": "IN",
                        "content": "India disclosure.",
                        "hidden": False,
                    },
                ],
            }
        }
        india = build_lesson_sections(
            source, regional_blocks=blocks, country_code="IN", region_code="APAC"
        )
        australia = build_lesson_sections(
            source, regional_blocks=blocks, country_code="AU", region_code="APAC"
        )
        unknown = build_lesson_sections(
            source, regional_blocks=blocks, country_code="ZZ", region_code=None
        )
        self.assertIn("India disclosure.", india["idea_html"])
        self.assertIn("APAC disclosure.", australia["idea_html"])
        self.assertIn("Global disclosure.", unknown["idea_html"])
        self.assertNotIn("[[regional-block:", india["idea_html"])

    def test_regional_block_can_be_explicitly_hidden_for_a_matching_country(self):
        source = "## Disclosure\n\nBefore.\n\n[[regional-block:notice]]\n\nAfter."
        blocks = {
            "notice": {
                "id": "notice",
                "base_content": "Global notice.",
                "variants": [
                    {"scope": "country", "code": "CA", "content": "unused", "hidden": True},
                    {"scope": "region", "code": "NA", "content": "North American notice."},
                ],
            }
        }
        canada = build_lesson_sections(
            source, regional_blocks=blocks, country_code="CA", region_code="NA"
        )
        us = build_lesson_sections(
            source, regional_blocks=blocks, country_code="US", region_code="NA"
        )
        self.assertNotIn("unused", canada["idea_html"])
        self.assertNotIn("North American notice.", canada["idea_html"])
        self.assertNotIn("Global notice.", canada["idea_html"])
        self.assertIn("North American notice.", us["idea_html"])
        self.assertNotIn("Global notice.", us["idea_html"])

    def test_whole_lesson_override_asset_references_are_collected_for_permissions(self):
        asset_id = "8c0f08ab-c9be-45d2-9cde-1f5a0a1c9031"
        content_json = {
            "regional_lesson_content": {
                "country:IN": f"![India chart](asset://{asset_id})",
                "region:APAC": "An override without images.",
            }
        }
        self.assertEqual(regional_lesson_content_asset_ids(content_json), {asset_id})

    def test_regional_blocks_never_render_unmanaged_images(self):
        from .regional_content import contains_unmanaged_regional_image

        source = "## Regional disclosure\n\n[[regional-block:notice]]"
        blocks = {
            "notice": {
                "base_content": (
                    "Global text ![remote](https://example.test/global.png) "
                    "![proxy](//cdn.example.test/proxy.png) "
                    "![static](/static/global.png) "
                    "and <img alt='legacy' src='https://example.test/legacy.png'> "
                    "plus <img src=//cdn.example.test/legacy-proxy.png alt='x'> tail."
                ),
                "variants": [
                    {
                        "scope": "country",
                        "code": "IN",
                        "content": (
                            "India text ![remote](https://example.test/india.png) "
                            "![static](/static/india.png) "
                            "and <img src=https://example.test/india-legacy.png alt='x'> tail."
                        ),
                        "hidden": False,
                    }
                ],
            }
        }

        india = build_lesson_sections(
            source, regional_blocks=blocks, country_code="IN", region_code="APAC"
        )["idea_html"]
        global_view = build_lesson_sections(
            source, regional_blocks=blocks, country_code="ZZ", region_code=None
        )["idea_html"]

        for url in (
            "https://example.test/global.png",
            "//cdn.example.test/proxy.png",
            "/static/global.png",
            "https://example.test/legacy.png",
            "//cdn.example.test/legacy-proxy.png",
            "https://example.test/india.png",
            "/static/india.png",
            "https://example.test/india-legacy.png",
        ):
            self.assertNotIn(url, india)
            self.assertNotIn(url, global_view)
        self.assertIn("India text", india)
        self.assertIn("tail.", india)
        self.assertIn("Global text", global_view)
        self.assertFalse(contains_unmanaged_regional_image(f"![managed](asset://{self.ASSET_ID})"))
        self.assertTrue(contains_unmanaged_regional_image("![site-relative](/static/example.png)"))

    def test_misplaced_tab_route_markers_do_not_hide_section_copy(self):
        source = "\n".join(
            [
                "## Start with the decision",
                "",
                "Begin with a practical question a trader may encounter.",
                "",
                "### What to notice",
                "",
                "[[lesson-tab:examples]]",
                "",
                "[[lesson-tab:practice]]",
                "",
                "Separate the visible evidence from the conclusion you may draw from it.",
                "",
                "### Compare the possibilities",
                "",
                "Use a second case to show how similar-looking conditions can lead to different outcomes.",
            ]
        )

        sections = build_lesson_sections(source)

        self.assertIn("What to notice", sections["idea_html"])
        self.assertIn("Separate the visible evidence", sections["idea_html"])
        self.assertIn("Compare the possibilities", sections["idea_html"])
        self.assertIn("Use a second case", sections["idea_html"])
        self.assertNotIn("Separate the visible evidence", sections["examples_html"])
        self.assertNotIn("Use a second case", sections["practice_html"])
        self.assertNotIn(
            "[[lesson-tab:",
            sections["idea_html"] + sections["examples_html"] + sections["practice_html"],
        )

    def test_tab_route_marker_inside_quote_is_hidden_without_breaking_quote(self):
        source = "\n".join(
            [
                "## Why prices move",
                "",
                "Prices move for one reason only:",
                "",
                "> [[lesson-tab:idea]]",
                ">",
                "> **When aggressive buyers outnumber aggressive sellers, price rises.**",
            ]
        )

        sections = build_lesson_sections(source)
        rendered = sections["idea_html"] + sections["examples_html"] + sections["practice_html"]

        self.assertNotIn("[[lesson-tab:idea]]", rendered)
        self.assertIn("<blockquote>", sections["idea_html"])
        self.assertIn("<strong>When aggressive buyers outnumber aggressive sellers, price rises.</strong>", sections["idea_html"])
        self.assertIn("Why prices move", sections["idea_html"])

    def test_explicit_tab_route_applies_to_the_heading_after_the_marker(self):
        source = "\n".join(
            [
                "## Start with the decision",
                "",
                "Introduction remains in the idea tab.",
                "",
                "[[lesson-tab:practice]]",
                "",
                "### What to notice",
                "",
                "This heading and its paragraph are intentionally routed to practice.",
            ]
        )

        sections = build_lesson_sections(source)

        self.assertNotIn("What to notice", sections["idea_html"])
        self.assertIn("What to notice", sections["practice_html"])
        self.assertIn("intentionally routed to practice", sections["practice_html"])
        self.assertIn("Introduction remains in the idea tab", sections["idea_html"])

    def test_duplicate_course_card_refs_keep_the_last_authored_placement(self):
        card = "[[course-card:8c0f08ab-c9be-45d2-9cde-1f5a0a1c9031]]"
        source = (
            "### What to notice\n\n" + card + "\n\n"
            "### Compare the possibilities\n\nCompare two outcomes.\n\n" + card
        )

        cleaned = _deduplicate_course_card_refs(source)

        self.assertEqual(cleaned.count(card), 1)
        self.assertLess(cleaned.index("Compare the possibilities"), cleaned.index(card))
        self.assertIn("Compare two outcomes.", cleaned)

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
        self.assertLess(
            rendered.index("Text before the figure."),
            rendered.index('class="tt-purpose-figure tt-image-group-figure tt-image-group-hard-index"'),
        )
        self.assertLess(
            rendered.index('class="tt-purpose-figure tt-image-group-figure tt-image-group-hard-index"'),
            rendered.index("Text after the figure."),
        )
        self.assertIn('class="tt-purpose-figure tt-image-group-figure tt-image-group-hard-index"', rendered)
        self.assertIn('class="index-label">CHART STUDY</span>', rendered)
        self.assertIn('class="image-count">×1</span>', rendered)
        self.assertIn('class="item-index">A</span>', rendered)
        self.assertIn('class="chart-grid count-1"', rendered)
        self.assertNotIn('class="tt-course-reference-image"', rendered)
        self.assertIn("What changing the settings changes", rendered)
        self.assertIn("Chart group · 01", rendered)
        self.assertNotIn("MODULE 5 · Build and trade setups", rendered)
        self.assertNotIn("TRADETHESIS · LEARNING ROOM", rendered)
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
        self.assertNotIn("<img src=x onerror=alert(1)>", rendered)
        self.assertIn("&lt;script&gt;bad&lt;/script&gt;", rendered)

    def test_legacy_image_and_adjacent_caption_still_render_as_figure(self):
        source = (
            f"![Legacy image](asset://{self.ASSET_ID})\n\n" "Legacy caption stays with the image."
        )
        rendered = render_safe_markdown(
            source,
            asset_urls={self.ASSET_ID: "/media/legacy.png"},
        )
        self.assertIn('<figure class="tt-purpose-figure tt-image-group-figure tt-image-group-hard-index">', rendered)
        self.assertIn('class="index-label">CHART STUDY</span>', rendered)
        self.assertIn('class="chart-grid count-1"', rendered)
        self.assertIn('class="item-index">A</span>', rendered)
        self.assertIn('class="caption-label">Note</span>', rendered)
        self.assertIn("Legacy caption stays with the image.", rendered)
        self.assertNotIn('<figure class="tt-course-figure">', rendered)

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
        self.assertLess(
            rendered.index("Text before the figure."), rendered.index('class="tt-purpose-figure')
        )
        self.assertLess(
            rendered.index('class="tt-purpose-figure'), rendered.index("Text after the figure.")
        )
        self.assertIn("What changing the settings changes", rendered)
        self.assertIn("MODULE 5 · Build and trade setups", rendered)
        self.assertNotIn("TRADETHESIS · LEARNING ROOM", rendered)
        self.assertNotIn("Figure 2.2 ·", rendered)
        self.assertNotIn("Purpose-built teaching aid", rendered)
        self.assertIn("SHORTER WINDOW", rendered)
        self.assertIn("More responsive", rendered)
        self.assertIn("Common baseline", rendered)
        self.assertIn("LONGER WINDOW", rendered)
        self.assertIn("Compare one setting at a time.", rendered)

    def test_course_builder_preview_uses_academy_renderer_for_figure_positions(self):
        backend_root = Path(__file__).resolve().parents[2]
        builder = (Path(__file__).resolve().parent / "course_builder_preview.html").read_text(
            encoding="utf-8"
        )
        course_overview = (
            backend_root / "templates" / "academy" / "course_detail.html"
        ).read_text(encoding="utf-8")
        lesson_experience = (
            backend_root
            / "templates"
            / "academy"
            / "partials"
            / "lesson_experience.html"
        ).read_text(encoding="utf-8")
        tabs_template = (
            backend_root / "templates" / "academy" / "partials" / "lesson_tabs.html"
        ).read_text(encoding="utf-8")
        views_source = (backend_root / "apps" / "academy" / "views.py").read_text(encoding="utf-8")

        # Builder saves the current draft and opens its real Academy preview.
        self.assertIn("data-builder-website-preview-frame", builder)
        self.assertIn("async function refreshBuilderWebsitePreview(force = false)", builder)
        self.assertIn("saveCurrentToAcademy(false)", builder)
        self.assertIn("website_preview_url", builder)
        self.assertIn(
            "previewUrl.searchParams.set('lesson', String(moduleIndex + 1) + '.' + String(lessonIndex + 1));",
            builder,
        )
        self.assertIn("preview_audience", builder)

        # The draft route uses the shared section renderer and learner-facing tabs.
        self.assertIn("selected_sections = build_lesson_sections(", views_source)
        self.assertIn('figure_metadata=content_json.get("figures", {})', views_source)
        self.assertIn('table_metadata=content_json.get("tables", {})', views_source)
        self.assertIn(
            'return render(request, "academy/lesson.html", preview_context)',
            views_source,
        )
        self.assertNotIn("tt-course-header--depth", course_overview)
        self.assertIn(
            'return render(request, "academy/course_detail.html", preview_context)',
            views_source,
        )
        self.assertIn("{{ lesson_sections.idea_html|safe }}", tabs_template)
        self.assertIn('{% include "academy/partials/lesson_tabs.html" with lesson_sections=lesson_sections', lesson_experience)
        self.assertIn("{{ lesson_sections.examples_html|safe }}", tabs_template)
        self.assertIn("{{ lesson_sections.practice_html|safe }}", tabs_template)

    def test_titled_image_group_renders_approved_hard_index_hierarchy(self):
        group_id = "image-group-method-two"
        first_id = "6a51e8ac-35e2-489c-9a18-48221818e5d9"
        second_id = "7b62f9bd-46f3-4ae0-8b13-59332929f6ea"
        source = (
            "Text before the group.\n\n" f"[[image-group:{group_id}]]\n\n" "Text after the group."
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
                    "description": "Both conditions must hold.",
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
            course_title="Understand Bollinger Bands",
        )
        figure_index = rendered.index("tt-image-group-hard-index")
        self.assertLess(rendered.index("Text before the group."), figure_index)
        self.assertLess(figure_index, rendered.index("Text after the group."))
        self.assertIn("Method II: price position and money flow", rendered)
        self.assertIn("Chart group · 01", rendered)
        self.assertNotIn("MODULE 5 · Build and trade setups", rendered)
        self.assertIn('src="/media/long-candidate.png"', rendered)
        self.assertIn('src="/media/near-miss.png"', rendered)
        self.assertIn('class="image-count">×2</span>', rendered)
        self.assertIn('title="2 images in this chart group"', rendered)
        self.assertIn('aria-label="2 images in this chart group">02</span>', rendered)
        self.assertEqual(rendered.count('class="chart-item"'), 2)
        self.assertEqual(rendered.count('class="item-index"'), 2)
        self.assertEqual(rendered.count('class="caption"'), 2)
        self.assertLess(
            rendered.index('class="item-title">Long candidate</span>'),
            rendered.index('class="chart-image"'),
        )
        self.assertEqual(rendered.count('class="tt-purpose-figure-image"'), 2)
        self.assertNotIn("tt-image-group-context", rendered)
        self.assertNotIn("tt-image-group-case-id", rendered)

    def test_hard_index_handles_one_to_four_images_and_empty_fields(self):
        image_ids = [
            "6a51e8ac-35e2-489c-9a18-48221818e5d9",
            "7b62f9bd-46f3-4ae0-8b13-59332929f6ea",
            "11111111-1111-4111-8111-111111111111",
            "22222222-2222-4222-8222-222222222222",
        ]
        for count in range(1, 5):
            with self.subTest(image_count=count):
                group_id = f"hard-index-{count}"
                ids = image_ids[:count]
                urls = {
                    asset_id: f"/media/chart-{index + 1}.png" for index, asset_id in enumerate(ids)
                }
                metadata = {
                    group_id: {
                        "type": "image-group",
                        "title": "A complete chart comparison",
                        "image_ids": ids,
                        "description": "Shared context." if count > 1 else "",
                        "note": "Legacy note that must stay cleared" if count == 1 else "",
                    }
                }
                for index, asset_id in enumerate(ids):
                    letter = chr(ord("A") + index)
                    metadata[asset_id] = {
                        "title": f"Image {letter}",
                        "alt": f"Accessible description for image {letter}",
                        "caption": "Caption A" if index == 0 else "",
                    }
                rendered = render_safe_markdown(
                    f"[[image-group:{group_id}]]",
                    asset_urls=urls,
                    figure_metadata=metadata,
                    module_label="Module 1 · Context",
                    course_title="Test course",
                )
                self.assertIn("tt-image-group-hard-index", rendered)
                self.assertIn(f'class="chart-grid count-{count}"', rendered)
                self.assertIn(f'class="image-count">×{count}</span>', rendered)
                self.assertIn(f'title="{count} images in this chart group"', rendered)
                self.assertIn(f'aria-label="{count} images in this chart group">{count:02d}</span>', rendered)
                self.assertEqual(rendered.count('class="chart-item"'), count)
                self.assertEqual(rendered.count('class="item-index"'), count)
                self.assertLess(
                    rendered.index('class="item-title">Image A</span>'),
                    rendered.index('class="chart-image"'),
                )
                self.assertIn("Note</span> — Caption A", rendered)
                self.assertEqual(rendered.count('class="caption"'), 1)
                self.assertNotIn('class="caption"></span>', rendered)
                if count == 1:
                    self.assertNotIn('class="group-description"', rendered)
                    self.assertNotIn("Legacy note that must stay cleared", rendered)
                else:
                    self.assertIn(
                        'class="group-description">Shared context.</span>',
                        rendered,
                    )
                for index in range(count):
                    self.assertIn(f'Image {chr(ord("A") + index)}', rendered)

    def test_image_groups_use_exact_hard_index_styles_in_builder_and_learner(self):
        root = Path(__file__).resolve().parents[2]
        learner_css = (root / "static" / "academy" / "learning-room.css").read_text(
            encoding="utf-8"
        )
        parity_css = (
            root / "static" / "academy" / "course-template-parity.css"
        ).read_text(encoding="utf-8")
        builder_html = (root / "apps" / "academy" / "course_builder_preview.html").read_text(
            encoding="utf-8"
        )

        # The approved Hard-block Index is deliberately owned by one shared stylesheet.
        self.assertEqual(
            1,
            parity_css.count("/* Hard-block index — exact approved design. */"),
        )
        self.assertNotIn("Hard-block index — exact approved design.", learner_css)
        self.assertNotIn("Hard-block index — exact approved design.", builder_html)
        for selector in (
            ".tt-image-group-hard-index .count-1",
            ".tt-image-group-hard-index .count-2",
            ".tt-image-group-hard-index .count-3",
            ".tt-image-group-hard-index .count-4",
            ".tt-image-group-hard-index .index-block",
            ".tt-image-group-hard-index .chart-item",
        ):
            with self.subTest(selector=selector):
                self.assertIn(selector, parity_css)

        self.assertIn(
            ".tt-tab-panel .tt-purpose-figure:not(.tt-image-group-hard-index),",
            learner_css,
        )
        self.assertIn(
            ".preview-body .tt-purpose-figure:not(.tt-image-group-hard-index) {",
            builder_html,
        )
        self.assertIn("tt-image-group-hard-index", builder_html)
        self.assertIn(
            "if (!String(lesson.content || '').includes(token) || group.imageIds.length > 0) return;",
            builder_html,
        )
        self.assertNotIn("const replacement = survivor", builder_html)


    def test_image_group_numbering_stays_consistent_across_lesson_tabs(self):
        first_id = "11111111-1111-4111-8111-111111111111"
        second_id = "22222222-2222-4222-8222-222222222222"
        source = (
            "[[lesson-tab:idea]]\n"
            "## First reading\n\n"
            "[[image-group:first-group]]\n\n"
            "[[lesson-tab:examples]]\n"
            "## Chart examples\n\n"
            "[[image-group:second-group]]"
        )
        rendered = build_lesson_sections(
            source,
            asset_urls={first_id: "/media/first.png", second_id: "/media/second.png"},
            figure_metadata={
                "first-group": {
                    "type": "image-group",
                    "title": "First group",
                    "image_ids": [first_id],
                },
                "second-group": {
                    "type": "image-group",
                    "title": "Second group",
                    "image_ids": [second_id],
                },
                first_id: {"title": "First chart", "alt": "First chart"},
                second_id: {"title": "Second chart", "alt": "Second chart"},
            },
        )
        self.assertIn("Chart group · 01", rendered["idea_html"])
        self.assertIn("Chart group · 02", rendered["examples_html"])

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
        self.assertIn('<span class="group-title">Chart</span>', rendered)
        self.assertNotIn("BANKNIFTY_2023-08-06_16-51-56_bd975.png", rendered)

    def test_structured_grouped_table_renders_spans_and_accessible_wrapper(self):
        source = "Opening copy.\n\n[[table-block:market-comparison]]\n\nClosing copy."
        rendered = render_safe_markdown(
            source,
            table_metadata={
                "market-comparison": {
                    "title": "Market comparison",
                    "columnWidths": [20, 20, 25, 35],
                    "rows": [
                        {
                            "section": "head",
                            "cells": [
                                {"text": "Context", "colspan": 2, "rowspan": 1, "header": True},
                                {"text": "Decision", "colspan": 2, "rowspan": 1, "header": True},
                            ],
                        },
                        {
                            "section": "head",
                            "cells": [
                                {"text": "Market", "colspan": 1, "rowspan": 1, "header": True},
                                {"text": "Evidence", "colspan": 1, "rowspan": 1, "header": True},
                                {
                                    "text": "If confirmed",
                                    "colspan": 1,
                                    "rowspan": 1,
                                    "header": True,
                                },
                                {"text": "If rejected", "colspan": 1, "rowspan": 1, "header": True},
                            ],
                        },
                        {
                            "section": "body",
                            "cells": [
                                {"text": "Range", "colspan": 1, "rowspan": 1, "header": False},
                                {
                                    "text": "Repeated rejection",
                                    "colspan": 1,
                                    "rowspan": 1,
                                    "header": False,
                                },
                                {
                                    "text": "Wait for follow-through",
                                    "colspan": 1,
                                    "rowspan": 1,
                                    "header": False,
                                },
                                {
                                    "text": "Reassess the range",
                                    "colspan": 1,
                                    "rowspan": 1,
                                    "header": False,
                                },
                            ],
                        },
                    ],
                }
            },
        )
        self.assertIn('class="lesson-table-wrap tt-structured-table-wrap"', rendered)
        self.assertIn('aria-label="Scrollable table: Market comparison"', rendered)
        self.assertIn(
            '<caption class="tt-structured-table-caption">Market comparison</caption>', rendered
        )
        self.assertIn('colspan="2" scope="colgroup"', rendered)
        self.assertIn('class="tt-structured-table tt-auto-layout" data-column-count="4"', rendered)
        self.assertIn('<col width="20.0%">', rendered)
        self.assertIn("Repeated rejection", rendered)
        self.assertIn("Opening copy.", rendered)
        self.assertIn("Closing copy.", rendered)
        self.assertNotIn("[[table-block:", rendered)

    def test_markdown_tables_receive_automatic_column_layout(self):
        rendered = render_safe_markdown(
            "| Order type | How it works | Advantage | Risk and when to use it |\n"
            "| --- | --- | --- | --- |\n"
            "| Market order | Executes at the best available price | Fast execution | Slippage can occur |"
        )
        self.assertIn('class="tt-auto-layout" data-column-count="4"', rendered)
        self.assertIn("<colgroup><col width=", rendered)
        self.assertIn('class="lesson-table-wrap"', rendered)

    def test_option_five_table_styles_override_generic_lesson_table_skin(self):
        root = Path(__file__).resolve().parents[2]
        styles = (root / "static" / "academy" / "learning-room.css").read_text(encoding="utf-8")

        self.assertIn(".tt-learning-room .tt-tab-panel .lesson-table-wrap,", styles)
        self.assertIn("border-radius: 0;", styles)
        self.assertIn("min-width: 490px;", styles)
        self.assertIn("background: #345943;", styles)
        self.assertIn("background: #e8eee4;", styles)
        self.assertIn(
            ".tt-learning-room .tt-tab-panel table.tt-structured-table caption.tt-structured-table-caption",
            styles,
        )

    def test_structured_grouped_table_renders_rowspans_for_single_column_headers(self):
        rendered = render_safe_markdown(
            "[[table-block:ohlc-context]]",
            table_metadata={
                "ohlc-context": {
                    "title": "From observation to execution",
                    "rows": [
                        {
                            "section": "head",
                            "cells": [
                                {
                                    "text": "Price structure",
                                    "colspan": 4,
                                    "rowspan": 1,
                                    "header": True,
                                },
                                {"text": "Volume", "colspan": 1, "rowspan": 2, "header": True},
                                {"text": "Context", "colspan": 1, "rowspan": 2, "header": True},
                            ],
                        },
                        {
                            "section": "head",
                            "cells": [
                                {"text": "Open", "colspan": 1, "rowspan": 1, "header": True},
                                {"text": "High", "colspan": 1, "rowspan": 1, "header": True},
                                {"text": "Low", "colspan": 1, "rowspan": 1, "header": True},
                                {"text": "Close", "colspan": 1, "rowspan": 1, "header": True},
                            ],
                        },
                        {
                            "section": "body",
                            "cells": [
                                {"text": "Breakout", "colspan": 1, "rowspan": 1, "header": False},
                                {
                                    "text": "Above range",
                                    "colspan": 1,
                                    "rowspan": 1,
                                    "header": False,
                                },
                                {
                                    "text": "Activity rises",
                                    "colspan": 1,
                                    "rowspan": 1,
                                    "header": False,
                                },
                                {
                                    "text": "Close holds",
                                    "colspan": 1,
                                    "rowspan": 1,
                                    "header": False,
                                },
                                {"text": "Strong", "colspan": 1, "rowspan": 1, "header": False},
                                {"text": "Trend", "colspan": 1, "rowspan": 1, "header": False},
                            ],
                        },
                    ],
                }
            },
        )
        self.assertIn(
            '<caption class="tt-structured-table-caption">From observation to execution</caption>',
            rendered,
        )
        self.assertIn('rowspan="2" scope="col">Volume</th>', rendered)
        self.assertIn('rowspan="2" scope="col">Context</th>', rendered)
        self.assertIn('colspan="4" scope="colgroup">Price structure</th>', rendered)
        self.assertIn("Open</th>", rendered)
        self.assertIn("Close</th>", rendered)

    def test_information_table_uses_accessible_scrollable_reference_wrapper(self):
        source = (
            "| Confirmed move | ADX above threshold | ADX below threshold |\n"
            "| :--- | :---: | ---: |\n"
            "| Two closes above the upper band | Trend-following buy alert | Reversal context only |\n"
            "| Two closes below the lower band | Trend-following short alert | Reversal context only |"
        )
        rendered = render_safe_markdown(source)
        self.assertIn('class="lesson-table-wrap"', rendered)
        self.assertIn('role="region"', rendered)
        self.assertIn('aria-label="Scrollable information table"', rendered)
        self.assertIn('tabindex="0"', rendered)
        self.assertIn('<table class="tt-auto-layout" data-column-count="3">', rendered)
        self.assertIn("<thead>", rendered)
        self.assertIn("<tbody>", rendered)
        self.assertIn('<th align="left">Confirmed move</th>', rendered)
        self.assertIn('<th align="center">ADX above threshold</th>', rendered)
        self.assertIn('<td align="right">Reversal context only</td>', rendered)
        self.assertIn("Two closes above the upper band", rendered)
        self.assertIn("Trend-following short alert", rendered)
        self.assertNotIn("| Confirmed move |", rendered)

    def test_course_builder_country_targets_match_server_geo_regions(self):
        preview = (Path(__file__).resolve().parent / "course_builder_preview.html").read_text(
            encoding="utf-8"
        )
        match = re.search(
            r"const regionalCountryOptions = \[(.*?)\n  \];",
            preview,
            re.DOTALL,
        )
        self.assertIsNotNone(match, "The regional audience options are missing.")
        parsed = re.findall(
            r"\['([A-Z]{2})','([^']+)','(APAC|EU|NA|LATAM|MENA|SSA)'\]",
            match.group(1),
        )
        option_map = {code: region for code, _label, region in parsed}
        self.assertEqual(
            len(parsed),
            len(option_map),
            "The regional audience list must not contain duplicate country codes.",
        )
        self.assertEqual(option_map, CONTENT_COUNTRY_TO_REGION)

    def test_content_audience_map_covers_more_countries_without_changing_pricing_regions(self):
        self.assertEqual(248, len(CONTENT_COUNTRY_TO_REGION))
        self.assertEqual("EU", get_content_region_for_country("is"))
        self.assertEqual("EU", get_content_region_for_country("UA"))
        self.assertEqual("APAC", get_content_region_for_country("fj"))
        self.assertIsNone(get_content_region_for_country("AQ"))
        # Regional lesson targeting must not silently expand geo-pricing policy.
        self.assertNotIn("IS", COUNTRY_TO_REGION)
        self.assertNotIn("UA", COUNTRY_TO_REGION)
        self.assertNotIn("FJ", COUNTRY_TO_REGION)

    def test_course_builder_preview_has_visual_table_editor_support(self):
        preview = (Path(__file__).resolve().parent / "course_builder_preview.html").read_text()
        learner_css = (
            Path(__file__).resolve().parents[2]
            / "static"
            / "academy"
            / "learning-room.css"
        ).read_text(encoding="utf-8")
        self.assertIn("const renderTable = block =>", preview)
        self.assertIn("isTableDivider", preview)
        self.assertIn('class="lesson-table-wrap" role="region"', preview)
        # The lesson body is now a no-code rich-text canvas; table insertion is a toolbar action.
        self.assertIn("const headingMatch = line =>", preview)
        self.assertIn("const isFence = line =>", preview)
        self.assertIn("output.push('<h' + level", preview)
        self.assertIn("output.push('<pre><code' + language", preview)
        self.assertIn("Compact figure treatment:", preview)
        self.assertIn("margin: 19px 0", preview)
        self.assertIn("max-height: min(56vh, 500px)", preview)
        self.assertIn('data-rich-command="bold" aria-label="Bold"', preview)
        self.assertIn('data-rich-command="italic" aria-label="Italic"', preview)
        self.assertIn('data-rich-command="underline" aria-label="Underline"', preview)
        self.assertIn('aria-keyshortcuts="Control+B Meta+B"', preview)
        self.assertIn('aria-keyshortcuts="Control+I Meta+I"', preview)
        self.assertIn('aria-keyshortcuts="Control+U Meta+U"', preview)
        self.assertIn("event.ctrlKey || event.metaKey", preview)
        self.assertIn("syncVisualEditorToModel(editor)", preview)
        self.assertIn("if (tag === 'u') return '<u>' + inner + '</u>'", preview)
        self.assertIn('title="1 image in this chart group"', preview)
        self.assertIn("images in this chart group", preview)
        self.assertIn('contenteditable="true" spellcheck="true"', preview)
        self.assertIn(
            'data-rich-command="table" aria-label="Insert table" title="Insert a table">Table',
            preview,
        )
        self.assertIn('data-visual-editor="true"', preview)
        self.assertIn("tt-image-group-hard-index", preview)
        self.assertIn("previewChartNumbers.get('asset:' + id)", preview)
        self.assertIn("chart-grid count-1", preview)
        self.assertNotIn("tt-course-reference", preview)
        self.assertIn("Drag an image into the lesson", preview)
        self.assertIn("data-image-tray-item", preview)
        self.assertIn("activeEditorImageDragMode = 'insert'", preview)
        self.assertIn(
            r".replace(/^[ \t]*(?:>[ \t]*)+\[\[lesson-tab:",
            preview,
        )
        self.assertIn(
            r".replace(/^[ \t]*\[\[lesson-tab:",
            preview,
        )
        self.assertIn("#edf3f8", preview)
        self.assertIn("data-editor-drag-handle", preview)
        self.assertIn("data-editor-block-move", preview)
        self.assertIn("editorImageDropPlacement", preview)
        self.assertIn("syncVisualEditorToModel(editedEditor)", preview)
        self.assertIn('data-action="remove-image-reference"', preview)
        self.assertIn('data-action="remove-image-from-group"', preview)
        self.assertIn(".tt-image-group-hard-index", preview)
        self.assertNotIn(".tt-course-reference-figure", learner_css)
        self.assertNotIn(".tt-course-reference-figure", preview)
        self.assertIn(".tt-figure-dialog[open]", learner_css)
        self.assertIn("grid-template-rows:42px minmax(0,1fr) auto", learner_css)
        self.assertIn("inset:8px", learner_css)
        self.assertIn("regionalCountryRegionMap = Object.fromEntries", preview)
        self.assertIn("regionalCountryOptions.map(([code, label, region])", preview)
        self.assertIn("regionalCountryRegionMap[country] || ''", preview)
        self.assertIn("audiencePicker.innerHTML", preview)
        self.assertIn("regionalLabels[code] || code", preview)
        self.assertIn("['NO','Norway','EU']", preview)
        self.assertIn("previewUrl.searchParams.set('preview_audience',audience||'GLOBAL')", preview)
        self.assertNotIn("Copy the structure below into a lesson", preview)
        self.assertNotIn("Information tables:", preview)


class TradingNotebookTemplateTests(SimpleTestCase):
    def test_notebook_sits_beside_the_entire_tabbed_content_column(self):
        template = (
            Path(__file__).resolve().parents[2]
            / "templates"
            / "academy"
            / "partials"
            / "lesson_tabs.html"
        )
        source = template.read_text(encoding="utf-8")

        grid = source.index('<div class="learning-content-grid">')
        column = source.index('<div class="lesson-content-column">', grid)
        tabs = source.index('<section class="tt-lesson-tabs"', column)
        notebook = source.index('<aside class="tt-notebook"', grid)

        self.assertLess(grid, column)
        self.assertLess(column, tabs)
        self.assertLess(tabs, notebook)

        # Both the complete tabs section and its content-column wrapper
        # must close before the Notebook sibling begins.
        tabs_end = source.rfind("</section>", tabs, notebook)
        self.assertGreaterEqual(
            tabs_end,
            tabs,
            "Could not find the closing tag for the complete lesson-tabs section.",
        )

        content_column_end = source.find("</div>", tabs_end)
        self.assertGreater(
            content_column_end,
            tabs_end,
            "Could not find the content-column closing tag after the tabs.",
        )
        self.assertLess(
            content_column_end,
            notebook,
            "The Notebook must be outside the complete content column.",
        )

        self.assertEqual(source.count('class="tt-notebook"'), 1)
        self.assertIn('data-tab-panel="idea"', source)
        self.assertIn('data-tab-panel="examples"', source)
        self.assertIn('data-tab-panel="practice"', source)
        self.assertIn("Your Trading Notebook", source)
        self.assertIn("Where is price relative to the bands and middle line?", source)
        self.assertIn("What would change your view?", source)
        self.assertIn('<strong class="tt-notebook-prompt-label">Apply</strong>', source)

    def test_notebook_styling_and_chart_tab_action_are_wired(self):
        backend = Path(__file__).resolve().parents[2]
        styles = (backend / "static" / "academy" / "learning-room.css").read_text(encoding="utf-8")
        notebook_styles = (backend / "static" / "academy" / "notebook-card.css").read_text(
            encoding="utf-8"
        )
        script = (backend / "static" / "academy" / "learning-room.js").read_text(encoding="utf-8")
        lesson_template = (backend / "templates" / "academy" / "lesson.html").read_text(
            encoding="utf-8"
        )
        course_overview_template = (
            backend / "templates" / "academy" / "course_detail.html"
        ).read_text(encoding="utf-8")
        tabs_template = (
            backend / "templates" / "academy" / "partials" / "lesson_tabs.html"
        ).read_text(encoding="utf-8")

        self.assertGreater(
            lesson_template.index("notebook-card.css"),
            lesson_template.index("admin-lesson-preview.css"),
        )
        self.assertIn("course-admin-preview.css", course_overview_template)
        self.assertNotIn("notebook-card.css", course_overview_template)
        self.assertNotIn("learning-room.css", course_overview_template)
        self.assertIn("grid-template-columns: minmax(0, 1fr) 220.5px;", notebook_styles)
        self.assertIn("font-size: 25px;", notebook_styles)
        self.assertIn("font-weight: 700;", notebook_styles)
        self.assertIn("font-size: 12px;", notebook_styles)
        self.assertIn(".tt-notebook-prompt-label", notebook_styles)
        self.assertIn("<summary>Write your reflections</summary>", tabs_template)
        self.assertIn('placeholder="Write a short reflection…" disabled', tabs_template)
        self.assertIn("data-notebook-response", tabs_template)
        self.assertIn(".tt-learning-room .tt-notebook-index", styles)
        self.assertIn(".tt-learning-room .learning-content-grid", styles)
        self.assertIn(".tt-learning-room .lesson-content-column", styles)
        self.assertIn("grid-row:1", styles)
        self.assertIn(".tt-learning-room .tt-notebook-examples-button", styles)
        self.assertIn("@media(max-width:620px)", styles)
        self.assertIn('event.target.closest("[data-open-tab]")', script)
        self.assertIn('form = event.target.closest("[data-notebook-response]")', script)

    def test_responsive_pause_and_record_uses_cards_below_lesson_on_small_screens(self):
        backend = Path(__file__).resolve().parents[2]
        tabs_template = (
            backend / "templates" / "academy" / "partials" / "lesson_tabs.html"
        ).read_text(encoding="utf-8")
        notebook_styles = (backend / "static" / "academy" / "notebook-card.css").read_text(
            encoding="utf-8"
        )

        # The mobile card alternative belongs after the full side-by-side grid,
        # so it is at the end of the lesson content and before Continue Learning.
        grid_end = tabs_template.index('</div>\n<section class="tt-mobile-pause-and-record"')
        mobile_cards = tabs_template.index('<section class="tt-mobile-pause-and-record"')
        template_end = tabs_template.rfind("{% endwith %}")
        self.assertLess(grid_end, mobile_cards)
        self.assertLess(mobile_cards, template_end)
        self.assertEqual(tabs_template.count('class="tt-mobile-pause-and-record"'), 1)
        for label in ("Describe", "Interpret", "Apply"):
            with self.subTest(label=label):
                self.assertIn(f"<h3>{label}</h3>", tabs_template)

        # The alternative is hidden on desktop and shown through tablet/mobile;
        # all three cards stay on one row, including the narrow mobile breakpoint.
        self.assertIn(
            ".tt-learning-room .tt-mobile-pause-and-record {\n  display: none;", notebook_styles
        )
        self.assertIn("@media (max-width: 920px)", notebook_styles)
        self.assertIn("display: none !important;", notebook_styles)
        self.assertIn(
            ".tt-learning-room .tt-mobile-pause-and-record {",
            notebook_styles,
        )
        self.assertIn("display: block;", notebook_styles)
        mobile_marker = notebook_styles.index(
            "/* Option A: keep all three reflection cards on one row on phone screens. */"
        )
        mobile_rule_start = notebook_styles.rindex("@media (max-width: 680px)", 0, mobile_marker)
        mobile_rule_end = notebook_styles.rfind("}", mobile_rule_start)
        mobile_rules = notebook_styles[mobile_rule_start:mobile_rule_end]
        self.assertIn("@media (max-width: 680px)", mobile_rules)
        self.assertIn("grid-template-columns: repeat(3, minmax(0, 1fr));", mobile_rules)
        self.assertNotIn("grid-template-columns: minmax(0, 1fr);", mobile_rules)

    def test_agreed_preview_width_editorial_type_scale_and_notebook_hierarchy(self):
        backend = Path(__file__).resolve().parents[2]
        lesson_styles = (backend / "static" / "academy" / "learning-room.css").read_text(
            encoding="utf-8"
        )
        preview_styles = (backend / "static" / "academy" / "course-admin-preview.css").read_text(
            encoding="utf-8"
        )
        notebook_styles = (backend / "static" / "academy" / "notebook-card.css").read_text(
            encoding="utf-8"
        )
        tabs_template = (
            backend / "templates" / "academy" / "partials" / "lesson_tabs.html"
        ).read_text(encoding="utf-8")
        builder_source = (backend / "apps" / "academy" / "course_builder_preview.html").read_text(
            encoding="utf-8"
        )
        parity_styles = (backend / "static" / "academy" / "course-template-parity.css").read_text(
            encoding="utf-8"
        )

        # The shared lesson shell owns page width; the Notebook component owns its column.
        self.assertIn(".main-content:has(> .tt-lesson-experience)", lesson_styles)
        self.assertIn("width: min(1600px, 100%)", lesson_styles)
        self.assertIn("grid-template-columns: minmax(0, 1fr) 220.5px", notebook_styles)
        self.assertNotIn("learning-content-grid", preview_styles)
        self.assertIn("font-size: clamp(42px, 5vw, 64px)", lesson_styles)
        # Authored H2-H5 roles now live in the canonical shared stylesheet.
        for selector in (
            ".tt-learning-room .tt-tab-panel h2,",
            ".tt-learning-room .tt-tab-panel h3,",
            ".tt-learning-room .tt-tab-panel h4,",
            ".tt-learning-room .tt-tab-panel h5,",
        ):
            self.assertIn(selector, parity_styles)
        self.assertIn("font-size: 30px;", parity_styles)
        self.assertIn("font-size: 27px;", parity_styles)
        self.assertIn("font-size: 22px;", parity_styles)
        self.assertIn("font-size: 1em;", parity_styles)
        self.assertIn("font-size: .83em;", parity_styles)
        self.assertIn("font-size: 13px;", parity_styles)
        self.assertIn("font-weight: 850;", parity_styles)
        self.assertIn("letter-spacing: .15em;", parity_styles)
        self.assertIn(
            'font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;',
            parity_styles,
        )
        self.assertIn(".preview-body h2,", parity_styles)
        self.assertIn('font-family: Georgia, "Times New Roman", serif;', parity_styles)
        for selector in (
            ".rich-editor-canvas h2 {",
            ".rich-editor-canvas h3 {",
            ".rich-editor-canvas h4 {",
            ".rich-editor-canvas h5 {",
        ):
            self.assertIn(selector, parity_styles)
        for heading in ("h2", "h3", "h4", "h5"):
            self.assertNotIn(f".rich-editor-canvas {heading} {{", builder_source)
        self.assertIn(".rich-editor-canvas h6,", parity_styles)
        self.assertIn(".rich-editor-canvas p.eyebrow,", parity_styles)
        self.assertIn("display: block;", lesson_styles)
        self.assertIn('{{ notebook.title|default:"Your Trading Notebook" }}', tabs_template)
        self.assertIn("{% if notebook.prompts %}", tabs_template)
        self.assertIn('<details class="tt-notebook-response-editor">', tabs_template)
        self.assertIn("<summary>Write your reflections</summary>", tabs_template)
        self.assertIn("{% if admin_preview or not lesson %}", tabs_template)
        self.assertIn("This design preview does not submit or store them.", tabs_template)
        self.assertIn('placeholder="Write a short reflection…" disabled', tabs_template)
        self.assertIn("data-notebook-response", tabs_template)
        self.assertIn("Your Trading Notebook", tabs_template)
        self.assertIn('<strong class="tt-notebook-prompt-label">Describe</strong>', tabs_template)
        self.assertIn("<p>What evidence is visible?</p>", tabs_template)

    def test_course_builder_heading_ladder_is_active_in_both_preview_paths(self):
        backend = Path(__file__).resolve().parents[2]
        parity_css = (backend / "static" / "academy" / "course-template-parity.css").read_text(
            encoding="utf-8"
        )
        learning_room_css = (backend / "static" / "academy" / "learning-room.css").read_text(
            encoding="utf-8"
        )
        course_admin_preview_css = (
            backend / "static" / "academy" / "course-admin-preview.css"
        ).read_text(encoding="utf-8")
        builder_source = (backend / "apps" / "academy" / "course_builder_preview.html").read_text(
            encoding="utf-8"
        )
        lesson_template = (backend / "templates" / "academy" / "lesson.html").read_text(
            encoding="utf-8"
        )
        course_overview_template = (
            backend / "templates" / "academy" / "course_detail.html"
        ).read_text(encoding="utf-8")

        self.assertGreater(
            lesson_template.index("course-template-parity.css"),
            lesson_template.index("notebook-card.css"),
        )
        self.assertIn("course-admin-preview.css", course_overview_template)
        self.assertNotIn("course-template-parity.css", course_overview_template)
        self.assertNotIn("notebook-card.css", course_overview_template)
        parity_link = builder_source.index("/static/academy/course-template-parity.css")
        self.assertGreater(parity_link, builder_source.index("</style>"))
        self.assertLess(parity_link, builder_source.index("</head>"))
        for selector in (
            ".rich-editor-canvas h2 {",
            ".rich-editor-canvas h3 {",
            ".rich-editor-canvas h4 {",
            ".rich-editor-canvas h5 {",
        ):
            self.assertIn(selector, parity_css)
        self.assertIn(".rich-editor-canvas p.eyebrow,", parity_css)
        self.assertIn(".rich-editor-canvas h6,", parity_css)
        for heading in ("h2", "h3", "h4", "h5", "h6"):
            self.assertNotIn(f".rich-editor-canvas {heading} {{", builder_source)
        # The embedded builder preview must not retain duplicate heading rules;
        # course-template-parity.css is the source of truth for H2-H5.
        for heading in ("h2", "h3", "h4", "h5"):
            self.assertNotIn(f".preview-body {heading} {{", builder_source)
        self.assertNotIn(".preview-body > h2:first-child", builder_source)
        self.assertNotIn(".preview-body > h3:first-child", builder_source)
        self.assertIn(".preview-body > h1:first-child { margin-top: .1em; }", builder_source)

        self.assertNotIn(
            "Visual parity pass 7: map every Academy content heading", learning_room_css
        )
        self.assertNotIn(
            "Visual parity pass 7: apply the canonical heading ladder", course_admin_preview_css
        )
        self.assertNotIn("Canonical authored-heading ladder", builder_source)
        # Only the global fallback remains in learning-room.css; the canonical stylesheet owns the scoped ladder.
        self.assertIn(".tt-tab-panel h3 {", learning_room_css)
        self.assertIn(".tt-tab-panel h4 {", learning_room_css)
        self.assertNotIn(".tt-learning-room .tt-tab-panel h2,", learning_room_css)
        self.assertNotIn(".tt-learning-room .tt-tab-panel h3 {", learning_room_css)
        self.assertNotIn(".tt-learning-room .tt-tab-panel h4 {", learning_room_css)
        self.assertNotIn('data-tab-panel="idea"', parity_css)
        self.assertNotIn("h6:first-child", parity_css)
        self.assertNotIn(".eyebrow:first-child", parity_css)
        self.assertEqual(learning_room_css.count("/*"), learning_room_css.count("*/"))
        self.assertEqual(course_admin_preview_css.count("/*"), course_admin_preview_css.count("*/"))

        def rule_body(selector):
            start = parity_css.index(selector)
            opening = parity_css.index("{", start)
            closing = parity_css.index("}", opening)
            return parity_css[opening + 1 : closing]

        h2 = rule_body(".tt-learning-room .tt-tab-panel h2,")
        h3 = rule_body(".tt-learning-room .tt-tab-panel h3,")
        h4 = rule_body(".tt-learning-room .tt-tab-panel h4,")
        h5 = rule_body(".tt-learning-room .tt-tab-panel h5,")
        eyebrow = rule_body(".tt-learning-room .tt-tab-panel .body-copy p.eyebrow,")
        no_rule = rule_body(".tt-learning-room .tt-tab-panel .body-copy p.eyebrow::before,")

        for value in (
            "font-size: 30px;",
            "font-weight: 600;",
            "line-height: 1.2;",
            "letter-spacing: -.025em;",
            "margin: 0 0 13px;",
            "max-width: 730px;",
        ):
            self.assertIn(value, h2)
        for value in (
            "font-size: 22px;",
            "font-weight: 600;",
            "line-height: 1.25;",
            "letter-spacing: -.025em;",
            "margin: 28px 0 9px;",
        ):
            self.assertIn(value, h3)
        for value in (
            "font-size: 1em;",
            "font-weight: 700;",
            "line-height: inherit;",
            "letter-spacing: normal;",
            "margin: 1.33em 0;",
        ):
            self.assertIn(value, h4)
        for value in (
            "font-size: .83em;",
            "font-weight: 700;",
            "line-height: inherit;",
            "letter-spacing: normal;",
            "margin: 1.67em 0;",
        ):
            self.assertIn(value, h5)
        for value in (
            "font-size: 13px;",
            "font-weight: 850;",
            "line-height: 1.82;",
            "letter-spacing: .15em;",
            "text-transform: uppercase;",
            "margin: 0 0 14px;",
            "color: #39463d;",
        ):
            self.assertIn(value, eyebrow)
        self.assertIn("content: none;", no_rule)
        self.assertIn("display: none;", no_rule)
        self.assertIn("@media (max-width: 560px)", parity_css)
        self.assertIn("font-size: 27px;", parity_css)
        self.assertIn("font-size: 20px;", parity_css)

    def test_rich_editor_canvas_fills_workspace_and_preserves_reading_measure(self):
        backend = Path(__file__).resolve().parents[2]
        parity_css = (backend / "static" / "academy" / "course-template-parity.css").read_text(
            encoding="utf-8"
        )

        # The editable surface is full width; the 730px limit applies to lesson content.
        canvas_start = parity_css.index(".rich-editor-canvas {")
        canvas_end = parity_css.index("}", canvas_start) + 1
        canvas_rule = parity_css[canvas_start:canvas_end]
        self.assertIn("width: 100%;", canvas_rule)
        self.assertIn("max-width: none;", canvas_rule)
        self.assertIn("box-sizing: border-box;", canvas_rule)
        self.assertNotIn("max-width: 730px;", canvas_rule)

        self.assertIn(
            ".tt-learning-room .tt-lesson-idea-copy,\n.preview-body {",
            parity_css,
        )
        self.assertIn("max-width: 730px;", parity_css)
        for selector in (
            ".rich-editor-canvas > p,",
            ".rich-editor-canvas > ul,",
            ".rich-editor-canvas > ol,",
            ".rich-editor-canvas > blockquote,",
            ".rich-editor-canvas > hr,",
            ".rich-editor-canvas > table,",
            ".rich-editor-canvas > .lesson-table-wrap,",
            ".rich-editor-canvas > .tt-editor-table-scroll",
        ):
            with self.subTest(selector=selector):
                self.assertIn(selector, parity_css)

    def test_course_builder_content_blocks_match_learner_treatment(self):
        backend = Path(__file__).resolve().parents[2]
        parity_css = (backend / "static" / "academy" / "course-template-parity.css").read_text(
            encoding="utf-8"
        )
        builder_source = (backend / "apps" / "academy" / "course_builder_preview.html").read_text(
            encoding="utf-8"
        )
        learner_css = (backend / "static" / "academy" / "learning-room.css").read_text(
            encoding="utf-8"
        )

        # The parity stylesheet loads after the builder's embedded component styles.
        parity_link = builder_source.index("/static/academy/course-template-parity.css")
        self.assertGreater(parity_link, builder_source.index("</style>"))
        self.assertLess(parity_link, builder_source.index("</head>"))
        self.assertIn("/* Hard-block index — exact approved design. */", parity_css)
        self.assertEqual(
            1,
            parity_css.count("/* Hard-block index — exact approved design. */"),
            "Hard-block Index styling must have one shared source of truth.",
        )
        self.assertNotIn("/* Hard-block index — exact approved design. */", learner_css)
        self.assertNotIn("/* Hard-block index — exact approved design. */", builder_source)
        self.assertIn(
            ".tt-tab-panel .tt-purpose-figure:not(.tt-image-group-hard-index),",
            learner_css,
        )
        self.assertIn(
            ".tt-learning-room .tt-tab-panel .tt-purpose-figure:not(.tt-image-group-hard-index),",
            learner_css,
        )
        self.assertIn(
            ".preview-body .tt-purpose-figure:not(.tt-image-group-hard-index) {",
            builder_source,
        )
        self.assertNotIn(".preview-body .tt-purpose-figure {", builder_source)
        for selector in (
            ".rich-editor-canvas blockquote {",
            ".rich-editor-canvas blockquote::before {",
            ".rich-editor-canvas table {",
            ".rich-editor-canvas table th {",
            ".rich-editor-canvas table tbody tr:nth-child(odd) td {",
            ".rich-editor-canvas table tbody tr:nth-child(even) td {",
            ".rich-editor-canvas .tt-editor-table-scroll table,",
            ".rich-editor-canvas table.tt-editor-structured-table {",
        ):
            self.assertIn(selector, parity_css)
        self.assertIn(".tt-learning-room .tt-lesson-idea-copy,\n.preview-body {", parity_css)
        self.assertIn(".rich-editor-canvas {", parity_css)
        self.assertIn("max-width: none;", parity_css)
        self.assertIn("table.tt-auto-layout", parity_css)
        self.assertIn("overflow-wrap: normal;", parity_css)
        self.assertIn(".tt-table-resize-handle", parity_css)
        self.assertIn('data-rich-table-action="auto-fit"', builder_source)
        self.assertNotIn('data-rich-table-action="delete-table"', builder_source)
        self.assertIn(".tt-editor-table-delete", builder_source)
        self.assertIn("button.dataset.richTableAction = 'delete-table'", builder_source)
        self.assertIn(".tt-editor-table-editable-wrap:hover > .tt-editor-table-delete", builder_source)
        self.assertIn(".tt-editor-table-editable-wrap.is-active > .tt-editor-table-delete", builder_source)
        self.assertIn("node.hasAttribute('data-editor-ui')", builder_source)
        self.assertIn("action==='delete-table'", builder_source)
        self.assertIn("delete lesson.tables[tableId]", builder_source)
        self.assertIn("tableContainer.replaceWith(placeholder)", builder_source)
        self.assertIn("syncVisualEditorToModel(editor)", builder_source)
        self.assertIn("data-table-resize-handle", builder_source)
        for selector in (
            ".tt-learning-room .tt-tab-panel h6,",
            ".tt-learning-room .tt-lesson-idea-copy h6,",
            ".preview-body h6,",
            ".rich-editor-canvas h6,",
            ".rich-editor-canvas h6::before,",
        ):
            with self.subTest(selector=selector):
                self.assertIn(selector, parity_css)
        for legacy_selector in (
            ".tt-learning-room .tt-lesson-idea-copy > h6:first-of-type,",
            ".preview-body > h6:first-of-type,",
            ".rich-editor-canvas > h6:first-of-type,",
        ):
            with self.subTest(legacy_selector=legacy_selector):
                self.assertNotIn(legacy_selector, parity_css)
        quote_start = parity_css.index(".tt-learning-room .tt-tab-panel blockquote,")
        quote_end = parity_css.index(".tt-learning-room .tt-tab-panel blockquote p,")
        quote_rule = parity_css[quote_start:quote_end]
        self.assertIn("min-height: 64px;", quote_rule)
        self.assertIn("padding: 0 0 0 92px;", quote_rule)
        self.assertIn("font-size: 20px;", parity_css)
        self.assertNotIn("font-size: 18px;", parity_css)
        self.assertNotIn("Quote Option 2: the chosen large editorial pull quote.", (backend / "static" / "academy" / "learning-room.css").read_text(encoding="utf-8"))
        self.assertIn("border: 0;", quote_rule)
        self.assertIn('font: 400 clamp(20px, 2.2vw, 27px)/1.5 Georgia, "Times New Roman", serif;', quote_rule)

        opening_quote_start = parity_css.index(".tt-learning-room .tt-tab-panel blockquote::after,")
        opening_quote_end = parity_css.index(
            ".tt-learning-room .tt-tab-panel blockquote p,", opening_quote_start
        )
        opening_quote_rule = parity_css[opening_quote_start:opening_quote_end]
        self.assertIn('content: "“";', opening_quote_rule)
        self.assertIn('font: 400 34px/.8 Georgia, "Times New Roman", serif;', opening_quote_rule)
        self.assertIn("pointer-events: none;", opening_quote_rule)

        margin_label_start = parity_css.index(".tt-learning-room .tt-tab-panel blockquote::before,")
        margin_label_end = parity_css.index(".tt-learning-room .tt-tab-panel blockquote p,")
        margin_label_rule = parity_css[margin_label_start:margin_label_end]
        self.assertIn('content: "CONTEXT FIRST";', margin_label_rule)
        self.assertIn("border-right: 1px solid #c9d8d2;", margin_label_rule)
        self.assertIn("writing-mode: vertical-rl;", margin_label_rule)

        for value in (
            "background: #345943;",
            "border-bottom: 2px solid #b48635;",
            "background: #f3f0e6;",
            "background: #e8eee4;",
        ):
            self.assertIn(value, parity_css)
        for legacy_rule in (
            ".preview-body blockquote {",
            ".preview-body blockquote::before {",
            ".rich-editor-canvas blockquote { margin:14px 0;",
            ".rich-editor-canvas table { width:100%; border-collapse:collapse;",
            ".rich-editor-canvas th,.rich-editor-canvas td { border:1px solid var(--line);",
            ".rich-editor-canvas th { background:var(--panel-soft);",
            ".rich-editor-canvas .tt-editor-structured-table thead tr:last-child th { background:#e8eee3;",
        ):
            self.assertNotIn(legacy_rule, builder_source)

    def test_builder_learner_preview_uses_the_saved_academy_website_template(self):
        builder = Path(__file__).resolve().parent / "course_builder_preview.html"
        source = builder.read_text(encoding="utf-8")
        start = source.index("function previewFields(c)")
        end = source.index("function renderCatalogue()", start)
        preview = source[start:end]

        self.assertIn("data-builder-website-preview", preview)
        self.assertIn("data-builder-website-preview-frame", preview)
        self.assertIn("data-website-preview-status", preview)
        self.assertIn("data-website-preview-error", preview)
        self.assertIn('data-action="refresh-website-preview"', preview)
        self.assertNotIn("builder-lesson-preview-grid", preview)
        self.assertNotIn("notebookPreviewMarkup(lesson)", preview)
        self.assertNotIn("lesson.questions.length?", preview)
        self.assertIn("async function refreshBuilderWebsitePreview(force = false)", source)
        self.assertIn("saveCurrentToAcademy(false)", source)
        self.assertIn("previewUrl.origin !== window.location.origin", source)
        self.assertIn("preview_audience", source)
        self.assertIn("moduleIndex + 1", source)
        self.assertIn("lessonIndex + 1", source)

    def test_builder_notebook_chart_examples_shortcut_is_present_and_wired(self):
        builder = Path(__file__).resolve().parent / "course_builder_preview.html"
        source = builder.read_text(encoding="utf-8")
        start = source.index("function notebookPreviewMarkup(lesson)")
        end = source.index("function previewFields(c)", start)
        notebook_renderer = source[start:end]

        section_close = notebook_renderer.index("'</section>'")
        action_button = notebook_renderer.index('data-action="preview-chart-examples"')
        self.assertLess(section_close, action_button)
        self.assertIn("preview-notebook-examples-button", notebook_renderer)
        self.assertIn("data-preview-lesson-content", source)
        self.assertIn("action === 'preview-chart-examples'", source)
        self.assertIn(
            "querySelector('.tt-purpose-figure, .tt-image-group-figure, .tt-comparison-figure')",
            source,
        )
        self.assertIn("target.scrollIntoView({behavior:'smooth', block:'start'})", source)
        self.assertIn(".preview-notebook-examples-button {", source)


class LessonSectionRoutingAndFigureCountTests(SimpleTestCase):
    def test_h2_heading_can_start_a_chart_examples_section(self):
        source = (
            "## Start with the question\n\n"
            "Opening idea.\n\n"
            "## Chart examples\n\n"
            "A separate worked example."
        )
        result = build_lesson_sections(source)
        self.assertIn("Opening idea.", result["idea_html"])
        self.assertIn("A separate worked example.", result["examples_html"])
        self.assertNotIn("A separate worked example.", result["idea_html"])

    def test_figure_count_includes_markdown_group_members_and_comparison_blocks(self):
        source = "\n\n".join(
            [
                "### The lead visual",
                "![Lead chart](https://example.com/lead.png)",
                "### Additional chart examples",
                "[[image-group:range-trend]]",
                "[[teaching-figure:settings-comparison]]",
            ]
        )
        metadata = {
            "range-trend": {
                "type": "image-group",
                "title": "Range versus trend",
                "image_ids": ["asset-a", "asset-b"],
            },
            "settings-comparison": {
                "type": "comparison-cards",
                "title": "Compare settings",
                "cards": [
                    {"kicker": "SHORTER", "title": "Responsive", "body": "Moves sooner."},
                    {"kicker": "LONGER", "title": "Smoother", "body": "Moves slower."},
                ],
            },
            "asset-a": {"title": "Range example", "alt": "A range"},
            "asset-b": {"title": "Trend example", "alt": "A trend"},
        }
        result = build_lesson_sections(
            source,
            asset_urls={
                "asset-a": "https://example.com/range.png",
                "asset-b": "https://example.com/trend.png",
            },
            figure_metadata=metadata,
        )
        self.assertEqual(result["figure_count"], 4)
        self.assertIn("Range versus trend", result["examples_html"])
        self.assertIn("Compare settings", result["examples_html"])

    def test_reused_structured_figures_are_counted_per_displayed_instance(self):
        source = "\n\n".join(
            [
                "### Additional chart examples",
                "[[image-group:range-trend]]",
                "[[image-group:range-trend]]",
                "[[teaching-figure:settings-comparison]]",
                "[[teaching-figure:settings-comparison]]",
            ]
        )
        metadata = {
            "range-trend": {"type": "image-group", "image_ids": ["asset-a", "asset-b"]},
            "settings-comparison": {"type": "comparison-cards", "cards": [{"title": "Short"}]},
        }
        result = build_lesson_sections(source, figure_metadata=metadata)
        self.assertEqual(result["figure_count"], 6)


class TemplateParityRegressionTests(SimpleTestCase):
    def test_explicit_tab_marker_overrides_ambiguous_heading_heuristics(self):
        source = (
            "## Opening explanation\n\n"
            "Keep the core idea in the first tab.\n\n"
            "[[lesson-tab:examples]]\n\n"
            "## Relative volume context\n\n"
            "This comparison belongs in chart examples even though the heading is ambiguous.\n\n"
            "[[lesson-tab:practice]]\n\n"
            "## What would change your view\n\n"
            "Name the next evidence before acting."
        )
        result = build_lesson_sections(source)
        self.assertIn("Keep the core idea", result["idea_html"])
        self.assertIn("This comparison belongs in chart examples", result["examples_html"])
        self.assertIn("Name the next evidence", result["practice_html"])
        for rendered in (result["idea_html"], result["examples_html"], result["practice_html"]):
            self.assertNotIn("[[lesson-tab:", rendered)

    def test_empty_non_bollinger_notebook_gets_topic_neutral_prompts(self):
        notebook = _notebook_for_course_display("volume-price-analysis", {})
        self.assertEqual(len(notebook["prompts"]), 3)
        self.assertEqual(notebook["prompts"][0]["label"], "Describe")
        self.assertEqual(notebook["prompts"][0]["text"], "What evidence is visible?")
        self.assertNotIn("bands", " ".join(item["text"] for item in notebook["prompts"]).lower())

    def test_legacy_generic_notebook_prompts_migrate_to_describe_apply(self):
        notebook = _notebook_for_course_display(
            "support-resistance",
            {
                "title": "Your Trading Notebook",
                "prompts": [
                    {"label": "Observe", "text": "Describe the evidence visible in the chart."},
                    {
                        "label": "Interpret",
                        "text": "State one possible reading and a reasonable alternative.",
                    },
                    {
                        "label": "Test",
                        "text": "Name the next evidence that would strengthen or weaken your reading.",
                    },
                ],
            },
        )
        self.assertEqual(notebook["prompts"][0]["label"], "Describe")
        self.assertEqual(notebook["prompts"][2]["label"], "Apply")

    def test_bollinger_default_notebook_retains_course_specific_prompts(self):
        notebook = _notebook_for_course_display(
            "understand-bollinger-bands",
            {"title": "Your Trading Notebook", "prompts": []},
        )
        self.assertEqual(notebook["title"], "Your Trading Notebook")
        self.assertIn("bands", " ".join(item["text"] for item in notebook["prompts"]).lower())
        self.assertEqual(notebook["prompts"][2]["label"], "Apply")


class LessonSectionRoutingRegressionTests(SimpleTestCase):
    def test_concept_heading_compare_the_possibilities_stays_in_the_idea_panel(self):
        source = (
            "## Start with the decision\n\n"
            "Begin with a practical question.\n\n"
            "### What to notice\n\n"
            "Describe the visible evidence.\n\n"
            "### Compare the possibilities\n\n"
            "Compare two possible readings and the evidence that separates them."
        )
        result = build_lesson_sections(source)
        self.assertIn("Compare the possibilities", result["idea_html"])
        self.assertNotIn("Compare the possibilities", result["examples_html"])


class CourseBuilderToolbarRegressionTests(SimpleTestCase):
    def test_visual_editor_toolbar_sticks_and_table_tools_are_contextual(self):
        backend = Path(__file__).resolve().parents[2]
        builder_source = (
            backend / "apps" / "academy" / "course_builder_preview.html"
        ).read_text(encoding="utf-8")

        # The editor shell must clip rounded edges without trapping position:sticky.
        self.assertRegex(
            builder_source,
            r"\.editor-shell\s*\{[^}]*overflow:clip;",
        )
        self.assertRegex(
            builder_source,
            r"\.rich-editor-toolbar\s*\{\s*position:sticky;\s*top:10px;",
        )

        # Insertion remains available; destructive/structural table actions are hidden
        # until the caret or selection is inside a table.
        toolbar_start = builder_source.index('<div class="rich-editor-toolbar"')
        table_tools_start = builder_source.index(
            'data-rich-table-tools hidden role="group"',
            toolbar_start,
        )
        table_tools_end = builder_source.index("</div>", table_tools_start)
        self.assertLess(
            builder_source.index('data-rich-command="grouped-table"', toolbar_start),
            table_tools_start,
        )
        for action in (
            "auto-fit",
            "add-column",
            "add-row",
            "remove-column",
            "remove-row",
            "group-headers",
        ):
            with self.subTest(action=action):
                action_position = builder_source.index(
                    'data-rich-table-action="' + action + '"',
                    table_tools_start,
                )
                self.assertLess(action_position, table_tools_end)

        # Selection changes update the contextual tools and active formatting states.
        capture_start = builder_source.index("function captureRichEditorRange()")
        capture_end = builder_source.index(
            "function rememberRichEditorCaretOffset()",
            capture_start,
        )
        capture_function = builder_source[capture_start:capture_end]
        self.assertIn("syncRichToolbarStateFromSelection(editor, selection);", capture_function)
        self.assertIn("updateRichTableToolbar(editor);", capture_function)
        self.assertIn("tools.hidden = true;", capture_function)
        self.assertIn("function updateRichTableToolbar(editor, tableOverride)", builder_source)
        self.assertIn(
            "const table = arguments.length > 1 ? tableOverride : selectedEditorTable(editor);",
            builder_source,
        )
        self.assertIn("updateRichTableToolbar(editor, table);", builder_source)
        self.assertIn("updateRichTableToolbar(editor, null);", builder_source)
        self.assertIn(
            "button.setAttribute('aria-pressed', pressed ? 'true' : 'false');",
            builder_source,
        )
        for command in (
            "bold",
            "italic",
            "underline",
            "strikeThrough",
            "insertUnorderedList",
            "insertOrderedList",
        ):
            with self.subTest(command=command):
                self.assertIn('data-rich-command="' + command + '"', builder_source)

class CourseBuilderFormatPreservationRegressionTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        backend = Path(__file__).resolve().parents[2]
        cls.builder_source = (
            backend / "apps" / "academy" / "course_builder_preview.html"
        ).read_text(encoding="utf-8")

    def test_underline_and_inline_code_survive_editor_round_trip(self):
        source = self.builder_source
        self.assertIn("if (tag === 'u') return '<u>' + inner + '</u>'", source)
        self.assertIn("source.replace(/<u>([\\s\\S]*?)<\\/u>/gi", source)
        self.assertIn("if (tag === 'code') return", source)
        self.assertIn("protectedMarkup[Number(index)]", source)

    def test_list_parser_index_binding_is_in_scope_for_recursive_parser(self):
        source = self.builder_source
        parser_position = source.index("const parseList = baseIndent =>")
        index_binding_position = source.index("let index = 0;", parser_position - 4000)
        loop_position = source.index("for (; index < lines.length;)", index_binding_position)
        self.assertLess(index_binding_position, parser_position)
        self.assertLess(parser_position, loop_position)
        self.assertNotIn("for (let index = 0; index < lines.length;)", source)

    def test_nested_and_start_numbered_lists_are_preserved(self):
        source = self.builder_source
        self.assertIn("function richListMarkdown(list, depth=0)", source)
        self.assertIn("const nestedLists = Array.from(item.children)", source)
        self.assertIn("item.nested.join('')", source)
        self.assertIn("const listMarkerMatch = line =>", source)
        self.assertIn("const parseList = baseIndent =>", source)
        self.assertIn("const startAttribute = tag === 'ol'", source)
        self.assertIn("const listMarker = listMarkerMatch(line);", source)

    def test_code_block_language_and_long_fences_are_preserved(self):
        source = self.builder_source
        self.assertIn("const languageClass = Array.from(code?.classList || []).find", source)
        self.assertIn("const longestFence = Math.max", source)
        self.assertIn("return fence + language + '\\n' + codeText + '\\n' + fence;", source)
        self.assertIn("const isFence = line =>", source)

    def test_simple_and_structured_table_alignment_are_preserved(self):
        source = self.builder_source
        self.assertIn("const alignments = Array.from({length:width}", source)
        self.assertIn("const dividerCells = alignments.map", source)
        self.assertIn("function tableCellMarkup(tag,text,colspan,rowspan,alignment)", source)
        self.assertIn("align:['left','center','right']", source)
        self.assertIn("function editorTableNeedsStructuredStorage(table)", source)
        self.assertIn("function promoteComplexEditorTables(editor)", source)
        self.assertIn("promoteComplexEditorTables(editor);", source)
        self.assertIn("if (node.isConnected) refreshStructuredTableMetadata(node);", source)
        self.assertNotIn("ensureStructuredTableForResize(node)", source)


    def test_embedded_course_builder_javascript_passes_node_syntax_check(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is unavailable in this test environment.")
        scripts = re.findall(
            r"<script\b[^>]*>(.*?)</script>",
            self.builder_source,
            flags=re.DOTALL,
        )
        self.assertTrue(scripts, "The Course Builder preview should include its editor script.")
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".js",
            encoding="utf-8",
            delete=False,
        ) as script_file:
            script_file.write("\n;\n".join(scripts))
            script_path = Path(script_file.name)
        try:
            result = subprocess.run(
                [node, "--check", str(script_path)],
                capture_output=True,
                text=True,
                check=False,
            )
        finally:
            script_path.unlink(missing_ok=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_obsolete_textarea_caret_handler_is_not_retained(self):
        source = self.builder_source
        self.assertNotIn("rememberLessonContentCaret", source)
        self.assertNotIn('textarea[data-entity="lesson"][data-field="content"]', source)
        # The contenteditable editor still has its active selection-to-Markdown path.
        self.assertIn("function rememberRichEditorCaretOffset()", source)
        self.assertIn("visualEditorToMarkdown(prefix)", source)
        self.assertIn("insertVisualTokenAtCursor(visualEditor, token, isBlock)", source)

