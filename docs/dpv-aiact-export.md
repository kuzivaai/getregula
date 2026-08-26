# DPV-AIAct machine-readable export

`regula dpv` exports a Regula scan's **risk indication** as **JSON-LD** tagged
with concept IRIs from the **DPVCG EU-AIAct vocabulary**, so that RDF and GRC
tooling can ingest the result without Regula in the loop.

> **Read this first.** This is risk **indication**, not classification,
> conformity assessment, or certification. The vocabulary it aligns to is a
> **W3C Community Group report — not a ratified W3C Standard.** The output says
> *aligned to* the DPVCG EU-AIAct vocabulary, never "the AI Act standard" or
> "standards-compliant". EU AI Act Article 6 requires contextual assessment
> that pattern matching cannot provide.

## What it is

The [DPVCG EU-AIAct vocabulary](https://w3c-cg.github.io/dpv/2.3/legal/eu/aiact/)
is the W3C Data Privacy Vocabularies and Controls Community Group's "EU-AIAct"
extension (DPV v2.3, namespace `https://w3id.org/dpv/legal/eu/aiact#`). It is an
RDF/OWL + SKOS vocabulary that encodes EU AI Act concepts: risk levels,
prohibited-practice categories (Article 5), Annex III high-risk areas, the
Article 6 high-risk routes, regulatory roles, and more.

`regula dpv` maps what a Regula scan already computes onto those concept IRIs:

| Regula output | DPV-AIAct concept |
|---|---|
| Prohibited tier | `eu-aiact:RiskLevelProhibited` + `eu-aiact:ProhibitedAISystem` |
| Article 5(1)(a)–(h) practice | `eu-aiact:ProhibitedAISystem-A5-1-a` … `-h` |
| High-risk tier | `eu-aiact:RiskLevelHigh` + `eu-aiact:HighRiskAISystem` |
| Annex III point (unambiguous, e.g. credit → 5(b)) | `eu-aiact:HighRiskAISystem-AnnexIII-5-b`, `-5-c`, `-5-d`, `-4-b`, `-2` |
| Annex I sectoral / safety component | `eu-aiact:HighRiskAISystem-A6-1` |
| Limited / transparency tier | `eu-aiact:RiskLevelTransparencyRequired` (Article 50) |
| Minimal tier | `eu-aiact:RiskLevelMinimal` |

## Usage

```bash
# Print JSON-LD for the current directory
regula dpv

# Name the system and write to a file
regula dpv --project ./my-app --name "My App" --output my-app.dpv.jsonld

# Include it as an optional artefact in an evidence pack (off by default)
regula evidence-pack --project . --dpv
# → adds 09-dpv-aiact.jsonld to the pack. Without --dpv the pack's manifest
#   is byte-identical to prior releases.
```

## What the output looks like

The document is a JSON-LD `@graph`. The first node is the scan result
(provenance, disclaimer, and the honest vocabulary-status block); each
subsequent node is a distinct detected indicator, typed with its DPV
concept(s) and linked from the scan node:

```json
{
  "@context": { "eu-aiact": "https://w3id.org/dpv/legal/eu/aiact#", "...": "..." },
  "@graph": [
    {
      "id": "urn:regula:dpv:scan:my-app",
      "type": "regula:ScanResult",
      "regula:highestRiskLevel": "eu-aiact:RiskLevelHigh",
      "regula:disclaimer": "Regula indicates EU AI Act risk; it does not certify compliance. ...",
      "regula:vocabulary": { "regula:standardStatus": "W3C Community Group report (not a ratified W3C Standard)", "...": "..." }
    },
    {
      "id": "urn:regula:dpv:indicator:1-highriskaisystem-annexiii-5-b",
      "type": ["eu-aiact:AISystem", "eu-aiact:HighRiskAISystem", "eu-aiact:HighRiskAISystem-AnnexIII-5-b"],
      "hasRiskLevel": "eu-aiact:RiskLevelHigh",
      "regula:category": "Annex III, Category 5(b)",
      "regula:mappingPrecision": "specific",
      "regula:findingCount": 2,
      "skos:note": "High-risk under EU AI Act Annex III, Category 5(b). Mapped to DPV concept HighRiskAISystem-AnnexIII-5-b."
    }
  ]
}
```

### `regula:mappingPrecision`

Every EU indicator declares how precise its DPV mapping is:

- **`specific`** — a single, unambiguous DPV concept (e.g. credit scoring →
  `HighRiskAISystem-AnnexIII-5-b`).
- **`practice`** — a prohibited practice mapped to its `A5-1-*` concept.
- **`transparency`** — an Article 50 transparency obligation.
- **`area`** — Regula detected an Annex III *area* (e.g. "Category 1,
  Biometrics") but not the specific sub-point. DPV has no bare point-level
  concept, and static analysis cannot resolve the sub-letter, so **only the
  parent `HighRiskAISystem` is asserted** — never a guessed sub-point. The
  area is recorded in `regula:annexIIIArea` for traceability.

## Honest gaps — stated, never invented

Two situations have **no** matching EU DPV concept. The export says so rather
than assert a nearest concept:

1. **Article 5(1)(ba) and (bb)** — the Regulation (EU) 2026/1744 prohibitions
   concerning NCII and CSAM were added *after* DPV-AIAct v2.3, so the vocabulary has no
   concepts for them. Findings get the parent `ProhibitedAISystem` plus a note
   explaining the gap.
2. **Non-EU regimes** — Regula also flags high-risk indicators under the
   **Korea AI Basic Act** and **Colorado SB 26-189**. DPV-AIAct models only the
   EU AI Act, so these appear in a separate `regula:outOfScopeIndicator` list,
   typed `regula:OutOfScopeIndicator`, with their jurisdiction recorded — not
   omitted, and not forced into an EU concept.

## How correctness is guaranteed

- **No fabricated IRIs, structurally.** `scripts/dpv_export.py` references DPV
  concepts by name and resolves them through a checked-in vocabulary snapshot
  (`scripts/dpv_data/dpv_aiact_terms.json`, 170 terms). At import it validates that every
  concept it can emit exists in that snapshot and raises otherwise — so the
  module cannot emit an IRI that is not in the real vocabulary.
- **No drift.** Tests (`tests/test_dpv_export.py`) pin the mapping to two
  sources of truth: the vocabulary snapshot, and `scripts/risk_patterns.py`
  (every high-risk category and every prohibited-practice sub-point the
  classifier can emit must have a mapping).
- **Refreshing the vocabulary.** `python3 scripts/refresh_dpv_vocab.py` fetches
  the upstream vocabulary and reports term drift; `--write` updates the
  snapshot. This is the only networked part of the subsystem and is a manual
  developer step — the scanner and exporter are zero-network.
- **Valid, offline-expandable JSON-LD.** The `@context` is fully inline (no
  remote context reference), so any conformant JSON-LD processor can expand the
  document and convert it to RDF triples with no network access — the concept
  and predicate IRIs resolve into the `https://w3id.org/dpv/legal/eu/aiact#`
  namespace.

## The `regula:` namespace

Predicates prefixed `regula:` (`https://getregula.com/ns/dpv/`) are Regula's
own provenance terms wrapped around the DPV concepts — clearly ours, never
presented as part of DPV. They carry the traceability (which findings, how many,
which files, mapping precision) that a consumer needs to judge the indication.

## Primary sources

- DPVCG EU-AIAct vocabulary — <https://w3c-cg.github.io/dpv/2.3/legal/eu/aiact/>
- DPV specification (Pandit et al., 2024) — <https://w3id.org/dpv>
- EU AI Act (Regulation (EU) 2024/1689) — the authoritative legal text
