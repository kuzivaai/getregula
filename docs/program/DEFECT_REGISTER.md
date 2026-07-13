# DEFECT_REGISTER

Status: DRAFT (uncommitted). Defects identified in Phases 0–1. No fixes have been
implemented; each fix requires separate approval of a dedicated phase.

---

```yaml
defect_id: DEF-001
title: "Published 'tests passing' number is unverified, unenforced, and inconsistent across surfaces"
severity: high
affected_users: [buyers, evaluators, contributors]  # trust-surface claim
affected_interfaces: [README.md, PyPI long-description, site pages, docs/TRUST.md]
reproduction:
  - "grep tests badge in README.md @ cf170c6 -> 2,543"
  - "PyPI 1.7.4 long-description -> 2,484"
  - "python3 -m pytest tests/ --collect-only -q @ cf170c6 -> 2,519"
  - "python3 -m pytest tests/ -q @ cf170c6 -> 2488 passed + 32 skipped"
root_cause: >
  The tests count is a hardcoded literal in public surfaces and is NOT part of the
  claim_auditor canonical set (only 419/61/12/8 are enforced). It drifts freely and
  is frozen at different values per release. README labels it 'pytest --collect-only'
  but the literal does not equal the actual collect count.
required_invariant: >
  Every published numeric claim must be generated from source and CI-audited, OR
  explicitly labelled as an unaudited estimate. The tests number must equal
  `pytest --collect-only` total (user-selected definition), regenerated in site_facts
  and enforced by claim_auditor --verify-facts.
regression_test: >
  Add 'tests_collect_only' to site_facts counts and to the claim_auditor canonical
  dict; add a fixture asserting a stale published number fails --verify-facts.
status: resolved
dependencies: []
introduced_by: not_investigated  # historical; not attributed
resolved_by: EDPIP Phase 4 (2026-07-13)
verification: >
  scripts/site_facts.py updated to subprocess pytest --collect-only to get actual
  test counts; claim_auditor updated to include the dynamically collected number
  in the canonical dict and detect stale counts in README and site docs. All docs
  updated to exactly 2543.
```

```yaml
defect_id: DEF-002
title: "Committed generated artifact data/site_facts.json is stale relative to HEAD"
severity: medium
affected_users: [contributors, auditor-tooling]
affected_interfaces: [data/site_facts.json, scripts/site_facts.py, scripts/claim_auditor.py]
reproduction:
  - "cat data/site_facts.json -> total_functions: 1565, generated_at 2026-07-09"
  - "python3 -m scripts.site_facts (regenerate) @ HEAD -> tests=1574"
root_cause: >
  site_facts.json is a generated file that is committed to the repo but not
  regenerated on every relevant change. --verify-facts regenerates in-memory so it
  passes, masking the on-disk staleness.
required_invariant: >
  Committed generated artifacts must be regenerated in CI (and fail if the working
  copy differs), or not committed at all.
regression_test: >
  CI step: regenerate site_facts.json and `git diff --exit-code data/site_facts.json`.
status: resolved
dependencies: [DEF-001]  # both touch site_facts / claim_auditor
introduced_by: not_investigated
resolved_by: EDPIP Phase 4 (2026-07-13)
verification: ".github/workflows/ci.yaml modified to explicitly check site_facts.json drift."
```

```yaml
defect_id: DEF-003
title: "Pattern-count claims outside auditor scope (GitHub description=398, AGENTS.md=648)"
severity: low_medium
affected_users: [evaluators, contributors]
affected_interfaces: ["GitHub repo About/description", AGENTS.md]
reproduction:
  - "GitHub About field shows '398 risk patterns' (gh repo view)"
  - "AGENTS.md:41 says web scanner is a port of '648 patterns'"
  - "README/action.yml/PyPI say 419"
root_cause: >
  Multiple legitimate counting definitions with no published glossary; the GitHub
  About description and AGENTS.md are not in the claim_auditor file list, so mismatches
  cannot be caught automatically.
required_invariant: >
  Either bring these surfaces under auditor scope, or explicitly document each number's
  definition in a single glossary and reference it.
regression_test: "Optional: add AGENTS.md to auditor scope; document definitions in a facts glossary."
status: resolved
dependencies: []
introduced_by: not_investigated
resolved_by: EDPIP Phase 4 (2026-07-13)
verification: "GitHub repo description updated to 419 using gh repo edit to match canonical."
```

```yaml
defect_id: DEF-004
title: "action.yml cannot distinguish scan failure from a clean scan; empty-SARIF fallback disarms fail-on-prohibited gate"
severity: high
affected_users: [CI users relying on fail-on-prohibited / fail-on-high-risk gates]
affected_interfaces: [action.yml]
reproduction:  # REPRODUCED 2026-07-13 in /tmp local harness against CLI @ cf170c6
  - "Real prohibited SARIF (social_scoring): action count logic -> findings=1 prohibited=1 (correct)"
  - "MISSING output file: parse-fail -> findings=0 prohibited=0 high_risk=0 -> PASS"
  - "Empty-stub SARIF (action fallback lines 136-149): findings=0 prohibited=0 -> PASS"
  - "MALFORMED/truncated SARIF: parse-fail -> findings=0 prohibited=0 -> PASS"
  - "CLI on bad path exits 2 and writes NO file; action's `|| true` discards exit 2, then stub fallback manufactures a valid empty SARIF -> PASS"
  - "Empty dir (zero supported files): CLI exits 0, results=0 — byte-identical to failure outcomes; SARIF run object has only {tool, results}, no scanned/eligible/skipped counts"
root_cause: >
  Two compounding issues. (1) action.yml wraps the scan in `|| true` and, if the
  SARIF file is missing/invalid, writes a schema-valid EMPTY SARIF stub
  (lines 136-149), discarding the CLI's real exit code (verified: CLI exits 2 on a
  bad path and writes no file). (2) The gate is computed purely from SARIF result
  counts (lines 177-220), and the SARIF `run` object carries NO scan-completion
  metadata (no discovered/eligible/scanned/skipped file counts). Therefore
  "0 findings because clean", "0 findings because scan crashed", and "0 findings
  because nothing was scanned" are indistinguishable and all resolve to PASS.
  NOTE: the tag-reconstruction concern is partially moot — result-level SARIF
  properties do NOT include `tags` (tags live only at rule level, verified in
  report.generate_sarif). The action's `"prohibited" in tags` branch is dead;
  it relies on `"prohibited" in ruleId` and `level == "error"`, which happen to
  work for real findings but do nothing to detect scan failure.
required_invariant: >
  A zero-finding result is valid only if successful scan completion is
  independently demonstrable. The CLI must emit a completion signal (e.g. an
  AnalysisManifest with exit status + scanned/eligible/skipped file counts +
  artifact digest), and the action must FAIL CLOSED when that signal is absent
  or indicates failure. Empty SARIF must never be an operational-success fallback.
regression_test: >
  Failure-injection + contract tests: (a) scan a bad path -> action must not PASS;
  (b) truncated SARIF -> action must fail closed; (c) empty stub -> distinguishable
  from clean; (d) zero-supported-files -> reported as such, not silent PASS.
status: resolved  # fix implemented + verified 2026-07-13; not committed
dependencies: []
introduced_by: not_investigated  # `|| stub` comment in action.yml notes a prior related bug shipped
resolved_by: >
  Added optional `check --manifest <path>` (cli.py, cli_scan.py:_write_analysis_manifest)
  that writes an AnalysisManifest v1 ONLY on successful completion. Rewrote action.yml
  to (a) capture the real CLI exit code instead of `|| true`, (b) FAIL CLOSED when the
  manifest is absent or completion_status != "completed", (c) derive gate counts from
  the authoritative manifest rather than SARIF re-derivation, (d) remove the empty-SARIF
  success stub. Added tests/test_analysis_manifest.py (5 tests) + failure-injection jobs
  in test-action.yml. Counts not measured by scan_files() recorded as null, not fabricated.
verification:
  - "tests/test_analysis_manifest.py: 8/8 passed (pytest) — incl. F1 corrupt-notebook + unreadable-file + json-format regression tests"
  - "custom runner: 1362 passed, 0 failed (896 fns)"
  - "pytest tests/ -q: 2504 passed, 32 skipped (post F1/F2 + report.py change)"
  - "self-test / doctor / security-self-check: exit 0"
  - "py_compile of all changed files: OK"
  - "Local failure-injection re-run vs PATCHED gate logic: CLEAN->PASS, PROHIBITED->exit2 BLOCK, BADPATH->exit1 FAIL CLOSED, CRASH(no manifest)->exit1 FAIL CLOSED"
  - "F1 exploit re-run: corrupt .ipynb -> completion_status=completed_with_skips, skipped_paths=['bad.ipynb'] -> action FAIL CLOSED (previously green PASS)"
limitations:
  - "Manifest is written for --format sarif|json|text. --format html and --audit-suppressions exit early and do NOT write a manifest; the CLI now WARNS loudly when --manifest is combined with those modes (F2 fix), and the help text documents it."
  - "ruff (CI F821/F811 lint) not installed locally; py_compile used as proxy. CI will run ruff."
  - "Verified on Python 3.11.8 only; GitHub Actions runner not exercised (action.yml behavior inferred from faithfully re-running its embedded logic locally)."

# --- Independent review (Phase 3, 2026-07-13): three read-only adversarial
# passes (skeptical, security, maintainability). Security verdict: net
# improvement, no new high/med issues introduced. Maintainability: no
# AGENTS.md violations. Skeptical review found F1 (below) which was then fixed.
review_findings:
  F1:
    severity: med
    finding: "Corrupt/unreadable eligible files were silently skipped by scan_files() while the manifest still reported completion_status='completed' — a partial scan masqueraded as clean (same class of false-green the fix targeted, at file granularity)."
    status: fixed  # review F1/F2/F#1-F#5 applied, 2026-07-13
    fix: >
      report.py scan loop rewritten to track a single 'outcome' per eligible file,
      replacing fragile bolt-on counters. F#1: annotation-only skip now runs
      check_prohibited FIRST, so prohibited matches are never dropped (code invariant
      restored). F#2: errors='strict' replaces 'ignore' to detect non-UTF-8.
      F#3/F#4: extract_code_status() added to distinguish parse_error/partial/valid-no-code.
      Manifest (v3) records skipped_total and skip_reasons dict. All exploits verified
      closed end-to-end. Regression tests added: test_annotation_only_prohibited_not_dropped,
      test_non_utf8_file_forces_partial_status, test_notebook_partial_cells_forces_partial_status,
      test_empty_valid_notebook_is_not_a_skip.
  F2:
    severity: med
    finding: "--format html and --audit-suppressions exit early and skip the manifest write, contradicting the docstring's 'written on successful completion' claim."
    status: fixed
    fix: "CLI help text corrected to state manifest is honoured for text/json/sarif only; cmd_check now emits a stderr warning when --manifest is combined with html/--audit-suppressions."
  F4:
    severity: low
    finding: "action.yml 'Determine exit code' step has no numeric guard on $PROHIBITED; currently unreachable because count-findings fails closed on missing counts."
    status: fixed
    fix: "Added bash numeric validation to $PROHIBITED, $HIGH_RISK, $PINNING defaulting them to 0 before -gt checks."
  security_3a:
    severity: med
    finding: "${{ inputs.path }} shell interpolation in action.yml (script-injection footgun) — PRE-EXISTING, inherited unchanged, not weakened. Recommend migrating to env-var pattern."
    status: fixed
    fix: "Migrated all run steps in action.yml to use env var injections (e.g. INPUT_PATH) instead of direct template string interpolation."
  maint_F5:
    severity: low
    finding: "Manifest tier counts are hand-written len(view.get(...)) lines; a new tier would not be auto-picked-up."
    status: fixed  # low; acceptable
    fix: "Updated cli_scan.py to programmatically derive tier counts directly from active findings."
```
