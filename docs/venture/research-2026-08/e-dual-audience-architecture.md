# (e) Dual-audience information architecture: an empty search, reported as one

## What was searched for, and what came back

Searched 2026-08-17 for controlled or empirical work on serving a technical and a
non-technical audience from one page, with no accounts and no framework:
progressive disclosure for mixed-expertise readers, documentation architecture
for developers and non-technical stakeholders, and layered technical content.

**Nothing decisive was found.** What the search returned, and why none of it is
evidence:

| Returned | Why it is not evidence here |
|---|---|
| A documentation vendor's post on API docs for non-technical users | Vendor content marketing. No study, no sample, no method. |
| Interaction Design Foundation's progressive-disclosure topic page | An encyclopaedia entry summarising a design principle. Cites no experiment bearing on mixed-expertise single-page architecture. |
| Two ResearchGate papers on progressive disclosure | Both concern **algorithmic transparency** disclosure, i.e. how much to tell a user about a model's reasoning. A genuinely adjacent literature, and a different question from how to lay out a page for two audiences. Abstract-only access; neither opened. |
| A Medium post on enterprise progressive disclosure | Practitioner opinion. |
| A C4-model architecture-documentation page | A diagramming convention, not a finding about readers. |

The honest summary is that "progressive disclosure" is a widely-repeated design
principle with a thin empirical base for *this specific question*, and that the
confident-sounding guidance available online is unattributed synthesis of the
same vendor posts. Given that this project's ledger records at N132 that all
three statistics previously supplied for a comparable decision failed at source,
quoting any of the above would repeat the error rather than avoid it.

## Reasoned, not evidenced

The project does have relevant evidence, and it is its own.

**What is measured.** The homepage already implements progressive disclosure: a
restructure across all locales shipped in v1.7.6. The 91-day Plausible export
(2026-05-15 to 2026-08-13) records for `/`:

- 109 visitors
- 85% bounce
- 23 seconds time on page
- **29% scroll depth**

**The inference, and it is an inference.** A layered page whose median reader
reaches 29% of it is not delivering its lower layers to anybody. Whatever
progressive disclosure does for a reader who scrolls, it does nothing for the
71% of the page that this page's readers do not reach. The dual-audience problem
here is therefore not primarily "which audience gets which layer"; it is that
**both audiences are leaving before the second layer**.

**Assumptions this rests on.** That scroll depth as Plausible reports it is a
reasonable proxy for what a reader saw, and that the 109 homepage visitors
include enough humans for the median to mean anything. Section (b) shows the
second assumption is weak: a substantial share of the direct traffic has an
automated signature, and automated traffic would depress scroll depth. If the
residue is large, the human scroll depth is higher than 29% and the inference
weakens.

**The observation that would overturn it** is scroll-depth data segmented to
traffic with a human signature, showing the median human reaching the terminal
block. That segmentation is available in principle from Plausible's own filters
and was not performed here.

**The observation that would confirm it** is cheaper and has never been done:
show the page to two representative readers, one developer and one non-technical
founder, and ask what the product does. This project has run no comprehension
test with any reader, ever, and every design conclusion in this document is
weaker than that one test would be.

## What follows for a design decision

**Reasoned, not evidenced**, and stated as a direction rather than a finding:

1. The dual-audience question is downstream of the fold question. Deciding which
   audience gets which layer is premature while the measured median reader sees
   less than a third of the page.
2. The cheapest structural response to two audiences with no accounts and no
   framework is not two layers on one page but **two named entry points**, each
   honest about who it is for, because a named route requires no inference about
   the reader and no scroll. The site already has the ingredients: a browser
   assessment for people without code, and a CLI quickstart for people with it.
   The README already does this explicitly with its "Choose how to start" table,
   and the homepage does not.
3. Whatever is chosen cannot be validated by measurement here. Section (b)
   establishes that a year of split testing at this traffic detects nothing
   smaller than a 1.7-fold change. This is a decision to be made on
   comprehension grounds and reviewed with readers, not a decision to be
   optimised.
