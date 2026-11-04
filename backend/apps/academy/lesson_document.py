"""Versioned structured lesson-document contract for the Course Builder.

The document envelope is intentionally separate from lesson sidecar data such as
questions, answer keys, notebook prompts, regional variants and media metadata.
This module is validation-only in the first phase: it does not migrate or write
existing lessons.
"""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any
from urllib.parse import urlsplit

DOCUMENT_FORMAT = "tradethesis.lesson"
DOCUMENT_SCHEMA_VERSION = 1
MAX_DOCUMENT_NODES = 20_000
MAX_DOCUMENT_DEPTH = 64
MAX_DOCUMENT_TEXT_CHARS = 2_000_000

_SAFE_REFERENCE_ID = re.compile(r"[A-Za-z0-9_-]{1,120}\Z")
_SAFE_COLOR = re.compile(r"#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?\Z")

BLOCK_NODES = frozenset(
    {
        "paragraph",
        "heading",
        "blockquote",
        "bulletList",
        "orderedList",
        "codeBlock",
        "horizontalRule",
        "table",
        "ttAssetImage",
        "ttFigure",
        "ttRegionalBlock",
        "ttLessonReference",
        "ttProtectedVideo",
        "ttLegacyReference",
    }
)
INLINE_NODES = frozenset({"text", "hardBreak"})
NODE_TYPES = BLOCK_NODES | INLINE_NODES | frozenset({"doc", "listItem", "tableRow", "tableCell", "tableHeader"})
MARK_TYPES = frozenset({"bold", "italic", "strike", "underline", "code", "link", "highlight"})

_NODE_ATTRS = {
    "doc": frozenset(),
    "paragraph": frozenset({"textAlign"}),
    "heading": frozenset({"level", "textAlign"}),
    "orderedList": frozenset({"start", "type"}),
    "codeBlock": frozenset({"language"}),
    "tableCell": frozenset(
        {"colspan", "rowspan", "colwidth", "align", "verticalAlign", "backgroundColor"}
    ),
    "tableHeader": frozenset(
        {"colspan", "rowspan", "colwidth", "align", "verticalAlign", "backgroundColor"}
    ),
    "ttAssetImage": frozenset({"assetId", "alt", "title", "caption", "width", "height", "display"}),
    "ttFigure": frozenset({"figureId"}),
    "ttRegionalBlock": frozenset({"blockId"}),
    "ttLessonReference": frozenset({"lessonId"}),
    "ttProtectedVideo": frozenset({"videoId"}),
    "ttLegacyReference": frozenset({"token", "referenceKind", "referenceId"}),
}
_MARK_ATTRS = {
    "link": frozenset({"href", "target", "rel"}),
    "highlight": frozenset({"color"}),
}

# These structures remain outside the rich-text document. They are intentionally
# not normalised or rewritten by this module.
LESSON_SIDECAR_KEYS = frozenset(
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
    }
)


class LessonDocumentValidationError(ValueError):
    """Raised when a document does not match the supported TradeThesis schema."""


def new_lesson_document(content: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a fresh, versioned TradeThesis lesson-document envelope."""
    body = deepcopy(content) if content is not None else {
        "type": "doc",
        "content": [{"type": "paragraph"}],
    }
    document = {
        "format": DOCUMENT_FORMAT,
        "schema_version": DOCUMENT_SCHEMA_VERSION,
        "content": body,
    }
    validate_lesson_document(document)
    return document


def is_lesson_document(value: Any) -> bool:
    """Return whether value is a recognised TradeThesis lesson-document envelope."""
    return (
        isinstance(value, dict)
        and value.get("format") == DOCUMENT_FORMAT
        and value.get("schema_version") == DOCUMENT_SCHEMA_VERSION
        and isinstance(value.get("content"), dict)
        and value["content"].get("type") == "doc"
    )


def validate_lesson_document(value: Any) -> dict[str, Any]:
    """Validate and return a defensive copy of a versioned Tiptap JSON envelope.

    Unknown nodes, marks and attributes are rejected rather than silently removed.
    Asset and video records are referenced by stable IDs, never by private paths or
    inline data URLs. Sidecar data is stored separately by the caller.
    """
    if not isinstance(value, dict):
        raise LessonDocumentValidationError("Lesson document must be an object.")
    if set(value) != {"format", "schema_version", "content"}:
        raise LessonDocumentValidationError(
            "Lesson document envelope must contain only format, schema_version and content."
        )
    if value.get("format") != DOCUMENT_FORMAT:
        raise LessonDocumentValidationError("Unsupported lesson-document format.")
    if value.get("schema_version") != DOCUMENT_SCHEMA_VERSION:
        raise LessonDocumentValidationError("Unsupported lesson-document schema version.")

    content = value.get("content")
    if not isinstance(content, dict) or content.get("type") != "doc":
        raise LessonDocumentValidationError("Lesson document content must be a Tiptap doc node.")

    counts = {"nodes": 0, "text": 0}
    _validate_node(content, path="content", depth=0, counts=counts)
    if counts["nodes"] > MAX_DOCUMENT_NODES:
        raise LessonDocumentValidationError("Lesson document exceeds the node limit.")
    if counts["text"] > MAX_DOCUMENT_TEXT_CHARS:
        raise LessonDocumentValidationError("Lesson document exceeds the text-size limit.")
    return deepcopy(value)


def _validate_node(
    node: Any,
    *,
    path: str,
    depth: int,
    counts: dict[str, int],
) -> None:
    if depth > MAX_DOCUMENT_DEPTH:
        raise LessonDocumentValidationError(f"{path}: document nesting is too deep.")
    if not isinstance(node, dict):
        raise LessonDocumentValidationError(f"{path}: node must be an object.")

    counts["nodes"] += 1
    if counts["nodes"] > MAX_DOCUMENT_NODES:
        raise LessonDocumentValidationError("Lesson document exceeds the node limit.")

    node_type = node.get("type")
    if not isinstance(node_type, str) or node_type not in NODE_TYPES:
        raise LessonDocumentValidationError(f"{path}: unsupported node type {node_type!r}.")

    allowed_keys = {"type"}
    if node_type in _NODE_ATTRS:
        allowed_keys.add("attrs")
    if node_type == "text":
        allowed_keys.add("text")
        allowed_keys.add("marks")
    elif node_type in {"doc", "paragraph", "heading", "blockquote", "bulletList", "orderedList", "listItem", "codeBlock", "table", "tableRow", "tableCell", "tableHeader"}:
        allowed_keys.add("content")

    unexpected = set(node) - allowed_keys
    if unexpected:
        field = sorted(unexpected)[0]
        raise LessonDocumentValidationError(f"{path}: unsupported node property {field!r}.")

    attrs = node.get("attrs", {})
    if not isinstance(attrs, dict):
        raise LessonDocumentValidationError(f"{path}.attrs: attributes must be an object.")
    allowed_attrs = _NODE_ATTRS.get(node_type, frozenset())
    extra_attrs = set(attrs) - allowed_attrs
    if extra_attrs:
        field = sorted(extra_attrs)[0]
        raise LessonDocumentValidationError(f"{path}.attrs: unsupported attribute {field!r}.")
    _validate_node_attrs(node_type, attrs, path)

    if node_type == "text":
        text = node.get("text")
        if not isinstance(text, str):
            raise LessonDocumentValidationError(f"{path}.text: text must be a string.")
        counts["text"] += len(text)
        _validate_marks(node.get("marks", []), f"{path}.marks")
        return

    if node_type in INLINE_NODES or node_type == "horizontalRule" or node_type in {
        "ttAssetImage", "ttFigure", "ttRegionalBlock", "ttLessonReference", "ttProtectedVideo", "ttLegacyReference"
    }:
        if "content" in node:
            raise LessonDocumentValidationError(f"{path}: this node cannot contain children.")
        return

    children = node.get("content", [])
    if not isinstance(children, list):
        raise LessonDocumentValidationError(f"{path}.content: children must be a list.")
    if node_type == "doc" and not children:
        # ProseMirror documents require at least one block; an empty paragraph is valid.
        raise LessonDocumentValidationError("content: a document must contain at least one block.")

    for index, child in enumerate(children):
        child_type = child.get("type") if isinstance(child, dict) else None
        if not isinstance(child_type, str) or not _child_type_allowed(node_type, child_type):
            raise LessonDocumentValidationError(
                f"{path}.content[{index}]: {child_type!r} is not allowed inside {node_type!r}."
            )
        _validate_node(child, path=f"{path}.content[{index}]", depth=depth + 1, counts=counts)


def _child_type_allowed(parent: str, child: str | None) -> bool:
    if parent == "doc":
        return child in BLOCK_NODES
    if parent in {"paragraph", "heading"}:
        return child in INLINE_NODES
    if parent == "blockquote":
        return child in BLOCK_NODES - {"ttProtectedVideo"}
    if parent in {"bulletList", "orderedList"}:
        return child == "listItem"
    if parent == "listItem":
        return child in BLOCK_NODES - {"ttAssetImage", "ttFigure", "ttRegionalBlock", "ttLessonReference", "ttProtectedVideo"}
    if parent == "codeBlock":
        return child == "text"
    if parent == "table":
        return child == "tableRow"
    if parent == "tableRow":
        return child in {"tableCell", "tableHeader"}
    if parent in {"tableCell", "tableHeader"}:
        return child in BLOCK_NODES - {"table", "ttAssetImage", "ttFigure", "ttRegionalBlock", "ttLessonReference", "ttProtectedVideo"}
    return False


def _validate_node_attrs(node_type: str, attrs: dict[str, Any], path: str) -> None:
    if node_type == "heading":
        level = attrs.get("level", 1)
        if not isinstance(level, int) or isinstance(level, bool) or level not in range(1, 7):
            raise LessonDocumentValidationError(f"{path}.attrs.level: expected an integer from 1 to 6.")
    if node_type in {"paragraph", "heading"}:
        _validate_enum(attrs.get("textAlign"), {"left", "center", "right", "justify"}, path, "textAlign")
    if node_type == "orderedList":
        start = attrs.get("start", 1)
        if not isinstance(start, int) or isinstance(start, bool) or not 1 <= start <= 1_000_000:
            raise LessonDocumentValidationError(f"{path}.attrs.start: expected a positive list start.")
        _validate_enum(attrs.get("type"), {"1", "a", "A", "i", "I"}, path, "type")
    if node_type == "codeBlock":
        language = attrs.get("language", "")
        if not isinstance(language, str) or len(language) > 40 or not re.fullmatch(
            r"[A-Za-z0-9_+-]*", language
        ):
            raise LessonDocumentValidationError(f"{path}.attrs.language: invalid language identifier.")
    if node_type in {"tableCell", "tableHeader"}:
        for key in ("colspan", "rowspan"):
            value = attrs.get(key, 1)
            if not _positive_int(value) or value > 100:
                raise LessonDocumentValidationError(f"{path}.attrs.{key}: expected an integer from 1 to 100.")
        widths = attrs.get("colwidth")
        if widths is not None and (
            not isinstance(widths, list)
            or len(widths) > 100
            or any(not _positive_int(width) for width in widths)
        ):
            raise LessonDocumentValidationError(f"{path}.attrs.colwidth: invalid column widths.")
        _validate_enum(attrs.get("align"), {"left", "center", "right"}, path, "align")
        _validate_enum(attrs.get("verticalAlign"), {"top", "middle", "bottom"}, path, "verticalAlign")
        color = attrs.get("backgroundColor")
        if color is not None and (not isinstance(color, str) or not _SAFE_COLOR.fullmatch(color)):
            raise LessonDocumentValidationError(f"{path}.attrs.backgroundColor: invalid color.")
    if node_type == "ttAssetImage":
        _validate_reference(attrs.get("assetId"), path, "assetId")
        for key in ("alt", "title", "caption"):
            if key in attrs and (not isinstance(attrs[key], str) or len(attrs[key]) > 2000):
                raise LessonDocumentValidationError(f"{path}.attrs.{key}: expected short text.")
        for key in ("width", "height"):
            value = attrs.get(key)
            if value is not None and (not _positive_int(value) or value > 10000):
                raise LessonDocumentValidationError(f"{path}.attrs.{key}: invalid image dimension.")
        _validate_enum(attrs.get("display"), {"inline", "block", "float-start", "float-end"}, path, "display")
    if node_type == "ttFigure":
        _validate_reference(attrs.get("figureId"), path, "figureId")
    if node_type == "ttRegionalBlock":
        _validate_reference(attrs.get("blockId"), path, "blockId")
    if node_type == "ttLessonReference":
        _validate_uuid_reference(attrs.get("lessonId"), path, "lessonId")
    if node_type == "ttProtectedVideo":
        _validate_uuid_reference(attrs.get("videoId"), path, "videoId")
    if node_type == "ttLegacyReference":
        token = attrs.get("token")
        if not isinstance(token, str) or not token.startswith("[[") or not token.endswith("]]") or len(token) > 2000:
            raise LessonDocumentValidationError(f"{path}.attrs.token: invalid legacy reference token.")
        _validate_enum(
            attrs.get("referenceKind"),
            {"asset", "figure", "table", "regional-block", "image-group", "lesson", "lesson-card", "unknown"},
            path,
            "referenceKind",
        )
        if attrs.get("referenceId") is not None:
            _validate_reference(attrs.get("referenceId"), path, "referenceId")


def _validate_marks(marks: Any, path: str) -> None:
    if not isinstance(marks, list):
        raise LessonDocumentValidationError(f"{path}: marks must be a list.")
    seen = set()
    for index, mark in enumerate(marks):
        mark_path = f"{path}[{index}]"
        if not isinstance(mark, dict):
            raise LessonDocumentValidationError(f"{mark_path}: mark must be an object.")
        unexpected_mark_keys = set(mark) - {"type", "attrs"}
        if unexpected_mark_keys:
            raise LessonDocumentValidationError(
                f"{mark_path}: unsupported mark property {sorted(unexpected_mark_keys)[0]!r}."
            )
        mark_type = mark.get("type")
        if not isinstance(mark_type, str) or mark_type not in MARK_TYPES:
            raise LessonDocumentValidationError(f"{mark_path}: unsupported mark type {mark_type!r}.")
        if mark_type in seen:
            raise LessonDocumentValidationError(f"{mark_path}: duplicate mark {mark_type!r}.")
        seen.add(mark_type)
        attrs = mark.get("attrs", {})
        if not isinstance(attrs, dict):
            raise LessonDocumentValidationError(f"{mark_path}.attrs: attributes must be an object.")
        extra = set(attrs) - _MARK_ATTRS.get(mark_type, frozenset())
        if extra:
            raise LessonDocumentValidationError(
                f"{mark_path}.attrs: unsupported attribute {sorted(extra)[0]!r}."
            )
        if mark_type == "link":
            href = attrs.get("href")
            if not isinstance(href, str) or not href or len(href) > 2048:
                raise LessonDocumentValidationError(f"{mark_path}: links require a valid href.")
            scheme = urlsplit(href).scheme.lower()
            if scheme and scheme not in {"https", "http", "mailto", "tel"}:
                raise LessonDocumentValidationError(f"{mark_path}: unsafe link scheme.")
            if href.lstrip().lower().startswith(("javascript:", "data:")):
                raise LessonDocumentValidationError(f"{mark_path}: unsafe link URL.")
            _validate_enum(attrs.get("target"), {"_blank", "_self"}, mark_path, "target")
            rel = attrs.get("rel")
            if rel is not None and (not isinstance(rel, str) or len(rel) > 120):
                raise LessonDocumentValidationError(f"{mark_path}.attrs.rel: invalid link rel.")
        if mark_type == "highlight":
            color = attrs.get("color")
            if color is not None and (not isinstance(color, str) or not _SAFE_COLOR.fullmatch(color)):
                raise LessonDocumentValidationError(f"{mark_path}.attrs.color: invalid color.")


def _validate_reference(value: Any, path: str, field: str) -> None:
    if not isinstance(value, str) or not _SAFE_REFERENCE_ID.fullmatch(value):
        raise LessonDocumentValidationError(f"{path}.attrs.{field}: invalid stable reference ID.")


def _validate_uuid_reference(value: Any, path: str, field: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
        value,
    ):
        raise LessonDocumentValidationError(f"{path}.attrs.{field}: expected a UUID.")


def _validate_enum(value: Any, allowed: set[str], path: str, field: str) -> None:
    if value is not None and (not isinstance(value, str) or value not in allowed):
        raise LessonDocumentValidationError(f"{path}.attrs.{field}: unsupported value {value!r}.")


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0
