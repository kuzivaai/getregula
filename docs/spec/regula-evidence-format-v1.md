# Regula Evidence Format v1

**Status:** Stable. Frozen for 1.x minor series.
**Version:** 1.1
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

`audit-trail.json` MUST be project-scoped: generators MUST NOT embed
audit events from any project other than the packed one. Generators
SHOULD declare the scope with a `scope: "project"` field alongside the
event payload; consumers MUST ignore fields they do not recognise.

### 3.1 SME simplified form

Where `regula conform --sme` is used (Article 11(1) second subparagraph),
the pack is a **single file** at `pack_root/annex-iv-sme-simplified.md`
plus `manifest.json`. The manifest's `form` field MUST be
`"sme_simplified_annex_iv"` (§4).

### 3.2 Bundle format

When a pack is distributed as an archive, it is a ZIP file with extension
`.regula.zip` containing the pack directory at the root. Consumers MUST
support both unzipped and zipped input to `regula verify`.

### 3.3 Optional DPV-AIAct machine-readable export (informative)

A pack MAY include an optional `09-dpv-aiact.jsonld` artefact: the risk
indication serialised as **JSON-LD** and tagged with concept IRIs from the
**DPVCG EU-AIAct vocabulary** (the W3C Data Privacy Vocabularies and Controls
Community Group's "EU-AIAct" extension, namespace
`https://w3id.org/dpv/legal/eu/aiact#`). It lets RDF/GRC tooling ingest the
result without Regula.

This artefact is **off by default** (`regula evidence-pack --dpv` opts in), so
its presence never changes a default pack's `manifest.json` byte-for-byte. When
present it is listed in the manifest `files[]` array and hashed like any other
file; per §4.3, consumers MUST ignore artefacts they do not recognise.

Honesty constraints on this artefact (normative for Regula generators):

- The vocabulary is a **W3C Community Group report, NOT a ratified W3C
  Standard.** The artefact MUST describe itself as *aligned to* the DPVCG
  EU-AIAct vocabulary, never as "the AI Act standard" or "standards-compliant".
- Every emitted concept IRI MUST be a real term in the referenced vocabulary
  version. Generators MUST NOT invent IRIs; where no vocabulary concept exists
  (e.g. Article 5(1)(i), added by the Digital Omnibus after the vocabulary
  version, or non-EU regimes such as the Korea AI Basic Act / Colorado
  SB 26-189), the artefact MUST state the gap rather than assert a nearest EU
  concept.
- The artefact is risk **indication**, not classification or conformity
  determination, and MUST carry that disclaimer.

## 4. Manifest schema (normative)

`manifest.json` is the canonical integrity record. Consumers MUST NOT trust
any file in the pack that is not listed in the manifest.

### 4.1 Required fields

| Field | Type | Description |
|---|---|---|
| `format` | string | MUST equal `"regula.evidence.v1"` for this spec version |
| `format_version` | string | MUST be `"1.0"` for manifests that use only the v1.0-defined fields, or `"1.1"` for manifests that use any v1.1 optional block (`signing`, `timestamp_authority`). See §4.3 for the block-to-version mapping. |
| `schema_uri` | string | URL to the JSON Schema for this format version |
| `regula_version` | string | The Regula version that generated the pack (semver, e.g. `"1.7.4"`) |
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

### 4.3 Optional fields

Consumers MUST accept the following optional fields and MUST NOT reject the
manifest if they are absent or unrecognised:

- `form` (string) — e.g. `"sme_simplified_annex_iv"`, `"full_annex_iv"`
- `interim_format_disclosure` (string) — free text disclosure
- `signing` (object) — Ed25519 signature over the canonical manifest (§4.5, added in v1.1)
- `timestamp_authority` (object) — RFC 3161 timestamp token (reserved; lands in v1.1 alongside signing)
- `engagement` (object) — consultant engagement metadata: `client`,
  `prepared_by`, `reference` (all strings, all optional, each ≤200
  characters). Present only when the producer configured engagement
  metadata (via the `engagement:` section of `regula-policy.yaml` or
  the `--client`/`--prepared-by`/`--engagement-ref` flags). Because the
  block sits inside the manifest, signatures and timestamps cover it.
  It does not affect `format_version`: a v1.0 manifest MAY carry it.

A manifest that uses any of the v1.1 fields MUST set `format_version` to
`"1.1"`. v1.0 manifests carry only the v1.0-defined fields and omit the
signing block.

### 4.4 Example

```json
{
  "format": "regula.evidence.v1",
  "format_version": "1.0",
  "schema_uri": "https://getregula.com/spec/regula.manifest.v1.schema.json",
  "regula_version": "1.7.4",
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

### 4.5 Signing block (v1.1)

A v1.1 pack MAY embed an Ed25519 signature over the canonical manifest JSON.

#### 4.5.1 Canonical form

The bytes that a signature covers are produced by:

1. Take the manifest object.
2. Remove the following keys entirely (not just empty them):
   - `signing`
   - `timestamp_authority`

   These are "post-canonical" blocks — they are added after the canonical
   bytes are fixed, so they must be excluded at serialisation time or a
   subsequent timestamp would invalidate the signature.

3. Serialise with:

   ```python
   json.dumps(manifest_stripped, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
   ```

   i.e. sorted keys, no whitespace, UTF-8. This canonical form is stable
   across producers and languages: the same manifest always produces the
   same bytes, regardless of key order in the source object.

Producers MUST NOT modify any field other than the post-canonical set
after signing. Verifiers MUST reproduce this canonical form exactly
before calling the signature verification routine.

#### 4.5.2 Signing block structure

```json
{
  "signing": {
    "algorithm": "ed25519",
    "canonical_serialization": "json-sort-keys-no-whitespace-utf8",
    "signature": "<base64(ed25519_signature)>",
    "public_key": "<base64(SubjectPublicKeyInfo PEM)>"
  }
}
```

- `algorithm` MUST be `"ed25519"` in v1.1.
- `canonical_serialization` MUST be `"json-sort-keys-no-whitespace-utf8"` in v1.1.
- `signature` is the raw 64-byte Ed25519 signature, base64-encoded.
- `public_key` is the signer's public key, serialised as a PEM-encoded
  `SubjectPublicKeyInfo` object, then base64-encoded again for clean
  JSON embedding. Consumers decode the outer base64 first, then load
  the PEM with any standard crypto library.

#### 4.5.3 Verification behaviour

A conforming verifier MUST:

1. If no `signing` block is present, proceed without signature verification.
   Under `--strict`, SHOULD emit a warning (unsigned provenance) but
   MUST NOT fail solely on absence.
2. If a `signing` block is present:
   - Check `algorithm == "ed25519"` and
     `canonical_serialization == "json-sort-keys-no-whitespace-utf8"`.
     Unknown values → fail.
   - Reconstruct the canonical form (§4.5.1).
   - Call the Ed25519 verify primitive on (signature, public_key, canonical).
   - Invalid signature → FAIL regardless of `--strict`.
   - Valid signature → record `signature_status: "VERIFIED"` in the
     verify report.
3. If the verifier cannot perform Ed25519 verification (no crypto
   library installed), it MUST warn with
   `signature_status: "UNVERIFIABLE"` and MUST NOT claim the pack
   is signed or unsigned. Under `--strict`, treat as failure.

#### 4.5.4 Key management (informative)

The reference implementation stores a user's Ed25519 private key at
`~/.regula/signing.key` (PEM, PKCS8, no passphrase) and the matching
public key at `~/.regula/signing.key.pub`. The location can be overridden
via `--signing-key <path>` or the `REGULA_SIGNING_KEY` environment
variable. Keys are generated on first `--sign` use.

Users who rely on a signed pack as provenance SHOULD back up the
private key separately and consider rotating it on a defined cadence
(e.g. per product release). Public-key distribution is out of scope for
this spec; organisations can publish signing keys via repo README, a
`.well-known/regula-signing-keys.pem` endpoint, or any existing PKI.

### 4.6 Timestamp block (v1.1)

A v1.1 pack MAY carry an RFC 3161 `timestamp_authority` block proving
that the signed canonical manifest existed at a given moment. The
timestamp complements the signature: signing binds `who`, timestamping
binds `when`.

#### 4.6.1 What is timestamped

The TSA request is built over the **canonical form defined in §4.5.1**
— i.e. the manifest with the `signing` block stripped, serialised with
sorted keys and no whitespace. A timestamp is therefore valid for the
unsigned canonical state; a valid signature over the same canonical
form, combined with a valid timestamp, gives "this content existed at
time T and was signed by key K".

Producers SHOULD add the timestamp AFTER signing (so the canonical form
is identical to what the signature covers).

#### 4.6.2 Block structure

```json
{
  "timestamp_authority": {
    "format": "rfc3161",
    "hash_algorithm": "sha256",
    "message_imprint": "<hex sha256 of canonical manifest>",
    "tsa_url": "https://freetsa.org/tsr",
    "requested_at": "2026-04-16T16:00:00+00:00",
    "token": "<base64-encoded TimeStampToken (CMS ContentInfo)>",
    "gen_time": "2026-04-16T15:59:58+00:00",
    "tsa_name": "FreeTSA",
    "chain_verified": false
  }
}
```

- `format` MUST be `"rfc3161"` in v1.1.
- `hash_algorithm` MUST be `"sha256"` in v1.1.
- `message_imprint` is the lowercase hex SHA-256 of the canonical
  manifest form (§4.5.1).
- `token` is a base64-encoded RFC 3161 TimeStampToken — a CMS
  ContentInfo wrapping SignedData wrapping TSTInfo. Consumers decode
  the base64 and parse with any RFC 3161-aware library.
- `gen_time` is the TSA's own timestamp from inside the token, copied
  out of the TSTInfo for quick reading without an ASN.1 decode.
- `chain_verified` records whether the **producer** validated the TSA
  signer-cert chain when the token was obtained. Producers set this to
  `false`: chain validation is a verify-time concern that depends on the
  consumer's trust anchor, not the producer's. A verifier MUST NOT treat
  this field as an assertion about the chain — see §4.6.3
  (`CHAIN_VERIFIED`) for the verify-time check and §4.6.4 for its limits.

#### 4.6.3 Verifier behaviour

A conforming verifier MUST:

1. If no `timestamp_authority` block is present, proceed without
   timestamp verification. Under `--strict`, SHOULD emit a warning but
   MUST NOT fail solely on absence.
2. If the block is present:
   - Check `format == "rfc3161"` and `hash_algorithm == "sha256"`. Unknown
     values → fail.
   - Reconstruct the canonical form (§4.5.1) from the manifest.
   - Base64-decode `token`, parse as RFC 3161 TimeStampToken, extract
     the `messageImprint.hashedMessage`.
   - If the extracted imprint ≠ SHA-256(canonical form) → FAIL regardless
     of `--strict`.
   - Otherwise, verify the token's PKCS#7 SignedData signature (RFC 5652
     §5.4) and record the **strongest status actually proven**, never more:

     | `timestamp_status` | What has been proven |
     |---|---|
     | `HASH_MATCHED` | The `messageImprint` matches the canonical form. The token binds to THIS manifest, but its signature was not evaluated, so `gen_time` is **not** authenticated. |
     | `SIGNATURE_VERIFIED` | The above, plus the SignedData signature verifies against the certificate embedded in the token, the signed attributes (`contentType`, `messageDigest`) bind that signature to this exact TSTInfo, and the certificate carries the critical `id-kp-timeStamping` EKU (RFC 3161 §2.3). The signer's **identity** remains self-asserted — nothing anchors that certificate. |
     | `CHAIN_VERIFIED` | The above, plus the signer certificate chains to a **caller-supplied** trust anchor and both certificates were valid at `gen_time`. |

     A verifier MUST NOT report a plain `"VERIFIED"` for timestamps. Each
     status MUST be accompanied by a `timestamp_detail` stating what was
     **not** checked (see §4.6.4).
   - If the imprint matches but the signature is **provably bad** —
     it fails to verify, the `messageDigest` signed attribute does not
     match the encapsulated TSTInfo, the `contentType` is not
     `id-ct-TSTInfo`, or the EKU requirement is violated — the verifier
     MUST record `timestamp_status: "INVALID"` and FAIL. A token that
     asserts provenance it cannot back is worse than no token.
3. If the verifier cannot **evaluate** the signature — no ASN.1 or crypto
   library installed, no embedded signer certificate, no signed
   attributes, an unimplemented signature algorithm, or a digest the
   verifier declines to vouch for (e.g. SHA-1) — it MUST NOT fail on that
   basis alone. Absence of evaluation is not evidence of tampering, and
   failing here would reject packs from a conforming TSA whose algorithms
   the verifier simply does not implement. It MUST instead retain the
   hash-only verdict (`HASH_MATCHED`), state the reason in
   `timestamp_detail`, and emit a warning. If no ASN.1 library is present
   at all it MUST report `timestamp_status: "UNVERIFIABLE"` and MUST NOT
   claim the pack is or is not timestamped. Under `--strict`, treat
   `UNVERIFIABLE` as failure.

#### 4.6.4 Trust boundaries (informative)

The verifier checks that the TSA's embedded hash matches what we claim to
have submitted, and — where it can — that the token's own signature
verifies. What it does **not** check depends on the status reached:

At `HASH_MATCHED`, none of the following are checked:

- Whether the token's signature cryptographically verifies.
- Whether the TSA signer certificate is trusted or was valid at `gen_time`.

At `SIGNATURE_VERIFIED`, the signature and the `id-kp-timeStamping` EKU
have been checked, but:

- The signer certificate is **self-asserted by the token**. Anyone can
  mint a certificate, sign a token with it, and reach this status. It
  proves the token is internally consistent and untampered — not that a
  TSA you trust issued it. Supply `--tsa-trust-anchor` to bind identity.

At `CHAIN_VERIFIED`, additionally the signer chains to the supplied
anchor and both certs were valid at `gen_time`, but **still not**:

- **Revocation.** No CRL or OCSP is consulted. Regula's core is
  zero-network by design, so a revocation check cannot be performed
  offline. A revoked TSA certificate will still reach `CHAIN_VERIFIED`.
- **Full RFC 5280 path validation.** No name constraints, no policy
  mapping or policy qualifiers, and no intermediate chain building — the
  supplied anchor must be the signer's direct issuer.

A consumer needing guarantees beyond these MUST validate the token with a
dedicated RFC 3161 tool against a maintained trust store.

Consumers with a higher trust bar (e.g. notified-body audit submission)
SHOULD run the raw `token` bytes through a dedicated RFC 3161 verifier
such as `openssl ts -verify` or the signer's own CLI. The base64
token in the block is the exact byte sequence such a tool expects.

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
  "omnibus_status": "provisional agreement 2026-05-07, EP approved 2026-06-16, Council approved 2026-06-29; pending OJ publication",
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
  "pack_regula_version": "1.7.4",
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

For attacker-resistant tamper detection, pair a v1 pack with one of:

- **Embedded Ed25519 signature** — `--sign` in the reference implementation
  produces a v1.1 manifest that carries an Ed25519 signature over the
  canonical manifest JSON (§4.5). Tampering after signing is detectable
  with the signer's public key.
- **RFC 3161 timestamp** — an external TSA token asserting that the
  manifest hash existed at a given time. Lands alongside signing in v1.1.
- **Public commit** — commit the pack to a public Git repository at a known
  ref; the external git history provides ordering evidence.

In v1.1, `signing` and `timestamp_authority` are optional blocks per §4.3
and MAY be combined (sign, then timestamp the signed canonical form).

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

### v1.1 (2026-04-16)
- Adds the optional signing block (§4.5) — Ed25519 signature over the
  canonical manifest JSON, with a stable canonical-serialisation tag
  so third-party implementations can reproduce the signed bytes.
- Defines verifier behaviour for signed, unsigned, and unverifiable
  manifests (§4.5.3).
- Adds the optional timestamp block (§4.6) — RFC 3161 TimeStampToken
  over the canonical manifest form. Reference verifier checks that the
  TSA's embedded hash matches what the manifest claims; it does NOT
  validate the TSA signer-cert chain (out of scope in v1.1 — consumers
  with a higher trust bar can run the raw token through `openssl ts`).
- Defines verifier behaviour for timestamped, un-timestamped, and
  unverifiable cases (§4.6.3).
- Manifests that use either optional block MUST set `format_version`
  to `"1.1"`. v1.0 manifests remain valid as-is.
- No breaking changes to §3, §4.1, §4.2, §5, §6, §7.1.

### v1.0 (2026-04-16)
- Initial stable release.
- Freezes manifest fields (§4.1), file record schema (§4.2), section
  layout (§3), and verification algorithm (§7.1) for the 1.x series.
- Leaves signing + timestamp as reserved optional fields (§4.3).
