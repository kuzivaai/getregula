# ADR 0001. Claim identity is (path, normalised claim text)

- **Status:** accepted, 29 July 2026
- **Decided at:** commit bf0c5d4, branch improvement/2026-08-programme
- **Implements:** `scripts/claim_diff.py`, guarded by `tests/test_claim_diff.py`
- **Consumers:** the gate-scope repair, still unstarted, which needs an
  introduced-claim condition and cannot define one without this

## Context

`claim_auditor.py --diff-base main` scans whole files. Any file the diff
touches is scanned in full, so a branch that edits one line of a document
inherits every unsourced claim already in it. At bf0c5d4 that produces 278
findings against main, of which 223 are claims this branch introduced and 55
already existed at the merge base (measured, `scripts/claim_diff.py --base
main`, main tree).

The proposed remedy is an introduced-claim condition: fail only on claims
present at HEAD and absent at the merge base. That condition is meaningless
until "the same claim" is defined, and defining it is a judgement, not a
measurement. This ADR records the judgement so a later session inherits the
basis and not only the conclusion.

## Decision

A claim is identified by **(repo-relative path, normalised claim text)**.

Normalisation lowercases, collapses whitespace runs to a single space, and
strips one trailing full stop. It does **not** normalise digits.

Three consequences follow, all intended.

1. **Editing a claim's text makes it read as newly introduced.** Changing
   "42.0% precision" to "51% precision" is a new claim, not an edited one.
2. **Editing prose around a claim does not.** Identity keys on the claim
   snippet, not the paragraph, so rewording a sentence next to a number leaves
   the number's identity intact.
3. **Moving a claim to another file makes it read as newly introduced** on
   that file, because the path is part of the key.

## Why, for consequence 1 specifically

This is the contested one, so the argument is set out rather than asserted.

The gate exists to enforce "you must source what you assert". If you changed
the text of a claim, you re-asserted it, and re-assertion is exactly the moment
to attach provenance. A figure that moves from 42.0% to 51% has a different
truth condition and needs a different source; treating it as the same claim
because it sits in the same sentence would let a changed number inherit an old
citation. This repository has already published a figure that did not match its
own source at least six times, so the failure mode is not hypothetical.

The false-positive cost is bounded and visible: a genuine reword of a claim
forces one provenance line. The false-negative cost of the alternative is
silent and is the failure this programme keeps paying for.

> **The figures 42.0% and 51% in this document are invented placeholders.**
> An earlier draft used the repository's real published precision figure as
> the example. `tests/test_precision_provenance.py` correctly failed: a
> tracked file carrying that figure must be on the surface manifest with its
> N and labeller route. The example was changed rather than the manifest.
> The previous session made the identical mistake and recorded it; this is
> the second occurrence.

## Rejected alternative: fuzzy or provenance-tracking identity

Track a claim across edits, either by similarity matching on the snippet or by
assigning stable claim IDs carried in the document.

Rejected for three reasons.

1. **It reintroduces the exact defect it is meant to avoid.** Any similarity
   threshold loose enough to survive a reword is loose enough to match 42.0%
   against 51%, so a changed number escapes the gate wearing its predecessor's
   citation. That is worse than a false positive.
2. **Stable IDs require authoring discipline the corpus does not have.** They
   would have to be embedded in Markdown and HTML by hand, in a repository
   whose recurring failure is hand-maintained bookkeeping drifting from
   measurement.
3. **It is a much larger machine** for a benefit that the measurement says is
   small. Only 55 of 278 findings sit in files that existed at the merge base
   at all, so the population where cross-edit tracking could help is at most
   those 55, and in practice far fewer.

## Status of the evidence

The measurement behind this ADR is evidenced, not reasoned:
`scripts/claim_diff.py --base main` at bf0c5d4 in the main tree.

The **judgement** in "Why, for consequence 1" is **reasoned, not evidenced**. No
literature was consulted on claim-identity conventions for provenance gates;
none is known to exist for this narrow problem, and a search was not attempted
because the decision turns on this repository's own observed failure modes
rather than on general practice.

It rests on two assumptions:

- that a reworded claim is more likely to be a substantive change than a
  cosmetic one, in this corpus;
- that the cost of an unnecessary provenance line is lower than the cost of a
  changed figure inheriting an old citation.

**What would overturn it:** running the strict rule over a period of real
branch work and finding that most re-flagged claims were cosmetic rewordings
with unchanged truth conditions. `tests/test_claim_diff.py`
::test_editing_a_claim_makes_it_read_as_introduced is the assertion to change
if that happens, and this ADR is the document to supersede.

**Cheapest to reverse:** the strict rule is a pure function of two trees and
adding tolerance later is additive. Starting loose and tightening would require
re-auditing everything the loose rule let through.

## Not decided here

Whether the introduced-claim condition is *sufficient* to unblock the merge. It
is not: 223 of 278 findings at bf0c5d4 are branch-introduced, so the condition
alone changes little. See LEDGER.md, "Merge-base measurement", and note that
owner decision 7 is affected.
