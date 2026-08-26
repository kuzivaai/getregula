"""Guards for the qualifier, the first view of all three locale pages.

The qualifier is generated: one engine (site/assets/qualifier.js), one
structure (scripts/build_qualifier.py) and three string tables
(data/qualifier_copy/*.json). These tests hold the properties that split buys.

WHAT THIS DOES NOT CLAIM. Nothing here says the qualifier is usable, or
understood, or correct as guidance. No comprehension test has been run with any
reader and none of these checks is a substitute for one. These are mechanical properties only:
identical structure across languages, dates that agree with the repository's own
single source of truth, no compliance-state assertion anywhere in the copy, and
no live link that goes nowhere.

Every enumeration here comes from `git ls-files` or from the generator, never
from a list in this file.

Stdlib only.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_qualifier as builder          # noqa: E402
import determination_guard as guard        # noqa: E402
import omnibus                             # noqa: E402

COPY_DIR = REPO_ROOT / "data" / "qualifier_copy"
ENGINE = REPO_ROOT / "site" / "assets" / "qualifier.js"

# The map the generator itself uses. Reading it rather than restating it means a
# fourth locale is covered by these tests the moment it is added.
TARGETS = builder.TARGETS


def _tracked() -> set[str]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=REPO_ROOT,
                         capture_output=True, text=True, check=True)
    return {p for p in out.stdout.split("\0") if p}


def _tables() -> dict[str, dict]:
    return {key: json.loads((COPY_DIR / f"{key}.json").read_text(encoding="utf-8"))
            for key in TARGETS}


def _shape(node, prefix=""):
    """Every key path in a nested structure, lists included by index."""
    paths = set()
    if isinstance(node, dict):
        for key, value in node.items():
            paths.add(f"{prefix}/{key}")
            paths |= _shape(value, f"{prefix}/{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            paths.add(f"{prefix}[{i}]")
            paths |= _shape(value, f"{prefix}[{i}]")
    return paths


def _strings(node):
    """Every string leaf, so a check can be exhaustive over the copy."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _strings(value)


# --------------------------------------------------------------------------
# The generated pages are current

def test_every_locale_page_matches_a_fresh_render():
    """A hand-edit between the markers, or a stale page after a copy change."""
    for rel, text in builder.build(write=False).items():
        on_disk = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert on_disk == text, (
            f"{rel} differs from a fresh render. "
            f"Run: python3 scripts/build_qualifier.py")


def test_the_render_check_can_fail():
    """Control. Without this the test above passes for an empty corpus."""
    tampered = builder.build(write=False)["site/index.html"].replace(
        "<form id=\"qual-form\"", "<form id=\"qual-form-tampered\"", 1)
    assert tampered != (REPO_ROOT / "site/index.html").read_text(encoding="utf-8")


def test_every_target_page_and_copy_table_is_tracked():
    tracked = _tracked()
    for key, rel in TARGETS.items():
        assert rel in tracked, f"{rel} is not tracked, so it is not a surface"
        assert f"data/qualifier_copy/{key}.json" in tracked
    assert "site/assets/qualifier.js" in tracked


# --------------------------------------------------------------------------
# The three string tables are the same thing in three languages

def test_every_locale_table_has_identical_key_structure():
    tables = _tables()
    shapes = {key: _shape(table) for key, table in tables.items()}
    reference_key = "en"
    for key, shape in shapes.items():
        if key == reference_key:
            continue
        missing = shapes[reference_key] - shape
        extra = shape - shapes[reference_key]
        assert not missing and not extra, (
            f"{key}.json diverges from {reference_key}.json. "
            f"missing={sorted(missing)} extra={sorted(extra)}")


def test_a_dropped_key_is_caught():
    """Control for the parity check above."""
    tables = _tables()
    broken = json.loads(json.dumps(tables["de"]))
    del broken["routes"]["consultant"]["body"]
    assert _shape(broken) != _shape(tables["en"])


def test_every_locale_asks_the_same_questions_with_the_same_values():
    """Translations may change words. They may not change the encoding."""
    tables = _tables()
    reference = [(q["id"], tuple(o["value"] for o in q["options"]))
                 for q in tables["en"]["questions"]]
    for key, table in tables.items():
        got = [(q["id"], tuple(o["value"] for o in q["options"]))
               for q in table["questions"]]
        assert got == reference, (
            f"{key}.json changes a question id or an option value. Shared links "
            f"encode those values, so a change breaks every link already sent.")


# --------------------------------------------------------------------------
# Dates come from one place

def test_every_regulatory_date_matches_the_omnibus_module():
    """scripts/omnibus.py is the single source of truth for qualifier dates."""
    expected = {
        "prohibited": omnibus.DEADLINE_PROHIBITED,
        "article50": omnibus.DEADLINE_CURRENT_LAW,
        "marking": omnibus.DEADLINE_OMNIBUS_LIMITED,
        "annexIII": omnibus.DEADLINE_OMNIBUS_ANNEX_III,
    }
    for key, table in _tables().items():
        assert table["dates"] == expected, (
            f"{key}.json disagrees with scripts/omnibus.py: "
            f"{table['dates']} != {expected}")


def test_no_date_is_written_out_in_prose():
    """A hand-typed date is a date that will drift in one language and not the
    others. Every one is a {placeholder} rendered from the ISO value."""
    for key, table in _tables().items():
        months = [m.lower() for m in table["months"]]
        for text in _strings(table):
            if text.lower() in months:
                continue
            for month in months:
                assert not re.search(rf"\b{re.escape(month)}\b\s+\d{{4}}",
                                     text.lower()), (
                    f"{key}.json writes a date in prose: {text[:80]!r}")


def test_every_date_placeholder_resolves():
    """`dateFormat` is excluded by name: its {d}/{month}/{y} are the date
    renderer's own slots, not references into `dates`. `{n}` is the count the
    incomplete-answer message substitutes."""
    for key, table in _tables().items():
        known = set(table["dates"])
        # `dateFormat` slots and the build-time {tests} count are not dates.
        # The count is not exempted from checking, only from THIS check:
        # test_the_published_count_is_the_canonical_one asserts it resolved.
        skip = {table["dateFormat"], table["proof"]["tests"]}
        for text in _strings(table):
            if text in skip:
                continue
            for name in re.findall(r"\{(\w+)\}", text):
                assert name in known or name == "n", (
                    f"{key}.json uses an unknown placeholder {{{name}}}")


# --------------------------------------------------------------------------
# The one claim this project forbids outright

def test_no_copy_string_asserts_a_compliance_state():
    """Belt and braces beside scripts/determination_guard.py, which scans the
    rendered page. This reads the source the page is rendered from, so a
    forbidden phrase is caught before it can reach three languages at once."""
    for key, table in _tables().items():
        for text in _strings(table):
            hits = guard.determinations_in_text(text)
            assert not hits, f"{key}.json asserts a compliance state: {hits}"


def test_that_check_can_fail():
    """Control. The shape below is the one N125 recorded as shipped."""
    planted = "The generated artefact is compliant documentation for Article 50."
    assert guard.determinations_in_text(planted), (
        "the determination predicate no longer reacts, so the check above is a "
        "blank gate")


# --------------------------------------------------------------------------
# Every route the reader is offered actually goes somewhere

def test_every_link_in_the_copy_resolves():
    """Never present an unavailable path as actionable."""
    tracked = _tracked()
    for key, table in _tables().items():
        hrefs = set()
        for point in table["points"].values():
            if point.get("href"):
                hrefs.add(point["href"])
        for route in table["routes"].values():
            hrefs.add(route["href"])
        for item in table["nojsItems"]:
            hrefs.add(item["href"])
        for href in sorted(hrefs):
            if href.startswith("mailto:"):
                continue
            assert href.startswith("/"), f"{key}.json: unexpected href {href}"
            target = href.lstrip("/")
            candidates = [f"site/{target}"] if not target.endswith("/") else []
            candidates.append(f"site/{target.rstrip('/')}/index.html")
            assert any(c in tracked for c in candidates), (
                f"{key}.json links to {href}, which is not a tracked page")


# --------------------------------------------------------------------------
# One engine, no prose in it

def test_the_engine_carries_no_user_facing_prose():
    """If a sentence lives in the engine it exists once and is English for
    every reader. Every sentence belongs to a locale table."""
    engine = ENGINE.read_text(encoding="utf-8")
    for key, table in _tables().items():
        for text in _strings(table):
            if len(text) < 12:
                continue
            assert text not in engine, (
                f"{key}.json copy is duplicated inside qualifier.js: {text[:60]!r}")


def test_every_locale_page_loads_the_shared_engine_exactly_once():
    for rel in TARGETS.values():
        page = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert page.count('src="/assets/qualifier.js"') == 1, rel
        assert page.count('id="qual-copy"') == 1, rel
        assert page.count('id="qual-form"') == 1, rel


def test_the_embedded_table_is_the_committed_table():
    """The page must carry the file, not a copy of it that has drifted."""
    blob = re.compile(r'<script type="application/json" id="qual-copy">(.*?)</script>',
                      re.DOTALL)
    for key, rel in TARGETS.items():
        page = (REPO_ROOT / rel).read_text(encoding="utf-8")
        match = blob.search(page)
        assert match, f"{rel} carries no copy table"
        embedded = json.loads(match.group(1).replace("<\\/", "</"))
        on_disk = json.loads((COPY_DIR / f"{key}.json").read_text(encoding="utf-8"))
        assert embedded == on_disk, f"{rel} embeds a table that is not {key}.json"


def test_the_published_count_is_the_canonical_one():
    """The count is generated from data/site_facts.json, never typed. This
    asserts the placeholder resolved and that what shipped is the canonical
    figure, grouped with the locale's own thousands separator."""
    canonical = builder.canonical_test_count()
    for key, rel in TARGETS.items():
        table = _tables()[key]
        expected = builder.group(canonical, table["thousandsSep"])
        page = (REPO_ROOT / rel).read_text(encoding="utf-8")
        strip = re.search(r'<ul class="qual-proof">(.*?)</ul>', page, re.DOTALL)
        assert strip, f"{rel} carries no credibility strip"
        assert "{tests}" not in strip.group(1), f"{rel} shipped an unresolved placeholder"
        assert expected in strip.group(1), (
            f"{rel} publishes a count that is not the canonical {expected}")


def test_the_count_check_can_fail():
    """Control: a different figure would not be accepted."""
    canonical = builder.canonical_test_count()
    page = (REPO_ROOT / "site/index.html").read_text(encoding="utf-8")
    strip = re.search(r'<ul class="qual-proof">(.*?)</ul>', page, re.DOTALL).group(1)
    assert builder.group(canonical + 1, ",") not in strip


def test_the_engine_never_writes_markup():
    """Every string that reaches the page goes through textContent.

    A shared link carries the reader's five answers in the URL, so the decoder
    is an untrusted input path. It already refuses any value that is not one of
    the radio values rendered on the page, which was exercised in a browser
    against a script-injection payload, a wrong version marker, a short vector
    and junk: all five were rejected with no result and nothing injected. This
    is the static half of the same property, and it is the half that survives a
    future edit: if the engine never writes markup, an injection has nowhere to
    land even if the decoder is later loosened.
    """
    engine = ENGINE.read_text(encoding="utf-8")
    for sink in ("innerHTML", "outerHTML", "insertAdjacentHTML",
                 "document.write", "eval(", "new Function"):
        assert sink not in engine, (
            f"qualifier.js uses {sink}; the copy tables and the shared-link "
            f"decoder are inputs, so every string must go through textContent")


def test_the_shared_link_encoding_is_versioned():
    """A stateless encoding whose meaning can change must say which it is.

    AGENTS.md: old encodings must keep decoding
    correctly, so the version marker is written and checked rather than assumed.
    """
    engine = ENGINE.read_text(encoding="utf-8")
    assert "ENCODING_VERSION" in engine
    assert "bits[0] !== ENCODING_VERSION" in engine, (
        "the decoder does not reject a link written under a different version")
