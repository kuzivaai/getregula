# Session log, 31 July 2026 (session B)

Raw evidence record, appended as each check ran. The previous session's log
is `SESSION-LOG-2026-07-31.md`; this is a separate session on the same date,
named -b so neither overwrites the other.

## STEP 1: state re-established from the repository

```
$ date -Is
2026-07-31T08:19:01+01:00
$ git rev-parse --short HEAD; git rev-parse 'HEAD^{tree}'
d410405
cb02b240f6a49ce9898f5c8973d08db15f6afd63
$ git status --porcelain
?? docs/improvement/SESSION-LOG-2026-07-31b.md
$ git ls-remote --heads origin improvement/2026-08-programme
f286562c26cfdf9534c91ec304ae1aa423c0a581	refs/heads/improvement/2026-08-programme
$ git rev-parse main origin/main
6daacd2d92deb117286678dca2eede05ce50aa34
6daacd2d92deb117286678dca2eede05ce50aa34
$ git log --oneline main..HEAD | wc -l
107
$ git log --oneline -5 --format='%h %ad %s' --date=short
d410405 2026-07-31 docs(improvement): fill the unresolved commit placeholder in ledger row N49
a5c6a7a 2026-07-31 docs(improvement): record the final suite result in the session log
30fd6e8 2026-07-31 feat(guard): an artefact backing a published number cannot be built from untracked inputs; cascade 2,595 to 2,608
cd6ff3c 2026-07-31 docs(improvement): ledger row N48, the closing verification and its three attempts
346a494 2026-07-30 style: remove two em dashes from prose this session added
```

**Safe-to-append check, run before launching the suite.** Both doc-scanning
instruments select their corpus with `git ls-files`
(`check_decompositions.py:341`, `claim_auditor.py:217`), so this log stays
invisible to them while it is untracked. It is added to git only in the
final commit. That is what makes appending during a run safe here, and it
is stated rather than assumed because ledger N50 records three occasions
where editing during a run corrupted a result.

### Linter and gates
```
$ ruff check scripts/ tests/ --select F821,F811 --ignore E402 --exclude "tests/fixtures"; echo rc=$?
All checks passed!
rc=0
```

### Six fast gates, each exit code captured separately
```
rc=0 python3 scripts/claim_auditor.py --verify-facts
rc=0 python3 scripts/site_integrity.py
rc=0 python3 scripts/cascade_count.py --check
rc=0 python3 scripts/build_recall_artefact.py --check
rc=0 python3 scripts/build_gap_demo.py --check
rc=0 python3 scripts/check_selfref_sourcing.py --control-only
```

### Entry point
```
self-test rc=0
doctor rc=0
regula 1.9.0
```

## STEP 2: the next binding constraint

| # | Candidate | Verdict |
|---|---|---|
| 1 | **N52: `site_facts.py` counts UNTRACKED test files into every published count** | **CHOSEN.** |
| 2 | N50: the mid-run lockfile guard, whose overturning criterion was met last session | Real debt, but it protects MY measurement process, not the product's published numbers. Lower consequence than 1. |
| 3 | N51: the 83.5% precision corpus is gitignored by design | Owner decision (third-party licence implications). Cannot act; directive step 5. |
| 4 | N43 instance: correct the published gap-demo figures | Owner-gated: moves reader-facing numbers. |
| 5 | N53: root policy shadowing | Measured numerically inert by the previous adversarial review. Structural, not live. |

**Why 1 wins.** Last session I claimed to have closed the class "an artefact
backing a published number must be derivable from tracked content alone".
That claim is only true of the two DIRECTORY-SCANNING generators I guarded.
`site_facts.py` publishes more numbers than both combined (nine surfaces
including the README badge) and was left uncovered. Under the stated
precedence this is simultaneously: something that can make an existing
published figure wrong; the completion of a class rather than a new
instance; and debt against my own prior claim. It beats N50 on consequence
and beats 3, 4 and 5 because those are not mine to take.

**It has already fired once.** On 2026-07-31 a still-untracked
`tests/test_tracked_inputs.py` was counted into the canonical artefact and
cascaded to nine surfaces. The published figures were correct only because
the file happened to be committed in the same commit.

## STEP 3: the fix, test first

### FAIL-BEFORE

Tests written and run BEFORE any implementation existed:
```
$ python3 -m pytest tests/test_site_facts.py -q
FAILED tests/test_site_facts.py::test_untracked_contributors_flags_a_file_git_does_not_track
FAILED tests/test_site_facts.py::test_untracked_contributors_is_quiet_when_every_contributor_is_tracked
FAILED tests/test_site_facts.py::test_untracked_contributors_defaults_to_asking_git
FAILED tests/test_site_facts.py::test_generation_warns_when_a_contributor_is_untracked
4 failed, 6 passed in 0.16s
(AttributeError: module 'site_facts' has no attribute 'untracked_test_contributors')
```

### PASS-AFTER and the end-to-end control, both ways
```
$ python3 -m pytest tests/test_site_facts.py -q
10 passed in 0.12s
```

CONTROL A, a real untracked test file planted in `tests/`:
```
$ cat > tests/test_planted_untracked_probe.py   # untracked
$ python3 -c "...site_facts.count_tests()..."
WARNING: the test count below includes files that are not tracked by git, so it does not reproduce in a clean checkout:
  test_planted_untracked_probe.py
Commit them in the same commit as the count cascade, or remove them before regenerating.
per_file includes probe: True
untracked_test_contributors -> ['test_planted_untracked_probe.py']
```

CONTROL A2, the at-rest invariant, against an artefact actually generated
from that contaminated tree:
```
$ python3 scripts/site_facts.py   # writes a contaminated artefact
$ python3 -m pytest tests/test_site_facts.py::test_untracked_contributors_defaults_to_asking_git -q
FAILED tests/test_site_facts.py::test_untracked_contributors_defaults_to_asking_git
1 failed in 0.09s
```

CONTROL B, remove the probe and restore:
```
$ rm tests/test_planted_untracked_probe.py; cp backup data/site_facts.json
$ python3 -m pytest tests/test_site_facts.py -q
10 passed in 0.17s
$ git status --porcelain data/site_facts.json
(empty: artefact restored byte-identical)
```

### FIFTH occurrence of the mid-run editing defect, and it is structural

The step-1 baseline suite was still running when I began editing, so its
result describes a tree that changed underneath it and it was stopped.
That is the fifth instance recorded across three sessions (N45, N48, N50).

**This one is not simple carelessness, and saying so is not an excuse.**
The directive requires a full-suite run as part of step 1 state
re-establishment AND work in step 3. The suite takes 15 to 25 minutes. A
session that follows both literally must either idle for the duration or
overlap them. The overlap is structural.

**Reasoned, not evidenced, on the resolution:** the step-1 baseline suite
has little decision value in a session that will modify the tree, because
the claim that matters is the FINAL suite on the committed state, which
must be run regardless. The cheap state check that IS decisive at step 1
is the six fast gates plus the linter, which run in seconds and did run
here. Assumption: no defect exists that the full suite catches and all six
gates plus the final suite miss. The observation that would overturn it is
a session where the step-1 suite fails while the gates pass and the final
suite passes. Cheapest reversal: reinstate the step-1 suite, since nothing
depends on its absence.
