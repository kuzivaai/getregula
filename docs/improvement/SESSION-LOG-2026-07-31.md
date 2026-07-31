# Session log, 31 July 2026

Raw evidence record. Appended as each check ran, not reconstructed.
Assembled into the handover at the end; nothing here is retyped from memory.

## STEP 1: state re-established from the repository

### Working tree, branch, remote
```
$ date -Is
2026-07-31T01:19:04+01:00
$ git rev-parse --short HEAD; git rev-parse 'HEAD^{tree}'
cd6ff3c
c563ce7dc4b0dc252bb904faa6de4c506a6ef0de
$ git status --porcelain
?? docs/improvement/SESSION-LOG-2026-07-31.md
(empty above = clean)
$ git ls-remote --heads origin improvement/2026-08-programme
f286562c26cfdf9534c91ec304ae1aa423c0a581	refs/heads/improvement/2026-08-programme
$ git rev-parse main origin/main
6daacd2d92deb117286678dca2eede05ce50aa34
6daacd2d92deb117286678dca2eede05ce50aa34
$ git log --oneline main..HEAD | wc -l
104
```

**Correction to the annotation above, made immediately:** `git status --porcelain`
was NOT empty. It shows this log file itself as untracked (`?? docs/improvement/SESSION-LOG-2026-07-31.md`),
because the log is created before any work per the directive. The tree is otherwise
clean: no tracked file is modified. The "(empty above = clean)" line was a
template echo written before the command ran, which is exactly the kind of
pre-written conclusion this programme's measurement rules forbid. Recorded
rather than deleted.

### Recent commit log
```
$ git log --oneline -10 --format='%h %ad %s' --date=short
cd6ff3c 2026-07-31 docs(improvement): ledger row N48, the closing verification and its three attempts
346a494 2026-07-30 style: remove two em dashes from prose this session added
fcc24ff 2026-07-30 docs(improvement): ledger rows N46 and N47, the item 2 verdict and my own defect
f4e98d7 2026-07-30 fix(guard): self-protect the two scripts my stamp gave a sibling import
9224a42 2026-07-30 docs(improvement): un-backtick the session id the ledger guard refused
ea2ccf7 2026-07-30 docs(improvement): ledger rows N43 to N45, the F30 count, and one correction
c812ceb 2026-07-30 feat(guard): working-tree drift detection at every measurement point; cascade 2,585 to 2,595
839b031 2026-07-30 docs(improvement): record session 6, the held tree landed and Phase 1.7 done
4ee37b2 2026-07-30 feat(phase-1.7): scaffolding audit; correct the rules and commands it faulted
82266e9 2026-07-30 test(regressions): guards for the gap tool, endpoint scheme and unmeasured count; cascade 2,581 to 2,585
```

### Linter (the project's configured command)
```
$ ruff check scripts/ tests/ --select F821,F811 --ignore E402 --exclude "tests/fixtures"
All checks passed!
rc=$?
```

**Logging defect, corrected in place:** the `rc=$?` line above printed
literally because it sat inside a single-quoted echo, so the evidence record
carried a placeholder instead of an exit code. Re-run with the code captured:
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

## STEP 2: the contamination class, enumerated

The question my previous handover left explicitly untested: does the N43
contamination class extend beyond the one known fixture? Answered by
enumeration over every tracked fixture-bearing directory, not by sampling.

```
$ git ls-files | grep -E "fixtures?/" | sed 's|/[^/]*$||' | sort -u | while read d; do n=$(git status --porcelain --ignored=matching "$d" | wc -l); [ "$n" != "0" ] && echo "CONTAMINATED ($n): $d"; done
CONTAMINATED (3): tests/fixtures
CONTAMINATED (1): tests/fixtures/sample_compliant
CONTAMINATED (2): tests/fixtures/sample_high_risk

$ git status --porcelain --ignored=matching tests/fixtures
!! tests/fixtures/sample_compliant/.regula-baseline.json
!! tests/fixtures/sample_high_risk/.regula/
!! tests/fixtures/sample_high_risk/garak.regula.yaml

$ git status --porcelain --ignored=matching benchmarks/synthetic/fixtures
(empty: the recall corpus is CLEAN, 38 tracked files, no untracked or ignored)
```

**Finding: 3 contaminated paths across 2 fixture directories; the recall
corpus is clean.** Only `sample_high_risk` is scanned by an artefact
generator (`scripts/build_gap_demo.py:72`), so only it reaches a published
figure today. `sample_compliant` carries `.regula-baseline.json` and is
scanned by no script in `scripts/`, so it is latent rather than live.

```
$ grep -rn "sample_compliant" scripts/*.py
(no matches: no generator scans it)
$ grep -rn "sample_high_risk" scripts/*.py
scripts/build_gap_demo.py:18:`tests/fixtures/sample_high_risk` is tracked, so a clone reproduces the
scripts/build_gap_demo.py:72:FIXTURE = "tests/fixtures/sample_high_risk"
```

### The next binding constraint: ranked candidates

| # | Candidate | Verdict |
|---|---|---|
| 1 | **N43 in full**: clean the fixture, regenerate `data/gap_demo.json`, update the published pages (overall 9 to 6, Article 11 25 to 0) | **BLOCKED, owner-gated.** It changes reader-facing published figures. The prior session raised this boundary and it has not been sanctioned. Directive step 5 applies: arrive with a recommendation, do not act. |
| 2 | **Close the N43 CLASS**: make it impossible for an artefact generator to silently build a published figure from untracked or ignored inputs | **CHOSEN.** See reasoning below. |
| 3 | F25 / F30 scoping | Owner decision 3, unchanged since 28 July. Not mine to take. |
| 4 | N28, the wall-clock assertion in `test_redos_ast_patterns` | Real debt, but it is a latent flake that has not fired in any run this session or last. Lower consequence than a wrong published figure. |
| 5 | Programme queue: re-derive Trust and Detection (DIRECTIVE-v3 section 6) | Multi-session work. Cannot be finished under this budget, and the directive forbids starting what cannot be finished. |

**Why 2 beats 1.** The directive ranks "closing a class of defect" above
"fixing another instance of it", and ranks anything that makes an existing
figure wrong above new capability. N43 is both a wrong figure AND a class.
The instance (the wrong published numbers) is owner-gated; the class (a
generator that can silently read untracked inputs) is not. So the highest-
ranked action actually available is to close the class, which also means the
owner decision, whenever it is taken, cannot be undone by the same mechanism
recurring.

**Why 2 beats 4 and 5.** Precedence: "a cheap check on a high-consequence
uncertainty outranks an expensive improvement to something already working".
The enumeration above was that cheap check; it found the class is real and
has a second, latent instance (`sample_compliant`). Closing it now is
bounded and finishable; 5 is not.

## STEP 3: the fix, test first

### FAIL-BEFORE: the test run against the unfixed tree

Written and run BEFORE any implementation existed, per the directive.
```
$ python3 -m pytest tests/test_tracked_inputs.py -q
                "precondition failed: the planted file should be invisible to a "
FAILED tests/test_tracked_inputs.py::test_clean_fixture_reports_nothing - Att...
FAILED tests/test_tracked_inputs.py::test_untracked_file_is_reported - Attrib...
FAILED tests/test_tracked_inputs.py::test_ignored_file_is_reported - Attribut...
FAILED tests/test_tracked_inputs.py::test_ignored_directory_contents_are_reported
FAILED tests/test_tracked_inputs.py::test_restoring_the_directory_clears_the_report
FAILED tests/test_tracked_inputs.py::test_assert_inputs_tracked_raises_with_the_paths_named
FAILED tests/test_tracked_inputs.py::test_assert_inputs_tracked_passes_on_a_clean_target
FAILED tests/test_tracked_inputs.py::test_generators_call_the_guard_before_writing
8 failed in 1.18s
rc=1
```

### PASS-AFTER: same test file, after the implementation
```
$ python3 -m pytest tests/test_tracked_inputs.py -q
........                                                                 [100%]
8 passed in 0.79s
```

### Behaviour controls on the real generators

Write path REFUSES today, because the real fixture is contaminated. This is
the class closure: an unreproducible artefact can no longer be created.
```
$ python3 scripts/build_gap_demo.py            # write mode
REFUSED: tests/fixtures/sample_high_risk holds content that is not in the repository, so an artefact built from it would not reproduce in a clean clone:
  tests/fixtures/sample_high_risk/.regula/
  tests/fixtures/sample_high_risk/garak.regula.yaml
Remove it, or track it, before regenerating.
rc=2   (no traceback; the artefact is left byte-identical, verified by diff
        against a pre-run backup and by an empty git status on the file)
```

Check path WARNS and leaves the verdict alone, deliberately:
```
$ python3 scripts/build_gap_demo.py --check 2>&1 >/dev/null | grep -A3 WARNING
WARNING: tests/fixtures/sample_high_risk holds content that is not in the repository, so these figures do not reproduce in a clean clone:
  tests/fixtures/sample_high_risk/.regula/
  tests/fixtures/sample_high_risk/garak.regula.yaml
This check compares the artefact against a run on the SAME contaminated inputs, so it passing does not mean the published figures are reproducible. See ledger N43.
$ python3 scripts/build_gap_demo.py --check >/dev/null 2>&1; echo rc=$?
rc=0
```

The clean corpus is NOT spuriously refused:
```
$ python3 -c "...; print(untracked_inputs(FIXTURES)); assert_inputs_tracked(FIXTURES)"
recall corpus: benchmarks/synthetic/fixtures
untracked_inputs -> []
assert_inputs_tracked: PASSED (no refusal on the clean corpus)
```

### THIRD OCCURRENCE of the mid-run editing defect, by me, again

The full suite launched at the top of this session (01:19, commit `cd6ff3c`)
was still running when I created `tests/test_tracked_inputs.py`. Collection
moved 2595 to 2603 underneath it. That is the third instance in two
sessions of the pattern ledger rows N45 and N48 record.

```
$ cat s31_suite.exit  ->  STILL RUNNING
$ python3 -m pytest tests/ --collect-only -q | tail -1
2603 tests collected in 2.44s
$ canonical at that moment: 2595
```

**This matters because N48 named it in advance.** That row deferred building
a mechanical guard and stated: "The observation that would overturn the
deferral is a third occurrence." The third occurrence has now happened, so
the deferral is overturned by the criterion the ledger itself set, not by a
later opinion. The run was stopped rather than allowed to finish, because a
result describing a tree that changed underneath it describes no commit.

**Not built under this budget, and the reason is not convenience.** The
directive forbids beginning what cannot be finished to standard, and the
guard has a real design question that a rushed answer would get wrong: a
pre-commit refusal keyed on a runner lockfile would block legitimate commits
whenever a run is left orphaned, which is a worse failure than the one it
prevents. Recorded as the next session's first task with the criterion
already met, so it does not need re-litigating.

## STEP 4: adversarial check

A subagent was given ONLY the diff, the new test file, the two callers and
the module under change. It was given no reasoning, no summary and no
justification, and was told that finding nothing is a legitimate result.
It confirmed it ran every mutation on copies under /tmp and left the
repository byte-identical.

**It found ten issues, three of them HIGH. Its findings are reproduced
verbatim below, then dispositioned. It falsified my central claim.**

### Verbatim findings

**1. The wiring test is a substring grep, and the guard can be moved after the write with every test still green. (HIGH)**

`tests/test_tracked_inputs.py:134-147` asserts `"assert_inputs_tracked" in text`. Its name and docstring both claim "before writing"; nothing checks ordering, exit code, or that the artefact was not written.

Mutation, in a copy: I moved the `try/except assert_inputs_tracked` block from before `ARTEFACT.write_text(...)` to after it.

```
8 passed in 0.22s                       # tests/test_tracked_inputs.py
md5 before: c4c184449b170b4238ea5955cecf326d  data/gap_demo.json
rc=2                                    # "REFUSED" still printed
md5 after:  f43d37a566b2d0c8df8681397c22c474  data/gap_demo.json   <-- written
```

The contaminated artefact was rewritten and the suite stayed green. The class is held closed by two lines in two files whose behaviour no test exercises. (Positive control: with the real code, write mode gives rc=2 and the md5 is unchanged, so the guard does work today.)

Related: the test hardcodes two filenames, so it is a hand-built completeness claim, which `.claude/rules/measurement.md` 4c forbids. Other directory-scanning generators of tracked artefacts exist and are uncovered: `scripts/site_facts.py:238`, `scripts/build_delta_dataset.py:109`, `benchmarks/label.py:86`.

**2. The class is open on the most-published number in the repo: the 83.5% precision artefact. (HIGH)**

`benchmarks/results/random_corpus/PRECISION.json` holds `overall_precision: 0.835`, which is published on README, `docs/TRUST.md`, `docs/MODEL_CARD.md` and the site. Its corpus is gitignored by design:

```
.gitignore:130  benchmarks/results/random_corpus/*.json
.gitignore:138  benchmarks/results/app_*.json
$ ls benchmarks/results/random_corpus/*.json | wc -l   -> 54
$ git ls-files benchmarks/results/random_corpus | wc -l -> 4
$ ls benchmarks/results/*.json | wc -l                 -> 19
$ git ls-files benchmarks/results/*.json | wc -l       -> 7
```

`benchmarks/label.py:86` (`for result_file in sorted(RESULTS_DIR.glob("*.json"))`) writes the tracked `benchmarks/results/PRECISION.json` (0.368, N=446) from those 19, of which 12 are `!!` ignored. `scripts/claim_auditor.py:886-887` reads both PRECISION.json files as the authority for which precision percentages may be published. No guard, no test. This is the same defect the change describes, on a larger surface. It may be an accepted design (the .gitignore comment says "regenerable via rescan_corpus.py", and METHODOLOGY.json is tracked), but "an artefact that backs a published number must be derivable from tracked content alone" is not true of it.

**3. The diff's own published numbers are derived from an untracked file, through the one generator that was not guarded. (HIGH)**

`git ls-files tests/test_tracked_inputs.py` is empty. `scripts/site_facts.py` enumerates by working-tree glob (`tests_dir.glob("test_*.py")` at :238) and by `pytest --collect-only` over the working tree (:221), not by `git ls-files`, unlike `claim_auditor.py`, `f25_exposure.py`, `merge_blockers.py` and `check_decompositions.py`, which all use `git ls-files`. The resulting 2,603 / 1,902 were written into `data/site_facts.json` and cascaded to README (badge + table), SECURITY.md, TRUST.md (5 places), MODEL_CARD.md, site/about.html, site/llms-full.txt, site/regions/uae.html.

Measured with that file absent (scratch copy):

```
2159 tests collected, 1 error in 1.60s
ERROR tests/test_classification.py -> ModuleNotFoundError: No module named 'test_tracked_inputs'
```

The tracked, modified `tests/test_classification.py:43` imports it, so a tracked-content-only checkout does not merely count differently, it fails to collect. Unless `tests/test_tracked_inputs.py` is committed in the same commit, seven published surfaces become false claims. A compensating control does exist and fires (`python3 -m scripts.site_facts` returns rc=1, "refusing to publish an unmeasured test count", which reddens the CI claim-audit step), but it is pre-existing, is not part of this change, and is not what the change claims closed the class.

**4. The `--check` warning is untested, and its only automated consumer discards it. `build_recall_artefact --check` has no warning at all. (MEDIUM)**

Mutation: deleting the entire warning block from `scripts/build_gap_demo.py` leaves `tests/test_tracked_inputs.py` + `tests/test_gap_demo.py` at `18 passed in 3.64s`. `tests/test_gap_demo.py:64-71` runs the script with `capture_output=True` and asserts only `returncode == 0`, so under `pytest -q` the warning is never displayed; CI never runs `--check` at all (`.github/workflows/ci.yaml` invokes site_facts and claim_auditor only; the `--check` gates live in `.claude/commands/verify.md`). Observed behaviour: `check rc=0`, stdout `data/gap_demo.json matches a fresh run.`, warning on stderr. "Impossible to miss" is held in place by nothing.

Asymmetry: `scripts/build_recall_artefact.py:241-252` returns from the `--check` branch before reaching the guard, so a contaminated recall corpus passes `--check` silently, with no warning of any kind.

**5. `untracked_inputs()` also returns modified, deleted, staged and renamed TRACKED paths; the docstring, the function name and the refusal message all say otherwise, and no test covers it. (MEDIUM)**

`scripts/tree_guard.py:63` says "Return every untracked or ignored path under `path`", but :80-84 returns every porcelain line unfiltered. Probe against the real module:

```
2 modified tracked file:  ['fixtures/sample/app.py']
2b assert_inputs_tracked: REFUSED -> "...Remove it, or track it, before regenerating."
3 staged rename:          ['fixtures/sample/app.py -> fixtures/sample/renamed.py']
4 deleted tracked file:   ['fixtures/sample/app.py']
```

Confirmed on the real repo too: `untracked_inputs("scripts")` returns `scripts/build_gap_demo.py`, `scripts/tree_guard.py` (tracked, modified) alongside `scripts/__pycache__/`. Consequences: any uncommitted edit under a guarded fixture blocks regeneration with advice ("track it") that does not apply; a rename is reported as one bogus path `old -> new`; and ordinary build detritus (`__pycache__/`, `.ruff_cache/`) under a scanned directory would refuse permanently. `test_assert_inputs_tracked_passes_on_a_clean_target` only tests a pristine tree, so the "would block every legitimate regeneration" risk it names is untested for every non-pristine case.

**6. Silent no-op on a nonexistent path; wrong exception class outside a repo. (MEDIUM)**

```
10 nonexistent path: []                       # assert_inputs_tracked passes
11 path outside repo: RAISED CalledProcessError ... exit status 128
```

A typo'd or renamed path constant turns the guard into a no-op with no signal, which is measurement rule 4 (absent signal is not a passing signal). Outside a repository `_git`'s `check=True` raises `CalledProcessError`, which the callers' `except UntrackedInputError` does not catch. By the same mechanism, `build_gap_demo.py --check` now calls git unconditionally at the top of `main()`, so running the shipped script from a non-git checkout (`scripts/` is the PyPI package) tracebacks where it previously worked.

**7. Unguarded inputs remain for the very artefact that motivated the work. (MEDIUM)**

Both generators run the CLI with `cwd=REPO_ROOT`, and `scripts/policy_config.py:42-53` resolves `$REGULA_POLICY`, `./regula-policy.yaml`, `./configs/regula-policy.*`, `$HOME/.regula/regula-policy.*`, in that order. `/regula-policy.yaml` exists on this machine and is gitignored (`.gitignore:59`; `git check-ignore -v` confirms), shadowing the tracked `configs/regula-policy.yaml`. `assert_inputs_tracked(FIXTURE)` inspects only the fixture subtree and cannot see it; `$HOME/.regula/` can never be covered by a git-based guard. One-variable control (parked the root policy, re-ran both commands): outputs identical apart from the assessment timestamp, so this path is **numerically inert on this fixture today**; it is a structural gap, not a live wrong number.

**8. Documentation now contradicts the code in the same file. (LOW)**

`scripts/build_gap_demo.py:18` still reads "`tests/fixtures/sample_high_risk` is tracked, so a clone reproduces the output exactly", and :32 "The fixture scores 9%", while :176-183 of the same file now prints "these figures do not reproduce in a clean clone". Measured in a scratch copy with the fixture's `.regula/` and `garak.regula.yaml` removed: `Overall score: 6%`, `Overall compliance score: 6/100`, `Article 11 ... [ 0%] NOT FOUND`. Separately, `docs/TRUST.md:78` still asserts "Every number Regula publishes can be reproduced by anyone with a checkout of the repo"; the diff edits TRUST.md in five places without qualifying that sentence, while `site/index.html` and both locale pages publish 9/100 and 25%.

**9. Refusal messages are not always actionable, contrary to the docstring. (LOW)**

`tree_guard.py:71-72` claims the output "names something the reader can act on directly". Git C-quotes unusual names: `'"fixtures/sample/stray file.txt"'` and `'"fixtures/sample/caf\\303\\251.txt"'`. Untested.

**10. A tracked symlink pointing outside the repo passes the guard. (LOW)**

Probe case 9: `untracked_inputs` returns `[]` for a committed symlink to `/etc/hostname`. Content absent from a clean clone, guard silent. No such symlink exists in either guarded fixture; theoretical.

## Checked and found sound

- **The write-path guard genuinely works.** Control both ways in a copy: contaminated fixture gives `rc=2`, "REFUSED", artefact md5 unchanged; fixture cleaned gives no refusal.
- **The tests are not pinned to today's contamination.** Every test builds a throwaway git repo via `tempfile`; none reads the real fixture. They pass unchanged in a copy whose fixture has been cleaned.
- **They do fail if the implementation is reverted.** `git show HEAD:scripts/tree_guard.py` restored gives `7 failed, 1 passed` (the survivor is the substring-grep wiring test, finding 1).
- **`--ignored=matching` is load-bearing and correctly tested.** The precondition assertion in `test_ignored_file_is_reported` (plain porcelain reports nothing) holds.
- **`fresh = build()` running before the guard is not self-contaminating.** Verified that `regula gap` and `regula comply --all` write nothing into the target: the cleaned fixture stayed clean after both runs.
- **The "38 tracked files, nothing untracked or ignored" comment in `build_recall_artefact.py` is accurate.** `git ls-files | wc -l` = 38, `find -type f | wc -l` = 38, `untracked_inputs` = `[]`.
- **The 2595 to 2603 cascade is complete.** `git grep "2595\|2,595"` returns exactly one hit, a substring of a `uv.lock` package hash, i.e. zero stale published surfaces, and the lockfile was correctly not touched (rule 4d).
- **The "1,051 functions" figure is machine-derived, not asserted.** `tests/test_published_count_manifest.py:158-186` imports `test_classification` and counts bound aliases against the number stated in TRUST.md; it passes (`31 passed` with `test_source_of_truth.py`, `test_tracked_inputs.py`, `test_tree_guard.py`). I did **not** run the legacy runner to completion; that measurement was still executing when I finished.
- **Sibling-import rule satisfied**: both generators carry `sys.path.insert` (`build_gap_demo.py:69`, `build_recall_artefact.py:52`); `test_source_of_truth.py` green.
- **Edge cases that are fine**: empty untracked directory gives `[]` (git semantics, harmless); relative path resolution against `root=` works; pathspec metacharacters in a directory name do not break detection (`fix[1]/contam.ignoreme` still reported); no submodules in the repo, so the gitlink blind spot is theoretical.


### Disposition of every finding

| # | Sev | Disposition |
|---|---|---|
| 1 | HIGH | **ACCEPTED AND FIXED.** The reviewer is right and this falsified the central claim: the wiring test was a substring grep, and moving the guard after the write left all 8 tests green while the artefact was rewritten. Replaced with `test_generator_refuses_and_does_not_write_when_inputs_are_untracked`, which clones the repo, overlays the working-tree modules, plants a gitignored `.regula/registry/` inside the tracked fixture, runs the real entry point and asserts rc!=0, a `REFUSED` message, AND that the artefact bytes are unchanged. Its partner asserts a clean clone still builds, so a guard that refused unconditionally could not pass both. **The reviewer's exact mutation was then re-applied here and the new test caught it: `1 failed, 12 passed`, restored byte-identical, `13 passed`.** |
| 2 | HIGH | **ACCEPTED, NOT FIXED, RECORDED as ledger N51.** The 83.5% precision corpus is gitignored by design and is a larger instance of the same class. Fixing it is not a code change: it needs an owner ruling on whether that corpus should be tracked, which has licence implications (it is third-party code) and would change what the most-published number in the repository rests on. Directive step 5 applies. |
| 3 | HIGH | **ACCEPTED; resolved by construction, and the underlying gap recorded.** The new test file IS committed in the same commit as the cascade, so the published counts and the tracked corpus agree at every commit. The reviewer's deeper point stands and is recorded: `site_facts.py` enumerates by working-tree glob while four sibling instruments use `git ls-files`. That inconsistency is real, is NOT closed by this change, and is ledger N52. |
| 4 | MEDIUM | **ACCEPTED AND PARTLY FIXED.** The asymmetry is closed: `build_recall_artefact --check` now emits the same warning before its early return. The reviewer is also right that the warning is untested and that no CI job runs `--check` at all, so "impossible to miss" was overstated; the phrase is withdrawn. Recorded in N49 as a stated limit rather than left as an implied guarantee. |
| 5 | MEDIUM | **ACCEPTED AND FIXED.** A real bug: the function returned every porcelain line, so a modified tracked file tripped a guard whose advice was "track it". Now filters to the `??` and `!!` codes only, with `-z` so awkward names survive. Two new tests cover modified, deleted and renamed tracked files; one covers spaces and non-ASCII names (finding 9). |
| 6 | MEDIUM | **ACCEPTED AND FIXED.** A nonexistent target now raises `FileNotFoundError` instead of returning `[]`, because a typo turning the guard into a permanent pass is measurement rule 4. The non-git-checkout regression the reviewer identified in `--check` is fixed by catching broadly around the advisory call in both generators, so the warning can never break the command it advises on. |
| 7 | MEDIUM | **ACCEPTED, NOT FIXED, RECORDED as ledger N53.** The reviewer proved it numerically inert today by a one-variable control. A `$HOME/.regula/` policy can never be covered by a git-based guard, so this needs a different mechanism (running generators with a pinned, explicit policy path) and is a design change beyond this unit. |
| 8 | LOW | **ACCEPTED AND FIXED.** `build_gap_demo.py`'s header claimed a clone reproduces the output exactly; corrected in place, keeping the original reasoning and stating why it still failed. `docs/TRUST.md` section 3 now carries an explicit documented exception naming the figures, the cause and N43, instead of a blanket reproducibility claim contradicted by the site. |
| 9 | LOW | **ACCEPTED AND FIXED** as part of finding 5: `-z` output, plus `test_awkward_filenames_are_reported_unescaped`. |
| 10 | LOW | **ACCEPTED, NOT FIXED, RECORDED in N51.** A tracked symlink pointing outside the repo defeats a git-based guard. Theoretical (no such symlink in either guarded fixture) and the cheapest honest response is a recorded known limit rather than speculative code. |

**Nothing was disputed.** Every finding was either fixed or recorded with
the reason it was not. Three HIGH findings were raised; one (1) was a real
falsification of the central claim and is fixed, one (3) resolves by
committing correctly with its residue recorded, and one (2) is a genuine
larger instance that needs an owner ruling.
