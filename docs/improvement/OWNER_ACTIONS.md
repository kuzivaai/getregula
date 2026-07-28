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

## 4. EUR-Lex eyeball — CLOSED 28 July 2026, no action required
Two independent retrievals of Regulation (EU) 2026/1744 (the ELI
`/eli/reg/2026/1744/oj/eng` record and the CELEX `32026R1744` text) agree:
there is **no agentic-AI category or definition**, and the Omnibus does
**not** amend Article 111(2) or set a 2 August 2030 date. Regula asserts
neither, so nothing needed fixing and nothing may be added. Recorded in
STATE.md under "EUR-LEX RE-VERIFICATION". Kept here as a closed record
rather than deleted, so the closure is visible to anyone working from an
older copy of this list. **Do not re-open or re-run this.**

## 5. BSI ART/1 / JTC 21 route (the (e) credential; slowest, highest ceiling)
ART/1 is BSI's AI standards committee and the UK route into CEN-CENELEC
JTC 21. Concrete first step: BSI committee-membership enquiry via the
BSI standards development portal for ART/1 (individual expert
membership). Cost and eligibility: UNVERIFIED this session — ask BSI;
do not budget from guesses. Cheap parallel path regardless of
membership: prEN 18286 is now OUT FOR FORMAL VOTE (verified 27 Jul;
fresher than the research sweep), so public-comment windows are mostly
past for this standard; alignment work matters more than commentary
now. Technical alignment task queued for a session: map Annex IV pack
structure to prEN 18286's published clause structure (10 normative
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

## 9. Private remote for `getregula-internal/` (still open, owner call)
A local-only git repo was authorised and created on 28 Jul 2026 (`git
init`, commit `756fb43`, no remote, `pre-push` hook refusing pushes). That
gives history but everything still lives on one disk. A **private** remote
would close it properly. Owner call because it needs an account. Whatever
is chosen must stay private: the directory holds competitive and
commercial strategy deliberately kept out of the public repo.

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

## 7. GSC re-auth (owner credential; unblocks J4 metrics)
`scripts/gsc_fetch.py` still fails with invalid_grant. UX metrics for
regulatory-currency queries (docs/UX-REVIEW-2026-07.md Section 4) wait
on this.
