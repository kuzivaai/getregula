"""Tests for red-team coverage scoring (handoff.py)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from handoff import (
    COVERAGE_MATRIX,
    OWASP_LLM_TOP_10,
    calculate_coverage_score,
    format_coverage_text,
)

import helpers
from helpers import assert_eq, assert_true


# --- Coverage score per tool ---

def test_garak_coverage_score():
    result = calculate_coverage_score([], "garak")
    # Garak covers 6 of 10 risks by default
    assert_eq(result["coverage_score"], 60, "garak coverage score")
    assert_eq(len(result["risks_covered"]), 6, "garak risks covered count")
    assert_eq(len(result["risks_uncovered"]), 4, "garak risks uncovered count")
    print("  pass: garak coverage score")


def test_giskard_coverage_score():
    result = calculate_coverage_score([], "giskard")
    assert_eq(result["coverage_score"], 50, "giskard coverage score")
    assert_eq(len(result["risks_covered"]), 5, "giskard risks covered count")
    print("  pass: giskard coverage score")


def test_promptfoo_coverage_score():
    result = calculate_coverage_score([], "promptfoo")
    assert_eq(result["coverage_score"], 40, "promptfoo coverage score")
    assert_eq(len(result["risks_covered"]), 4, "promptfoo risks covered count")
    print("  pass: promptfoo coverage score")


def test_deepteam_coverage_score():
    result = calculate_coverage_score([], "deepteam")
    assert_eq(len(result["risks_covered"]), 6, "deepteam risks covered count")
    print("  pass: deepteam coverage score")


def test_pyrit_coverage_score():
    result = calculate_coverage_score([], "pyrit")
    assert_eq(len(result["risks_covered"]), 7, "pyrit risks covered count")
    print("  pass: pyrit coverage score")


# --- Full and zero coverage ---

def test_full_coverage_all_risks():
    """Synthetic scenario: probes covering all 10 risks."""
    # Temporarily patch the coverage matrix to cover all 10 OWASP risks,
    # then call calculate_coverage_score and verify it returns 100%.
    import handoff
    original_matrix = handoff.COVERAGE_MATRIX.get("pyrit", {}).copy()
    try:
        # Add probes for the 3 risks PyRIT doesn't normally cover
        handoff.COVERAGE_MATRIX["pyrit"]["LLM03"] = ["data_poisoning_test"]
        handoff.COVERAGE_MATRIX["pyrit"]["LLM05"] = ["supply_chain_test"]
        handoff.COVERAGE_MATRIX["pyrit"]["LLM09"] = ["hallucination_test"]
        result = calculate_coverage_score([], "pyrit")
        assert_eq(result["coverage_score"], 100, "100% when all 10 risks covered")
        assert_eq(len(result["risks_covered"]), 10, "all 10 risks covered")
        assert_eq(len(result["risks_uncovered"]), 0, "no risks uncovered")
    finally:
        handoff.COVERAGE_MATRIX["pyrit"] = original_matrix
    print("  pass: full coverage scenario")


def test_zero_coverage_no_probes():
    """When specific probes are given that match nothing, score is 0."""
    result = calculate_coverage_score([], "garak", probes=["nonexistent_probe"])
    assert_eq(result["coverage_score"], 0, "zero coverage with no matching probes")
    assert_eq(len(result["risks_covered"]), 0, "no risks covered")
    assert_eq(len(result["risks_uncovered"]), 10, "all risks uncovered")
    print("  pass: zero coverage scenario")


# --- Partial coverage with specific probes ---

def test_partial_coverage_specific_probes():
    """Only promptinject probe -> covers LLM01 only."""
    result = calculate_coverage_score([], "garak", probes=["promptinject"])
    assert_eq(result["coverage_score"], 10, "partial: 1 risk = 10%")
    assert_eq(len(result["risks_covered"]), 1, "partial: 1 risk covered")
    assert_eq(result["risks_covered"][0]["id"], "LLM01", "partial: LLM01 covered")
    print("  pass: partial coverage with specific probes")


def test_partial_coverage_two_probes():
    """promptinject + malwaregen -> LLM01, LLM02, LLM08."""
    result = calculate_coverage_score(
        [], "garak", probes=["promptinject", "malwaregen"]
    )
    covered_ids = {r["id"] for r in result["risks_covered"]}
    assert_true("LLM01" in covered_ids, "LLM01 covered by promptinject")
    assert_true("LLM02" in covered_ids, "LLM02 covered by malwaregen")
    assert_true("LLM08" in covered_ids, "LLM08 covered by malwaregen")
    assert_eq(result["coverage_score"], 30, "3 risks = 30%")
    print("  pass: partial coverage two probes")


# --- Entrypoint coverage ---

def test_entrypoint_coverage():
    eps = [{"file": "a.py", "kind": "openai-chat"}, {"file": "b.py", "kind": "anthropic"}]
    result = calculate_coverage_score(eps, "garak")
    assert_eq(result["entrypoint_coverage"]["total"], 2, "ep total")
    assert_eq(result["entrypoint_coverage"]["covered"], 2, "ep covered")
    print("  pass: entrypoint coverage")


# --- Recommendations ---

def test_recommendations_for_uncovered():
    result = calculate_coverage_score([], "garak")
    assert_true(len(result["recommendations"]) > 0, "has recommendations")
    # Each uncovered risk should appear in recommendations
    rec_text = "\n".join(result["recommendations"])
    for r in result["risks_uncovered"]:
        assert_true(r["id"] in rec_text, f"{r['id']} in recommendations")
    print("  pass: recommendations for uncovered risks")


# --- Text formatting ---

def test_format_coverage_text_contains_score():
    result = calculate_coverage_score([], "garak")
    text = format_coverage_text(result)
    assert_true("60%" in text, "text contains score percentage")
    assert_true("garak" in text, "text contains tool name")
    print("  pass: format text contains score")


def test_format_coverage_text_has_checkmarks_and_crosses():
    result = calculate_coverage_score([], "garak")
    text = format_coverage_text(result)
    assert_true("\u2714" in text, "text contains checkmark")
    assert_true("\u2718" in text, "text contains cross")
    print("  pass: format text has checkmarks and crosses")


def test_format_coverage_text_red_for_low_score():
    result = calculate_coverage_score([], "garak", probes=["promptinject"])
    text = format_coverage_text(result)
    # RED ANSI code should appear for 10% score
    assert_true("\033[31m" in text, "red ANSI for low score")
    print("  pass: format text red for low score")


def test_format_coverage_text_green_for_high_score():
    result = calculate_coverage_score([], "pyrit")
    text = format_coverage_text(result)
    # PyRIT covers 7/10 = 70% -> yellow, not green
    assert_true("\033[33m" in text, "yellow ANSI for 70% score")
    print("  pass: format text yellow for 70% score")


# --- Edge: unknown tool ---

def test_unknown_tool_returns_zero():
    result = calculate_coverage_score([], "unknown_tool_xyz")
    assert_eq(result["coverage_score"], 0, "unknown tool: 0%")
    assert_eq(len(result["risks_covered"]), 0, "unknown tool: no covered")
    assert_eq(len(result["risks_uncovered"]), 10, "unknown tool: all uncovered")
    assert_true(
        any("Unknown tool" in r for r in result["recommendations"]),
        "unknown tool: helpful message",
    )
    print("  pass: unknown tool returns 0% with helpful message")


def test_unknown_tool_case_insensitive():
    result = calculate_coverage_score([], "Garak")
    assert_eq(result["coverage_score"], 60, "case insensitive: Garak -> 60%")
    print("  pass: tool name is case insensitive")


# --- Matrix structure ---

def test_coverage_matrix_has_all_five_tools():
    expected = {"garak", "giskard", "promptfoo", "deepteam", "pyrit"}
    assert_eq(set(COVERAGE_MATRIX.keys()), expected, "matrix has 5 tools")
    print("  pass: coverage matrix has all 5 tools")


def test_owasp_top_10_has_10_entries():
    assert_eq(len(OWASP_LLM_TOP_10), 10, "OWASP list has 10 entries")
    print("  pass: OWASP top 10 has 10 entries")


# --- Runner ---
if __name__ == "__main__":
    import inspect

    test_funcs = [
        obj
        for name, obj in sorted(globals().items())
        if name.startswith("test_") and callable(obj)
    ]
    print(f"Running {len(test_funcs)} red-team coverage tests...")
    for fn in test_funcs:
        try:
            fn()
        except Exception as e:
            helpers.failed += 1
            print(f"  FAIL: {fn.__name__} raised {e}")
    print(f"\n{helpers.passed} passed, {helpers.failed} failed")
    raise SystemExit(1 if helpers.failed else 0)
