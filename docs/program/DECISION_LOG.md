# DECISION_LOG

Status: DRAFT (uncommitted). Material design decisions with evidence and trade-offs.

---

```yaml
decision_id: D-001
problem: >
  action.yml treated failed/empty/malformed scans as PASS, disarming the
  fail-on-prohibited / fail-on-high-risk compliance gate (DEF-004, reproduced
  2026-07-13).
options_considered:
  - "A: CLI AnalysisManifest (proof-of-completion) + fail-closed action + manifest-driven counts"
  - "B: Trust CLI exit code in the action only, remove `|| true` (no manifest)"
  - "C: Embed completion metadata inside SARIF run.properties"
selected_option: A
rejected_options:
  - "B: rejected — still cannot distinguish 'clean' from 'zero files scanned', and gives no artifact-integrity signal; the file-count blindness would remain."
  - "C: deferred — overloads a third-party interchange format (consumed by CodeQL) with our operational metadata; couples the gate to SARIF's schema. A sibling manifest is cleaner. Revisit only if a manifest proves insufficient."
evidence:
  - "Reproduced: missing/empty/malformed SARIF all -> 0/0/0 -> PASS."
  - "CLI already exits 2 (bad path, no file written), 1 (BLOCK findings), 0 (clean) — verified in cli_scan.py:696-720 and by subprocess tests."
  - "SARIF result-level properties carry NO tags (report.generate_sarif); action's tag-branch was dead."
tradeoffs: >
  Adds one optional CLI flag + a ~70-line manifest writer + a ~50-line action
  rewrite + 5 unit tests + 2 CI jobs. Minimal, additive, fully backward
  compatible (flag optional; omitting it reproduces prior behaviour byte-for-byte).
security_impact: "Positive — fail-closed prevents prohibited code merging when CI breaks."
privacy_impact: "Manifest holds scan path + counts + SARIF digest only; no new data class beyond what SARIF/logs already contain."
accessibility_impact: none
compatibility_impact: >
  json_output() envelope untouched (AGENTS.md constraint honoured); cli.py monolith
  not refactored; generate_sarif not changed; v1 floating-tag consumers unaffected
  (new inputs/outputs optional with safe defaults). New action output `manifest-file`
  is additive.
maintenance_cost: "Low. One schema at manifest_version '1', unit-tested; no new dependency (stdlib hashlib/datetime)."
revisit_trigger: >
  If per-file counts become needed for the gate (would require exposing them from
  scan_files, a schema-adjacent change), or if a future consumer needs completion
  metadata inside SARIF itself (option C).
approved_by: "user (implementation authorized 2026-07-13); not committed"
```

```yaml
decision_id: D-002
problem: >
  Independent skeptical review (F1) showed the manifest reported
  completion_status="completed" even when scan_files() silently skipped
  unreadable/unparseable eligible files — a partial scan could hide a prohibited
  pattern and still pass the gate. How to expose skip information without
  breaking scan_files()'s widely-used contract?
options_considered:
  - "A: add skip counters to the EXISTING scan_files.last_stats side-channel; cmd_check reads it; manifest gains a 'completed_with_skips' status (chosen)"
  - "B: change scan_files() return type to (findings, report) tuple"
  - "C: add a tree-sitter / real notebook parser so notebooks never fail to parse"
selected_option: A
rejected_options:
  - "B: rejected — scan_files() has 40+ call sites and an explicit test asserting it returns a list (test_classification.py:4231). Changing the return type is a large blast radius for no added value; last_stats already exists for exactly this purpose."
  - "C: rejected — adds an external dependency (violates stdlib-only), does not address unreadable files (permissions/IO), and a parser can still fail. The correct fix is to COUNT skips honestly, not to try to eliminate them."
evidence:
  - "scan_files.last_stats already publishes files_scanned/tests_skipped etc (report.py); adding two counters is idiomatic."
  - "F1 exploit reproduced pre-fix (completed/0 findings/PASS) and post-fix (completed_with_skips/FAIL CLOSED)."
  - "Full suite 2504 passed, 32 skipped after the report.py change — no scan-engine regression."
tradeoffs: "Two new counters + a bounded skipped_paths list (capped at 100) + manifest schema v1->v2. No signature change to scan_files(); no new dependency."
security_impact: "Positive — closes a file-granularity fail-open in the compliance gate."
privacy_impact: "skipped_paths adds relative file paths (already local, non-secret); capped to bound manifest size."
accessibility_impact: none
compatibility_impact: >
  Manifest schema bumped to '2' (additive + one status value added). action.yml
  and the 5 original tests updated accordingly. scan_files() callers unaffected.
  New action input allow-partial-scan defaults false (fail-closed) — safe default.
maintenance_cost: "Low; counters live at the existing skip points, one side-channel."
revisit_trigger: "If scan_files() gains structured discovered/eligible/unsupported counts, promote those from null to measured and bump manifest to v3."
approved_by: "user (best-practice/objective mandate, 2026-07-13); not committed"
```

```yaml
decision_id: D-003
problem: >
  Skeptical re-review of the D-002 fix identified critical flaws (F#1-F#5). The bolt-on
  skip counters failed to catch: (1) annotation-only precision filter silently dropping
  files with prohibited phrases, violating the tool's core invariant; (2) non-UTF-8 files
  scanned as garbage via errors="ignore"; (3) notebook partial-cell drops. It also created
  a false-positive: (4) benign markdown-only notebooks wrongly flagged as partial scans.
options_considered:
  - "A: Add more bolt-on counters at each point, keep errors='ignore'."
  - "B: Architectural rewrite — a single per-file outcome model in scan_files(), strict UTF-8 decoding, structured notebook status, and prohibited-check hoisted BEFORE precision filters."
selected_option: B
rejected_options:
  - "A: Rejected. Bolt-on counters at `continue` points are fragile and inevitably miss edge cases. errors='ignore' is inherently unsafe for a security/compliance scanner."
evidence:
  - "F#1 reproduced: 'predictive policing' in an annotation-only file was silently dropped and the CI gate passed."
  - "F#4 reproduced: valid markdown-only notebook triggered the gate failure."
tradeoffs: >
  Extracting notebook status required a new extract_code_status() method, keeping the old
  one as a wrapper for backward compatibility. Hoisting check_prohibited costs slightly more
  CPU per annotation-only file, but correctly enforces the Article 5 detection invariant.
security_impact: "High positive. Closes the annotation-only prohibited evasion (F#1) and the non-UTF-8 evasion (F#2)."
privacy_impact: none
accessibility_impact: none
compatibility_impact: >
  Manifest bumped to v3 to support structured skip_reasons dict instead of flat keys.
  scan_files() contract unchanged. extract_code() contract unchanged.
maintenance_cost: "Lower. Single per-file outcome path is easier to reason about than scattered counters."
revisit_trigger: "None currently."
approved_by: "user (objective/comprehensive mandate, 2026-07-13); not committed"
```

```yaml
decision_id: D-004
problem: >
  The public claim "2,531 tests passing" in README.md and other surfaces was not dynamically
  verified and had drifted from reality. Also, the data/site_facts.json was stale.
options_considered:
  - "A: Add test count to claim_auditor but use simple regex grep for count."
  - "B: Use `pytest --collect-only` as the true count, and enforce it in claim_auditor and ci.yaml."
selected_option: B
rejected_options:
  - "A: Rejected. Grepping for 'def test_' is inaccurate and misses parametrize tests.
evidence:
  - "pytest --collect-only collected 2543 tests. Replaced all stale values across the site."
tradeoffs: >
  Running `pytest --collect-only` via subprocess in site_facts.py adds a small overhead, but
  ensures 100% accuracy.
security_impact: none
privacy_impact: none
accessibility_impact: none
compatibility_impact: "None"
maintenance_cost: "Low. Enforced by CI."
revisit_trigger: "None currently."
approved_by: "user (objective/comprehensive mandate, 2026-07-13); not committed"
```

```yaml
decision_id: D-005
problem: >
  Phase 5 threat-model investigation of scan_files() (report.py) found two
  concrete, reproduced gaps: (1) a symlinked file inside a scanned repo
  resolving outside the project root was followed and its content scanned
  with no origin check; (2) no per-file size ceiling existed before
  filepath.read_bytes(), so a single huge file could exhaust memory. A
  scanned repository must be treated as untrusted input (e.g. a third-party
  PR scanned in CI).
options_considered:
  - "A: Add a single path-safety+size gate (_is_safe_to_scan) applied once per file before any read, reusing the existing _record_skip/skip_reasons/completion_status machinery from DEF-004."
  - "B: Reject the entire scan (hard error) if any unsafe file is encountered."
  - "C: Silently exclude unsafe files with no manifest signal (matches historical behaviour for other skip types before DEF-004)."
selected_option: A
rejected_options:
  - "B: Rejected — too disruptive; a single stray symlink or one oversized generated file (e.g. a committed binary-ish artifact) would hard-fail the entire scan instead of being reported as a bounded, explainable partial scan. Inconsistent with how DEF-004 already handles other per-file skip reasons."
  - "C: Rejected — this is exactly the DEF-004 anti-pattern (silent skip -> false-clean completion). Would reintroduce the same class of fail-open bug this program has been closing."
evidence:
  - "Reproduced: symlink to a file outside the scan root, containing a prohibited-pattern trigger, was read and a finding was produced BEFORE the fix; after the fix, 0 findings + skip_reasons.symlink_escape=1."
  - "Reproduced: an 11 MB file was read into memory with no limit before the fix; after the fix (MAX_FILE_SIZE_BYTES=10MB), the file is stat()'d and rejected before any read."
  - "False-positive checks confirm no regression: an in-root symlink still scans normally; a normal-sized file is unaffected."
tradeoffs: >
  Adds one new constant (MAX_FILE_SIZE_BYTES) and one new ~35-line function
  (_is_safe_to_scan), called once per file. No change to scan_files()'s
  signature, return type, or the 40+ existing call sites. Two new skip_reasons
  values ("symlink_escape", "oversized") flow through the existing
  AnalysisManifest without a schema version bump (the shape was already a
  free-form dict of reason -> count).
security_impact: >
  Positive. Closes an arbitrary-file-read vector (a scanned repo's symlink
  could previously read anything the scanning process could access — CI
  secrets, SSH keys, /etc/passwd) and a memory-exhaustion vector (unbounded
  single-file read).
privacy_impact: "Positive — prevents a hostile repo from causing Regula to read and potentially surface file content the user did not intend to scan."
accessibility_impact: none
compatibility_impact: >
  A file that was previously silently followed via symlink-escape (extremely
  unlikely to be intentional/legitimate) will now be skipped and the scan
  marked completed_with_skips. A file over 10 MB (a large but real scenario
  for e.g. a committed lockfile or generated bundle) will likewise be
  skipped rather than scanned. Both are surfaced explicitly in the manifest
  (skipped_files + skip_reasons), not silent.
maintenance_cost: "Low — one function, one constant, reuses existing skip-accounting/manifest machinery."
revisit_trigger: >
  If a legitimate use case needs a file size >10MB scanned, MAX_FILE_SIZE_BYTES
  should become configurable (CLI flag or policy config) rather than raised
  globally.
approved_by: "user (objective/unbiased/best-practice mandate, 2026-07-14); not committed"
```
