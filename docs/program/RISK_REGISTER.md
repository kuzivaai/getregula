# RISK_REGISTER

Status: Verified and Updated (EDPIP Phase 4, 2026-07-13).

| ID | Risk | Severity | Evidence tier | Phase | Status |
|---|---|---|---|---|---|
| R1 | `action.yml` empty-SARIF fallback + SARIF-derived counting mask scan failure as "0 findings / PASS", disarming the `fail-on-prohibited` gate. Directly threatens the tool's core safety promise. | High | reproduced | 3 | resolved (Fix implemented in Phase 3/4; DEF-004) |
| R2 | Public "verified numbers" surface contains unverified/inconsistent numbers. Undermines the product's trust positioning. | High | reproduced | 1 | resolved (Fix implemented in Phase 4; DEF-001) |
| R3 | Network-capable modules (telemetry/sentry, feed, indexnow, timestamp, adoption_pulse, dev_sentiment) vs "zero data transmission / no data leaves the machine" marketing. | Medium | source | 6 | resolved (Marketing copy accurately updated to "local-first execution" in Phase 4) |
| R4 | `cli.py` monolith + AGENTS.md "do not refactor" constraint limits structural remediation; solo maintainer. | Low-medium | source | ongoing | open |
| R5 | Committed generated artifact (site_facts.json) drifts silently because the auditor regenerates in-memory. Erodes confidence in "generated" artifacts generally. | Medium | reproduced | 1 | resolved (ci.yaml explicitly guards against drift; DEF-002) |

## Notes

- R1, R2, R3, and R5 were resolved cleanly and defensively without breaking the architecture.
- Severity/priority reflect impact on the product's stated value (trustworthy,
  reproducible, safety-gating), not code volume.
