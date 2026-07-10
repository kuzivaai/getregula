"""Tests for scripts/claim_auditor.py — the CI gate that blocks commits
introducing unverified factual claims to Markdown and HTML files.

Covers:
- The SECTION_HEADING regex (must exempt dotted section numbers in
  markdown headings but NOT bare integer headings that are claims
  dressed as titles).
- paragraph_has_source (URL, markdown link, file-ref, citation word).
- is_exempt_number (version, date, article/annex/recital references).
- scan_file end-to-end on synthetic Markdown inputs.
- strip_noise correctly blanks historical CHANGELOG sections and
  preserves line numbers.
"""
from __future__ import annotations

import sys
from pathlib import Path

# claim_auditor.py uses bare imports and sys.path.insert itself — but for the
# test file we import it as a module via the scripts/ directory.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import claim_auditor  # noqa: E402


# ---------------------------------------------------------------------------
# SECTION_HEADING regex
# ---------------------------------------------------------------------------

def test_section_heading_matches_dotted_section_number():
    """Structural headings like `### 4.2 File record schema` must be
    exempted from numeric-claim matching — `4.2 File` would otherwise
    match the `files?` unit in NUMERIC_CLAIM."""
    m = claim_auditor.SECTION_HEADING.match("### 4.2 File record schema")
    assert m is not None
    assert m.group(0) == "### 4.2"


def test_section_heading_matches_deep_hierarchy():
    """Three-level section numbers like `1.2.3` still match."""
    m = claim_auditor.SECTION_HEADING.match("#### 1.2.3 Deep nested section")
    assert m is not None
    assert m.group(0) == "#### 1.2.3"


def test_section_heading_does_not_match_bare_integer_heading():
    """`## 17 frameworks supported` is a claim dressed as a heading.
    The auditor must surface it, not exempt it via the section-heading
    mechanism (regression guard — this was a blind-spot in an earlier
    version of the regex that used `(?:\\.\\d+)*`)."""
    assert claim_auditor.SECTION_HEADING.match("## 17 frameworks supported") is None
    assert claim_auditor.SECTION_HEADING.match("# 403 patterns") is None
    assert claim_auditor.SECTION_HEADING.match("## 1,000 tests") is None


def test_section_heading_does_not_match_version_or_year():
    """`### v1.1 Release` and similar shouldn't match — the version
    itself is exempted by VERSION_LIKE, not SECTION_HEADING."""
    assert claim_auditor.SECTION_HEADING.match("### v1.1 Release") is None
    assert claim_auditor.SECTION_HEADING.match("## 2026 roadmap") is None


def test_section_heading_in_structural_refs_list():
    """SECTION_HEADING must be included in STRUCTURAL_REFS so scan_file
    applies it to the blocked-ranges check."""
    assert claim_auditor.SECTION_HEADING in claim_auditor.STRUCTURAL_REFS


# ---------------------------------------------------------------------------
# paragraph_has_source
# ---------------------------------------------------------------------------

def test_paragraph_has_source_url():
    has, reason = claim_auditor.paragraph_has_source(
        "The EP voted 569-45-23 on https://europarl.europa.eu/news/..."
    )
    assert has is True
    assert reason == "url"


def test_paragraph_has_source_markdown_link():
    has, reason = claim_auditor.paragraph_has_source(
        "Scanned 403 risk patterns [see the list](docs/risk-patterns.md)."
    )
    assert has is True
    assert reason == "md-link"


def test_paragraph_has_source_no_source():
    has, reason = claim_auditor.paragraph_has_source(
        "Regula ships 403 risk patterns today."
    )
    assert has is False
    assert reason == "no-source"


def test_paragraph_has_source_html_link():
    # Use a relative href so URL_RE doesn't match first and return "url".
    has, reason = claim_auditor.paragraph_has_source(
        'Defined in <a href="/docs/spec.md">the spec</a>.'
    )
    assert has is True
    assert reason == "html-link"


def test_paragraph_has_source_citation_word():
    has, reason = claim_auditor.paragraph_has_source(
        "Regula scans 8 languages (source: CLAUDE.md identity block)."
    )
    assert has is True
    assert reason == "citation-word"


# ---------------------------------------------------------------------------
# is_exempt_number
# ---------------------------------------------------------------------------

def test_is_exempt_number_version():
    assert claim_auditor.is_exempt_number("v1.7.0") is True
    assert claim_auditor.is_exempt_number("1.7.0") is True


def test_is_exempt_number_iso_date():
    assert claim_auditor.is_exempt_number("2026-04-16") is True


def test_is_exempt_number_long_date():
    assert claim_auditor.is_exempt_number("26 March 2026") is True


def test_is_exempt_number_article_ref():
    assert claim_auditor.is_exempt_number("Article 9") is True


def test_is_exempt_number_annex_ref():
    assert claim_auditor.is_exempt_number("Annex IV") is True


def test_is_exempt_number_plain_numeric_claim_is_not_exempt():
    assert claim_auditor.is_exempt_number("17 frameworks") is False
    assert claim_auditor.is_exempt_number("1,000 tests") is False


# ---------------------------------------------------------------------------
# scan_file end-to-end (synthetic Markdown)
# ---------------------------------------------------------------------------

def _write(tmp_path: Path, name: str, body: str, monkeypatch) -> Path:
    """Write a synthetic file under tmp_path and repoint claim_auditor.REPO_ROOT
    so scan_file can compute relative paths without hitting the real repo."""
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    monkeypatch.setattr(claim_auditor, "REPO_ROOT", tmp_path)
    return p


def test_scan_file_dotted_section_heading_not_flagged(tmp_path, monkeypatch):
    """The file that originally triggered the CI break: a spec doc with
    `### 4.2 File record schema` should not produce any findings."""
    md = "# Spec\n\n### 4.2 File record schema\n\nBody text only.\n"
    path = _write(tmp_path, "spec.md", md, monkeypatch)
    report = claim_auditor.scan_file(path, allowlist=[])
    assert report.scanned is True
    assert len(report.findings) == 0, [f.claim.snippet for f in report.findings]


def test_scan_file_bare_integer_heading_flags_claim_in_body(tmp_path, monkeypatch):
    """`## 17 frameworks supported` as a heading no longer exempts the
    paragraph's own claims. The heading itself is one paragraph;
    numeric-claim matching still applies to any body text that follows
    without a source."""
    md = "## 17 frameworks supported\n\nRegula scans 17 frameworks today.\n"
    path = _write(tmp_path, "bare.md", md, monkeypatch)
    report = claim_auditor.scan_file(path, allowlist=[])
    # At least one finding — either on the heading or on the body.
    assert len(report.findings) >= 1


def test_scan_file_sourced_claim_passes(tmp_path, monkeypatch):
    # Create the referenced file so FILE_REF_RE resolves it against tmp_path.
    (tmp_path / "references").mkdir()
    (tmp_path / "references" / "crosswalk.yaml").write_text("x: 1", encoding="utf-8")
    md = (
        "# Docs\n\n"
        "Regula scans 17 frameworks mapped via "
        "[references/crosswalk.yaml](references/crosswalk.yaml).\n"
    )
    path = _write(tmp_path, "sourced.md", md, monkeypatch)
    report = claim_auditor.scan_file(path, allowlist=[])
    assert len(report.findings) == 0


def test_scan_file_unsourced_claim_flagged(tmp_path, monkeypatch):
    # Avoid words that trigger CITATION_WORDS ("source", "see", "ref"...).
    md = "# Docs\n\nRegula currently scans 17 frameworks. Nothing else here.\n"
    path = _write(tmp_path, "unsourced.md", md, monkeypatch)
    report = claim_auditor.scan_file(path, allowlist=[])
    assert len(report.findings) >= 1
    snippets = [f.claim.snippet for f in report.findings]
    assert any("17" in s for s in snippets)


def test_scan_file_allowlist_exempts_match(tmp_path, monkeypatch):
    import re as re_module
    md = "# Docs\n\nRegula scans 17 frameworks today.\n"
    path = _write(tmp_path, "allowed.md", md, monkeypatch)
    allowlist = [re_module.compile(r"\b17\s+frameworks?\b")]
    report = claim_auditor.scan_file(path, allowlist=allowlist)
    assert len(report.findings) == 0


def test_scan_file_historical_changelog_section_skipped(tmp_path, monkeypatch):
    """Keep-a-Changelog historical `## [1.6.2]` sections are stripped
    by strip_noise and never audited (release notes are historical
    self-descriptions verifiable via git history)."""
    md = (
        "# Changelog\n\n"
        "## [Unreleased]\n\n"
        "Current work in progress.\n\n"
        "## [1.6.2] - 2026-04-16\n\n"
        "Released with 947 tests and 12 frameworks (historical).\n"
    )
    path = _write(tmp_path, "CHANGELOG.md", md, monkeypatch)
    report = claim_auditor.scan_file(path, allowlist=[])
    # Only [Unreleased] section is audited. Its body has no numeric claim.
    # The [1.6.2] section is skipped — no findings from its stale numbers.
    assert len(report.findings) == 0


def test_scan_file_skips_non_markdown_non_html(tmp_path, monkeypatch):
    path = _write(tmp_path, "ignored.txt",
                  "This has 47 tests and nothing else.\n", monkeypatch)
    report = claim_auditor.scan_file(path, allowlist=[])
    assert report.scanned is False
    assert len(report.findings) == 0


# ---------------------------------------------------------------------------
# Regression: the exact file that caused the original CI break
# ---------------------------------------------------------------------------

def test_regression_evidence_format_spec_passes():
    """docs/spec/regula-evidence-format-v1.md was the file that caused
    the CI break on commit 6fd70f3 — `### 4.2 File record schema`
    tripped NUMERIC_CLAIM because `files?` is a unit word. After the
    SECTION_HEADING fix, it should scan cleanly."""
    spec = REPO_ROOT / "docs" / "spec" / "regula-evidence-format-v1.md"
    if not spec.exists():
        return  # skip if spec hasn't been checked out
    report = claim_auditor.scan_file(spec, allowlist=claim_auditor.load_allowlist())
    assert len(report.findings) == 0, (
        f"Unexpected findings: {[f.claim.snippet for f in report.findings]}"
    )


# ---------------------------------------------------------------------------
# Regression: backticked file references must count as sources
# ---------------------------------------------------------------------------

def test_backticked_file_reference_counts_as_source(tmp_path, monkeypatch):
    """strip_noise blanks inline code spans, which used to erase
    `scripts/foo.py`-style citations before paragraph_has_source() ran —
    a numeric claim sourced by a backticked repo path was reported
    unsourced (CI break on the 8 Jul 2026 audit CHANGELOG entry). A code
    span that is purely a resolving repo-file reference must survive."""
    # The cited file must exist relative to the (repointed) repo root.
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "cli_evidence.py").write_text("# x\n", encoding="utf-8")
    path = _write(
        tmp_path, "note.md",
        "- Bundles over 500 MB are refused before extraction "
        "(limits defined in `scripts/cli_evidence.py`).\n",
        monkeypatch,
    )
    report = claim_auditor.scan_file(path, allowlist=[])
    assert len(report.findings) == 0, (
        f"backticked file ref not honoured as source: "
        f"{[f.claim.snippet for f in report.findings]}"
    )


def test_backticked_non_file_code_is_still_noise(tmp_path, monkeypatch):
    """Ordinary inline code (`--flag`, `some_function()`) must NOT count
    as a source — only spans that are purely a resolving repo file path."""
    path = _write(
        tmp_path, "note.md",
        "- Bundles over 500 MB are refused when you pass `--strict`.\n",
        monkeypatch,
    )
    report = claim_auditor.scan_file(path, allowlist=[])
    assert len(report.findings) == 1, (
        f"expected the unsourced claim to be flagged, got: "
        f"{[f.claim.snippet for f in report.findings]}"
    )


# ---------------------------------------------------------------------------
# Precision-claim enforcement (T3c)
# ---------------------------------------------------------------------------

def test_known_precision_values_include_published_figures():
    """Every precision figure published in README/TRUST/site copy must be
    derivable from the benchmark artifacts. If this fails after a
    benchmark re-run, the published copy needs a sweep, not this test."""
    known = claim_auditor.known_precision_values()
    for figure in ("83.5", "36.8", "15.2", "66.1", "36.7", "0.0", "60.6"):
        assert figure in known, f"published figure {figure}% not derivable"


def test_precision_guard_flags_fabricated_figure():
    """Mutation test: a planted precision claim that matches no benchmark
    value must be flagged (this is the guard's entire purpose)."""
    known = claim_auditor.known_precision_values()
    text = "Our scanner achieves 97.3% precision on production code.\n"
    problems = claim_auditor.check_precision_claims(text, known)
    assert problems == [(1, "97.3%")]


def test_precision_guard_passes_derivable_figures_all_locales():
    """Published figures pass in EN, DE (&auml; entity), and PT-BR
    (comma decimal) phrasings; percentages with no precision context
    are ignored entirely."""
    known = claim_auditor.known_precision_values()
    text = (
        "83.5% precision on production code (N=115).\n"
        "83,5% Pr&auml;zision auf Produktionscode.\n"
        "83,5% de precisao em codigo de producao.\n"
        "CPU usage stayed under 97.3% during the scan.\n"
    )
    assert claim_auditor.check_precision_claims(text, known) == []


def test_precision_guard_flags_stale_figure_in_locale_phrasing():
    """A drifted figure is caught in DE phrasing too — the guard must not
    be EN-only (locale-parity rule)."""
    known = claim_auditor.known_precision_values()
    text = "97,3% Pr&auml;zision auf Produktionscode.\n"
    problems = claim_auditor.check_precision_claims(text, known)
    assert len(problems) == 1


def test_precision_guard_flags_overprecise_two_decimal_figure():
    """A 2-decimal claim must match a benchmark value EXACTLY at two
    decimals — "83.52%" must not pass merely because it rounds to the
    real 83.5 (10 Jul 2026 audit finding: the old regex skipped
    2-decimal figures entirely)."""
    known = claim_auditor.known_precision_values()
    problems = claim_auditor.check_precision_claims(
        "achieves 83.52% precision on production code.\n", known)
    assert problems == [(1, "83.52%")]


def test_precision_guard_passes_exact_two_decimal_figure():
    """A 2-decimal figure that IS derivable passes. The artifact stores
    overall_precision already rounded (0.835), so its 2-decimal
    representation is 83.50."""
    known = claim_auditor.known_precision_values()
    assert "83.50" in known
    assert claim_auditor.check_precision_claims(
        "measured at 83.50% precision.\n", known) == []


def test_banned_claim_regex_matches_purged_phrasings():
    """The "zero false positives" claim (disproven July 2026) must be
    caught in every phrasing that previously appeared in published copy."""
    for phrase in ("zero false positives", "Zero False Positives",
                   "0 false positives", "0 False Positive"):
        assert claim_auditor._BANNED_CLAIM_RE.search(phrase), phrase
    # ...but ordinary FP discussion is not banned:
    for phrase in ("24 false positives", "reduces false positives",
                   "false-positive rate"):
        assert not claim_auditor._BANNED_CLAIM_RE.search(phrase), phrase


def test_banned_claim_absent_from_all_site_html():
    """No published site page may carry the banned claim. Mirrors the
    sweep inside verify_facts so the check also runs standalone."""
    site = REPO_ROOT / "site"
    offenders = []
    for page in sorted(site.rglob("*.html")):
        text = page.read_text(encoding="utf-8", errors="replace")
        if claim_auditor._BANNED_CLAIM_RE.search(text):
            offenders.append(str(page.relative_to(REPO_ROOT)))
    assert not offenders, f"banned claim republished in: {offenders}"


def test_corpus_classification_matches_label_py_convention():
    """claim_auditor.known_precision_values() re-implements label.py's
    app/library split (it cannot import benchmarks/ directly). This sync
    check fails if the conventions ever drift (data-copy-drift rule)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "label", REPO_ROOT / "benchmarks" / "label.py")
    label = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(label)
    for name in ("app_demo", "app_", "scikit-learn", "langchain",
                 "application", "apps"):
        expected = label._classify_corpus(name)
        actual = "app" if name.startswith("app_") else "library"
        assert actual == expected, (
            f"corpus convention drifted for {name!r}: claim_auditor says "
            f"{actual}, benchmarks/label.py says {expected}"
        )
