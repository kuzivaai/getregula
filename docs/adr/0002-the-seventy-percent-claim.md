# ADR 0002: the "roughly 70% of the EU AI Act" claim has no source

**Status:** OPEN, owner ruling still needed. **A DRAFT AGAINST OPTION 2 NOW
EXISTS AND IS HELD UNPUSHED. The decision is NOT confirmed and the other two
options remain open.** Read the "Held draft" section at the end of this file
before treating anything here as settled.
**Date:** 2026-07-30
**Measured at:** `2c1f080`, tree `8e9e483` for the original investigation;
`509c997` for the corrected enumeration and the held draft.

## The claim

> Questionnaires capture the roughly 70% of the EU AI Act that has no
> source-code footprint.

It is materially different from a percentage inside a scan report. It is the
premise of the product's positioning: it is the reason questionnaires exist
alongside the scanner, and the reason the scanner's limits are presented as
acceptable rather than as a gap.

## It is on ten reader-facing locations across six files, not one

**CORRECTED 2026-07-30. THIS SECTION SAID FOUR AND THE ANSWER IS TEN, ACROSS
SIX FILES.** The original enumeration is kept below because the way it was
wrong is the point. It was produced by a predicate, which is the rule, but the
predicate was chosen by hand and matched only the phrasings that say **70%**.
The identical claim is also published as its complement, **"roughly 30% of the
EU AI Act"**, and none of those occurrences was in scope of the pattern. A
predicate does not make an enumeration complete; a predicate that covers the
claim does. This is measurement rule 4c failing at the step before the command.

The original, incomplete:

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

The corrected predicate, at `509c997`, which asks for a proportional claim
about the Act in either direction rather than for one phrasing of it:

```
$ git ls-files -z | xargs -0 grep -nE \
    "(roughly|about|approximately|around)? ?[0-9]{1,3}% of the (EU AI Act|regulation)|[0-9]{1,3}% organisational|remaining [0-9]{1,3}%" \
    | grep -vE "^docs/(improvement|adr)/|^\.claim-quarantine"
content/blog/article-code-scanning-vs-questionnaires.md:20   (70% organisational / 30% technical)
content/blog/article-code-scanning-vs-questionnaires.md:48   (roughly 30% of the EU AI Act)
content/blog/article-code-scanning-vs-questionnaires.md:84   (roughly 30% of the regulation)
site/about.html:140                                          (roughly 30% / remaining 70%)
site/blog/blog-code-scanning-vs-questionnaires.html:191      (70% organisational / 30% technical)
site/blog/blog-code-scanning-vs-questionnaires.html:238      (roughly 30% of the EU AI Act)
site/blog/blog-code-scanning-vs-questionnaires.html:285      (roughly 30% of the regulation)
site/blog/blog-static-analysis-ai-compliance.html:189        (roughly 70% of the EU AI Act)
docs/what-regula-does-not-do.md:6                            (about 30% of the EU AI Act)
site/llms-full.txt:291                                       (about 30% of the EU AI Act)
```

**Ten locations, six files.**

**Two of those ten make this ADR's own argument circular, and that is the most
important thing on this page.** `docs/what-regula-does-not-do.md` is the
document this ADR names as the qualitative basis for weakening the claim, and
its opening paragraph published **"static code scanning may fundamentally
address only about 30% of the EU AI Act"**. Citing it as the basis for removing
an unsourced proportional figure, while it published the same unsourced
proportional figure, is the self-citation loop this ADR warns about, realised
inside the repository rather than out on the web. `site/llms-full.txt:291`
mirrors that paragraph verbatim, so the figure was also on a published
AI-discovery surface.

**This section previously stated the opposite of that.** It said "`site/llms-full.txt`
carries the qualitative Article 9 statement but not the figure." That was
wrong: it carried the figure, in the 30% phrasing the predicate did not look
for.

## What was searched, and what came back

**In the repository.**

- Every tracked occurrence of a `70%` figure: **16 files at `509c997`**, of
  which the surfaces enumerated above carry this claim. The rest are thresholds
  in `scripts/classify_risk.py` and `scripts/questionnaire.py`, an unrelated
  healthcare-guide figure, and programme working documents. **This said "15
  files" with no commit attached.** The number moves whenever a record
  discussing the claim is edited, because those records are inside the corpus
  being counted, which is rule 24 in `docs/improvement/LEDGER.md`. It is
  correct at its commit or it is not a measurement, so the commit is now stated.
- `docs/what-regula-does-not-do.md` carries the nearest thing to a basis: a
  table of articles Regula cannot verify, with a reason for each. It is
  qualitative, and it is about a listed set of articles rather than about a
  proportion of the Act. **CORRECTED 2026-07-30: this said "seven" and listed
  seven (9, 17, 26, 27, 23, 43, 63). The table has nine rows**, the two it
  missed being Article 72/73 (serious incident reporting) and Article 74
  (market surveillance cooperation). Derived, not read: parsing the two tables
  gives **10 articles Regula can partially or fully address and 9 it cannot**,
  and of the 10 addressable, **8 carry a confidence of scaffold-only,
  reference-only or medium**, leaving 2 of 19 rows as high-confidence code
  coverage.

  **What that means for the wording of any replacement, and it is a real
  constraint.** A table of 19 articles is a coverage map, not a census of a
  113-article regulation, so it cannot support a statement about the SHARE of
  the Act's obligations whatever quantifier is used. Nine of nineteen is not a
  substantial majority even of the table's own rows. A replacement reading "a
  substantial majority of the Act's obligations are organisational" would
  therefore be an unsourced proportional claim standing in for an unsourced
  proportional claim, which is this ADR's own argument against option 1. The
  drafted replacement claims the KIND of obligation and not its share.
- `references/article_obligations.yaml` covers **Articles 9 to 15 only**, and
  its own header says the effort estimates in it "are NOT sourced from a
  specific study". It cannot support a claim about the whole Act.
- No tracked file states an organisational-versus-technical split:
  `git ls-files -z | xargs -0 grep -lniE "organisational (vs|versus|and) technical"`
  returns nothing.
- `git log -S` on the phrase across all refs: the claim entered at `d29f545`
  ("feat: REST API, web dashboard, SLA, Trust Center, legislation fixes"), a
  large feature commit, **with no source attached at introduction**. Nothing
  was ever removed. The `about.html` wording was added later at `e541cb9`.

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
  programme has already paid for: the headline precision figure passed the gate
  while failing honest provenance at five of eight locations, which is the
  finding `tests/test_precision_provenance.py` exists to enforce against. The
  figure itself is deliberately not repeated here, because that test's bar is
  that any surface publishing it must carry N and the single-reviewer basis at
  the point of use, and this document has no business restating either.

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

---

## Held draft: what exists, what it is conditional on, what it costs

**A draft against option 2 is committed and held unpushed. The decision is not
confirmed.** Options 1 (derive a defensible figure) and 3 (remove the sentence)
remain fully open. If either is chosen, the held commit is discarded, which
costs one commit and no published change, because nothing was pushed and
nothing was deployed.

**What the draft changes.** Ten locations across six files, enumerated by the
corrected predicate above rather than carried from this document's original
four:

| File | Locations |
|---|---|
| `content/blog/article-code-scanning-vs-questionnaires.md` | 20, 48, 84 |
| `site/blog/blog-code-scanning-vs-questionnaires.html` | 191, 238, 285 |
| `site/about.html` | 140 |
| `site/blog/blog-static-analysis-ai-compliance.html` | 189 |
| `docs/what-regula-does-not-do.md` | 6 |
| `site/llms-full.txt` | 291 |

**No locale variant carries the claim.** All six locale surfaces were checked
individually. `site/locales/de.html:586` and `site/locales/pt-br.html:603`
already carry the qualitative framing with no percentage, so the English pages
were the outliers and the drafted wording brings them into line with what the
translations already say.

**The wording, and the one place it departs from what was asked for.** The
instruction was to weaken to "a substantial majority of the Act's obligations
are organisational". The section above sets out why the cited basis cannot
support that, or any other proportional quantifier. The draft therefore claims
the KIND of obligation rather than its share: that the named obligations are
organisational and have no source-code footprint, which the table supports row
by row. The surrounding argument is untouched; scanning alone is still
presented as insufficient, and the questionnaire layer is still presented as
unskippable.

**A consequence that had to be handled in the same commit.** The draft removes
both `30%` and `70%` from `site/about.html` and
`site/blog/blog-code-scanning-vs-questionnaires.html`, and those four claims
had four LIVE entries in `.claim-quarantine.json`. Measured before the edit at
`509c997`: 29 entries, 21 live, 8 silent. Leaving the entries would leave four
suppressions firing on nothing. They are burned down through the file's own
`_burn_down` protocol, with disposition `corrected` because the page content
changed, which is different from the fifteen records above them where the text
had never been present. The ceiling falls by four automatically and
`tests/test_claim_quarantine.py` re-measures every record, so a burn-down
written on a false premise fails the suite. Entries 29 to 25.
`site/guides/eu-ai-act-healthcare.html '70%'` is untouched: it is a worked
example about model accuracy for a demographic subgroup and has nothing to do
with this claim.

**What is NOT fixed, and should not be read as fixed.**
`site/blog/blog-static-analysis-ai-compliance.html:189` is finding N30(1): the
paragraph is held green by the word `source` inside "source-code footprint".
The replacement keeps that phrase, so the paragraph is still held green by the
same word. Narrowing what counts as a citation word is gate-scope work.
