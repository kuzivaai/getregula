# Regula Evidence Format v1

**Status:** Stable. Frozen for 1.x minor series.
**Version:** 1.0
**Specification ID:** `regula.evidence.v1`
**Last updated:** 2026-04-16

The Regula Evidence Format (REF) is the on-disk layout and JSON schema
produced by `regula conform`. It is a portable, integrity-verified,
Article 43 / Annex IV-aligned evidence pack intended for:

- Audit submission to a notified body (high-risk provider conformity assessment).
- Internal compliance review (ISO 42001 Clause 9.2 / 9.3 audits).
- Hand-off to downstream reviewers (legal counsel, GRC platform, customer
  due-diligence questionnaire).
- Mechanical verification — any consumer can reproduce the pack's integrity
  state without re-running Regula.

This spec describes **v1**. Additive fields may be introduced as v1.1, v1.2;
breaking changes bump to v2.

---

## 1. Scope

A Regula Evidence Pack covers **one project** (one AI system). Packs that
cover multiple systems are explicitly out of scope in v1. Downstream tooling
can compose multiple v1 packs into a higher-level bundle, but the format
defined here is single-project.

A v1 pack consists of:

1. A **pack directory** with a fixed section layout (§3).
2. A top-level `manifest.json` conforming to the schema in §4.
3. A `00-assessment-summary.json` and `README.md` at pack root.
4. Per-article sub-directories with at minimum an `evidence.json` and a
   `coverage.json`.
5. Optional article-specific artefacts (audit-trail, SBOM, Annex IV draft,
   oversight analysis — see §3).
6. Optional `.zip` bundle wrapping the directory for transport.

All text files are UTF-8. All JSON files are indented with two spaces. All
timestamps are RFC 3339 / ISO 8601 with timezone offset. All hashes are
SHA-256, lowercase hex.

## 2. File naming and encoding

- **Directory names** follow `NN-slug` where `NN` is a two-digit numeric
  prefix (zero-padded) and `slug` is kebab-case. Articles use
  `NN-<article-slug>-art<N>` (e.g. `02-risk-management-art9`).
- **Filenames** inside sub-directories are lowercase, kebab-case, with
  one of these suffixes: `.json`, `.md`, `.xml`.
- **Line endings:** LF (Unix). Consumers MUST accept CRLF but SHOULD emit LF.

## 3. Section layout (normative)

A v1 pack directory contains — in this order:

| Path | Kind | Purpose |
|---|---|---|
| `00-assessment-summary.json` | json | Top-level readiness + article scores (§5) |
| `README.md` | markdown | Human-readable pack guide |
| `manifest.json` | json | Integrity manifest (§4) |
| `01-risk-classification/` | dir | `findings.json` + `coverage.json` |
| `02-risk-management-art9/` | dir | `evidence.json` + `coverage.json` |
| `03-data-governance-art10/` | dir | `evidence.json` + `coverage.json` |
| `04-technical-documentation-art11/` | dir | `annex-iv-draft.md` + `evidence.json` + `coverage.json` |
| `05-record-keeping-art12/` | dir | `audit-trail.json` + `evidence.json` + `coverage.json` |
| `06-transparency-art13/` | dir | `evidence.json` + `coverage.json` |
| `07-human-oversight-art14/` | dir | `oversight-analysis.json` + `evidence.json` + `coverage.json` |
| `08-accuracy-robustness-art15/` | dir | `sbom.json` + `evidence.json` + `coverage.json` |
| `09-supply-chain/` | dir | `dependency-report.json` + `sbom.json` |
| `10-declaration-of-conformity/` | dir | `declaration-template.md` |
| `11-remediation/` | dir | `remediation-plan.md` |

Each per-article sub-directory MUST contain at least `evidence.json` and
`coverage.json`. Additional artefacts (e.g. `annex-iv-draft.md`,
`audit-trail.json`, `sbom.json`, `oversight-analysis.json`) are
article-specific and described in their section's `evidence.json`.

### 3.1 SME simplified form

Where `regula conform --sme` is used (Article 11(1) second subparagraph),
the pack is a **single file** at `pack_root/annex-iv-sme-simplified.md`
plus `manifest.json`. The manifest's `form` field MUST be
`"sme_simplified_annex_iv"` (§4).

### 3.2 Bundle format

When a pack is distributed as an archive, it is a ZIP file with extension
`.regula.zip` containing the pack directory at the root. Consumers MUST
support both unzipped and zipped input to `regula verify`.

## 4. Manifest schema (normative)

`manifest.json` is the canonical integrity record. Consumers MUST NOT trust
any file in the pack that is not listed in the manifest.

### 4.1 Required fields

| Field | Type | Description |
|---|---|---|
| `format` | string | MUST equal `"regula.evidence.v1"` for this spec version |
| `format_version` | string | MUST equal `"1.0"` for the initial v1 release |
| `schema_uri` | string | URL to the JSON Schema for this format version |
| `regula_version` | string | The Regula version that generated the pack (semver, e.g. `"1.6.2"`) |
| `generated_at` | string | RFC 3339 timestamp with timezone |
| `project` | string | Project / system name |
| `project_directory` | string | Directory name scanned |
| `hash_algorithm` | string | MUST equal `"sha256"` in v1 |
| `files` | array | List of file records (§4.2) |

### 4.2 File record schema

Each entry in `files`:

| Field | Type | Description |
|---|---|---|
| `filename` | string | Path relative to the pack root, using `/` separators |
| `sha256` | string | Lowercase hex SHA-256 digest of file contents |
| `size_bytes` | integer | File size in bytes |

### 4.3 Optional fields (reserved for v1.x)

Consumers MUST accept the following optional fields and MUST NOT reject the
manifest if they are absent or unrecognised:

- `form` (string) — e.g. `"sme_simplified_annex_iv"`, `"full_annex_iv"`
- `interim_format_disclosure` (string) — free text disclosure
- `signing` (object) — reserved for future Ed25519 / cosign signatures
- `timestamp_authority` (object) — reserved for RFC 3161 timestamp tokens

### 4.4 Example

```json
{
  "format": "regula.evidence.v1",
  "format_version": "1.0",
  "schema_uri": "https://getregula.com/spec/regula.manifest.v1.schema.json",
  "regula_version": "1.6.2",
  "generated_at": "2026-04-16T14:43:31.035789+00:00",
  "project": "cv-screening-app",
  "project_directory": "cv-screening-app",
  "hash_algorithm": "sha256",
  "files": [
    {
      "filename": "01-risk-classification/findings.json",
      "sha256": "3fa919fd…",
      "size_bytes": 1395
    }
  ]
}
```

## 5. Assessment summary schema (normative)

`00-assessment-summary.json` at pack root:

| Field | Type | Description |
|---|---|---|
| `regula_version` | string | Regula version |
| `generated_at` | string | RFC 3339 timestamp |
| `project` | string | Project name |
| `conformity_type` | string | e.g. `"internal (Annex VI, Module A)"` |
| `overall_readiness` | string | Percentage as `"NN%"` |
| `articles` | array | Per-article readiness entries |
| `deadline` | object | Deadline summary (see §5.1) |
| `human_required` | array | Fields requiring human completion |
| `auto_generated` | array | Fields auto-filled from scan |

### 5.1 Deadline summary

```json
{
  "base_deadline": "2026-08-02",
  "omnibus_provisional_deadline": "2027-12-02",
  "omnibus_status": "not yet adopted (trilogue 2026-04-28)",
  "applicable_to_this_system": "high-risk" | "limited-risk" | "minimal-risk" | "prohibited"
}
```

## 6. Per-article files (informative)

### 6.1 evidence.json

Each `NN-<article>/evidence.json` MUST contain:

```json
{
  "article": 9,
  "article_title": "Risk management system",
  "indicators_found": ["..."],
  "evidence_files_generated": ["..."],
  "coverage_note": "Regula checks X; cannot check Y"
}
```

### 6.2 coverage.json

Each `NN-<article>/coverage.json` MUST contain:

```json
{
  "article": 9,
  "what_regula_checks": "...",
  "what_regula_cannot_check": "...",
  "framework_crosswalk": {
    "ISO_42001": "...",
    "NIST_AI_RMF": "...",
    "SOC2": "..."
  }
}
```

This is the **honesty field**. It explicitly lists what Regula does and does
not verify, so an auditor never mistakes a Regula "PASS" for full-article
conformity. The `what_regula_cannot_check` field is MANDATORY.

## 7. Integrity and verification

### 7.1 Verification algorithm

Given a pack path, a conforming verifier MUST:

1. Locate `manifest.json` at the pack root (or in a `.regula.zip` archive root).
2. Parse the manifest and check `format == "regula.evidence.v1"`. If the
   field is absent or different, emit a warning and proceed under best-effort
   v0 semantics unless `--strict` is set (fail in that case).
3. For each entry in `files`:
   - Resolve `filename` relative to pack root.
   - If missing: MISSING.
   - Else: compute SHA-256, compare with `sha256`. If equal: OK. If not: MODIFIED.
4. Report counts of `OK`, `MISSING`, `MODIFIED`.
5. Exit non-zero if any file is `MISSING` or `MODIFIED`.

### 7.2 Verification report (optional)

A verifier MAY emit a `regula.verify.v1.json` report alongside the pack:

```json
{
  "format": "regula.verify.v1",
  "format_version": "1.0",
  "pack_path": "path/to/pack",
  "verified_at": "2026-04-16T14:50:00+00:00",
  "verifier_version": "1.6.3",
  "pack_format": "regula.evidence.v1",
  "pack_regula_version": "1.6.2",
  "total": 26,
  "passed": 26,
  "failed": 0,
  "results": [
    {"filename": "01-risk-classification/findings.json", "status": "OK"}
  ]
}
```

### 7.3 Tamper detection

The v1 manifest protects against **accidental** corruption (truncation, line
ending conversion, re-serialisation) and **inattentive** modification
(editing a file after generation without updating the manifest). It does
NOT protect against a motivated attacker who can regenerate the whole pack.

For attacker-resistant tamper detection in v1.x, pair a v1 pack with one of:

- **Detached signature** — Ed25519 signature over the manifest's canonical
  JSON, published separately (reserved for v1.1).
- **External timestamp** — RFC 3161 timestamp token of the manifest's hash,
  from a trusted TSA (reserved for v1.1).
- **Public commit** — commit the pack to a public Git repository at a known
  ref; the external git history provides ordering evidence.

The v1 spec treats signing + timestamp as out-of-band additions that may
arrive in v1.1 without a breaking change (per §4.3 optional fields).

## 8. Compatibility with other formats

### 8.1 SPDX

The SBOM files in `08-accuracy-robustness-art15/sbom.json` and
`09-supply-chain/sbom.json` SHOULD be CycloneDX 1.6+ format. An SPDX 2.3
alternative MAY be provided at `09-supply-chain/sbom.spdx.json`.

### 8.2 NIST AI RMF, ISO 42001, SOC 2, others

Coverage mappings in `coverage.json` reference these frameworks by their
canonical identifiers. A consumer producing a multi-framework compliance
view (e.g. a GRC tool) can read these mappings directly.

### 8.3 EuConform Evidence Format

The Regula Evidence Format and the [EuConform Evidence
Format](https://github.com/Hiepler/EuConform/blob/main/docs/spec/README.md)
are **not interchangeable**. They target the same regulatory surface from
different tooling lineages and package information differently. A bridge
tool producing both formats from a single source is possible and would be
valuable to the OSS compliance ecosystem.

## 9. Versioning and stability

- v1.x is source-compatible: consumers written against v1.0 MUST continue
  to work against v1.x.
- Additive changes land as v1.1, v1.2, … with the `format_version` field
  incremented.
- Breaking changes (field removal, semantic changes, rename) bump to v2
  and land with a new `format` identifier (`regula.evidence.v2`).
- The `format` + `format_version` fields are the single source of truth
  for consumers deciding how to interpret a pack.

## 10. Reference implementation

The reference implementation lives in this repository:

- Producer: [`scripts/conform.py`](../../scripts/conform.py) — generates
  packs conforming to this spec.
- Verifier: [`scripts/cli_util.py:cmd_verify`](../../scripts/cli_util.py) —
  verifies packs against this spec.
- Schemas: [`docs/spec/regula.manifest.v1.schema.json`](regula.manifest.v1.schema.json).

Compatibility test fixtures for future implementations will land at
`tests/fixtures/evidence-packs-v1/` in a later release.

## 11. Licence

This specification is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
You may implement it freely in any tool. Attribution is appreciated but
not required (the spec stands on its own).

The reference implementation is licensed under `(MIT OR EUPL-1.2) AND
LicenseRef-DRL-1.1` — see the repository root `LICENSE.*` files.

---

## Changelog

### v1.0 (2026-04-16)
- Initial stable release.
- Freezes manifest fields (§4.1), file record schema (§4.2), section
  layout (§3), and verification algorithm (§7.1) for the 1.x series.
- Leaves signing + timestamp as reserved optional fields (§4.3).
