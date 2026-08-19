# regula-ignore
"""Reading the text a terminal-recorder SVG publishes.

`site/assets/demo/regula-check.svg` was rendered by `README.md` as the first
visual on the project's front page while three instruments classified it as an
opaque asset on the strength of its suffix. It was not an image: the whole
transcript sat in `<text>` nodes, and it published `Confidence scores: 0-100`,
the framing retired across nine surfaces, plus a sibling recording showing
`regula-ai-1.6.1` against a current 1.9.0 and a 36-command listing against a
registry of 62.

These checks pin the two ways a naive reading gets it wrong, and one way a
careless one fails open.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from svg_text import (  # noqa: E402
    SvgTextError,
    carries_text,
    rendered_lines,
    text_of,
)

REPO = Path(__file__).resolve().parent.parent
_TAG = re.compile(r"<[^>]+>")

# The retired framing, assembled rather than written whole. This module is
# inside the corpus its own subject scans, and `tests/` is excluded from that
# scan today; assembling it means the check does not depend on that exclusion
# staying true. Same discipline N111 recorded after a comment explaining a
# count-guard fix tripped the count guard.
_RETIRED = "Confidence" + " " + "scores"


def _naive_tag_strip(source: str) -> str:
    """What a guard does when it treats an SVG as a bag of bytes."""
    return re.sub(r"\s+", " ", html.unescape(_TAG.sub(" ", source))).strip()


def test_words_on_one_baseline_are_joined_into_the_line_a_reader_sees():
    """A recorder emits one <text> per WORD, so a per-node reading sees none."""
    source = ('<svg xmlns="http://www.w3.org/2000/svg">'
              f'<text x="0" y="1">{_RETIRED.split()[0]}</text>'
              f'<text x="70" y="1">{_RETIRED.split()[1]}:</text>'
              '<text x="130" y="1">0-100</text></svg>')
    assert rendered_lines(source) == [f"{_RETIRED}: 0-100"]
    assert _RETIRED in text_of(source)


def test_a_y_only_key_would_merge_unrelated_lines_and_this_one_does_not():
    """svg-term restarts every <symbol> at the same y.

    Grouping on y alone merged 41 distinct lines of the shipped
    `regula-bare.svg` into 9, the first of them 1,400 characters of interleaved
    words. The key is (parent element, y), so two symbols sharing a baseline
    stay two lines.
    """
    source = ('<svg xmlns="http://www.w3.org/2000/svg"><defs>'
              '<symbol id="a"><text x="0" y="1.67">first</text>'
              '<text x="20" y="1.67">line</text></symbol>'
              '<symbol id="b"><text x="0" y="1.67">second</text>'
              '<text x="20" y="1.67">line</text></symbol>'
              '</defs></svg>')
    assert rendered_lines(source) == ["first line", "second line"]


def test_reconstruction_beats_tag_stripping_where_it_matters():
    """Measured both ways, and the honest result is recorded in the assertions.

    On the shape svg-term actually emits, document order equals x order and a
    naive tag-strip would have found the marker too. It fails on two shapes that
    are just as legal: words emitted out of x order, and a node from another
    line interleaved between two words of this one. The reconstruction is
    load-bearing for the general case and was not for the specific shipped
    file, and both halves are asserted here rather than only the flattering one.
    """
    word_a, word_b = _RETIRED.split()
    same_order = ('<svg xmlns="http://www.w3.org/2000/svg">'
                  f'<text x="0" y="1">{word_a}</text>'
                  f'<text x="70" y="1">{word_b}</text></svg>')
    reversed_order = ('<svg xmlns="http://www.w3.org/2000/svg">'
                      f'<text x="70" y="1">{word_b}</text>'
                      f'<text x="0" y="1">{word_a}</text></svg>')
    interleaved = ('<svg xmlns="http://www.w3.org/2000/svg">'
                   f'<text x="0" y="1">{word_a}</text>'
                   '<text x="0" y="20">$ regula check .</text>'
                   f'<text x="70" y="1">{word_b}</text></svg>')

    assert _RETIRED in _naive_tag_strip(same_order)
    assert _RETIRED in text_of(same_order)

    assert _RETIRED not in _naive_tag_strip(reversed_order)
    assert _RETIRED in text_of(reversed_order)

    assert _RETIRED not in _naive_tag_strip(interleaved)
    assert _RETIRED in text_of(interleaved)


def test_tspan_children_belong_to_their_parent_text_node():
    source = ('<svg xmlns="http://www.w3.org/2000/svg">'
              '<text x="0" y="1">Files <tspan>scanned:</tspan> 1</text></svg>')
    assert rendered_lines(source) == ["Files scanned: 1"]


def test_entities_are_decoded_so_accented_copy_can_match():
    """N107's second defect, in this carrier: `c&oacute;digo` never matched."""
    source = ('<svg xmlns="http://www.w3.org/2000/svg">'
              '<text x="0" y="1">c&#243;digo</text></svg>')
    assert rendered_lines(source) == ["código"]


def test_an_unparseable_svg_raises_rather_than_reading_as_empty():
    """The fail-open shape this module exists to refuse.

    Empty is the PASS value for every caller, so returning it on a parse
    failure would turn an unreadable carrier into a clean one. That is
    measurement rule 4's blank gate and is exactly how the N55(a) vacuous pass
    worked: swallowing the error returned the answer that means "nothing wrong".
    """
    for broken in ('<svg xmlns="http://www.w3.org/2000/svg"><text>unclosed',
                   "not xml at all",
                   ""):
        try:
            rendered_lines(broken)
        except SvgTextError:
            continue
        raise AssertionError(f"parsed without raising: {broken!r}")


def test_carries_text_separates_a_recording_from_a_drawing():
    recording = ('<svg xmlns="http://www.w3.org/2000/svg">'
                 '<text x="0" y="1">Files scanned: 1</text></svg>')
    drawing = ('<svg xmlns="http://www.w3.org/2000/svg">'
               '<path d="M0 0h10v10H0z"/></svg>')
    whitespace_only = ('<svg xmlns="http://www.w3.org/2000/svg">'
                       '<text x="0" y="1">   </text></svg>')
    assert carries_text(recording) is True
    assert carries_text(drawing) is False
    assert carries_text(whitespace_only) is False


def test_the_shipped_sidebar_icon_is_a_drawing_and_not_a_transcript():
    """A real tracked file, so this is not only a fixture exercise.

    The VS Code sidebar icon is the case a suffix rule would have got wrong in
    the other direction: including `.svg` unconditionally would classify a logo
    as reader-facing text.
    """
    icon = REPO / "vscode-extension/resources/regula-sidebar.svg"
    assert icon.is_file(), icon
    assert carries_text(icon.read_text(encoding="utf-8")) is False
