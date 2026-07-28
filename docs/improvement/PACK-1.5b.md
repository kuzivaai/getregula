# PACK 1.5b — quarantine burn-down, for owner approval

**Status: BUILT, HELD, NOT LANDED. Nothing in this pack has been applied.**
No public surface has changed. Approval is required before any of it lands.

Scope: the 42 unique `(file, claim)` pairs in `.claim-quarantine.json`,
equal to **45 occurrence-level findings** (MEASURED 28 Jul 2026, in place;
see STATE.md "RECONCILED CHAIN"). Plus the 83.5% provenance audit, which
is not in the quarantine but was ordered dispositioned first. Plus finding
**F21**, added to this pack because it is the same instrument.

Format per item: **current text → proposed text → disposition → evidence.**
Where a disposition needs information only the owner holds, it is marked
**OWNER-INPUT** and the rest of the pack continues without it.

---

## SUMMARY OF WHAT IS BEING ASKED

| § | Item | Pairs | Disposition | Public surface? |
|---|---|---|---|---|
| 1 | 83.5% provenance | n/a (not quarantined) | correct 5 of 8 locations | YES |
| 2 | F21 self-canonical URL as source | n/a (gate defect) | fix the auditor | no |
| 3 | Class 1, progress-bar percentages | ~30 | DERIVE from real output | YES, landing page |
| 4 | Class 2, blog statistics | 9 | 1 verified, 1 CORRECTION | YES |
| 5 | Class 3, hypotheticals | 3 | reframe + typed exemption | YES |

**The single most serious item in this pack is §4.** A published blog
statistic does not reconcile with the repo's own tracked scan data. That
is a correction to a public page, not a labelling exercise.

---

## §1. THE 83.5% PRECISION CLAIM — full per-occurrence table

The owner's bar: **N=115 and single-labeller provenance visible or one
link away at every point of use.**

Auditor status: **NOT allowlisted.** The number is artefact-verified,
derived live from `benchmarks/results/random_corpus/PRECISION.json` via
`known_precision_values()`. There is no excused flagship claim. That is
the auditor's criterion, and it is satisfied. It is not the bar.

Single-labeller is disclosed in **exactly one place repo-wide**:
`benchmarks/README.md:198`.

**All eight locations, passing and failing, so approval happens on full
evidence:**

| # | Location | N at point of use | Single-labeller reachable | Verdict |
|---|---|---|---|---|
| 1 | `README.md:246` | yes | yes, links `benchmarks/README.md` which carries it at :198 | **PASS** |
| 2 | `benchmarks/README.md` (:87,:105,:108,:132,:140,:180) | yes | yes, same file | **PASS** |
| 3 | `docs/MODEL_CARD.md:75,:79` | via :143 same page | see #4 | **PASS on N** |
| 4 | `docs/MODEL_CARD.md:143` | yes | **NO** — links `METHODOLOGY.json`, which has corpus construction only (description, date, pool, sample, seed, queries, filters, repos) and **no labeller field** | **FAIL** |
| 5 | `docs/TRUST.md:157` | yes | **NO** — no route to the disclosure | **FAIL** |
| 6 | `docs/examples/exec-summary-sample.html:89` | yes | **NO** — links TRUST.md, which per #5 lacks it | **FAIL** |
| 7 | `scripts/exec_summary.py:225` (generates #6) | yes | **NO** — same chain | **FAIL** |
| 8 | **`site/about.html:132`** | **NO** | **NO** | **FAIL, worst** |

### Item 1.1 — `site/about.html:132` (the worst; public landing surface)

**Current text**
> Published precision on a random corpus: 83.5%.

No sample size. No labeller disclosure. No link. On a public page.

**Proposed text**
> Published precision on a random corpus: 83.5% (N=115, single labeller,
> no inter-rater agreement — <a href="...benchmarks/README.md">methodology
> and limitations</a>).

**Disposition: CORRECTED.** Not "verified": the figure is real and
artefact-backed, but its presentation was not honest about its basis.

**Evidence:** `PRECISION.json` (overall precision, N=115);
`benchmarks/README.md:198` for the single-reviewer disclosure.

**Do not strip the number.** Its successor is Phase 3's multi-annotator
corpus. Removing it would trade a disclosed weak number for no number,
which is worse.

### Items 1.2–1.5 — MODEL_CARD:143, TRUST.md:157, exec-summary sample, exec_summary.py:225

**Current:** each cites 83.5% with N but no reachable labeller disclosure.

**Proposed:** append to each, at the point of use:
> Single reviewer; no inter-rater agreement. See `benchmarks/README.md`.

For #7 (`scripts/exec_summary.py:225`) the change is in the **generator**,
so #6 regenerates from it. Fixing the sample HTML alone would drift on the
next regeneration.

**Disposition: CORRECTED (5 locations, one of them a generator).**

**Structural addition, not optional:** add a claim-auditor rule that any
paragraph containing `83.5` must also contain `N=115` **and** a route to
the labeller disclosure. Without it, this recurs the moment a surface is
added. This is PROGRAMME.md principle 3 (every new public number gets a
claim-auditor rule).

### Item 1.6 — F20, the version-attribution split

**Current:** `README.md` and `docs/TRUST.md` say the 83.5% was measured on
**v1.7.4**. `PRECISION.json` and both exec summaries say **v1.7.0**.

**Proposed:** determine which is correct from `PRECISION.json`'s own
metadata and make all five surfaces agree.

**Disposition: OWNER-INPUT is NOT required — this is determinable from
the artefact.** But it must be settled before any of §1 lands, because
four of the five surfaces being corrected also carry the version.

---

## §2. F21 — a page's own canonical URL is accepted as its source

Not a quarantine item. Included because it is the same instrument, and
because dispositioning §1 and §3 while this stands would put corrected
numbers behind a gate that cannot see them.

**Current behaviour (MEASURED 28 Jul 2026, in place):**

`strip_noise` does not blank `<meta>` tags, so the auditor **does** sweep
them and extracts **27 claims** from numeric `<meta>` description lines
across the 56 site pages. All 27 pass. The `<head>` block parses as one
paragraph containing `<link rel="canonical" href="https://getregula.com/…">`,
and `paragraph_has_source()` returns True on its first check, `URL_RE`.

| source reason | claims |
|---|---|
| NOT sourced (then allowlist + quarantine) | 167 |
| `url` | 92 |
| `citation-word` | 88 |
| `html-link` | 22 |
| `file-ref:README.md` | 1 |
| **total** | **370** (reconciles to the gate's own figure) |

**16** claims sit in a paragraph whose URL context includes a
self-canonical link. Live examples:
`site/blog/blog-scanning-5-frameworks.html:24` "562 findings";
`site/blog/blog-article-5-prohibited-practices.html:29` "35M", "7%".

**Proposed fix:** a URL must not count as a source when it resolves to the
page's own canonical host and path. Narrow and testable:

1. In `paragraph_has_source()`, exclude URLs appearing inside
   `rel="canonical"`, `rel="alternate"`, `og:url` and `twitter:url`.
2. Add a control test asserting a numeric claim in a `<meta name="description">`
   **is** flagged when its page has only a self-canonical link, and **is
   not** flagged when a genuine citation is present. Without the negative
   case the test proves nothing.

**Disposition: FIX THE INSTRUMENT.** Do not stop sweeping meta; the sweep
is correct and should stay.

**Expected consequence, stated in advance so it is not a surprise:** this
will surface new findings, plausibly around 16, which then need their own
dispositions. **That is the gate working.** It must not be used as an
argument against the fix.

---

## §3. CLASS 1 — progress-bar percentages (~30 pairs). DERIVE.

Files: `site/index.html` (7), `site/locales/de.html` (7),
`site/locales/pt-br.html` (7), `site/about.html` (2),
`site/assess/{index,de,pt-br}.html` (1 each),
`site/blog/blog-code-scanning-vs-questionnaires.html` (2).

**Current text** — `site/index.html:413-421`, a terminal mock-up presented
as real command output:

```
$ regula gap .

COMPLIANCE GAP ASSESSMENT

Art. 9  Risk management    ██░░░░░░░░  20%  FAIL
Art. 10 Data governance    ████░░░░░░  40%  WARN
Art. 11 Documentation      ██████░░░░  60%  WARN
Art. 12 Record-keeping     ████████░░  80%  PASS
Art. 13 Transparency       ░░░░░░░░░░   0%  FAIL
Art. 14 Human oversight    ███░░░░░░░  30%  FAIL
Art. 15 Accuracy           █████░░░░░  50%  WARN
```

and `:429-437`, `$ regula comply` with "Overall compliance score: 42/100".

**The honest problem, stated precisely.** These are not claims about
Regula's coverage of Article 14. They are a **depiction of tool output**,
shown behind a `$` prompt with no indication that the numbers are
invented. A visitor reads them as a real scan. No scan produced them.

**This changes the disposition from what was assumed.** The owner's
instruction was derive-or-remove, and derive is available — but not by
inventing a numerator and denominator for "30% of Article 14". It is
available because **`regula gap` is a real command with a real, defined
denominator**, and it can be run against a committed fixture.

**Proposed text** — real output, MEASURED 28 Jul 2026 by running
`python3 -m scripts.cli gap tests/fixtures/sample_high_risk` (rc=0):

```
$ regula gap tests/fixtures/sample_high_risk

EU AI Act Compliance Gap Assessment: sample_high_risk
Highest risk tier: not_ai
Overall score:     9%

  NOTE: This score measures the PRESENCE of compliance
  documentation and infrastructure — it does not assess code
  risk and cannot offset scan findings. A project can score
  100% here and still fail `regula check` on prohibited or
  high-risk patterns. Run both; they answer different questions.

Article 9   Risk Management                     [  0%] NOT FOUND
Article 10  Data Governance                     [  0%] NOT FOUND
Article 11  Technical Documentation             [ 25%] PARTIAL
Article 12  Record-Keeping                      [  0%] NOT FOUND
Article 13  Transparency                        [  0%] NOT FOUND
Article 14  Human Oversight                     [ 45%] PARTIAL
Article 15  Accuracy, Robustness, Cybersecurity [  0%] NOT FOUND
Article 17  Quality Management System           [  0%] NOT FOUND
```

**This is how it would render.** Three differences the owner should see
before approving, because they change the page's face:

1. **The numbers get worse and more honest.** 20/40/60/80/0/30/50 becomes
   0/0/25/0/0/45/0 on this fixture, and the headline score 42/100 becomes
   9%. The current mock-up flatters.
2. **The real command emits a NOTE the mock-up omits entirely** — that
   this score measures presence of documentation, not code risk, and
   cannot offset scan findings. That NOTE *is* the denominator disclosure.
   Its absence from the site is the actual defect.
3. **The real output has 8 articles, not 7** (it includes Article 17 QMS).

**Disposition: DERIVED, test-backed.** Add a test asserting the site block
matches regenerated fixture output, so it cannot drift. This is the
`site_facts` pattern the owner named.

**OWNER-INPUT:** which fixture to feature. `sample_high_risk` scores 9%
and reports `Highest risk tier: not_ai`, which is unflattering and
slightly confusing as a shop window. `sample_mixed_tier` or a purpose-built
fixture may present better while staying real. **Any fixture is acceptable
except one chosen because it scores well** — that would be metric gaming
under PROGRAMME.md principle 3.

**Alternative if derive is rejected: REMOVE the numerals**, keeping the
bars as a qualitative widget with a visible "illustrative" label. Weaker,
because the page then shows a capability it does not evidence.

**Locale parity is mandatory.** `de.html` and `pt-br.html` carry the same
7 pairs each and must change in the same commit (standing rule).
New DE/PT-BR prose needs competent-speaker sign-off — **OWNER-INPUT**.

---

## §4. CLASS 2 — blog statistics (9 pairs). ONE VERIFIED, ONE CORRECTION.

Bar: **reproducible or externally cited. A post asserting its own number
is not a source for that number.**

Both posts link their data directory, so the *intent* was reproducibility.
The question is whether the numbers actually reconcile. **I measured
both.** They do not behave the same way.

### Item 4.1 — `blog-scanning-5-frameworks.html` (4 pairs: 41%, 57%, 65%, 72%)

**Current text (extract):**
> HuggingFace Transformers is 65% AI security (Article 15 cybersecurity).
> CrewAI is 72% agent autonomy…
> 562 findings across 5 AI frameworks.

**MEASURED** from tracked `benchmarks/results/framework_scan_2026_04/`
(5 files, tracked in git):

| framework | findings | top category | share |
|---|---|---|---|
| transformers | 175 | AI Security | **65%** |
| llama_index | 163 | AI Security | 60% |
| pytorch | 93 | AI Security | **57%** |
| crewAI | 78 | Agent Autonomy | **72%** |
| langchain | 53 | AI Security | 47% |
| **total** | **562** | | |

**562 reconciles exactly. 65%, 72% and 57% all reconcile exactly.**

**Disposition: VERIFIED-WITH-SOURCE.** Add an explicit provenance line
naming the tracked data directory, the tool version and the scan date, so
the reader can reproduce rather than having to notice a link.

**Residual, honest:** I did not locate the context for the **41%** claim
in this post; my extraction window missed it and no framework in the
tracked data shows 41% as a headline share. **41% is UNVERIFIED and must
be resolved item-by-item before this post's items land.** It may be a
different denominator; it may be wrong. Not assumed either way.

### Item 4.2 — `blog-scanning-10-ai-apps.html` (4 pairs: 56.6%, 27.8%, 7.4%, 5.6%)

**Current text:**
> Regula flagged 553 findings across 8,659 source files. Agent autonomy
> dominated at 56.6% of findings, followed by limited-risk transparency
> patterns (27.8%), AI security issues (7.4%)…

**MEASURED** from tracked `benchmarks/results/blog_scan_2026_04/`
(10 files, tracked in git):

| quantity | published in post | tracked data | reconciles? |
|---|---|---|---|
| total findings | **553** | **665** | **NO** |
| agent autonomy share | **56.6%** | 216/665 = **32.5%** | **NO** |
| limited-risk share | **27.8%** | 155/665 = **23.3%** | **NO** |
| AI security share | **7.4%** | 225/665 = **33.8%** | **NO** |

**The post also contradicts its own data directory's README**, which is
tracked and states **"Total | 665"** for the same ten projects at
v1.7.0, 23 April 2026.

**Disposition: CORRECTION REQUIRED. This is the most serious item in the
pack.** A public post's headline statistics do not match the repository's
own tracked evidence for that post, and the discrepancy runs in both
directions across categories (AI security is understated by a factor of
about 4.5; agent autonomy is overstated by about 24 points).

**I have not determined the cause and will not guess.** Candidates, none
verified: the post may have been written from a different scan run than
the one committed; it may apply a dedup or filter the data does not
record; or the figures may simply be wrong.

**OWNER-INPUT: was this post written from a scan other than
`blog_scan_2026_04`?** The two branches, clarified by the owner 28 Jul 2026:

- **Branch A — drawn from an older or uncommitted run.** That run must be
  committed, or the post must cite what actually exists. The note frames it
  as a **version skew**: the figures were right for the run they came from.
- **Branch B — wrong at publication.** This is the **correct-to-canonical**
  branch. The post is corrected to **665 / 32.5% / 23.3% / 33.8%**, and the
  note **must state the error was original, not a version skew.** Framing
  an original error as a version difference would layer a second
  misstatement on the first, and it is the more flattering of the two
  stories, which is exactly why it must not be reached for by default.

Either way the correction is **visible, not a silent edit.**

**Until resolved, these 4 pairs stay quarantined.** Do not land a
"verified-with-source" label on numbers that contradict the source.

### Item 4.3 — remaining class 2 pairs (`sample-report.html` 43%; `article-9-risk-management.html` 29%; `eu-ai-act-recruitment-hiring.html` 29%, 43%)

**Not yet individually traced.** Stated rather than glossed. Each needs
the same treatment: locate the claim, find or fail to find its artefact,
disposition. **These remain quarantined and are NOT covered by this pack's
approval.**

---

## §5. CLASS 3 — hypotheticals (3 pairs) and the typed ILLUSTRATIVE exemption

### Item 5.1 — `site/guides/eu-ai-act-healthcare.html` (95%, 70%)

**Current text:**
> A model with 95% accuracy overall but 70% accuracy for a specific
> demographic subgroup has an Article 15 problem.

A worked example. Not a claim about Regula or about any real model. But a
bare figure in prose reads as factual.

**Proposed text:**
> Consider a hypothetical model with 95% accuracy overall but 70% accuracy
> for a specific demographic subgroup: that gap is an Article 15 problem.

**Disposition: CORRECTED by explicit framing in the sentence itself.**
The framing carries the meaning; no exemption mechanism is required for
this item.

### Item 5.2 — the typed `ILLUSTRATIVE` exemption

Required by the owner: **typed, constrained to framed sentences, carrying
a control proving a factual claim cannot ride it, and distinct from the
shrink-only quarantine.**

**Proposed design:**

1. **A separate file**, `.claim-illustrative.json`, never the quarantine.
   Different meaning, different lifecycle: the quarantine is a shrinking
   backlog of things that are wrong; this is a permanent, small register
   of things that are correct and deliberately hypothetical.
2. **Typed entries**, keyed on `(file, normalised claim)` exactly like the
   quarantine, each carrying `"type": "ILLUSTRATIVE"` and a mandatory
   `"framing"` field quoting the framing phrase.
3. **The constraint, enforced in code, not by convention.** An entry only
   suppresses a claim if the claim's own sentence matches a framing
   pattern (`hypothetical`, `for example`, `suppose`, `consider a`,
   `imagine`). **An entry whose sentence does not match does not
   suppress**, and the loader raises. This is what makes it typed rather
   than a second quarantine.
4. **The control test, which is the point of the mechanism:**
   - Positive: a framed hypothetical with an entry **is** suppressed.
   - **Negative (the control): a factual claim — "Regula detects 419 risk
     patterns" — with an otherwise-valid `ILLUSTRATIVE` entry is still
     FLAGGED**, because its sentence carries no framing. This proves a
     factual claim cannot ride the exemption. Without this test the
     mechanism is unproven and must not ship.
5. **Ratchet:** the register may not grow without an entry-level reason
   string, and its size is asserted in the test, so silent growth fails.

**Disposition: BUILD, with the control test as a blocking acceptance
criterion.**

**Honest note on necessity:** after item 5.1's reframing, it is possible
that **zero** items need the exemption. If reframing clears all three,
**the right outcome is not to build it.** A mechanism with no users is a
liability, and the shrink-only quarantine plus honest prose may be
sufficient. **Recommendation: reframe first, then build the exemption only
if a real item survives that cannot be honestly reframed.** The design
above is ready either way.

---

## §5b. PRE-LANDING GATE (owner amendment, 28 Jul 2026) — MANDATORY

**Before the batch commit**, every paragraph the pack touches must be
checked: **none may satisfy `paragraph_has_source()` solely via its page's
own canonical URL** (the F21 mechanism). Any that would is either sourced
properly within the batch or **held for 1.5c**. The check's output goes in
the commit body.

**Tool:** `scripts/check_selfref_sourcing.py --pack`. It reads the file
list out of this pack, so the gate follows the pack rather than a
hand-maintained list.

**Control run first**, per measurement rule 4 (an absent signal is not a
passing signal):

```
$ python3 scripts/check_selfref_sourcing.py site/blog/blog-scanning-5-frameworks.html
paragraphs with numeric claims checked: 20
RESULT: 1 PARAGRAPH(S) SOURCED ONLY BY A SELF-REFERENTIAL URL
rc=1
```

The gate fires on a known case, so a clean result from it means something.

**MEASURED against the pack's own surfaces, 28 Jul 2026:**

```
$ python3 scripts/check_selfref_sourcing.py --pack
auditing 13 file(s) named in PACK-1.5b.md
paragraphs with numeric claims checked: 101
RESULT: 1 PARAGRAPH(S) SOURCED ONLY BY A SELF-REFERENTIAL URL

  site/blog/blog-scanning-5-frameworks.html:23-30
      claims : ['562 findings']
      'source': https://getregula.com/blog/blog-scanning-5-frameworks.html
rc=1
```

**One offender, and its disposition.** The `<head>` paragraph of
`blog-scanning-5-frameworks.html` carries `562 findings` in its
`<meta name="description">`, sourced only by the page's own canonical link.

The number itself is **verified** — 562 reconciles exactly with tracked
`framework_scan_2026_04` data (§4.1). The defect is provenance, not
accuracy. A `<head>` cannot carry a citation without turning a meta
description into something else.

**Disposition: HELD FOR 1.5c.** The body-text corrections for this page may
land; **the meta-description occurrence does not.** This is the amendment
working as designed: it closes the hole for the surfaces being changed
without serialising the whole batch behind 1.5c.

**Re-run this gate immediately before the batch commit**, not once now.
Files change between approval and landing.

---

## §6. WHAT APPROVAL WOULD AUTHORISE, AND WHAT IT WOULD NOT

**Would authorise:**
- §1: correcting 5 of 8 locations of the 83.5% claim, plus the F20 version
  reconciliation and a new claim-auditor rule.
- §2: fixing F21 in the auditor, with its control test.
- §3: replacing the landing-page mock-up with real derived output across
  EN/DE/PT-BR, subject to the fixture choice.
- §5: reframing the healthcare hypothetical.

**Would NOT authorise, and is explicitly held back:**
- §4.2's four pairs, pending the owner's answer on which scan run the post
  used. These contradict tracked evidence.
- §4.1's `41%`, unverified.
- §4.3's four pairs, not yet individually traced.
- Building the ILLUSTRATIVE mechanism, unless a real item survives
  reframing.

**Quarantine arithmetic if the authorised items land:** 42 pairs less
~30 (class 1) less 4 (§4.1, if 41% resolves) less 1 (§5.1) leaves
**about 7 pairs**, all in §4.2 and §4.3. The quarantine must be **empty
before Phase 6/8 publishes anything**, so those 7 are the remaining debt.

**Nothing in this pack has been applied.** The working tree is clean and
every public surface is untouched.
