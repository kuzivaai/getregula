# regula-ignore
"""Tests for consultant engagement metadata (engagement.py).

Covers: field loading and precedence, value normalisation, exec summary
rendering (including HTML escaping), and evidence-pack manifest
inclusion/byte-compatibility.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from engagement import (
    ENGAGEMENT_FIELDS, load_engagement, engagement_from_args, _clean,
)
from exec_summary import generate_exec_summary


# ---------------------------------------------------------------------------
# load_engagement: sources and precedence
# ---------------------------------------------------------------------------

def test_field_tuple_is_stable():
    """Field order is presentation order in deliverables — a change here
    changes every rendered deliverable, so it must be deliberate."""
    assert ENGAGEMENT_FIELDS == ("client", "prepared_by", "reference")

def test_empty_when_nothing_configured():
    assert load_engagement(policy={}) == {}

def test_loads_from_policy_section():
    policy = {"engagement": {"client": "Acme Ltd", "prepared_by": "PK Advisory",
                             "reference": "ENG-1"}}
    result = load_engagement(policy=policy)
    assert result == {"client": "Acme Ltd", "prepared_by": "PK Advisory",
                      "reference": "ENG-1"}

def test_cli_overrides_win_per_field():
    policy = {"engagement": {"client": "Policy Client", "reference": "ENG-1"}}
    result = load_engagement(policy=policy, overrides={"client": "Flag Client"})
    assert result["client"] == "Flag Client"
    assert result["reference"] == "ENG-1"  # untouched fields survive

def test_empty_override_does_not_erase_policy_value():
    policy = {"engagement": {"client": "Policy Client"}}
    result = load_engagement(policy=policy, overrides={"client": None})
    assert result["client"] == "Policy Client"

def test_non_dict_engagement_section_ignored():
    assert load_engagement(policy={"engagement": "not a dict"}) == {}
    assert load_engagement(policy={"engagement": ["list"]}) == {}

def test_unknown_fields_dropped():
    policy = {"engagement": {"client": "A", "malicious_extra": "x"}}
    assert "malicious_extra" not in load_engagement(policy=policy)

def test_project_path_policy_wins_over_cwd(tmp_path):
    proj = tmp_path / "client"
    proj.mkdir()
    (proj / "regula-policy.yaml").write_text(
        'engagement:\n  client: "Project Client"\n', encoding="utf-8")
    result = load_engagement(project_path=str(proj))
    assert result.get("client") == "Project Client"


# ---------------------------------------------------------------------------
# Value normalisation
# ---------------------------------------------------------------------------

def test_clean_collapses_whitespace_and_newlines():
    assert _clean("  a\n b\t c  ") == "a b c"

def test_clean_caps_length():
    assert len(_clean("x" * 10_000)) == 200

def test_clean_handles_none_and_non_strings():
    assert _clean(None) == ""
    assert _clean(12345) == "12345"


# ---------------------------------------------------------------------------
# engagement_from_args
# ---------------------------------------------------------------------------

def test_engagement_from_args_maps_flags():
    class Args:
        client = "C"
        prepared_by = "P"
        engagement_ref = "R"
    result = engagement_from_args(Args())
    assert result == {"client": "C", "prepared_by": "P", "reference": "R"}

def test_engagement_from_args_tolerates_missing_attrs():
    class Args:
        pass
    result = engagement_from_args(Args())
    assert result == {"client": None, "prepared_by": None, "reference": None}


# ---------------------------------------------------------------------------
# Exec summary rendering
# ---------------------------------------------------------------------------

def test_exec_summary_renders_engagement_lines():
    html = generate_exec_summary([], "proj", engagement={
        "client": "Acme Ltd", "prepared_by": "PK Advisory", "reference": "ENG-1"})
    assert "Prepared for:</strong> Acme Ltd" in html
    assert "Prepared by:</strong> PK Advisory" in html
    assert "Engagement ref:</strong> ENG-1" in html

def test_exec_summary_without_engagement_unchanged():
    html = generate_exec_summary([], "proj")
    assert "Prepared for" not in html
    assert "Prepared by" not in html
    assert "Engagement ref" not in html

def test_exec_summary_escapes_engagement_values():
    html = generate_exec_summary([], "proj", engagement={
        "client": 'Evil <script>alert(1)</script> & Co'})
    assert "<script>" not in html
    assert "Evil &lt;script&gt;" in html

def test_exec_summary_escapes_project_name_and_finding_fields():
    findings = [{"tier": "high_risk", "category": "employment",
                 "file": "<img src=x onerror=alert(1)>.py", "line": 3,
                 "description": "desc & <b>bold</b>", "confidence_score": 70}]
    html = generate_exec_summary(findings, "Acme <script>")
    assert "<script>" not in html
    assert "<img src=x" not in html
    assert "&lt;img src=x" in html


# ---------------------------------------------------------------------------
# Evidence pack manifest
# ---------------------------------------------------------------------------

def _make_project(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "app.py").write_text("import openai\n", encoding="utf-8")
    return proj

def test_manifest_carries_engagement_block(tmp_path):
    from evidence_pack import generate_evidence_pack
    proj = _make_project(tmp_path)
    result = generate_evidence_pack(
        str(proj), output_dir=str(tmp_path),
        engagement={"client": "Acme Ltd", "reference": "ENG-1"})
    assert result["manifest"]["engagement"] == {
        "client": "Acme Ltd", "reference": "ENG-1"}

def test_manifest_omits_engagement_when_absent(tmp_path):
    from evidence_pack import generate_evidence_pack
    proj = _make_project(tmp_path)
    result = generate_evidence_pack(str(proj), output_dir=str(tmp_path))
    assert "engagement" not in result["manifest"], (
        "unsigned manifest must stay byte-compatible when no engagement "
        "metadata is configured")
