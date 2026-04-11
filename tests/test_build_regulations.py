"""Tests for scripts/build_regulations.py — the reusable region page generator.

Covers: schema validation, template substitution, JSON-LD generation,
required SEO metadata, content rendering, and end-to-end build output.

Stdlib only. Every new region page added to content/regulations/ will
be automatically picked up by test_build_regulations_all_regions_render.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_regulations import (  # noqa: E402
    REGION_SCHEMA,
    _load_region,
    _render_faq_block,
    _render_jsonld_article,
    _render_jsonld_breadcrumb,
    _render_jsonld_faq,
    _render_sections,
    _render_sources_block,
    _render_tracker_block,
    _validate_region,
    build,
    render_region,
)

CONTENT_DIR = ROOT / "content" / "regulations"


def _minimal_valid_region(slug: str = "test-region") -> dict:
    """Build a minimum-viable REGION dict that satisfies every schema requirement."""
    return {
        "slug": slug,
        "flag": "🏳️",
        "nav_label": "Test",
        "lang": "en",
        "og_locale": "en_US",
        "hreflang_self": "en",
        "geo_region": "XX",
        "geo_placename": "Testland",
        "status_cls": "live",
        "status_text": "Test status",
        "title_tag": "Test title tag",
        "title_html": "Test <span class='hl'>title</span>",
        "meta_description": "Test meta description.",
        "meta_keywords": "test, region",
        "og_title": "Test OG title",
        "og_description": "Test OG description.",
        "twitter_title": "Test twitter title",
        "twitter_description": "Test twitter description.",
        "last_updated": "2026-04-08",
        "published_time": "2026-04-08T00:00:00+00:00",
        "modified_time": "2026-04-08T00:00:00+00:00",
        "lede": "Test lede paragraph.",
        "tracker_rows": [
            {"label": "Test row", "value": "Test value", "state": "verified"},
        ],
        "sections_html": [
            {"id": "test-section", "heading": "Test section", "body": "<p>Test body.</p>"},
        ],
        "faq": [
            {"q": "Test question?", "a": "Test answer."},
        ],
        "sources": [
            {"title": "Test source", "note": "Test note", "url": "https://example.com"},
        ],
    }


def test_build_regulations_region_schema_has_all_required_keys():
    """The REGION_SCHEMA set must match the minimum viable region dict."""
    region = _minimal_valid_region()
    assert REGION_SCHEMA == set(region.keys()), \
        f"Schema mismatch: extra={set(region.keys()) - REGION_SCHEMA}, missing={REGION_SCHEMA - set(region.keys())}"
    print(f"✓ build_regulations: schema has {len(REGION_SCHEMA)} required keys")


def test_build_regulations_validate_rejects_missing_keys():
    """Validator must fail loudly on a dict missing any required key."""
    import pytest as _pt
    region = _minimal_valid_region()
    del region["slug"]
    with _pt.raises(ValueError, match="missing required keys"):
        _validate_region(region, Path("test.py"))
    print("✓ build_regulations: validator rejects missing keys")


def test_build_regulations_validate_rejects_empty_tracker_rows():
    """tracker_rows must be a non-empty list."""
    import pytest as _pt
    region = _minimal_valid_region()
    region["tracker_rows"] = []
    with _pt.raises(ValueError, match="tracker_rows must be a non-empty list"):
        _validate_region(region, Path("test.py"))
    print("✓ build_regulations: validator rejects empty tracker_rows")


def test_build_regulations_validate_rejects_malformed_faq():
    """FAQ entries must have both 'q' and 'a' keys."""
    import pytest as _pt
    region = _minimal_valid_region()
    region["faq"] = [{"q": "No answer here"}]
    with _pt.raises(ValueError, match="faq\\[0\\] missing 'a'"):
        _validate_region(region, Path("test.py"))
    print("✓ build_regulations: validator rejects malformed FAQ entries")


def test_build_regulations_tracker_block_renders_badge_by_state():
    """Tracker row with state='verified' must render the green OK badge."""
    rows = [{"label": "Row 1", "value": "Value 1", "state": "verified"}]
    html = _render_tracker_block(rows)
    assert 'class="ok">VERIFIED' in html
    assert "Row 1" in html and "Value 1" in html

    rows = [{"label": "Row 2", "value": "Value 2", "state": "pending"}]
    html = _render_tracker_block(rows)
    assert 'class="pend">PENDING' in html

    # Missing state → no badge
    rows = [{"label": "Row 3", "value": "Value 3"}]
    html = _render_tracker_block(rows)
    assert "Row 3" in html and "Value 3" in html
    assert "class=\"ok\"" not in html and "class=\"pend\"" not in html
    print("✓ build_regulations: tracker badge states map correctly")


def test_build_regulations_sections_include_id_and_heading():
    """Each section must render with its id anchor and h2 heading."""
    sections = [
        {"id": "first", "heading": "First Heading", "body": "<p>First body.</p>"},
        {"id": "second", "heading": "Second Heading", "body": "<p>Second body.</p>"},
    ]
    html = _render_sections(sections)
    assert 'id="first"' in html and "First Heading" in html and "First body" in html
    assert 'id="second"' in html and "Second Heading" in html
    print("✓ build_regulations: sections render with id + heading")


def test_build_regulations_faq_block_is_empty_when_faq_empty():
    assert _render_faq_block([]) == ""
    print("✓ build_regulations: faq block empty when faq missing")


def test_build_regulations_sources_render_with_url_and_note():
    sources = [{"title": "Source A", "note": "A note", "url": "https://a.example"}]
    html = _render_sources_block(sources)
    assert "Source A" in html
    assert "A note" in html
    assert "https://a.example" in html
    print("✓ build_regulations: sources render with url and note")


def test_build_regulations_jsonld_article_is_valid_schema_org():
    region = _minimal_valid_region()
    raw = _render_jsonld_article(region)
    data = json.loads(raw)
    assert data["@context"] == "https://schema.org"
    assert data["@type"] == "Article"
    assert data["headline"] == "Test OG title"
    assert data["mainEntityOfPage"]["@id"] == "https://getregula.com/test-region.html"
    print("✓ build_regulations: Article JSON-LD valid")


def test_build_regulations_jsonld_breadcrumb_has_three_levels():
    region = _minimal_valid_region()
    data = json.loads(_render_jsonld_breadcrumb(region))
    assert data["@type"] == "BreadcrumbList"
    items = data["itemListElement"]
    assert len(items) == 3
    assert items[0]["name"] == "Regula"
    assert items[1]["name"] == "Regulations"
    assert items[2]["name"] == "Testland"
    print("✓ build_regulations: BreadcrumbList has 3 levels")


def test_build_regulations_jsonld_faq_matches_visible_questions():
    region = _minimal_valid_region()
    data = json.loads(_render_jsonld_faq(region))
    assert data["@type"] == "FAQPage"
    assert len(data["mainEntity"]) == 1
    assert data["mainEntity"][0]["name"] == "Test question?"
    print("✓ build_regulations: FAQ JSON-LD matches visible questions")


def test_build_regulations_render_region_produces_valid_html():
    """End-to-end: render a minimal region and assert required SEO elements are present."""
    region = _minimal_valid_region()
    html = render_region(region)

    # SEO metadata
    assert "<title>Test title tag</title>" in html
    assert 'rel="canonical" href="https://getregula.com/test-region.html"' in html
    assert 'content="Test meta description.' in html
    assert 'property="og:title" content="Test OG title"' in html
    assert 'content="en_US"' in html  # og:locale

    # Content
    assert 'id="test-section"' in html
    assert "Test section" in html
    assert "Test body." in html
    assert "Test question?" in html
    assert "Test source" in html

    # Chrome
    assert 'class="skip-link"' in html
    assert 'id="progress-bar"' in html
    assert 'href="regulations.html"' in html or 'href="/regulations.html"' in html
    assert 'href="writing.html"' in html or 'href="/writing.html"' in html

    # All three JSON-LD blocks present and parseable
    blocks = list(re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S))
    assert len(blocks) == 3
    types = [json.loads(b.group(1))["@type"] for b in blocks]
    assert types == ["Article", "BreadcrumbList", "FAQPage"]
    print("✓ build_regulations: end-to-end render produces valid HTML")


def test_build_regulations_uk_region_loads_and_validates():
    """The shipped united-kingdom.py region file must load and validate."""
    uk_path = CONTENT_DIR / "united-kingdom.py"
    assert uk_path.exists(), "united-kingdom.py is missing"
    region = _load_region(uk_path)
    _validate_region(region, uk_path)
    assert region["slug"] == "uk-ai-regulation"
    assert region["flag"] == "🇬🇧"
    assert region["lang"] == "en-GB"
    assert len(region["tracker_rows"]) >= 3
    assert len(region["sections_html"]) >= 3
    assert len(region["faq"]) >= 3
    assert len(region["sources"]) >= 3
    print(f"✓ build_regulations: UK region loads and validates ({len(region['sections_html'])} sections)")


def test_build_regulations_all_regions_render_successfully(tmp_path, monkeypatch):
    """Every content/regulations/*.py file must build to valid HTML without errors.

    This is the regression guard: any new region file added to the directory
    will automatically be tested by this function. If a future region dict is
    malformed, this test will catch it.
    """
    files = sorted(CONTENT_DIR.glob("*.py"))
    files = [f for f in files if not f.name.startswith("_")]
    assert len(files) >= 1, "No region files found in content/regulations/"

    for path in files:
        region = _load_region(path)
        _validate_region(region, path)
        html = render_region(region)
        assert len(html) > 10_000, f"{path.name}: suspicious small output ({len(html)} bytes)"
        # Every rendered page must parse all three JSON-LD blocks
        blocks = list(re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S))
        for i, block in enumerate(blocks):
            try:
                json.loads(block.group(1))
            except Exception as e:
                raise AssertionError(f"{path.name}: JSON-LD block {i+1} invalid: {e}")
    print(f"✓ build_regulations: all {len(files)} region file(s) build successfully")
