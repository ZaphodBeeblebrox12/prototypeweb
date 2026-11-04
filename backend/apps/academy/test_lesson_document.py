from django.test import SimpleTestCase

from .lesson_document import (
    DOCUMENT_FORMAT,
    DOCUMENT_SCHEMA_VERSION,
    LESSON_SIDECAR_KEYS,
    LessonDocumentValidationError,
    is_lesson_document,
    new_lesson_document,
    validate_lesson_document,
)


class LessonDocumentContractTests(SimpleTestCase):
    def test_new_document_uses_a_versioned_tiptap_envelope(self):
        document = new_lesson_document()
        self.assertEqual(document["format"], DOCUMENT_FORMAT)
        self.assertEqual(document["schema_version"], DOCUMENT_SCHEMA_VERSION)
        self.assertEqual(document["content"]["type"], "doc")
        self.assertEqual(document["content"]["content"][0]["type"], "paragraph")
        self.assertTrue(is_lesson_document(document))

    def test_common_formatting_and_nested_lists_are_valid(self):
        document = new_lesson_document(
            {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Lesson title"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Careful reading",
                                "marks": [
                                    {"type": "bold"},
                                    {"type": "italic"},
                                    {"type": "underline"},
                                ],
                            },
                            {"type": "text", "text": " and "},
                            {"type": "text", "text": "code", "marks": [{"type": "code"}]},
                        ],
                    },
                    {
                        "type": "orderedList",
                        "attrs": {"start": 3},
                        "content": [
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Top level"}],
                                    },
                                    {
                                        "type": "bulletList",
                                        "content": [
                                            {
                                                "type": "listItem",
                                                "content": [
                                                    {
                                                        "type": "paragraph",
                                                        "content": [{"type": "text", "text": "Nested"}],
                                                    }
                                                ],
                                            }
                                        ],
                                    },
                                ],
                            }
                        ],
                    },
                ],
            }
        )
        validated = validate_lesson_document(document)
        self.assertEqual(validated["content"]["content"][2]["attrs"]["start"], 3)

    def test_table_cells_preserve_merges_width_and_alignment(self):
        document = new_lesson_document(
            {
                "type": "doc",
                "content": [
                    {
                        "type": "table",
                        "attrs": {"columnWidths": [120, 180, 160], "layout": "fixed"},
                        "content": [
                            {
                                "type": "tableRow",
                                "content": [
                                    {
                                        "type": "tableHeader",
                                        "attrs": {
                                            "colspan": 2,
                                            "rowspan": 1,
                                            "colwidth": [120, 180],
                                            "align": "center",
                                            "verticalAlign": "middle",
                                        },
                                        "content": [
                                            {
                                                "type": "paragraph",
                                                "content": [{"type": "text", "text": "Group header"}],
                                            }
                                        ],
                                    },
                                    {
                                        "type": "tableHeader",
                                        "attrs": {"align": "right"},
                                        "content": [
                                            {
                                                "type": "paragraph",
                                                "content": [{"type": "text", "text": "Last"}],
                                            }
                                        ],
                                    },
                                ],
                            }
                        ],
                    }
                ],
            }
        )
        cell = document["content"]["content"][0]["content"][0]["content"][0]
        self.assertEqual(cell["attrs"]["colspan"], 2)
        self.assertEqual(cell["attrs"]["align"], "center")
        self.assertEqual(cell["attrs"]["colwidth"], [120, 180])

    def test_trade_thesis_reference_nodes_store_ids_not_private_urls(self):
        document = new_lesson_document(
            {
                "type": "doc",
                "content": [
                    {"type": "ttAssetImage", "attrs": {"assetId": "asset-image-01", "alt": "Chart"}},
                    {"type": "ttFigure", "attrs": {"figureId": "figure-01"}},
                    {"type": "ttRegionalBlock", "attrs": {"blockId": "risk-note"}},
                    {
                        "type": "ttLessonReference",
                        "attrs": {"lessonId": "12345678-1234-5678-1234-567812345678"},
                    },
                    {
                        "type": "ttProtectedVideo",
                        "attrs": {"videoId": "87654321-4321-8765-4321-876543218765"},
                    },
                ],
            }
        )
        self.assertTrue(is_lesson_document(document))
        self.assertNotIn("src", document["content"]["content"][0]["attrs"])

    def test_unconverted_legacy_tokens_can_be_preserved_as_visible_reference_nodes(self):
        document = new_lesson_document(
            {
                "type": "doc",
                "content": [
                    {
                        "type": "ttLegacyReference",
                        "attrs": {
                            "token": "[[unknown-widget:original-id]]",
                            "referenceKind": "unknown",
                        },
                    }
                ],
            }
        )
        self.assertTrue(is_lesson_document(document))
        self.assertEqual(
            document["content"]["content"][0]["attrs"]["token"],
            "[[unknown-widget:original-id]]",
        )

    def test_unsafe_links_are_rejected(self):
        with self.assertRaisesRegex(LessonDocumentValidationError, "unsafe link"):
            new_lesson_document(
                {
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "click",
                                    "marks": [
                                        {"type": "link", "attrs": {"href": "javascript:alert(1)"}}
                                    ],
                                }
                            ],
                        }
                    ],
                }
            )

    def test_unknown_nodes_and_attributes_are_rejected_not_dropped(self):
        with self.assertRaisesRegex(LessonDocumentValidationError, "unsupported node type"):
            new_lesson_document(
                {"type": "doc", "content": [{"type": "magicWidget"}]}
            )
        with self.assertRaisesRegex(LessonDocumentValidationError, "unsupported attribute"):
            new_lesson_document(
                {
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "attrs": {"fontFamily": "Comic Sans"},
                        }
                    ],
                }
            )

    def test_invalid_nested_content_is_rejected(self):
        with self.assertRaisesRegex(LessonDocumentValidationError, "not allowed inside"):
            new_lesson_document(
                {
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "table"}],
                        }
                    ],
                }
            )

    def test_invalid_schema_version_is_rejected(self):
        document = new_lesson_document()
        document["schema_version"] = 999
        with self.assertRaisesRegex(LessonDocumentValidationError, "schema version"):
            validate_lesson_document(document)

    def test_sidecar_feature_contract_remains_outside_the_document(self):
        self.assertTrue(
            {
                "questions",
                "tables",
                "figures",
                "asset_ids",
                "regional_blocks",
                "regional_lesson_content",
                "notebook",
                "reflection",
                "related_course_ids",
                "video_url",
            }.issubset(LESSON_SIDECAR_KEYS)
        )
