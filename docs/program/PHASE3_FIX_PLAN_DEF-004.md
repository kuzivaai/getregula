# Phase 3 Fix Plan — DEF-004 (CI fail-open on scan failure)

Status: DRAFT PLAN (uncommitted). No source edited. Requires explicit approval of
the diffs below before implementation.

Baseline commit: `cf170c663422277c6d0f7e6e1d53d299736daa45`
Defect: DEF-004 (reproduced 2026-07-13) — `action.yml` cannot distinguish a failed,
empty, or malformed scan from a genuinely clean scan; all resolve to PASS,
disarming `fail-on-prohibited` / `fail-on-high-risk`.

---

## 1. Root-cause summary (verified)

1. `action.yml` runs the scan with `|| true` and, if the SARIF file is missing or
   invalid, writes a schema-valid EMPTY SARIF stub (lines 136-149), discarding the
   CLI's real exit code. Verified: the CLI exits **2** on a bad path and writes no
   file; it exits **1** on BLOCK findings (`cli_scan.py:622-628`); it exits **0** on
   a clean scan.
2. The gate is derived only from SARIF result counts (`action.yml:177-220`), and the
   SARIF `run` object carries **no scan-completion metadata** (keys: `{tool, results}`).
   So "clean", "crashed", "nothing scanned" are indistinguishable.

Design principle: **fail closed**. Absence of positive proof of a completed scan
must not be treated as success.

## 2. Chosen approach

Smallest complete root-cause fix, additive and backward-compatible:

- **CLI (`check`)**: add an optional `--manifest <path>` flag that writes an
  AnalysisManifest JSON on **successful** completion, AFTER the scan and artifact
  write. If the scan raises, the manifest is never written (its absence is the
  failure signal). The manifest records completion state and file counts.
- **action.yml**: request the manifest, and **fail closed** if it is absent or
  reports non-completion. Stop treating a missing/empty SARIF as success. Keep the
  existing exit-code semantics (0 / 1 / 2) for the *findings* gate.
- **Tests**: add failure-injection jobs to `test-action.yml` and a Python unit test
  for the manifest writer.

This does NOT change the `json_output()` envelope (AGENTS.md constraint), does NOT
refactor `cli.py`, adds no external dependency, and preserves the `v1` consumer
contract (all new inputs/outputs are optional with safe defaults).

Rejected alternatives (recorded in DECISION_LOG draft below):
- **Re-parse CLI exit code in the action only** (no manifest): rejected — still can't
  distinguish "0 files scanned" from "clean", and `|| true` + stub would need removal
  anyway; the manifest also fixes the file-count blindness.
- **Put completion data inside SARIF `run.properties`**: viable, but SARIF is an
  interchange format consumed by CodeQL; overloading it with our operational metadata
  is less clean than a sibling manifest. Deferred, not rejected.

## 3. Acceptance criteria (testable)

Positive:
- AC1: `regula check <clean-dir> --format sarif --output s.sarif --manifest m.json`
  exits 0, writes both files; `m.json.completion_status == "completed"`,
  `m.json.exit_code == 0`, `scanned >= 0`.
- AC2: `regula check <prohibited-fixture> --format sarif --manifest m.json` writes a
  manifest with `completion_status == "completed"` and a non-zero finding count, and
  the CLI exit code is 1 (BLOCK).

Negative / failure:
- AC3: `regula check <bad-path> --manifest m.json` exits 2 and writes **no** manifest
  (and no SARIF).
- AC4: A scan that raises mid-run writes no manifest (absence = failure).

Unsupported / edge:
- AC5: `regula check <empty-dir> --manifest m.json` exits 0, manifest present,
  `completion_status == "completed"`, `eligible == 0` / `scanned == 0` — a clean scan
  of nothing is reported AS SUCH, distinct from failure.

Action behavior (fail-closed):
- AC6: action with a valid completed manifest + prohibited findings → exit 2.
- AC7: action where the scan step fails (bad path / crash) and no manifest is written
  → action exits non-zero (FAIL), NOT a green PASS. No empty-SARIF success fallback.
- AC8: action with a malformed/truncated SARIF but a present completed manifest with
  0 findings → still must not silently PASS if the SARIF is unparseable AND findings
  are unknown; fail closed.
- AC9: action on a clean fixture with a completed manifest → exit 0 (PASS) — the happy
  path still works (regression).

Compatibility:
- AC10: `--manifest` is optional; omitting it reproduces today's behavior exactly.
- AC11: `json_output()` envelope unchanged; existing tests still pass.
- AC12: Existing `test-action.yml` jobs 1-8 still pass unchanged.

Security:
- AC13: `--manifest` path is validated/created under the runner temp dir; no path
  traversal beyond the intended output location (reuse existing `mkdir(parents=True)`
  pattern; do not follow symlinks outside the target).

## 4. AnalysisManifest schema (proposed, minimal)

```json
{
  "manifest_version": "1",
  "regula_version": "1.7.4",
  "scan_target": "/abs/path/scanned",
  "started_at": "2026-07-13T16:40:00Z",
  "completed_at": "2026-07-13T16:40:03Z",
  "completion_status": "completed",
  "exit_code": 0,
  "counts": {
    "discovered": 12,
    "eligible": 9,
    "scanned": 9,
    "skipped": 3,
    "unsupported": 0,
    "findings_total": 1,
    "prohibited": 1,
    "high_risk": 0
  },
  "sarif_sha256": "<hex or null if no sarif written>"
}
```
Notes: version starts at "1"; unknown fields ignored by consumers; counts are
authoritative for the gate (the action should prefer manifest counts over SARIF
re-derivation). `sarif_sha256` lets the action confirm the SARIF it counts is the one
the scan wrote.

LIMITATION: `scan_files()` currently returns only findings; per-file discovered/
eligible/skipped counts may not all be readily available without a small change to
`report.scan_files`. If any count cannot be obtained cheaply, it will be recorded as
`null` (explicitly unknown) rather than fabricated. This will be verified during
implementation and reported.

## 5. Exact files to change (proposed)

CHANGE:
- `scripts/cli.py` — add `p_check.add_argument("--manifest", ...)` (~1 line, after
  line 882 `--name`).
- `scripts/cli_scan.py` — in `cmd_check`, after the SARIF/JSON/HTML branch and before
  the final `sys.exit`, write the manifest if `args.manifest` is set. Populate counts
  from the already-computed `_view` partition (`prohibited`, `high_risk`, `active`) and
  from scan bookkeeping. (~15-25 lines; new helper `_write_analysis_manifest`.)
- `action.yml` — request `--manifest "${MANIFEST_FILE}"`; replace the empty-SARIF
  success fallback with fail-closed logic driven by manifest presence + status; prefer
  manifest counts for the gate. (~20-40 lines net.)
- `.github/workflows/test-action.yml` — add failure-injection jobs (bad path, missing
  manifest, malformed SARIF) asserting the action FAILS.

ADD:
- `tests/test_analysis_manifest.py` — unit tests for `_write_analysis_manifest`
  (AC1-AC5), wired into `tests/test_classification.py` per AGENTS.md convention.

INTENTIONALLY NOT CHANGED:
- `json_output()` envelope; `cli.py` monolith structure; `report.generate_sarif`
  (unless a count is unobtainable otherwise — will ask first); the `v1` tag.

## 6. Risks & rollback

- Risk: `report.scan_files` may need a minor return-shape addition to expose file
  counts. If so, that is a schema-adjacent change → will re-run the full suite and
  report before finalizing (revalidation trigger per program rules). If it's more than
  trivial, I will stop and re-scope.
- Rollback: revert the 4 changed files + delete the new test; all changes are additive
  and gated behind an optional flag.

## 7. Verification plan (on approval)

1. `python3 tests/test_classification.py` + `pytest tests/ -q` (full suite, no
   weakening).
2. New `tests/test_analysis_manifest.py` (AC1-AC5).
3. Local re-run of the Phase 3 failure-injection harness against the patched CLI +
   action count logic (AC6-AC9) — reproduce that failures now FAIL closed.
4. `self-test`, `doctor`, `security-self-check`.
5. Confirm `--manifest`-omitted path is byte-identical to prior behavior (AC10).
6. Inspect full diff; update DEFECT_REGISTER (DEF-004 → resolved_by + verification)
   and DECISION_LOG.

---

## Draft DECISION_LOG entry

```yaml
decision_id: D-001
problem: "action.yml treats failed/empty/malformed scans as PASS, disarming the compliance gate (DEF-004)."
options_considered:
  - "A: CLI AnalysisManifest + fail-closed action (chosen)"
  - "B: Trust CLI exit code in action only, remove `|| true` (rejected — no file-count signal)"
  - "C: Embed completion data in SARIF run.properties (deferred)"
selected_option: A
rejected_options: [B]
evidence: "Reproduced 2026-07-13: missing/empty/malformed SARIF all -> 0/0/0 -> PASS; CLI itself exits 2/1/0 correctly."
tradeoffs: "Adds one optional CLI flag + a small manifest writer; minimal surface, additive, back-compat."
security_impact: "Positive — fail-closed prevents prohibited code merging on CI breakage."
privacy_impact: "Manifest contains paths + counts only (already in SARIF/logs); no new data classes."
accessibility_impact: none
compatibility_impact: "Optional flag; v1 consumers unaffected; json_output envelope untouched."
maintenance_cost: "Low; one schema at version 1, unit-tested."
revisit_trigger: "If scan_files needs non-trivial changes, or if SARIF-embedded metadata (option C) becomes preferable."
approved_by: PENDING
```
