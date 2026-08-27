#!/usr/bin/env python3
"""Safely acquire and scan Regula's pinned external diagnostic corpus.

Target repositories are untrusted data. This runner never executes their code
and deliberately stores no source excerpts in its result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO_ROOT / "benchmarks" / "external" / "manifest.v1.json"
_GITHUB_URL = re.compile(
    r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)\.git"
)
_SAFE_ID = re.compile(r"[a-z0-9][a-z0-9-]{0,79}")
_COMMIT = re.compile(r"[0-9a-f]{40}")
_LICENCE = re.compile(r"[A-Za-z0-9][A-Za-z0-9.+-]{1,79}")
_ALLOWED_DOMAINS = {
    "employment", "medical", "finance", "biometrics", "education",
    "law_enforcement", "infrastructure", "migration",
}
_EXPECTATION_KINDS = {"no_detector_classes", "any_detector_class"}


class CorpusError(RuntimeError):
    """A manifest, acquisition or scan failed closed."""


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_sha256(value) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return _sha256_bytes(encoded)


def _files_sha256(paths: list[Path]) -> str:
    """Hash file names and bytes so an uncommitted evaluator is identifiable."""
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: str(item)):
        digest.update(str(path.relative_to(REPO_ROOT)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def validate_manifest(payload: dict) -> list[str]:
    """Return every validation error; do not stop after the first one."""
    errors: list[str] = []
    if payload.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if payload.get("status") != "preregistered_diagnostic":
        errors.append("status must be preregistered_diagnostic")
    config = payload.get("scan_configuration") or {}
    if config.get("target_code_execution") is not False:
        errors.append("target_code_execution must be false")
    if config.get("clean_repetitions") != 2:
        errors.append("clean_repetitions must be exactly 2")
    repositories = payload.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        return errors + ["repositories must be a non-empty list"]
    seen: set[str] = set()
    for index, entry in enumerate(repositories):
        prefix = f"repositories[{index}]"
        repo_id = entry.get("id", "")
        if not isinstance(repo_id, str) or not _SAFE_ID.fullmatch(repo_id):
            errors.append(f"{prefix}.id is not a safe stable id")
        elif repo_id in seen:
            errors.append(f"{prefix}.id is duplicated")
        seen.add(repo_id)
        url = entry.get("url", "")
        match = _GITHUB_URL.fullmatch(url) if isinstance(url, str) else None
        if not match:
            errors.append(f"{prefix}.url must be an exact public GitHub clone URL")
        elif entry.get("repository") != f"{match.group(1)}/{match.group(2)}":
            errors.append(f"{prefix}.repository must match url")
        commit = entry.get("commit", "")
        if not isinstance(commit, str) or not _COMMIT.fullmatch(commit):
            errors.append(f"{prefix}.commit must be a lowercase 40-character SHA")
        licence = entry.get("license_spdx", "")
        if (not isinstance(licence, str) or licence in {"", "NOASSERTION", "NONE"}
                or not _LICENCE.fullmatch(licence)):
            errors.append(f"{prefix}.license_spdx must be declared")
        variants = entry.get("variants")
        if not isinstance(variants, list) or not variants:
            errors.append(f"{prefix}.variants must be a non-empty list")
            continue
        variant_ids: set[str] = set()
        for variant in variants:
            variant_id = variant.get("id", "")
            if not isinstance(variant_id, str) or not _SAFE_ID.fullmatch(variant_id):
                errors.append(f"{prefix}.variant id is not safe")
            elif variant_id in variant_ids:
                errors.append(f"{prefix}.variant id {variant_id!r} is duplicated")
            variant_ids.add(variant_id)
            domains = variant.get("domains", [])
            if not isinstance(domains, list) or any(
                    domain not in _ALLOWED_DOMAINS for domain in domains):
                errors.append(f"{prefix}.{variant_id}.domains contains an invalid value")
            expectations = variant.get("expectations", [])
            if not isinstance(expectations, list):
                errors.append(f"{prefix}.{variant_id}.expectations must be a list")
                continue
            for expectation in expectations:
                if expectation.get("kind") not in _EXPECTATION_KINDS:
                    errors.append(f"{prefix}.{variant_id} has an invalid expectation kind")
                classes = expectation.get("classes")
                if not isinstance(classes, list) or not classes or not all(
                        isinstance(item, str) and item for item in classes):
                    errors.append(f"{prefix}.{variant_id} expectation classes are invalid")
                if not expectation.get("rationale"):
                    errors.append(f"{prefix}.{variant_id} expectation needs a rationale")
    return errors


def _run(command: list[str], *, cwd: Path | None = None,
         env: dict | None = None, timeout: int = 300) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            command, cwd=cwd, env=env, text=True, capture_output=True,
            check=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise CorpusError(f"command timed out after {timeout}s: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()[-1000:]
        raise CorpusError(f"command failed ({exc.returncode}): {command[0]}: {detail}") from exc


def acquire(entry: dict, destination: Path) -> None:
    """Fetch exactly one commit into a new directory and verify its identity."""
    destination.mkdir(parents=True, exist_ok=False)
    _run(["git", "init", "--quiet"], cwd=destination)
    _run(["git", "remote", "add", "origin", entry["url"]], cwd=destination)
    _run(
        ["git", "fetch", "--quiet", "--depth=1", "origin", entry["commit"]],
        cwd=destination, timeout=600,
    )
    _run(["git", "checkout", "--quiet", "--detach", "FETCH_HEAD"], cwd=destination)
    resolved = _run(["git", "rev-parse", "HEAD"], cwd=destination).stdout.strip()
    if resolved != entry["commit"]:
        raise CorpusError(f"{entry['id']}: fetched {resolved}, expected {entry['commit']}")


def _summarise_findings(findings: list[dict]) -> dict:
    """Retain reproducible metadata while dropping descriptions/source context."""
    classes: Counter = Counter()
    categories: Counter = Counter()
    records = []
    for finding in findings:
        detector_class = str(finding.get("detector_class", "unknown"))
        category = str(finding.get("category", "unknown"))
        classes[detector_class] += 1
        categories[category] += 1
        records.append({
            "file": str(finding.get("file", "")),
            "line": finding.get("line"),
            "detector_class": detector_class,
            "detector_priority": finding.get("detector_priority"),
            "category": category,
            "pattern_name": str(finding.get("pattern_name", "")),
            "indicators": sorted(str(item) for item in finding.get("indicators", [])),
            "suppressed": bool(finding.get("suppressed", False)),
        })
    records.sort(key=lambda item: (
        item["file"], item["line"] if isinstance(item["line"], int) else -1,
        item["detector_class"], item["pattern_name"],
    ))
    return {
        "total": len(records),
        "by_detector_class": dict(sorted(classes.items())),
        "by_category": dict(sorted(categories.items())),
        "findings": records,
    }


def _evaluate(expectations: list[dict], class_counts: dict[str, int]) -> list[dict]:
    outcomes = []
    for expectation in expectations:
        observed = {name: int(class_counts.get(name, 0)) for name in expectation["classes"]}
        passed = (all(count == 0 for count in observed.values())
                  if expectation["kind"] == "no_detector_classes"
                  else any(count > 0 for count in observed.values()))
        outcomes.append({
            "kind": expectation["kind"], "classes": expectation["classes"],
            "observed": observed, "passed": passed,
            "rationale": expectation["rationale"],
            "interpretation": (
                "diagnostic assertion only; independent contextual annotation "
                "is required before assigning false-positive or false-negative status"
            ),
        })
    return outcomes


def scan_variant(entry: dict, variant: dict, checkout: Path,
                 work: Path, repetition: int, config: dict) -> dict:
    scan_root = work / f"scan-{entry['id']}-{variant['id']}-{repetition}"
    scan_root.mkdir(parents=True)
    manifest_path = scan_root / "analysis-manifest.json"
    env = os.environ.copy()
    env["REGULA_CACHE_DIR"] = str(scan_root / "cache")
    env["REGULA_AUDIT_DIR"] = str(scan_root / "audit")
    command = [
        sys.executable, "-m", "scripts.cli", "check", str(checkout),
        "--format", "json", "--manifest", str(manifest_path),
        "--scope", config["scope"], "--min-tier", config["min_tier"],
        "--deterministic", "--no-facts", "--jurisdictions",
        ",".join(config["jurisdictions"]),
        "--skip-tests" if config["skip_tests"] else "--no-skip-tests",
    ]
    if variant["domains"]:
        command.extend(["--domain", ",".join(variant["domains"])])
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command, cwd=REPO_ROOT, env=env, text=True, capture_output=True,
            timeout=900,
        )
    except subprocess.TimeoutExpired as exc:
        raise CorpusError(f"{entry['id']}/{variant['id']} timed out after 900s") from exc
    duration = round(time.perf_counter() - started, 3)
    if completed.returncode not in {0, 1}:
        detail = (completed.stderr or completed.stdout or "").strip()[-1000:]
        raise CorpusError(
            f"{entry['id']}/{variant['id']} scan failed "
            f"({completed.returncode}): {detail}"
        )
    try:
        envelope = json.loads(completed.stdout)
        analysis = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise CorpusError(f"{entry['id']}/{variant['id']} emitted invalid evidence") from exc
    findings = (envelope.get("data") or {}).get("detector_findings")
    if not isinstance(findings, list):
        raise CorpusError(f"{entry['id']}/{variant['id']} has no detector_findings list")
    summary = _summarise_findings(findings)
    stable = {
        "exit_code": completed.returncode,
        "analysis_completion_status": analysis.get("completion_status"),
        "analysis_counts": analysis.get("counts"),
        "finding_summary": summary,
    }
    return {
        "repetition": repetition, "duration_seconds": duration, **stable,
        "content_sha256": _canonical_sha256(stable),
        "expectations": _evaluate(
            variant.get("expectations", []), summary["by_detector_class"]
        ),
    }


def evaluate_corpus(payload: dict, work: Path) -> dict:
    config = payload["scan_configuration"]
    results = []
    for index, entry in enumerate(payload["repositories"], 1):
        print(f"[{index}/{len(payload['repositories'])}] acquiring "
              f"{entry['repository']} at {entry['commit'][:12]}", file=sys.stderr)
        checkout = work / "checkouts" / entry["id"]
        checkout.parent.mkdir(parents=True, exist_ok=True)
        acquire(entry, checkout)
        variant_results = []
        for variant in entry["variants"]:
            runs = []
            for repetition in range(1, config["clean_repetitions"] + 1):
                print(f"  scan {variant['id']} repetition {repetition}", file=sys.stderr)
                runs.append(scan_variant(entry, variant, checkout, work, repetition, config))
            variant_results.append({
                "id": variant["id"], "domains": variant["domains"],
                "repeatable": len({run["content_sha256"] for run in runs}) == 1,
                "runs": runs,
            })
        results.append({
            key: entry[key] for key in (
                "id", "repository", "commit", "license_spdx",
                "primary_language", "stratum", "documented_capability"
            )
        } | {"variants": variant_results})
    variants = [variant for repo in results for variant in repo["variants"]]
    all_runs = [run for variant in variants for run in variant["runs"]]
    assertions = [
        outcome for variant in variants for outcome in variant["runs"][0]["expectations"]
    ]
    scanner_sources = sorted((REPO_ROOT / "scripts").glob("*.py")) + [
        REPO_ROOT / "references" / "decision_model.v1.json",
        REPO_ROOT / "references" / "framework_crosswalk.yaml",
        *sorted((REPO_ROOT / "references" / "jurisdictions").glob("*.yaml")),
    ]
    git_status = _run(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=REPO_ROOT
    ).stdout
    return {
        "result_schema_version": "1.0", "corpus_id": payload["corpus_id"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest_sha256": _canonical_sha256(payload),
        "regula_git_commit": _run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT).stdout.strip(),
        "regula_tracked_worktree_dirty": bool(git_status.strip()),
        "scanner_source_files": len(scanner_sources),
        "scanner_source_sha256": _files_sha256(scanner_sources),
        "ruleset_sha256": _sha256_bytes(
            (REPO_ROOT / "scripts" / "risk_patterns.py").read_bytes()
        ),
        "configuration_sha256": _canonical_sha256(payload["scan_configuration"]),
        "evaluator_sha256": _sha256_bytes(Path(__file__).read_bytes()),
        "codebook_sha256": _sha256_bytes(
            (REPO_ROOT / "benchmarks" / "external" / "README.md").read_bytes()
        ),
        "protocol_sha256": _sha256_bytes(
            (REPO_ROOT / "benchmarks" / "evaluation_protocol.v1.json").read_bytes()
        ),
        "environment": {"python": platform.python_version(),
                        "platform": platform.platform(), "machine": platform.machine()},
        "configuration": config,
        "summary": {
            "repositories": len(results), "variants": len(variants), "runs": len(all_runs),
            "repeatable_variants": sum(variant["repeatable"] for variant in variants),
            "completed_runs": sum(run["analysis_completion_status"] == "completed"
                                  for run in all_runs),
            "completed_with_skips_runs": sum(
                run["analysis_completion_status"] == "completed_with_skips" for run in all_runs),
            "diagnostic_assertions": len(assertions),
            "diagnostic_assertions_passed": sum(item["passed"] for item in assertions),
            "diagnostic_assertions_failed": sum(not item["passed"] for item in assertions),
        },
        "claim_boundary": (
            "Diagnostic output only. No precision, recall, specificity, F1, MCC, "
            "calibration, legal applicability, risk classification or compliance "
            "claim can be derived without independent context-complete annotation."
        ),
        "repositories": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path,
                        help="Keep acquisition/run state here instead of a temporary directory")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        raw = args.manifest.read_bytes()
        payload = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"manifest error: {exc}", file=sys.stderr)
        return 2
    errors = validate_manifest(payload)
    if errors:
        for error in errors:
            print(f"manifest error: {error}", file=sys.stderr)
        return 2
    if args.validate_only:
        print(f"valid: {len(payload['repositories'])} repositories; sha256={_sha256_bytes(raw)}")
        return 0
    try:
        if args.work_dir:
            args.work_dir.mkdir(parents=True, exist_ok=True)
            result = evaluate_corpus(payload, args.work_dir)
        else:
            with tempfile.TemporaryDirectory(prefix="regula-external-") as tmp:
                result = evaluate_corpus(payload, Path(tmp))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                               encoding="utf-8")
    except CorpusError as exc:
        print(f"corpus failed closed: {exc}", file=sys.stderr)
        return 2
    print(f"wrote {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
