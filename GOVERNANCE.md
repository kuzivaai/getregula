# Governance

This document exists because enterprise buyers and security reviewers ask
these questions before adopting a tool, and the honest answers are short.
It satisfies OSPS Baseline OSPS-GV-01.01 and OSPS-GV-01.02 (a documented
list of members with access to sensitive resources, and their roles).

## Who maintains Regula

**One person.** Regula currently has a single maintainer. This is a material
bus-factor risk, so access and release controls are stated without publishing
the maintainer's personal identity.

| Resource | Holder | Notes |
|---|---|---|
| GitHub repository admin | Repository owner account | Sole admin |
| PyPI project `regula-ai` | Project owner account | Published via GitHub Actions Trusted Publishing (OIDC), not a stored API token |
| Domain `getregula.com` | Project owner | |
| Crash-reporting endpoint | none shipped | Published builds contain no endpoint; see `SECURITY.md` |

There are no other maintainers, no organisation, and no foundation.
Automated accounts (`dependabot`, `github-actions`) hold no credentials and
cannot approve or release.

## What that means for you — stated plainly

**Bus factor is one.** If the maintainer stops, releases stop. We are not
going to dress this up: it is the single largest adoption risk, and it is
the reason for the mitigations below rather than a reason to ignore it.

What limits the damage:

- **The code is open** under Apache-2.0 OR EUPL-1.2. Anyone can fork and
  continue. Detection rules are separately licensed
  (`LicenseRef-DRL-1.1`) — see `docs/LICENSE.Detection.Rules.md`.
- **Your data is local.** Regula runs on your machine and makes no network
  calls in its core scan. If the project were abandoned tomorrow, an
  installed copy keeps working, and nothing you scanned was ever held by
  us. There is no service to shut down and no account to lose.
- **Releases are verifiable without trusting us.** Published artefacts
  carry PyPI attestations (SLSA v1.0 Build Level 2) tying each file to the
  GitHub Actions workflow that built it.

What we cannot claim:

- **We are OSPS Baseline Level 1**, and structurally cannot reach Level 2,
  which requires at least two maintainers. Stated here so it is not
  discovered later.
- No third-party security audit or penetration test has been performed.
- There is no funded support contract or response-time guarantee. The
  security disclosure SLA in `SECURITY.md` is a good-faith commitment by
  one person, not an underwritten obligation.

## Decision-making

Decisions are made by the maintainer. Where a change affects a published
claim, the standard is in `docs/TRUST.md`: quantitative claims identify their
method, scope and known limits, and a claim that cannot be verified is removed
rather than softened.

Two rules constrain the maintainer as much as contributors:

1. **Security alerts are never dismissed or suppressed** — not through the
   GitHub UI, not with inline suppression comments, not via scanner
   configuration, and not by rewriting correct code until a scanner goes
   quiet. If a finding is a false positive, it stays open with the
   reasoning recorded publicly.
2. **Corrections are published, not quietly patched.** When a claim in
   `docs/TRUST.md` or the README turns out to be wrong, it is corrected
   with a dated notice. See §8.2 of `docs/TRUST.md` for a worked example.

## Contributing

See `CONTRIBUTING.md`. Contributions are welcome and reviewed by the
maintainer. Because there is one maintainer, a contribution cannot receive
independent review by a second person — a limitation OSPS Baseline Level 3
would require us to fix, and which we cannot fix alone.

Non-code contribution is genuinely valuable here: regulatory content
currency, jurisdiction coverage, implementation guidance, and
documentation are the areas where the project is most constrained.

## Succession

There is no formal succession plan. If you depend on Regula commercially
and this matters to you, open an issue — a documented handover
arrangement is worth building with someone who needs it rather than
inventing in the abstract.

## Reporting security issues

See `SECURITY.md` in the repository root. Do not use public issues for
vulnerability reports.
