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
