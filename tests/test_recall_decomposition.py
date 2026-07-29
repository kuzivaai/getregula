"""The published recall decomposition must derive from RECALL.json.

Finding N2. `docs/MODEL_CARD.md` published "13 suppressed by opt-in domain
gating, 4 by the AI-indicator gate, and 3 are genuine pattern gaps, so 17 of
20 misses are gate behaviour", citing `benchmarks/synthetic/RECALL.json`. The
artefact does not support any of those numbers. Derived by set difference over
its per-fixture `missed` lists, the split is 6 / 7 / 7, so 13 of 20 are gate
behaviour and 7 are pattern-side exposure, not 3.

The published figure understated the product's weakness by more than double,
and it survived because nothing recomputed it. This file recomputes it.

The decomposition is a set difference, not a subtraction of fractions. A
fixture can be suppressed by more than one gate at once, so
`20 - 10 recovered` does not tell you which gate did the suppressing. Only the
`missed` lists do.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RECALL = REPO_ROOT / "benchmarks" / "synthetic" / "RECALL.json"
MODEL_CARD = REPO_ROOT / "docs" / "MODEL_CARD.md"


def decomposition() -> dict[str, int]:
    """Recompute the split from the artefact. The single source of truth."""
    conditions = json.loads(RECALL.read_text(encoding="utf-8"))["conditions"]

    def missed(key: str) -> set[str]:
        return set(conditions[key]["tiers"]["high_risk"]["missed"])

    default = missed("scanner/default")
    domains = missed("scanner/domains-declared")
    domains_ai = missed("scanner/domains-declared+ai-import")
    return {
        "missed_on_default": len(default),
        "recovered_by_domains": len(default - domains),
        "recovered_by_ai_import": len(domains - domains_ai),
        "never_recovered": len(domains_ai),
    }


def test_the_three_conditions_are_nested():
    """Precondition. Set difference is only meaningful if they nest.

    Declaring domains must not cause a fixture to stop being detected, and
    neither must adding an AI import. If either did, "recovered by" would be
    the wrong frame entirely and every number below would be meaningless.
    """
    conditions = json.loads(RECALL.read_text(encoding="utf-8"))["conditions"]

    def missed(key):
        return set(conditions[key]["tiers"]["high_risk"]["missed"])

    default = missed("scanner/default")
    domains = missed("scanner/domains-declared")
    domains_ai = missed("scanner/domains-declared+ai-import")
    assert domains <= default, (
        f"declaring domains LOST fixtures: {sorted(domains - default)}")
    assert domains_ai <= domains, (
        f"adding an AI import LOST fixtures: {sorted(domains_ai - domains)}")


def test_decomposition_sums_to_the_default_miss_count():
    d = decomposition()
    parts = (d["recovered_by_domains"] + d["recovered_by_ai_import"]
             + d["never_recovered"])
    assert parts == d["missed_on_default"], (
        f"{d['recovered_by_domains']} + {d['recovered_by_ai_import']} + "
        f"{d['never_recovered']} = {parts}, expected {d['missed_on_default']}")


def test_model_card_publishes_the_derived_numbers():
    """The assertion N2 exists for. Fails before the correction, passes after.

    Reads the published prose and checks it against the artefact. If the
    artefact is regenerated and the split moves, this fails until the
    published paragraph is updated, which is the point.
    """
    d = decomposition()
    text = MODEL_CARD.read_text(encoding="utf-8")
    gate_behaviour = d["recovered_by_domains"] + d["recovered_by_ai_import"]

    expected = [
        (rf"\*\*{d['recovered_by_domains']} are recovered by declaring the",
         f"the domain-recovered count ({d['recovered_by_domains']})"),
        (rf"a further {d['recovered_by_ai_import']} by also having an "
         rf"AI-library import",
         f"the AI-import-recovered count ({d['recovered_by_ai_import']})"),
        (rf"and {d['never_recovered']} are never recovered",
         f"the never-recovered count ({d['never_recovered']})"),
        (rf"\*\*{gate_behaviour} of {d['missed_on_default']} misses are gate "
         rf"behaviour and {d['never_recovered']} are pattern-side",
         f"the headline split ({gate_behaviour} of "
         f"{d['missed_on_default']}, {d['never_recovered']} pattern-side)"),
    ]
    for pattern, what in expected:
        assert re.search(pattern, text), (
            f"docs/MODEL_CARD.md does not publish {what} as derived from "
            f"benchmarks/synthetic/RECALL.json. Recomputed values: {d}")


def test_the_withdrawn_split_is_gone_from_the_model_card():
    """The specific wrong numbers must not come back."""
    text = MODEL_CARD.read_text(encoding="utf-8")
    assert "17 of 20 misses are gate behaviour rather than missing patterns" \
        not in text, "the withdrawn 17-of-20 split has returned"


def test_control_a_wrong_published_number_is_caught(tmp_path, monkeypatch):
    """Plant a disagreement and confirm the assertion fires.

    Without this, test_model_card_publishes_the_derived_numbers could pass
    against a document that happened to contain the right digits for the wrong
    reason, and nobody would know the check had teeth.
    """
    import pytest
    text = MODEL_CARD.read_text(encoding="utf-8")
    d = decomposition()
    broken = text.replace(
        f"and {d['never_recovered']} are never recovered",
        "and 3 are never recovered")
    assert broken != text, "the planted edit did not apply; control is invalid"
    planted = tmp_path / "MODEL_CARD.md"
    planted.write_text(broken, encoding="utf-8")

    monkeypatch.setattr(
        __import__(__name__.split(".")[-1] if "." in __name__ else __name__,
                   fromlist=["MODEL_CARD"]),
        "MODEL_CARD", planted, raising=True)
    with pytest.raises(AssertionError):
        test_model_card_publishes_the_derived_numbers()
