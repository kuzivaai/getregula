# Representative evaluation protocol

Date: 30 August 2026

Status: draft entry protocol. No representative evaluation was conducted.

## Evaluation object

Freeze candidate commit `3b6ca1f7e483ff35838a814c043e6b0361a2d55a`, public review schema 2.0, evidence schema 1.0, rating packet schema 1.0, assessment share schema 4, cache schema v8, and exact corpus hashes before rating begins.

The evaluation concerns useful code-indicator retrieval and review-evidence preparation. It does not evaluate autonomous legal classification, compliance determination, legal advice or certification.

## Target users and task

Target users are software engineers, security reviewers and AI-governance reviewers who can inspect source code and prepare evidence for an accountable decision. Each participant must review code observations, declared context, unknowns, contradictions, references and reviewer questions, then identify whether the material helps a human review without overstating what the code proves.

## Sampling frame

Construct a versioned corpus from real, permission-compatible repositories or independently authored representative samples. Include common supported languages, ordinary non-AI code, generic AI integrations, Article 50-relevant interaction patterns, Annex III-relevant intended-use evidence where observable, Article 5-related names, indirect use, tests, examples, generated code and deliberately ambiguous cases.

Exclude repositories without lawful evaluation permission, samples selected after seeing Regula's result, synthetic fixtures used to tune the detector, inaccessible proprietary data, and cases whose ground truth requires disclosing personal or secret information.

## Rating design

- Assign one canonical item identifier from rating packet schema 1.0.
- Blind raters to Regula's detector class where feasible.
- Use two independent raters for every scored item.
- Permit abstention with a recorded reason.
- Keep missing second ratings explicitly incomplete.
- Adjudicate disagreements only after independent ratings are frozen.
- Preserve the original ratings, adjudicated result, evidence references and rater-role metadata.
- Do not manufacture or impute a second rating.

## Primary measures

- Useful indicator retrieval.
- Harmful misses, with separately defined severity.
- False-positive review burden.
- Appropriate abstention and preservation of unknowns.
- Quality and actionability of unresolved questions.
- Source-location and source-version provenance.
- User comprehension of observed versus declared versus unknown information.
- Time on task for the review workflow.

Report uncertainty intervals and denominators. Predefine subgroup reporting by language, detector class, use-case family and ambiguity. Do not report a combined score that conceals harmful misses or incomplete ratings.

## Stopping rules

Stop and investigate if the frozen candidate or corpus changes, an item was used for detector tuning, a privacy or licensing concern appears, rater blinding is compromised, a required second rating is missing beyond the declared collection window, or harmful misses exceed the pre-registered safety threshold.

Stop reporting if any calculation silently drops abstentions, incomplete packets or contradictory evidence.

## Entry gate

CONDITIONAL GO for protocol and corpus preparation. Before representative rating begins:

1. Re-run the complete suite in a loopback-capable environment.
2. Resolve the version and public candidate identity.
3. Freeze corpus inclusion criteria and hashes before running Regula.
4. Recruit two appropriately independent raters under an approved data and consent process.
5. Pilot the packet and instructions without using pilot outcomes to tune the frozen evaluation set.
6. Pre-register measures, uncertainty method, subgroup analysis, adjudication and stopping rules.

Representative evaluation remains BLOCKED because the frozen external corpus, approved raters and complete loopback verification do not yet exist.

