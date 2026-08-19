"""Fail-closed classification for files carrying the published test count."""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# A whole file whose count literal was true when the file was frozen. Keyed on
# an immutable blob hash, because the file must never change again.
DATED_EVIDENCE = "dated_evidence"

# A single OCCURRENCE inside a LIVE file that is not a claim about the test
# count at all: a hex colour, an OID arc, a byte size, a port. Keyed on the
# surrounding text rather than a blob hash, because the file keeps changing.
#
# THE DISPOSITION N109 AND N111 SAID WAS OWED. Four collisions in two weeks
# (a `#dcNNNN` hex colour, a `cli:NNNNfb52...` stable_id, the PKCS#7 RSADSI
# arc, and a sub-1000 count no candidate scanner could nominate) were each
# resolved by widening a lookaround in `count_pattern`. That works, and those
# lookarounds are correct, but it does not scale and it is the wrong shape:
#
#   - Every widening is GLOBAL. Excluding a hex colour in one file narrows the
#     guard in every file, for every value, forever.
#   - It can only express LEXICAL facts. "This integer is a byte size" or
#     "this is a port number" has no lexical signature to exclude on.
#   - The reason lives in a docstring beside the regex, detached from the
#     occurrence it explains, and drifts the way N111 records a copy drifting.
#
# So a fifth collision is now a data entry with a re-measured premise instead
# of a fifth regex. Two properties make it a disposition rather than a bypass,
# both enforced in classify_count_occurrences:
#
#   1. Declaring a file does NOT exempt the file. EVERY occurrence must be
#      covered by a declared context; one uncovered hit and the file is still
#      a violation. This is the objection N70 raised against broad path
#      exclusions, answered directly.
#   2. A record that matches nothing FAILS. A stale exclusion is an exclusion
#      whose premise has gone, and leaving it is how the guard quietly stops
#      guarding. Same discipline as the quarantine's burn-down re-measurement.
NOT_A_COUNT_CLAIM = "not_a_count_claim"

ALLOWED_RECORD_CLASSES = {DATED_EVIDENCE}
ALLOWED_EXCLUSION_CLASSES = {NOT_A_COUNT_CLAIM}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# A context_regex is matched against the hit's OWN LINE, and nothing else.
#
# The first attempt used a symmetric character window either side of the hit.
# It was wrong in a way the fixtures caught immediately: in a short file every
# line is inside every other line's window, so one declared timeout constant
# vouched for a genuine published claim two lines below it. A window has no
# principled width, and any width is too wide for a small file.
#
# The line is a real boundary and it fits every collision seen so far: a hex
# colour, an OID arc, a stable_id, a byte size and a timeout constant all sit
# on the same line as the digits they explain. A context that needs more than
# a line is not describing the token; it is describing the file, which is the
# broad exclusion this whole registry refuses.
CONTEXT_SCOPE = "line"


def discover_tracked_files(repo: Path) -> list[Path]:
    """Return tracked paths; incomplete Git discovery is always an error."""
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=repo, capture_output=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(
            f"git ls-files failed with exit {result.returncode}: {detail}")
    return [Path(part.decode("utf-8", errors="strict"))
            for part in result.stdout.split(b"\0") if part]


def read_tracked_files(repo: Path, paths: list[Path]) -> dict[str, bytes]:
    """Read every tracked regular file; a read failure cannot disappear."""
    files: dict[str, bytes] = {}
    for path in paths:
        absolute = repo / path
        try:
            files[path.as_posix()] = absolute.read_bytes()
        except OSError as exc:
            raise RuntimeError(f"cannot read tracked file {path}: {exc}") from exc
    return files


def _raw(value: str | bytes) -> bytes:
    return value if isinstance(value, bytes) else value.encode("utf-8")


def verify_record_provenance(repo: Path, record: dict) -> None:
    """Prove the declared commit contains the exact registered file blob."""
    commit = record["evidence_commit"]
    path = record["path"]
    exists = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=repo,
        capture_output=True, check=False)
    if exists.returncode != 0:
        raise ValueError(f"evidence commit does not exist for {path}: {commit}")
    blob = subprocess.run(
        ["git", "show", f"{commit}:{path}"], cwd=repo,
        capture_output=True, check=False)
    if blob.returncode != 0:
        raise ValueError(f"path missing at evidence commit: {path}")
    historical_hash = hashlib.sha256(blob.stdout).hexdigest()
    if historical_hash != record["immutable_sha256"]:
        raise ValueError(f"evidence-commit blob hash mismatch for {path}")


def validate_record_policy(policy: dict, files: dict[str, str | bytes],
                           current_paths: set[str],
                           non_surface_paths: set[str],
                           repo: Path | None = None) -> dict[str, dict]:
    """Validate centrally assigned historical classes and return by path."""
    if "excluded_by_design" in policy:
        raise ValueError("broad exclusion is forbidden; classify exact records")
    if policy.get("schema_version") != 1:
        raise ValueError("record policy schema_version must be 1")
    records = policy.get("records")
    if not isinstance(records, list):
        raise ValueError("record policy records must be a list")
    by_path: dict[str, dict] = {}
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("record policy entry must be an object")
        path = record.get("path")
        if not isinstance(path, str) or not path or path.endswith("/"):
            raise ValueError("record path must name one exact file")
        if path in by_path:
            raise ValueError(f"duplicate record classification: {path}")
        if path in current_paths:
            raise ValueError(f"current surface cannot be historical: {path}")
        if path in non_surface_paths:
            raise ValueError(f"generated/source carrier cannot be historical: {path}")
        if path not in files:
            raise ValueError(f"historical record points to missing tracked file: {path}")
        if record.get("record_class") not in ALLOWED_RECORD_CLASSES:
            raise ValueError(f"invalid historical record class for {path}")
        if not DATE_RE.fullmatch(str(record.get("recorded_at", ""))):
            raise ValueError(f"recorded_at must be an ISO date for {path}")
        if record["recorded_at"] not in path:
            raise ValueError(f"dated evidence path must contain recorded_at: {path}")
        if not COMMIT_RE.fullmatch(str(record.get("evidence_commit", ""))):
            raise ValueError(f"evidence_commit must be a full commit for {path}")
        if not SHA256_RE.fullmatch(str(record.get("immutable_sha256", ""))):
            raise ValueError(f"immutable_sha256 must be lowercase SHA-256 for {path}")
        if not str(record.get("rationale", "")).strip():
            raise ValueError(f"rationale is required for {path}")
        actual = hashlib.sha256(_raw(files[path])).hexdigest()
        if actual != record["immutable_sha256"]:
            raise ValueError(
                f"historical record content changed without reclassification: {path}")
        if repo is not None:
            verify_record_provenance(repo, record)
        by_path[path] = record
    return by_path


def count_pattern(count: int) -> re.Pattern:
    grouped = f"{count:,}"
    variants = {str(count), grouped, grouped.replace(",", ".")}
    # (?<!\w) and (?!\w), not (?<!\d)/(?!\d): a digit run embedded in a
    # longer alphanumeric token (hex colour, hash, stable_id) is not a claim
    # rendering. The leading side was fixed for `#dcNNNN` (2026-07-31); the
    # trailing side for a stable_id of the form `cli:NNNNfb52...` where the
    # canonical count landed at the start of a hex run (2026-08-07).
    #
    # (?<!\d\.) and (?!\.\d) exclude a dotted numeric run. The European
    # rendering uses a full stop as the thousands separator, so MEASURED
    # 2026-08-15: at one canonical value the dot variant matched inside the
    # PKCS#7 OIDs in scripts/timestamp.py, on the RSADSI arc. Those are not
    # claims, and text-replacing them to cascade a count would break RFC 3161
    # timestamping outright, which is measurement rule 4d's exact hazard. A
    # standalone dot-grouped rendering in prose still matches, because the
    # DE and PT-BR pages publish the count that way; only a component sitting
    # inside a longer dotted sequence is excluded. The colliding value is
    # deliberately not written here, for the reason this whole check exists
    # (N111).
    return re.compile(
        r"(?<!\w)(?<!\d\.)(" + "|".join(re.escape(v) for v in sorted(variants))
        + r")(?!\w)(?!\.\d)")


def validate_exclusion_policy(policy: dict, files: dict[str, str | bytes],
                              current_paths: set[str],
                              non_surface_paths: set[str] | None = None,
                              ) -> dict[str, list[dict]]:
    """Validate per-occurrence `not_a_count_claim` records, grouped by path.

    Deliberately NOT keyed on a blob hash: these live in files that keep
    changing, so a hash would fail on every unrelated edit and be deleted for
    noise. The premise is re-measured instead, in classify_count_occurrences.
    """
    excluded: dict[str, list[dict]] = {}
    for record in policy.get("occurrence_exclusions", []):
        if not isinstance(record, dict):
            raise ValueError("occurrence exclusion entry must be an object")
        path = record.get("path")
        if not isinstance(path, str) or not path or path.endswith("/"):
            raise ValueError("exclusion path must name one exact file")
        if record.get("record_class") not in ALLOWED_EXCLUSION_CLASSES:
            raise ValueError(f"invalid exclusion class for {path}")
        if path in current_paths:
            raise ValueError(
                f"a current surface publishes the count and cannot also "
                f"declare it not a claim: {path}")
        if path in (non_surface_paths or set()):
            raise ValueError(
                f"already skipped as a non-surface, so this exclusion could "
                f"never match and would be stale from birth: {path}")
        if path not in files:
            raise ValueError(f"exclusion points to missing tracked file: {path}")
        context = record.get("context_regex")
        if not isinstance(context, str) or not context.strip():
            raise ValueError(f"context_regex is required for {path}")
        try:
            compiled = re.compile(context)
        except re.error as exc:
            raise ValueError(f"invalid context_regex for {path}: {exc}") from exc
        # A context that matches everything excludes everything, which is the
        # broad exclusion `validate_record_policy` already refuses by name.
        if compiled.search("") is not None:
            raise ValueError(
                f"context_regex for {path} matches the empty string, so it "
                f"would vouch for every occurrence in the file")
        if not str(record.get("rationale", "")).strip():
            raise ValueError(f"rationale is required for {path}")
        if not str(record.get("finding", "")).strip():
            raise ValueError(
                f"finding is required for {path}: an exclusion with no ledger "
                f"row is a decision nobody can audit")
        excluded.setdefault(path, []).append(
            {**record, "_compiled": compiled})
    return excluded


def classify_count_occurrences(count: int, files: dict[str, str | bytes],
                               current_paths: set[str],
                               non_surface_paths: set[str],
                               policy: dict, repo: Path | None = None) -> list[str]:
    """Return files whose count literal lacks an authorised record class."""
    historical = validate_record_policy(
        policy, files, current_paths, non_surface_paths, repo)
    exclusions = validate_exclusion_policy(
        policy, files, current_paths, non_surface_paths)
    pattern = count_pattern(count)
    structural_json_key = re.compile(
        r'"(line|line_number|start_line|end_line|lineno|offset|column|'
        r'total_lines|loc|size|bytes)"\s*:\s*$')
    violations: list[str] = []
    matched_exclusions: set[int] = set()
    for path, raw_body in files.items():
        if path in current_paths or path in non_surface_paths or path in historical:
            continue
        raw_body = _raw(raw_body)
        if b"\0" in raw_body:
            continue
        try:
            body = raw_body.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            continue
        hits = [match for match in pattern.finditer(body)
                if not structural_json_key.search(body[:match.start()])]
        declared = exclusions.get(path, [])
        if hits and declared:
            # Per-OCCURRENCE, not per-file. A file that declares its hex
            # colours stays fully audited for everything else in it, so one
            # genuine claim among a hundred excluded tokens is still caught.
            uncovered = []
            for match in hits:
                line_start = body.rfind("\n", 0, match.start()) + 1
                line_end = body.find("\n", match.end())
                line = body[line_start:
                            line_end if line_end != -1 else len(body)]
                covering = [i for i, rec in enumerate(declared)
                            if rec["_compiled"].search(line)]
                if covering:
                    matched_exclusions.update(id(declared[i]) for i in covering)
                else:
                    uncovered.append(match)
            hits = uncovered
        if hits:
            violations.append(path)

    # A record that covered nothing is stale: either the token it described is
    # gone, or the canonical count moved and it no longer collides. Reporting
    # it keeps the registry the size of the real problem, the same reason the
    # quarantine re-measures its burn-downs rather than trusting them.
    for path, records in sorted(exclusions.items()):
        for record in records:
            if id(record) not in matched_exclusions:
                violations.append(
                    f"{path} [stale exclusion: context_regex "
                    f"{record['context_regex']!r} matched no occurrence]")
    return sorted(violations)
