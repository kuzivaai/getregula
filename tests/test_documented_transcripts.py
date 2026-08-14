# regula-ignore
"""Published CLI transcripts must reproduce, and retired output must stay retired.

Measured 2026-08-14, before any of this existed:

- Nine tracked surfaces published a `Verdict:` line as CLI output. No command
  emitted `Verdict:` at all. Six of them went further and printed "Your project
  is classified as high-risk under EU AI Act Annex III"; four added "You must
  comply with Articles 9-15 before the enforcement deadline". Those are a legal
  classification and an obligation, attributed to the tool, inside a transcript
  that made it look like the tool had said them. The project's hard rule
  forbids exactly that, and the shipped tool does not do it: it reports
  `insufficient_information` and names the facts a person still has to settle.
- Two guides published `Overall score: NN%` per article, from `format_gap_text`,
  which no CLI path reaches any more.
- examples/cv-screening-app/README.md published `[INFO] [ 43]` for a finding
  that now scores 63 and lands in WARN. The tier had changed, not just the
  number, and the page carried a dated "verified against v1.7.6" line.

Two guards, because one cannot cover both cases. Transcripts bound to a tracked
fixture are re-run and compared. Transcripts of a hypothetical project cannot be
re-run at all, so those are covered by proving the vocabulary they use is dead.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from verify_transcripts import (  # noqa: E402
    RETIRED_MARKERS,
    load_manifest,
    normalise,
    retired_marker_hits,
    retired_markers_are_unreachable,
    tracked_surfaces,
    verify,
)


def test_every_documented_transcript_reproduces():
    problems, checked = verify()
    assert not problems, (
        "published transcripts that do not reproduce:\n  "
        + "\n  ".join(problems))
    # A manifest that stopped being read would pass the assertion above while
    # checking nothing. Require positive proof the run happened.
    assert checked > 0, "no anchors were checked; this gate proved nothing"


def test_no_published_surface_shows_a_retired_output_marker():
    hits = retired_marker_hits()
    assert not hits, (
        "these published surfaces show CLI output the tool cannot produce:\n  "
        + "\n  ".join(hits))


def test_retired_markers_are_genuinely_retired():
    """The list is a measurement, not an assertion.

    If the CLI starts emitting one of these again, this fails rather than
    letting the list forbid wording the tool now legitimately produces.
    """
    problems = retired_markers_are_unreachable()
    assert not problems, "\n  ".join(problems)


def test_surface_enumeration_is_non_vacuous():
    """Guard the guard: a scan over an empty file list passes for free."""
    surfaces = tracked_surfaces()
    assert len(surfaces) > 40, len(surfaces)
    for expected in ("site/sample-report.html",
                     "examples/cv-screening-app/README.md",
                     "site/guides/eu-ai-act-recruitment-hiring.html"):
        assert expected in surfaces, expected


def test_manifest_is_non_vacuous_and_covers_the_fixture_bound_pages():
    entries = load_manifest()
    assert len(entries) >= 5, len(entries)
    assert all(entry["anchors"] for entry in entries), \
        "an entry with no anchors verifies nothing"
    covered = {entry["surface"] for entry in entries}
    assert {"examples/cv-screening-app/README.md",
            "examples/customer-chatbot/README.md",
            "site/sample-report.html"} <= covered, sorted(covered)


def test_marker_matching_survives_markup_and_entities():
    """Control for the matching primitive, on planted text.

    The blog page wrapped its verdict in markup
    (`<span class="cli-red">Verdict</span>: ...`) and HTML-escapes its em
    dashes, so a raw substring scan would have missed it.
    """
    marker = normalise("Verdict: PROHIBITED")
    assert marker in normalise('<span class="cli-red">Verdict</span>: '
                               '<span class="cli-red">PROHIBITED</span>')
    assert marker in normalise("Verdict:\n  PROHIBITED")
    assert marker not in normalise("Verdict: LIMITED-RISK")


def test_every_retired_marker_carries_a_reason():
    for marker, why in RETIRED_MARKERS.items():
        assert why and len(why) > 15, (marker, why)
