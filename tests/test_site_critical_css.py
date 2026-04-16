"""Guard tests for the FOUC fix applied site-wide in commits 7ed6e47 / 7d25105.

Every landing page under site/ carries an inline critical-CSS <style> block
that establishes the dark brand background on first paint, plus two external
stylesheet links loaded via the media="print" + onload swap pattern so they
don't block paint. These tests lock the pattern in: any page that regresses
back to a render-blocking <link rel="stylesheet"> for site.css will fail.

Stdlib only.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

# Pages that carry the full landing-page chrome and therefore MUST have the
# FOUC fix applied. Redirect stubs (site/de.html, site/pt-br.html etc. — 14
# lines each with a meta refresh) are excluded because they redirect away
# in 0s and never render their own styling.
REDIRECT_STUBS = {
    "site/de.html", "site/pt-br.html", "site/uae.html",
    "site/uk-ai-regulation.html", "site/south-africa-ai-policy.html",
    "site/south-korea-ai-regulation.html", "site/colorado-ai-regulation.html",
    "site/regulations.html",
    "site/blog-does-ai-act-apply.html", "site/blog-omnibus-delay.html",
    "site/blog-risk-tiers-in-code.html", "site/writing.html",
}

# Canonical critical-CSS markers every FOUC-fixed page must contain.
REQUIRED_MARKERS = (
    "color-scheme: dark",                    # canvas hint for pre-paint
    "background: #070711",                   # brand dark bg
    'media="print" onload="this.media=',     # non-render-blocking swap
    '<noscript>',                            # JS-disabled fallback
    'theme-color" content="#070711"',        # mobile browser chrome
)

# Pages with the hero terminal demo must additionally carry pre-CSS
# .term-panel rules so the inactive panels are hidden on first paint.
# Currently only site/index.html contains the demo.
TERMINAL_PAGES = {"site/index.html"}
TERMINAL_MARKERS = (".term-panel {", ".term-panel.active", ".term-body {")


def _fouc_fixed_pages():
    """Yield every HTML file under site/ that is NOT a redirect stub."""
    for path in sorted(SITE.rglob("*.html")):
        rel = path.relative_to(ROOT).as_posix()
        if rel in REDIRECT_STUBS:
            continue
        yield path, rel


def test_fouc_fix_applied_to_every_non_stub_page():
    """Every non-stub page under site/ carries the critical-CSS pattern."""
    pages = list(_fouc_fixed_pages())
    assert pages, "no pages found — glob regression?"
    missing = []
    for path, rel in pages:
        src = path.read_text()
        for marker in REQUIRED_MARKERS:
            if marker not in src:
                missing.append(f"{rel}: missing {marker!r}")
    assert not missing, (
        "FOUC fix drift detected. Each page listed below is missing a critical-CSS\n"
        "marker it must carry. Re-run /tmp/apply_fouc_fix.py (or the equivalent)\n"
        "or add the exemption to tests/test_site_critical_css.py if intentional.\n\n"
        + "\n".join(missing)
    )


def test_pages_with_terminal_demo_carry_panel_rules():
    """Only pages with the .term-panel elements carry the pre-CSS panel rules.

    This guards against two regressions:
      1. site/index.html drops the panel rules → panels flash on first paint
      2. A non-demo page gains the rules unnecessarily → ~200 extra bytes of CSS
    """
    for path, rel in _fouc_fixed_pages():
        src = path.read_text()
        has_panels_in_body = "<div class=\"term-panel" in src
        has_panel_rules_in_css = all(m in src for m in TERMINAL_MARKERS)

        if has_panels_in_body:
            assert has_panel_rules_in_css, (
                f"{rel} contains .term-panel elements but the critical-CSS\n"
                f"block is missing one of {TERMINAL_MARKERS}. The panel stack\n"
                "will flash on first paint before site.css arrives."
            )
        else:
            assert not has_panel_rules_in_css, (
                f"{rel} carries .term-panel critical-CSS rules but has no\n"
                ".term-panel elements in the body — dead code, safe to remove."
            )


def test_critical_css_style_block_is_in_head():
    """The inline <style> with brand colours must sit inside <head>, not <body>.

    A <style> in <body> is technically valid but defeats the fix: the browser
    may have already committed first paint using the blank canvas before
    reaching the body.
    """
    for path, rel in _fouc_fixed_pages():
        src = path.read_text()
        # Find the critical-CSS marker
        idx = src.find("color-scheme: dark")
        assert idx != -1, f"{rel} missing critical-CSS marker (covered by the main test)"

        # Check it appears before </head>
        head_close = src.find("</head>")
        assert head_close != -1, f"{rel} has no </head>"
        assert idx < head_close, (
            f"{rel}: critical-CSS appears AFTER </head>. Move the <style>\n"
            "block into <head> — otherwise it doesn't apply on first paint."
        )
