# RISK_REGISTER

Status: DRAFT (uncommitted). Risks identified in Phases 0–1.

| ID | Risk | Severity | Evidence tier | Phase | Status |
|---|---|---|---|---|---|
| R1 | `action.yml` empty-SARIF fallback + SARIF-derived counting mask scan failure as "0 findings / PASS", disarming the `fail-on-prohibited` gate. Directly threatens the tool's core safety promise. | High | **reproduced 2026-07-13** | 3 | substantiated (see DEF-004) |
| R2 | Public "verified numbers" surface contains unverified/inconsistent numbers (tests: 2543 vs 2543 vs 2519). Undermines the product's trust positioning. | High | reproduced | 1 | substantiated (see DEF-001) |
| R3 | Network-capable modules (telemetry/sentry, feed, indexnow, timestamp, adoption_pulse, dev_sentiment) vs "zero data transmission / no data leaves the machine" marketing. Requires per-mode verification. | Medium | source (not yet analyzed) | 6 | open |
| R4 | `cli.py` monolith + AGENTS.md "do not refactor" constraint limits structural remediation; solo maintainer. | Low-medium | source | ongoing | open |
| R5 | Committed generated artifact (site_facts.json) drifts silently because the auditor regenerates in-memory. Erodes confidence in "generated" artifacts generally. | Medium | reproduced | 1 | open (see DEF-002) |

## Notes

- R1 is the highest-priority open item and is investigation-only until a fix phase is
  explicitly approved.
- R2 and R5 are addressable together by extending the existing `site_facts` +
  `claim_auditor` mechanism (low-risk, high-value), pending approval of an
  implementation phase and the canonical definition (already selected: `pytest
  --collect-only` total for the tests number).
- Severity/priority reflect impact on the product's stated value (trustworthy,
  reproducible, safety-gating), not code volume.
