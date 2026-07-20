#!/usr/bin/env python3
# regula-ignore
"""
DPV-AIAct machine-readable export for Regula scan results.

Emits a JSON-LD document that tags Regula's risk indication (risk tier,
Annex III category, Article 5 prohibited-practice sub-point) with the real
concept IRIs of the **DPVCG EU-AIAct vocabulary** — the W3C Data Privacy
Vocabularies and Controls Community Group's "EU-AIAct" extension.

Honesty guards baked into this module (do not remove):

- **It is a W3C Community Group report, NOT a ratified W3C Standard.** The
  output describes itself as "aligned to the DPVCG EU-AIAct vocabulary",
  never as "the AI Act standard" or "standards-compliant".
- **Every emitted IRI is a real vocabulary term.** The mapping tables below
  reference term identifiers by name; `_validate_mappings()` checks each one
  against the checked-in vocabulary snapshot (`data/dpv_aiact_terms.json`) at
  import time and raises if any name is not in the vocabulary. It is therefore
  structurally impossible for this module to emit a fabricated IRI.
- **Gaps are stated, never invented.** Where Regula detects something the
  vocabulary has no concept for — Article 5(1)(i) (the Digital Omnibus
  CSAM/NCII prohibition, added after DPV-AIAct v2.3) or non-EU jurisdictions
  (Korea AI Basic Act, Colorado SB 26-189) — the export says so explicitly
  instead of asserting the nearest EU concept.
- **This is risk INDICATION, not legal classification.** The document carries
  a prominent disclaimer; consumers must treat concepts as flags for human
  review, not conformity determinations.

Zero external dependencies — stdlib only. Zero network calls: the vocabulary
snapshot is checked into the repo (regenerate with scripts/refresh_dpv_vocab.py).

Vocabulary provenance:
  DPVCG EU-AIAct extension, DPV v2.3
  namespace  https://w3id.org/dpv/legal/eu/aiact#
  canonical  https://w3c-cg.github.io/dpv/2.3/legal/eu/aiact/
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from constants import VERSION

# ---------------------------------------------------------------------------
# Namespaces
# ---------------------------------------------------------------------------

# The DPV-AIAct vocabulary namespace (verified from the vocabulary's own
# @prefix declaration in eu-aiact.ttl).
DPV_AIACT_NS = "https://w3id.org/dpv/legal/eu/aiact#"
DPV_AIACT_PREFIX = "eu-aiact"
# The vocabulary term for the whole scheme, used as dct:conformsTo target.
DPV_AIACT_VOCAB_IRI = "https://w3id.org/dpv/legal/eu/aiact"

# Regula's own extension namespace for the provenance predicates we add around
# the DPV concepts. Clearly OURS (getregula.com) — never presented as DPV.
REGULA_NS = "https://getregula.com/ns/dpv/"
REGULA_PREFIX = "regula"

_VOCAB_PATH = Path(__file__).parent.parent / "data" / "dpv_aiact_terms.json"


# ---------------------------------------------------------------------------
# Vocabulary snapshot loading
# ---------------------------------------------------------------------------

_VOCAB_CACHE = None


def load_vocabulary() -> dict:
    """Load the checked-in authoritative DPV-AIAct term snapshot.

    Returns the parsed data/dpv_aiact_terms.json. Cached after first read.
    """
    global _VOCAB_CACHE
    if _VOCAB_CACHE is None:
        with open(_VOCAB_PATH, encoding="utf-8") as f:
            _VOCAB_CACHE = json.load(f)
    return _VOCAB_CACHE


def term_iri(term: str) -> str:
    """Return the full IRI for a vocabulary term name.

    Raises KeyError if the term is not in the snapshot — the guard that
    prevents fabricated IRIs from ever being emitted.
    """
    vocab = load_vocabulary()
    if term not in vocab["terms"]:
        raise KeyError(
            f"DPV-AIAct term {term!r} is not in the vocabulary snapshot "
            f"({_VOCAB_PATH.name}). Refusing to emit an unverified IRI."
        )
    return vocab["terms"][term]["iri"]


def term_label(term: str) -> str:
    """Return the rdfs:label for a vocabulary term (for human-readable notes)."""
    vocab = load_vocabulary()
    return vocab["terms"].get(term, {}).get("label", term)


# ---------------------------------------------------------------------------
# Mapping tables — Regula internal categories -> DPV-AIAct concept term names
#
# Each mapping is verified against the DPV term DEFINITION (not just its name)
# — see analysis/research/2026-07/tech-frontier.md and the definitions in
# data/dpv_aiact_terms.json. Term NAMES only; term_iri() resolves and validates
# them against the snapshot.
# ---------------------------------------------------------------------------

# Regula RiskTier.value -> DPV RiskLevel term.
# Verified definitions: RiskLevelProhibited = "Article 5" practices;
# RiskLevelHigh = "high-risk ... Article 6"; RiskLevelTransparencyRequired =
# "not high-risk but where transparency is required"; RiskLevelMinimal =
# "not prohibited or high-risk or transparency required".
TIER_TO_RISK_LEVEL = {
    "prohibited": "RiskLevelProhibited",
    "high_risk": "RiskLevelHigh",
    "limited_risk": "RiskLevelTransparencyRequired",
    "minimal_risk": "RiskLevelMinimal",
}

# Severity order for computing the highest EU risk level in a scan.
_RISK_LEVEL_SEVERITY = {
    "RiskLevelProhibited": 4,
    "RiskLevelHigh": 3,
    "RiskLevelTransparencyRequired": 2,
    "RiskLevelMinimal": 1,
}

# Base DPV AISystem subclass to assert for a tier (parent concept — always
# safe for an EU finding of that tier). Limited/minimal risk have no dedicated
# AISystem subclass in the vocabulary; the RiskLevel term carries the meaning.
TIER_TO_SYSTEM_CLASS = {
    "prohibited": "ProhibitedAISystem",
    "high_risk": "HighRiskAISystem",
}

# Article 5(1) sub-point letter -> DPV ProhibitedAISystem concept.
# Verified: each DPV ProhibitedAISystem-A5-1-x definition matches the
# corresponding Regula prohibited practice (see tech-frontier.md). Practices:
#   a subliminal/manipulative   b exploitation of vulnerabilities
#   c social scoring            d criminal-offence risk prediction
#   e facial-recognition DB scraping   f emotion inference workplace/education
#   g biometric categorisation (sensitive)   h real-time remote biometric ID
# Article 5(1)(i) (CSAM/NCII generation) is INTENTIONALLY ABSENT: it was added
# by the Digital Omnibus, and DPV-AIAct v2.3 has no concept for it. Findings
# for (i) get the parent ProhibitedAISystem plus an explicit gap note.
PROHIBITED_LETTER_TO_CONCEPT = {
    "a": "ProhibitedAISystem-A5-1-a",
    "b": "ProhibitedAISystem-A5-1-b",
    "c": "ProhibitedAISystem-A5-1-c",
    "d": "ProhibitedAISystem-A5-1-d",
    "e": "ProhibitedAISystem-A5-1-e",
    "f": "ProhibitedAISystem-A5-1-f",
    "g": "ProhibitedAISystem-A5-1-g",
    "h": "ProhibitedAISystem-A5-1-h",
}

_A5_LETTER_RE = re.compile(r"5\(1\)\(([a-z])\)")


# Regula high-risk category string (emitted as finding["category"]) -> mapping.
# Each entry: (concept_term_or_None, jurisdiction, precision, annex_area).
#   precision "specific"  -> concept_term is a single unambiguous Annex III /
#                            Article 6 concept.
#   precision "area"      -> Regula detected the Annex III area but not the
#                            sub-point; DPV has no bare point-N concept and
#                            asserting one sub-letter would over-claim, so only
#                            the parent HighRiskAISystem is asserted. annex_area
#                            records the point number for traceability.
#   precision "non_eu"    -> a non-EU classification (Korea / Colorado). No
#                            DPV-AIAct (EU) concept applies; reported honestly
#                            as out-of-scope for this vocabulary.
# Verified DPV definitions (data/dpv_aiact_terms.json):
#   AnnexIII-2  critical infrastructure (single point, no sub-letter)
#   AnnexIII-4-b decisions affecting terms of work (worker management)
#   AnnexIII-5-b creditworthiness / credit score
#   AnnexIII-5-c risk assessment & pricing, life & health insurance
#   AnnexIII-5-d emergency services dispatching / triage
#   A6-1  high-risk via sectoral laws in Annex I (safety component route)
HIGH_RISK_CATEGORY_MAP = {
    # Unambiguous single Annex III / Annex I points
    "Annex III, Category 2":    ("HighRiskAISystem-AnnexIII-2", "EU", "specific", "2"),
    "Annex III, Category 4(b)": ("HighRiskAISystem-AnnexIII-4-b", "EU", "specific", "4"),
    "Annex III, Category 5(b)": ("HighRiskAISystem-AnnexIII-5-b", "EU", "specific", "5"),
    "Annex III, Category 5(c)": ("HighRiskAISystem-AnnexIII-5-c", "EU", "specific", "5"),
    "Annex III, Category 5(d)": ("HighRiskAISystem-AnnexIII-5-d", "EU", "specific", "5"),
    # Annex III areas detected at point level only (no sub-letter resolvable)
    "Annex III, Category 1":    (None, "EU", "area", "1"),
    "Annex III, Category 3":    (None, "EU", "area", "3"),
    "Annex III, Category 4":    (None, "EU", "area", "4"),
    "Annex III, Category 5":    (None, "EU", "area", "5"),
    "Annex III, Category 6":    (None, "EU", "area", "6"),
    "Annex III, Category 7":    (None, "EU", "area", "7"),
    "Annex III, Category 8":    (None, "EU", "area", "8"),
    # Annex I sectoral safety route -> Article 6(1)
    "Medical Devices":          ("HighRiskAISystem-A6-1", "EU", "specific", None),
    "Safety Components":        ("HighRiskAISystem-A6-1", "EU", "specific", None),
    # Non-EU classifications — no DPV-AIAct (EU) concept applies
    "Transportation (Korea AI Basic Act Art 33)": (None, "KR", "non_eu", None),
    "Housing (Colorado SB 26-189)":               (None, "US-CO", "non_eu", None),
    # Custom high-risk rules (user-defined) — parent concept only
    "Custom High-Risk":         (None, "EU", "area", None),
}


def _validate_mappings() -> None:
    """Assert every concept term this module can emit exists in the vocabulary.

    Runs at import. Raises RuntimeError if any mapped term name is absent from
    the snapshot — the hard guard against fabricated IRIs.
    """
    referenced = set(TIER_TO_RISK_LEVEL.values())
    referenced |= set(TIER_TO_SYSTEM_CLASS.values())
    referenced |= set(PROHIBITED_LETTER_TO_CONCEPT.values())
    referenced |= {"AISystem", "ProhibitedAISystem", "HighRiskAISystem", "hasRiskLevel"}
    for entry in HIGH_RISK_CATEGORY_MAP.values():
        if entry[0]:
            referenced.add(entry[0])
    vocab = load_vocabulary()
    known = set(vocab["terms"])
    missing = sorted(referenced - known)
    if missing:
        raise RuntimeError(
            "dpv_export mapping references DPV-AIAct terms not present in "
            f"{_VOCAB_PATH.name}: {missing}. Refusing to emit unverified IRIs."
        )


_validate_mappings()


# ---------------------------------------------------------------------------
# Per-finding mapping
# ---------------------------------------------------------------------------

def map_finding(finding: dict):
    """Map one Regula finding to a DPV-AIAct concept record.

    Never raises for an unknown category — falls back to the parent concept
    with an honest note. Returns None for tiers that carry no AI Act risk
    classification (Regula operational tiers such as agent_autonomy /
    credential_exposure / ai_security, or minimal_risk which contributes only
    to the risk-level summary).

    Record fields:
      tier, risk_level (DPV term or None), concepts (list of DPV term names to
      assert as rdf:type), jurisdiction ("EU"|"KR"|"US-CO"), precision
      ("specific"|"area"|"practice"|"transparency"|"non_eu"), annex_area,
      category, articles, note.
    """
    tier = finding.get("tier")
    category = finding.get("category", "") or ""
    articles = finding.get("articles", []) or []

    if tier == "prohibited":
        # The specific practice is in articles[0] (e.g. "5(1)(a)"), not the
        # category (which is the generic "Prohibited (Article 5)").
        letter = None
        for art in articles:
            m = _A5_LETTER_RE.search(str(art))
            if m:
                letter = m.group(1)
                break
        concepts = ["AISystem", "ProhibitedAISystem"]
        if letter and letter in PROHIBITED_LETTER_TO_CONCEPT:
            concepts.append(PROHIBITED_LETTER_TO_CONCEPT[letter])
            note = (
                f"Prohibited practice under EU AI Act Article 5(1)({letter}). "
                f"Mapped to DPV concept {PROHIBITED_LETTER_TO_CONCEPT[letter]}."
            )
            precision = "practice"
        elif letter == "i":
            note = (
                "Prohibited practice under EU AI Act Article 5(1)(i) "
                "(CSAM/NCII generation, added by the Digital Omnibus). "
                "DPV-AIAct v2.3 has no concept for Article 5(1)(i); only the "
                "parent ProhibitedAISystem is asserted."
            )
            precision = "practice"
        else:
            note = (
                "Prohibited practice (EU AI Act Article 5); the specific "
                "sub-point was not resolved, so only the parent "
                "ProhibitedAISystem is asserted."
            )
            precision = "area"
        return {
            "tier": tier,
            "risk_level": TIER_TO_RISK_LEVEL["prohibited"],
            "concepts": concepts,
            "jurisdiction": "EU",
            "precision": precision,
            "annex_area": None,
            "category": category,
            "articles": articles,
            "note": note,
        }

    if tier == "high_risk":
        entry = HIGH_RISK_CATEGORY_MAP.get(category)
        if entry is None:
            # Unknown high-risk category — assert the parent only, be honest.
            concept, jurisdiction, precision, annex_area = None, "EU", "area", None
            note = (
                f"High-risk indicator (category {category!r}) with no specific "
                "DPV-AIAct mapping; only the parent HighRiskAISystem is asserted."
            )
        else:
            concept, jurisdiction, precision, annex_area = entry
            if precision == "non_eu":
                note = (
                    f"High-risk under a non-EU regime (category {category!r}); "
                    "DPV-AIAct models only the EU AI Act, so no EU concept is "
                    "asserted. Reported as out-of-scope for this vocabulary."
                )
            elif precision == "specific":
                note = (
                    f"High-risk under EU AI Act {category}. Mapped to DPV "
                    f"concept {concept}."
                )
            else:  # area
                note = (
                    f"High-risk under EU AI Act Annex III area {annex_area} "
                    f"({category}). The specific sub-point is not determined by "
                    "static analysis and DPV-AIAct has no bare point-level "
                    "concept, so only the parent HighRiskAISystem is asserted."
                )

        if precision == "non_eu":
            # Out-of-scope for the EU vocabulary — no risk_level, no eu-aiact type.
            return {
                "tier": tier,
                "risk_level": None,
                "concepts": [],
                "jurisdiction": jurisdiction,
                "precision": precision,
                "annex_area": annex_area,
                "category": category,
                "articles": articles,
                "note": note,
            }

        concepts = ["AISystem", "HighRiskAISystem"]
        if concept:
            concepts.append(concept)
        return {
            "tier": tier,
            "risk_level": TIER_TO_RISK_LEVEL["high_risk"],
            "concepts": concepts,
            "jurisdiction": jurisdiction,
            "precision": precision,
            "annex_area": annex_area,
            "category": category,
            "articles": articles,
            "note": note,
        }

    if tier == "limited_risk":
        return {
            "tier": tier,
            "risk_level": TIER_TO_RISK_LEVEL["limited_risk"],
            "concepts": ["AISystem"],
            "jurisdiction": "EU",
            "precision": "transparency",
            "annex_area": None,
            "category": category,
            "articles": articles or ["50"],
            "note": (
                "Transparency obligation under EU AI Act Article 50 (e.g. "
                "chatbot / synthetic-content disclosure). DPV-AIAct expresses "
                "this as RiskLevelTransparencyRequired, not a dedicated "
                "AISystem subclass."
            ),
        }

    # minimal_risk contributes only to the risk-level summary; all other tiers
    # (agent_autonomy, credential_exposure, ai_security, not_ai) are Regula
    # operational observations, not EU AI Act risk classifications.
    return None


# ---------------------------------------------------------------------------
# JSON-LD document construction
# ---------------------------------------------------------------------------

def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "x"


def _article_sort_key(article: str):
    """Sort article ids: plain integers numerically, others lexically after."""
    try:
        return (0, int(article), "")
    except (ValueError, TypeError):
        return (1, 0, str(article))


def _context() -> dict:
    """The JSON-LD @context. Binds prefixes and coerces IRI-valued predicates."""
    return {
        "eu-aiact": DPV_AIACT_NS,
        "dpv": "https://w3id.org/dpv#",
        "ai": "https://w3id.org/dpv/ai#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "dct": "http://purl.org/dc/terms/",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        REGULA_PREFIX: REGULA_NS,
        "id": "@id",
        "type": "@type",
        "hasRiskLevel": {"@id": "eu-aiact:hasRiskLevel", "@type": "@id"},
        "indicates": {"@id": "regula:indicates", "@type": "@id"},
        "outOfScopeIndicator": {"@id": "regula:outOfScopeIndicator", "@type": "@id"},
        "conformsTo": {"@id": "dct:conformsTo", "@type": "@id"},
    }


def build_dpv_jsonld(findings, project_name=None, scan_meta=None, created=None):
    """Build the DPV-AIAct JSON-LD document from Regula findings.

    findings      list of finding dicts (as produced by report.scan_files).
    project_name  optional human name for the scanned system.
    scan_meta     optional dict of extra scan metadata (files_scanned, etc.).
    created       optional ISO-8601 timestamp string (defaults to now, UTC).
                  Pass a fixed value for reproducible output.

    Returns a dict ready for json.dumps.
    """
    vocab = load_vocabulary()
    if created is None:
        created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Map active (non-suppressed) findings and aggregate by identical concept
    # signature so repeated findings collapse into one indicator node.
    active = [f for f in findings if not f.get("suppressed")]
    aggregated = {}      # key -> aggregate record (EU, in-vocabulary)
    out_of_scope = {}    # key -> aggregate record (non-EU)
    highest_sev = 0
    highest_level = None

    for f in active:
        rec = map_finding(f)
        if rec is None:
            # minimal_risk still moves the summary risk level if nothing higher.
            if f.get("tier") == "minimal_risk":
                lvl = TIER_TO_RISK_LEVEL["minimal_risk"]
                sev = _RISK_LEVEL_SEVERITY.get(lvl, 0)
                if sev > highest_sev:
                    highest_sev, highest_level = sev, lvl
            continue

        if rec["risk_level"]:
            sev = _RISK_LEVEL_SEVERITY.get(rec["risk_level"], 0)
            if sev > highest_sev:
                highest_sev, highest_level = sev, rec["risk_level"]

        bucket = out_of_scope if rec["precision"] == "non_eu" else aggregated
        key = (
            rec["jurisdiction"],
            tuple(rec["concepts"]),
            rec["category"],
            rec["precision"],
            rec["annex_area"],
        )
        agg = bucket.get(key)
        if agg is None:
            agg = {"record": rec, "count": 0, "files": [], "articles": set()}
            bucket[key] = agg
        agg["count"] += 1
        fp = f.get("file")
        if fp and fp not in agg["files"] and len(agg["files"]) < 10:
            agg["files"].append(fp)
        for a in rec["articles"]:
            agg["articles"].add(str(a))

    graph = []

    scan_id = "urn:regula:dpv:scan"
    if project_name:
        scan_id = f"urn:regula:dpv:scan:{_slug(project_name)}"

    def _sort_key(item):
        rec = item[1]["record"]
        sev = _RISK_LEVEL_SEVERITY.get(rec["risk_level"], 0)
        return (-sev, rec["category"], tuple(rec["concepts"]))

    eu_items = sorted(aggregated.items(), key=_sort_key)
    oos_items = sorted(out_of_scope.items(),
                       key=lambda it: (it[1]["record"]["jurisdiction"],
                                       it[1]["record"]["category"]))

    indicator_ids = []
    oos_ids = []

    for i, (key, agg) in enumerate(eu_items):
        rec = agg["record"]
        node_id = f"urn:regula:dpv:indicator:{i + 1}-{_slug(rec['concepts'][-1])}"
        indicator_ids.append(node_id)
        node = {
            "id": node_id,
            "type": [f"{DPV_AIACT_PREFIX}:{c}" for c in rec["concepts"]],
            "hasRiskLevel": f"{DPV_AIACT_PREFIX}:{rec['risk_level']}",
            "regula:category": rec["category"],
            "regula:articles": sorted(agg["articles"], key=_article_sort_key),
            "regula:mappingPrecision": rec["precision"],
            "regula:findingCount": agg["count"],
            "regula:exampleFiles": agg["files"],
            "skos:note": rec["note"],
        }
        if rec["annex_area"]:
            node["regula:annexIIIArea"] = rec["annex_area"]
        graph.append(node)

    for i, (key, agg) in enumerate(oos_items):
        rec = agg["record"]
        node_id = f"urn:regula:dpv:out-of-scope:{i + 1}-{_slug(rec['jurisdiction'])}"
        oos_ids.append(node_id)
        graph.append({
            "id": node_id,
            "type": ["regula:OutOfScopeIndicator"],
            "regula:jurisdiction": rec["jurisdiction"],
            "regula:category": rec["category"],
            "regula:articles": sorted(agg["articles"], key=_article_sort_key),
            "regula:findingCount": agg["count"],
            "regula:exampleFiles": agg["files"],
            "skos:note": rec["note"],
        })

    # The scan node — provenance, disclaimer, vocabulary honesty block, links.
    scan_node = {
        "id": scan_id,
        "type": "regula:ScanResult",
        "dct:title": (
            f"{project_name} — EU AI Act risk indication (DPV-AIAct aligned)"
            if project_name else
            "EU AI Act risk indication (DPV-AIAct aligned)"
        ),
        "dct:description": (
            "Automated static-analysis risk INDICATION for the scanned "
            "codebase, tagged with DPVCG EU-AIAct vocabulary concept IRIs. "
            "This is NOT a legal classification, conformity assessment, or "
            "certification. Concepts are flags for human review; false "
            "positives and negatives occur. EU AI Act Article 6 requires "
            "contextual assessment that pattern matching cannot provide."
        ),
        "dct:creator": f"Regula v{VERSION} (https://getregula.com)",
        "dct:created": {"@value": created, "@type": "xsd:dateTime"},
        "conformsTo": DPV_AIACT_VOCAB_IRI,
        "regula:disclaimer": (
            "Regula indicates EU AI Act risk; it does not certify compliance. "
            "Output is aligned to the DPVCG EU-AIAct vocabulary, a W3C "
            "Community Group report — NOT a ratified W3C Standard."
        ),
        "regula:vocabulary": {
            "regula:name": vocab.get("vocabulary"),
            "regula:standardStatus": vocab.get("standard_status"),
            "regula:dpvVersion": vocab.get("dpv_version"),
            "regula:namespace": vocab.get("namespace"),
            "regula:canonicalUrl": vocab.get("canonical_url"),
            "regula:retrieved": vocab.get("retrieved"),
        },
        "regula:highestRiskLevel": (
            f"{DPV_AIACT_PREFIX}:{highest_level}" if highest_level else None
        ),
        "regula:indicatorCount": len(indicator_ids),
    }
    if scan_meta:
        for k, v in scan_meta.items():
            scan_node[f"regula:{k}"] = v
    if indicator_ids:
        scan_node["indicates"] = indicator_ids
    if oos_ids:
        scan_node["outOfScopeIndicator"] = oos_ids
        scan_node["regula:outOfScopeNote"] = (
            "The scan also flagged indicators under non-EU regimes (e.g. Korea "
            "AI Basic Act, Colorado SB 26-189). DPV-AIAct models only the EU AI "
            "Act, so those are listed separately as out-of-scope for this "
            "vocabulary — not omitted, not forced into an EU concept."
        )

    return {
        "@context": _context(),
        "@graph": [scan_node] + graph,
    }


def format_dpv_jsonld(doc: dict) -> str:
    """Serialise a DPV-AIAct JSON-LD document to a stable, indented string."""
    return json.dumps(doc, indent=2, ensure_ascii=False)


def generate_dpv_export(project_path: str, project_name=None, created=None) -> dict:
    """Scan a project and build its DPV-AIAct JSON-LD document.

    Convenience wrapper used by the CLI and evidence pack. Imports the scanner
    lazily to keep this module cheap to import.
    """
    from report import scan_files
    findings = scan_files(project_path)
    active = [f for f in findings if not f.get("suppressed")]
    scan_meta = {
        "findingsScanned": len(findings),
        "activeFindings": len(active),
    }
    return build_dpv_jsonld(findings, project_name=project_name,
                            scan_meta=scan_meta, created=created)


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Export DPV-AIAct JSON-LD for a project")
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--name", "-n", default=None)
    ap.add_argument("--output", "-o", default=None)
    args = ap.parse_args()
    doc = generate_dpv_export(args.project, project_name=args.name)
    content = format_dpv_jsonld(doc)
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
        print(f"DPV-AIAct export written to {args.output}", file=sys.stderr)
    else:
        print(content)


if __name__ == "__main__":
    main()
