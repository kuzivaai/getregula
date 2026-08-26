# Test performance audit — 26 August 2026

## Outcome

The defensible speed-up is execution parallelism over the **unchanged complete
pytest collection**, not test selection. Two xdist workers with the `worksteal`
scheduler roughly halved local pytest wall time while preserving one complete
sequential run for order and shared-state evidence. The custom harness remains
an independently executed product-contract surface, but it need not repeat on
all four Python versions because pytest already executes its assertions across
the version matrix.

No measured test population, interpreter, assertion surface, security audit,
or product-contract audit was removed. Predictive or change-based test
selection is explicitly excluded from required pull-request and release gates.

## Measurement method

- Host: Linux under WSL2, Python 3.12.3.
- Test engine: pytest 9.1.1; parallel runner: pytest-xdist 3.8.0.
- Population: 2,920 pytest-collected cases. Result totals include pytest's
  subtest reporting and therefore should not be reverse-engineered into a
  second population count.
- Commands were run from a clean checkout worktree with the same source tree.
- Each candidate executed the full `tests/` collection. No `-k`, path subset,
  last-failed cache, or changed-file selector was used.
- Wall time is the decision metric. CPU time and peak RSS are retained to make
  the resource trade-off visible.

## Local results before the contributor-extra expansion

These three directly comparable runs used the same optional-test environment.
The complete final verification after the dependency expansion is recorded in
the dated validity audit; these numbers remain the controlled worker-count
comparison.

| Mode | Pytest time | External wall | User CPU | Peak RSS | Result |
|---|---:|---:|---:|---:|---|
| Sequential | 293.06 s | not separately captured | not separately captured | not separately captured | 2,861 passed, 38 skipped, 11 subtests passed |
| 2 workers, `worksteal` (run 1) | 151.40 s | 155.85 s | 294.38 s | 244 MB | same result totals |
| 2 workers, `worksteal` (repeat) | 148.29 s | 152.66 s | 288.68 s | not recaptured | same result totals |
| 4 workers, `worksteal` | 143.50 s | 144.97 s | 496.66 s | 224 MB | same result totals |

Two workers reduced pytest-reported wall time by 49.4% on the repeat. Four
workers saved only another 4.79 seconds (3.2%) against that repeat while using
about 72% more user CPU than two-worker run 1. Repository-wide scans became
contention-bound, so four workers are not the default.

### Post-change verification (not folded into the controlled comparison)

| Mode | Pytest time | External wall | User CPU | Peak RSS | Result |
|---|---:|---:|---:|---:|---|
| 2 workers, final tree | 157.68 s | 165.13 s | 309.89 s | 249 MB | 2,861 passed, 38 skipped, 11 subtests passed |
| Sequential, final tree | 527.66 s | 553.75 s | 514.58 s | 257 MB | same result totals |

The later runs included the expanded contributor environment, claim guards,
reports and website changes. They prove the final tree passes in both modes;
they are not used as the speed headline. Repository-wide tests were markedly
slower in the later sequential run (for example the self-scan rose from about
39 to 61 seconds), showing host/source-state drift. Comparing a post-change
run with an earlier-tree baseline as though it were a controlled experiment
would overstate precision. The worker-count decision therefore remains based
on the same-tree controlled runs above, with the remote matrix as external
confirmation.

The custom runner completed 1,268 functions with 1,445 helper assertions,
zero failures and 12 optional-feature skips in 278.87 seconds external wall
time. Its slowest operations were repository self-scans and security/source
guards, not assertion dispatch.

On the final expanded contributor environment, the same 1,268-function custom
harness reported 1,453 helper assertions, zero failures and 8 skips in 155.90
seconds external wall. The four recovered skips include the syntax-aware
Tree-sitter path. This later run validates the complete environment; its timing
is not compared causally with the earlier run because host and source state had
changed.

## GitHub Actions evidence

The last ordinary CI run inspected before this change had a critical path of
11 minutes 44 seconds. In the four Python cells, the custom runner took
3:18–3:49 and sequential pytest took 6:18–7:06. Installing the test tools took
only 4–6 seconds, so caching installation would not address the bottleneck.

A manual, non-gating experiment on commit `59fa3146` ran custom, sequential
pytest and xdist independently on Python 3.10–3.13. All 12 cells succeeded:
[GitHub Actions run 32962560625](https://github.com/kuzivaai/getregula/actions/runs/32962560625).
The remote experiment used the then-committed `-n auto`; the adopted workflow
uses the locally characterised and resource-bounded `-n 2`.

| Python | Sequential pytest | Remote xdist experiment | Reduction |
|---|---:|---:|---:|
| 3.10 | 426 s | 204 s | 52.1% |
| 3.11 | 379 s | 175 s | 53.8% |
| 3.12 | 416 s | 185 s | 55.5% |
| 3.13 | 330 s | 222 s | 32.7% |

The median remote step fell from 397.5 to 194.5 seconds (51.1%). This proves
that the complete suite can run successfully under xdist on all supported
interpreters at the measured commit. It does not prove that every future test
will be parallel-safe.

## Implemented CI design

1. Python 3.10–3.13 each execute all pytest cases with two workers and
   `--dist worksteal`.
2. Python 3.12 also executes the complete collection sequentially to retain a
   fixed-order/shared-state audit.
3. Python 3.12 executes the alternate custom runner once, followed by the
   security self-check, quotation verifier, transcript verifier and browser
   questionnaire contract.
4. Matrix `fail-fast` is false, so one interpreter failure cannot cancel the
   remaining diagnostic evidence.
5. The `test` extra now includes every optional feature dependency needed by
   the tests plus xdist. `uv.lock` records the exact contributor environment;
   the installed product core still has zero required runtime dependencies.

Separating the custom harness from the interpreter matrix removes repeated
harness overhead without removing assertion coverage: those functions remain
inside pytest's complete four-version population, while one run still verifies
the distinct custom discovery/dispatch mechanism. The additional sequential
job means the expected workflow critical path is approximately the full
sequential pytest duration rather than sequential pytest plus the custom
runner. That expectation has not been called a measured CI improvement because
the updated workflow cannot run remotely until the sanitised history is safe
to push.

## Slow-path findings

The largest local costs were intentional repository-wide behaviour tests:

- Regula scanning its own repository: about 39–40 seconds;
- two large-scan resource/safety tests: about 30 seconds each;
- security self-check and security source scans: about 20–31 seconds;
- public-claim, determination and repository guard scans: about 10–23 seconds.

Caching these results inside tests would make them faster but risks concealing
state changes that the tests exist to detect. The audit therefore leaves their
semantics intact and parallelises independent cases around them.

## Alternatives reviewed

| Candidate | Decision | Reason |
|---|---|---|
| [pytest-xdist](https://github.com/pytest-dev/pytest-xdist) | Adopted, bounded to two workers | Executes the complete collection; `worksteal` is designed for uneven test durations |
| [pytest-split](https://github.com/jerry-git/pytest-split) | Not adopted now | Job splitting could help once timing data is stable, but duplicates job setup and does not replace the sequential order audit |
| [pytest-testmon](https://github.com/tarpas/pytest-testmon) and research test selection | Rejected for required gates | Changed-code selection can miss dependency, environment, generated-surface and global-state effects; even the stronger 2026 NameRTS preprint reports less than 100% safety |
| [mutmut](https://github.com/boxed/mutmut) / [Cosmic Ray](https://github.com/sixty-north/cosmic-ray) | Targeted future quality audit, not a speed mechanism | Mutation testing evaluates whether assertions kill plausible faults; it is computationally expensive and predictive-mutation research warns that methodology can inflate results |
| Dependency caching | Not prioritised | Measured installation was 4–7 seconds versus minutes in the test bodies |
| Removing slow repository scans | Rejected | Those scans exercise the product and its public-integrity controls end to end |

The emerging NameRTS result is a preprint, not peer-reviewed settled evidence:
[arXiv 2605.25356](https://arxiv.org/abs/2605.25356). The mutation-testing
methodology warning is peer reviewed: ["Methodological pitfalls in predictive
mutation testing"](https://doi.org/10.1007/s10515-026-00626-9), *Automated
Software Engineering* (2026).

## Remaining validation and risks

- Run the updated workflow on a reviewable remote branch after the public
  history replacement gate is cleared; compare critical path and per-step
  totals with the 11:44 baseline.
- Treat an xdist-only failure as a concurrency defect until disproved; do not
  mark it flaky or rerun it away.
- Add an occasional random-order audit only after its failure triage and seed
  retention policy are defined.
- Pilot mutation testing on a small, decision-critical pure module and publish
  killed, survived, invalid and timeout counts. Do not report a mutation score
  without operator set, exclusions and equivalent-mutant handling.
- Reprofile after material test-population or repository-size changes. Worker
  count is an empirical configuration, not a permanent constant.

## Sources checked 26 August 2026

- [pytest-xdist distribution documentation](https://pytest-xdist.readthedocs.io/en/stable/distribution.html)
- [pytest flaky-test guidance](https://docs.pytest.org/en/stable/explanation/flaky.html)
- [GitHub-hosted runner reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
- [pytest repository](https://github.com/pytest-dev/pytest)
- [pytest-xdist repository](https://github.com/pytest-dev/pytest-xdist)

Repository activity and popularity were used only as maintenance signals, not
as evidence that a tool is correct or suitable.
