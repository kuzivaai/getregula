#!/usr/bin/env python3
# regula-ignore
"""
Refresh the checked-in DPV-AIAct vocabulary snapshot (scripts/dpv_data/dpv_aiact_terms.json)
from the upstream DPVCG source, and report term drift.

This is a DEVELOPER tool, run manually — it is NOT part of any scan path and
makes the only network call in the DPV subsystem. The scanner and exporter
themselves are zero-network and read only the checked-in snapshot.

Usage:
    python3 scripts/refresh_dpv_vocab.py            # show drift, do not write
    python3 scripts/refresh_dpv_vocab.py --write    # rewrite the snapshot

Drift matters because a mapping in scripts/dpv_export.py that points at a term
the vocabulary later renames or removes would silently emit a dangling IRI.
Run this periodically; if terms Regula maps to have changed, update the mapping.
"""

import csv
import io
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

SOURCE_CSV = (
    "https://raw.githubusercontent.com/w3c/dpv/master/"
    "2.3/legal/eu/aiact/eu-aiact.csv"
)
CANONICAL_URL = "https://w3c-cg.github.io/dpv/2.3/legal/eu/aiact/"
NAMESPACE = "https://w3id.org/dpv/legal/eu/aiact#"
SNAPSHOT_PATH = Path(__file__).parent / "dpv_data" / "dpv_aiact_terms.json"


def fetch_terms(url: str = SOURCE_CSV) -> dict:
    """Download and parse the upstream vocabulary CSV into a term map."""
    with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310 (trusted host)
        text = resp.read().decode("utf-8")
    terms = {}
    for row in csv.DictReader(io.StringIO(text)):
        name = (row.get("term") or "").strip()
        if not name:
            continue
        terms[name] = {
            "iri": (row.get("iri") or "").strip(),
            "type": (row.get("type") or "").strip(),
            "label": re.sub(r"\s+", " ", row.get("label") or "").strip(),
        }
    return terms


def build_snapshot(terms: dict, retrieved: str) -> dict:
    return {
        "_comment": (
            "Authoritative snapshot of the DPVCG EU-AIAct vocabulary term set. "
            "Used by scripts/dpv_export.py (via load_vocabulary) and by "
            "tests/test_dpv_export.py to guarantee every IRI Regula emits exists "
            "in the real vocabulary. This is a W3C Community Group report, NOT a "
            "ratified W3C Standard. Regenerate with scripts/refresh_dpv_vocab.py."
        ),
        "vocabulary": "DPVCG EU-AIAct extension",
        "standard_status": "W3C Community Group report (not a ratified W3C Standard)",
        "dpv_version": "2.3",
        "namespace": NAMESPACE,
        "namespace_prefix": "eu-aiact",
        "canonical_url": CANONICAL_URL,
        "source_serialisation": SOURCE_CSV,
        "retrieved": retrieved,
        "term_count": len(terms),
        "terms": dict(sorted(terms.items())),
    }


def load_current() -> dict:
    if SNAPSHOT_PATH.exists():
        return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    return {"terms": {}}


# Top-level concepts the EU-AIAct vocabulary would never legitimately drop.
# Their absence means a broken/partial upstream parse, not a real vocab change.
_REQUIRED_ANCHORS = (
    "AISystem", "HighRiskAISystem", "ProhibitedAISystem", "RiskLevelHigh",
)


def _validate_upstream(upstream: dict, current: dict) -> list:
    """Return a list of hard errors that must block a --write.

    The snapshot is a TRUST ANCHOR: dpv_export validates every emittable IRI
    against it, so a degenerate upstream response (an upstream CSV schema change
    that renames the `term`/`iri` columns, a partial fetch) must not silently
    overwrite a good snapshot with zero/garbage terms. These checks catch the
    catastrophic cases without blocking legitimate term-level drift.
    """
    errors = []
    if not upstream:
        return ["upstream returned 0 terms (schema change or partial fetch?)"]
    bad_iri = sorted(
        t for t, v in upstream.items()
        if not (v.get("iri") or "").startswith(NAMESPACE)
    )
    if bad_iri:
        shown = bad_iri[:5] + (["..."] if len(bad_iri) > 5 else [])
        errors.append(
            f"{len(bad_iri)} term(s) have an IRI outside {NAMESPACE}: {shown}"
        )
    missing_anchors = [a for a in _REQUIRED_ANCHORS if a not in upstream]
    if missing_anchors:
        errors.append(f"required anchor term(s) absent upstream: {missing_anchors}")
    cur = set(current.get("terms", {}))
    if cur:
        removed_frac = len(cur - set(upstream)) / len(cur)
        if removed_frac > 0.5:
            errors.append(
                f"{removed_frac:.0%} of current terms would be removed (>50%) — "
                "refusing; almost certainly an upstream schema change"
            )
    return errors


def main() -> int:
    write = "--write" in sys.argv
    retrieved = None
    for a in sys.argv:
        if a.startswith("--retrieved="):
            retrieved = a.split("=", 1)[1]

    current = load_current()
    try:
        upstream = fetch_terms()
    except Exception as e:  # noqa: BLE001 — surface any network/parse failure clearly
        print(f"refresh_dpv_vocab: failed to fetch upstream: {e}", file=sys.stderr)
        return 2

    cur_terms = set(current.get("terms", {}))
    up_terms = set(upstream)
    added = sorted(up_terms - cur_terms)
    removed = sorted(cur_terms - up_terms)
    changed = sorted(
        t for t in (cur_terms & up_terms)
        if current["terms"][t].get("iri") != upstream[t]["iri"]
    )

    print(f"upstream terms: {len(up_terms)} | snapshot terms: {len(cur_terms)}")
    print(f"added: {len(added)}  removed: {len(removed)}  iri-changed: {len(changed)}")
    for label, items in (("ADDED", added), ("REMOVED", removed), ("CHANGED", changed)):
        for t in items:
            print(f"  {label}: {t}")

    if not write:
        if added or removed or changed:
            print("\nDrift detected. Re-run with --write to update the snapshot,")
            print("then check scripts/dpv_export.py mappings still resolve.")
            return 1
        print("\nNo drift. Snapshot is current.")
        return 0

    errors = _validate_upstream(upstream, current)
    if errors:
        print("\nrefresh_dpv_vocab: REFUSING to write — the upstream response "
              "failed sanity checks (the snapshot is a trust anchor):",
              file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print("If this reflects a genuine upstream change, review it and update "
              "the checks or the snapshot manually.", file=sys.stderr)
        return 2

    snapshot = build_snapshot(upstream, retrieved or current.get("retrieved") or "")
    SNAPSHOT_PATH.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"\nWrote {SNAPSHOT_PATH} ({len(upstream)} terms).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
