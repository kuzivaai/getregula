# Public-claim integrity correction — 2026-08-01

## Evidence boundary and before-state inventory

Inventory population: the 13 active source surfaces in
`data/public_claim_surfaces.json`, plus released PyPI 1.9.0 METADATA. Historical
records are individually classified in that contract and are not broadly
directory-exempt. Before correction, the following class-level defects were
present:

| Claim ID | Exact before wording (representative) | Active surfaces | Disposition | Required boundary |
|---|---|---|---|---|
| PCI-LEGAL-1 | “classifies your system … and tells you which obligations apply” | README, wheel METADATA, machine-readable and site variants | CONTRADICTED by observable-input boundary | report code-observable indicators; human review; no legal classification/compliance determination |
| PCI-NET-1 | “zero network calls … no DPA required” | README, wheel, TRUST, site variants | UNVERIFIED / legal overclaim | local-first design only; optional network features disclosed; DPA is contextual |
| PCI-EVIDENCE-1 | “Auditor-ready evidence package” | README, wheel, machine-readable/site variants | UNVERIFIED | reviewer-completable hash-manifested scaffold |
| PCI-REPRO-1 | “Every metric … independently verified” | README, TRUST, wheel | CONTRADICTED by known exceptions and red merge blocker | selected generated facts and explicit limitations |
| PCI-RUNTIME-1 | “30 seconds” / “10 seconds” | README, site, wheel | CONTRADICTED as universal | no bound without named command, corpus, version and environment |
| PCI-SEC-1 | “0 known security findings” | TRUST, UAE page | CONTRADICTED by versioned open-alert inventory; alerts are not confirmed vulnerabilities | link inventory without converting alerts into vulnerabilities |
| PCI-COUNT-1 | stale test-count badge and prose | 11 manifest surfaces | STALE after benchmark tests | regenerate only after all tests are final |

The active-surface contract was created during correction, so it has no
before-state hash. Its post-correction SHA-256 is recorded below. The fail-before control
`python3 -m pytest tests/test_public_claim_integrity.py -q` returned exit 1:
3 failed, 4 passed; it found 27 prohibited active-surface class occurrences,
missing EN/DE/PT-BR limitations, and prohibited README copy in package metadata.

## Primary sources retrieved 2026-08-01

- PyPI JSON, `https://pypi.org/pypi/regula-ai/json`: version 1.9.0,
  `Requires-Python >=3.10`, optional `Requires-Dist` entries and no unconditional
  `Requires-Dist`. The downloaded published wheel SHA-256 was
  `01cde674270adcf08acedf1b79e003c6f083c464944cf158582a14afde93cff3`.
- Regulation (EU) 2024/1689, EUR-Lex CELEX 32024R1689. Article 3(12) defines
  intended purpose by reference to the context and conditions of use; Article 6
  and Article 6(3) make high-risk treatment context-sensitive.
- Regulation (EU) 2026/1744, EUR-Lex OJ L 2026/1744, published 24 July 2026.
  Article 113 as amended applies Chapter III sections 1–3 from 2 December 2027
  for Article 6(2)/Annex III and 2 August 2028 for Article 6(1)/Annex I; its
  Article 50 transition gives pre-2-August-2026 generative systems until
  2 December 2026 for Article 50(2).
- Regulation (EU) 2024/1689 Article 40(1), corroborated by the Commission AI Act
  Service Desk: presumption requires the harmonised standard's reference to be
  published in the Official Journal and extends only to covered requirements.
  No exact OJ citation for the named EN work items was established in this unit;
  no presumption claim is retained.

## Frozen correction contract

- Legal: code observations, declared-context questions, provision links and
  human escalation only; no legal classification, compliance determination or
  applicable-obligation determination.
- Network/privacy/dependencies: distinguish zero required core third-party
  dependencies from optional extras; disclose optional network paths; make no
  DPA conclusion. No universal negative is retained because OS-level tracing
  was not available and no positive instrumentation control was completed.
- Evidence: reviewer-completable scaffolds with integrity metadata, not auditor
  completeness or legal sufficiency.
- Accuracy/runtime/security/counts: version and corpus bound; no universal
  runtime; open alerts remain visible without being called vulnerabilities;
  mutable counts are generated last.

## Correction status

Source corrections cover the contract population as corrected after independent
review, including package metadata and MCP declarations. German and Brazilian
Portuguese limitation text is intentionally short and factual; competent-
speaker legal review remains OWNER_GATED. Live PyPI and website surfaces remain
unchanged until an owner-authorised release/deployment. commercial_v1 remains
STOP and PRODUCT_PILOT_STATUS remains NOT_APPROVED.

The final measured pytest-collected canonical is recorded, with its per-file
decomposition, in `data/site_facts.json`; it was reproduced with
`python3 -m pytest tests/ --collect-only -q` and
`python3 scripts/site_facts.py`. All 11 manifest count surfaces were updated by
`python3 scripts/cascade_count.py --apply`. The retained Git diff shows the
increase from the previous canonical, the commercial_v1 additions, and the
seven new claim-integrity tests without turning this dated report into a
twelfth mutable-count surface. Contract SHA-256:
`2b98200b498813242d9a951330743837da051877ed3ca9d33aae56fa445a805f`.
