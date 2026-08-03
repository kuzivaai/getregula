#!/usr/bin/env python3
# regula-ignore
"""Produce the canonical recall artefact from an actual benchmark run.

F24. Before this existed, `claim_auditor` could derive precision from
`benchmarks/results/random_corpus/PRECISION.json` but could not derive a
recall figure at all, so every published recall fraction was unverifiable
by the gate that exists to verify published numbers. Worse, the figures in
circulation came from ad-hoc runs whose conditions were described in prose:
"10/30 default", "14/30 domain declared", "19/30 with both gates". Nothing
committed could reproduce them, and the first published recall figure
(80%, n=5) survived precisely because nothing could.

This script is the only writer of `benchmarks/synthetic/RECALL.json`.
`tests/test_recall_artefact.py` re-runs it and fails if the committed file
disagrees, so the artefact cannot be edited by hand and cannot drift.

WHY EVERY FRACTION CARRIES A PATH AND A GATE CONDITION
------------------------------------------------------
The same corpus yields different recall depending on which code path runs
and which gates are satisfied. Those are not rounding differences: the
scanner path and the classifier path disagree on this corpus, which is
finding F8. A recall number without both labels is not a measurement, it
is an average over conditions nobody chose.

DEFINITION OF A HIT
-------------------
A fixture counts as recalled when the HIGHEST tier detected in it equals
the tier the manifest expects. This is the definition
`benchmarks/synthetic/run.py` already used; it is reused unchanged so the
classifier row stays comparable with the historical figure.

Usage:
    python3 scripts/build_recall_artefact.py            # write the artefact
    python3 scripts/build_recall_artefact.py --check    # compare, do not write

Stdlib only.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))

FIXTURES = REPO_ROOT / "benchmarks/synthetic/fixtures"
MANIFEST = REPO_ROOT / "benchmarks/synthetic/manifest.json"
ARTEFACT = REPO_ROOT / "benchmarks/synthetic/RECALL.json"

ALL_DOMAINS = [
    "employment", "medical", "finance", "biometrics",
    "education", "law_enforcement", "infrastructure", "migration",
]

# Injected verbatim at the top of a fixture COPY to satisfy the AI-indicator
# gate. Recorded in the artefact because the condition is meaningless
# without it: a different import would move the number.
AI_IMPORT_LINE = "import torch  # injected by build_recall_artefact.py\n"

TIER_ORDER = {"prohibited": 4, "high_risk": 3, "limited_risk": 2,
              "minimal_risk": 1, "not_ai": 0}


def _highest_tier(findings: list[dict]) -> str:
    if not findings:
        return "not_ai"
    return max(findings,
               key=lambda f: TIER_ORDER.get(f.get("tier", "not_ai"), 0)
               ).get("tier", "not_ai")


def _run_cli(target: Path, domains: list[str] | None) -> dict[str, list[dict]]:
    """The scanner path: exactly what a user runs, via the CLI."""
    cmd = [sys.executable, "-m", "scripts.cli", "check", str(target),
           "--format", "json"]
    if domains:
        cmd += ["--domain", ",".join(domains)]
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          cwd=str(REPO_ROOT), timeout=1800)
    if not proc.stdout.strip():
        raise RuntimeError(
            f"regula produced no output (rc={proc.returncode}): "
            f"{proc.stderr[:400]}")
    doc = json.loads(proc.stdout)
    payload = doc.get("data", doc) if isinstance(doc, dict) else doc
    findings = payload if isinstance(payload, list) else payload.get("findings", [])
    by_file: dict[str, list[dict]] = defaultdict(list)
    for f in findings:
        by_file[Path(f.get("file", "")).name].append(f)
    return by_file


def _run_classifier(domains: list[str]) -> dict[str, list[dict]]:
    """The classifier path: report.scan_files called directly, as
    benchmarks/synthetic/run.py does. Not what a user runs."""
    from report import scan_files
    findings = scan_files(str(FIXTURES), declared_domains=set(domains))
    by_file: dict[str, list[dict]] = defaultdict(list)
    for f in findings:
        by_file[Path(f.get("file", "")).name].append(f)
    return by_file


def _fixtures_with_ai_import(dest: Path) -> Path:
    """A copy of the corpus with an AI-library import prepended to each
    fixture, so the AI-indicator gate is satisfied for every file."""
    shutil.copytree(FIXTURES, dest)
    for p in sorted(dest.glob("*.py")):
        p.write_text(AI_IMPORT_LINE + p.read_text(encoding="utf-8"),
                     encoding="utf-8")
    return dest


def _score(by_file: dict[str, list[dict]], expectations: dict) -> dict:
    """Per expected tier: hits, total, misses (named, so traces can start)."""
    stats: dict[str, dict] = {}
    for fname, expected in sorted(expectations.items()):
        if expected == "not_high":
            continue
        row = stats.setdefault(expected, {"hits": 0, "total": 0, "missed": []})
        row["total"] += 1
        if _highest_tier(by_file.get(fname, [])) == expected:
            row["hits"] += 1
        else:
            row["missed"].append(fname)
    for tier, row in stats.items():
        row["fraction"] = f"{row['hits']}/{row['total']}"
        row["percent"] = round(100.0 * row["hits"] / row["total"], 1)
    return stats


CONDITIONS = [
    {
        "id": "scanner/default",
        "path": "scanner",
        "gates": "none",
        "label": "default scan",
        "invocation": "python3 -m scripts.cli check <fixtures> --format json",
        "note": "What a user runs with no flags. Opt-in domains stay off.",
    },
    {
        "id": "scanner/domains-declared",
        "path": "scanner",
        "gates": "domains-declared",
        "label": "all opt-in domains declared",
        "invocation": ("python3 -m scripts.cli check <fixtures> --format json "
                       "--domain " + ",".join(ALL_DOMAINS)),
        "note": ("All eight opt-in domains declared at once. This is a "
                 "SUPERSET of declaring only each fixture's own matching "
                 "domain, so it is an upper bound on the per-fixture "
                 "condition, not the same measurement."),
    },
    {
        "id": "scanner/domains-declared+ai-import",
        "path": "scanner",
        "gates": "domains-declared+ai-import",
        "label": "domains declared and an AI-library import present",
        "invocation": ("python3 -m scripts.cli check <fixtures-with-ai-import> "
                       "--format json --domain " + ",".join(ALL_DOMAINS)),
        "note": ("Fixtures copied and given " + AI_IMPORT_LINE.strip() +
                 " so the AI-indicator gate is satisfied for every file. "
                 "The corpus is modified; the number is not comparable to a "
                 "scan of the corpus as committed."),
    },
    {
        "id": "classifier/domains-declared",
        "path": "classifier",
        "gates": "domains-declared",
        "label": "report.scan_files called directly",
        "invocation": ("report.scan_files(fixtures, declared_domains=all) "
                       "- benchmarks/synthetic/run.py"),
        "note": ("NOT what a user runs. Bypasses the CLI's scope and "
                 "min-tier filtering. Its disagreement with the scanner "
                 "path on this corpus is finding F8."),
    },
]


def build() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expectations = manifest["expectations"]

    measured = {}
    for cond in CONDITIONS:
        if cond["id"] == "scanner/default":
            by_file = _run_cli(FIXTURES, None)
        elif cond["id"] == "scanner/domains-declared":
            by_file = _run_cli(FIXTURES, ALL_DOMAINS)
        elif cond["id"] == "scanner/domains-declared+ai-import":
            with tempfile.TemporaryDirectory() as td:
                dest = _fixtures_with_ai_import(Path(td) / "fixtures")
                by_file = _run_cli(dest, ALL_DOMAINS)
        elif cond["id"] == "classifier/domains-declared":
            by_file = _run_classifier(ALL_DOMAINS)
        else:
            raise AssertionError(f"unhandled condition {cond['id']}")
        measured[cond["id"]] = {
            **{k: v for k, v in cond.items() if k != "id"},
            "tiers": _score(by_file, expectations),
        }

    return {
        "_what_this_is": (
            "Canonical recall fractions for the synthetic corpus. Produced "
            "by scripts/build_recall_artefact.py from an actual run. Never "
            "hand-edited: tests/test_recall_artefact.py re-runs the "
            "measurement and fails if this file disagrees."),
        "_hit_definition": (
            "A fixture is recalled when the HIGHEST tier detected in it "
            "equals the tier manifest.json expects."),
        "_publication_rule": (
            "Every published recall fraction must state its path and gate "
            "condition. A bare fraction is not a measurement: the same "
            "corpus gives different answers per condition, and the scanner "
            "and classifier paths disagree (finding F8)."),
        "_ai_import_injected": AI_IMPORT_LINE.strip(),
        "manifest_version": manifest.get("version"),
        "fixture_count": len(expectations),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "conditions": measured,
    }


def _comparable(doc: dict) -> str:
    """The artefact minus its timestamp, for drift comparison."""
    return json.dumps({k: v for k, v in doc.items() if k != "generated_at"},
                      indent=2, sort_keys=True)


def main(argv: list[str]) -> int:
    from tree_guard import untracked_inputs

    check_only = "--check" in argv
    fresh = build()
    if check_only:
        # Symmetry with build_gap_demo: --check reports contamination rather
        # than refusing, so a reader cannot mistake a passing comparison for
        # a reproducible artefact. Without this the recall corpus could be
        # contaminated and --check would stay silent, which is the asymmetry
        # an adversarial review of the first version found.
        try:
            stray = untracked_inputs(FIXTURES)
        except Exception:
            stray = []
        if stray:
            print(
                "WARNING: " + str(FIXTURES) + " holds content that is not in "
                "the repository, so these figures do not reproduce in a clean "
                "clone:\n  " + "\n  ".join(stray) + "\n"
                "This check compares the artefact against a run on the SAME "
                "inputs, so it passing does not mean the published figures "
                "are reproducible. See ledger N43.",
                file=sys.stderr,
            )
        if not ARTEFACT.exists():
            print(f"MISSING: {ARTEFACT.relative_to(REPO_ROOT)}", file=sys.stderr)
            return 1
        committed = json.loads(ARTEFACT.read_text(encoding="utf-8"))
        if _comparable(committed) != _comparable(fresh):
            print("RECALL.json disagrees with a fresh run. Re-run "
                  "scripts/build_recall_artefact.py and commit the result.",
                  file=sys.stderr)
            return 1
        print("RECALL.json matches a fresh run.")
        return 0

    # Refuse to write a published artefact from inputs a clone does not have.
    # This corpus is clean today (38 tracked files, nothing untracked or
    # ignored, measured 2026-07-31), so this changes no current behaviour; it
    # is here because the same defect reached data/gap_demo.json through the
    # other generator, and a guard on only the fixture that already failed
    # would close the instance rather than the class. See ledger N43.
    from tree_guard import UntrackedInputError, assert_inputs_tracked
    try:
        assert_inputs_tracked(FIXTURES)
    except UntrackedInputError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    ARTEFACT.write_text(json.dumps(fresh, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(f"wrote {ARTEFACT.relative_to(REPO_ROOT)}")
    for cid, row in sorted(fresh["conditions"].items()):
        for tier, s in sorted(row["tiers"].items()):
            print(f"  {cid:38s} {tier:12s} {s['fraction']:>7s}  "
                  f"{s['percent']}%")
    return 0


if __name__ == "__main__":
    from tree_guard import stamp
    stamp()
    raise SystemExit(main(sys.argv[1:]))
