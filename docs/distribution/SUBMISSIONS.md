# Distribution listings register

Updated 14 August 2026. This file is the single register of where Regula is
listed, what is prepared, and what is held pending owner authorisation.

This version supersedes the May 2026 revision, whose copy-paste-ready drafts
carried claims the repository has since prohibited (risk-tier classification
presented as determination, absolute no-network claims, "audit-ready"
phrasing) and stale regulatory dates. Those drafts are withdrawn and must not
be reused; git history preserves them as a record. Only the copy in this
version is approved.

## Status register

"World-checked" means verified against the live external surface on the
stated date, not read from a repository record.

| Surface | Status |
|---|---|
| PyPI `regula-ai` | PUBLISHED, 1.9.0 (27 Jul 2026). World-checked 14 Aug 2026 via the PyPI JSON API: live version 1.9.0, and the `mcp-name: io.github.kuzivaai/regula` ownership marker is present on line 1 of the published package description. The description still shows the pre-14-Aug README headline; the repositioned headline reaches PyPI at the next release. |
| GitHub Action (`action.yml`) | EXISTS in the repository, exercised by `.github/workflows/test-action.yml`, branding present. LISTED on the GitHub Marketplace since 14 Aug 2026 (owner-published release v1.9.0 at 07:46:45Z with the Marketplace box ticked; world-checked the same day: the action page shows publisher kuzivaai, v1.9.0, categories Security and Code quality). Earlier the same day a Marketplace search had returned no kuzivaai action. The May 2026 revision of this file recorded the Marketplace listing as already done; either that record was wrong or the listing lapsed, and which of the two cannot be determined from here. The floating `v1` tag exists locally and on the remote and moves on each release (`.github/workflows/release.yml` header), so the `uses: kuzivaai/getregula@v1` examples resolve. |
| MCP server (`scripts/mcp_server.py`) | EXISTS, stdio, stdlib-only, tool-level errors flagged per the MCP error form since 14 Aug 2026. LISTED on the official MCP registry since 2026-08-14T06:56:16Z as `io.github.kuzivaai/regula` 1.9.0 (owner-executed publish; world-checked via the registry API the same day, count 1; see the authorisation ledger below). Earlier the same day the search had returned only an unrelated third-party server. |
| VS Code extension | Recorded as published (v0.1.0, May 2026). Not re-verified this session; the 11 Aug 2026 audit records the extension as outside CI. Treat as unverified until checked against the live marketplace. |
| Hacker News | Submissions were already made (May 2026). Do not resubmit; this is a standing project rule. |
| dev.to | Articles published (May 2026 record; not re-verified this session). |
| Pre-commit hook | Configured (May 2026 record; not re-verified this session). |

## Prepared and held

Publishing to a registry or marketplace is a distribution act and an owner
decision. Everything below is built and verifiable in the repository; nothing
has been submitted. Each item activates only on a dated owner authorisation
recorded in this file's authorisation ledger.

### 1. Official MCP registry (registry.modelcontextprotocol.io)

- Artefact: `server.json` at the repository root, `$schema` 2025-12-11 (the
  schema version live registry entries carry, checked 14 Aug 2026), name
  `io.github.kuzivaai/regula`, PyPI package `regula-ai` 1.9.0, stdio
  transport.
- Ownership validation: the registry verifies PyPI packages by finding the
  `mcp-name` marker in the published package description. Verified present in
  the live 1.9.0 package (see status register), so validation will run
  against the package already on PyPI; no new release is required first.
- Version discipline: the manifest's two version fields must equal
  `scripts/constants.py:VERSION`; enforced by
  `tests/test_source_of_truth.py::test_current_version_declared_consistently_everywhere`
  (control run 14 Aug 2026: a planted 9.9.9 package version fails the guard
  by name).
- Owner steps at authorisation: install `mcp-publisher`;
  `mcp-publisher login github` as the kuzivaai account;
  `mcp-publisher publish` from the repository root.

### 2. GitHub Marketplace (Actions)

- Artefact: `action.yml` is listing-ready (unique name "Regula AI Governance
  Check", description, `branding` icon `shield` colour `blue`).
- Owner steps at authorisation: repository Releases, draft a new release (or
  edit the latest), tick "Publish this Action to the GitHub Marketplace",
  choose a primary category (Code quality) and optionally a second
  (Security). GitHub requires the account to have two-factor authentication
  and to accept the Marketplace Developer Agreement on first listing.

### 3. Aggregator directories (Glama, mcp.so)

- Glama auto-indexes public GitHub MCP servers; a listing may appear without
  any action once the repository is discoverable, and appears faster once the
  official registry entry exists. mcp.so accepts submissions.
- Only the approved copy below may be used on any directory form.

## Approved listing copy (14 August 2026)

Deliberately free of counts and dates so it cannot go stale, and consistent
with the repository's prohibited-claims classes
(`scripts/public_surface_inventory.py`).

> Regula scans code locally for patterns that may need AI governance review
> under the EU AI Act, South Korea's AI Basic Act, and Colorado SB 26-189,
> records the deployment facts code cannot show, and reports insufficient
> information rather than inventing a score. Open source (Apache-2.0 /
> EUPL-1.2), offline-capable, no account required. Risk indication, not
> legal advice.

## Authorisation ledger

| Date | Surface | Authorised by | Record |
|---|---|---|---|
| 2026-08-14 | GitHub Marketplace | Owner, by publishing release v1.9.0 with "Publish this Action to the GitHub Marketplace" ticked | Listed as "Regula AI Governance Check", publisher kuzivaai, v1.9.0, categories Security and Code quality; verified on the action's Marketplace page 14 Aug 2026 |
| 2026-08-14 | Official MCP registry | Owner, by personally executing `mcp-publisher login github` and `mcp-publisher publish` | Listed as `io.github.kuzivaai/regula` 1.9.0, status active, publishedAt 2026-08-14T06:56:16Z; verified via the registry API (`/v0/servers?search=io.github.kuzivaai/regula`, count 1) |
