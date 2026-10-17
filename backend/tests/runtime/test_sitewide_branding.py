"""Static regressions for the self-contained public community page."""
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
COMMUNITY_PAGE = REPOSITORY_ROOT / "site" / "community.html"


def test_community_skip_link_is_hidden_until_keyboard_focus():
    source = COMMUNITY_PAGE.read_text(encoding="utf-8")
    css = source.split("</style>", 1)[0]
    markup = source.split("</style>", 1)[1]
    assert '<a class="skip-link" href="#main-content">Skip to main content</a>' in markup
    assert ".skip-link{position:absolute" in css
    assert "transform:translateY(-180%)" in css
    assert ".skip-link:focus,.skip-link:focus-visible" in css
    assert "transform:translateY(0)" in css


def test_community_uses_official_header_and_footer_logo_assets():
    source = COMMUNITY_PAGE.read_text(encoding="utf-8")
    markup = source.split("</style>", 1)[1]
    assert 'class="brand-image" src="assets/tradethesis-horizontal.png"' in markup
    assert 'class="footer-logo" src="assets/tradethesis-wordmark.png"' in markup
    assert '<span class="brand-fallback">' not in markup
