# Distribution listings register

Updated 24 August 2026. This file is the single register of where Regula is
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
| GitHub repository description | Corrected live 24 Aug 2026 to remove an absolute data-transmission claim. Current text: "Local code-observable AI-governance indicators for EU AI Act, South Korea AI Basic Act and Colorado review. Open-source Python CLI." |
| PyPI `regula-ai` | PUBLISHED, 2.0.0 (24 Aug 2026). Release workflow build, trusted publish, clean PyPI install and smoke tests passed. Independently downloaded GitHub assets match `SHA256SUMS`; clean wheel install reports 2.0.0 and passes 6/6 self-tests. PyPI Integrity records bind wheel SHA-256 `6b8e9a38b0d9c9cb18bb054b9b932a785dd3678e343f503aece406f2b41966d1` and sdist SHA-256 `3ef5b7e34436a8ce4e510927129944d223fb4ea650cfe29b4b42c8a1bbf0ed36` to the GitHub `release.yml` publisher. |
| GitHub Action (`action.yml`) | EXISTS and exercised by `.github/workflows/test-action.yml`; branding present. The Marketplace page is live and was world-checked 24 Aug 2026. The accessible public page does not expose a version string proving that the Marketplace recommendation moved from the owner-published 1.9.0 release. The new immutable `v2.0.0` and floating `v2` tags exist; `v1` is unchanged. Marketplace-version confirmation remains an owner/UI check, not an executed update claim. |
| MCP server (`scripts/mcp_server.py`) | EXISTS, stdio, stdlib-only. The official registry still serves immutable version 1.9.0 as active/latest (world-checked 24 Aug). The 2.0.0 `server.json` passes the registry's live validator, but publication returned HTTP 401 because the saved registry JWT expired. `mcp-publisher login github` produced a device-auth prompt; 2.0.0 is therefore BLOCKED_EXTERNAL_AUTH and has not been published. |
| VS Code extension | Recorded as published (v0.1.0, May 2026). Not re-verified this session; the 11 Aug 2026 audit records the extension as outside CI. Treat as unverified until checked against the live marketplace. |
| Hacker News | Submissions were already made (May 2026). Do not resubmit; this is a standing project rule. |
| dev.to | Articles published (May 2026 record; not re-verified this session). |
| Pre-commit hook | Configured (May 2026 record; not re-verified this session). |

## Prepared and held

Publishing to a registry or marketplace is authorised by the 19 August owner
directive after platform checks. A prepared action is still not an executed
one; platform authentication or acceptance remains a blocker where required.

### 1. Official MCP registry (registry.modelcontextprotocol.io)

- Artefact: `server.json` at the repository root, `$schema` 2025-12-11 (the
  schema version live registry entries carry, checked 14 Aug 2026), name
  `io.github.kuzivaai/regula`, PyPI package `regula-ai` 2.0.0, stdio
  transport.
- Ownership validation: the live `mcp-publisher validate` check passed for
  2.0.0 on 24 Aug; the 2.0.0 PyPI package and entry point are published and
  independently installed.
- Version discipline: the manifest's two version fields must equal
  `scripts/constants.py:VERSION`; enforced by
  `tests/test_source_of_truth.py::test_current_version_declared_consistently_everywhere`
  (control run 14 Aug 2026: a planted 9.9.9 package version fails the guard
  by name).
- Exact blocked action: complete `mcp-publisher login github` as `kuzivaai`,
  then run `mcp-publisher publish server.json` from the repository root and
  verify 2.0.0 through `/v0.1/servers`. Registry versions are immutable;
  status can be changed, but metadata remains accessible.

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
| 2026-08-19 | Registry/directory and editorial submissions | Owner directive | Authorised after platform/evidence checks; does not waive human platform-authentication or commercial-terms acceptance |

## Editorial submission register

Every row is one submission, not a reusable mass-mail list. `PREPARED_NOT_SENT`
means no external message or form submission occurred.

| Channel | Route world-checked | Version / asset | State | Follow-up / stop |
|---|---|---|---|---|
| Console.dev | `hello@console.dev`, primary selection page, 24 Aug | 2.0.0; CLI sample, release, trust/limits | PREPARED_NOT_SENT; external distribution halted pending production privacy-hotfix proof | One follow-up after 7 business days; stop after rejection or 14 days |
| AI Governance Library | editorial contact on primary About page, 24 Aug | Free open-source evidence workflow; disclose inactive commercial hypothesis | PREPARED_NOT_SENT; external distribution halted pending production privacy-hotfix proof; fit risk is its explicit no-hidden-funnel policy | One direct curation question; no follow-up after rejection |
| Python Bytes | `/home/contact` "Submit news", 24 Aug | PyPI 2.0.0 and reproducible Python CLI journey | PREPARED_NOT_SENT; external distribution halted pending production privacy-hotfix proof | One submission; no duplicate Talk Python pitch in the same cycle |
| Changelog News | `/news/submit`, primary site, 24 Aug | OSS release and falsifiable local sample | PREPARED_NOT_SENT; external distribution halted pending production privacy-hotfix proof | One news submission; episode request only after editorial interest |
