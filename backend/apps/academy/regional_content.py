"""Country-to-region policy for regional lesson content.

This mapping is intentionally separate from subscription pricing. New content
markets must not silently change a learner's geo-pricing tier. Region assignment
is a TradeThesis audience policy, not a legal or billing classification.
"""

import re

REGIONAL_CONTENT_CODES = frozenset({"APAC", "EU", "NA", "LATAM", "MENA", "SSA"})
ASSET_REFERENCE_RE = re.compile(r"asset://([0-9a-fA-F-]{36})")
IMAGE_GROUP_REFERENCE_RE = re.compile(r"\[\[image-group:([A-Za-z0-9_-]{1,120})\]\]")

# ISO 3166-1 alpha-2 audience codes, grouped by the six Course Builder regions.
# Existing pricing-region assignments are preserved, but this map is for lesson
# content only. Antarctica (AQ) is not an intended learner market.
_COUNTRY_CODES_BY_REGION = {
    "APAC": """AF AS AU BD BN BT CC CK CN CX FJ FM GU HK HM ID IN JP KG KH KI KP KR KZ LA LK MH MM MN MO MP MV MY NC NF NP NR NU NZ PF PG PH PK PN PW SB SG TH TJ TK TL TM TO TV TW UZ VN VU WF WS""".split(),
    "EU": """AD AL AT AX BA BE BG BV BY CH CY CZ DE DK EE ES FI FO FR GB GG GI GR HR HU IE IM IS IT JE LI LT LV MC MD ME MK MT NL NO PL PT RO RS RU SE SI SJ SK SM UA VA""".split(),
    "NA": """BM CA GL MX PM UM US""".split(),
    "LATAM": """AG AI AR AW BB BL BO BQ BR BS BZ CL CO CR CU CW DM DO EC FK GD GF GP GS GT GY HN HT JM KN KY LC MF MQ MS NI PA PE PR PY SR SV SX TC TT UY VC VE VG VI""".split(),
    "MENA": """AE AM AZ BH DZ EG EH GE IL IQ IR JO KW LB LY MA OM PS QA SA SD SY TN TR YE""".split(),
    "SSA": """AO BF BI BJ BW CD CF CG CI CM CV DJ ER ET GA GH GM GN GQ GW IO KE KM LR LS MG ML MR MU MW MZ NA NE NG RE RW SC SH SL SN SO SS ST SZ TD TF TG TZ UG YT ZA ZM ZW""".split(),
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


def regional_block_asset_ids(content_json):
    """Collect every managed-asset reference in regional base and variant content."""
    asset_ids = set()
    for block in regional_block_values(content_json):
        base_content = block.get("base_content", block.get("baseContent", ""))
        asset_ids.update(value.lower() for value in ASSET_REFERENCE_RE.findall(str(base_content or "")))
        variants = block.get("variants") if isinstance(block.get("variants"), list) else []
        for variant in variants:
            if isinstance(variant, dict):
                asset_ids.update(
                    value.lower()
                    for value in ASSET_REFERENCE_RE.findall(str(variant.get("content") or ""))
                )
    return asset_ids
