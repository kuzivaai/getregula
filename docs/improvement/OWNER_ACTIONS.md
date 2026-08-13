# Owner actions — moat programme (27 July 2026)

> **RELOCATED AND PARTIALLY REDACTED, 28 July 2026.** This file was
> `.claude/owner-actions-2026-07.md`, untracked and one `git clean` from
> gone. It is now tracked. **Section 6 ("Competitive watch additions") has
> been removed**: this is a public repository, that section was competitor
> pricing and positioning material, and the repo's own `.gitignore`
> already treats competitor analysis as not-public. It is held verbatim at
> `getregula-internal/competitive-intelligence-2026-07.md`. Item 4 has been
> marked closed to match the evidence. Nothing else has been altered.

Everything the session could not do autonomously because it is
outward-facing, needs a human identity, or needs money. Ordered by
moat value per hour of owner effort. Nothing here blocks the shipped
work; each unlocks the next stage of one moat asset.

## 1. Post the DPVCG contribution (10 minutes; unlocks Moat Asset 1's credential layer)
Draft ready at `docs/dpvcg-contribution-draft.md` (relocated from
`.claude/` on 28 Jul 2026 and now tracked). Post as a comment
on https://github.com/w3c/dpv/issues/229 (verified open, asks for
"representing more of AIAct itself"; #199 is the GPAI sibling with
help-wanted). The machine-readable dataset it references is already
built, tested, and in the repo. A named DPVCG contribution is the (e)
institutional-credential layer on top of the (b)+(d) dataset.

## 2. Recruit raters 2 and 3 (the single binding constraint on Moat Asset 2)
Rater 2's 50-finding blind packet already exists
(`benchmarks/rater2_blind_subset.json`, 0/50 filled). The upgraded
protocol (`benchmarks/MULTI_ANNOTATOR_PROTOCOL.md`) needs one more
independent rater beyond that. Channels per the existing protocol:
academic contacts in AI auditing/fairness, OSS compliance-tooling
contributors; offer co-authorship on the dataset paper
(`benchmarks/PAPER_OUTLINE.md`). Raters must be human, not LLMs.
Everything else (Fleiss tooling, dedup, temporal-split, paper skeleton)
is built and tested.

## 3. Zenodo account + DOI decision (15 minutes; fallback for Asset 1, later home for Asset 2)
If DPVCG declines or stalls, the dataset publishes under a Zenodo DOI.
Needs your account (free). Also decide whether the published dataset
carries CC BY 4.0 (common for datasets) — that is a licensing decision
only you can make; the in-repo dataset currently states the repo
licences.

## 4. EUR-Lex eyeball: CLOSED, then PARTLY OVERTURNED 29 July 2026

**The original closure, kept verbatim because the record of a wrong call is
the point:** two independent retrievals of Regulation (EU) 2026/1744 agreed
that there is "no agentic-AI category or definition", that the Omnibus does
not amend Article 111(2) or set a 2 August 2030 date, and the item was closed
with "Do not re-open or re-run this."

**That instruction was wrong and has been withdrawn.** A full-text retrieval
of the OJ HTML on 29 July 2026 (HTTP 200) found **Annex XIV, Section 3**:

- `AIH 0401` = "AI systems based on other emerging AI technologies not covered
  by other codes, **including Agentic AI**"
- `AIH 0205` = "AI systems that learn from their environment, **excluding AI
  systems covered under AIH 0401**"

**A category label does exist and it names Agentic AI.** The earlier closure
was **wrong on existence** and **right on substance**: the word appears
exactly once in the whole regulation, in a notified-body competence table, with
no definition, no risk tier and no obligation. The Article 111(2) and 2030
findings stand and were correct but partial; recital 39 of 2026/1744 clarifies
that grace period's scope without altering the date.

**Standing lesson: a closure that forbids re-opening is a claim, and it carries
the same evidence burden as any other.** The two earlier retrievals did not
reach the annexes, and the closure asserted a negative over material it had not
read. Recorded in the delta log at
`content/regulations/delta-log/entries/2026-07-29-annex-xiv-aih-codes.json`
with the delegated-act trigger conditions that would re-open the crosswalk
question.

## 5. BSI ART/1 / JTC 21 route (the (e) credential; slowest, highest ceiling)
ART/1 is BSI's AI standards committee and the UK route into CEN-CENELEC
JTC 21. Concrete first step: BSI committee-membership enquiry via the
BSI standards development portal for ART/1 (individual expert
membership). Cost and eligibility: UNVERIFIED this session — ask BSI;
do not budget from guesses.

**CORRECTED 29 July 2026.** The paragraph that stood here said prEN 18286
was "OUT FOR FORMAL VOTE (verified 27 Jul)" and that "public-comment
windows are mostly past". **Both statements are now false, two days
after they were written.** EN 18286 was approved 12 July 2026 and is
published as EN 18286:2026, and other JTC 21 windows are open right now.
This is what decaying-currency knowledge looks like in practice: a
confident, correctly-hedged, correctly-dated claim went stale in 48
hours. It is recorded rather than deleted because it is the argument for
the delta log.

### 5a. OPEN PUBLIC ENQUIRY WINDOWS — owner action, time-critical

**Public comment is the cheapest route to standards participation, asset
class (e), with no committee membership and no fee.**

| Draft | Subject | Public enquiry closes |
|---|---|---|
| `prEN 18228` | AI Risk Management (Article 9) | **30 July 2026** (now passed; whether it was met is unrecorded, see N4) |
| `prEN 18282` | Cybersecurity Specifications for AI Systems | **30 July 2026** (now passed; whether it was met is unrecorded, see N4) |
| `prEN 18229-1` | Trustworthiness Framework, Part 1: Logging (Arts. 12, 13, 14) | **20 August 2026** |

**prEN 18229-1 corroboration strengthened, 6 August 2026.** The genorma
standards tracker lists the draft at stage 40.20 with the enquiry ballot
initiated **28 May 2026 for 12 weeks**, which lands exactly on
**20 August 2026**, independently agreeing with the owner-supplied
jtc21.eu date. Still verified-secondary: no CEN-CENELEC primary page was
reachable, and the AI Standards Hub entry consulted was stale (last
updated 27 April 2026, still saying pre-draft). Confirm with BSI before
relying on it; the window does not reopen.

**Draft comment themes for prEN 18229-1, prepared 6 August 2026.**
Candidate themes only, grounded in this repository's documented
implementation experience. **The draft text has not been read** (enquiry
drafts are accessed through the national portal), so before submitting:
read the draft first and DROP any theme it already addresses. Comments
should be practitioner-neutral; do not mention or promote Regula.

1. *Separate machine-checkable requirements from process requirements
   (Article 12).* An implementer of static tooling can verify that log
   emission points, structured formats and retention configuration exist;
   it cannot verify that logged events serve Article 12(2)'s purposes.
   If the standard distinguishes requirements whose conformity is
   mechanically assessable from those needing process evidence,
   conformity assessment can be partially automated and SMEs can
   self-check the mechanical half cheaply.
2. *A normative minimum event taxonomy.* Article 12(2) states purposes
   (risk identification, substantial modification, Article 79 market
   surveillance). Purpose-level requirements are unassessable without a
   stated minimum event set. A normative minimal taxonomy, format-neutral
   rather than prescribing a logging stack, would make both
   implementation and assessment concrete.
3. *Oversight-to-function traceability (Article 14).* In real codebases
   oversight measures live far from the AI function they gate (approval
   gates in different modules from model calls). A requirement that
   documentation link each oversight measure to the specific AI function
   it controls would make oversight auditable rather than asserted.
4. *Machine-readable transparency artefacts (Article 13).* Encouraging a
   machine-readable structure for instructions-for-use content would let
   deployers ingest provider transparency material into their own
   governance tooling instead of re-keying it.
5. *Proportionality alignment with the Omnibus.* Regulation (EU)
   2026/1744 point (10) gives SMEs, start-ups and SMCs a simplified
   technical-documentation route under Article 11(1). Part 1's logging
   and oversight evidence expectations should state how they compose with
   that simplified route, so the standard does not reintroduce the burden
   the amendment removed.

Route: BSI Standards Development Portal (free account), or the
commenting template to `admin.start@bsigroup.com`, before 20 August
2026. Submission is an owner action; nothing has been sent.

**Corroboration chain, stated at its real strength.** Four independent
signals agree, and **no CEN-CENELEC primary page was reachable**:

1. `jtc21.eu` states the 30 July and 20 August closing dates (owner-supplied,
   29 Jul 2026).
2. Adam Leon Smith, a named JTC 21 participant, published the enquiry-launch
   posts for `prEN 18228` and `prEN 18282` on **7 and 8 May 2026**. A standard
   12-week CEN enquiry from that launch lands on approximately 31 July, which
   is consistent with a 30 July close.
3. The ACM Europe Technology Policy Committee published public reflections on
   draft `prEN 18282` roughly three weeks ago, which is a live enquiry with a
   professional body commenting in it.
4. BSI is a full CEN-CENELEC member, so the UK route is valid.

**What could NOT be verified, checked 29 July 2026:** the official
CEN-CENELEC AI topic page carries no enquiry dates at all; the JTC 21
tracker consulted is a June 2026 snapshot with no closing dates that
itself instructs readers to check the live work programme; the two
participant posts are paywalled beyond their first paragraphs; and the
BSI project page for `BS EN 18228`
(`standardsdevelopment.bsigroup.com/projects/2025-01990`) exists but
would not render for an automated fetch.

**Route to comment:** the BSI standards development portal, or a
commenting template emailed to `admin.start@bsigroup.com`.

**This is an owner action and was not executed here.** Four corroborations
are not a primary source. Confirm the window with BSI before relying on
it; the check costs minutes and the window does not reopen.

### 5b. Alignment task, unchanged

Technical alignment task queued for a session: map Annex IV pack
structure to EN 18286:2026's published clause structure (10 normative
clauses, 5 informative annexes, ISO 9001/13485/42001-compatible per
public summaries; the standard text itself is paywalled and must be
purchased before claiming clause-level alignment).

## 6. Competitive watch additions — REDACTED FROM THE TRACKED COPY
Three bullets of competitor pricing, licence and star counts, a note that
one competitor's remediation roadmap is stale post-Omnibus, and Regula's
absence from a competitor comparison page. Gathered as positioning
material and removed when this file entered a public repository. Held
verbatim at `getregula-internal/competitive-intelligence-2026-07.md`.
All of it is a snapshot of fetches dated 27 Jul 2026 and needs
re-verifying before any external use.

## 7. GSC re-auth (owner credential; unblocks J4 metrics)
`scripts/gsc_fetch.py` still fails with invalid_grant. UX metrics for
regulatory-currency queries (docs/UX-REVIEW-2026-07.md Section 4) wait
on this.

## 8. Does the claim auditor sweep meta descriptions? ANSWERED 28 Jul 2026
**Yes it sweeps them, and that turned out not to be the problem.** It
extracts 27 claims from numeric `<meta>` description lines across the 56
site pages. The real defect is that all 27 pass, because the `<head>`
parses as one paragraph containing `<link rel="canonical">` and a URL
satisfies `paragraph_has_source()`. A page's own address is accepted as
the source for every number in its head. Logged as **finding F21** (HIGH,
Trust) with the full measurement in STATE.md; disposition goes in the 1.5b
pack. **No owner action required** beyond approving that disposition.

### Original note, kept for the record
A search-index snippet for getregula.com seen on 27 Jul 2026 showed
"398 risk patterns, 12 frameworks" against the canonical 419/13 in
`data/site_facts.json`. The live pages are correct, so that specific
instance is an external index cache and not a repo defect. **The open
question is the general one: if a stale number sat in a `<meta>`
description, would `claim_auditor` catch it?** Nobody has checked. This
belongs with the Phase 8 every-number sweep, and it is a plausible gap
in the same instrument Phase 1.5 just repaired. Preserved here because
it was buried in the redacted section 6 and would otherwise have been
lost with it.

## 9. Private remote for `getregula-internal/` (still open, owner call)
A local-only git repo was authorised and created on 28 Jul 2026 (`git
init`, commit `756fb43`, no remote, `pre-push` hook refusing pushes). That
gives history but everything still lives on one disk. A **private** remote
would close it properly. Owner call because it needs an account. Whatever
is chosen must stay private: the directory holds competitive and
commercial strategy deliberately kept out of the public repo.

## 10. DEFERRED SESSIONS, recorded 29 July 2026 so neither is silently lost

Owner-set sequencing. **Both are deferred deliberately, not dropped.**

### Session B: F29 unit reconciliation, agentic draft humanising and validation

**Contents:** settle F29 (387 against 386, and whether the blog post's 389 is
corrected); humanise and validate
`content/blog/article-agentic-ai-annex-xiv.md`, currently `published: false`.

**Why it runs next, not now:** both are content corrections, and content
corrections should be verified by the **repaired** claim gate rather than the
current one. The current gate scans whole files and fails on pre-existing
claims (see the session 5c checkpoint in STATE.md), so a content fix verified
against it cannot be distinguished from a file that merely happens to be
touched. Verifying content against a gate that is itself under repair proves
nothing about the content.

### Session C: repository restructure to public-repo standard

**Contents:** full file inventory classified needed / superseded /
never-public, structure to current conventions, governance files, SPDX
headers, OpenSSF Scorecard in CI, Best Practices passing badge.

**Why it runs last:** it is the largest diff, and **it moves the paths that
every measurement currently on record is keyed to.** The F25 figure
(33 / 61 at `81e14a3`, corpus of 156 files excluding `docs/improvement/`), the
`--diff-base` distribution (195 / 67 / 8 at `b43f95d`), the manifest surfaces
that `cascade_count --check` validates, and the claim identity rule the gate
repair depends on are all path-keyed. Restructuring first would invalidate all
of them at once and leave nothing to compare against.

**Ordering rule that follows from this:** the gate repair and the measurements
it produces must land and be stable **before** any path moves. Session C is a
mechanical change once that is true, and an unmeasurable one before it.
