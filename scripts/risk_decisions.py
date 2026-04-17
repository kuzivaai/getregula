# regula-ignore
"""Risk decision annotation parser for regula-ignore / regula-accept.

Parses inline source code annotations that document risk treatment decisions:

- ``# regula-ignore`` — false positive suppression (finding is silenced)
- ``# regula-accept`` — documented risk acceptance per ISO 42001 Clause 6.1.3
  (finding moves to the "accepted" bucket with mandatory owner + review date)

Standards alignment:
  ISO 42001 Clause 6.1.3  — risk treatment decisions
  ISO 42001 Clause 8.2    — periodic review of accepted risks
  NIST AI RMF MANAGE 2.1  — risk response documentation
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

# ── Patterns ───────────────────────────────────────────────────────

_IGNORE_RE = re.compile(
    r"#\s*regula-ignore\s*(?::\s*(?P<pattern>[^—\-\n]+?))?\s*"
    r"(?:(?:—|--)\s*(?P<rationale>.+?))?\s*$"
)

_ACCEPT_RE = re.compile(
    r"#\s*regula-accept\s*:\s*(?P<pattern>[^—\-\n]+?)\s*"
    r"(?:(?:—|--)\s*(?P<rest>.+?))?\s*$"
)

_OWNER_RE = re.compile(r"\|\s*owner\s*=\s*(?P<owner>\S+)")
_REVIEW_RE = re.compile(r"\|\s*review\s*=\s*(?P<review>\d{4}-\d{2}-\d{2})")


# ── Data model ─────────────────────────────────────────────────────

@dataclass
class RiskDecision:
    """A single parsed risk-treatment annotation."""

    dtype: str                           # "ignore" | "accept"
    file: str                            # filepath
    line: int                            # 1-based line number
    pattern: str                         # pattern name or "*"
    rationale: Optional[str] = None
    owner: Optional[str] = None
    review_date: Optional[str] = None    # ISO 8601 YYYY-MM-DD
    raw: str = ""                        # original line text
    warning: Optional[str] = None
    error: Optional[str] = None

    # -- helpers --------------------------------------------------------

    def is_overdue(self) -> bool:
        """True if review_date is in the past."""
        if not self.review_date:
            return False
        try:
            return date.fromisoformat(self.review_date) < date.today()
        except ValueError:
            return False

    def is_valid_accept(self) -> bool:
        """True if this is a well-formed accept with no error."""
        return self.dtype == "accept" and self.error is None

    def to_dict(self) -> dict:
        """JSON-serialisable dictionary."""
        return asdict(self)


# ── Parsing ────────────────────────────────────────────────────────

def _parse_ignore(line_text: str, filepath: str, lineno: int) -> Optional[RiskDecision]:
    """Parse a ``# regula-ignore`` annotation."""
    m = _IGNORE_RE.search(line_text)
    if m is None:
        return None

    pattern = (m.group("pattern") or "").strip() or "*"
    rationale_raw = (m.group("rationale") or "").strip() or None

    warning = None
    if rationale_raw is None:
        warning = "No rationale provided for regula-ignore suppression"

    return RiskDecision(
        dtype="ignore",
        file=filepath,
        line=lineno,
        pattern=pattern,
        rationale=rationale_raw,
        raw=line_text,
        warning=warning,
    )


def _parse_accept(line_text: str, filepath: str, lineno: int) -> Optional[RiskDecision]:
    """Parse a ``# regula-accept`` annotation."""
    m = _ACCEPT_RE.search(line_text)
    if m is None:
        return None

    pattern = (m.group("pattern") or "").strip()
    rest = (m.group("rest") or "").strip()

    # Extract rationale (everything before first pipe)
    rationale = None
    if rest:
        rationale_part = rest.split("|")[0].strip()
        if rationale_part:
            rationale = rationale_part

    # Extract owner and review fields
    owner_m = _OWNER_RE.search(rest)
    review_m = _REVIEW_RE.search(rest)
    owner = owner_m.group("owner") if owner_m else None
    review_date = review_m.group("review") if review_m else None

    # Validate required fields
    missing = []
    if rationale is None:
        missing.append("rationale")
    if owner is None:
        missing.append("owner")
    if review_date is None:
        missing.append("review")

    error = None
    if missing:
        error = f"regula-accept missing required field(s): {', '.join(missing)}"

    return RiskDecision(
        dtype="accept",
        file=filepath,
        line=lineno,
        pattern=pattern,
        rationale=rationale,
        owner=owner,
        review_date=review_date,
        raw=line_text,
        error=error,
    )


def parse_annotations(lines: list[str], filepath: str) -> list[RiskDecision]:
    """Parse all regula-ignore and regula-accept annotations from source lines.

    Args:
        lines: Source file lines (no trailing newlines required).
        filepath: Path string attached to each decision for traceability.

    Returns:
        List of RiskDecision objects, one per annotation found.
    """
    decisions: list[RiskDecision] = []
    for idx, line in enumerate(lines):
        lineno = idx + 1  # 1-based
        if "regula-accept" in line:
            d = _parse_accept(line, filepath, lineno)
            if d is not None:
                decisions.append(d)
        elif "regula-ignore" in line:
            d = _parse_ignore(line, filepath, lineno)
            if d is not None:
                decisions.append(d)
    return decisions


# ── Suppression set builder ────────────────────────────────────────

def build_suppression_set(decisions: list[RiskDecision]) -> set[str]:
    """Build the set of pattern names that should be suppressed.

    Same interface as the old ``_parse_suppression_rules`` in report.py:
    returns a set of lowercase pattern strings.

    Rules:
    - ``regula-ignore`` always suppresses (with or without rationale).
    - ``regula-accept`` suppresses ONLY when all required fields are present
      (i.e. ``is_valid_accept()`` is True). Invalid accepts leave the
      finding active so it remains visible in scan results.
    """
    suppressed: set[str] = set()
    for d in decisions:
        if d.dtype == "ignore":
            suppressed.add(d.pattern.lower())
        elif d.dtype == "accept" and d.is_valid_accept():
            suppressed.add(d.pattern.lower())
    return suppressed


# ── Feedback recording (local-only) ──────────────────────────────

_FEEDBACK_FILE = ".regula/feedback.json"


def record_feedback(
    kind: str,
    pattern: str,
    file: str,
    line: int,
    confidence: int = 0,
    tier: str = "",
    rationale: str = "",
) -> None:
    """Record a feedback event to ~/.regula/feedback.json.

    This is the local-only feedback loop. Users own their data.
    No network calls. Data stays on disk.
    """
    try:
        fb_path = Path.home() / _FEEDBACK_FILE
        fb_path.parent.mkdir(parents=True, exist_ok=True)

        new_record = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "kind": kind,
            "pattern": pattern,
            "file": file,
            "line": line,
            "confidence": confidence,
            "tier": tier,
            "rationale": rationale,
        }

        # File-locked write to prevent race conditions with concurrent scans
        try:
            import fcntl
            with open(fb_path, "a+") as fh:
                fcntl.flock(fh, fcntl.LOCK_EX)
                fh.seek(0)
                raw = fh.read()
                records = json.loads(raw) if raw.strip() else []
                if not isinstance(records, list):
                    records = []
                records.append(new_record)
                fh.seek(0)
                fh.truncate()
                fh.write(json.dumps(records, indent=2))
                fcntl.flock(fh, fcntl.LOCK_UN)
        except ImportError:
            # fcntl not available (Windows) — fall back to unlocked write
            records = []
            if fb_path.exists():
                try:
                    records = json.loads(fb_path.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, ValueError):
                    records = []
            records.append(new_record)
            fb_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    except Exception:
        pass  # feedback recording is best-effort


def load_feedback() -> list[dict]:
    """Load all feedback records from ~/.regula/feedback.json.

    Returns an empty list if the file does not exist or is unreadable.
    """
    try:
        fb_path = Path.home() / _FEEDBACK_FILE
        if not fb_path.exists():
            return []
        return json.loads(fb_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError, OSError):
        return []
