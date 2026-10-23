import re
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

    def test_whole_lesson_body_uses_country_then_region_then_main_fallback(self):
        source = "Main lesson body."
        overrides = {
            "country:IN": "India lesson body.\n\n| Market | Example |\n|---|---|\n| India | NIFTY |",
            "region:APAC": "APAC lesson body.",
        }

        india = build_lesson_sections(
            source, regional_content=overrides, country_code="IN", region_code="APAC",
        )
        australia = build_lesson_sections(
            source, regional_content=overrides, country_code="AU", region_code="APAC",
        )
        unknown = build_lesson_sections(
            source, regional_content=overrides, country_code="ZZ", region_code=None,
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
                    {"scope": "region", "code": "APAC", "content": "APAC disclosure.", "hidden": False},
                    {"scope": "country", "code": "IN", "content": "India disclosure.", "hidden": False},
                ],
            }
        }
        india = build_lesson_sections(source, regional_blocks=blocks, country_code="IN", region_code="APAC")
        australia = build_lesson_sections(source, regional_blocks=blocks, country_code="AU", region_code="APAC")
        unknown = build_lesson_sections(source, regional_blocks=blocks, country_code="ZZ", region_code=None)
        self.assertIn("India disclosure.", india["idea_html"])
        self.assertIn("APAC disclosure.", australia["idea_html"])
        self.assertIn("Global disclosure.", unknown["idea_html"])
        self.assertNotIn("[[regional-block:", india["idea_html"])

    def test_regional_block_can_be_explicitly_hidden_for_a_matching_country(self):
        source = "## Disclosure\n\nBefore.\n\n[[regional-block:notice]]\n\nAfter."
        blocks = {"notice": {"id": "notice", "base_content": "Global notice.", "variants": [
            {"scope": "country", "code": "CA", "content": "unused", "hidden": True},
            {"scope": "region", "code": "NA", "content": "North American notice."}
        ]}}
        canada = build_lesson_sections(source, regional_blocks=blocks, country_code="CA", region_code="NA")
        us = build_lesson_sections(source, regional_blocks=blocks, country_code="US", region_code="NA")
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
        source = "\n".join([
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
        ])

        sections = build_lesson_sections(source)

        self.assertIn("What to notice", sections["idea_html"])
        self.assertIn("Separate the visible evidence", sections["idea_html"])
        self.assertIn("Compare the possibilities", sections["idea_html"])
        self.assertIn("Use a second case", sections["idea_html"])
        self.assertNotIn("Separate the visible evidence", sections["examples_html"])
        self.assertNotIn("Use a second case", sections["practice_html"])
        self.assertNotIn("[[lesson-tab:", sections["idea_html"] + sections["examples_html"] + sections["practice_html"])

    def test_explicit_tab_route_applies_to_the_heading_after_the_marker(self):
        source = "\n".join([
            "## Start with the decision",
            "",
            "Introduction remains in the idea tab.",
            "",
            "[[lesson-tab:practice]]",
            "",
            "### What to notice",
            "",
            "This heading and its paragraph are intentionally routed to practice.",
        ])

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
        self.assertLess(rendered.index("Text before the figure."), rendered.index('class="tt-purpose-figure"'))
        self.assertLess(rendered.index('class="tt-purpose-figure"'), rendered.index("Text after the figure."))
        self.assertIn("What changing the settings changes", rendered)
        self.assertIn("MODULE 5 · Build and trade setups", rendered)
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
        self.assertNotIn("TRADETHESIS · LEARNING ROOM", rendered)
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
        self.assertIn("groupedReference", preview)
        self.assertIn("imageGroups.some", preview)
        self.assertNotIn("TRADETHESIS · LEARNING ROOM", preview)
        self.assertIn("tt-purpose-figure-module", preview)
        self.assertIn("data-image-storage-status", preview)
        self.assertIn("compactDuplicateCourseCards(resolveBuilderRegionalBlocks(String(src || '')", preview)
        self.assertIn("result.asset_storage", preview)
        self.assertIn("Image uploads are blocked because no durable image provider is configured", preview)


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
            course_title="Understand Bollinger Bands",
        )
        figure_index = rendered.index("tt-image-group-figure")
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
        self.assertIn(
            'class="tt-image-group-context" title="Understand Bollinger Bands">Understand Bollinger Bands</span>',
            rendered,
        )
        self.assertNotIn("2 images · compare before interpreting", rendered)
        self.assertEqual(rendered.count('class="tt-image-group-case-id"'), 2)
        self.assertIn("tt-image-group-item-heading", rendered)

    def test_image_groups_use_borderless_compact_layout_in_builder_and_learner(self):
        root = Path(__file__).resolve().parents[2]
        learner_css = (root / "static" / "academy" / "learning-room.css").read_text(encoding="utf-8")
        builder_html = (root / "apps" / "academy" / "course_builder_preview.html").read_text(encoding="utf-8")

        self.assertIn("Image-group Option 3 — borderless, compact chart group", learner_css)
        self.assertIn("Image-group Option 3 — borderless compact chart group, matching the learner view.", builder_html)
        self.assertIn("const courseTitleLabel = String(course?.title || 'Course')", builder_html)
        self.assertIn("text-overflow:ellipsis", builder_html)
        self.assertIn("text-overflow:ellipsis", learner_css)

        for source in (learner_css, builder_html):
            self.assertIn("border:0", source)
            self.assertIn("aspect-ratio:auto", source)
            self.assertIn("height:auto", source)
            self.assertIn("grid-template-columns:repeat(2,minmax(0,1fr))", source)
            self.assertIn("counter-reset:image-group-case", source)
            self.assertIn("content:counter(image-group-case, upper-alpha)", source)
            self.assertIn(".tt-image-group-item:nth-child(odd)", source)
            self.assertIn(".tt-image-group-item:nth-child(n+3)", source)
            self.assertIn(".tt-image-group-item:last-child:nth-child(odd)", source)
            self.assertIn(".tt-image-group-item-heading", source)
            self.assertIn(".tt-image-group-context", source)
            self.assertIn("grid-template-columns:minmax(0,1fr)", source)
            self.assertIn(".tt-image-group-item:not(:last-child)", source)
            self.assertNotIn(".tt-image-group-item:nth-child(odd) { border-right:1px solid", source)
            self.assertNotIn(".tt-image-group-item:nth-child(n+3) { border-top:1px solid", source)
            self.assertNotIn(".tt-image-group-item:not(:last-child) { border-bottom:1px solid", source)

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

    def test_structured_grouped_table_renders_spans_and_accessible_wrapper(self):
        source = "Opening copy.\n\n[[table-block:market-comparison]]\n\nClosing copy."
        rendered = render_safe_markdown(
            source,
            table_metadata={
                "market-comparison": {
                    "title": "Market comparison",
                    "rows": [
                        {"section": "head", "cells": [
                            {"text": "Context", "colspan": 2, "rowspan": 1, "header": True},
                            {"text": "Decision", "colspan": 2, "rowspan": 1, "header": True},
                        ]},
                        {"section": "head", "cells": [
                            {"text": "Market", "colspan": 1, "rowspan": 1, "header": True},
                            {"text": "Evidence", "colspan": 1, "rowspan": 1, "header": True},
                            {"text": "If confirmed", "colspan": 1, "rowspan": 1, "header": True},
                            {"text": "If rejected", "colspan": 1, "rowspan": 1, "header": True},
                        ]},
                        {"section": "body", "cells": [
                            {"text": "Range", "colspan": 1, "rowspan": 1, "header": False},
                            {"text": "Repeated rejection", "colspan": 1, "rowspan": 1, "header": False},
                            {"text": "Wait for follow-through", "colspan": 1, "rowspan": 1, "header": False},
                            {"text": "Reassess the range", "colspan": 1, "rowspan": 1, "header": False},
                        ]},
                    ],
                }
            },
        )
        self.assertIn('class="lesson-table-wrap tt-structured-table-wrap"', rendered)
        self.assertIn('aria-label="Scrollable table: Market comparison"', rendered)
        self.assertIn('colspan="2" scope="colgroup"', rendered)
        self.assertIn("Repeated rejection", rendered)
        self.assertIn("Opening copy.", rendered)
        self.assertIn("Closing copy.", rendered)
        self.assertNotIn("[[table-block:", rendered)

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
        self.assertIn("<table>", rendered)
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
        self.assertIn('contenteditable="true" spellcheck="true"', preview)
        self.assertIn('data-rich-command="table" aria-label="Insert table">Table', preview)
        self.assertIn('data-visual-editor="true"', preview)
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
    def test_notebook_is_inside_the_idea_panel_before_chart_examples_action(self):
        template = (
            Path(__file__).resolve().parents[2]
            / "templates"
            / "academy"
            / "partials"
            / "lesson_tabs.html"
        )
        source = template.read_text(encoding="utf-8")
        idea = source.index('data-tab-panel="idea"')
        notebook = source.index('class="tt-notebook"')
        action = source.index('data-open-tab="examples"')
        examples = source.index('data-tab-panel="examples"')

        self.assertLess(idea, notebook)
        self.assertLess(notebook, action)
        self.assertLess(action, examples)
        self.assertEqual(source.count('class="tt-notebook"'), 1)
        self.assertIn("Before treating a touch as a setup", source)
        self.assertIn("Where is price relative to the bands and middle line?", source)
        self.assertIn("What would change your view?", source)
        self.assertIn("<strong>Apply.</strong>", source)

    def test_notebook_styling_and_chart_tab_action_are_wired(self):
        backend = Path(__file__).resolve().parents[2]
        styles = (backend / "static" / "academy" / "learning-room.css").read_text(encoding="utf-8")
        script = (backend / "static" / "academy" / "learning-room.js").read_text(encoding="utf-8")

        self.assertIn(".tt-learning-room .tt-notebook-index", styles)
        self.assertIn(".tt-learning-room .tt-notebook-examples-button", styles)
        self.assertIn("@media(max-width:620px)", styles)
        self.assertIn('event.target.closest("[data-open-tab]")', script)
        self.assertIn('form = event.target.closest("[data-notebook-response]")', script)

    def test_builder_learner_preview_renders_notebook_before_practice_questions(self):
        builder = Path(__file__).resolve().parent / "course_builder_preview.html"
        source = builder.read_text(encoding="utf-8")
        start = source.index("function previewFields(c)")
        end = source.index("function renderMarkdown(src)", start)
        preview = source[start:end]

        lesson_body = preview.index("renderMarkdown(lessonBodyForAudience(lesson,")
        notebook = preview.index("notebookPreviewMarkup(lesson)")
        questions = preview.index("lesson.questions.length?")
        self.assertLess(lesson_body, notebook)
        self.assertLess(notebook, questions)
        self.assertEqual(preview.count("notebookPreviewMarkup(lesson)"), 1)

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
        self.assertIn("querySelector('.tt-purpose-figure, .tt-image-group-figure, .tt-comparison-figure')", source)
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
        source = "\n\n".join([
            "### The lead visual",
            "![Lead chart](https://example.com/lead.png)",
            "### Additional chart examples",
            "[[image-group:range-trend]]",
            "[[teaching-figure:settings-comparison]]",
        ])
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
        source = "\n\n".join([
            "### Additional chart examples",
            "[[image-group:range-trend]]",
            "[[image-group:range-trend]]",
            "[[teaching-figure:settings-comparison]]",
            "[[teaching-figure:settings-comparison]]",
        ])
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
            {"title": "Your Trading Notebook", "prompts": [
                {"label": "Observe", "text": "Describe the evidence visible in the chart."},
                {"label": "Interpret", "text": "State one possible reading and a reasonable alternative."},
                {"label": "Test", "text": "Name the next evidence that would strengthen or weaken your reading."},
            ]},
        )
        self.assertEqual(notebook["prompts"][0]["label"], "Describe")
        self.assertEqual(notebook["prompts"][2]["label"], "Apply")

    def test_bollinger_default_notebook_retains_course_specific_prompts(self):
        notebook = _notebook_for_course_display(
            "understand-bollinger-bands",
            {"title": "Your Trading Notebook", "prompts": []},
        )
        self.assertEqual(notebook["title"], "Before treating a touch as a setup")
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
