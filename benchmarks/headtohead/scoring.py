#!/usr/bin/env python3
# regula-ignore
"""FP-penalising benchmark scoring, adapted from the CASTLE Score.

Source: Dubniczky et al., "CASTLE: Benchmarking Dataset for Static Code
Analyzers and LLMs towards CWE Detection" (arXiv:2503.09433), Section 3.3.
Their per-test scoring: a correct detection earns a 5-point base MINUS one
point per extraneous finding on the same test, PLUS a severity bonus
(b_max = 5, decreasing with the CWE's MITRE Top-25 rank); a clean test
with no findings earns 2; otherwise each reported finding costs a point.

ADAPTATION (stated, not hidden): Regula's domain is AI-regulation risk
tiers, not CWEs, so the severity bonus ranks risk tiers instead of MITRE
ranks. Everything else keeps the CASTLE shape. Results produced with this
module must be described as "adapted from the CASTLE Score", never as the
CASTLE Score itself.

A test case is a dict:
    {"id": str, "expected_tier": str or None, "findings": [tier, ...]}
where expected_tier None means a clean case, and findings are the tiers of
the findings a tool reported on that case.

Stdlib only.
"""

import sys

BASE_POINTS = 5
TRUE_NEGATIVE_POINTS = 2

# Severity bonus: replaces CASTLE's MITRE-rank bonus (b_max = 5) with the
# risk-tier ordering the EU AI Act itself establishes.
TIER_BONUS = {
    "prohibited": 5,
    "high_risk": 4,
    "ai_security": 3,
    "agent_autonomy": 3,
    "limited_risk": 2,
    "minimal_risk": 1,
}


def score_case(case: dict) -> int:
    expected = case.get("expected_tier")
    findings = case.get("findings", [])
    if expected is None:
        if not findings:
            return TRUE_NEGATIVE_POINTS
        return -len(findings)
    if expected in findings:
        extraneous = len(findings) - 1
        return BASE_POINTS - extraneous + TIER_BONUS.get(expected, 0)
    return -len(findings)


def score_run(cases: list) -> dict:
    per_case = {c["id"]: score_case(c) for c in cases}
    detected = sum(1 for c in cases
                   if c.get("expected_tier") is not None
                   and c["expected_tier"] in c.get("findings", []))
    positives = sum(1 for c in cases if c.get("expected_tier") is not None)
    clean = [c for c in cases if c.get("expected_tier") is None]
    false_alarm_cases = sum(1 for c in clean if c.get("findings"))
    return {
        "score": sum(per_case.values()),
        "cases": len(cases),
        "positives": positives,
        "detected": detected,
        "clean_cases": len(clean),
        "clean_cases_with_false_alarms": false_alarm_cases,
        "per_case": per_case,
    }


def _self_test() -> int:
    cases = [
        # detected high_risk, no extraneous: 5 + 4 = 9
        {"id": "t1", "expected_tier": "high_risk",
         "findings": ["high_risk"]},
        # detected prohibited with 2 extraneous: 5 - 2 + 5 = 8
        {"id": "t2", "expected_tier": "prohibited",
         "findings": ["prohibited", "limited_risk", "minimal_risk"]},
        # clean case, no findings: 2
        {"id": "t3", "expected_tier": None, "findings": []},
        # clean case, 3 false alarms: -3
        {"id": "t4", "expected_tier": None,
         "findings": ["high_risk", "high_risk", "limited_risk"]},
        # missed vulnerability, 1 wrong-tier finding: -1
        {"id": "t5", "expected_tier": "high_risk",
         "findings": ["minimal_risk"]},
    ]
    result = score_run(cases)
    expected_total = 9 + 8 + 2 - 3 - 1
    ok = result["score"] == expected_total
    print(f"self-test: score={result['score']} expected={expected_total} "
          f"{'OK' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(_self_test())
