"""Country-to-region policy for regional lesson content.

This mapping is intentionally separate from subscription pricing. New content
markets must not silently change a learner's geo-pricing tier. Region assignment
is a TradeThesis audience policy, not a legal or billing classification.
"""

import re

REGIONAL_CONTENT_CODES = frozenset({"APAC", "EU", "NA", "LATAM", "MENA", "SSA"})
ASSET_REFERENCE_RE = re.compile(r"asset://([0-9a-fA-F-]{36})")
IMAGE_GROUP_REFERENCE_RE = re.compile(r"\[\[image-group:([A-Za-z0-9_-]{1,120})\]\]")

# Regional images must use managed asset references so permissions can be enforced.
_REGIONAL_MARKDOWN_IMAGE_RE = re.compile(
    r"!\[[^\]]*\]\(\s*(?P<src>[^)\s]+)(?:\s+[^)]*)?\)",
    re.IGNORECASE,
)
_REGIONAL_HTML_IMAGE_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
_REGIONAL_HTML_IMAGE_SRC_RE = re.compile(
    r"""\bsrc\s*=\s*(?:"(?P<double>[^"]*)"|'(?P<single>[^']*)'|(?P<bare>[^\s>]+))""",
    re.IGNORECASE,
)


def _is_managed_regional_image_source(source):
    """Only a complete asset://UUID reference is eligible for regional image rendering."""
    from html import unescape

    return bool(ASSET_REFERENCE_RE.fullmatch(unescape(str(source or "")).strip()))


def contains_unmanaged_regional_image(content):
    """Whether a regional block embeds any image outside protected course storage."""
    source = str(content or "")
    for match in _REGIONAL_MARKDOWN_IMAGE_RE.finditer(source):
        if not _is_managed_regional_image_source(match.group("src")):
            return True
    for match in _REGIONAL_HTML_IMAGE_RE.finditer(source):
        src_match = _REGIONAL_HTML_IMAGE_SRC_RE.search(match.group(0))
        if not src_match:
            return True
        source_url = next(
            (value for value in src_match.groupdict().values() if value is not None), ""
        )
        if not _is_managed_regional_image_source(source_url):
            return True
    return False


def strip_unmanaged_regional_images(content):
    """Remove unmanaged Markdown/HTML image embeds from regional content at render time."""
    source = str(content or "")
    source = _REGIONAL_MARKDOWN_IMAGE_RE.sub(
        lambda match: (
            match.group(0) if _is_managed_regional_image_source(match.group("src")) else ""
        ),
        source,
    )

    def keep_managed_html_image(match):
        src_match = _REGIONAL_HTML_IMAGE_SRC_RE.search(match.group(0))
        if not src_match:
            return ""
        source_url = next(
            (value for value in src_match.groupdict().values() if value is not None), ""
        )
        return match.group(0) if _is_managed_regional_image_source(source_url) else ""

    return _REGIONAL_HTML_IMAGE_RE.sub(keep_managed_html_image, source)


# ISO 3166-1 alpha-2 audience codes, grouped by the six Course Builder regions.
# Existing pricing-region assignments are preserved, but this map is for lesson
# content only. Antarctica (AQ) is not an intended learner market.
_COUNTRY_CODES_BY_REGION = {
    "APAC": """AF AS AU BD BN BT CC CK CN CX FJ FM GU HK HM ID IN JP KG KH KI KP KR KZ LA LK MH MM MN MO MP MV MY NC NF NP NR NU NZ PF PG PH PK PN PW SB SG TH TJ TK TL TM TO TV TW UZ VN VU WF WS""".split(),  # noqa: SIM905,
    "EU": """AD AL AT AX BA BE BG BV BY CH CY CZ DE DK EE ES FI FO FR GB GG GI GR HR HU IE IM IS IT JE LI LU LT LV MC MD ME MK MT NL NO PL PT RO RS RU SE SI SJ SK SM UA VA""".split(),  # noqa: SIM905,
    "NA": """BM CA GL MX PM UM US""".split(),  # noqa: SIM905,
    "LATAM": """AG AI AR AW BB BL BO BQ BR BS BZ CL CO CR CU CW DM DO EC FK GD GF GP GS GT GY HN HT JM KN KY LC MF MQ MS NI PA PE PR PY SR SV SX TC TT UY VC VE VG VI""".split(),  # noqa: SIM905,
    "MENA": """AE AM AZ BH DZ EG EH GE IL IQ IR JO KW LB LY MA OM PS QA SA SD SY TN TR YE""".split(),  # noqa: SIM905,
    "SSA": """AO BF BI BJ BW CD CF CG CI CM CV DJ ER ET GA GH GM GN GQ GW IO KE KM LR LS MG ML MR MU MW MZ NA NE NG RE RW SC SH SL SN SO SS ST SZ TD TF TG TZ UG YT ZA ZM ZW""".split(),  # noqa: SIM905,
}
CONTENT_COUNTRY_TO_REGION = {
    country_code: region
    for region, country_codes in _COUNTRY_CODES_BY_REGION.items()
    for country_code in country_codes
}
del _COUNTRY_CODES_BY_REGION


def get_content_region_for_country(country_code):
    """Return the regional lesson audience without consulting pricing policy."""
    code = str(country_code or "").strip().upper()
    return CONTENT_COUNTRY_TO_REGION.get(code)


def get_content_country(request):
    """Resolve the real request country without honoring debug/pricing overrides."""
    country = str(request.META.get("HTTP_CF_IPCOUNTRY") or "").strip().upper()
    if country != "XX" and len(country) == 2 and country.isascii() and country.isalpha():
        return country

    try:
        from apps.subscriptions.geoip import get_country_from_maxmind

        country = str(get_country_from_maxmind(request) or "").strip().upper()
    except Exception:
        return None
    if country != "XX" and len(country) == 2 and country.isascii() and country.isalpha():
        return country
    return None


def regional_block_values(content_json):
    """Return normalized regional block dictionaries from published lesson JSON."""
    if not isinstance(content_json, dict):
        return []
    blocks = content_json.get("regional_blocks", {})
    if isinstance(blocks, dict):
        return [value for value in blocks.values() if isinstance(value, dict)]
    if isinstance(blocks, list):
        return [value for value in blocks if isinstance(value, dict)]
    return []


def regional_lesson_content_values(content_json):
    """Return whole-lesson audience overrides from learner-safe lesson JSON."""
    if not isinstance(content_json, dict):
        return {}
    values = content_json.get(
        "regional_lesson_content", content_json.get("regionalLessonContent", {})
    )
    if not isinstance(values, dict):
        return {}
    return {
        str(key).strip().lower(): str(value or "")
        for key, value in values.items()
        if isinstance(key, str) and isinstance(value, str)
    }


def regional_lesson_content_asset_ids(content_json):
    """Collect managed assets referenced by every whole-lesson audience override."""
    asset_ids = set()
    for content in regional_lesson_content_values(content_json).values():
        asset_ids.update(value.lower() for value in ASSET_REFERENCE_RE.findall(content))
    return asset_ids


def resolve_regional_lesson_content(
    source, regional_content=None, country_code=None, region_code=None
):
    """Choose a complete lesson body by audience: country, region, then main."""
    source = str(source or "")
    raw_variants = regional_content if isinstance(regional_content, dict) else {}
    variants = {
        str(key).strip().lower(): value
        for key, value in raw_variants.items()
        if isinstance(key, str)
    }
    country = str(country_code or "").strip().upper()
    region = str(region_code or "").strip().upper()
    selected = variants.get(f"country:{country.lower()}") if country else None
    if selected is None and region in REGIONAL_CONTENT_CODES:
        selected = variants.get(f"region:{region.lower()}")
    if not isinstance(selected, str):
        return source
    return strip_unmanaged_regional_images(selected)


def regional_block_asset_ids(content_json):
    """Collect every managed-asset reference in regional base and variant content."""
    asset_ids = set()
    for block in regional_block_values(content_json):
        base_content = block.get("base_content", block.get("baseContent", ""))
        asset_ids.update(
            value.lower() for value in ASSET_REFERENCE_RE.findall(str(base_content or ""))
        )
        variants = block.get("variants") if isinstance(block.get("variants"), list) else []
        for variant in variants:
            if isinstance(variant, dict):
                asset_ids.update(
                    value.lower()
                    for value in ASSET_REFERENCE_RE.findall(str(variant.get("content") or ""))
                )
    return asset_ids
