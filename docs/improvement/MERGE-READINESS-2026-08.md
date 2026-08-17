# Merge readiness, `feat/engagement-fixes` into `main`

**Written 2026-08-17.** Measured at `ae59cd5d60e230b475fd5fc5f460cfd99337b9fc`,
tree `2c8b99b736079a19e6910b576108f0974250f104`, working tree clean apart from
the deliberately untracked `marketing/`.

This file exists so the owner can decide in one reading. It is not a
recommendation to merge without qualification. It states what merging would
ship, what has been run, what has never been run, and what I believe.

**Every exit code below was captured from `$?` after redirection to a file that
was deleted before the run started.** No edit and no commit was made between
launching a run and reading its result.

**Two things moved after this document was written, and are stated here rather
than edited into the figures above.** The sitemap defect in section 2b is
repaired in `60f9d82`, so `27_sitemap` is rc=0 at the session tip; the row is left
reading rc=1 because it is the measurement at `ae59cd5` and that is what the
commit range was assessed at. And `ba96a74` added seven tests, so the collected
count moved by seven from 2,960 and the runner count by seven from 1,285. **The
`2960 passed` line in section 3 is the run at `ae59cd5` and is correct at that
commit.** The final chain at the session tip is in the session handover.

**The new values are deliberately not written here as literals, and the first
draft of this paragraph did write them.** This file is inside the corpus
`test_count_literal_appears_nowhere_outside_the_manifest` measures, so quoting the
current count in it *creates* the violation. The full suite at `06f5ac6` failed on
exactly that, naming this file as the sole violation, after an isolated run of the
same guard had passed minutes earlier because the sentence had not yet been
written. **That is the fourth occurrence of this trap in this programme** (N109
twice, N111 once) and the second time the "a narrower run is not evidence about a
corpus the run itself is inside" lesson has had to be relearned by the person who
had just read it. Re-derive both figures with
`python3 scripts/cascade_count.py --check`, whose source is `data/site_facts.json`.

---

## 0. The verdict, first

**Not ready as it stood, and one commit away from ready on the mechanical
criteria.**

One CI check fails at the tip: the sitemap step of the `Claim auditor` job. It is
a generated artefact whose inputs four commits on this branch changed and which
none of them regenerated. It is repaired in this session. Without that repair the
merge turns `main` red on the first push.

**With that repair the branch passes every check this machine can run.** That is
a narrower statement than "ready", and section 8 says what no gate covers.

**The judgement a mechanical result cannot make** is in section 6. This branch is
not a polish backlog. It is the difference between a product that prints
`Compliance score: 2/100` and one that prints `Decision: insufficient_information`.
The published product does the first.

---

## 1. The commit range

`main..HEAD` is **26 commits**, 179 files changed, 14,096 insertions, 2,151
deletions.

```
e0e0709  2026-08-14  feat(site): engagement fixes from the 91-day analytics analysis
         13 files changed, 60 insertions(+), 122 deletions(-)
238d1f1  2026-08-14  fix(site): raise CTA button contrast to meet WCAG AA
         9 files changed, 9 insertions(+), 9 deletions(-)
6f5223d  2026-08-14  docs(brain): add BRAIN-FEED.md, the five-line status block the ops repo reads
         1 file changed, 28 insertions(+)
f008756  2026-08-14  feat(site): share one questionnaire flow across the three assess locales
         10 files changed, 956 insertions(+), 975 deletions(-)
b2f9f73  2026-08-14  fix(site): verify quoted law, make the claim guards locale-aware, cascade the count
         64 files changed, 856 insertions(+), 198 deletions(-)
c72e910  2026-08-14  chore(surfaces): regenerate the derived contract for the new assess-flow asset
         2 files changed, 19 insertions(+), 7 deletions(-)
080c0d3  2026-08-14  docs(ledger): record N107, the monolingual and markup-blind claim guards
         1 file changed, 78 insertions(+)
9e21501  2026-08-14  fix(docs): published CLI transcripts asserted conclusions the tool does not make
         32 files changed, 968 insertions(+), 167 deletions(-)
2385b63  2026-08-14  chore(quarantine): burn down six entries the transcript corrections removed
         2 files changed, 130 insertions(+), 37 deletions(-)
769f1e6  2026-08-14  docs(brain): refresh the feed for the transcript-integrity workstream
         1 file changed, 1 insertion(+), 1 deletion(-)
c86af70  2026-08-15  fix(metrics): a tracked artefact recorded cumulative totals as weekly ones
         17 files changed, 643 insertions(+), 84 deletions(-)
8331910  2026-08-15  docs(brain): refresh the feed for the metrics-integrity finding
         1 file changed, 2 insertions(+), 2 deletions(-)
5786666  2026-08-15  feat(site): published pricing, a sourced comparison table, and three integrity fixes
         37 files changed, 1549 insertions(+), 262 deletions(-)
a98ab06  2026-08-15  fix(counts): land the README and SECURITY cascade omitted from 5786666
         2 files changed, 3 insertions(+), 3 deletions(-)
d55ac68  2026-08-15  docs(errata): record two commits whose messages named files they do not contain
         1 file changed, 64 insertions(+)
b349531  2026-08-15  fix(pricing): reduce published prices to sit inside the measured market
         1 file changed, 4 insertions(+), 4 deletions(-)
4d922be  2026-08-15  fix(site): the site published two different prices, and now a guard compares them
         15 files changed, 97 insertions(+), 35 deletions(-)
c4216de  2026-08-17  chore(custody): commit the 15 August working tree, verified green and unsplittable
         89 files changed, 3364 insertions(+), 352 deletions(-)
3cbfa88  2026-08-17  fix(claims): no output or key may assert a compliance state, and the class was eleven sites
         32 files changed, 1079 insertions(+), 91 deletions(-)
c3f379e  2026-08-17  docs(ledger): close N125, and record six findings from the 17 August session
         2 files changed, 395 insertions(+), 3 deletions(-)
6462446  2026-08-17  fix(regulatory): South Africa had three withdrawal dates and the operative one was recorded nowhere
         20 files changed, 327 insertions(+), 70 deletions(-)
0c9031a  2026-08-17  docs(ledger): close N127 with the researched three-event timeline, record N134
         1 file changed, 175 insertions(+), 1 deletion(-)
bc36b66  2026-08-17  docs(brain): record the resolved South African withdrawal timeline in the feed
         1 file changed, 1 insertion(+), 1 deletion(-)
50e5dfd  2026-08-17  fix(claims): the front page published a transcript no instrument could read, and the class was five carriers
         40 files changed, 1787 insertions(+), 264 deletions(-)
7a84e9c  2026-08-17  refactor(fixtures): sample_compliant asserted the one thing this project does not determine
         9 files changed, 29 insertions(+), 29 deletions(-)
ae59cd5  2026-08-17  docs(ledger,research): close N130, N131 and N133, record N135 to N142, and land the research that was not done
         11 files changed, 2043 insertions(+), 4 deletions(-)
```

**None of these 26 commits has ever been through CI.** Owner decision 8 records
why: `.github/workflows/ci.yaml` triggers only on push and pull request to
`main`, and adding `workflow_dispatch` on this branch cannot enable dispatch
because GitHub reads the default branch's copy.

---

## 2. Every CI check, enumerated from the workflow files and run locally

The list was **not written from memory**. It is the itemisation printed by a
predicate over `.github/workflows/*.y*ml` that walks every job and step and
reconciles each total against its own itemisation before printing.

```
RECONCILED: 13 workflow files, 13 with jobs, 134 steps

SUBSET THAT FIRES ON A PULL REQUEST WHOSE BASE IS `main`
steps: 90  of which run: 40  uses: 50
RECONCILED: run + uses == total for the PR subset

workflows total 13 = fires-on-PR 6 + does-not 7
RECONCILED
```

A correction to that predicate is recorded rather than hidden. Its first version
treated `pull_request:` with an empty body as an absent key, because PyYAML parses
it to `None` and `.get` cannot tell the two apart. That wrongly excluded
`test-action.yml`. It now tests key membership before the value, and the figures
above are the corrected run.

**All three path-filtered PR workflows fire on this branch**, measured rather
than assumed:

| workflow | filter | changed files under it |
|---|---|---|
| `accessibility.yml` | `site/**`, `docs/accessibility/**` | 57, 2 |
| `site-integrity.yml` | `site/**`, `content/regulations/**`, four scripts, one data file | 57, 7, 3 |
| `benchmark.yml` | three `scripts/*.py`, `benchmarks/**` | 2 |

### 2a. The 30 run-steps reproducible here, each rc from its own file

Numbering is the predicate's, so a gap is a step that is not a check (a
`pip install`, an `actions/*` step, or an artefact upload).

```
03_bench_baseline            0     19_locale                    0
04_bench_score               0     20_determ_ctrl               0
05_bench_thresh              0     21_determ_check              0
06_bench_compare             0     22_html                      0
07_bench_synth               0     24_claimdiff                 0
09_runner                    0     25_sitefacts                 0
10_pytest                    0     26_verifyfacts               0
11_selftest                  0     27_sitemap                   1   <-- FAILS
12_doctor                    0     28_siteintegrity             0
13_selfscan                  0     29_comparison                0
14_quotes                    0     30_comparison_fresh          0
15_transcripts               0
16_questionnaire             0
18_ruff                      0
```

Summary lines, pasted:

```
[custom runner]  All tests passed!
[pytest]         2960 passed in 1138.64s (0:18:58)      FAILED lines: 0
[self-test]      6/6 passed in 0.1s
[doctor]         8 passed, 4 info
[security]       PASS  No unexpected findings in regula's own source.
[quotations]     quotation-check: 13 passage(s) judged, 13 verbatim, 0 mismatched
[transcripts]    transcript-check: 39 anchor(s) across 9 surface(s)
[questionnaire]  "passed": 177,  "failed": 0
[ruff]           All checks passed!
[locale-links]   locale-link-audit: 82 cross-language link(s) across 8 localised page(s); 0 unmarked
[determination]  determination-guard: scanned 556 tracked file(s) of 953, 0 finding(s)
[claim diff]     claim-auditor: scanned 56 file(s), 375 claim(s), 0 unsourced
[verify-facts]   claim-auditor --verify-facts: checked 154 fact references across 17 files
[site integrity] RESULT: OK (warnings, if any, are ticketed debt)
[comparison]     comparison-freshness: OK, stamp 2026-08-15 is 2 day(s) old, limit 90
```

### 2b. The check that fails, and why no local gate saw it

```
$ python3 scripts/update_sitemap.py && git diff --exit-code site/sitemap.xml
sitemap: 47 canonical URL(s) reconciled; 37 lastmod value(s) updated from git history
rc=1
```

**37 `lastmod` values in the committed `site/sitemap.xml` are stale.** They read
`2026-08-14` for pages whose last commit is 15 or 17 August. Four commits on this
branch changed pages under `site/` and none regenerated the sitemap.

This is **N76(a) recurring**. That entry recorded the same defect on PR #44,
established that a sitemap is a generated artefact of a site change exactly as
the count cascade is, and noted that `update_sitemap.py` is not one of the fast
gates so no local check can see it. The lesson was written down and the defect
recurred four commits later. **The gate set is still narrower than CI, and this
is the second instance in the same class.**

Regeneration is idempotent, verified rather than assumed: a second run reports
`0 lastmod value(s) updated` and leaves the file byte-identical
(`9c9eca7c91bbed8232aa0a6326f514c61b7ab0607ee1a0e04a84c69d31f53fe4` before and
after).

### 2c. Checks that cannot be run on this machine, and why

| check | why not |
|---|---|
| `ci.yaml::test` on Python 3.10, 3.11, 3.13 | only `python3.12` exists here; `3.10`, `3.11`, `3.13` and `3.14` all report ABSENT. **Three quarters of the test matrix is unreproducible locally.** |
| `pytest~=9.0` | CI pins `pytest~=9.0`; system `python3 -m pytest` is **8.4.2**, and the repo's `.venv` carries 9.1.1. The suite above ran on 8.4.2, which is the project's own documented verify command and is not the version CI installs. |
| `test-action.yml`, all 10 jobs | every one runs `uses: ./` and asserts on `${{ steps.regula.outputs.* }}`, which are GitHub Actions runtime expressions. **10 of the 40 PR run-steps are unreproducible.** |
| `codeql.yml` | requires the CodeQL action and GitHub's analysis service. |
| `regula-scan.yaml` | runs the composite action and uploads SARIF to GitHub code scanning. |
| `ci.yaml::deploy` | gated on `github.ref == refs/heads/main` and a push event. |

**30 of the 40 PR run-steps were reproduced and 10 were not**, and the 30 ran on
one of the four Python versions CI uses. 30 + 10 = 40, reconciled.

---

## 3. The full verification chain at the tip

Launched with the tree quiescent, each code from `$?` after redirection to a file
deleted before the run:

```
09_runner   = 0    All tests passed!
10_pytest   = 0    2960 passed in 1138.64s (0:18:58)
11_selftest = 0    6/6 passed in 0.1s
12_doctor   = 0    8 passed, 4 info
18_ruff     = 0    All checks passed!

commit before = ae59cd5   tree before = 2c8b99b
commit after  = ae59cd5   tree after  = 2c8b99b
```

`2960 passed` matches the canonical collected count of 2,960.

**The standing N28 caveat applies:** the suite carries assertions metered on CPU
time, so a full-suite result is one run, on one machine, at one load.

### 3a. The accessibility job, at both audited viewports

Its green status was previously inherited from 15 August. It has now been run at
this tip.

```
Audited 48 canonical pages at 2 viewport(s) (96 runs); 0 failed.
rc=0
runs: 96   pages: 48   viewports: {'desktop': 48, 'mobile': 48}
failures: 0   total passes: 2064   total incomplete: 61
pages with incomplete>0: 48
```

Tool versions match the workflow pins exactly: `playwright 1.62.1`,
`@axe-core/playwright 4.12.1`, `axe-core 4.12.1`.

**Positive control, run both ways on a real tracked page and restored
byte-exactly:**

```
sha before: 0326644531e7c28011515133617f7ec532154c6fdf6e85a53e6922c24b9c46c1

=== A: CLEAN ===
  /blog/blog-aicdi-governance-gaps.html @desktop: violations=0
  /blog/blog-aicdi-governance-gaps.html @mobile:  violations=0

=== B: PLANTED (tabindex removed from the N126 wrapper) ===
  @desktop: violations=0
  @mobile:  violations=1
      scrollable-region-focusable (serious) nodes=1 :: #mapping > div

=== C: RESTORE ===
sha after : 0326644531e7c28011515133617f7ec532154c6fdf6e85a53e6922c24b9c46c1
RESTORED BYTE-EXACTLY
  @desktop: violations=0   @mobile: violations=0

rc clean=0 planted=1 restored=0
```

The planted violation appears **only at 390px and not at 1400px**, which is
independent confirmation that N126's two-viewport widening is load-bearing rather
than decorative.

**Not conformance.** 61 `incomplete` results remain across all 48 pages: axe
reports those where a human must decide. Zero violations means zero violations of
the rules this tool evaluates at these two widths.

**One honesty note about the control's own conditions.** The first audit's HTTP
server survived its script's `trap`, so the control block's own server exited 1
and the control ran against the earlier one. That does not invalidate it: the
server reads from disk per request and the planted change was visible to it,
which is positive proof it was serving live content. The stray process was found
with `pgrep` and stopped.

---

## 4. What merging changes on public surfaces

Enumerated by predicate over `data/public_claim_surfaces.json`, the
delivery-derived inventory N62 built, intersected with `git diff --name-only
main..HEAD` and filtered to git-tracked paths per measurement rule 4b.

```
records                                  : 788
  active_product                         : 761
  active_product AND claim_capable       : 761
  distinct source paths                  : 108
  of those, git-tracked                  : 108
PUBLIC SURFACES THIS MERGE CHANGES       : 58

  web-page                   47
  repository-document         7
  machine-readable            3
  cli-option                  1
  cli-parser                  1

RECONCILED: itemised 58 == counted 58; union over kinds = 58
```

The 58 paths, in full:

```
README.md
SECURITY.md
docs/MODEL_CARD.md
docs/TRUST.md
docs/accessibility/README.md
docs/architecture.md
docs/benchmarks/PRECISION_RECALL_2026_04.md
scripts/cli.py
site/about.html
site/assess/de.html
site/assess/index.html
site/assess/pt-br.html
site/blog/blog-aicdi-governance-gaps.html
site/blog/blog-art50-code-of-practice.html
site/blog/blog-article-5-prohibited-practices.html
site/blog/blog-classify-ai-system.html
site/blog/blog-code-scanning-vs-questionnaires.html
site/blog/blog-does-ai-act-apply.html
site/blog/blog-en-standards-mapping.html
site/blog/blog-omnibus-decision-framework.html
site/blog/blog-omnibus-delay.html
site/blog/blog-omnibus-trilogue-failed.html
site/blog/blog-risk-tiers-in-code.html
site/blog/blog-scanning-10-ai-apps.html
site/blog/blog-scanning-5-frameworks.html
site/blog/blog-startups-ignoring-ai-act.html
site/blog/blog-static-analysis-ai-compliance.html
site/blog/writing.html
site/examples/sample-exec-summary.html
site/guides/article-14-human-oversight.html
site/guides/article-5-prohibited-practices.html
site/guides/article-50-transparency.html
site/guides/article-9-risk-management.html
site/guides/eu-ai-act-healthcare.html
site/guides/eu-ai-act-javascript.html
site/guides/eu-ai-act-python.html
site/guides/eu-ai-act-recruitment-hiring.html
site/guides/index.html
site/index.html
site/llms-full.txt
site/llms.txt
site/locales/de.html
site/locales/pt-br.html
site/pricing.html
site/privacy-de.html
site/privacy-pt-br.html
site/privacy.html
site/regions/brazil-ai-regulation.html
site/regions/colorado-ai-regulation.html
site/regions/regulations.html
site/regions/south-africa-ai-policy.html
site/regions/south-korea-ai-regulation.html
site/regions/uae.html
site/regions/uk-ai-regulation.html
site/sa-tracker.json
site/sample-report.html
site/terms-de.html
site/terms-pt-br.html
```

**A merge to `main` IS a publication.** `ci.yaml::deploy` runs on push to `main`
and deploys `site/` to GitHub Pages, so the 47 web pages above go live on the
merge, not on a later decision. That is the fact the owner is actually ruling on.

Three items on that list change what a reader is told, and are worth naming:

- **Pricing goes live.** `site/pricing.html` carries GBP 950 for a fixed-scope
  starter assessment and GBP 650 per day for advisory work (`b349531`,
  `4d922be`). `PAYMENT_GATE` is `NOT_ACTIVE` and no payment path is wired, so
  these are published prices with no way to pay them.
- **The README's only visual was removed** (`50e5dfd`) and replaced by a fenced
  transcript. The previous session flagged this as departing from its brief and as
  one commit to revert. It still needs a ruling.
- **A comparison table naming competitors goes live.**
  `docs/venture/research-2026-08/d-uk-comparative-advertising.md`, landed in this
  same range, sets out the BPMMR 2008 reg 4 conditions and the DMCCA 2024
  ss.226/227 cross-reference in force from 6 April 2025, including that the
  advertiser holds the evidential burden and that inadequate evidence may be
  treated as inaccuracy. **That research was written after the table shipped**, and
  whether the table meets reg 4(d)'s "material, relevant, verifiable and
  representative" test has not been assessed against it.

---

## 5. Known-open items this merge would ship

**The ledger's own count understates, and the cause is a defect in its
enumerator rather than in anyone's reading.**

```
$ python3 scripts/ledger_status.py
ledger-status: 81 entries in LEDGER.md
  OPEN     15
  PARTIAL  25
  CLOSED   41
```

`ledger_status._HEADING` is `^#{2,3} \*?\*?N(\d+)[.\s—-]`, so it matches prose
entry headings only. **Section 1 of the ledger is a markdown table of 74 rows and
carries no `**State:**` field at all**, so none of it is in that population.

```
section-1 rows                                   : 74
rows whose Status STARTS 'OPEN'                  : 15
  of those, the same cell later says 'CLOSED'    : 2 -> ['N28', 'N53']
RECONCILED: 15 = 2 contradicted + 13 not contradicted
```

**Neither 15 nor 30 is the answer, and that is the finding.** The section has no
field to enumerate, which is exactly the condition N116 ended for the prose
entries and never extended to the table. Recorded as **N143**.

### 5a. The 15 OPEN prose entries

```
N66  Validation-readiness decision pack remains externally disabled
N71  Stage A linkage and re-identification controls remain pre-execution
N79  Unresolved browser answers can reach a handable regulatory artefact
N80  The epistemic defect is not confined to the questionnaire
N81  Decision engines are copied and contractually divergent
N82  Adapter boundaries do not fail closed
N83  Assurance targets agreement with current artefacts more often than validity
N84  Product surface exceeds validated evidence
N85  The binding constraint is an absent executable meaning contract
N86  N78 is not closed on the current tree
N87  Current standards status must separate publication from OJ citation
N88  Remediation sequence and repository/external boundary
N98  Generator status after this work
N99  Verification and release state
N132 The pricing-transparency evidence base does not exist at source
```

**N132 bears directly on section 4.** All three statistics supplied for the
pricing decision failed at source, one of them attributed to a firm that had wound
down before the report could exist. The prices go live anyway. That is not an
argument against the prices; it is a statement that they rest on no evidence that
survived checking.

### 5b. The 13 section-1 rows reading OPEN and not later contradicted

```
F25   CITATION_WORDS accepts ordinary prose as provenance
F30   Allowlist entries suppress the whole paragraph, not the matched claim
N6    site/llms-full.txt is a manifest surface the claim auditor never scans
N7    SHORT_DURATION exempts published performance claims
N10   NUMERIC_CLAIM misses claims whose unit word is not adjacent
N11   67 of 89 test files are not wired into the custom runner
N12   A published-surface gate condition would turn main red (168 findings)
N13   The residue under both gate conditions is 15 and not all fixable
N14   main carries 168 unsourced claims on published surfaces today
N35   A CSS class name sources published prose
N36   An HTML section with no blank lines is one paragraph
N51   The 83.5% precision corpus is not reconstructible
"Gate scope repair"   --diff-base scans whole files rather than introduced claims
```

**N14 is the one to read before merging.** It is a statement about `main` as it
already is: 168 numeric and superlative claims on main's published surfaces carry
no in-paragraph provenance. Merging neither creates nor removes that.

### 5c. Items no State token covers, carried forward

The `demos/regula-cli.cast` disposition (hand-authored, generated by nothing,
checked by nothing); the claim-auditor coverage-register question; `CLAUDE.md`
remains gitignored, reachable by no gate and absent from a fresh clone; **`main`
is unprotected**; and the standing owner items (DPVCG post, raters 2 and 3,
Zenodo DOI, BSI ART/1, **GSC re-auth**, private remote, the 20 August
`prEN 18229-1` enquiry window).

---

## 6. The installable product against this tree

This is the section that changes what the branch is for.

### 6a. The command and flag surface is identical

Measured by building the real parser on both sides and reading the subparser
choices, not by parsing help text:

```
tree      : 62 commands
installed : 62 commands
only in tree      : []
only in installed : []
common            : 62
RECONCILED both sides

FLAG SURFACE: 0 of 61 commands differ in the option strings their --help prints
```

**A prospect comparing `--help` would see no difference at all.** That makes the
behavioural divergence harder to notice, not easier.

### 6b. The behaviour differs, and the difference is this project's hard rule

`regula-ai 1.9.0`, cold `pip install` into a clean virtual environment (1.15s,
zero dependencies), run on a third-party repository:

```
$ regula                                          # PyPI 1.9.0
  Files scanned:          6
  Compliance score:       2/100
  Highest risk tier:      high_risk
```

```
$ python3 -m scripts.cli                          # this tree, same repository
  Files scanned:          8
  Detector findings locate code for review. They do not establish legal applicability.
  ...
Decision: insufficient_information
Model: 2026-08-12.4
Rule resolution: unresolved
Facts needed to resolve the next decision: 2
  - is_ai_system: Does the subject meet the governing law's definition of an AI system ...
  - jurisdiction_in_scope: Does this jurisdiction's territorial and operator scope apply?
```

```
$ regula check .                                  # PyPI 1.9.0
  Verdict: HIGH-RISK
  Your project shows indicators of high-risk AI under EU AI Act Annex III.
  If confirmed high-risk (Article 6), Articles 9-15 obligations apply before the enforcement deadline.
  ...
  Confidence scores: 0-100 (higher = more indicators matched)
```

Located exactly, by grep over both trees:

```
installed  scripts/cli.py:178       print(f"  {'Compliance score:':<24}{gap_score}/100")
installed  scripts/cli_scan.py:525  print(f"\n  {verdict_color('Verdict')}: {verdict_color(verdict_tier)}")

tree       scripts/verify_transcripts.py:117  "Verdict: HIGH-RISK": "replaced by the decision
                                              block; asserted a tier the tool does not determine"
```

**The strings this tree's own guard lists as retired, and asserts unreachable, are
reachable in the product on PyPI.** `retired_markers_are_unreachable()` is correct
about the tree, and the tree is not what anyone has.

```
scripts/decision_kernel.py in installed 1.9.0 : ABSENT
files containing 'insufficient_information'
  installed 1.9.0 : 0
  this tree       : 4
```

**The entire epistemic kernel is absent from the installable product.** N94 and
everything downstream of it exists only here.

### 6c. Output shape of the commands a demo would use

| | PyPI 1.9.0 | this tree |
|---|---|---|
| `check --format json`, `data` | a **list** of findings | a **dict** with `decision`, `detector_findings`, `jurisdiction_decisions` |
| finding's tier field | `tier` | `detector_class` |
| priority label | `[BLOCK] [ 88]` | `[BLOCK] [priority 88]` |
| bare `regula` headline | `Compliance score: N/100`, `Highest risk tier` | `Decision: insufficient_information` and the facts needed |
| `check` headline | `Verdict: HIGH-RISK` plus an obligation sentence | decision block, no verdict |
| `comply` headline | `Overall compliance score: 2/100` | not compared; the two above are decisive |
| trailer | `Confidence scores: 0-100` | detector-priority framing |

### 6d. What the consultant would be wrong about

If she demonstrates from this tree and the prospect installs from PyPI, she will
have shown a tool that declines to make a determination and the prospect will
install one that prints a compliance score out of 100, a verdict and a risk tier.
**Every honesty claim in the pitch would be false of the artefact the prospect
holds.** That is the strongest argument in this document for releasing rather than
merely merging.

---

## 7. Release readiness

**Prepared, not released. Nothing has been pushed, tagged or published.**

### 7a. What a release would publish

The 26 commits in section 1: the epistemic decision kernel and its conformance
corpus; the removal of `Verdict:`, `Compliance score:` and `Confidence scores:`
from every output path; the eleven-site compliance-state closure (N129) with its
guard and CI job; the scan-cache key fix that closes a false-negative class
(N113); the two-viewport accessibility gate; the South African withdrawal-date
corrections; the metrics-label correction; and the `regula plan --done` refusal
(N119).

### 7b. What breaks for anyone on 1.9.0

1. **`check --format json` changes shape.** `data` goes from a list to a dict.
   Any consumer indexing `data[0]` breaks.
2. **The finding tier field is renamed** from `tier` to `detector_class`.
3. **The `ai-codegen` payload key is renamed** to the observable it measures, with
   no alias, recorded in N129 as a deliberate breaking change.
4. **`regula plan --done` now refuses with exit 2** (N119). It previously printed
   `Marked <id> as completed.`, exited 0, and wrote a status file for a task no
   plan contained.
5. **Bare `regula` no longer emits a compliance score or a risk tier** (N105).
6. **`regula badge` no longer renders a green EU AI Act compliance badge** (N129).
   Any third-party README embedding it changes appearance and meaning.
7. **The scan-cache schema moves v4 to v5** (N113), invalidating every cached
   entry, so the first run after upgrade is a cold scan. Section 9 says what that
   costs.

### 7c. What the version number should be

**1.10.0 is wrong. This is 2.0.0.**

`docs/VERSIONING.md` is the project's own decision record and declares a public
API and a deprecation policy. Items 1, 2 and 3 are removals and renames in a
declared output contract with no alias and no deprecation period. Item 4 changes
an exit code from 0 to 2. Under SemVer each alone requires a major bump.

The counter-argument, stated because it is real: 1.9.0 was itself a corrective
realignment after the 1.7.x line shipped features in patch releases six times, and
a second discontinuity within three weeks reads as churn. **That is a presentation
cost, not a correctness argument**, and this project's own remediation precedent
was to take the correct number rather than the comfortable one.

One consequence the owner should price in: a user who pins `regula-ai<2` keeps a
product that makes exactly the claims this project says it must not make. Whether
that warrants a deprecation note against 1.9.0 is an owner call and is
outward-facing.

`tests/test_source_of_truth.py` enumerates the enforced version set and fails on
drift, so the bump itself is mechanical. The ruling is not.

### 7d. Release preconditions not met

- The sitemap check must be green (section 2b). Repaired this session.
- `release.yml` runs only on a tag push and its `verify` job installs from PyPI
  and smoke-tests `--version`, `self-test`, `demo` and `dpv`. **None of that has
  been exercised for this tree.** v1.7.6 shipped `regula dpv` broken because
  source tests do not catch packaging bugs; no wheel has been built here.
- **`main` is unprotected.** A release from an unprotected default branch has no
  review gate at all.

---

## 8. What no gate covers

Stated per measurement rule 5, because a green gate set is what a session reads as
a trustworthy tree, and this branch has now produced two counterexamples.

1. **CI itself.** No commit here has been through it, and section 2b is the second
   demonstration in the same class.
2. **Three of the four Python versions.** Only 3.12 exists here.
3. **The pytest version CI installs.** The suite ran on 8.4.2; CI pins `~=9.0`.
4. **The composite action.** All 10 `test-action.yml` jobs are unreproducible
   locally, and that workflow is what a GitHub Marketplace user runs.
5. **Packaging.** No wheel built, no clean install from a built artefact. The
   clean install in section 6 is of **1.9.0 from PyPI**, not of this tree.
6. **Real-world accuracy.** Untested over 0 human-labelled repositories. The only
   measured commercial benchmark result is **0/40 against a transparent baseline at
   40/40**, diagnostic over constructed correlated families, not real-world
   accuracy.
7. **Any human reader.** No comprehension, usability or trust testing has ever
   been run on any surface of this project.
8. **The default scan's own scope.** Section 9.

---

## 9. What the buyer's path found

Full record in the session handover. Listed here because it bears on the ruling.

**Hashes in this section name objects in the third-party repository beside them,
never in this one.** `docs/improvement/LEDGER.md` carries a guard asserting that a
backticked hash resolves here, which is why the same commits appear there without
backticks (N39c).

- **The scan does not disclose what it declined to read.** On
  `ageitgey/face_recognition` at `9f3061a`, `regula check . --scope all` reports
  `Files scanned: 6` and 3 high-risk findings. Pointed at each subdirectory the
  same tool reports **14** high-risk findings over 28 files, because `examples`,
  `example`, `demos` and `demo` are in `SKIP_DIRS` and 23 files live under
  `examples/`. **11 of 14 findings, 79%, are invisible at the default invocation
  and nothing in the output says so.** `SKIP_DIRS` is byte-identical between the
  installed product and this tree, so this is current.
- **`regula check` never fills the cache it reads.** On `open-webui/open-webui` at
  `01f4282`, one variable: with the cache emptied, three consecutive
  `regula check .` runs left it at 2 bytes and the third took **40.7s**; one bare
  `regula` wrote 59,079 bytes and the next `check` took **4.0s**. `cmd_check`
  passes `min_tier='limited_risk'` and `_cache_put` refuses to write on a partial
  scan. N113 documents the mechanism, not this consequence. **A prospect who runs
  the documented `regula check .` pays the cold cost on every run, forever.**
- **A false positive is the headline finding on a major vendor's repository.** On
  `vercel/ai` at `86892f3`, the highest-priority finding across 2,408 files is
  `[BLOCK] [ 98] ... Private key detected in AI system code` at
  `packages/google-vertex/src/edge/google-vertex-auth-edge.ts:59`. That line
  assigns a constant holding the PEM header text that marks the start of a private
  key block, and is used to parse a key supplied at runtime. There is no key in
  the file. The remediation offered is to use an SSH agent, which is advice for a
  different situation. **Not changed here**: altering a detection pattern moves the
  published precision and recall figures and requires re-measuring the corpus.
  *(This project's own pre-tool hook blocked the first attempt to write this
  paragraph, on the same string. The hook is working as designed and the string is
  described rather than quoted, as `AGENTS.md` prescribes.)*
- **The tool asks two questions and discards the answers.** `regula` reports
  `insufficient_information` needing `is_ai_system` and `jurisdiction_in_scope`.
  `regula assess --answers yes,yes,no,yes,no` answers exactly those, exits 0, and
  its own Next steps say `regula check .`. Running it again returns the identical
  block. Nothing is written to the project or to `~/.regula`. **Demonstrated in
  both directions.**
- **345 seconds on a first scan of `vercel/ai`.** Progress output exists but is
  gated on `sys.stderr.isatty()`, so it does appear for a human at a terminal. My
  first framing of this as "no progress output" was **wrong and is withdrawn**; a
  pty re-test showed `Scanning... 300 files` and `Scanned 344 files`.

---

## 10. Contradictions a reviewer should see rather than have resolved

**One, carried from the previous session.** Its section 1 says Phase 0 COMPLETE;
its section 11 says `references/*.yaml` currency is policed by nothing and the
`site/llms-full.txt` mirror drift is open (N139 PARTIAL). Both are true under
different readings: the class of published transcripts and retired framings is
closed and gated at every surface it was live on, and the maintenance mechanism
for two of those surfaces does not exist.

**Two, carried from the previous session.** Its section 5 says `.svg` should not be
in the claim auditor; its section 6.3 says a claim-capable surface the auditor
cannot read is a hole. The coverage register (N138) is the attempt to hold both. A
reviewer may reasonably think the auditor should have been widened and its false
positives dispositioned instead.

**Three, which is mine and is new.** Section 0 says the branch is one commit from
ready on the mechanical criteria. Section 8 lists eight things no gate covers,
including packaging, the composite action, three quarters of the test matrix, and
any human reader. Both are true and they are not the same statement. **"Passes
every check this machine can run" is a much smaller claim than "ready to merge",
and the gap between them is section 8.**

---

## 11. What would make it ready

1. **Commit the regenerated sitemap.** Done this session.
2. **Open a pull request.** The only way CI can ever run on these commits (owner
   decision 8), and an owner action because it is outward-facing. Items 1 to 4 of
   section 8 are answered by that and by nothing else available here.
3. **Build the wheel and clean-install it**, then run the features that changed.
   Source tests do not catch packaging bugs; v1.7.6 is the precedent.
4. **Rule on the README visual** (section 4). One commit to revert.
5. **Rule on the version number** (section 7c). I believe 2.0.0.
6. **Rule on the default scan's scope** (section 9, first item, and
   `DEFAULTS-RECOMMENDATION-2026-08.md`).

---

## 12. What I believe

**Merge and release together.** Not because the branch is finished, which it is
not, but because the alternative is worse in a specific way: for as long as this
sits unpushed, the product a prospect can install prints `Compliance score: 2/100`
and `Verdict: HIGH-RISK`, and this repository's hard rule says it must not. The 26
commits are not polish. They are the removal of a compliance determination from a
tool that is sold on not making one.

**I would not release without opening the pull request first**, because four of
the eight uncovered areas in section 8 are answered by CI and by nothing that can
be run here.

**And I would not present the merge as making the product ready.** It makes the
product honest. Readiness is section 8 item 6, and that remains untested over zero
human-labelled repositories.

---

## 13. Addendum, 2026-08-17: the build, the parity, and the release verdict

**Appended rather than folded into the sections above**, because those are the
measurement at `ae59cd5` and this is a different tree. Measured at `1ddc614`.

### 13.1 A wheel was built from this tree and installed, which had never been done

The clean install recorded in section 6 is of **1.9.0 from PyPI**. Section 7d
named this as an unmet precondition. It is now met.

```
$ python3 -m build --outdir <dist>
rc=0        regula_ai-1.9.0-py3-none-any.whl, regula_ai-1.9.0.tar.gz

$ <fresh venv>/bin/pip install --no-index --no-cache-dir <dist>/regula_ai-1.9.0-py3-none-any.whl
rc=0        Successfully installed regula-ai-1.9.0

$ <venv>/bin/regula --version        rc=0   regula 1.9.0
$ <venv>/bin/regula self-test        rc=0   6/6 passed
$ <venv>/bin/regula doctor           rc=0
$ <venv>/bin/regula demo             rc=0
$ <venv>/bin/regula dpv --help       rc=0
```

`--no-index` is load-bearing: the package came from the file and not from PyPI.
The console script's interpreter is the venv's, checked structurally rather than
assumed, and every measured run used a working directory outside this repository
so no route existed by which the tree could answer for the artefact.

### 13.2 Parity, in three layers, each by predicate

**Layer 1, command and flag surface**, by constructing the real argparse parser
on both sides and reading the subparser choices, not by parsing help text:

```
tree      : 62 commands   installed : 62 commands
only in tree : []         only in installed : []
FLAG SURFACE : 0 of 62 common commands differ in option strings
NESTED SUBS  : 0 of 62 common commands differ in nested subparser choices
root options : tree 8, installed 8, identical True
```

**Layer 2, module presence**: the decision kernel, the CLI entry point and the
transitive closure of everything they import, computed from the TREE and checked
against the artefact, because computing it from the artefact would shrink the
closure to fit the defect. 99 of 99 present; all 150 `scripts/*.py` present;
every required runtime data file present.

**Layer 3, behaviour**, same commands, same pinned repository, both sides, cold
cache and isolated HOME per invocation:

```
target: ageitgey/face_recognition at 9f3061aaeed9a8756d2c970f5dfe066617a8281d
         (a commit in THAT repository)
commands compared : 7      DIFFERENCES : 0
```

**Total differences across all three layers: 0, reconciled against itemisation.**

**The comparison discriminates**, which is the control that stops this being a
blank gate. The same layer-3 harness pointed at `regula-ai==1.9.0` from PyPI
returns **7 of 7 commands differing**, naming `Verdict: HIGH-RISK` against
`Decision: insufficient_information`, a JSON `data` list against a dict, and a
badge labelled `EU AI Act` against one labelled `regula`.

### 13.3 One packaging defect was found by construction, and fixed

`regula api-server` registers as "Start the REST API server with web dashboard"
and serves `scripts/dashboard/index.html` at `/v1/dashboard`. No package-data
pattern named it. The tree answered that endpoint with 52,443 bytes of HTML and
the installed wheel with 302 bytes of JSON advising the user to place a file
inside site-packages. Same class as the 1.7.6 `regula dpv` break. Fixed in
`e63cd13`; the rebuilt wheel now serves bytes identical to the tree's. See
ledger N154.

### 13.4 The guards can now be run against an installed artefact

`scripts/verify_installed_artefact.py`, ledger N154. Against the wheel built
from this tree: **0 findings across 7 checks**. Against `regula-ai==1.9.0` from
PyPI: **23 findings**, being 3 absent kernel modules, 3 absent data files, 8
compliance-state assertions in shipped source, and 9 retired markers emitted by
the live CLI. That is N144 produced by an instrument rather than by hand, and it
is the only mechanism here that could have caught it before a user did.

### 13.5 Correction to section 2's workflow tally

Section 2 prints `workflows total 13 = fires-on-PR 6 + does-not 7`. Re-derived
at this tip with the same corrected predicate over unchanged workflow files, the
answer is **7 + 6**. Every other figure in that block is the corrected one and
reconciles. Recorded as ledger N160; nothing downstream changes, because the
merge decision rests on the step-level figures.

### 13.6 The ten checks a merge would be trusting rather than knowing

The ten are the `test-action.yml` verify steps, one per job:
`test-no-findings`, `test-high-risk-warn`, `test-high-risk-fail`,
`test-sarif-output`, `test-outputs`, `test-pinning-threshold`, `test-warn-tier`,
`test-defaults`, `test-fail-closed-bad-path`, `test-manifest-present`. Each runs
`uses: ./` and asserts on `${{ steps.regula.outputs.* }}`, GitHub Actions
runtime expressions with no local equivalent. That workflow is what a Marketplace
user runs.

Four further classes, not among those ten and equally unrunnable: three quarters
of the Python matrix (only 3.12 exists here, verified by command); the pytest
version CI installs (CI pins `~=9.0`, the suite ran on 8.4.2); CodeQL and the
Regula scan upload, which need GitHub services; and `ci.yaml::deploy`. Ledger
N161 states what each means for a merge.

### 13.7 Release verdict

**2.0.0, and I agree with the previous session's reasoning.** The two pieces of
evidence the question turns on:

- **The `ai-codegen` payload key was renamed with no alias** (N129). A consumer
  reading that key gets a `KeyError`, not a changed value, and no deprecation
  period was offered.
- **The default output shape changed.** `check --format json`'s `data` moves
  from a list to a dict, and the finding tier field is renamed `tier` to
  `detector_class`. Any consumer indexing `data[0]` breaks. This is now measured
  rather than inherited: the layer-3 harness reports the difference by name,
  `tree='  "data": {'` against `installed='  "data": ['`.

Either alone requires a major bump under the deprecation policy
`docs/VERSIONING.md` declares. `regula plan --done` moving from exit 0 to exit 2
(N119) is a third.

**Two things this session adds to that reasoning.**

First, **the fact-store flags are additive and change nothing about the version
question**: `--fact`, `--facts-file`, `--no-facts`, `--list-facts` and
`--save-facts` are new flags on existing commands, the command count is
unchanged at 62, and no existing invocation behaves differently.

Second, **the scan-cache schema moves v5 to v6** and invalidates every existing
entry, so the first run after upgrade is cold. That is not a breaking change to
a declared contract, it is a performance characteristic, and it is stated
because a user who upgrades and sees a slow first scan should be able to find
out why.

**Corrected in section 14: the schema now moves v5 to v7**, for a second and
different reason. The sentence above is left as the measurement at `09ec405`.

**The counter-argument, restated because it is real and has not gone away.**
1.9.0 was itself a corrective realignment three weeks ago, and a second
discontinuity reads as churn. That is a presentation cost, not a correctness
argument, and this project's own precedent is to take the correct number.

**Preconditions now met that were not:** a wheel exists, it installs from the
file into a clean environment, and its parity with the tree is measured in three
layers.

**Preconditions still not met:** `main` is unprotected, and no commit on this
branch has been through CI. Both are owner actions.

### 13.8 What is still true from section 8

Everything in section 8 except item 5. Packaging is now covered. CI itself, three
of four Python versions, the pytest version CI installs, the composite action,
real-world accuracy over zero human-labelled repositories, and any human reader,
all remain uncovered. **"Passes every check this machine can run" is still a
much smaller claim than "ready to merge", and the gap is still section 8.**

---

## 14. Addendum, 2026-08-17 (fifth session): one more cache defect, same class

**Appended rather than folded in**, for the reason section 13 gives. Measured at
`09ec405`, tree `0fa38947d118716dabcc8ae36702da10368e6022`.

### 14.1 What was found

The previous session closed section 13 with an open question it had looked at and
not answered: whether `min_tier` is the only `scan_files` parameter that changes
what a per-file cache entry contains. **It is not.** `respect_ignores`, the flag
behind `regula check --no-ignore`, is threaded into `_parse_suppression_rules`
(`scripts/report.py`) and decides whether a finding is emitted with
`suppressed: True`. It was absent from the cache key, so both settings of a
user-facing flag shared one entry.

Measured on an isolated fixture, `REGULA_CACHE_DIR` per condition, one variable
moving:

```
A. cold cache, --no-ignore   suppressed=False   exit 1   <- correct
B. cold cache, default       suppressed=True    exit 0   <- correct
C. B's cache,  --no-ignore   suppressed=True    exit 0   <- WRONG
```

C is a **silent false negative** on the one command whose purpose is to
disregard the annotation. The reverse order is a **false positive**: a scan
warmed by `--no-ignore` makes a later default scan report a finding the file's
own `# regula-ignore` silences. Both directions were reproduced before the fix
and both are asserted by tests. Ledger **N163**.

### 14.2 What the fix changes for a release

- **The scan-cache schema moves v4 to v7 for anyone upgrading from the published
  product**, and that composite is worth stating because no single sentence in
  this file said it. Section 7b records `v4 to v5` (N113) at `ae59cd5`; section
  13.7 records `v5 to v6` (N147); this session adds `v6 to v7`. Each increment is
  correct about itself. **The number a user experiences is the composite**, and it
  is measured rather than added up: `git show main:scripts/scan_cache.py` and the
  installed `regula-ai==1.9.0` both read `_CACHE_SCHEMA = f"v4:..."`, and the
  branch tip reads `v7`. v5 and v6 are states that have only ever existed on this
  unpushed branch. Nothing migrates at any step, for the reason every bump gives:
  an entry written under an unsound key cannot be told from a sound one
  afterwards. The user-visible consequence is one cold scan after upgrade.
- **A second cost, new and worth stating**: two scans of the same tree that
  differ in `--no-ignore` now each pay a cold scan, because they no longer share
  entries. That is the correct trade: it buys a slow right answer in place of a
  fast wrong one, which is the same call section 13 made for `min_tier`.
- **Nothing else in section 13.7's reasoning moves.** This is not a change to a
  declared output contract, so it does not add to the 2.0.0 case and does not
  weaken it. **2.0.0 remains the verdict.**

### 14.3 The durable half

The one-line fix would have been to add the flag to the key. What landed instead
is `report.CACHE_KEY_SCAN_PARAMS` and `report.CACHE_EXEMPT_SCAN_PARAMS`, which
classify **every** parameter of `scan_files` as either in the key or provably
unable to change an entry, each with its reason, plus a test that reads
`inspect.signature(scan_files)` and fails if a parameter appears in neither.

That matters because this is the third instance of one class: N112 (classifiers
derived from the full path), N147 (scan completeness), N163 (scan parameters).
Each was found by someone happening to look. **A parameter added after today
cannot be forgotten the way this one was**, because there is now a list for it
to be missing from and a test that reads the list against the function.

### 14.4 The published product is exposed to all three, established by reading it

**Demonstrated, statically.** `regula-ai==1.9.0` installed from PyPI builds its
cache key inline in two places and it carries no discriminator beyond the scan
context:

```
site-packages/scripts/scan_cache.py:69   key = f"{path}:{_CACHE_SCHEMA}:{context}:{self._hash(content)}"
site-packages/scripts/scan_cache.py:73   key = f"{path}:{_CACHE_SCHEMA}:{context}:{self._hash(content)}"
site-packages/scripts/report.py:642      cache.put(rel_path, content, file_findings, context=_cache_ctx)
site-packages/scripts/report.py:830      cached_raw = cache.get(rel_path, content, context=_cache_ctx)
```

No path-context component (N112), no scope component (N147), no scan-parameter
component (N163), and `respect_ignores` is threaded into the same two suppression
call sites there as here (`report.py:862`, `report.py:875`). **The published
product is exposed to all three defects by construction.**

Its `_cache_put` returns early on any partial scan
(`if cache is None or min_tier_level > 0: return`), which is the N147 slowness
and which also means `regula check` alone cannot poison anything there. The
reachable path in 1.9.0 is a **full** scan writing an entry and a differently
`--no-ignore`'d scan reading it, since both compute the identical key.

### 14.5 What this addendum does NOT establish, and why

**The runtime comparison against 1.9.0 was attempted and is withdrawn.** It ran
and produced output, and the output means nothing, which is worse than not
running it.

`regula-ai==1.9.0` resolves its scan cache as `Path.home() / ".regula" / "cache"`
with no environment override; `REGULA_CACHE_DIR` reached the scan cache only in
this branch, as part of the N112 work. So all three conditions of the experiment
shared the operator's **ambient** cache instead of the isolated directory each
was given, they were not independent runs, and the test condition and its own
cold-cache control returned the same exit code. **A comparison whose control does
not discriminate is a blank gate** (measurement rule 4), and the conclusion drawn
from it is withdrawn rather than reported.

Two consequences recorded rather than tidied away. **A behavioural claim about
1.9.0's cache cannot be measured on this machine at all** without moving `HOME`
wholesale, which is why 14.4 reads the source instead. And **those runs wrote
into `~/.regula/cache/scan_cache.json`**, the operator's real cache. The entries
are keyed on a scratch fixture path that will never be scanned again and are
therefore inert, and the file was left in place rather than deleted, because
deleting it would discard the operator's legitimate cached entries to tidy up
after mine.

### 14.6 The wheel was rebuilt, because section 13's parity no longer described this tree

Section 13.1 and 13.2 measured a wheel built at `1ddc614`. **This session changed
packaged source** (`scripts/scan_cache.py`, `scripts/report.py`), so that result
stopped describing the tree the moment the fix landed. Re-run at `d32c7be`:

```
$ python3 -m build --outdir <dist>
rc=0    Successfully built regula_ai-1.9.0.tar.gz and regula_ai-1.9.0-py3-none-any.whl

$ <fresh venv>/bin/pip install --no-index --no-cache-dir <dist>/regula_ai-1.9.0-py3-none-any.whl
rc=0    Successfully installed regula-ai-1.9.0

$ <venv>/bin/regula --version    rc=0   regula 1.9.0
$ <venv>/bin/regula self-test    rc=0
$ <venv>/bin/regula doctor       rc=0
```

`--no-index` is load-bearing: the package came from the file. Every run used a
working directory outside this repository.

```
$ python3 scripts/verify_installed_artefact.py --package-root <venv-site-packages> --cli <venv>/bin/regula
  MANIFEST     182 file(s) named in RECORD: OK
  MODULES      99 module(s) in the import closure: OK
  PACKAGING    7 required data file(s) against pyproject: OK
  DATA         7 required data file(s) in this install: OK
  CLAIMS       180 installed file(s) scanned: OK
  PROVENANCE   1 console script: OK
  TRANSCRIPTS  4 command(s) run: OK
  TOTAL       0 finding(s) across 7 check(s); RECONCILED: itemised 0 == counted 0
rc=0
```

**And the repair itself was verified in the artefact, not only in the tree**,
which is the whole point of N144. The same three conditions, run against the
installed wheel from a working directory outside this repository:

```
installed artefact: regula 1.9.0
  A_cold_noignore        exit=1  [('ai_security', False)]
  B_cold_default         exit=0  [('ai_security', True)]
  C_warm_noignore        exit=1  [('ai_security', False)]
```

A and C are identical, which is the property. **A guard that can only read the
working tree cannot answer for the product anyone holds**, and this is the first
session in which a behavioural repair was confirmed in the built package on the
same day it was written.

---

## 15. Addendum, 2026-08-17 (fifth session): the remote, read instead of repeated

**This section corrects claims sections 1, 2c, 8 and 11 have carried since this
branch opened.** They were re-stated by three consecutive sessions, including
mine, and none of us checked the remote. Ledger **N164**.

### 15.1 A pull request is already open

```
$ gh pr list --state open --json number,title,headRefName,baseRefName,headRefOid
{"baseRefName":"main","headRefName":"feat/engagement-fixes",
 "headRefOid":"238d1f1b648aeb57e426da4abeee0b9f2178c940","number":55, ...}
```

Section 11 item 2 says "Open a pull request. The only way CI can ever run on
these commits". **PR #55 is open, base `main`, head this branch.** The action is a
**push**, not opening a pull request.

### 15.2 Two of the forty commits have been through CI, and it passed

```
$ git reflog show --date=iso refs/remotes/origin/feat/engagement-fixes
238d1f1 ...@{2026-08-14 09:25:49 +0100}: update by push

$ git rev-list --count main..238d1f1     -> 2
$ git rev-list --count 238d1f1..HEAD     -> 38
```

```
$ gh pr checks 55
test (3.10) pass 9m42s   test (3.11) pass 6m59s
test (3.12) pass 9m46s   test (3.13) pass 10m22s
Compliant code passes pass          High-risk warns (pass) pass
High-risk fails when configured pass  SARIF file generated pass
Outputs populated pass              Dependency pinning threshold pass
Warn-tier fixture pass              Default inputs pass
Fail closed on failed scan pass     Completion manifest present pass
CodeQL pass   regula-scan pass   axe WCAG 2.2 automated checks pass
site-integrity pass   Analyze (python) pass   Lint (ruff) pass
deploy skipping
```

**All four Python versions and all ten composite-action jobs have run and
passed.** Section 2c and N161 call both unreproducible; that is true of **this
machine** and not of this branch's history.

**The honest form:** both have passed on a two-commit state, and neither has been
exercised on the 38 commits carrying the decision kernel, the claim closures, the
fact loop and the cache repairs. **The gap is 38 commits wide, not 40**, and
everything that makes this branch worth merging is inside it.

### 15.3 A push is already a publication, and no gate here could see that

`netlify.toml` sets `publish = "site"`. No workflow file mentions Netlify, so it
is a GitHub App integration rather than a workflow step, and **the enumeration in
section 2 walks `.github/workflows/*.y*ml` and is therefore structurally
incapable of reporting it.** Its "13 workflow files, 134 steps" is complete about
workflows and silent about this.

```
netlify/getregula/deploy-preview   pass   https://deploy-preview-55--getregula.netlify.app
```

Section 4 says "A merge to `main` IS a publication." True and insufficient.
**A push to this branch is also a publication**, to a different and already-live
address, and it happens before any merge decision is taken. Whoever authorises
the push is authorising that, and it should be said before it is done rather than
discovered after.

**This is measurement rule 5 in its exact form:** a correct answer to "which
workflow steps fire", reported in a section headed as the CI picture, with a
check that is not a workflow outside the predicate's population and nothing
saying so.

### 15.4 What this changes for the owner

- **Owner action 1 becomes "push", not "open a pull request".** Cheaper, and it
  carries the publication consequence in 15.3.
- **The evidence position improves and the gap sharpens.** Four Python versions
  and the composite action are demonstrated on this branch's history rather than
  assumed. They are demonstrated on the wrong two commits.
- **Nothing else moves.** `main` is still unprotected, the 2.0.0 verdict stands,
  and every standing verdict is unchanged. **No push was made and none is
  recommended here.**
