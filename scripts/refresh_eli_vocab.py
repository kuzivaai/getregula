#!/usr/bin/env python3
# regula-ignore
"""
Refresh the checked-in ELI ontology term snapshot (scripts/eli_data/eli_ontology_terms.json)
from the Publications Office OWL distribution, and report term drift.

This is a DEVELOPER tool, run manually — it is NOT part of any scan path and
makes the only network call in the ELI subsystem. The delta-log dataset
builder (scripts/build_delta_dataset.py) is zero-network and reads only the
checked-in snapshot, mirroring the DPV pattern in scripts/refresh_dpv_vocab.py.

The ELI (European Legislation Identifier) ontology is maintained by the
Publications Office of the EU / the ELI Task Force. It is the vocabulary
EUR-Lex itself uses to describe legislation, including the amendment
relations (eli:amends / eli:amended_by) that the delta-log dataset emits.

Usage:
    python3 scripts/refresh_eli_vocab.py                 # show drift, do not write
    python3 scripts/refresh_eli_vocab.py --write         # rewrite the snapshot
    python3 scripts/refresh_eli_vocab.py --from-file F   # parse a local OWL file

Drift matters because a property used by build_delta_dataset.py that the
ontology later renames or removes would silently emit a dangling IRI.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from safe_io import urlopen_https

# OWL distribution hosted by the Publications Office (found via the EU
# Vocabularies ELI page, op.europa.eu/en/web/eu-vocabularies/eli).
SOURCE_OWL = "https://op.europa.eu/documents/3938058/11669184/eli.owl/"
CANONICAL_URL = "http://data.europa.eu/eli/ontology"
NAMESPACE = "http://data.europa.eu/eli/ontology#"
SNAPSHOT_PATH = Path(__file__).parent / "eli_data" / "eli_ontology_terms.json"

_TERM_RE = re.compile(
    r'rdf:about="http://data\.europa\.eu/eli/ontology#([A-Za-z_][A-Za-z0-9_]*)"'
)


def parse_terms(owl_text: str) -> dict:
    """Extract every named term the ontology declares (classes + properties)."""
    terms = {}
    for match in _TERM_RE.finditer(owl_text):
        name = match.group(1)
        terms[name] = NAMESPACE + name
    return dict(sorted(terms.items()))


def fetch_terms(url: str = SOURCE_OWL) -> dict:
    with urlopen_https(
        url, allowed_hosts=frozenset({"op.europa.eu"}), timeout=60
    ) as resp:
        return parse_terms(resp.read().decode("utf-8", errors="replace"))


def load_snapshot() -> dict:
    if not SNAPSHOT_PATH.exists():
        return {}
    return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))


def build_snapshot(terms: dict, retrieved: str) -> dict:
    return {
        "_comment": (
            "Authoritative snapshot of the ELI ontology term set (classes and "
            "properties). Used by scripts/build_delta_dataset.py and "
            "tests/test_delta_dataset.py to guarantee every eli: IRI Regula "
            "emits exists in the real ontology. The ELI ontology is maintained "
            "by the Publications Office of the EU. Regenerate with "
            "scripts/refresh_eli_vocab.py."
        ),
        "vocabulary": "ELI ontology (European Legislation Identifier)",
        "maintainer": "Publications Office of the EU / ELI Task Force",
        "namespace": NAMESPACE,
        "namespace_prefix": "eli",
        "canonical_url": CANONICAL_URL,
        "source_serialisation": SOURCE_OWL,
        "retrieved": retrieved,
        "term_count": len(terms),
        "terms": terms,
    }


def main() -> int:
    import argparse
    from datetime import date

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--write", action="store_true",
                        help="rewrite the snapshot file")
    parser.add_argument("--from-file", metavar="F",
                        help="parse a local OWL file instead of downloading")
    args = parser.parse_args()

    if args.from_file:
        terms = parse_terms(Path(args.from_file).read_text(
            encoding="utf-8", errors="replace"))
    else:
        terms = fetch_terms()

    if not terms:
        print("error: no terms parsed — source format may have changed",
              file=sys.stderr)
        return 1

    old = load_snapshot().get("terms", {})
    added = sorted(set(terms) - set(old))
    removed = sorted(set(old) - set(terms))
    print(f"upstream terms: {len(terms)}  snapshot terms: {len(old)}")
    if added:
        print(f"  new upstream terms ({len(added)}): {', '.join(added[:10])}"
              + (" ..." if len(added) > 10 else ""))
    if removed:
        print(f"  REMOVED upstream ({len(removed)}): {', '.join(removed)}")
        print("  WARNING: check build_delta_dataset.py for dangling references")

    if args.write:
        SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        snapshot = build_snapshot(terms, date.today().isoformat())
        SNAPSHOT_PATH.write_text(
            json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
        print(f"wrote {SNAPSHOT_PATH} ({len(terms)} terms)")
    elif not old:
        print("no snapshot on disk yet — run with --write to create it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
