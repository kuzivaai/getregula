# regula-ignore
"""Build reusable region tracker pages from content/regulations/*.py.

Stdlib only. Reads each REGION dict, validates against the schema, and
renders an SEO-optimised HTML page using content/regulations/_template.html.

Usage:
    python3 -m scripts.build_regulations              # build all regions
    python3 -m scripts.build_regulations united-kingdom  # build one region
    python3 -m scripts.build_regulations --check      # dry-run, validate only

See content/regulations/united-kingdom.py for the canonical example of
the REGION schema. Every field is required unless explicitly marked
optional in REGION_SCHEMA below.
"""
import importlib.util
import json
import sys
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content" / "regulations"
TEMPLATE_PATH = CONTENT_DIR / "_template.html"

# Required top-level keys on the REGION dict. Lists and dicts are validated by
# _validate_region() below with per-field rules.
REGION_SCHEMA = {
    "slug", "flag", "nav_label", "lang", "og_locale", "hreflang_self",
    "geo_region", "geo_placename", "status_cls", "status_text",
    "title_tag", "title_html", "meta_description", "meta_keywords",
    "og_title", "og_description", "twitter_title", "twitter_description",
    "last_updated", "published_time", "modified_time",
    "lede", "tracker_rows", "sections_html", "faq", "sources",
}

# Map tracker row state to the HTML badge class + visible label.
STATE_BADGE = {
    "verified": ("ok", "VERIFIED"),
    "gazetted": ("ok", "GAZETTED"),
    "confirmed": ("ok", "CONFIRMED"),
    "secondary": ("pend", "SECONDARY"),
    "pending": ("pend", "PENDING"),
    "estimated": ("pend", "ESTIMATED"),
    "live": ("ok", "LIVE"),
}


def _validate_region(region: dict, source: Path) -> None:
    """Fail loudly if the region dict is missing required keys or has wrong shape."""
    missing = REGION_SCHEMA - set(region.keys())
    if missing:
        raise ValueError(f"{source.name}: missing required keys: {sorted(missing)}")

    if not isinstance(region["tracker_rows"], list) or not region["tracker_rows"]:
        raise ValueError(f"{source.name}: tracker_rows must be a non-empty list")
    for i, row in enumerate(region["tracker_rows"]):
        for key in ("label", "value"):
            if key not in row:
                raise ValueError(f"{source.name}: tracker_rows[{i}] missing '{key}'")

    if not isinstance(region["sections_html"], list) or not region["sections_html"]:
        raise ValueError(f"{source.name}: sections_html must be a non-empty list")
    for i, sec in enumerate(region["sections_html"]):
        for key in ("id", "heading", "body"):
            if key not in sec:
                raise ValueError(f"{source.name}: sections_html[{i}] missing '{key}'")

    if not isinstance(region["faq"], list):
        raise ValueError(f"{source.name}: faq must be a list")
    for i, qa in enumerate(region["faq"]):
        for key in ("q", "a"):
            if key not in qa:
                raise ValueError(f"{source.name}: faq[{i}] missing '{key}'")

    if not isinstance(region["sources"], list):
        raise ValueError(f"{source.name}: sources must be a list")
    for i, src in enumerate(region["sources"]):
        if "title" not in src or "url" not in src:
            raise ValueError(f"{source.name}: sources[{i}] missing 'title' or 'url'")


def _load_region(path: Path) -> dict:
    """Import a content/regulations/<region>.py module and return its REGION dict."""
    spec = importlib.util.spec_from_file_location(f"region_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load region file: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "REGION"):
        raise ValueError(f"{path.name}: missing top-level REGION dict")
    return module.REGION


def _render_tracker_block(rows: list) -> str:
    """Render the live tracker HTML block from tracker_rows data."""
    html = ['        <div class="tracker">',
            '            <h2>Live tracker</h2>']
    for row in rows:
        state = row.get("state")
        badge_html = ""
        if state in STATE_BADGE:
            cls, label = STATE_BADGE[state]
            badge_html = f' &nbsp;<span class="{cls}">{label}</span>'
        html.append('            <div class="tracker-row">')
        html.append(f'                <div class="lbl">{row["label"]}</div>')
        html.append(f'                <div class="val">{row["value"]}{badge_html}</div>')
        html.append('            </div>')
    html.append('        </div>')
    return "\n".join(html)


def _render_sections(sections: list) -> str:
    """Render each content section with id anchor + heading + body HTML."""
    html = []
    for sec in sections:
        html.append(f'        <section id="{sec["id"]}">')
        html.append(f'            <h2>{sec["heading"]}</h2>')
        html.append(sec["body"].rstrip())
        html.append('        </section>\n')
    return "\n".join(html)


def _render_faq_block(faq: list) -> str:
    """Render the FAQ details/summary block."""
    if not faq:
        return ""
    html = ['        <section id="faq">',
            '            <h2>Frequently asked questions</h2>',
            '            <div class="faq">']
    for qa in faq:
        html.append('                <details>')
        html.append(f'                    <summary>{qa["q"]}</summary>')
        html.append(f'                    <p>{qa["a"]}</p>')
        html.append('                </details>')
    html.append('            </div>')
    html.append('        </section>')
    return "\n".join(html)


def _render_sources_block(sources: list) -> str:
    """Render the sources list with titles, notes, and URLs."""
    if not sources:
        return ""
    html = ['        <section id="sources">',
            '            <h2>Sources</h2>',
            '            <div class="sources">',
            '                <ul>']
    for src in sources:
        note = f' &mdash; {src["note"]}' if src.get("note") else ""
        html.append('                    <li>'
                    f'<strong><a href="{src["url"]}" target="_blank" rel="noopener">{src["title"]}</a></strong>'
                    f'{note}</li>')
    html.append('                </ul>')
    html.append('            </div>')
    html.append('        </section>')
    return "\n".join(html)


def _render_jsonld_article(region: dict) -> str:
    """Article schema — canonical SEO block for every region page."""
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": region["og_title"],
        "description": region["meta_description"],
        "image": "https://getregula.com/og-image.png",
        "datePublished": region["published_time"],
        "dateModified": region["modified_time"],
        "author": {
            "@type": "Organization",
            "name": "Regula",
            "url": "https://getregula.com",
        },
        "publisher": {
            "@type": "Organization",
            "name": "Regula",
            "url": "https://getregula.com",
            "logo": {
                "@type": "ImageObject",
                "url": "https://getregula.com/og-image.png",
            },
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"https://getregula.com/{region['slug']}.html",
        },
        "about": [
            {"@type": "Thing", "name": f"{region['geo_placename']} AI regulation"},
            {"@type": "Thing", "name": "Artificial Intelligence Governance"},
        ],
    }
    return json.dumps(data, indent=4)


def _render_jsonld_breadcrumb(region: dict) -> str:
    """BreadcrumbList schema — Regula > Regulations > <region>."""
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Regula", "item": "https://getregula.com/"},
            {"@type": "ListItem", "position": 2, "name": "Regulations", "item": "https://getregula.com/regulations.html"},
            {"@type": "ListItem", "position": 3, "name": region["geo_placename"],
             "item": f"https://getregula.com/{region['slug']}.html"},
        ],
    }
    return json.dumps(data, indent=4)


def _render_jsonld_faq(region: dict) -> str:
    """FAQPage schema from region.faq. Returns {} if no FAQ."""
    if not region.get("faq"):
        return json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": []}, indent=4)
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": qa["q"],
                "acceptedAnswer": {"@type": "Answer", "text": qa["a"]},
            }
            for qa in region["faq"]
        ],
    }
    return json.dumps(data, indent=4)


def render_region(region: dict) -> str:
    """Build the complete HTML page for a region dict and return it as a string."""
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    template = Template(template_text)

    substitutions = {
        **{k: region[k] for k in REGION_SCHEMA
           if k not in ("tracker_rows", "sections_html", "faq", "sources")},
        "tracker_block": _render_tracker_block(region["tracker_rows"]),
        "sections": _render_sections(region["sections_html"]),
        "faq_block": _render_faq_block(region["faq"]),
        "sources_block": _render_sources_block(region["sources"]),
        "jsonld_article": _render_jsonld_article(region),
        "jsonld_breadcrumb": _render_jsonld_breadcrumb(region),
        "jsonld_faq": _render_jsonld_faq(region),
    }
    return template.safe_substitute(substitutions)


def build(region_name: str | None = None, check_only: bool = False) -> list:
    """Build one region (by slug stem) or all regions. Returns list of built paths."""
    built = []
    files = sorted(CONTENT_DIR.glob("*.py"))
    files = [f for f in files if not f.name.startswith("_")]

    if region_name:
        target = CONTENT_DIR / f"{region_name}.py"
        if not target.exists():
            raise FileNotFoundError(f"Region file not found: {target}")
        files = [target]

    for path in files:
        region = _load_region(path)
        _validate_region(region, path)

        if check_only:
            print(f"  [check] {path.name} → OK ({region['slug']}.html)")
            continue

        html = render_region(region)
        out_path = ROOT / f"{region['slug']}.html"
        out_path.write_text(html, encoding="utf-8")
        size_kb = len(html) / 1024
        print(f"  [build] {path.name} → {out_path.name} ({size_kb:.1f} KB)")
        built.append(out_path)

    return built


def main(argv=None):
    argv = argv or sys.argv[1:]
    check_only = "--check" in argv
    positional = [a for a in argv if not a.startswith("--")]
    region_name = positional[0] if positional else None

    print(f"Regula regulations build — source: {CONTENT_DIR}")
    try:
        built = build(region_name=region_name, check_only=check_only)
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    if check_only:
        print("  All region files valid.")
    else:
        print(f"  Built {len(built)} region page(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
