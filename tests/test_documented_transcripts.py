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

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from verify_transcripts import (  # noqa: E402
    BenchmarkContract,
    QUALIFIED_OUTPUT,
    RETIRED_MARKERS,
    STRUCTURED_TEXT_SUFFIXES,
    SURFACE_SUFFIXES,
    discover_benchmark_contracts,
    load_manifest,
    normalise,
    public_benchmark_surfaces,
    qualified_output_is_really_emitted,
    retired_marker_hits,
    retired_markers_are_unreachable,
    surface_text,
    tracked_surfaces,
    unqualified_output_hits,
    verify_benchmark_contracts,
    verify_published_benchmarks,
    verify,
)

REPO = Path(__file__).resolve().parent.parent

# Assembled rather than written whole: this module sits inside the corpus the
# marker scan reads, and `tests/` being excluded from it is a fact that could
# change. N111 recorded the same trap when a comment explaining a count-guard
# fix tripped the count guard.
_RETIRED_FRAMING = "Confidence" + " " + "scores"


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


# ---------------------------------------------------------------------------
# Published benchmark commands and the figures beside them
# ---------------------------------------------------------------------------

def test_every_published_benchmark_instruction_reproduces_in_isolation():
    """Run the discovered commands and prove their writes stay out of the tree."""
    result = REPO / "benchmarks/results/PRECISION.json"
    before = result.read_bytes()
    problems, checked = verify_published_benchmarks()
    after = result.read_bytes()

    assert checked >= 8, (
        f"only {checked} benchmark contracts were found; the public-surface "
        "enumeration or block parser has narrowed")
    assert not problems, (
        "published benchmark instructions that do not reproduce:\n  "
        + "\n  ".join(problems))
    assert after == before, (
        "a benchmark verifier changed benchmarks/results/PRECISION.json in the "
        "working tree instead of containing the write in its isolated checkout")


def test_benchmark_surface_corpus_comes_from_the_delivery_inventory():
    surfaces = public_benchmark_surfaces()
    assert len(surfaces) > 80, len(surfaces)
    for expected in (
            "docs/benchmarks/PRECISION_RECALL_2026_04.md",
            "docs/cli-reference.md",
            "site/blog/blog-aicdi-governance-gaps.html",
            "site/llms-full.txt"):
        assert expected in surfaces, expected
    assert "CHANGELOG.md" not in surfaces, (
        "the changelog is a historical record, not an active product promise; "
        "the inventory classification has been ignored")


def _benchmark_fixture(tmp_path, prose: str):
    root = tmp_path / "repo"
    surface = root / "docs/result.md"
    script = root / "benchmarks/label.py"
    surface.parent.mkdir(parents=True)
    script.parent.mkdir(parents=True)
    surface.write_text(prose, encoding="utf-8")
    script.write_text("# local fixture\n", encoding="utf-8")
    inventory = root / "inventory.json"
    inventory.write_text(json.dumps({"records": [{
        "source": "docs/result.md",
        "classification": "active_product",
        "claim_capable": True,
    }]}), encoding="utf-8")
    contracts = discover_benchmark_contracts(inventory, root)
    assert len(contracts) == 1, contracts
    return root, contracts


def test_control_a_wrong_figure_beside_the_right_command_fails(tmp_path):
    root, contracts = _benchmark_fixture(
        tmp_path,
        "Reproduce the 99.9% primary precision with "
        "`python3 benchmarks/label.py score --corpus library`.\n",
    )
    real_output = "Precision: 15.2% (measured)\n"
    problems = verify_benchmark_contracts(
        contracts, runner=lambda _command: (real_output, 0), root=root)
    assert problems and "99.9%" in problems[0], problems


def test_control_a_wrong_command_fails_even_if_a_breakdown_has_the_figure(
        tmp_path):
    """The exact weak check the dossier proposed must not be reintroduced."""
    root, contracts = _benchmark_fixture(
        tmp_path,
        "Reproduce the 15.2% primary precision with "
        "`python3 benchmarks/label.py score`.\n",
    )
    wrong_command_output = (
        "Precision by Corpus Type\n"
        "library 39 218 257 15.2%\n"
        "Precision: 36.8% (measured)\n"
    )
    problems = verify_benchmark_contracts(
        contracts, runner=lambda _command: (wrong_command_output, 0), root=root)
    assert problems, "a secondary 15.2% breakdown was accepted as the result"
    assert "secondary breakdown" in problems[0], problems


def test_control_the_right_primary_result_passes(tmp_path):
    root, contracts = _benchmark_fixture(
        tmp_path,
        "Reproduce the 15.2% primary precision with "
        "`python3 benchmarks/label.py score --corpus library`.\n",
    )
    problems = verify_benchmark_contracts(
        contracts,
        runner=lambda _command: ("Precision: 15.2% (measured)\n", 0),
        root=root,
    )
    assert not problems, problems


def test_benchmark_executor_refuses_shell_syntax(tmp_path):
    root = tmp_path / "repo"
    script = root / "benchmarks/label.py"
    script.parent.mkdir(parents=True)
    script.write_text("# local fixture\n", encoding="utf-8")
    contract = BenchmarkContract(
        surface="docs/result.md",
        command=("python3", "benchmarks/label.py", "score", ";", "touch"),
        figure="15.2%",
        context="planted unsafe command",
    )
    problems = verify_benchmark_contracts([contract], runner=lambda _c: ("", 0),
                                          root=root)
    assert problems and "unsafe argument refused" in problems[0], problems


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


# ---------------------------------------------------------------------------
# Carriers: a transcript is a transcript whatever file holds it
# ---------------------------------------------------------------------------

def test_svg_is_a_scanned_carrier():
    """The gap this closes, stated so it cannot be narrowed back by accident.

    `README.md` rendered `site/assets/demo/regula-check.svg` as the project's
    first visual while `public_surface_inventory.TEXT_SITE`,
    `claim_auditor.SCANNED_SUFFIXES` and this module's own surface filter all
    excluded `.svg` on the strength of the suffix. The file was a terminal
    recording: entirely text.
    """
    assert ".svg" in SURFACE_SUFFIXES
    assert ".svg" in STRUCTURED_TEXT_SUFFIXES
    assert ".yaml" in SURFACE_SUFFIXES and ".yml" in SURFACE_SUFFIXES


def test_a_retired_marker_split_across_svg_text_nodes_is_found(tmp_path):
    """The control the carrier needed, and the reason it is not a byte scan.

    A recorder emits one `<text>` per word. No single node contains the marker;
    only the reconstructed line does. This asserts both halves, so a future
    change that reverts `surface_text` to reading raw bytes fails here rather
    than passing on the accident that svg-term happens to emit words in x
    order.
    """
    first, second = _RETIRED_FRAMING.split()
    planted = tmp_path / "planted.svg"
    planted.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg">'
        f'<text x="0" y="1">{first}</text>'
        f'<text x="70" y="1">{second}:</text>'
        '<text x="130" y="1">0-100</text></svg>',
        encoding="utf-8")

    from xml.etree import ElementTree
    nodes = [n.text for n in ElementTree.parse(planted).iter()
             if n.tag.endswith("}text")]
    assert not any(_RETIRED_FRAMING in (t or "") for t in nodes), nodes

    body = surface_text(planted)
    assert normalise(_RETIRED_FRAMING) in body, body


def test_an_unreadable_svg_is_reported_and_not_read_as_clean(tmp_path):
    """Fail-closed: "I could not read it" must not resolve to "nothing found"."""
    broken = tmp_path / "broken.svg"
    broken.write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>unclosed',
                      encoding="utf-8")
    try:
        surface_text(broken)
    except Exception as exc:  # noqa: BLE001 - the type is asserted below
        assert type(exc).__name__ == "SvgTextError", type(exc).__name__
        return
    raise AssertionError("an unparseable SVG was read as clean text")


# ---------------------------------------------------------------------------
# Current output published without the sentence that qualifies it
# ---------------------------------------------------------------------------

def test_no_published_surface_shows_output_stripped_of_its_qualifier():
    hits = unqualified_output_hits()
    assert not hits, (
        "these surfaces publish current CLI output without the qualifier the "
        "tool prints beside it:\n  " + "\n  ".join(hits))


def test_qualified_output_rules_describe_output_the_tool_really_emits():
    """The positive half, without which the rules are an author's preference.

    A rule whose pattern the CLI never emits, or whose qualifier the CLI has
    stopped printing, fails here instead of quietly policing a shape that no
    longer exists. `retired_markers_are_unreachable` is the same discipline in
    the opposite direction.
    """
    problems = qualified_output_is_really_emitted()
    assert not problems, "\n  ".join(problems)


def test_a_template_expression_is_not_a_classification_line():
    """The false positive this rule had to exclude, pinned in both directions.

    `action.yml` carries `PROHIBITED: ${{ steps.count-findings.outputs...}}`
    twice. That is a YAML mapping key whose value is a variable name, and
    reading it as a legal claim is the N34 class (`ATTRIBUTED_CLAIM` reading the
    tool name `Write` as an attribution verb). The rule requires a prose
    category name after the colon. Both directions are asserted, because a rule
    that only silences is a rule that can be silenced.
    """
    pattern = QUALIFIED_OUTPUT["classification line"]["pattern"]
    tier = "PROHI" + "BITED"
    assert not pattern.search(f"{tier}: ${{{{ steps.count.outputs.n }}}}")
    assert not pattern.search(f"{tier}: $VAR")
    assert pattern.search(f"{tier}: So" + "cial scoring by public authorities")
    assert pattern.search("HIGH-RISK: Employment and workers management")


def test_action_yml_really_is_in_scope_and_really_is_silent():
    """Guard the guard: the exclusion above must not be excluding the file.

    If `action.yml` had simply fallen out of the scanned corpus, the previous
    check would pass for the wrong reason.
    """
    surfaces = tracked_surfaces()
    assert "action.yml" in surfaces, "action.yml is not being scanned at all"
    body = surface_text(REPO / "action.yml")
    tier = "PROHI" + "BITED"
    assert f"{tier}:" in body, "the shape being excluded is not present"
    assert not [h for h in unqualified_output_hits() if h.startswith("action.yml")]


def test_every_qualified_output_rule_is_completely_declared():
    for name, rule in QUALIFIED_OUTPUT.items():
        for field in ("pattern", "qualifiers", "window", "why", "proof_command"):
            assert field in rule, (name, field)
        assert rule["qualifiers"], name
        assert rule["window"] > 0, name
        assert len(rule["why"]) > 30, name
    discover_benchmark_contracts,
    public_benchmark_surfaces,
