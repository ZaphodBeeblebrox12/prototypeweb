"""Tests for the versioned structured lesson-document contract."""

from copy import deepcopy

from django.test import SimpleTestCase

from apps.academy.course_builder_api import _build_import_payload
from apps.academy.lesson_document import (
    LESSON_DOCUMENT_FORMAT,
    LESSON_DOCUMENT_VERSION,
    LessonDocumentError,
    content_json_with_lesson_document,
    lesson_document_from_content_json,
    make_lesson_document,
    validate_lesson_document,
)


class LessonDocumentContractTests(SimpleTestCase):
    def test_empty_document_is_valid_and_uses_the_current_version(self):
        document = make_lesson_document()

        self.assertEqual(document["format"], LESSON_DOCUMENT_FORMAT)
        self.assertEqual(document["version"], LESSON_DOCUMENT_VERSION)
        self.assertEqual(document["document"]["type"], "doc")
        self.assertEqual(document["document"]["content"][0]["type"], "paragraph")

    def test_rich_document_accepts_course_content_nodes_and_marks(self):
        document = make_lesson_document(
            {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [
                            {
                                "type": "text",
                                "text": "Evidence first",
                                "marks": [{"type": "bold"}],
                            }
                        ],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "Read the "},
                            {
                                "type": "text",
                                "text": "source",
                                "marks": [
                                    {"type": "italic"},
                                    {
                                        "type": "link",
                                        "attrs": {"href": "https://example.com/source"},
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        "type": "table",
                        "content": [
                            {
                                "type": "tableRow",
                                "content": [
                                    {
                                        "type": "tableHeader",
                                        "attrs": {
                                            "colspan": 1,
                                            "rowspan": 1,
                                            "colwidth": [160],
                                            "align": "center",
                                        },
                                        "content": [{"type": "paragraph"}],
                                    }
                                ],
                            }
                        ],
                    },
                    {
                        "type": "regionalBlock",
                        "attrs": {"blockId": "region-apac"},
                    },
                    {
                        "type": "practiceQuestion",
                        "attrs": {"questionId": "question-1"},
                    },
                ],
            }
        )

        validated = validate_lesson_document(document)
        self.assertEqual(validated, document)

    def test_document_is_detached_before_returning(self):
        source = make_lesson_document(
            {"type": "doc", "content": [{"type": "paragraph"}]}
        )
        validated = validate_lesson_document(source)
        validated["document"]["content"].append({"type": "horizontalRule"})

        self.assertEqual(len(source["document"]["content"]), 1)

    def test_unknown_node_is_rejected_instead_of_silently_discarded(self):
        with self.assertRaisesMessage(LessonDocumentError, "unsupported node type"):
            make_lesson_document(
                {
                    "type": "doc",
                    "content": [{"type": "unknownWidget", "attrs": {"label": "Keep me"}}],
                }
            )

    def test_unknown_mark_is_rejected_instead_of_silently_discarded(self):
        with self.assertRaisesMessage(LessonDocumentError, "unsupported mark type"):
            make_lesson_document(
                {
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Keep formatting",
                                    "marks": [{"type": "unregisteredMark"}],
                                }
                            ],
                        }
                    ],
                }
            )

    def test_executable_link_schemes_are_rejected(self):
        with self.assertRaisesMessage(LessonDocumentError, "unsupported URL scheme"):
            make_lesson_document(
                {
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Unsafe",
                                    "marks": [
                                        {
                                            "type": "link",
                                            "attrs": {"href": "javascript:alert(1)"},
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                }
            )

    def test_non_finite_numbers_and_empty_root_documents_are_rejected(self):
        with self.assertRaisesMessage(LessonDocumentError, "at least one block"):
            make_lesson_document({"type": "doc", "content": []})

        with self.assertRaisesMessage(LessonDocumentError, "non-finite numbers"):
            make_lesson_document(
                {
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "attrs": {"scale": float("nan")},
                        }
                    ],
                }
            )

    def test_unsupported_and_boolean_document_versions_are_rejected(self):
        document = make_lesson_document()
        document["version"] = 99
        with self.assertRaisesMessage(LessonDocumentError, "Unsupported lesson document version"):
            validate_lesson_document(document)

        document["version"] = True
        with self.assertRaisesMessage(LessonDocumentError, "Unsupported lesson document version"):
            validate_lesson_document(document)

    def test_excessive_depth_is_rejected(self):
        node = {"type": "paragraph"}
        for _ in range(45):
            node = {"type": "blockquote", "content": [node]}

        with self.assertRaisesMessage(LessonDocumentError, "nesting is too deep"):
            make_lesson_document({"type": "doc", "content": [node]})

    def test_content_json_helpers_preserve_unrelated_legacy_fields(self):
        original = {
            "schema_version": 1,
            "regional_blocks": {"apac": {"title": "APAC"}},
            "questions": [{"id": "q1", "prompt": "Question"}],
        }
        document = make_lesson_document()
        updated = content_json_with_lesson_document(original, document)

        self.assertEqual(updated["schema_version"], 1)
        self.assertEqual(updated["regional_blocks"], original["regional_blocks"])
        self.assertEqual(updated["questions"], original["questions"])
        self.assertEqual(updated["lesson_document"], document)
        self.assertNotIn("lesson_document", original)

    def test_document_can_be_read_from_content_json_without_mutating_it(self):
        document = make_lesson_document()
        content_json = {"lesson_document": document, "asset_ids": ["asset-1"]}
        before = deepcopy(content_json)

        self.assertEqual(lesson_document_from_content_json(content_json), document)
        self.assertEqual(content_json, before)

    def test_legacy_lesson_without_document_remains_valid(self):
        self.assertIsNone(lesson_document_from_content_json({"schema_version": 1}))
        self.assertIsNone(lesson_document_from_content_json(None))

class LessonDocumentImportPayloadTests(SimpleTestCase):
    def test_builder_import_payload_carries_document_beside_markdown(self):
        document = make_lesson_document(
            {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Structured body"}],
                    }
                ],
            }
        )
        state = {
            "title": "Structured Editor Pilot",
            "accessType": "free",
            "modules": [
                {
                    "title": "Foundations",
                    "lessons": [
                        {
                            "id": "lesson-1",
                            "title": "Read the evidence",
                            "content": "# Existing Markdown mirror",
                            "document": document,
                        }
                    ],
                }
            ],
        }

        payload, _image_sources = _build_import_payload(
            state,
            "structured-editor-pilot",
        )
        saved_lesson = payload["modules"][0]["lessons"][0]

        self.assertEqual(saved_lesson["content_markdown"], "# Existing Markdown mirror")
        self.assertEqual(saved_lesson["content_json"]["lesson_document"], document)
        self.assertEqual(payload["builder_state"]["modules"][0]["lessons"][0]["document"], document)

    def test_legacy_builder_payload_remains_markdown_only(self):
        state = {
            "title": "Legacy Markdown Course",
            "accessType": "free",
            "modules": [
                {
                    "title": "Foundations",
                    "lessons": [
                        {
                            "id": "lesson-1",
                            "title": "Read the evidence",
                            "content": "# Legacy lesson body",
                        }
                    ],
                }
            ],
        }

        payload, _image_sources = _build_import_payload(state, "legacy-markdown-course")
        saved_lesson = payload["modules"][0]["lessons"][0]

        self.assertEqual(saved_lesson["content_markdown"], "# Legacy lesson body")
        self.assertNotIn("lesson_document", saved_lesson["content_json"])

