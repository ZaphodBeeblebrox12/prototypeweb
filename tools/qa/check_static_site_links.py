#!/usr/bin/env python3
"""Validate local href/src/poster references in the static TradeThesis site.

Run after deployment workflow staging steps so generated learning-room chart assets
are present. External URLs, mailto/tel links, data URLs, and fragment-only links
are intentionally ignored.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

SITE_ROOT = Path("site")
ATTRIBUTES = {"href", "src", "poster"}
SKIP_SCHEMES = {"http", "https", "mailto", "tel", "javascript", "data", "blob"}


class LocalReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[tuple[int, str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name.lower() in ATTRIBUTES and value:
                self.references.append((self.getpos()[0], name.lower(), value.strip()))


def resolve_local_reference(source: Path, raw_url: str) -> Path | None:
    parsed = urlsplit(raw_url)
    if parsed.scheme.lower() in SKIP_SCHEMES or parsed.netloc:
        return None
    url_path = unquote(parsed.path)
    if not url_path or url_path.startswith("#"):
        return None

    if url_path.startswith("/"):
        target = SITE_ROOT / url_path.lstrip("/")
    else:
        target = source.parent / url_path

    target = target.resolve()
    root = SITE_ROOT.resolve()
    try:
        target.relative_to(root)
    except ValueError:
        # Do not allow an HTML reference to escape the published site folder.
        return target

    if target.is_dir():
        target = target / "index.html"
    elif not target.exists() and url_path.endswith("/"):
        target = target / "index.html"
    elif not target.exists() and not target.suffix:
        index_target = target / "index.html"
        if index_target.exists():
            target = index_target
    return target


def main() -> int:
    if not SITE_ROOT.is_dir():
        raise SystemExit("Static site directory not found: site/")

    errors: list[str] = []
    pages = sorted(SITE_ROOT.rglob("*.html"))
    for page in pages:
        parser = LocalReferenceParser()
        try:
            parser.feed(page.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"{page}: could not read HTML: {exc}")
            continue

        for line, attribute, raw_url in parser.references:
            target = resolve_local_reference(page, raw_url)
            if target is None:
                continue
            if not target.exists() or not target.is_file():
                relative = page.relative_to(SITE_ROOT)
                errors.append(
                    f"{relative}:{line}: {attribute}={raw_url!r} "
                    f"does not resolve to a published file"
                )

    if errors:
        print(f"Found {len(errors)} broken local reference(s) across {len(pages)} HTML page(s):")
        for error in errors:
            print(f" - {error}")
        return 1

    print(f"Static site link audit passed: {len(pages)} HTML page(s), all local href/src/poster references resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
