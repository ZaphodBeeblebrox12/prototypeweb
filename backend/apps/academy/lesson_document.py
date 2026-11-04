"""Versioned structured lesson-document contract for the Course Builder.

The document is stored beside legacy Markdown during the editor migration. It is
never rendered directly until the learner renderer supports the same version.
"""

from __future__ import annotations

from copy import deepcopy
from urllib.parse import urlsplit


LESSON_DOCUMENT_FORMAT = "tradethesis.lesson-document"
LESSON_DOCUMENT_VERSION = 1

MAX_DOCUMENT_NODES = 20_000
MAX_DOCUMENT_DEPTH = 40
MAX_TEXT_LENGTH = 250_000
MAX_ATTRIBUTE_KEYS = 64
MAX_ATTRIBUTE_DEPTH = 8
MAX_COLLECTION_ITEMS = 2_000
MAX_ATTRIBUTE_STRING_LENGTH = 20_000

# Names intentionally match the Tiptap/ProseMirror JSON node names used by the
# future editor. Course-specific block names are part of our own extension API.
ALLOWED_NODE_TYPES = frozenset(
    {
        "doc",
        "paragraph",
        "heading",
        "text",
        "hardBreak",
        "horizontalRule",
        "blockquote",
        "bulletList",
        "orderedList",
        "listItem",
        "codeBlock",
        "table",
        "tableRow",
        "tableHeader",
        "tableCell",
        "image",
        "courseFigure",
        "imageGroup",
        "comparisonFigure",
        "courseCard",
        "lessonReference",
        "regionalBlock",
        "practiceQuestion",
        "videoBlock",
        "notebookBlock",
        "reflectionBlock",
        "lessonTab",
        "tableReference",
        "legacyMarkdown",
        "callout",
    }
)

ALLOWED_MARK_TYPES = frozenset(
    {
        "bold",
        "italic",
        "strike",
        "underline",
        "code",
        "link",
        "subscript",
        "superscript",
        "highlight",
        "textStyle",
    }
)

_SAFE_LINK_SCHEMES = frozenset({"http", "https", "mailto"})


class LessonDocumentError(ValueError):
    """Raised when structured lesson content is not safe or supported."""


def _validate_json_value(value, *, path: str, depth: int = 0) -> None:
    if depth > MAX_ATTRIBUTE_DEPTH:
        raise LessonDocumentError(f"{path}: attribute nesting is too deep.")

    if value is None or isinstance(value, (bool, int)):
        return
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise LessonDocumentError(f"{path}: non-finite numbers are not allowed.")
        return

    if isinstance(value, str):
        if len(value) > MAX_ATTRIBUTE_STRING_LENGTH:
            raise LessonDocumentError(f"{path}: attribute text is too long.")
        return

    if isinstance(value, list):
        if len(value) > MAX_COLLECTION_ITEMS:
            raise LessonDocumentError(f"{path}: attribute list contains too many items.")
        for index, item in enumerate(value):
            _validate_json_value(item, path=f"{path}[{index}]", depth=depth + 1)
        return

    if isinstance(value, dict):
        if len(value) > MAX_ATTRIBUTE_KEYS:
            raise LessonDocumentError(f"{path}: attribute object contains too many keys.")
        for key, item in value.items():
            if not isinstance(key, str) or not key or len(key) > 100:
                raise LessonDocumentError(f"{path}: attribute keys must be short strings.")
            if key.casefold().startswith("on") or key in {"__proto__", "constructor", "prototype"}:
                raise LessonDocumentError(
                    f"{path}: executable or reserved attribute is not allowed."
                )
            if key.casefold() in {"href", "url"} and isinstance(item, str):
                _validate_link_target(item, path=f"{path}.{key}")
            if key.casefold() == "src" and isinstance(item, str):
                _validate_media_source(item, path=f"{path}.{key}")
            _validate_json_value(item, path=f"{path}.{key}", depth=depth + 1)
        return

    raise LessonDocumentError(f"{path}: attribute value is not JSON-compatible.")


def _validate_link_target(value: str, *, path: str) -> None:
    target = value.strip()
    if not target:
        return
    parsed = urlsplit(target)
    if parsed.scheme and parsed.scheme.casefold() not in _SAFE_LINK_SCHEMES:
        raise LessonDocumentError(f"{path}: unsupported URL scheme.")
    if target.casefold().startswith(("javascript:", "data:", "vbscript:")):
        raise LessonDocumentError(f"{path}: executable URLs are not allowed.")


def _validate_media_source(value: str, *, path: str) -> None:
    target = value.strip()
    if not target:
        return
    parsed = urlsplit(target)
    if parsed.scheme and parsed.scheme.casefold() not in {"http", "https", "asset"}:
        raise LessonDocumentError(f"{path}: unsupported media URL scheme.")
    if target.casefold().startswith(("javascript:", "data:", "vbscript:")):
        raise LessonDocumentError(f"{path}: executable media URLs are not allowed.")


def _validate_marks(marks, *, path: str, node_counter: list[int], depth: int) -> None:
    if marks is None:
        return
    if not isinstance(marks, list) or len(marks) > 20:
        raise LessonDocumentError(f"{path}: marks must be a short list.")

    seen = set()
    for index, mark in enumerate(marks):
        mark_path = f"{path}[{index}]"
        if not isinstance(mark, dict):
            raise LessonDocumentError(f"{mark_path}: mark must be an object.")
        mark_type = mark.get("type")
        if not isinstance(mark_type, str) or mark_type not in ALLOWED_MARK_TYPES:
            raise LessonDocumentError(f"{mark_path}: unsupported mark type {mark_type!r}.")
        if mark_type in seen:
            raise LessonDocumentError(f"{mark_path}: duplicate mark type {mark_type!r}.")
        seen.add(mark_type)
        attrs = mark.get("attrs", {})
        if not isinstance(attrs, dict):
            raise LessonDocumentError(f"{mark_path}.attrs: expected an object.")
        if len(attrs) > MAX_ATTRIBUTE_KEYS:
            raise LessonDocumentError(f"{mark_path}.attrs: too many attributes.")
        _validate_json_value(attrs, path=f"{mark_path}.attrs", depth=depth + 1)


def _validate_node(node, *, path: str, node_counter: list[int], depth: int) -> None:
    if depth > MAX_DOCUMENT_DEPTH:
        raise LessonDocumentError(f"{path}: document nesting is too deep.")

    node_counter[0] += 1
    if node_counter[0] > MAX_DOCUMENT_NODES:
        raise LessonDocumentError("The lesson document contains too many nodes.")

    if not isinstance(node, dict):
        raise LessonDocumentError(f"{path}: node must be an object.")

    node_type = node.get("type")
    if not isinstance(node_type, str) or node_type not in ALLOWED_NODE_TYPES:
        raise LessonDocumentError(f"{path}: unsupported node type {node_type!r}.")

    if node_type == "text":
        text = node.get("text")
        if not isinstance(text, str):
            raise LessonDocumentError(f"{path}.text: text nodes must contain text.")
        if len(text) > MAX_TEXT_LENGTH:
            raise LessonDocumentError(f"{path}.text: text is too long.")
        if "content" in node:
            raise LessonDocumentError(f"{path}: text nodes cannot contain child nodes.")
        _validate_marks(
            node.get("marks"),
            path=f"{path}.marks",
            node_counter=node_counter,
            depth=depth,
        )
        return

    if "text" in node:
        raise LessonDocumentError(f"{path}: only text nodes may contain a text property.")

    attrs = node.get("attrs", {})
    if not isinstance(attrs, dict):
        raise LessonDocumentError(f"{path}.attrs: expected an object.")
    if len(attrs) > MAX_ATTRIBUTE_KEYS:
        raise LessonDocumentError(f"{path}.attrs: too many attributes.")
    _validate_json_value(attrs, path=f"{path}.attrs", depth=depth + 1)

    if node.get("marks"):
        raise LessonDocumentError(f"{path}: marks may only be applied to text nodes.")

    children = node.get("content")
    if children is None:
        return
    if not isinstance(children, list):
        raise LessonDocumentError(f"{path}.content: expected a list.")
    if len(children) > MAX_COLLECTION_ITEMS:
        raise LessonDocumentError(f"{path}.content: too many child nodes.")

    for index, child in enumerate(children):
        _validate_node(
            child,
            path=f"{path}.content[{index}]",
            node_counter=node_counter,
            depth=depth + 1,
        )


def validate_lesson_document(value) -> dict:
    """Validate and return a detached copy of a versioned lesson document.

    Unknown node or mark types are rejected rather than stripped. This is a
    deliberate data-preservation rule: a newer editor must never silently
    destroy content created by an extension it does not understand.
    """
    if not isinstance(value, dict):
        raise LessonDocumentError("A lesson document must be an object.")

    if value.get("format") != LESSON_DOCUMENT_FORMAT:
        raise LessonDocumentError("The lesson document format is not recognised.")

    version = value.get("version")
    if type(version) is not int or version != LESSON_DOCUMENT_VERSION:
        raise LessonDocumentError(f"Unsupported lesson document version: {version!r}.")

    document = value.get("document")
    if not isinstance(document, dict) or document.get("type") != "doc":
        raise LessonDocumentError("The lesson document root must be a doc node.")
    if not isinstance(document.get("content"), list) or not document["content"]:
        raise LessonDocumentError("The lesson document must contain at least one block.")

    counter = [0]
    _validate_node(document, path="document", node_counter=counter, depth=0)

    return deepcopy(
        {
            "format": LESSON_DOCUMENT_FORMAT,
            "version": LESSON_DOCUMENT_VERSION,
            "document": document,
        }
    )


def make_lesson_document(document: dict | None = None) -> dict:
    """Create an empty or wrapped v1 lesson document."""
    if document is None:
        document = {
            "type": "doc",
            "content": [{"type": "paragraph"}],
        }
    return validate_lesson_document(
        {
            "format": LESSON_DOCUMENT_FORMAT,
            "version": LESSON_DOCUMENT_VERSION,
            "document": document,
        }
    )


def lesson_document_from_content_json(content_json) -> dict | None:
    """Return a validated canonical document from legacy content_json, if present."""
    if not isinstance(content_json, dict):
        return None
    document = content_json.get("lesson_document")
    if document is None:
        return None
    return validate_lesson_document(document)


def content_json_with_lesson_document(content_json, document) -> dict:
    """Return content_json with a validated canonical document attached."""
    result = deepcopy(content_json) if isinstance(content_json, dict) else {}
    result["lesson_document"] = validate_lesson_document(document)
    return result
