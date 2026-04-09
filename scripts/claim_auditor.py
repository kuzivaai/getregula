#!/usr/bin/env python3
# regula-ignore
"""Claim Auditor — block commits that introduce unverified factual claims.

Scans Markdown, HTML, and landing-page files for:
  - Numeric claims (percentages, counts, fines, stars, users, benchmarks)
  - Currency amounts
  - Superlatives and competitive assertions ("only", "first", "best", "most")
  - Attributed quotes ("X said", "according to Y")

For each claim it checks whether a verifiable source is present in the same
paragraph: a URL, markdown link, HTML anchor, or reference to a file that
exists in the repository (e.g. `benchmarks/results/PRECISION.json`,
`tests/test_classification.py`). Claims without a nearby source are flagged.

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
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
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
    \s*                                         # optional space
    (?:""" + _NUMERIC_UNITS + r""")             # unit
    \b
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
# Ranges that should suppress numeric claim matches entirely
STRUCTURAL_REFS = [ARTICLE_REF, ANNEX_REF, RECITAL_REF, CATEGORY_REF, CHAPTER_REF]
LINE_REF = re.compile(r":\d+(?::\d+)?\b")
SECTION_REF = re.compile(r"^\s*#{1,6}\s")

# Source indicators — presence of any of these within the same paragraph
# exempts the paragraph's claims.
URL_RE = re.compile(r"https?://[^\s)>\]}\"']+")
MD_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
HTML_LINK_RE = re.compile(r"<a\s+[^>]*href\s*=", re.IGNORECASE)
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
    """Remove code fences, inline code, HTML script/style, HTML comments.

    Preserves newline counts so line numbers continue to map to the
    original file — each stripped region is replaced with the same number
    of newlines it originally contained.
    """
    def _blank(m: re.Match[str]) -> str:
        return "\n" * m.group(0).count("\n")

    text = re.sub(r"<!--.*?-->", _blank, text, flags=re.DOTALL)
    text = re.sub(r"<script[^>]*>.*?</script>", _blank, text,
                  flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", _blank, text,
                  flags=re.DOTALL | re.IGNORECASE)
    if suffix in (".md", ".markdown"):
        text = re.sub(r"```.*?```", _blank, text, flags=re.DOTALL)
        text = re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), text)
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

def paragraph_has_source(paragraph: str) -> tuple[bool, str]:
    """Return (has_source, reason_if_not)."""
    if URL_RE.search(paragraph):
        return True, "url"
    if MD_LINK_RE.search(paragraph):
        return True, "md-link"
    if HTML_LINK_RE.search(paragraph):
        return True, "html-link"
    if CITATION_WORDS.search(paragraph):
        return True, "citation-word"
    if VERIFICATION_LABEL.search(paragraph):
        return True, "verification-label"
    # File references — must resolve on disk
    for m in FILE_REF_RE.finditer(paragraph):
        candidate = REPO_ROOT / m.group(1)
        if candidate.exists():
            return True, f"file-ref:{m.group(1)}"
    return False, "no-source"


# ---------------------------------------------------------------------------
# Scan a single file
# ---------------------------------------------------------------------------

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

    def match_line(para_text: str, offset: int, para_start_line: int) -> int:
        """Return 1-based file line for a regex match inside a paragraph."""
        return para_start_line + para_text.count("\n", 0, offset)

    for start, end, para in paragraphs:
        has_src, src_reason = paragraph_has_source(para)
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

        def _in_blocked(pos: int) -> bool:
            return any(lo <= pos < hi for lo, hi in blocked_ranges)

        def _add(kind: str, m: re.Match[str]) -> None:
            snippet = m.group(0).strip()
            if kind == "numeric" and is_exempt_number(snippet):
                return
            if kind in ("numeric", "currency") and _in_blocked(m.start()):
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
            report.findings.append(Finding(
                claim=claim, reason=src_reason,
            ))
    return report


# ---------------------------------------------------------------------------
# Input selection
# ---------------------------------------------------------------------------

def git(*args: str) -> str:
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
    p.add_argument("--format", choices=("text", "json"), default="text")
    args = p.parse_args(argv)

    allowlist = load_allowlist()

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
              "or --backtest)", file=sys.stderr)
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
    sys.exit(main())
