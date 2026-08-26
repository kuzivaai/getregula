# Regula engineering roadmap

This is the public technical roadmap. It deliberately excludes private plans,
personal information, outreach records, pricing experiments, handovers and
session logs.

Regula reports code-observable indicators for human review. It does not decide
legal applicability, legal classification, conformity or compliance. Absence
of a finding is not clearance.

## Current priorities

1. **Public-repository privacy.** Remove internal operating material from the
   current tree, prevent reintroduction, and replace public Git history only
   after the sanitised tree passes the complete verification gate.
2. **Independent detector evaluation.** Replace maintainer-only synthetic
   results with a versioned, licence-compatible corpus, independent labels,
   a written codebook, disagreement adjudication and confidence intervals.
3. **Evidence quality.** Report detector observations separately from declared
   deployment facts, legal questions and reviewer decisions. Preserve source
   location, rule identity, rule version and analysis limitations.
4. **Language-aware analysis.** Prefer syntax-aware rules where supported and
   measure fallback behaviour explicitly. A regex match is a candidate signal,
   not a semantic conclusion.
5. **Calibration and abstention.** Evaluate rule-level precision and recall,
   expose uncertainty, and abstain when required context is unavailable.
6. **Repeatability and performance.** Use deterministic fixtures, content-hash
   caching, bounded resource use and reproducible manifests. Publish benchmark
   methods alongside results.
7. **Human usability and accessibility.** Test the primary tasks with
   representative users and assistive technologies. Automated checks remain
   necessary but are not human-validation evidence.
8. **Regulatory maintenance.** Bind claims to primary legislation and dated
   source records, identify unresolved legal interpretation, and require
   qualified review before presenting mappings as authoritative.

## Acceptance rules

- Every quantitative claim identifies its population, method, date and limits.
- Runtime parity is not detector validity.
- Synthetic performance is not real-world performance.
- One reviewer is not independent ground truth.
- Generated governance artefacts remain reviewer-completable scaffolds.
- Public releases contain no private operating records or machine identity.

## Known unknowns

- Real-world precision and recall across languages and application domains.
- Inter-rater agreement for legal-risk indicator labels.
- Whether users understand the distinction between an indicator and a legal
  determination.
- Generalisation under code generation, wrappers, indirection and framework
  changes.
- Performance on large monorepositories under cold and warm cache conditions.

The source appraisal and resulting implementation decisions are recorded in
[`RESEARCH_BASIS_2026-08-25.md`](RESEARCH_BASIS_2026-08-25.md).
