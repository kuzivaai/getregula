#!/usr/bin/env python3
# regula-ignore
"""
Build the machine-readable delta-log DATASET (JSON-LD) from the delta-log
entries. Zero network. Stdlib only.

What this produces
------------------
content/regulations/delta-log/dataset/regula-aiact-delta-log.jsonld

A single JSON-LD document that publishes Regula's EU AI Act regulatory
delta-log as a citable dataset:

- Dataset-level metadata uses W3C DCAT and Dublin Core terms.
- Legal acts are identified by their EUR-Lex **ELI** IRIs and related with
  the ELI ontology's own amendment property (eli:amends) — the vocabulary
  the Publications Office itself uses. Every eli: term emitted is validated
  against the checked-in ontology snapshot
  (scripts/eli_data/eli_ontology_terms.json) at build time, mirroring the
  never-emit-a-fabricated-IRI guarantee of scripts/dpv_export.py.
- Change events use Regula's OWN extension namespace
  (https://getregula.com/ns/delta/), clearly ours, never presented as ELI,
  DCAT, or DPV terms.
- The DPVCG EU-AIAct vocabulary is referenced at dataset level
  (dct:conformsTo) because Regula's scan-result export
  (scripts/dpv_export.py) emits its concepts; per-event DPV concepts are
  deliberately NOT asserted because the vocabulary has no
  regulatory-change-event concepts today. Proposing those concepts
  upstream is tracked in docs/dpvcg-contribution-draft.md.

Honesty guards (do not remove):
- Article references are plain literals ("Article 5"), never invented
  article-level IRIs: the EUR-Lex ELI template for regulations resolves at
  act level, and this module must not emit IRIs it cannot guarantee exist.
- ELI act IRIs are constructed only from CELEX-verified entries using the
  documented EUR-Lex pattern http://data.europa.eu/eli/reg/{year}/{number}/oj.
- The source of truth is content/regulations/delta-log/entries/*.json.
  This module derives; it never hand-maintains a copy.

Usage:
    python3 scripts/build_delta_dataset.py           # build
    python3 scripts/build_delta_dataset.py --check   # verify committed file is current
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from constants import VERSION
from dpv_export import DPV_AIACT_VOCAB_IRI

ROOT = Path(__file__).parent.parent
ENTRIES_DIR = ROOT / "content" / "regulations" / "delta-log" / "entries"
DATASET_DIR = ROOT / "content" / "regulations" / "delta-log" / "dataset"
DATASET_PATH = DATASET_DIR / "regula-aiact-delta-log.jsonld"
ELI_SNAPSHOT_PATH = Path(__file__).parent / "eli_data" / "eli_ontology_terms.json"

ELI_NS = "http://data.europa.eu/eli/ontology#"
REGULA_DELTA_NS = "https://getregula.com/ns/delta/"
DATASET_IRI = "https://getregula.com/regulations/delta-log/dataset/"
LANDING_PAGE = "https://getregula.com/regulations/delta-log/"

# The ELI terms this module is allowed to emit. Each is validated against the
# checked-in ontology snapshot at build time; a term the ontology drops or
# renames fails the build instead of shipping a dangling IRI.
ELI_TERMS_USED = [
    "LegalResource",
    "amends",
    "date_publication",
    "in_force",
    "title",
]

# CELEX sector-3 regulation number -> ELI IRI, using the documented EUR-Lex
# pattern for regulations. Only acts that appear in a CELEX-carrying entry
# (or are named in its summary as amended acts) are listed; each IRI follows
# the template http://data.europa.eu/eli/reg/{year}/{number}/oj that EUR-Lex
# documents and dereferences.
def eli_iri_for_regulation(year: int, number: int) -> str:
    return f"http://data.europa.eu/eli/reg/{year}/{number}/oj"


AI_ACT_IRI = eli_iri_for_regulation(2024, 1689)
OMNIBUS_IRI = eli_iri_for_regulation(2026, 1744)

_CELEX_REG_RE = re.compile(r"^3(\d{4})R(\d{4})$")


def load_eli_snapshot() -> dict:
    snap = json.loads(ELI_SNAPSHOT_PATH.read_text(encoding="utf-8"))
    return snap.get("terms", {})


def validate_eli_terms() -> None:
    terms = load_eli_snapshot()
    missing = [t for t in ELI_TERMS_USED if t not in terms]
    if missing:
        raise SystemExit(
            f"build_delta_dataset: ELI term(s) not in the ontology snapshot: "
            f"{missing}. Refusing to emit unverified IRIs. "
            f"Run scripts/refresh_eli_vocab.py and reconcile.")


def load_entries() -> list:
    entries = []
    for path in sorted(ENTRIES_DIR.glob("*.json")):
        entries.append(json.loads(path.read_text(encoding="utf-8")))
    entries.sort(key=lambda e: (e["date"], e["id"]))
    return entries


def entry_node(e: dict) -> dict:
    node = {
        "@id": DATASET_IRI + "event/" + e["id"],
        "@type": "regula:RegulatoryDeltaEvent",
        "dct:identifier": e["id"],
        "dct:date": {"@value": e["date"], "@type": "xsd:date"},
        "regula:eventType": e["type"],
        "dct:description": e["summary"],
        "dct:source": {"@id": e["source_url"]},
        "regula:sourceTitle": e["source_title"],
        "regula:affectedArticles": [str(a) for a in e.get("affected_articles", [])],
        "regula:confidence": e["confidence"],
        "regula:jurisdiction": e.get("jurisdiction", "EU"),
    }
    if e.get("affected_recitals"):
        node["regula:affectedRecitals"] = [str(r) for r in e["affected_recitals"]]
    if e.get("celex_number"):
        node["dct:subject"] = {"@id": _celex_to_eli(e["celex_number"])}
        node["regula:celexNumber"] = e["celex_number"]
    if e.get("verified_on"):
        node["regula:verifiedOn"] = {"@value": e["verified_on"], "@type": "xsd:date"}
    if e.get("verified_by"):
        node["regula:verifiedBy"] = e["verified_by"]
    if e.get("mechanical_change"):
        node["regula:mechanicalChange"] = e["mechanical_change"]
    if e.get("supersedes"):
        node["regula:supersedes"] = {"@id": DATASET_IRI + "event/" + e["supersedes"]}
    return node


def _celex_to_eli(celex: str) -> str:
    m = _CELEX_REG_RE.match(celex)
    if not m:
        raise SystemExit(
            f"build_delta_dataset: CELEX {celex!r} is not a sector-3 "
            f"regulation number; extend _celex_to_eli before emitting an IRI.")
    return eli_iri_for_regulation(int(m.group(1)), int(m.group(2)))


def legal_resource_nodes(entries: list) -> list:
    """The legal acts the log describes, with the ELI amendment relation.

    Only relations stated in a verified-primary entry are asserted: the
    2026-07-24 OJ entry (verified against the EUR-Lex ELI record) states that
    Regulation (EU) 2026/1744 amends the AI Act together with Regulations
    (EU) 2018/1139 and (EU) 2023/1230.
    """
    oj_entry = next((e for e in entries if e["id"] == "2026-07-24-oj-publication"), None)
    nodes = [
        {
            "@id": AI_ACT_IRI,
            "@type": "eli:LegalResource",
            "eli:title": (
                "Regulation (EU) 2024/1689 (Artificial Intelligence Act)"
            ),
        }
    ]
    if oj_entry is not None:
        omnibus = {
            "@id": OMNIBUS_IRI,
            "@type": "eli:LegalResource",
            "eli:title": oj_entry["source_title"],
            "eli:date_publication": {"@value": "2026-07-24", "@type": "xsd:date"},
            "eli:amends": [
                {"@id": AI_ACT_IRI},
                {"@id": eli_iri_for_regulation(2018, 1139)},
                {"@id": eli_iri_for_regulation(2023, 1230)},
            ],
        }
        nodes.append(omnibus)
    return nodes


def build_document(entries: list) -> dict:
    dates = [e["date"] for e in entries]
    return {
        "@context": {
            "eli": ELI_NS,
            "dct": "http://purl.org/dc/terms/",
            "dcat": "http://www.w3.org/ns/dcat#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "regula": REGULA_DELTA_NS,
        },
        "@graph": [
            {
                "@id": DATASET_IRI,
                "@type": "dcat:Dataset",
                "dct:title": (
                    "Regula EU AI Act Regulatory Delta-Log "
                    "(machine-readable dataset)"
                ),
                "dct:description": (
                    "A versioned, primary-source-linked, machine-readable "
                    "record of changes to the EU AI Act (Regulation (EU) "
                    "2024/1689) and its amendments, including the Digital "
                    "Omnibus on AI (Regulation (EU) 2026/1744). Each event "
                    "carries the affected articles, a dated summary, the "
                    "primary source, and an explicit verification-confidence "
                    "grade. Legal acts are identified by EUR-Lex ELI IRIs; "
                    "amendment relations use the ELI ontology. This is risk "
                    "and currency INFORMATION, not legal advice."
                ),
                "dct:creator": "Regula (getregula.com)",
                "dct:issued": {"@value": dates[0], "@type": "xsd:date"},
                "dct:modified": {"@value": dates[-1], "@type": "xsd:date"},
                "dct:license": [
                    {"@id": "https://www.apache.org/licenses/LICENSE-2.0"},
                    {"@id": "https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12"},
                ],
                "dcat:landingPage": {"@id": LANDING_PAGE},
                "dcat:keyword": [
                    "EU AI Act", "Regulation (EU) 2024/1689",
                    "Digital Omnibus", "Regulation (EU) 2026/1744",
                    "regulatory change", "delta log", "AI governance",
                    "compliance", "ELI", "DPV",
                ],
                "dct:conformsTo": [
                    {"@id": DPV_AIACT_VOCAB_IRI},
                    {"@id": "http://data.europa.eu/eli/ontology"},
                ],
                "regula:generatorVersion": VERSION,
                "regula:eventCount": len(entries),
                "regula:vocabularyNote": (
                    "The DPVCG EU-AIAct vocabulary (a W3C Community Group "
                    "report, not a ratified W3C Standard) is referenced "
                    "because Regula's scan-result export emits its concepts. "
                    "Per-event DPV concepts are not asserted: the vocabulary "
                    "currently has no regulatory-change-event concepts. "
                    "Regula proposes adding them upstream (DPVCG issue #229)."
                ),
            },
            *legal_resource_nodes(entries),
            *[entry_node(e) for e in entries],
        ],
    }


def render() -> str:
    validate_eli_terms()
    entries = load_entries()
    if not entries:
        raise SystemExit("build_delta_dataset: no entries found")
    doc = build_document(entries)
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    check = "--check" in sys.argv[1:]
    text = render()
    if check:
        current = DATASET_PATH.read_text(encoding="utf-8") if DATASET_PATH.exists() else ""
        if current != text:
            print("delta-dataset: STALE — regenerate with "
                  "python3 scripts/build_delta_dataset.py", file=sys.stderr)
            return 1
        print("delta-dataset: current")
        return 0
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    DATASET_PATH.write_text(text, encoding="utf-8")
    print(f"delta-dataset: wrote {DATASET_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
