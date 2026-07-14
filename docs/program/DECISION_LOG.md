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

```yaml
decision_id: D-006
problem: >
  Continued Phase 5 investigation empirically fuzz-tested all 432 built-in
  regex patterns against ReDoS attack strings (none failed) and then against
  realistic file-scale adversarial content, finding ~15 patterns sharing a
  (?:word)[^"\n]{0,30}(?:word) shape take 2.2-2.7s EACH on a 10MB file
  densely saturated with their trigger keyword, applied whole-file (not
  per-line) by classify_risk.py. Full classification pipeline measured at
  27.8s worst-case on one file.
options_considered:
  - "A: Cap total content length passed to the whole-file classification path (MAX_CLASSIFY_CHARS), truncating and marking as a dangerous skip (chosen)"
  - "B: Rewrite each of the ~15 vulnerable patterns to eliminate the gap-alternation shape (e.g. tighten {0,30} or restructure)"
  - "C: Add a wall-clock timeout around the whole classification call (e.g. signal.alarm) and treat a timeout as a skip"
  - "D: Switch whole-file matching to per-line matching for these tiers (matching check_ai_security's existing approach)"
selected_option: A
rejected_options:
  - "B: Rejected for this pass — these are legal-consequence-mapped patterns (Article 5/Annex III triggers with specific `article`/`conditions`/`exceptions` metadata); hand-editing 15 of them individually risks introducing false-negatives in a safety-critical detector for comparatively small aggregate benefit, since a content-length cap already bounds the blast radius without touching detection semantics for any real file. Worth a dedicated future pass with proper before/after benchmark comparison (see revisit_trigger)."
  - "C: Rejected — signal-based timeouts are not thread-safe/portable (SIGALRM is POSIX-only, complicating Windows support which the project's CI matrix does not explicitly exclude), and killing mid-classification could leave partial/inconsistent state harder to reason about than a simple, deterministic content cap applied up front."
  - "D: Rejected as a blanket change — would alter match-line-number semantics and touch more code than necessary; per-line matching only works cleanly when a pattern's alternation halves are expected on the same line, which several of these are not guaranteed to be (see the credit_scoring/insurance/housing groups, which use generic language that can legitimately span short multi-line contexts). A future targeted redesign of this pattern shape could revisit this."
evidence:
  - "27.8s worst-case measured pre-fix (full 4-call pipeline, 10MB adversarial file) -> 0.23s post-fix (full scan_files() end-to-end)."
  - "Largest legitimate source file in the codebase measured at ~95 KB; MAX_CLASSIFY_CHARS (1 MB) gives 10x+ margin."
tradeoffs: >
  A file with real, meaningful content beyond 1 MB (rare — no such file
  exists in this codebase) would have content past that point excluded from
  classification and the scan marked partial. This is a strictly safer
  failure mode than either silently missing content (no signal) or crashing
  (DEF-007's failure mode).
security_impact: "Positive — bounds a real (if not catastrophic-exponential) CPU-exhaustion vector to a small, fixed per-file budget."
privacy_impact: none
accessibility_impact: none
compatibility_impact: >
  No signature/return-type changes anywhere. Reuses the DEF-004/DEF-005
  skip-accounting and completion_status machinery unchanged; adds one new
  skip_reasons value ("oversized_for_classification").
maintenance_cost: "Low — one constant, one truncation point, no new dependency."
revisit_trigger: >
  If MAX_CLASSIFY_CHARS proves too tight for a real, legitimate large
  generated/minified file class, OR if a dedicated benchmark-backed pass is
  done to rewrite the ~15 root-cause patterns (option B) to eliminate the
  underlying cost rather than bound its blast radius.
approved_by: "user (objective/unbiased/best-practice mandate, 2026-07-14); not committed"
```

```yaml
decision_id: D-007
problem: >
  While verifying D-006's fix end-to-end, discovered that ast.parse() raises
  an uncaught MemoryError on pathological input as small as ~10 KB (many
  bare word tokens, no other Python structure). build_context_map()'s
  except clause covered only (SyntaxError, ValueError), so this crashed the
  ENTIRE scan (all files, not just the triggering one) with exit code 2 and
  no manifest written — silently discarding a genuine, already-detected
  finding in an unrelated legitimate file in the same reproduction.
options_considered:
  - "A: Catch MemoryError (and defensively RecursionError) in build_context_map(), returning {} — the function's own pre-existing documented graceful-degradation contract (chosen)"
  - "B: Wrap the entire per-file scan iteration in report.py in a try/except that logs and continues on any exception"
  - "C: Run AST parsing in a subprocess with a resource limit, to fully sandbox against any CPython-internal resource exhaustion"
selected_option: A
rejected_options:
  - "B: Rejected as the PRIMARY fix — a blanket per-file try/except in the scan loop would mask the specific, now-understood root cause behind generic exception-swallowing, making future similar bugs harder to diagnose (silent catch-all is explicitly against this program's truthfulness principles). The narrow fix at the actual failure point is both smaller and more diagnosable. (A general per-file safety net in report.py may still be worth adding in a future defence-in-depth pass — not rejected outright, just not the primary fix here.)"
  - "C: Rejected as disproportionate — subprocess isolation for every file's AST parse would add meaningful performance overhead and complexity (process spawn per file) to defend against a failure mode now closed by a two-exception-type addition to an existing except clause. Revisit only if evidence emerges of OTHER CPython-internal resource-exhaustion bugs beyond ast.parse()."
evidence:
  - "Direct reproduction: ast.parse('a ' * 5000) raises MemoryError; ast.parse('a ' * 1000) raises SyntaxError (the already-handled case)."
  - "End-to-end CLI reproduction: 2-file project, one crash-trigger file (~20KB) + one legitimate file with a real prohibited-pattern finding -> pre-fix: exit 2, generic 'Internal error', no manifest, finding lost. Post-fix: exit 1, manifest written, completion_status=completed, the genuine finding correctly reported."
tradeoffs: >
  None identified — this restores build_context_map()'s own pre-existing
  documented contract ('graceful degradation... no breakage') rather than
  introducing new behaviour or a new tradeoff.
security_impact: "Positive — closes a full scan-availability failure reachable by a single small (~10 KB) adversarial or even accidentally-malformed file anywhere in a repository."
privacy_impact: none
accessibility_impact: none
compatibility_impact: "None. No signature change; return value {} on this new failure path is identical in shape to the existing SyntaxError/ValueError path, and callers already handle an empty context map (that is the whole point of the function's graceful-degradation design)."
maintenance_cost: "Negligible — two additional exception types in one existing except clause."
revisit_trigger: >
  If evidence emerges of other CPython stdlib calls in this codebase
  (beyond ast.parse() in build_context_map()) that can raise MemoryError/
  RecursionError on small adversarial input, each should be reviewed
  individually — this fix was scoped to the one call site verified to be
  reachable from the main scan loop.
approved_by: "user (objective/unbiased/best-practice mandate, 2026-07-14); not committed"
```

```yaml
decision_id: D-008
problem: >
  D-007's own revisit_trigger explicitly flagged that other ast.parse()
  call sites in the codebase should be reviewed for the same MemoryError
  gap. Rather than leave this as an acknowledged-but-unaddressed limitation,
  followed up immediately: grepped the whole codebase for every ast.parse()
  call, found 7 more sites (5 in ast_analysis.py, 2 in cross_file_flow.py),
  and independently verified reachability and a real, distinct failure mode
  for each before deciding how to fix.
options_considered:
  - "A: Apply the identical (MemoryError, RecursionError) except-clause fix to all 7 sites, matching D-007's pattern exactly (chosen)"
  - "B: Introduce a shared safe_ast_parse() wrapper function and migrate all 8 call sites to use it"
  - "C: Leave the additional sites unfixed and only document them as a known limitation, since D-007's actual verified impact was on the main scan loop"
selected_option: A
rejected_options:
  - "B: Rejected for THIS pass — a shared wrapper is a reasonable future refactor (would prevent a newly-added ast.parse() call from reintroducing the gap), but each of the 8 sites has a DIFFERENT graceful-degradation return shape (empty list, empty dict with specific keys, 'not_python' string, etc.), so a generic wrapper would need per-callsite default values passed in anyway, reducing the simplification benefit. Applying the same 2-exception-type addition inline at each site is smaller, more obviously correct by inspection, and matches the existing code style (each site already has its own bespoke except-and-return-default pattern for SyntaxError)."
  - "C: Rejected — reproduction proved this is not a theoretical residual risk. `regula gap` genuinely exits 0 while silently producing no output on the exact same trivial trigger (~10-20 KB), which is arguably a WORSE failure mode than the originally-fixed site (that one at least exits 2). Documenting a reproduced, easily-triggered, silently-successful command failure as merely a 'limitation' rather than fixing it would contradict this program's truthfulness principles."
evidence:
  - "Direct reproduction: analyse_project_oversight() called directly raised MemoryError uncaught, pre-fix."
  - "Direct reproduction: `regula gap <project-with-adversarial-file>` exited 0 with only 'Internal error' printed and no real report, pre-fix; produces genuine gap-analysis output, post-fix."
  - "Verified report.py's existing --enrich-oversight `except Exception` block already caught this specific crash as an accidental side effect (MemoryError/RecursionError both derive from Exception, confirmed via .__mro__) — but this was not a designed contract and did not protect the same underlying function when called from compliance_check.py instead."
tradeoffs: "Identical to D-007: no signature/behavior changes for any well-formed input; only the previously-uncaught-crash path now degrades gracefully."
security_impact: "Positive — closes 2 more concretely-reproduced availability failures (regula gap silent failure; oversight analysis crash) using the exact same trivial (~10-20 KB) trigger as D-007's original finding."
privacy_impact: none
accessibility_impact: none
compatibility_impact: "None — each site's return value on this new failure path is identical in shape to its existing SyntaxError-handling path."
maintenance_cost: "Negligible per-site; slightly higher aggregate maintenance burden than a shared wrapper would have (see rejected option B), accepted as a reasonable trade for a smaller, more obviously-correct change in this pass."
revisit_trigger: >
  If a THIRD round of ast.parse() gaps is found (e.g. via a newly-added
  call site elsewhere), consider promoting to a shared safe_ast_parse()
  helper (option B) at that point, since three independent occurrences of
  the same hand-applied fix would be a stronger signal that centralising it
  is worth the reduced flexibility.
approved_by: "user (objective/unbiased/best-practice mandate, 2026-07-14); not committed"
```

```yaml
decision_id: D-009
problem: >
  While investigating scripts/api_server.py for Phase 5 network-surface
  hardening (found to already be well-designed), noticed `check --format
  json`'s envelope always reports exit_code=0 regardless of findings.
  Verified this contradicts the real process exit code (reproduced: a
  prohibited finding gives process exit 1, but the JSON body's own
  exit_code field said 0). Also found --format html independently
  computes its own narrower exit condition, ignoring warn-tier+--ci.
  Discovered an identical, already-fixed bug class for the sibling
  `assess` command (test docstring cites a "July 2026 UX-audit Critical"),
  which was evidently never cross-checked against other commands sharing
  the same envelope contract.
options_considered:
  - "A: Compute the exit code ONCE early in cmd_check(), before any format branch, and have every format (json/html) reuse that single value; remove the later duplicate computation entirely (chosen)"
  - "B: Leave the duplicate computations in place but manually keep them in sync (add a comment linking them)"
  - "C: Fix only the json envelope (the more severe, machine-parsed case) and leave html's narrower bug as a separate lower-priority item"
selected_option: A
rejected_options:
  - "B: Rejected — this program has repeatedly found that manually-synchronized duplicates drift (DEF-002/DEF-003's stale-number pattern; this defect ITSELF is a case of duplicated exit-code logic drifting). Adding a comment does not prevent a future edit to one copy forgetting the other; removing the duplication structurally does."
  - "C: Rejected — the html bug is the same root cause (an independently re-derived verdict instead of one shared value) and the fix for A already naturally covers both with no extra cost; splitting it into a separate, deferred item would be arbitrary given the fix is a single, already-scoped diff."
evidence:
  - "Reproduced pre-fix: prohibited finding, --format json -> process exit 1, envelope exit_code=0 (contradiction). Clean scan -> process exit 0, envelope exit_code=0 (consistent, as a control)."
  - "Reproduced pre-fix: warn-tier-only finding, --format html, --ci -> process exit 0 (should be 1, matching text/json/sarif under the same --ci flag)."
  - "tests/test_cli_integration.py:test_assess_json_prohibited_exit_code_in_envelope already exists for `assess` and passes both before and after this fix (confirms this fix does not touch or regress the already-correct assess command)."
tradeoffs: >
  None identified beyond the fix itself — this is a strict simplification
  (net removal of duplicated logic) with no behavior change for any
  already-correct case (verified via a dedicated clean-scan regression test).
security_impact: "Positive (Medium) — closes a data-integrity gap in the documented, frozen envelope contract that could cause CI/automation trusting the JSON body to silently treat a prohibited/high-risk finding as a pass."
privacy_impact: none
accessibility_impact: none
compatibility_impact: >
  The json_output() envelope SHAPE is unchanged (AGENTS.md constraint
  honoured: still {format_version, regula_version, command, timestamp,
  exit_code, data}) — only the VALUE of the pre-existing exit_code field
  changes for cases that were previously wrong. Any consumer already
  correctly checking the process exit code (the majority, and the only
  documented/tested path prior to this fix) is unaffected. A consumer that
  was relying on the buggy always-0 envelope value for a check command
  specifically (not assess, which was already correct) would see a
  behavior change — assessed as extremely unlikely and not a supported
  use case, since it would mean deliberately ignoring the process exit
  code in favour of a field this fix proves was unreliable.
maintenance_cost: "Negative (reduces cost) — removes one of two duplicate exit-code computations."
revisit_trigger: >
  If a systematic audit of every json_output(...) call site across all CLI
  commands is done (flagged as a limitation of this pass, scoped only to
  check/assess), any further instances of this bug class found should be
  fixed the same way: compute once, share the value across every format.
approved_by: "user (objective/unbiased/best-practice mandate, 2026-07-14); not committed"
```
