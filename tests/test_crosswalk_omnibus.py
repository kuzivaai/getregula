# regula-ignore
"""Owner decision 2, the split ruling on Articles 11 and 12, encoded.

WHY THIS EXISTS
---------------
F14 recorded that `references/framework_crosswalk.yaml` was stale and that
`owasp_agentic` was missing from two articles. A session deviated from the
literal instruction to blank Articles 11 and 12, on the measured ground that
`scripts/compliance_check.py` never reads the crosswalk, and sent the deviation
for ratification.

The owner ruled on 2026-07-28 and SPLIT it:

  REJECTED  for `article_11`. The Omnibus route was missing and had to be
            added. Regulation (EU) 2026/1744 amends Article 11(1) to provide a
            simplified technical-documentation form for SMEs and small mid-cap
            enterprises.
  RATIFIED  for `owasp_agentic` absent from Articles 11 and 12, with the reason
            to be recorded IN THE CROSSWALK and not only in the ledger.

The ruling went unapplied for five sessions. A ruling that is not encoded is
indistinguishable from a ruling that was never made, so it is encoded here as
tests over the data rather than as prose about it.

WHAT WAS VERIFIED AGAINST THE PRIMARY TEXT, AND HOW
---------------------------------------------------
2026-07-30. The regulation was retrieved in full from
eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202601744 and searched
locally, because two summarising fetches of the same document truncated before
the annexes and one of them reported that the word "agentic" does not occur.
It does occur, once. A truncated retrieval is not evidence of absence, and that
near-miss is the reason this module states its method.

Established from that retrieval:

- The amending point reads "in Article 11(1), the second subparagraph is
  replaced by the following", and is Article 1, point (10).
- Article 12 is not amended. Point (9) is Article 10, point (10) is Article 11,
  point (11) is Article 17; an enumeration of all amending points to Regulation
  (EU) 2024/1689 contains no point for Article 12.
- "agentic" occurs exactly once, case-insensitive, in Annex XIV at code
  AIH 0401, and Annex XIV Section 4 puts those codes to work scoping which
  conformity assessment bodies may be designated for which system types.

WHAT THIS MODULE DOES NOT DO
----------------------------
It does not re-fetch EUR-Lex. A unit test that depends on a third-party website
fails for reasons that have nothing to do with this repository. The primary-text
verification is recorded in the data it produced, in the crosswalk's
`amendment_verified` field and in the delta-log entry, and this module checks
that those records are present and say what they are supposed to say.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

CROSSWALK = REPO / "references" / "framework_crosswalk.yaml"
OJ_ENTRY = (REPO / "content" / "regulations" / "delta-log" / "entries"
            / "2026-07-24-oj-publication.json")
ANNEX_XIV_ENTRY = (REPO / "content" / "regulations" / "delta-log" / "entries"
                   / "2026-07-29-annex-xiv-aih-codes.json")

OMNIBUS = "2026/1744"


def _load() -> dict:
    """Load the crosswalk the way `framework_mapper` loads it."""
    import framework_mapper as fm
    return fm._load_crosswalk()


def _mapping(article: str) -> dict:
    return _load()["mappings"][f"article_{article}"]


# ---------------------------------------------------------------------------
# The REJECTED half: article_11 gains the Omnibus route
# ---------------------------------------------------------------------------

def test_article_11_declares_the_omnibus_amendment():
    eu = _mapping("11")["eu_ai_act"]
    assert eu["article"] == "11"
    amended_by = eu.get("amended_by", "")
    assert OMNIBUS in amended_by, (
        f"article_11 does not name the amending regulation. Owner decision 2 "
        f"rejected the deviation that left this gap. Got: {amended_by!r}")
    assert "point (10)" in amended_by, (
        "the amending point number is missing; 'amended by the Omnibus' is not "
        "checkable, 'Article 1, point (10)' is")

    amendment = eu.get("amendment", "")
    for required in ("SME", "SMC", "Annex IV", "simplified",
                     "notified bodies"):
        assert required in amendment, (
            f"the amendment text does not mention {required!r}, so it does not "
            f"describe what Article 11(1) now permits. Got: {amendment!r}")


def test_article_11_keeps_the_base_requirement_alongside_the_amendment():
    """The amendment adds a route. It does not delete the duty."""
    eu = _mapping("11")["eu_ai_act"]
    assert "Technical documentation shall be drawn up" in eu["requirement"], (
        "the base Article 11 requirement was replaced rather than annotated. "
        "A simplified FORM for SMEs is not an exemption from documenting.")


def test_article_11_amendment_names_its_primary_source_and_its_verification():
    eu = _mapping("11")["eu_ai_act"]
    src = eu.get("amendment_source", "")
    assert "eur-lex.europa.eu" in src, (
        f"the amendment cites no primary source. Got: {src!r}")
    verified = eu.get("amendment_verified", "")
    assert "2026-07-30" in verified, verified
    assert "second subparagraph is replaced" in verified, (
        "the verification record does not quote the operative amending "
        "language, so a reader cannot tell what was actually checked")


def test_the_omnibus_delta_log_entry_records_the_article_11_amendment():
    """The repo's own primary-source record must agree with the crosswalk."""
    entry = json.loads(OJ_ENTRY.read_text(encoding="utf-8"))
    assert entry["celex_number"] == "32026R1744"
    assert entry["confidence"] == "verified-primary"
    assert "11" in entry["affected_articles"], (
        "the OJ delta-log entry does not list Article 11 among the articles it "
        "affects, while its own verified_by note names the amended Article "
        "11(1). The two halves of one record disagreed until 2026-07-30.")
    assert "Article 11(1)" in entry["verified_by"]


def test_article_12_is_not_claimed_to_be_amended():
    """The other half of the same measurement: 12 is untouched by the Omnibus.

    Recorded as a negative because asserting an amendment that does not exist
    is the same class of error as omitting one that does.
    """
    eu = _mapping("12")["eu_ai_act"]
    assert "amended_by" not in eu, (
        "article_12 claims an Omnibus amendment. An enumeration of every "
        "amending point in Regulation (EU) 2026/1744 on 2026-07-30 found none "
        "for Article 12: point (9) is Article 10, (10) is Article 11, (11) is "
        "Article 17.")


# ---------------------------------------------------------------------------
# The RATIFIED half: owasp_agentic stays unmapped, with the reason in the data
# ---------------------------------------------------------------------------

def test_articles_11_and_12_carry_the_ratified_owasp_agentic_reason():
    """Ratified is not the same as silent.

    Before this, `owasp_agentic` was simply absent from both articles, which is
    indistinguishable from an oversight. The ruling required the reason to live
    in the crosswalk itself.
    """
    for article in ("11", "12"):
        block = _mapping(article).get("owasp_agentic")
        assert block is not None, (
            f"article_{article} has no owasp_agentic block at all, so a reader "
            f"cannot tell a ratified decision from an omission")
        assert block["items"] == [], (
            f"article_{article} now maps OWASP Agentic items. Owner decision 2 "
            f"ratified leaving it unmapped; adding items reverses a ruling.")
        notes = block.get("notes", "")
        assert notes.strip(), f"article_{article} owasp_agentic has no reason"
        for required in ("AIH 0401", "Annex XIV", "decision 2"):
            assert required in notes, (
                f"article_{article} owasp_agentic notes omit {required!r}. The "
                f"reason must name the code, the annex it sits in, and the "
                f"ruling, or it is an assertion rather than a record.")


def test_the_reason_states_that_annex_xiv_attaches_no_obligation():
    """The load-bearing legal point, in both places.

    If a mapping were added on the strength of AIH 0401 existing, it would
    assert a regulatory relationship the text does not create. That claim is
    what the ratification rests on, so it has to be written down.
    """
    for article in ("11", "12"):
        notes = _mapping(article)["owasp_agentic"]["notes"]
        assert "no obligation" in notes.lower(), notes


def test_the_annex_xiv_delta_log_entry_backs_the_reason():
    entry = json.loads(ANNEX_XIV_ENTRY.read_text(encoding="utf-8"))
    assert entry["confidence"] == "verified-primary"
    assert "AIH 0401" in entry["summary"]
    assert "Agentic AI" in entry["summary"]
    # The entry's own watch list is what re-opens the question later.
    impacts = entry["impact_on_regula_patterns"]
    assert any("AIH 0401" in i.get("notes", "") for i in impacts), (
        "the Annex XIV entry no longer records what would re-open the OWASP "
        "Agentic crosswalk question; a ratified decision with no trigger list "
        "becomes a permanent one by accident")


# ---------------------------------------------------------------------------
# The amendment has to reach a reader, not just sit in the file
# ---------------------------------------------------------------------------

def test_the_cli_text_output_surfaces_the_amendment():
    """`regula map-frameworks` must not show a reader the pre-Omnibus duty only.

    `format_mapping_text` renders a fixed set of fields, so data added to the
    crosswalk is invisible in the default output unless the formatter is
    taught about it. Showing the base requirement alone is showing stale law.
    """
    import framework_mapper as fm
    mapping = fm.map_to_frameworks(articles=["11"], frameworks=["eu-ai-act"])
    text = fm.format_mapping_text(mapping)
    assert "Amended by:" in text, text
    assert OMNIBUS in text, text
    assert "simplified" in text, text

    # And an article with no amendment must not grow an empty label.
    plain = fm.format_mapping_text(
        fm.map_to_frameworks(articles=["12"], frameworks=["eu-ai-act"]))
    assert "Amended by:" not in plain, plain


def test_both_yaml_parsers_read_the_new_fields():
    """The crosswalk has a pyyaml path and a hand-rolled fallback.

    Stdlib-only is a hard constraint for this project, so the fallback is a
    real code path and not a formality. A structure only pyyaml can read would
    make the amendment vanish for anyone without the optional dependency.
    """
    import yaml
    from policy_config import _parse_yaml_fallback

    raw = CROSSWALK.read_text(encoding="utf-8")
    strict = yaml.safe_load(raw)["mappings"]["article_11"]
    lenient = _parse_yaml_fallback(raw)["mappings"]["article_11"]

    assert "amended_by" in strict["eu_ai_act"]
    assert "amended_by" in lenient["eu_ai_act"], (
        "the fallback YAML parser cannot see the amendment fields; keep them "
        "flat scalars, not block sequences of mappings")
    assert "owasp_agentic" in strict and "owasp_agentic" in lenient
