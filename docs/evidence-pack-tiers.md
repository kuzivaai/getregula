# Evidence Pack Tiers (Internal — Not Yet Public)

Status: Prepared, not launched. Launch trigger: enterprise procurement
starts requiring AI Act evidence, OR first enforcement action, OR
organic demand from CLI users asking for paid reports.

## Tiers

| Tier | Price | What's included | CLI command |
|------|-------|----------------|-------------|
| Free | EUR 0 | Scan results, gap analysis, risk classification (current behaviour) | `regula check .` + `regula gap .` |
| Starter | EUR 49 | Signed evidence pack with SHA-256 integrity, Annex IV scaffold, compliance score | `regula evidence-pack --sign .` |
| Professional | EUR 149 | Everything in Starter + conformity assessment pack, Declaration of Conformity template, remediation plan, CycloneDX SBOM | `regula conform --sign .` |

## Implementation

- Payment via Stripe Payment Links (no server-side code)
- Three links created in Stripe Dashboard (not yet created — do this when launching)
- CLI outputs informational message pointing to pricing page after free scan
- No feature gating — all commands remain free. Payment is for the *branded, signed report* as a deliverable, not for access to the tool.

## Pricing rationale

- EUR 49: 1% of the EUR 5,000 minimum conformity assessment cost. Positioned as "try before you hire a consultant."
- EUR 149: 3% of the EUR 5,000 minimum. Includes everything a small company needs to hand to an auditor.
- Free remains free forever. The CLI is the distribution channel. The report is the product.
