# ADR 0002: the "roughly 70% of the EU AI Act" claim has no source

**Status:** OPEN, owner ruling needed. Nothing was changed on any page.
**Date:** 2026-07-30
**Measured at:** `9e6b6de`, tree `8e9e483`

## The claim

> Questionnaires capture the roughly 70% of the EU AI Act that has no
> source-code footprint.

It is materially different from a percentage inside a scan report. It is the
premise of the product's positioning: it is the reason questionnaires exist
alongside the scanner, and the reason the scanner's limits are presented as
acceptable rather than as a gap.

## It is on four reader-facing surfaces, not one

Produced by predicate, never by reading:

```
$ git ls-files -z | xargs -0 grep -n -E "roughly 70%|remaining 70%|70% organisational|70% of the EU AI Act" \
    | grep -vE "^docs/improvement/"
content/blog/article-code-scanning-vs-questionnaires.md:20:... The EU AI Act is roughly 70% organisational and 30% technical. ...
site/about.html:140:Static code scanning can address roughly 30% of the EU AI Act. The remaining 70% ...
site/blog/blog-code-scanning-vs-questionnaires.html:191:... The EU AI Act is roughly 70% organisational and 30% technical. ...
site/blog/blog-static-analysis-ai-compliance.html:189:Questionnaires capture the roughly 70% of the EU AI Act that has no source-code footprint ...
$ ... | wc -l
4
```

`site/llms-full.txt` carries the qualitative Article 9 statement ("It has no
source-code footprint") but not the figure.

## What was searched, and what came back

**In the repository.**

- Every tracked occurrence of a `70%` figure: 15 files, of which the four above
  carry this claim. The rest are thresholds in `scripts/classify_risk.py` and
  `scripts/questionnaire.py`, an unrelated healthcare-guide figure, and
  programme working documents.
- `docs/what-regula-does-not-do.md` carries the nearest thing to a basis: a
  table of **seven** articles Regula cannot verify (9, 17, 26, 27, 23, 43, 63)
  with a reason for each. It is qualitative and it is about seven articles, not
  about a proportion of the Act.
- `references/article_obligations.yaml` covers **Articles 9 to 15 only**, and
  its own header says the effort estimates in it "are NOT sourced from a
  specific study". It cannot support a claim about the whole Act.
- No tracked file states an organisational-versus-technical split:
  `git ls-files -z | xargs -0 grep -lniE "organisational (vs|versus|and) technical"`
  returns nothing.
- `git log -S` on the phrase across all refs: the claim entered at `001b6c5`
  ("feat: REST API, web dashboard, SLA, Trust Center, legislation fixes"), a
  large feature commit, **with no source attached at introduction**. Nothing
  was ever removed. The `about.html` wording was added later at `2e9fd8b`.

**Externally**, four searches:

- "EU AI Act percentage of obligations organisational versus technical 70%":
  nothing on point. The top hit is a LinkedIn post about 70% of AI regulations
  being enforceable rather than advisory, a different claim entirely.
- "what share of EU AI Act requirements can static code analysis detect":
  nothing quantifying it. **Regula's own page is the seventh result**, which is
  the circularity risk stated below.
- An exact-phrase search for `"70% organisational" OR "70% organizational"`
  with `"30% technical"`: **zero results**. The split is not a published,
  quotable figure anywhere the index reaches, and it is not a GDPR trope with a
  traceable origin either; a separate search for that came back with nothing on
  point.
- Academic search for an obligation taxonomy. The closest is Cappelli et al.,
  "Approaching the AI Act... with AI: LLMs and knowledge graphs to extract and
  analyse obligations" (ScienceDirect S2212473X25001026), which does give a
  quantitative legal analysis: roughly 729 provisions, 603 (+/-20) deontic
  obligations, 754 "obligations of action" against 108 "obligations of being".
  **It does not split them into code-detectable and organisational.** It says
  the Act imposes "technical, procedural, and organisational duties" without
  apportioning them.

## Conclusion

**No source and no derivation exists.** This is the third of the three
conclusions the question allowed.

## The circularity risk, stated because it is not hypothetical

`getregula.com/blog/blog-static-analysis-ai-compliance.html` already ranks on
the first page for the query a person would use to check this claim. If the
figure propagates, Regula becomes its own citation, and a later session
searching in good faith will find it and read it as corroboration.

## Options

**1. Derive it.** Classify the Act's provider-facing obligations as
code-detectable or not, and publish the derivation.

**2. Weaken it to a qualitative statement.** Replace the figure with the claim
the repository can already support: most of the Act's obligations are
organisational and have no code footprint, as
`docs/what-regula-does-not-do.md` sets out article by article.

**3. Remove it.**

## Recommendation, and the case against it

**Recommended: option 2, weaken to qualitative.**

The reasoning is **reasoned, not evidenced**. The evidence establishes only
that no source exists; what to do about that is an argument.

- It is the only option that is true under every choice of denominator. The
  qualitative claim is already supported article by article in the repository.
- A derivation's answer is an artefact of its denominator. Counting all 113
  articles includes institutional machinery addressed to regulators, not
  providers; counting only Chapter III Section 2 gives a different number
  again; counting the 862 obligations in the Cappelli taxonomy gives a third.
  Whichever is chosen, the number would be defensible only alongside the choice,
  and a figure that needs its denominator quoted with it is not the crisp
  marketing number the current sentence is doing duty as.
- Publishing a derived figure would create a NEW claim of exactly the kind this
  programme has already paid for: the 83.5% precision figure passed the gate
  while failing honest provenance at five of eight locations.

**The case against, stated because the owner should weigh it:**

- The number is doing commercial work. "Roughly 70%" is concrete and memorable;
  "most" is weaker in a positioning argument, and the owner may judge that cost
  higher than the honesty gain.
- It is a four-surface content change, not a one-line edit, and two of the four
  are locale-sensitive site pages.
- If a defensible derivation IS achievable, it would be a genuine
  differentiator, and declining to attempt it forgoes that. Option 1 is not
  obviously wrong; it is more expensive and more fragile.

**Assumptions this recommendation rests on:** that no source exists (searched,
above); that the qualitative claim is independently supportable (it is, in
`docs/what-regula-does-not-do.md`); and that a denominator-dependent figure is
worse than no figure.

**What would overturn it:** a published analysis apportioning the Act's
obligations between code-detectable and organisational. That would make option
1 correct and cheap at once.

**Cheapest to reverse:** option 2. Weakening a sentence and later restoring a
figure once a source exists is a text edit. Publishing a derived figure and
later withdrawing it is a correction on four public pages, which is the move
this programme exists to avoid.
