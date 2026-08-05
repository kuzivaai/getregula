"""Fail-closed classification for files carrying the published test count."""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

ALLOWED_RECORD_CLASSES = {"dated_evidence", "historical_quote"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


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


def validate_record_policy(policy: dict, files: dict[str, str],
                           current_paths: set[str],
                           non_surface_paths: set[str]) -> dict[str, dict]:
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
        if not COMMIT_RE.fullmatch(str(record.get("evidence_commit", ""))):
            raise ValueError(f"evidence_commit must be a full commit for {path}")
        if not SHA256_RE.fullmatch(str(record.get("immutable_sha256", ""))):
            raise ValueError(f"immutable_sha256 must be lowercase SHA-256 for {path}")
        if not str(record.get("rationale", "")).strip():
            raise ValueError(f"rationale is required for {path}")
        actual = hashlib.sha256(files[path].encode("utf-8")).hexdigest()
        if actual != record["immutable_sha256"]:
            raise ValueError(
                f"historical record content changed without reclassification: {path}")
        by_path[path] = record
    return by_path


def count_pattern(count: int) -> re.Pattern:
    grouped = f"{count:,}"
    variants = {str(count), grouped, grouped.replace(",", ".")}
    return re.compile(
        r"(?<!\w)(" + "|".join(re.escape(v) for v in sorted(variants))
        + r")(?!\d)")


def classify_count_occurrences(count: int, files: dict[str, str],
                               current_paths: set[str],
                               non_surface_paths: set[str],
                               policy: dict) -> list[str]:
    """Return files whose count literal lacks an authorised record class."""
    historical = validate_record_policy(
        policy, files, current_paths, non_surface_paths)
    pattern = count_pattern(count)
    structural_json_key = re.compile(
        r'"(line|line_number|start_line|end_line|lineno|offset|column|'
        r'total_lines|loc|size|bytes)"\s*:\s*$')
    violations: list[str] = []
    for path, body in files.items():
        if path in current_paths or path in non_surface_paths or path in historical:
            continue
        hits = [match for match in pattern.finditer(body)
                if not structural_json_key.search(body[:match.start()])]
        if hits:
            violations.append(path)
    return sorted(violations)
