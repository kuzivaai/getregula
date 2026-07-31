#!/usr/bin/env python3
# regula-ignore
"""Claim Auditor — block commits that introduce unverified factual claims.

Scans Markdown, HTML, and landing-page files for:
  - Numeric claims (percentages, counts, fines, stars, users, benchmarks)
  - Currency amounts
  - Superlatives and competitive assertions ("only", "first", "best", "most")
  - Attributed quotes ("X said", "according to Y")

For each claim it checks whether a verifiable source is present in the same
paragraph: a URL, markdown link, HTML anchor, or reference to a file that is
GIT-TRACKED in the repository (e.g. `benchmarks/results/PRECISION.json`,
`tests/test_classification.py`). Claims without a nearby source are flagged.
Tracked, not merely present on disk: a gitignored file is not a source,
because a reader cannot open it. See ref_is_tracked() and finding N1.

Usage:
  python3 scripts/claim_auditor.py FILE [FILE ...]   # explicit file list
  python3 scripts/claim_auditor.py --staged           # git staged changes
  python3 scripts/claim_auditor.py --diff-base REF    # diff vs REF
  python3 scripts/claim_auditor.py --backtest N       # scan last N commits

Allowlist: lines matching any regex in `.claim-allowlist` (one per line,
'#' comments, blank lines ignored) are exempt. Use sparingly — each
allowlist entry is an unverified claim you have promised to verify manually.

Exit codes:
  0 = clean (no unverified claims found)
  1 = one or more files contain unverified claims
  2 = internal error
"""
from __future__ import annotations

import argparse
import functools
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# The gap a published count may put between the digits and its unit word.
# SINGLE SOURCE: scripts/cascade_count.py::GAP. Imported rather than copied,
# because the comment beside unit_patterns["tests"] asserts that this module
# and cascade_count "agree on what a test-count claim looks like", and a
# copied regex makes that assertion decay silently. The fallback keeps this
# module importable if cascade_count is ever absent (scripts/ ships as the
# PyPI package); tests/test_cascade_count.py asserts the two are identical,
# so the fallback cannot drift unnoticed either.
try:
    from cascade_count import GAP as _GAP, _dotted
except Exception:  # pragma: no cover - defensive, asserted equal by tests
    _GAP = r"(?:\s|</?[a-zA-Z][^>]*>)+"

    def _dotted(value: int) -> str:
        return f"{value:,}".replace(",", ".")


ALLOWLIST_PATH = REPO_ROOT / ".claim-allowlist"

SCANNED_SUFFIXES = {".md", ".markdown", ".html", ".htm"}

# ---------------------------------------------------------------------------
# Claim detection regexes
# ---------------------------------------------------------------------------

# Numeric claims: counts, percentages, with unit word. Excludes dates, versions,
# article numbers, and simple ordinals.
_NUMERIC_UNITS = (
    r"%|percent|stars?|users?|customers?|downloads?|installs?|subscribers?"
    r"|members?|companies|organi[sz]ations?|teams?|developers?|people"
    r"|tests?|commits?|pull requests?|PRs?|issues?|contributors?"
    r"|patterns?|commands?|frameworks?|languages?|files?|lines?|findings?"
    r"|fines?|penalties|cases?|incidents?|violations?|breaches?"
    r"|years?|months?|days?|hours?|minutes?|seconds?"
    r"|GB|MB|KB|TB|ms|tokens?|models?|datasets?|studies|papers?|surveys?"
    r"|million|billion|thousand|bn|M|k"
)
NUMERIC_CLAIM = re.compile(
    r"""
    (?<!\w)                                     # word boundary
    (?:[€$£¥]\s*)?                              # optional currency
    \d{1,3}(?:[,.\s]\d{3})*(?:\.\d+)?           # number with grouping
    (?:
        \s*%                                    # percent IS the unit
      | \s*(?:""" + _NUMERIC_UNITS + r""")\b    # or a word unit
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Standalone currency figures (no unit word needed)
CURRENCY_CLAIM = re.compile(
    r"(?<!\w)[€$£¥]\s*\d{1,3}(?:[,.\s]\d{3})*(?:\.\d+)?\s*"
    r"(?:million|billion|bn|M|k)?",
)

# Superlatives / competitive assertions — risky even without numbers
SUPERLATIVE_CLAIM = re.compile(
    r"\b("
    r"the only|only tool|first tool|first to|world'?s? first|industry'?s? first"
    r"|unique(?:ly)?|unprecedented|unrivall?ed|revolutionary"
    r"|no other|nothing else|sole|exclusive"
    r"|most (?:advanced|comprehensive|accurate|powerful)"
    r"|best[- ]in[- ]class|fastest|cheapest|leading"
    r"|outperform(?:s|ed)?|beats|better than"
    r")\b",
    re.IGNORECASE,
)

# Attributed statements — "X said", "according to Y", "Z reports"
# Only fires when the attribution verb is followed within ~100 chars by a
# number, quoted text, or explicit percentage — otherwise it's a noun form
# (e.g. "the project", "compliance reports") and should not flag.
ATTRIBUTED_CLAIM = re.compile(
    r"""
    \b(?:said|says|told|writes?|wrote|reported|reports|claimed?|stated
       |announced|confirmed|estimated|estimates|according\s+to|found\s+that)\b
    [^.\n]{0,100}?
    (?: \d | " | [‘’'] | \d+\s*% )
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Short time durations — UX copy, not statistical claims
SHORT_DURATION = re.compile(
    r"^\s*\d{1,3}\s*(?:seconds?|minutes?|ms|s|m)\s*$",
    re.IGNORECASE,
)

# Exemptions — matches we should NOT flag as numeric claims
VERSION_LIKE = re.compile(r"\bv?\d+\.\d+(?:\.\d+)?(?:[-+][\w.]+)?\b")
DATE_ISO = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
DATE_LONG = re.compile(
    r"\b\d{1,2}\s+"
    r"(?:January|February|March|April|May|June|July|August|"
    r"September|October|November|December)\s+\d{4}\b",
    re.IGNORECASE,
)
ARTICLE_REF = re.compile(r"\bArticles?\s+\d+", re.IGNORECASE)
ANNEX_REF = re.compile(r"\bAnnex\s+[IVX]+(?:,?\s+Category\s+\d+)?", re.IGNORECASE)
RECITAL_REF = re.compile(r"\bRecital\s+\d+", re.IGNORECASE)
CATEGORY_REF = re.compile(r"\bCategory\s+\d+", re.IGNORECASE)
CHAPTER_REF = re.compile(r"\bChapter\s+\d+", re.IGNORECASE)
# Markdown heading section-number prefix, e.g. `### 4.2 File record schema`.
# Without this, the `4.2 File` fragment matches NUMERIC_CLAIM (files? unit).
# Section numbers are structural when they include a decimal subsegment
# (4.2, 1.2.3) — those are always a hierarchy. Bare integer headings like
# `## 17 frameworks supported` are NOT exempted: those are claims dressed
# as headings, and the auditor should surface them.
SECTION_HEADING = re.compile(
    r"^\s*#{1,6}\s+\d+(?:\.\d+)+\b", re.MULTILINE,
)
# Ranges that should suppress numeric claim matches entirely
STRUCTURAL_REFS = [ARTICLE_REF, ANNEX_REF, RECITAL_REF, CATEGORY_REF, CHAPTER_REF,
                   SECTION_HEADING]

# Source indicators — presence of any of these within the same paragraph
# exempts the paragraph's claims.
URL_RE = re.compile(r"https?://[^\s)>\]}\"']+")
MD_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
HTML_LINK_RE = re.compile(r"<a\s+[^>]*href\s*=", re.IGNORECASE)
# The href VALUE, so a fragment-only or self-referential anchor can be told
# apart from a real outbound citation (F21).
ANCHOR_HREF = re.compile(
    r"""<a\s+[^>]*href\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""",
    re.IGNORECASE | re.VERBOSE,
)
MD_LINK_TARGET = re.compile(r"\[[^\]]+\]\(([^)\s]+)")

# F21 - markup whose URLs are infrastructure, never citations. Blanked
# before source detection so a stylesheet, favicon or og:image cannot
# vouch for a number. Claim detection still sees the untouched text.
NONCITATION_TAG = re.compile(
    r"<(?:link|meta|img|source|iframe|base|track|area|use)\b[^>]*>",
    re.IGNORECASE,
)
# Tags that carry the page's OWN address.
SELFREF_TAG = re.compile(r"<(?:link|meta)\b[^>]*>", re.IGNORECASE)
SELFREF_ATTR = re.compile(
    r"""rel\s*=\s*["'](?:canonical|alternate)["']"""
    r"""|(?:property|name)\s*=\s*["'](?:og:url|twitter:url)["']""",
    re.IGNORECASE,
)
URL_IN_ATTR = re.compile(r"""(?:href|content)\s*=\s*["']([^"']+)["']""",
                         re.IGNORECASE)
# Any HTML tag, used to tell attribute syntax from prose.
HTML_TAG = re.compile(r"<[^>]+>")
CITATION_WORDS = re.compile(
    r"\b(source|citation|ref(?:erence)?|see|cf\.|ibid\.|op\.? cit\.?|"
    r"primary source|verified against|verified via|verified[- ]primary|"
    r"verdict:?|per\s+https?://)\b[:.]?",
    re.IGNORECASE,
)
# Explicit bracketed verification labels used in audit/research docs.
# Presence of any of these in a paragraph effectively cites a source
# because the source URL lives in the surrounding doc (table row, footnote).
VERIFICATION_LABEL = re.compile(
    r"\[(?:VERIFIED|UNVERIFIED|FABRICATED|MISATTRIBUTED|OUTDATED|SOUND|"
    r"Verified|Unverified|Secondary(?:-confirmed)?|Partially\s+verified|"
    r"BROADLY\s+VERIFIED|NOT\s+FOUND|NOT\s+RE-VERIFIED|NOT\s+VERIFIED|"
    r"Verified[- ](?:primary|via-?secondary)"
    r")",
    re.IGNORECASE,
)
# Reference to a repo file (must resolve on disk to count)
FILE_REF_RE = re.compile(
    r"(?:(?<=[\s(`'\"])|^)"
    r"([a-zA-Z0-9_./-]+\.(?:json|md|yaml|yml|py|txt|html|csv|png|svg))"
    r"(?=[\s)`'\".,;:]|$)"
)


@functools.lru_cache(maxsize=1)
def tracked_paths() -> frozenset[str]:
    """Every path git tracks, repo-relative. Cached; see cache_clear().

    Loaded with `-z` so a path containing a newline or a quote cannot split
    a record. `git ls-files` without it quotes such names, which would then
    never match a reference.

    A repository with zero tracked files is impossible, so an empty result
    means git failed rather than that nothing is tracked. Raising here is
    deliberate: the alternative is that every file citation in the corpus
    silently stops counting and the gate reports hundreds of spurious
    findings with no clue why. Measurement rule 4 - an absent signal is not
    a passing signal.
    """
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=REPO_ROOT,
        capture_output=True, text=True, check=False,
    )
    paths = frozenset(p for p in result.stdout.split("\0") if p)
    if not paths:
        raise RuntimeError(
            f"git ls-files returned nothing in {REPO_ROOT} "
            f"(rc={result.returncode}, stderr={result.stderr.strip()!r}). "
            f"The claim auditor resolves citations against the tracked set, "
            f"so it cannot run without it."
        )
    return paths


def ref_is_tracked(ref: str) -> bool:
    """Is this file reference something a reader could actually open?

    Finding N1. All three call sites used to ask
    `(REPO_ROOT / ref).exists()`, which consults the WORKING TREE. A
    gitignored file therefore counted as provenance on the author's
    machine and was absent from a clean checkout,
    so `--diff-base main` scored 276 locally and 277 in CI at the same
    commit. `.claude/rules/measurement.md` rule 4b already holds that an
    untracked file is not a published surface because nobody outside the
    machine can read it; a citation is held to the same bar.

    `os.path.normpath` collapses `./x` and `a/../x` so the two spellings of
    one path give one answer. A reference that escapes the repository
    normalises to a `../` prefix, which is never in the tracked set.
    """
    return os.path.normpath(ref) in tracked_paths()


@dataclass
class Claim:
    file: str
    line: int
    kind: str          # numeric | currency | superlative | attributed
    snippet: str
    paragraph_start: int
    paragraph_end: int


@dataclass
class Finding:
    claim: Claim
    reason: str        # why no source was accepted


@dataclass
class FileReport:
    path: str
    scanned: bool
    claims: int = 0
    findings: list[Finding] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Loading & parsing
# ---------------------------------------------------------------------------

def load_allowlist() -> list[re.Pattern[str]]:
    if not ALLOWLIST_PATH.exists():
        return []
    patterns: list[re.Pattern[str]] = []
    for raw in ALLOWLIST_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            patterns.append(re.compile(line))
        except re.error as e:
            print(f"[claim-auditor] invalid allowlist regex: {line!r} ({e})",
                  file=sys.stderr)
    return patterns


def strip_noise(text: str, suffix: str) -> str:
    """Remove code fences, inline code, HTML script/style, HTML comments,
    and historical CHANGELOG sections.

    Preserves newline counts so line numbers continue to map to the
    original file — each stripped region is replaced with the same number
    of newlines it originally contained.

    Historical CHANGELOG sections under `## [X.Y.Z]` headings (but NOT
    `[Unreleased]`) are skipped because they are release-note
    self-descriptions verifiable via git history at the release commit
    and should not be re-audited on every PR.
    """
    def _blank(m: re.Match[str]) -> str:
        return "\n" * m.group(0).count("\n")

    text = re.sub(r"<!--.*?-->", _blank, text, flags=re.DOTALL)
    text = re.sub(r"<script[^>]*>.*?</script\s*>", _blank, text,
                  flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style\s*>", _blank, text,
                  flags=re.DOTALL | re.IGNORECASE)

    # Inline style attribute VALUES only. CSS lengths ("width:100%") are not
    # claims, and once percentages became detectable they would otherwise
    # have produced standing false positives forever — degrading the gate
    # this is meant to sharpen. Deliberately narrow: only the value inside
    # style="...", never the surrounding markup. Rendered-text attributes
    # (alt, title, aria-label) are user-visible prose and stay in scope.
    def _blank_style_value(m: re.Match[str]) -> str:
        head, value, tail = m.group(1), m.group(2), m.group(3)
        return head + "".join(
            "\n" if ch == "\n" else " " for ch in value) + tail

    text = re.sub(r'(\bstyle\s*=\s*")([^"]*)(")', _blank_style_value, text,
                  flags=re.IGNORECASE)
    text = re.sub(r"(\bstyle\s*=\s*')([^']*)(')", _blank_style_value, text,
                  flags=re.IGNORECASE)

    # A <pre> block is ONE verbatim unit. split_paragraphs() breaks on blank
    # lines, so a terminal transcript was being cut into stanzas, each an
    # island the auditor demanded a source for. There is nowhere to put a
    # citation inside verbatim command output without falsifying it, which
    # left only bad options: allowlist real output as if unverified, or
    # delete the blank lines the command actually prints.
    #
    # Each blank line inside a <pre> gets a zero-width space: the line count
    # is untouched, so reported coordinates still map to the original file,
    # but the block no longer splits. A plain space does NOT work, because
    # split_paragraphs() tests `line.strip() == ""` and a space strips to
    # empty; U+200B is not whitespace to str.strip(). Found landing the
    # class 1 derivation, and again one step later by the control.
    def _join_pre(m: re.Match[str]) -> str:
        return re.sub(r"^[ \t]*$", "​", m.group(0), flags=re.MULTILINE)

    text = re.sub(r"<pre\b[^>]*>.*?</pre\s*>", _join_pre, text,
                  flags=re.DOTALL | re.IGNORECASE)

    if suffix in (".md", ".markdown"):
        text = re.sub(r"```.*?```", _blank, text, flags=re.DOTALL)

        def _blank_inline(m: re.Match[str]) -> str:
            # Inline code is noise EXCEPT when the span is purely a
            # repo-file reference (`scripts/foo.py`) that resolves on
            # disk — backticks are this repo's idiomatic way of citing a
            # source file, and erasing them made such citations
            # invisible to paragraph_has_source().
            inner = m.group(0)[1:-1]
            if FILE_REF_RE.fullmatch(inner) and ref_is_tracked(inner):
                return f" {inner} "
            # ...and EXCEPT when the span is a command that names a repo
            # file. `fullmatch` above accepts `benchmarks/label.py` but
            # rejects `benchmarks/label.py score --breakdown`, so citing a
            # file worked while citing the command that produced the number
            # did not. That is backwards for this repo: PROGRAMME.md
            # Principle 1 accepts "MEASURED (command + output)" as evidence,
            # and the auditor's own remedy text tells the reader to add "a
            # reference to an existing file". The gate was blanking the
            # remedy it recommends. Finding F32.
            #
            # Still requires a path that is GIT-TRACKED, so prose cannot
            # satisfy it: a span like `we measured this carefully` has no
            # file token and stays blanked. Tracked rather than merely
            # present on disk since N1; see ref_is_tracked().
            for ref in FILE_REF_RE.finditer(inner):
                if ref_is_tracked(ref.group(1)):
                    return f" {inner} "
            # Blank the span but KEEP its newlines. `[^`]*` matches across
            # line breaks, so a span that wraps lines used to be replaced by
            # spaces alone — silently deleting those newlines and shifting
            # every subsequent reported line number up by one per wrapped
            # span. Reported coordinates then drift further the deeper into
            # the file a claim sits, which sends anyone fixing a finding to
            # the wrong line. Guarded by tests/test_claim_auditor_coords.py.
            return "".join("\n" if ch == "\n" else " " for ch in m.group(0))

        text = re.sub(r"`[^`]*`", _blank_inline, text)
        # Skip historical release sections in Keep-a-Changelog files.
        # Match from a `## [1.2.3]` heading (or any non-Unreleased
        # bracketed version) up to the next `## ` heading at the same
        # level or EOF. Preserves newlines.
        text = re.sub(
            r"(?ms)^##\s+\[(?!Unreleased\])[^\]]+\].*?(?=^##\s+\[|\Z)",
            _blank, text,
        )
    return text


def split_paragraphs(text: str) -> list[tuple[int, int, str]]:
    """Return [(start_line_1based, end_line_1based, text)]."""
    lines = text.splitlines()
    paragraphs: list[tuple[int, int, str]] = []
    buf: list[str] = []
    start: int = 1
    for i, line in enumerate(lines, start=1):
        if line.strip() == "":
            if buf:
                paragraphs.append((start, i - 1, "\n".join(buf)))
                buf = []
            start = i + 1
        else:
            if not buf:
                start = i
            buf.append(line)
    if buf:
        paragraphs.append((start, len(lines), "\n".join(buf)))
    return paragraphs


def is_exempt_number(match_text: str) -> bool:
    """Numeric-looking text that should not count as a claim."""
    snippet = match_text.strip()
    if VERSION_LIKE.fullmatch(snippet):
        return True
    if DATE_ISO.search(snippet) or DATE_LONG.search(snippet):
        return True
    if ARTICLE_REF.search(snippet) or ANNEX_REF.search(snippet):
        return True
    if RECITAL_REF.search(snippet):
        return True
    if SHORT_DURATION.match(snippet):
        return True
    # Small integer "N files" / "N cases" / "N commands" phrases within a
    # repo that publishes its own counts — these are self-claims that are
    # either verifiable from the repo or allowlisted explicitly.
    return False


# ---------------------------------------------------------------------------
# Source presence
# ---------------------------------------------------------------------------

def _blank_preserving_newlines(text: str) -> str:
    return "".join("\n" if ch == "\n" else " " for ch in text)


def _citable_text(paragraph: str) -> str:
    """The paragraph with non-citation markup blanked, newlines preserved.

    Claim DETECTION still runs on the untouched paragraph; this view exists
    only to answer "is there a citation here", where machine metadata must
    not vote.
    """
    return NONCITATION_TAG.sub(
        lambda m: _blank_preserving_newlines(m.group(0)), paragraph)


def _normalise_url(url: str) -> str:
    """Compare-ready form: no fragment, no trailing slash or punctuation."""
    url = url.split("#", 1)[0]
    return url.rstrip("/.,;:\"')>]}").lower()


@dataclass(frozen=True)
class PageIdentity:
    """What counts as "this page itself" for self-citation purposes."""
    urls: frozenset[str]
    rel_path: str

    @property
    def basename(self) -> str:
        return self.rel_path.rsplit("/", 1)[-1]


def page_identity(text: str, rel_path: str) -> PageIdentity:
    """Collect every address that means "this page", from its own markup."""
    urls = set()
    for m in SELFREF_TAG.finditer(text):
        tag = m.group(0)
        if not SELFREF_ATTR.search(tag):
            continue
        for u in URL_IN_ATTR.findall(tag):
            urls.add(_normalise_url(u))
    return PageIdentity(urls=frozenset(urls), rel_path=rel_path)


def _is_self_url(url: str, identity: PageIdentity | None) -> bool:
    return bool(identity) and _normalise_url(url) in identity.urls


def _is_self_file_ref(ref: str, identity: PageIdentity | None) -> bool:
    """A document citing its own filename is a circle, not a source."""
    if identity is None:
        return False
    if ref == identity.rel_path:
        return True
    # A bare filename with no directory component, matching this page's own.
    return "/" not in ref and ref == identity.basename


def paragraph_has_source(paragraph: str,
                         identity: PageIdentity | None = None) -> tuple[bool, str]:
    """Return (has_source, reason_if_not).

    F21. A page's own address is not a source for anything on that page,
    and most URLs in an HTML `<head>` are not citations at all. This
    function used to return True on the first URL it saw; a `<head>` parses
    as one paragraph and is dense with non-citation URLs (rel=canonical,
    og:url, og:image, stylesheet and preconnect hrefs, icons), so every
    numeric claim in a `<meta name="description">` was permanently
    "sourced".

    MEASURED 2026-07-28, before the repair: 27 numeric matches inside
    description-like `<meta>` tags across the 56 tracked site pages (24
    after exemptions), every one reporting reason "url".

    Three classes of URL never count as a citation:
      1. machine metadata  - link/meta/img/source/iframe attributes
      2. self-reference    - the page's own address, on a tag or in prose
      3. fragment anchors  - href="#section" points back into this page

    `identity` supplies (2) and is optional so existing callers keep
    working; `scan_file` always passes it. Guarded by
    tests/test_selfref_sourcing.py.
    """
    citable = _citable_text(paragraph)

    for m in URL_RE.finditer(citable):
        if not _is_self_url(m.group(0), identity):
            return True, "url"
    for m in MD_LINK_RE.finditer(citable):
        target = MD_LINK_TARGET.search(m.group(0))
        if target and not _is_self_url(target.group(1), identity):
            return True, "md-link"
    for m in ANCHOR_HREF.finditer(citable):
        href = (m.group(1) or m.group(2) or m.group(3) or "").strip()
        if not href or href.startswith("#"):
            continue          # in-page anchor: points back at this page
        if not _is_self_url(href, identity):
            return True, "html-link"
    if CITATION_WORDS.search(citable):
        return True, "citation-word"
    if VERIFICATION_LABEL.search(citable):
        return True, "verification-label"
    # File references - must resolve on disk, and must not be this page
    for m in FILE_REF_RE.finditer(citable):
        ref = m.group(1)
        if _is_self_file_ref(ref, identity):
            continue
        if ref_is_tracked(ref):
            return True, f"file-ref:{ref}"
    return False, "no-source"


# ---------------------------------------------------------------------------
# Scan a single file
# ---------------------------------------------------------------------------

QUARANTINE_PATH = REPO_ROOT / ".claim-quarantine.json"
_QUARANTINE_CACHE: set | None = None


def _normalise_claim(text: str) -> str:
    """Whitespace-normalised claim text — the quarantine's key material."""
    return " ".join(text.split())


def load_quarantine() -> set:
    """Load the pre-existing unverified backlog as {(file, claim)}.

    Quarantine is NOT approval. These claims predate the auditor's ability
    to see bare percentages; they are recorded so the gate can go green for
    NEW claims immediately while the backlog is burned down. Entries key on
    file plus normalised claim text, never line numbers: line-keyed entries
    rot on every page edit.
    """
    global _QUARANTINE_CACHE
    if _QUARANTINE_CACHE is not None:
        return _QUARANTINE_CACHE
    entries: set = set()
    if QUARANTINE_PATH.exists():
        try:
            doc = json.loads(QUARANTINE_PATH.read_text(encoding="utf-8"))
            for e in doc.get("entries", []):
                entries.add((e["file"], _normalise_claim(e["claim"])))
        except (OSError, ValueError, KeyError) as exc:
            # Fail loud: a malformed quarantine must not silently become an
            # empty one, which would look like a clean gate.
            raise SystemExit(
                f"claim-auditor: {QUARANTINE_PATH.name} is unreadable "
                f"({exc}). Refusing to run with an unknown quarantine state."
            ) from exc
    _QUARANTINE_CACHE = entries
    return entries


def is_quarantined(file_path: str, snippet: str) -> bool:
    return (file_path, _normalise_claim(snippet)) in load_quarantine()


def scan_file(path: Path, allowlist: list[re.Pattern[str]]) -> FileReport:
    report = FileReport(path=str(path.relative_to(REPO_ROOT)
                                  if path.is_absolute() else path),
                        scanned=False)
    if path.suffix.lower() not in SCANNED_SUFFIXES:
        return report
    if not path.exists():
        return report
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return report

    report.scanned = True
    cleaned = strip_noise(raw, path.suffix.lower())
    paragraphs = split_paragraphs(cleaned)
    # F21: the page's own address, collected once from its own markup, so a
    # self-citation cannot source anything on this page.
    identity = page_identity(raw, report.path)

    def match_line(para_text: str, offset: int, para_start_line: int) -> int:
        """Return 1-based file line for a regex match inside a paragraph."""
        return para_start_line + para_text.count("\n", 0, offset)

    for start, end, para in paragraphs:
        has_src, src_reason = paragraph_has_source(para, identity)
        para_claims: list[Claim] = []

        # Pre-compute character ranges occupied by structural regulatory
        # references (Article N, Annex IV, Category 4, etc.). Numeric claim
        # matches whose start falls inside any of these ranges are treated
        # as exempt — they are cross-references to regulatory text, not
        # statistical claims.
        blocked_ranges: list[tuple[int, int]] = []
        for pat in STRUCTURAL_REFS:
            for m in pat.finditer(para):
                blocked_ranges.append((m.start(), m.end()))

        # ATTRIBUTED_CLAIM needs quoted text near an attribution verb. Inside
        # a tag the quote characters are attribute syntax, not quotation, so
        # `<meta ... content="... Reports | Regula">` reads as "Regula
        # reports <quote>". Surfaced on site/pricing.html the moment the F21
        # repair stopped the head block counting as sourced. Numeric claims
        # inside tags are still detected: a meta description IS published
        # prose. Only the attribution kind is excluded here.
        tag_ranges = [(m.start(), m.end()) for m in HTML_TAG.finditer(para)]

        def _in_blocked(pos: int) -> bool:
            return any(lo <= pos < hi for lo, hi in blocked_ranges)

        def _in_tag(pos: int) -> bool:
            return any(lo <= pos < hi for lo, hi in tag_ranges)

        def _add(kind: str, m: re.Match[str]) -> None:
            snippet = m.group(0).strip()
            if kind == "numeric" and is_exempt_number(snippet):
                return
            if kind in ("numeric", "currency") and _in_blocked(m.start()):
                return
            if kind == "attributed" and _in_tag(m.start()):
                return
            para_claims.append(Claim(
                file=report.path,
                line=match_line(para, m.start(), start),
                kind=kind,
                snippet=snippet[:120],
                paragraph_start=start,
                paragraph_end=end,
            ))

        for m in NUMERIC_CLAIM.finditer(para):
            _add("numeric", m)
        for m in CURRENCY_CLAIM.finditer(para):
            _add("currency", m)
        for m in SUPERLATIVE_CLAIM.finditer(para):
            _add("superlative", m)
        for m in ATTRIBUTED_CLAIM.finditer(para):
            _add("attributed", m)

        report.claims += len(para_claims)

        if has_src:
            continue  # paragraph sourced → all claims inside are fine

        raw_lines = raw.splitlines()
        for claim in para_claims:
            idx = claim.line - 1
            claim_line = raw_lines[idx] if 0 <= idx < len(raw_lines) else ""
            if any(
                p.search(claim_line)
                or p.search(claim.snippet)
                or p.search(para)
                for p in allowlist
            ):
                continue
            if is_quarantined(report.path, claim.snippet):
                continue
            report.findings.append(Finding(
                claim=claim, reason=src_reason,
            ))
    return report


# ---------------------------------------------------------------------------
# Input selection
# ---------------------------------------------------------------------------

def git(*args: str) -> str:
    # Safe: args are a hardcoded list, no shell injection risk
    result = subprocess.run(
        ["git", *args], cwd=REPO_ROOT,
        capture_output=True, text=True, check=False,
    )
    return result.stdout


def files_staged() -> list[Path]:
    out = git("diff", "--cached", "--name-only", "--diff-filter=ACMR")
    return [REPO_ROOT / f for f in out.splitlines() if f]


def files_diff_base(base: str) -> list[Path]:
    out = git("diff", "--name-only", "--diff-filter=ACMR", f"{base}...HEAD")
    return [REPO_ROOT / f for f in out.splitlines() if f]


def files_commit(sha: str) -> list[Path]:
    out = git("show", "--name-only", "--diff-filter=ACMR",
              "--pretty=format:", sha)
    return [REPO_ROOT / f for f in out.splitlines() if f]


def last_n_commits(n: int) -> list[str]:
    out = git("log", "-n", str(n), "--pretty=format:%h")
    return [s for s in out.splitlines() if s]


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def human_report(reports: list[FileReport]) -> str:
    lines: list[str] = []
    total_claims = sum(r.claims for r in reports)
    total_findings = sum(len(r.findings) for r in reports)
    scanned = [r for r in reports if r.scanned]
    lines.append(
        f"claim-auditor: scanned {len(scanned)} file(s), "
        f"{total_claims} claim(s), {total_findings} unsourced"
    )
    if total_findings == 0:
        lines.append("  all claims sourced — OK")
        return "\n".join(lines)
    for r in reports:
        if not r.findings:
            continue
        lines.append(f"\n  {r.path} — {len(r.findings)} unsourced")
        for f in r.findings[:20]:
            lines.append(
                f"    L{f.claim.line} [{f.claim.kind}] {f.claim.snippet!r}"
            )
        if len(r.findings) > 20:
            lines.append(f"    ... and {len(r.findings) - 20} more")
    lines.append(
        "\nFix: add a URL, markdown link, or reference to an existing file "
        "(benchmarks/*.json, tests/*.py) in the same paragraph. "
        "To exempt a line, add a regex to .claim-allowlist."
    )
    return "\n".join(lines)


def json_report(reports: list[FileReport]) -> str:
    return json.dumps(
        {
            "scanned": [r.path for r in reports if r.scanned],
            "total_claims": sum(r.claims for r in reports),
            "total_findings": sum(len(r.findings) for r in reports),
            "files": [
                {
                    "path": r.path,
                    "claims": r.claims,
                    "findings": [asdict(f) for f in r.findings],
                }
                for r in reports if r.scanned
            ],
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# Backtest
# ---------------------------------------------------------------------------

def backtest(n: int, allowlist: list[re.Pattern[str]]) -> int:
    shas = last_n_commits(n)
    if not shas:
        print("claim-auditor: no commits found", file=sys.stderr)
        return 2
    grand_total_findings = 0
    per_commit: list[tuple[str, int, int]] = []
    for sha in shas:
        files = files_commit(sha)
        reports = [scan_file(f, allowlist) for f in files]
        scanned = sum(1 for r in reports if r.scanned)
        findings = sum(len(r.findings) for r in reports)
        per_commit.append((sha, scanned, findings))
        grand_total_findings += findings
    print(f"\nclaim-auditor backtest — last {n} commits\n")
    print(f"{'commit':<10}  {'files':>6}  {'findings':>10}  "
          f"{'would block':>12}  subject")
    print("-" * 80)
    for sha, scanned, findings in per_commit:
        subject = git("log", "-n", "1", "--pretty=format:%s", sha).strip()
        block = "YES" if findings > 0 else "no"
        print(f"{sha:<10}  {scanned:>6}  {findings:>10}  "
              f"{block:>12}  {subject[:45]}")
    print("-" * 80)
    print(f"total unsourced findings across {n} commits: "
          f"{grand_total_findings}")
    blocked = sum(1 for _, _, f in per_commit if f > 0)
    print(f"commits that would have been blocked: {blocked} / {len(shas)}")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Precision-claim enforcement (T3c)
# ---------------------------------------------------------------------------

# A percentage is treated as a precision claim when one of these word stems
# appears on the same line. Same-line (not a char window) so an unrelated
# percentage on an adjacent line can't inherit the context. Covers EN
# "precision", DE "Präzision" (raw or the &auml; entity), PT-BR
# "precisão"/"precisao".
_PRECISION_CONTEXT_RE = re.compile(r"(?i)(precis|pr&auml;z|präz)")
# Up to 2 decimals: a fabricated "83.52%" must be MATCHED (then rejected
# against the known set) rather than silently skipped by the regex.
_PCT_RE = re.compile(r"(?<![\d.,])(\d{1,3}(?:[.,]\d{1,2})?)\s*%")

# Phrases banned from published site copy: the "zero false positives"
# claim was disproven by the July 2026 audit (24 BLOCK-severity FPs of 62
# on the v1.7.0 blind corpus) and purged from 8 locations across two
# sessions. This check stops it returning. docs/MODEL_CARD.md's scoped
# synthetic-corpus statement and llms-full.txt's correction block are
# deliberately NOT covered (site HTML only).
_BANNED_CLAIM_RE = re.compile(r"(?i)\b(?:zero|0)\s+false\s+positives?\b")


def known_precision_values() -> set[str]:
    """Every precision figure derivable from the benchmark artifacts.

    Sources (never a hardcoded copy — the data-copy-drift rule):
      - benchmarks/results/PRECISION.json           (dev corpus, N=446)
      - benchmarks/results/random_corpus/PRECISION.json (random corpus, N=115)
      - benchmarks/labels.json                       (per-corpus and
        per-severity figures, computed the same way benchmarks/label.py
        and the published PRECISION_RECALL report compute them)

    Returns string representations at 1-decimal and integer rounding
    (e.g. 0.835 -> {"83.5", "84"}), since published copy uses both.
    """
    values: set[float] = set()

    def _walk(obj) -> None:
        if isinstance(obj, dict):
            for key, val in obj.items():
                if isinstance(val, (int, float)) and "precision" in key:
                    values.add(float(val))
                elif isinstance(val, str):
                    # Notes/methodology prose inside the artifact also states
                    # figures (e.g. "Including test code: 60.6%").
                    for m in re.finditer(r"(\d{1,3}(?:\.\d)?)%", val):
                        values.add(float(m.group(1)) / 100)
                else:
                    _walk(val)
        elif isinstance(obj, list):
            for val in obj:
                _walk(val)

    for rel in ("benchmarks/results/PRECISION.json",
                "benchmarks/results/random_corpus/PRECISION.json"):
        path = REPO_ROOT / rel
        if path.exists():
            _walk(json.loads(path.read_text(encoding="utf-8")))

    labels_path = REPO_ROOT / "benchmarks" / "labels.json"
    if labels_path.exists():
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from risk_types import compute_finding_tier

        labelled = [entry for entry in
                    json.loads(labels_path.read_text(encoding="utf-8"))
                    if entry.get("label") in ("tp", "fp")]
        groups: dict[str, list[int]] = {}
        for entry in labelled:
            # Same corpus convention as benchmarks/label.py _classify_corpus.
            corpus = ("app" if entry.get("project", "").startswith("app_")
                      else "library")
            severity = compute_finding_tier(entry.get("tier", ""),
                                            entry.get("confidence_score", 0))
            for key in (corpus, "all", f"{corpus}:{severity}", f"all:{severity}"):
                bucket = groups.setdefault(key, [0, 0])
                bucket[0 if entry["label"] == "tp" else 1] += 1
        for tp, fp in groups.values():
            if tp + fp:
                values.add(tp / (tp + fp))

    reps: set[str] = set()
    for val in values:
        pct = val * 100
        reps.add(f"{pct:.1f}")
        reps.add(f"{pct:.2f}")
        reps.add(str(int(round(pct))))
    return reps


def check_precision_claims(text: str, known: set[str]) -> list[tuple[int, str]]:
    """Return (line, claim) for each precision percentage in `text` that does
    not match any figure derivable from the benchmark data."""
    problems: list[tuple[int, str]] = []
    for line_num, line in enumerate(text.splitlines(), start=1):
        if not _PRECISION_CONTEXT_RE.search(line):
            continue
        for m in _PCT_RE.finditer(line):
            raw = m.group(1).replace(",", ".")
            val = float(raw)
            if re.search(r"\.\d\d$", raw):
                # A 2-decimal claim asserts more precision than published
                # copy ever legitimately uses — require an exact 2-decimal
                # match, never a 1-decimal rounding (else fabricated
                # "83.52%" would pass because it rounds to the real 83.5).
                candidates = {raw}
            else:
                candidates = {raw, f"{val:.1f}", str(int(round(val)))}
            if candidates & known:
                continue
            problems.append((line_num, m.group(0)))
    return problems


# Files carrying precision claims, beyond the count-check list.
PRECISION_EXTRA_FILES = [
    "site/about.html",
    "site/regions/uae.html",
    "site/llms.txt",
    "site/llms-full.txt",
    "docs/AI_GOVERNANCE.md",
    "docs/benchmarks/PRECISION_RECALL_2026_04.md",
    "docs/examples/exec-summary-sample.html",
]


# ---------------------------------------------------------------------------
# F22 - stale-number decisions are data, not a magnitude guess
# ---------------------------------------------------------------------------

# The defect this replaces:
#
#     if found_val < int(actual_str) * 0.5:
#         continue
#
# Canonical test count 2,363 put that floor at 1,181.5, so any published
# figure below it was skipped in silence. The programme's own P0 control
# cleared the floor by 2%. A gate that goes quiet as the error gets larger
# is worse than no gate, because it reads as a pass.
#
# The floor did guard something real: a legitimately different quantity can
# share a unit word with a canonical one. That is now handled by NAMING the
# exemptions instead of guessing them from size. Every suppression is
# visible, carries a reason, and is scoped to one file and one phrase -
# exactly the discipline `.claim-quarantine.json` already applies to claims.
#
# Adding an entry here is a claim that the number means something else.
# Guarded by tests/test_stale_number_floor.py.

# ---------------------------------------------------------------------------
# F24 - published recall fractions must be derivable from a committed artefact
# ---------------------------------------------------------------------------
#
# The auditor could derive precision from PRECISION.json and could not
# derive a recall figure at all, so every published recall number was
# outside the reach of the gate that exists to catch published numbers.
# That is how "80% recall" (n=5) survived, and how three different
# conditions came to be quoted as though they were one measurement.
#
# `benchmarks/synthetic/RECALL.json` is now produced by
# scripts/build_recall_artefact.py from an actual run, and every fraction in
# it carries a path and a gate condition. This check enforces two things
# about any published synthetic-corpus recall fraction:
#
#   1. the fraction exists in the artefact, and
#   2. the paragraph publishing it names a path AND a gate condition.
#
# (2) is not pedantry. MEASURED 2026-07-28: on this corpus the same tier
# scores 10/30, 16/30 and 23/30 depending only on which gates are
# satisfied. A bare fraction is an average over conditions nobody chose.

RECALL_ARTEFACT_PATH = REPO_ROOT / "benchmarks/synthetic/RECALL.json"

# Paragraphs are only inspected when they are talking about recall.
# Inflections included: "the scanner recalls 10/30" is a recall claim, and a
# bare `\brecall\b` silently skipped it. Found by a test of this check
# passing for the wrong reason - the paragraph was never inspected at all.
RECALL_CONTEXT = re.compile(r"\brecall(?:s|ed|ing)?\b", re.IGNORECASE)
FRACTION_RE = re.compile(r"(?<!\w)(\d{1,3})\s*/\s*(\d{1,3})(?!\w)")

# A published fraction must name where it came from, on both axes.
RECALL_PATH_LABEL = re.compile(
    r"\bscanner\b|\bclassifier\b|regula\s+check|classify\(\)|scan_files",
    re.IGNORECASE,
)
RECALL_GATE_LABEL = re.compile(
    r"\bdefault\b|\bdomain[- ]?(?:declared|s)?\b|ai[- ]?(?:library\s+)?import"
    r"|both\s+gates|no\s+flags",
    re.IGNORECASE,
)
# A figure the programme has withdrawn may still appear, because deleting a
# corrected number destroys the record of the correction. It must say so in
# the same paragraph. This is the only way past the artefact check, and
# tests/test_recall_artefact.py holds it to being a label rather than a
# bypass: a bare unknown fraction still fails.
RECALL_WITHDRAWN_LABEL = re.compile(
    r"NOT\s+REPRODUCIBLE|WITHDRAWN|SUPERSEDED|UNREPRODUCIBLE",
    re.IGNORECASE,
)

# Surfaces whose synthetic recall fractions are checked. Deliberately the
# published ones plus the benchmark writeups that feed them; the
# docs/improvement/ programme record is excluded because it quotes
# superseded figures ON PURPOSE, as the record of how they were corrected.
RECALL_CHECKED_FILES: list[str] = [
    "README.md",
    "docs/TRUST.md",
    "docs/MODEL_CARD.md",
    "benchmarks/README.md",
    "benchmarks/headtohead/RESULTS-synthetic-v2-2026-07-28.md",
    "site/index.html",
    "site/llms.txt",
    "site/llms-full.txt",
]


def load_recall_artefact() -> dict:
    if not RECALL_ARTEFACT_PATH.exists():
        raise SystemExit(
            "claim-auditor: benchmarks/synthetic/RECALL.json is missing. "
            "Run scripts/build_recall_artefact.py. Refusing to pass recall "
            "claims with no artefact to check them against.")
    return json.loads(RECALL_ARTEFACT_PATH.read_text(encoding="utf-8"))


def known_recall_fractions(artefact: dict) -> dict[str, list[str]]:
    """{"10/30": ["scanner/default high_risk"], ...}"""
    out: dict[str, list[str]] = {}
    for cond_id, cond in artefact.get("conditions", {}).items():
        for tier, stats in cond.get("tiers", {}).items():
            out.setdefault(stats["fraction"], []).append(f"{cond_id} {tier}")
    return out


def check_recall_claims(text: str, rel_path: str,
                        artefact: dict) -> list[tuple[int, str]]:
    """Published recall fractions that are unknown or unlabelled."""
    known = known_recall_fractions(artefact)
    denominators = {f.split("/")[1] for f in known}
    problems: list[tuple[int, str]] = []

    for start, _end, para in split_paragraphs(strip_noise(text, ".md")):
        if not RECALL_CONTEXT.search(para):
            continue
        for m in FRACTION_RE.finditer(para):
            num, den = m.group(1), m.group(2)
            if den not in denominators:
                continue           # not a synthetic-corpus recall fraction
            fraction = f"{num}/{den}"
            line = start + para.count("\n", 0, m.start())
            if fraction not in known:
                if RECALL_WITHDRAWN_LABEL.search(para):
                    continue      # kept as the record of a correction
                problems.append((
                    line,
                    f"recall {fraction} is not in RECALL.json. Known: "
                    f"{', '.join(sorted(known))}"))
                continue
            if not RECALL_PATH_LABEL.search(para):
                problems.append((
                    line,
                    f"recall {fraction} published without naming a path "
                    f"(scanner or classifier). It is {known[fraction][0]}."))
            elif not RECALL_GATE_LABEL.search(para):
                problems.append((
                    line,
                    f"recall {fraction} published without naming a gate "
                    f"condition. It is {known[fraction][0]}."))
    return problems


# Files verify_facts() cross-references against canonical counts, relative to
# the repo root. Module level so the coverage question ("which surfaces does
# this gate actually reach?") is answerable by reading one list, and so a
# test can extend it against a planted fixture.
#
# STILL NOT the full set of published surfaces, and the reason this list
# cannot be trusted to be complete is that it is maintained by hand.
#
# MEASURED 2026-07-28: docs/architecture.md ("1,223 tests") and
# docs/CONTINUITY.md ("2,600+ tests") both carried test-count claims while
# absent from this list, so neither was checked. Extending it was recorded
# as P0 and parked behind 1.5c on the principle that a gate's reach must
# not be widened before its sensitivity is repaired.
#
# 2026-07-31: the sensitivity defect was repaired (unit_patterns["tests"]
# now tolerates inline markup and dotted grouping), and the cost of the
# parking was then measured: docs/architecture.md had been publishing
# "1,223 tests" against a canonical of 2,619, short by 1,396. It is added
# below. docs/CONTINUITY.md is deliberately NOT added: "2,600+ tests" is an
# open-ended claim that remains true, and cascading a hard number into it
# would make a doc that needs no maintenance need it.
#
# The durable answer to "is this list complete?" is not a longer list. It is
# tests/test_cascade_count.py::TestEveryPublishedSurfaceCarriesTheCanonicalCount,
# which enumerates tracked .md/.html/.txt with `git ls-files` and never reads
# this list at all (measurement rule 4c: a completeness claim must come from
# enumeration).
# Entries are either a plain path (every fact in `canonical` is checked) or
# a (path, {fact_names}) pair naming the facts that surface actually
# publishes. The pair form exists so that widening reach cannot import false
# positives from documents that carry legitimately scoped counts; see
# docs/architecture.md below.
VERIFY_FACTS_FILES: list = [
    "README.md",
    # SECURITY.md carries the same numeric badges (test count etc.) and was
    # previously unchecked, so a stale "2,468 tests" line drifted undetected.
    "SECURITY.md",
    "docs/TRUST.md",
    "docs/MODEL_CARD.md",
    # Added 2026-07-31 after it was found 1,396 short. See the note above.
    #
    # SCOPED, and the scoping is not a suppression. This file is a directory
    # tree whose comments carry deliberate PER-MODULE counts:
    # `credential_check.py # Secret detection (18 patterns ...)` and
    # `gdpr_patterns.py # GDPR pattern definitions (14 patterns ...)`. Both
    # were verified correct on 2026-07-31 against the modules themselves
    # (len(credential_check.SECRET_PATTERNS) == 18,
    # len(gdpr_patterns.GDPR_PATTERNS) == 14). The file makes NO repo-wide
    # pattern claim, so the unscoped gate read "18 pattern" as a failed
    # attempt at the canonical 419 and reported two mismatches that were the
    # gate's error, not the document's. Listing the facts a surface actually
    # publishes is the fix; adding either number to .claim-allowlist would
    # have hidden a real defect class behind a real false positive.
    ("docs/architecture.md", {"tests"}),
    "site/index.html",
    "site/pricing.html",
    "site/about.html",
    "site/regions/uae.html",
    "site/regions/regulations.html",
    "site/locales/de.html",
    "site/locales/pt-br.html",
    # llms.txt / llms-full.txt are published AI-discovery surfaces and
    # carry the same numeric claims; they were previously unchecked, so
    # a stale test badge sat in llms-full.txt undetected.
    "site/llms.txt",
    "site/llms-full.txt",
]

STALE_CHECK_EXEMPTIONS: dict[tuple[str, str], dict] = {
    # (repo-relative path, canonical fact name) -> {"phrases": [...], "why": str}
    #
    # Empty, and it took work to keep it that way. MEASURED 2026-07-28:
    # removing the magnitude floor surfaced four suppressed matches. None
    # was a legitimate sub-count needing an exemption; all four were
    # pattern-precision defects the floor had been hiding - three instances
    # of `python3 tests/...` read as "3 tests", and one "963 test
    # functions" swept up by a singular unit. Both were fixed at the
    # pattern, which is the better repair: an exemption records that a
    # number means something else, it does not excuse a regex that cannot
    # tell a filename from a count.
    #
    # If an entry is ever added, it must say why in prose a reviewer can
    # disagree with, and the first question to ask is whether the pattern
    # should have matched at all.
}


def stale_number_verdict(fact_name: str, actual_val: int, found_val: int,
                         rel_path: str, matched_text: str,
                         exemptions: dict | None = None) -> tuple[bool, str]:
    """Should this published number be reported as stale? (flag, reason).

    Magnitude plays no part. A number either equals the canonical value,
    is explicitly exempted for a stated reason, or is flagged.
    """
    if found_val == actual_val:
        return False, "matches canonical"
    table = STALE_CHECK_EXEMPTIONS if exemptions is None else exemptions
    entry = table.get((rel_path, fact_name))
    if entry:
        normalised = " ".join(matched_text.split())
        for phrase in entry["phrases"]:
            if " ".join(phrase.split()) in normalised:
                return False, f"exempt: {entry['why']}"
    return True, f"{found_val} does not match canonical {actual_val}"


def verify_facts() -> int:
    """Cross-reference published numbers against canonical counts from site_facts.

    Regenerates site_facts.json, then scans key documents for numeric claims
    that should match canonical counts. Returns 1 if any mismatch found.
    """
    # Regenerate canonical facts
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        import site_facts as sf
        facts = sf.compute()
    except Exception as e:
        print(f"claim-auditor --verify-facts: cannot load site_facts: {e}",
              file=sys.stderr)
        return 2

    canonical = {
        "419": ("tier_regexes", facts["counts"]["patterns"]["tier_regexes"]),
        "62": ("commands", facts["counts"]["commands"]),
        "13": ("frameworks", facts["counts"]["frameworks"]),
        "8": ("languages", facts["counts"]["languages"]),
        # Derived, never hand-written. This key used to be the literal
        # "2354" with a comment claiming it was "kept in sync with the
        # current count for clarity"; it was not, and by 2026-07-31 it was
        # 265 out of date, so the one thing it promised was the one thing it
        # did not do. The key is only a human-readable hint (the check
        # compares the CURRENT value below), which is exactly why nothing
        # forced it to stay true.
        str(facts["counts"]["tests"]["total_collected"]): (
            "tests", facts["counts"]["tests"]["total_collected"]),
    }

    check_files = VERIFY_FACTS_FILES
    # Bare paths, for the checks below that are not fact-scoped. Kept as one
    # derivation so a scoped entry cannot reach a loop expecting a string,
    # which is exactly what broke when the tuple form was introduced.
    check_paths = [e[0] if isinstance(e, tuple) else e for e in check_files]

    mismatches: list[str] = []
    checked = 0

    for entry in check_files:
        if isinstance(entry, tuple):
            rel_path, only_facts = entry
        else:
            rel_path, only_facts = entry, None
        fpath = REPO_ROOT / rel_path
        if not fpath.exists():
            continue
        text = fpath.read_text(encoding="utf-8", errors="replace")

        for published_str, (fact_name, actual_val) in canonical.items():
            if only_facts is not None and fact_name not in only_facts:
                continue
            actual_str = str(actual_val)
            if published_str != actual_str:
                # The published number and the canonical number differ.
                # Check if the WRONG (published) number appears in the file.
                # This would mean a doc still uses a stale number.
                # Not relevant here since we check that the correct number
                # IS present and the wrong one is NOT.
                pass

            # Check that the canonical number appears in the file in the
            # expected context (near the fact name or unit word).
            # This catches cases where someone changes the code but not the docs.
            # We search for common patterns like "419 patterns", "62 commands",
            # "12 frameworks", "8 languages".
            # `(?<!\w)`, not `(?<!\d)`. A digit-final identifier is not a
            # count: `python3 tests/test_classification.py` was read as
            # "3 tests" and reported as a stale suite total on three
            # surfaces the moment the magnitude floor stopped hiding it
            # (MEASURED 2026-07-28).
            #
            # `tests` plural only, never `tests?`. "963 test functions" is a
            # different quantity - the legacy runner's function count - and
            # the singular form swept it up. This matches the shape list
            # scripts/cascade_count.py already uses for the same count, so
            # the two instruments agree on what a test-count claim looks
            # like.
            unit_patterns = {
                "tier_regexes": rf"(?<!\w){actual_str}\s*(?:pattern|regex|risk\s+pattern)",
                "commands": rf"(?<!\w){actual_str}\s+(?:commands?\b|CLI\s+commands?)",
                "frameworks": rf"(?<!\w){actual_str}\s+(?:compliance\s+)?frameworks?",
                "languages": rf"(?<!\w){actual_str}\s+(?:programming\s+)?languages?",
                # `_GAP`, not `\s*`. MEASURED 2026-07-31: site/index.html
                # published the count as `<strong ...>2,354</strong> tests`
                # and `</strong> ` is neither whitespace nor `%20`, so this
                # pattern could not see it and --verify-facts reported OK
                # while the landing page was 258 short. The dotted
                # alternative covers the de-DE and pt-BR locale pages, which
                # group thousands with a full stop.
                "tests": rf"(?<!\w)(?:{actual_str}|{int(actual_str):,}|{_dotted(int(actual_str))})(?:{_GAP}|%20)?(?:unique\s+)?(?:pytest-collected\s+)?(?:tests\b(?:\s+passing)?|passing|automated\s+tests\b)",
            }
            pat = unit_patterns.get(fact_name)
            if not pat:
                continue

            # NOTE: a near-identical block used to sit here, searching an
            # `actual_pat` variant and computing `found_val` — but it never
            # appended to `mismatches`, so its only reachable effect was to
            # raise ValueError when its `[\d,]+` sub-pattern matched a lone
            # comma (e.g. the text ", test counts") and `int("")` was called.
            # The block below performs the real check correctly. Removed
            # rather than patched: dead code that can only crash is not worth
            # keeping.

            # Check for the canonical number in context
            if not re.search(pat, text, re.IGNORECASE):
                # Canonical number not found in expected context — check if
                # a WRONG number is present instead
                # Safely construct wrong_pat by replacing {actual_str} and {int(actual_str):,} with a generic number matcher
                wrong_pat = pat.replace(actual_str, r"\d+(?:,\d+)*")
                if f"{int(actual_str):,}" != actual_str:
                    wrong_pat = wrong_pat.replace(f"{int(actual_str):,}", r"\d+(?:,\d+)*")
                wrong_matches = list(re.finditer(wrong_pat, text, re.IGNORECASE))
                for wm in wrong_matches:
                    # Capture the WHOLE number including thousands separators.
                    # A bare \d+ stops at the comma, so "2,778" was read as
                    # "2" — which then fell under the 50%% floor below and was
                    # silently skipped. That single bug let every comma-
                    # formatted stale count ("2,778 tests") pass unflagged
                    # across README, TRUST.md, MODEL_CARD and the site pages.
                    # Strip separators before int().
                    found_num = re.search(r"\d[\d,]*\d|\d", wm.group(0))
                    if found_num and found_num.group(0).replace(",", "") != actual_str:
                        found_val = int(found_num.group(0).replace(",", ""))
                        flag, _why = stale_number_verdict(
                            fact_name=fact_name,
                            actual_val=int(actual_str),
                            found_val=found_val,
                            rel_path=rel_path,
                            matched_text=wm.group(0),
                        )
                        if not flag:
                            continue
                        line_num = text[:wm.start()].count("\n") + 1
                        mismatches.append(
                            f"  {rel_path}:L{line_num} — "
                            f"{fact_name}: found {found_num.group(0)}, "
                            f"expected {actual_str} "
                            f"(context: {wm.group(0)[:60]!r})"
                        )
            checked += 1

    # Also check for the known-bad number 780 in pattern context
    for rel_path in check_paths:
        fpath = REPO_ROOT / rel_path
        if not fpath.exists():
            continue
        text = fpath.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"\b780\b.*?pattern", text, re.IGNORECASE):
            line_num = text[:m.start()].count("\n") + 1
            mismatches.append(
                f"  {rel_path}:L{line_num} — "
                f"PROHIBITED: '780' in pattern context "
                f"(context: {m.group(0)[:60]!r})"
            )

    # Precision-figure enforcement (T3c): every "<N>% ...precision" claim in
    # published copy must be derivable from the benchmark artifacts.
    known = known_precision_values()
    precision_files = list(dict.fromkeys(check_paths + PRECISION_EXTRA_FILES))
    if not known:
        print("claim-auditor --verify-facts: WARNING — benchmark artifacts "
              "not found, precision claims not checked", file=sys.stderr)
    else:
        for rel_path in precision_files:
            fpath = REPO_ROOT / rel_path
            if not fpath.exists():
                continue
            text = fpath.read_text(encoding="utf-8", errors="replace")
            for line_num, claim in check_precision_claims(text, known):
                mismatches.append(
                    f"  {rel_path}:L{line_num} — "
                    f"precision figure {claim!r} does not match any value "
                    f"derivable from benchmarks/ data"
                )
            checked += 1

    # Recall-figure enforcement (F24): every published synthetic-corpus
    # recall fraction must exist in benchmarks/synthetic/RECALL.json and
    # must name the path and gate condition it was measured under.
    recall_artefact = load_recall_artefact()
    for rel_path in RECALL_CHECKED_FILES:
        fpath = REPO_ROOT / rel_path
        if not fpath.exists():
            continue
        text = fpath.read_text(encoding="utf-8", errors="replace")
        for line_num, problem in check_recall_claims(text, rel_path,
                                                     recall_artefact):
            mismatches.append(f"  {rel_path}:L{line_num} — {problem}")
        checked += 1

    # Banned-claim sweep: every HTML page under site/ (the purged
    # "zero false positives" claim must not return anywhere published).
    for fpath in sorted((REPO_ROOT / "site").rglob("*.html")):
        text = fpath.read_text(encoding="utf-8", errors="replace")
        for m in _BANNED_CLAIM_RE.finditer(text):
            line_num = text[:m.start()].count("\n") + 1
            mismatches.append(
                f"  {fpath.relative_to(REPO_ROOT)}:L{line_num} — "
                f"BANNED CLAIM {m.group(0)!r}: disproven by the July 2026 "
                f"audit; do not republish"
            )
        checked += 1

    print(f"claim-auditor --verify-facts: checked {checked} fact references "
          f"across {len(precision_files)} files")

    if mismatches:
        print(f"\n  FAIL — {len(mismatches)} mismatch(es):\n")
        for m in mismatches:
            print(m)
        return 1
    else:
        print("  all published numbers match canonical counts — OK")
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("files", nargs="*", type=Path,
                   help="explicit file paths to scan")
    p.add_argument("--staged", action="store_true",
                   help="scan files currently staged in git")
    p.add_argument("--diff-base", metavar="REF",
                   help="scan files changed vs REF (e.g. origin/main)")
    p.add_argument("--backtest", type=int, metavar="N",
                   help="run auditor against files in last N commits")
    p.add_argument("--verify-facts", action="store_true",
                   help="cross-reference published numbers against "
                        "canonical counts from site_facts.py")
    p.add_argument("--format", choices=("text", "json"), default="text")
    args = p.parse_args(argv)

    allowlist = load_allowlist()

    if args.verify_facts:
        return verify_facts()

    if args.backtest is not None:
        return backtest(args.backtest, allowlist)

    targets: list[Path] = []
    if args.staged:
        targets = files_staged()
    elif args.diff_base:
        targets = files_diff_base(args.diff_base)
    elif args.files:
        targets = [Path(f) for f in args.files]
    else:
        print("claim-auditor: no input (use FILE, --staged, --diff-base, "
              "--verify-facts, or --backtest)", file=sys.stderr)
        return 2

    reports = [scan_file(t, allowlist) for t in targets]
    scanned_reports = [r for r in reports if r.scanned]

    if args.format == "json":
        print(json_report(scanned_reports))
    else:
        print(human_report(scanned_reports))

    has_findings = any(r.findings for r in scanned_reports)
    return 1 if has_findings else 0


if __name__ == "__main__":
    from tree_guard import stamp
    stamp()
    sys.exit(main())
