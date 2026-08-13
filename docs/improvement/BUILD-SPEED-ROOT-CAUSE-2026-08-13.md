# Build and verification speed root-cause record

**Date:** 2026-08-13

**Baseline implementation commit:** `b6a151f5995d8ea48d1af024c8f0ca7333346ff4`

**Baseline implementation tree:** `b9a08aed1ad613eeb5dd22b737e8f09c80cbbeff`

## Classification rule

- **Demonstrated** means a command was run or the implementation was read.
- **Asserted** means a prior record states it and this investigation did not
  reproduce it.
- **Interpreted** means an inference whose assumptions and falsifier are named.

## Baseline observation

**Demonstrated from the final custom-runner output retained in the consolidated
handover.** The 15 slowest custom-runner functions had these durations, in
seconds:

```text
428.141  test_evidence_pack_summary_contains_risk_tier
427.471  test_evidence_pack_cli_integration
401.176  test_annex_iv_standards_from_policy
340.820  test_annex_iv_has_all_nine_sections
291.196  test_evidence_pack_sha256_integrity
260.116  test_evidence_pack_contains_required_files
224.416  test_evidence_pack_generates_manifest
222.008  test_annex_iv_completion_covers_new_sections
200.092  test_docs_include_data_flow
192.191  test_docs_completion_report
190.626  test_docs_auto_populated_sections
84.031   test_smoke_check_html_output_file
62.393   test_smoke_check_html
34.852   test_smoke_inventory
27.155   test_cli_exit_codes
```

Command used to reconcile the itemisation:

```text
python3 -c "values=[428.141,427.471,401.176,340.820,291.196,260.116,224.416,222.008,200.092,192.191,190.626,84.031,62.393,34.852,27.155]; print(sum(values)); print(sum(values)/60)"
3386.684
56.44473333333334
```

**Demonstrated by implementation read.** Each selected function uses the real
generator or CLI, but passes `.` or the repository root as the project under
test. The assertions concern output structure, required sections, hashes,
exit-code classes, or document language. None asserts a property that requires
the whole Regula repository as input.

## Root-cause hypothesis and prediction recorded before modification

**Interpreted.** The dominant cost is fixture amplification: independent tests
re-scan the whole repository even though a small real project can exercise the
same code path and assertion. Assumptions: the existing
`tests/fixtures/sample_high_risk` fixture reaches the same generator branches,
and the generators do not have a hidden repository-size-dependent contract.
Falsifier: any unchanged assertion fails on that fixture for a reason that is
part of the intended test property, or the selected group remains slow.

**Prediction, recorded before modification or post-change timing:** changing
only the scan input for these tests to the existing four-file fixture, while
keeping the real generators, real subprocesses, isolated output directories,
and every assertion, will make the selected 15-test group pass in less than
120 seconds on this host. No skip, mock, timeout increase, cache, pin,
allowlist, or assertion weakening will be introduced.

**Secondary prediction:** if the selected group meets the primary prediction,
a full custom-runner or pytest path should fall below 10 minutes on a host with
comparable load. This secondary prediction can be falsified by another slow
class outside the custom-runner top 15 or by materially different host load.

## Measurements after the prediction

### Controlled 15-test comparison

The same 15 named tests passed after changing only their project input to the
existing four-file `tests/fixtures/sample_high_risk` fixture:

```text
15 passed, 426 deselected in 2.70s
ELAPSED=3.69 CPU_USER=3.17 CPU_SYSTEM=0.52 MAX_RSS_KB=78616
```

The measured wall-time reduction is `3386.684 / 3.69 = 917.8x`. The comparison
is deliberately limited to the selected group: the baseline values are the sum
of per-test durations, while the new value is the process wall time, so the
ratio is approximate rather than a laboratory-grade microbenchmark. The
prediction was nevertheless confirmed by a margin too large to be explained by
timer noise.

Every assertion remained in place. The tests still call the real CLI, document
generators, evidence-pack generator, filesystem, hashing code, and subprocesses.
No mock, skip, shared mutable output directory, timeout increase, cache, pin,
allowlist, or reduced assertion was used.

### Complete-command measurements

An isolated custom-runner attempt immediately after the fixture correction took
58.11 seconds wall time. Its only failure was the repository provenance guard:
the new bare-route regression file was not yet tracked. That is expected guard
behaviour and not a product failure.

After staging that test, the exact four-command verification chain was run. The
custom runner passed `1464` cases across `1161` callable functions. Pytest then
reported `2780` passes and one failure in 943.42 seconds. The failure was a
stale sentence in `docs/TRUST.md` that still said `1159` custom-runner
functions; the new test made the measured total `1161`. Because the commands
are joined with `&&`, self-test and doctor correctly did not run. The complete
chain ended after 1386.74 seconds (23 minutes 6.74 seconds), rc=1. The stale
count was then repaired and its focused guard passed.

This 23-minute run is not represented as the final green result. It is useful
diagnostic evidence because the custom runner itself was green and the single
pytest failure was identified, repaired, and rechecked. A clean final execution
is recorded in the verification section below when available.

### Load sensitivity

The same custom-runner functions varied sharply between nearby runs:

| Test | Lower-load run | Contended run |
|---|---:|---:|
| self scan | 7.923 s | 163.220 s |
| JSON envelope | 6.134 s | 93.228 s |
| security self-check | 2.426 s | 20.523 s |
| large scan | 1.917 s | 17.927 s |

This is demonstrated host-load sensitivity, not evidence that those functions
became slower in source. The affected tests intentionally scan a large tree or
spawn a process; their elapsed time expands when CPU and filesystem resources
are contended. Timing targets therefore need both a stable CI reference host
and trend distributions, not a single developer-machine threshold.

## Root-cause tree

### Primary cause: assertion scope was coupled to fixture scope

The slow tests asked narrow questions such as whether an Annex document has its
required sections, whether a manifest hash is correct, or whether HTML output
is emitted. They nevertheless supplied the Regula repository as the project to
scan. Each test recursively repeated work over thousands of repository files.
The test's input size was accidental; it was not part of the asserted contract.

The controlled fixture substitution and 917.8x selected-group reduction make
this the demonstrated dominant deterministic cause of the hour-long custom
runner.

### Secondary cause: two intentionally overlapping discovery systems

The required verification chain runs the custom function enumerator and then
pytest discovery. This overlap is intentional: the first guards the manually
wired compatibility runner, while the second catches tests omitted from it.
It provides independent discovery evidence, but it also executes many cases
twice. Removing either runner would change the project's assurance policy and
was not authorised by a speed investigation. The cost should remain visible so
an owner can later decide whether the compatibility runner still earns it.

### Secondary cause: expensive whole-repository tests were mixed into the
ordinary suite

Some repository-scale scans are legitimate: security self-checks and
self-analysis explicitly need the whole tree. They were not replaced with the
small fixture. Their purpose differs from the corrected document-shape tests,
but the suite previously offered no timing report in its normal CI command, so
accidental and intentional large scans looked the same until an hour-long run
was manually profiled.

### Amplifier: harness constraints caused repeated partial executions

The managed execution sandbox denied the localhost socket used by RFC 3161
timestamp fixtures. The unrestricted wrapper could start those fixtures but
terminated long-lived commands in earlier attempts. This produced several
honest-but-incomplete runs before the exhaustive two-part result was obtained.
It did not make an individual test computationally expensive, but it multiplied
the elapsed investigation time.

### Amplifier: broad work scope

The approximately 24-hour session was not one build. It included primary-law
research, decision-surface enumeration, implementation, mutation and property
controls, browser-engine unification, three locale updates, real VS Code host
testing, live/local browser comparison, failure repair, repeated verification,
and a multi-megabyte evidence handover. That scope explains part of the wall
clock, but it does not excuse the avoidable test amplification.

### Amplifier: variable shared-host load

CPU time remained close to wall time during the long runs, which demonstrates
active computation rather than an I/O deadlock. Nearby measurements nevertheless
showed 10x to 20x per-test variance on repository scans. That makes an absolute
developer-host deadline an unreliable regression oracle unless load is
controlled.

## Five-whys analysis

1. Why did verification take roughly an hour per runner? Because multiple tests
   repeatedly scanned the complete repository and generated full document or
   evidence outputs.
2. Why did narrow output-contract tests scan the complete repository? Their
   fixture was `.` or the repository root, inherited from convenient smoke-test
   examples.
3. Why was this not caught earlier? The default CI invocation did not print a
   useful slow-test table, and total green/red status hid the cost distribution.
4. Why did the session approach a day? The slow runners were repeated after
   fixes, sandbox limitations forced complementary partitions, and the task also
   contained regulatory research and cross-surface browser validation.
5. Why not simply parallelise everything? Parallelism can reduce wall time but
   cannot repair pathological input scope, and this repository contains Git,
   worktree, port, timestamp-server, and filesystem-state tests that must first
   demonstrate isolation under concurrency.

## Was 24 hours normal?

No, not for ordinary code verification of this repository. The demonstrated
56.4-minute concentration in 15 fixture-amplified tests was avoidable and is now
repaired. A long adversarial regulatory migration with primary-source research,
cross-runtime conformance, browser inspection, and an evidence handover can
reasonably consume many hours, but that is a statement about task scope, not a
justification for hour-long feedback loops.

A more honest operating expectation is:

- focused tests for a local change: seconds to a few minutes;
- the canonical serial verification chain: measured and trended on a stable CI
  host, with the result below recorded rather than assumed;
- repository-wide self-analysis and browser/extension checks: explicit lanes
  whose cost and purpose are visible;
- regulatory research and representative human usability testing: separate
  work products, not disguised as build time.

## Current official methods and their fit here

The investigation used current primary technical documentation rather than
tool-fashion claims.

- Pytest documents `--durations` and `--durations-min` for exposing slow tests.
  The canonical CI command now emits its 50 slowest cases instead of hiding the
  distribution. See [pytest invocation documentation](https://docs.pytest.org/en/stable/how-to/usage.html).
- Pytest fixture scopes can reuse genuinely expensive setup at module or session
  scope. This is appropriate only when the shared object is immutable or reset
  safely; it is not needed for the corrected small-fixture tests. See [pytest
  fixture documentation](https://docs.pytest.org/en/stable/how-to/fixtures.html).
- Pytest-xdist supports CPU distribution. Its `worksteal` scheduler is designed
  for unequal test durations, while `loadscope`, `loadfile`, and explicit groups
  can keep related state together. A manual, non-gating workflow now measures
  xdist; it does not replace the serial gate until repository-state and port
  isolation are demonstrated. See [pytest-xdist distribution
  documentation](https://pytest-xdist.readthedocs.io/en/stable/distribution.html).
- GitHub Actions matrices and `max-parallel` support controlled interpreter and
  suite experiments. The repository already uses a Python-version matrix; its
  manual experiment now compares custom, serial pytest, and xdist without
  weakening required CI. See [GitHub Actions matrix
  documentation](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations).

At the measurement date, the project's locked test environment resolves pytest
9.1.1, and the current PyPI releases inspected were pytest 9.1.1 and
pytest-xdist 3.8.0. Those are current technologies, but version novelty is not
the speed strategy: correcting fixture scope produced the demonstrated gain.
The test matrix remains Python 3.10 through 3.13 because the product supports
Python 3.10+, and core runtime dependencies remain stdlib-only.

## Changes made

1. Replaced repository-root input with the existing four-file real fixture in
   the 15 tests whose assertions do not depend on repository size.
2. Corrected one additional JSON-envelope test that also used `.` for a narrow
   output contract.
3. Added `--durations=50 --durations-min=0.1` to serial CI pytest.
4. Expanded the manual experiment to compare custom, serial pytest, and
   pytest-xdist `--dist worksteal` across Python 3.10 to 3.13.
5. Kept the canonical CI serial and blocking while parallel safety remains
   unproved.

## Changes deliberately not made

- No test was skipped, quarantined, mocked, or given a longer timeout.
- No assertion was removed or loosened.
- No result cache was introduced that could conceal changes between runs.
- No production dependency was added; xdist exists only in a manual CI
  experiment.
- No repository-scale security or self-analysis contract was converted to a
  toy fixture.
- No timing threshold was made a required gate from a noisy shared-host sample.
- The required custom-runner plus pytest chain was not redefined.

## Recommended operating model

### P0: retain the fixture correction and timing visibility

Acceptance: all corrected tests exercise the real generators and retain their
assertions; the canonical CI log always identifies the slowest 50 cases.
Falsifier: a required behavior is shown to depend on full-repository input, or
duration output disappears from CI.

### P0: treat the published site as a release-integrity gate

The browser investigation found the deployed site behind the local decision
kernel. Deployment state must be checked separately from source tests. A future
release gate should compare a build identifier or decision-contract probe on
the deployed EN, DE, and PT-BR pages after publication. This must not silently
deploy from a developer test command.

### P1: run the manual xdist matrix and classify failures

Acceptance: repeated serial and xdist runs execute the same collected cases and
produce the same outcomes on all supported Python versions. Any test that owns
a fixed port, mutates Git/worktree state, or assumes process-global state must
be isolated or grouped before xdist can gate merges. Falsifier: intermittent or
order-dependent disagreement with the serial suite.

### P1: separate intentional scale benchmarks from contract tests

Keep at least one explicit whole-repository scan for performance and security
regression evidence, label it accordingly, and avoid repeating that input in
document-shape tests. Record median and high-percentile timing on a stable host
rather than using one shared-machine result.

### P2: review the compatibility runner's long-term value

The custom runner currently protects manual registration and legacy execution.
An owner may later decide whether an automated registration manifest or a
pytest collection guard can preserve that assurance with less duplicate
execution. This is a policy decision, not an optimisation silently made here.

## Residual risks and uncertainties

- The canonical serial suite still contains legitimate whole-repository scans
  and remains sensitive to host contention.
- The monolithic `tests/test_classification.py` couples compatibility,
  registration, functional tests, and performance reporting. It was not
  structurally refactored in this work.
- Xdist safety is unproven. A manual workflow definition is not evidence that a
  parallel run is deterministic.
- The earlier 23-minute command failed before self-test and doctor because of
  the intended `&&` semantics. Only a later complete command can close final
  verification.
- A developer-machine timing cannot establish a service-level objective.
  Stable CI history is still required.

## Final verification at the repaired implementation commit

Pending the clean, one-command run. This section must contain the commit, tree,
wall time, per-stage result, and any environment-bound qualification before this
record is called complete.
