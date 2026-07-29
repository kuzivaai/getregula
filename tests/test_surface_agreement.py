"""Every published surface carrying a figure must agree with every other.

This is the class behind N2, and behind five recorded predecessors: a figure
published in more than one place drifts, and nothing compares the copies.
`scripts/cascade_count.py --check` compares each surface against the canonical
test count, which catches drift in ONE figure. Nothing catches drift between
surfaces in any other figure.

The surface list is read from `data/published_count_manifest.json` rather than
hardcoded here, so a surface added to the manifest is covered automatically.
That file's own `_enforcement` note explains why it exists: "an eleventh
surface cannot appear silently."

WHAT THIS DOES NOT DO. It does not decide whether a figure is correct. It
decides whether the copies agree. A figure that is wrong in the same way
everywhere passes here and is caught by its own derivation test, for example
`tests/test_recall_decomposition.py`. The two guards are complementary and
neither subsumes the other.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "data" / "published_count_manifest.json"


def manifest_surfaces() -> list[str]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))["published_surfaces"]


# A tracked figure is a (label, regex) pair. The label names the quantity; the
# regex must have exactly one capture group, the value. Labels are added here
# when a figure starts appearing on more than one surface.
TRACKED_FIGURES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("pytest-collected test count",
     re.compile(r"([\d,]{3,7})\s+pytest-collected")),
    ("unique test count",
     re.compile(r"([\d,]{3,7})\s+unique tests")),
    ("CLI command count",
     re.compile(r"(\d{1,3})\s+CLI commands")),
    ("compliance framework mappings",
     re.compile(r"(\d{1,3})\s+compliance framework mappings")),
)


def _norm(v: str) -> str:
    return v.replace(",", "").strip()


def collect(surfaces: list[str]) -> dict[str, dict[str, set[str]]]:
    """label -> value -> set of surfaces publishing that value."""
    found: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for rel in surfaces:
        p = REPO_ROOT / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for label, pat in TRACKED_FIGURES:
            for m in pat.finditer(text):
                found[label][_norm(m.group(1))].add(rel)
    return found


def test_manifest_is_readable_and_populated():
    """Precondition. An empty surface list would make every test below vacuous."""
    surfaces = manifest_surfaces()
    assert len(surfaces) >= 5, f"implausibly few surfaces: {surfaces}"
    missing = [s for s in surfaces if not (REPO_ROOT / s).exists()]
    assert missing == [], f"manifest lists files that do not exist: {missing}"


def test_at_least_one_tracked_figure_is_actually_found():
    """Control against the guard silently matching nothing.

    If every regex stopped matching, the agreement test would pass trivially
    for ever. Measurement rule 4: an absent signal is not a passing signal.
    """
    found = collect(manifest_surfaces())
    assert found, (
        "no tracked figure matched on any manifest surface; the regexes have "
        "drifted from the prose and this guard is asserting nothing")
    multi = {k: v for k, v in found.items() if sum(len(s) for s in v.values()) > 1}
    assert multi, (
        "no tracked figure appears on more than one surface, so cross-surface "
        "agreement is untested")


def test_published_figures_agree_across_surfaces():
    """The guard. Same figure, different surfaces, must be the same value."""
    found = collect(manifest_surfaces())
    disagreements = {
        label: {val: sorted(files) for val, files in vals.items()}
        for label, vals in found.items() if len(vals) > 1
    }
    assert not disagreements, (
        "published figures disagree across manifest surfaces:\n"
        + json.dumps(disagreements, indent=2))


def test_control_a_planted_disagreement_is_caught(tmp_path, monkeypatch):
    """Plant a disagreement between two surfaces; the guard must fail.

    Copies the whole manifest surface set into a temporary tree, edits ONE
    surface so its test count differs, and points the guard at the copy. The
    real repository is never modified.
    """
    surfaces = manifest_surfaces()
    found = collect(surfaces)
    label = "pytest-collected test count"
    assert label in found and found[label], (
        f"{label} not found on any surface; cannot plant a disagreement")
    value = next(iter(found[label]))
    carriers = sorted(found[label][value])
    assert len(carriers) >= 2, (
        f"{label} appears on only {carriers}; need two surfaces to disagree")

    for rel in surfaces:
        src = REPO_ROOT / rel
        if not src.exists():
            continue
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding="utf-8", errors="replace"),
                       encoding="utf-8")

    victim = tmp_path / carriers[0]
    text = victim.read_text(encoding="utf-8")
    bogus = str(int(value) + 1)
    patched = re.sub(r"([\d,]{3,7})(\s+pytest-collected)",
                     bogus + r"\2", text, count=1)
    assert patched != text, "the planted edit did not apply; control invalid"
    victim.write_text(patched, encoding="utf-8")

    monkeypatch.setattr(
        __import__(__name__), "REPO_ROOT", tmp_path, raising=False)
    import sys
    mod = sys.modules[__name__]
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path, raising=True)

    with pytest.raises(AssertionError, match="disagree across manifest"):
        test_published_figures_agree_across_surfaces()
