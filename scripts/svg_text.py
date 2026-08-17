#!/usr/bin/env python3
"""Read the text a terminal-recorder SVG publishes.

An SVG produced by a terminal recorder is not an image in any useful sense: it
is a transcript, and every character of it sits in `<text>` nodes. Three
instruments treated `site/assets/demo/regula-check.svg` as an opaque asset
purely because of its suffix, while `README.md:32` rendered it as the first
visual on the project's front page. This module is what lets a guard read it.

WHY GROUPING MATTERS, AND WHY A NAIVE READING IS WRONG TWICE.

A recorder emits ONE `<text>` element PER WORD, positioned by `x` on a shared
`y` baseline. So:

  1. Reading each node on its own cannot see a phrase. `Confidence` and
     `scores` are separate nodes, and a guard matching `Confidence scores`
     against node text finds nothing. That is the same defect N107 recorded for
     inline markup splitting `zero <strong>network</strong> calls`, in a new
     carrier.
  2. Grouping on `y` ALONE is also wrong. svg-term emits reusable `<symbol>`
     definitions that each restart their coordinate system at `y="1.67"`, so a
     y-only key merges unrelated lines from different symbols into one run-on
     line. Measured on the shipped `regula-bare.svg`: a y-only key collapsed 41
     distinct lines into 9, the first of which was 1,400 characters of
     interleaved words in x order.

The key is therefore `(parent element, y)`, joined in `x` order, which
reconstructs the line a reader sees.

STATED LIMIT. Groups are emitted in first-appearance document order, so
`<symbol>` definitions come before the main flow that `<use>`s them. Every LINE
is intact and in reading order within itself; the ORDER OF LINES is document
order, not playback order. That is sufficient for the questions asked of this
module (does this file contain a retired marker; does this anchor appear) and
insufficient for reconstructing a playback, which nothing here claims to do.

FAILING CLOSED. A file that cannot be parsed raises `SvgTextError` rather than
returning an empty result. An empty result is the PASS value for every caller,
so swallowing a parse failure would turn an unreadable carrier into a clean
one, which is measurement rule 4's blank gate and is exactly how the N55(a)
vacuous pass worked.
"""
from __future__ import annotations

import sys
from html import unescape
from pathlib import Path
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).parent))

SVG_NS = "{http://www.w3.org/2000/svg}"
TEXT_TAG = SVG_NS + "text"


class SvgTextError(Exception):
    """An SVG could not be read. Never downgraded to an empty result."""


def _number(value, default: float = 0.0) -> float:
    """Coordinate as a float. Units and percentages are position, not content."""
    if value is None:
        return default
    text = str(value).strip()
    for unit in ("px", "pt", "em", "ex", "%", "mm", "cm", "in"):
        if text.endswith(unit):
            text = text[: -len(unit)]
            break
    try:
        return float(text)
    except ValueError:
        return default


def _node_text(node) -> str:
    """Every character inside one `<text>`, including `<tspan>` children."""
    parts = []
    if node.text:
        parts.append(node.text)
    for child in node.iter():
        if child is node:
            continue
        if child.text:
            parts.append(child.text)
        if child.tail:
            parts.append(child.tail)
    return unescape("".join(parts))


def rendered_lines(source: str) -> list[str]:
    """The lines a reader sees, one string per rendered line.

    Raises SvgTextError if the document cannot be parsed.
    """
    try:
        root = ElementTree.fromstring(source)
    except ElementTree.ParseError as exc:
        raise SvgTextError(f"SVG could not be parsed: {exc}") from exc

    parent_of = {}
    for parent in root.iter():
        for child in parent:
            parent_of[id(child)] = parent

    rows: dict[tuple[int, float], list[tuple[float, str]]] = {}
    order: list[tuple[int, float]] = []
    for node in root.iter():
        if node.tag != TEXT_TAG:
            continue
        text = _node_text(node)
        if not text.strip():
            continue
        key = (id(parent_of.get(id(node), root)), round(_number(node.get("y"), -1.0), 3))
        if key not in rows:
            rows[key] = []
            order.append(key)
        rows[key].append((_number(node.get("x")), text))

    lines = []
    for key in order:
        chunks = sorted(rows[key], key=lambda pair: pair[0])
        lines.append(" ".join(chunk for _, chunk in chunks).strip())
    return lines


def text_of(source: str) -> str:
    """The whole transcript as newline-separated lines."""
    return "\n".join(rendered_lines(source))


def read_text_of(path) -> str:
    """`text_of` for a file on disk."""
    return text_of(Path(path).read_text(encoding="utf-8", errors="replace"))


def carries_text(source: str) -> bool:
    """True if this SVG publishes readable words, rather than being a drawing.

    The distinction a classifier needs is not the suffix. A terminal recording
    can carry a claim; a logo cannot. Deciding by content means a future icon
    added under `site/` is not mislabelled as claim-capable, and a future
    recording is not missed.
    """
    return any(line.strip() for line in rendered_lines(source))


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="svg_text",
        description="Print the text a terminal-recorder SVG publishes.")
    parser.add_argument("paths", nargs="+", help="SVG files to read")
    parser.add_argument("--count", action="store_true",
                        help="print the line count instead of the lines")
    args = parser.parse_args(argv)

    for raw in args.paths:
        path = Path(raw)
        try:
            lines = rendered_lines(path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, SvgTextError) as exc:
            print(f"{path}: {exc}", file=sys.stderr)
            return 1
        if args.count:
            print(f"{path}: {len(lines)} line(s)")
            continue
        print(f"=== {path} ===")
        for line in lines:
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
