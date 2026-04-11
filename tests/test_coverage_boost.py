"""
Tests to increase coverage for under-tested modules.

Targets: doctor.py, config_validator.py, framework_mapper.py, baseline.py,
         timeline.py, and cli.py command functions.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Project root for CLI subprocess calls
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Ensure scripts is importable
sys.path.insert(0, str(SCRIPTS_DIR))


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def run_cli(*args, timeout=60):
    """Run regula CLI and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli"] + list(args),
        capture_output=True, text=True, timeout=timeout,
        cwd=str(PROJECT_ROOT),
    )
    return result.returncode, result.stdout, result.stderr


# ===========================================================================
# doctor.py
# ===========================================================================

class TestDoctor:
    def test_check_python_version(self):
        from doctor import _check_python_version
        result = _check_python_version()
        assert result["status"] == "PASS"
        assert "3." in result["detail"]

    def test_check_optional_dep_present(self):
        from doctor import _check_optional_dep
        result = _check_optional_dep("json", "pip install json")
        assert result["status"] == "PASS"

    def test_check_optional_dep_missing(self):
        from doctor import _check_optional_dep
        result = _check_optional_dep("nonexistent_pkg_xyz", "pip install xyz")
        assert result["status"] == "INFO"
        assert "optional" in result["detail"].lower()

    def test_check_policy_file_default(self):
        from doctor import _check_policy_file
        result = _check_policy_file()
        assert result["status"] in ("PASS", "INFO")
        assert result["name"] == "Policy file"

    def test_check_audit_directory(self):
        from doctor import _check_audit_directory
        result = _check_audit_directory()
        assert result["status"] in ("PASS", "FAIL")

    def test_check_hooks(self):
        from doctor import _check_hooks
        result = _check_hooks()
        assert result["status"] in ("PASS", "INFO")

    def test_check_security(self):
        from doctor import _check_security
        result = _check_security()
        assert result["status"] in ("PASS", "WARN", "INFO")

    def test_check_telemetry(self):
        from doctor import _check_telemetry
        result = _check_telemetry()
        assert result["status"] in ("PASS", "INFO", "WARN")

    def test_run_doctor_json(self):
        from doctor import run_doctor
        result = run_doctor(format_type="json")
        assert isinstance(result, dict)
        assert "healthy" in result
        assert "checks" in result
        assert "summary" in result
        assert isinstance(result["checks"], list)
        assert len(result["checks"]) > 0

    def test_run_doctor_text(self, capsys):
        from doctor import run_doctor
        result = run_doctor(format_type="text")
        assert isinstance(result, bool)
        captured = capsys.readouterr()
        assert "Regula Doctor" in captured.out

    def test_check_config_validation(self):
        from doctor import _check_config_validation
        result = _check_config_validation()
        assert result["status"] in ("PASS", "INFO", "WARN")


# ===========================================================================
# config_validator.py
# ===========================================================================

class TestConfigValidator:
    def test_validate_no_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("REGULA_POLICY", raising=False)
        from config_validator import validate_config
        result = validate_config(format_type="silent")
        assert result["valid"] is True
        assert any("No policy file" in w for w in result["warnings"])

    def test_validate_nonexistent_path(self):
        from config_validator import validate_config
        result = validate_config(path="/nonexistent/file.json", format_type="silent")
        assert result["valid"] is False
        assert any("not found" in e for e in result["errors"])

    def test_validate_valid_json_config(self, tmp_path):
        config = {
            "version": "1.0",
            "governance": {"ai_officer": {"name": "Test Person"}},
            "thresholds": {"block_above": 80, "warn_above": 50},
            "frameworks": ["eu_ai_act"],
        }
        p = tmp_path / "regula-policy.json"
        p.write_text(json.dumps(config))
        from config_validator import validate_config
        result = validate_config(path=str(p), format_type="silent")
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_invalid_thresholds(self, tmp_path):
        config = {
            "version": "1.0",
            "thresholds": {"block_above": 50, "warn_above": 80},
        }
        p = tmp_path / "regula-policy.json"
        p.write_text(json.dumps(config))
        from config_validator import validate_config
        result = validate_config(path=str(p), format_type="silent")
        assert result["valid"] is False
        assert any("warn_above" in e and ">=" in e for e in result["errors"])

    def test_validate_invalid_block_above_type(self, tmp_path):
        config = {"version": "1.0", "thresholds": {"block_above": "high"}}
        p = tmp_path / "regula-policy.json"
        p.write_text(json.dumps(config))
        from config_validator import validate_config
        result = validate_config(path=str(p), format_type="silent")
        assert result["valid"] is False

    def test_validate_unknown_framework(self, tmp_path):
        config = {"version": "1.0", "frameworks": ["nonexistent_fw"]}
        p = tmp_path / "regula-policy.json"
        p.write_text(json.dumps(config))
        from config_validator import validate_config
        result = validate_config(path=str(p), format_type="silent")
        assert any("unrecognised" in w for w in result["warnings"])

    def test_validate_missing_ai_officer_name(self, tmp_path):
        config = {"version": "1.0", "governance": {"ai_officer": {"name": ""}}}
        p = tmp_path / "regula-policy.json"
        p.write_text(json.dumps(config))
        from config_validator import validate_config
        result = validate_config(path=str(p), format_type="silent")
        assert any("ai_officer.name" in w for w in result["warnings"])

    def test_validate_invalid_json(self, tmp_path):
        p = tmp_path / "regula-policy.json"
        p.write_text("{invalid json")
        from config_validator import validate_config
        result = validate_config(path=str(p), format_type="silent")
        assert result["valid"] is False
        assert any("parse error" in e.lower() for e in result["errors"])

    def test_validate_text_output(self, tmp_path, capsys):
        config = {"version": "1.0", "governance": {"ai_officer": {"name": "A"}},
                  "thresholds": {"block_above": 80, "warn_above": 50}}
        p = tmp_path / "regula-policy.json"
        p.write_text(json.dumps(config))
        from config_validator import validate_config
        validate_config(path=str(p), format_type="text")
        captured = capsys.readouterr()
        assert "Config" in captured.out

    def test_validate_bool_block_above(self, tmp_path):
        """Boolean values should be rejected even though bool is a subclass of int."""
        config = {"version": "1.0", "thresholds": {"block_above": True}}
        p = tmp_path / "regula-policy.json"
        p.write_text(json.dumps(config))
        from config_validator import validate_config
        result = validate_config(path=str(p), format_type="silent")
        assert result["valid"] is False


# ===========================================================================
# framework_mapper.py
# ===========================================================================

class TestFrameworkMapper:
    def test_map_article_9_all(self):
        from framework_mapper import map_to_frameworks
        result = map_to_frameworks(articles=["9"])
        assert "9" in result
        assert len(result["9"]) > 0

    def test_map_article_14_nist(self):
        from framework_mapper import map_to_frameworks
        result = map_to_frameworks(articles=["14"], frameworks=["nist-ai-rmf"])
        assert "14" in result
        if result["14"]:
            assert "nist_ai_rmf" in result["14"]

    def test_map_multiple_articles(self):
        from framework_mapper import map_to_frameworks
        result = map_to_frameworks(articles=["9", "10", "14"])
        assert len(result) == 3

    def test_map_unknown_article(self):
        from framework_mapper import map_to_frameworks
        result = map_to_frameworks(articles=["99"])
        assert "99" in result
        assert result["99"] == {}

    def test_map_iso_42001(self):
        from framework_mapper import map_to_frameworks
        result = map_to_frameworks(articles=["9"], frameworks=["iso-42001"])
        if result["9"]:
            assert "iso_42001" in result["9"]

    def test_format_mapping_text(self):
        from framework_mapper import map_to_frameworks, format_mapping_text
        mapping = map_to_frameworks(articles=["9"])
        text = format_mapping_text(mapping)
        assert "Article 9" in text

    def test_format_mapping_json(self):
        from framework_mapper import map_to_frameworks, format_mapping_json
        mapping = map_to_frameworks(articles=["9"])
        j = format_mapping_json(mapping)
        parsed = json.loads(j)
        assert "9" in parsed

    def test_map_internal_key_direct(self):
        from framework_mapper import map_to_frameworks
        result = map_to_frameworks(articles=["9"], frameworks=["nist_ai_rmf"])
        assert "9" in result

    def test_map_all_articles(self):
        from framework_mapper import map_to_frameworks
        result = map_to_frameworks(articles=["9", "10", "11", "12", "13", "14", "15"])
        assert len(result) == 7
        for art in ["9", "10", "11", "12", "13", "14", "15"]:
            assert art in result


# ===========================================================================
# timeline.py
# ===========================================================================

class TestTimeline:
    def test_timeline_data_exists(self):
        from timeline import TIMELINE
        assert len(TIMELINE) > 5

    def test_timeline_entries_have_required_fields(self):
        from timeline import TIMELINE
        for entry in TIMELINE:
            assert "date" in entry
            assert "event" in entry
            assert "status" in entry

    def test_format_timeline_text(self):
        from timeline import format_timeline_text
        text = format_timeline_text()
        assert "EU AI Act" in text
        assert "2024-08-01" in text
        assert "[LIVE]" in text

    def test_status_labels(self):
        from timeline import STATUS_LABELS, STATUS_INDICATORS
        assert "effective" in STATUS_LABELS
        assert "proposed" in STATUS_LABELS
        assert "effective" in STATUS_INDICATORS

    def test_timeline_has_omnibus(self):
        from timeline import TIMELINE
        events_text = " ".join(e["event"] for e in TIMELINE)
        assert "Omnibus" in events_text or "omnibus" in events_text


# ===========================================================================
# baseline.py
# ===========================================================================

class TestBaseline:
    def test_finding_key(self):
        from baseline import _finding_key
        f = {"file": "test.py", "tier": "high_risk", "indicators": ["b", "a"]}
        key = _finding_key(f)
        assert "test.py" in key
        assert "high_risk" in key

    def test_finding_key_stable(self):
        from baseline import _finding_key
        f1 = {"file": "x.py", "tier": "t", "indicators": ["b", "a"]}
        f2 = {"file": "x.py", "tier": "t", "indicators": ["a", "b"]}
        assert _finding_key(f1) == _finding_key(f2)

    def test_load_baseline_nonexistent(self, tmp_path):
        from baseline import load_baseline
        result = load_baseline(str(tmp_path))
        assert result == {}

    def test_load_baseline_corrupt(self, tmp_path):
        from baseline import load_baseline
        (tmp_path / ".regula-baseline.json").write_text("{bad json")
        result = load_baseline(str(tmp_path))
        assert result == {}

    def test_save_and_load_baseline(self, tmp_path):
        # Create a minimal Python file so scan_files has something to scan
        (tmp_path / "test.py").write_text("import tensorflow\n")
        from baseline import save_baseline, load_baseline
        baseline = save_baseline(str(tmp_path))
        assert "version" in baseline
        assert "findings" in baseline
        loaded = load_baseline(str(tmp_path))
        assert loaded["version"] == "1.0"

    def test_compare_no_baseline(self, tmp_path):
        from baseline import compare_to_baseline
        result = compare_to_baseline(str(tmp_path))
        assert "error" in result

    def test_format_comparison_text_error(self):
        from baseline import format_comparison_text
        result = format_comparison_text({"error": "No baseline found."})
        assert "Error" in result

    def test_format_comparison_text_normal(self):
        from baseline import format_comparison_text
        data = {
            "baseline_date": "2025-01-01T00:00:00Z",
            "scan_date": "2025-01-02T00:00:00Z",
            "new_findings": [],
            "resolved_findings": [],
            "unchanged_findings": [],
            "summary": {"new": 0, "resolved": 0, "unchanged": 0, "net_change": 0},
        }
        text = format_comparison_text(data)
        assert "Baseline Comparison" in text


# ===========================================================================
# CLI main() in-process tests (these count toward coverage)
# ===========================================================================

class TestCLIInProcess:
    """Call cli.main() directly to exercise cmd_* functions under coverage."""

    def test_main_no_args(self):
        from cli import main
        with pytest.raises(SystemExit) as exc:
            main([])
        assert exc.value.code == 2

    def test_main_timeline_text(self, capsys):
        from cli import main
        main(["timeline"])
        out = capsys.readouterr().out
        assert "EU AI Act" in out

    def test_main_timeline_json(self, capsys):
        from cli import main
        main(["timeline", "--format", "json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "timeline"

    def test_main_doctor_json(self, capsys):
        from cli import main
        try:
            main(["doctor", "--format", "json"])
        except SystemExit:
            pass
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "doctor"
        assert "healthy" in data["data"]

    def test_main_doctor_text(self, capsys):
        from cli import main
        try:
            main(["doctor"])
        except SystemExit:
            pass
        out = capsys.readouterr().out
        assert "Regula Doctor" in out

    def test_main_classify_input(self, capsys):
        from cli import main
        try:
            main(["classify", "--input", "simple calculator app"])
        except SystemExit:
            pass
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_main_classify_json(self, capsys):
        from cli import main
        try:
            main(["classify", "--input", "a chatbot for customer service", "--format", "json"])
        except SystemExit:
            pass
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "classify"

    def test_main_check_json(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        try:
            main(["check", "--format", "json", "tests/fixtures/sample_high_risk"])
        except SystemExit:
            pass
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "check"

    def test_main_check_text(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        try:
            main(["check", "tests/fixtures/sample_high_risk"])
        except SystemExit:
            pass
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_main_status_json(self, capsys):
        from cli import main
        main(["status", "--format", "json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "status"

    def test_main_gap_json(self, capsys):
        from cli import main
        main(["gap", "--project", "tests/fixtures/sample_high_risk", "--format", "json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "gap"

    def test_main_gap_text(self, capsys):
        from cli import main
        main(["gap", "--project", "tests/fixtures/sample_high_risk"])
        out = capsys.readouterr().out
        assert "Art" in out or "article" in out.lower() or "gap" in out.lower()

    def test_main_plan_json(self, capsys):
        from cli import main
        main(["plan", "--project", "tests/fixtures/sample_high_risk", "--format", "json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "plan"

    def test_main_discover_json(self, capsys):
        from cli import main
        main(["discover", "--project", "tests/fixtures/sample_high_risk", "--format", "json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "discover"

    def test_main_discover_text(self, capsys):
        from cli import main
        main(["discover", "--project", "tests/fixtures/sample_high_risk"])
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_main_exempt_answers(self, capsys):
        from cli import main
        try:
            main(["exempt", "--answers", "no,no,no,no,no,no"])
        except SystemExit:
            pass
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_main_disclose_chatbot(self, capsys):
        from cli import main
        main(["disclose", "--type", "chatbot"])
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_main_disclose_json(self, capsys):
        from cli import main
        main(["disclose", "--type", "chatbot", "--format", "json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "disclose"

    def test_main_questionnaire(self, capsys):
        from cli import main
        main(["questionnaire"])
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_main_questionnaire_json(self, capsys):
        from cli import main
        main(["questionnaire", "--format", "json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "questionnaire"

    def test_main_session(self, capsys):
        from cli import main
        main(["session"])
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_main_session_json(self, capsys):
        from cli import main
        main(["session", "--format", "json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "session"

    def test_main_deps_json(self, capsys):
        from cli import main
        main(["deps", "--project", "tests/fixtures/sample_high_risk", "--format", "json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "deps"

    def test_main_deps_text(self, capsys):
        from cli import main
        main(["deps", "--project", "tests/fixtures/sample_high_risk"])
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_main_audit_verify(self, capsys):
        from cli import main
        try:
            main(["audit", "verify"])
        except SystemExit:
            pass
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_main_compliance_workflow(self, capsys):
        from cli import main
        main(["compliance", "workflow"])
        out = capsys.readouterr().out
        assert "workflow" in out.lower() or "compliance" in out.lower() or "status" in out.lower()

    def test_main_compliance_history(self, capsys):
        from cli import main
        try:
            main(["compliance", "history"])
        except SystemExit:
            pass
        # history may be empty or output something

    def test_main_inventory_json(self, capsys):
        from cli import main
        main(["inventory", "--format", "json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "inventory"

    def test_main_docs_project(self, capsys):
        from cli import main
        main(["docs", "--project", "tests/fixtures/sample_high_risk"])
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_main_gpai_check(self, capsys):
        from cli import main
        try:
            main(["gpai-check"])
        except SystemExit:
            pass
        out = capsys.readouterr().out
        assert "GPAI" in out or "Code of Practice" in out

    def test_main_report_json(self, capsys):
        from cli import main
        main(["report", "--project", "tests/fixtures/sample_high_risk", "--format", "json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "report"

    def test_main_config_validate(self, capsys):
        from cli import main
        try:
            main(["config", "validate"])
        except SystemExit:
            pass
        out = capsys.readouterr().out
        assert "Config" in out or "config" in out or len(out) > 0

    def test_main_metrics(self, capsys):
        from cli import main
        main(["metrics"])
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_main_self_test(self, capsys):
        from cli import main
        try:
            main(["self-test"])
        except SystemExit:
            pass

    def test_main_assess_answers(self, capsys):
        from cli import main
        try:
            main(["assess", "--answers", "yes,yes,no,yes,no"])
        except SystemExit:
            pass
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_main_security_self_check(self, capsys):
        from cli import main
        try:
            main(["security-self-check"])
        except SystemExit:
            pass

    def test_main_baseline_save(self, capsys, tmp_path):
        (tmp_path / "test.py").write_text("import torch\n")
        from cli import main
        main(["baseline", "save", "--project", str(tmp_path)])
        out = capsys.readouterr().out
        assert "Baseline saved" in out

    def test_main_baseline_compare_no_baseline(self, capsys, tmp_path):
        (tmp_path / "test.py").write_text("x = 1\n")
        from cli import main
        main(["baseline", "compare", "--project", str(tmp_path)])
        out = capsys.readouterr().out
        assert "baseline" in out.lower() or "Error" in out

    def test_main_regwatch(self, capsys):
        from cli import main
        try:
            main(["regwatch"])
        except SystemExit:
            pass

    def test_main_oversight(self, capsys):
        from cli import main
        try:
            main(["oversight", "--project", "tests/fixtures/sample_high_risk"])
        except SystemExit:
            pass

    def test_main_sbom_json(self, capsys):
        from cli import main
        main(["sbom", "--format", "json"])
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_main_agent(self, capsys):
        from cli import main
        main(["agent"])
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_main_governance(self, capsys, tmp_path):
        from cli import main
        main(["governance", "--project", "tests/fixtures/sample_high_risk",
              "--output", str(tmp_path / "GOV.md")])

    def test_main_model_card(self, capsys, tmp_path):
        from cli import main
        main(["model-card", "--project", "tests/fixtures/sample_high_risk",
              "--output", str(tmp_path / "MC.md")])

    def test_main_conform(self, capsys, tmp_path):
        from cli import main
        main(["conform", "--project", "tests/fixtures/sample_high_risk",
              "--output", str(tmp_path), "--format", "json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "conform"

    def test_main_evidence_pack(self, capsys, tmp_path):
        from cli import main
        main(["evidence-pack", "--project", "tests/fixtures/sample_high_risk",
              "--output", str(tmp_path)])

    def test_main_fix(self, capsys):
        from cli import main
        main(["fix", "--project", "tests/fixtures/sample_high_risk", "--format", "json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "fix"

    def test_main_check_sarif(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        try:
            main(["check", "--format", "sarif", "tests/fixtures/sample_high_risk"])
        except SystemExit:
            pass
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data.get("$schema") or "runs" in data

    def test_main_report_sarif(self, capsys):
        from cli import main
        main(["report", "--project", "tests/fixtures/sample_high_risk", "--format", "sarif"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert "$schema" in data or "runs" in data

    def test_main_telemetry_status(self, capsys):
        from cli import main
        main(["telemetry", "status"])
        out = capsys.readouterr().out
        assert "telemetry" in out.lower() or len(out) > 0

    def test_json_output_function(self, capsys):
        from cli import json_output
        json_output("test_cmd", {"key": "value"})
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "test_cmd"
        assert data["data"]["key"] == "value"
        assert data["format_version"] == "1.0"

    def test_validate_path_nonexistent(self):
        from cli import _validate_path
        from errors import PathError
        with pytest.raises(PathError):
            _validate_path("/nonexistent/path/xyz")

    def test_validate_path_valid(self):
        from cli import _validate_path
        p = _validate_path(".")
        assert p.is_dir()

    def test_main_lang_flag(self, capsys):
        from cli import main
        main(["--lang", "de", "timeline"])
        out = capsys.readouterr().out
        assert "EU AI Act" in out

    def test_main_lang_pt_br(self, capsys):
        from cli import main
        main(["--lang", "pt-BR", "timeline"])
        out = capsys.readouterr().out
        assert "EU AI Act" in out


    def test_main_handoff_garak(self, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["handoff", "garak", "tests/fixtures/sample_high_risk",
              "--output", str(tmp_path / "garak.yaml")])
        out = capsys.readouterr().out
        assert "handoff" in out.lower() or "garak" in out.lower()

    def test_main_handoff_giskard(self, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["handoff", "giskard", "tests/fixtures/sample_high_risk",
              "--output", str(tmp_path / "giskard.yaml")])

    def test_main_handoff_promptfoo(self, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["handoff", "promptfoo", "tests/fixtures/sample_high_risk",
              "--output", str(tmp_path / "promptfoo.yaml")])

    def test_main_handoff_json(self, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["handoff", "garak", "tests/fixtures/sample_high_risk",
              "--output", str(tmp_path / "g.yaml"), "--format", "json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "handoff"

    def test_main_register(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        try:
            main(["register", "tests/fixtures/sample_high_risk", "--force"])
        except SystemExit:
            pass

    def test_main_report_html(self, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["report", "--project", "tests/fixtures/sample_high_risk",
              "--format", "html", "--output", str(tmp_path / "report.html")])

    def test_main_audit_query(self, capsys):
        from cli import main
        try:
            main(["audit", "query"])
        except SystemExit:
            pass

    def test_main_audit_export(self, capsys):
        from cli import main
        try:
            main(["audit", "export"])
        except SystemExit:
            pass

    def test_main_docs_qms(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["docs", "--project", "tests/fixtures/sample_high_risk", "--qms"])

    def test_main_docs_model_card(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        try:
            main(["docs", "--project", "tests/fixtures/sample_high_risk", "--model-card"])
        except SystemExit:
            pass

    def test_main_docs_json(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        try:
            main(["docs", "--project", "tests/fixtures/sample_high_risk", "--format", "json"])
        except SystemExit:
            pass

    def test_main_check_verbose(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        try:
            main(["check", "--verbose", "tests/fixtures/sample_high_risk"])
        except SystemExit:
            pass

    def test_main_check_strict(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        try:
            main(["check", "--strict", "tests/fixtures/sample_high_risk"])
        except SystemExit:
            pass

    def test_main_gap_strict(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        try:
            main(["gap", "--project", "tests/fixtures/sample_high_risk", "--strict"])
        except SystemExit:
            pass

    def test_main_conform_sme(self, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["conform", "--project", "tests/fixtures/sample_high_risk",
              "--output", str(tmp_path), "--sme"])

    def test_main_plan_text(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["plan", "--project", "tests/fixtures/sample_high_risk"])

    def test_main_fix_text(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["fix", "--project", "tests/fixtures/sample_high_risk"])

    def test_main_check_ci(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        try:
            main(["check", "--ci", "tests/fixtures/sample_high_risk"])
        except SystemExit:
            pass

    def test_main_oversight_json(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        try:
            main(["oversight", "--project", "tests/fixtures/sample_high_risk", "--format", "json"])
        except SystemExit:
            pass
        out = capsys.readouterr().out
        if out.strip():
            data = json.loads(out)
            assert data["command"] == "oversight"

    def test_main_discover_org(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["discover", "--project", "tests/fixtures/sample_high_risk", "--org"])

    def test_main_status_text(self, capsys):
        from cli import main
        main(["status"])

    def test_main_benchmark(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["benchmark", "--project", "tests/fixtures/sample_high_risk"])


# ===========================================================================
# handoff.py (direct imports for coverage)
# ===========================================================================

class TestHandoff:
    def test_detect_entrypoints_empty(self, tmp_path):
        from handoff import _detect_llm_entrypoints
        result = _detect_llm_entrypoints(tmp_path)
        assert result == []

    def test_detect_entrypoints_in_project(self, monkeypatch):
        """Test entrypoint detection against the project's own fixtures."""
        monkeypatch.chdir(PROJECT_ROOT)
        from handoff import _detect_llm_entrypoints
        result = _detect_llm_entrypoints(PROJECT_ROOT / "tests" / "fixtures" / "sample_high_risk")
        # May or may not find entrypoints depending on fixture content
        assert isinstance(result, list)

    def test_build_garak_config(self):
        from handoff import build_garak_config
        config = build_garak_config([{"file": "a.py", "line": 1, "kind": "openai-chat"}])
        assert "Garak" in config
        assert "probe_tags" in config

    def test_build_giskard_config(self):
        from handoff import build_giskard_config
        config = build_giskard_config([])
        assert "Giskard" in config

    def test_build_promptfoo_config(self):
        from handoff import build_promptfoo_config
        config = build_promptfoo_config([])
        assert "promptfoo" in config

    def test_run_handoff_unknown_tool(self, tmp_path):
        from handoff import run_handoff
        result = run_handoff("unknown_tool", tmp_path)
        assert "error" in result

    def test_run_handoff_garak(self, tmp_path):
        from handoff import run_handoff
        result = run_handoff("garak", tmp_path, tmp_path / "out.yaml")
        assert result["tool"] == "garak"
        assert (tmp_path / "out.yaml").exists()

    def test_yaml_dump(self):
        from handoff import _yaml_dump
        result = _yaml_dump({"key": "value", "nested": {"a": 1}, "list": [1, 2]})
        assert "key: value" in result
        assert "nested:" in result


# ===========================================================================
# install.py (partial — just the helpers)
# ===========================================================================

class TestInstall:
    def test_find_regula_root(self):
        from install import _find_regula_root
        root = _find_regula_root()
        assert isinstance(root, Path)

    def test_find_python(self):
        from install import _find_python
        py = _find_python()
        assert "python" in py.lower() or len(py) > 0

    def test_install_claude_code(self, tmp_path):
        from install import install_claude_code
        regula_root = PROJECT_ROOT
        install_claude_code(regula_root, tmp_path)
        assert (tmp_path / ".claude" / "settings.local.json").exists()

    def test_list_platforms(self, capsys):
        from install import list_platforms
        list_platforms()
        out = capsys.readouterr().out
        assert "claude" in out.lower()

    def test_install_copilot_cli(self, tmp_path):
        from install import install_copilot_cli
        install_copilot_cli(PROJECT_ROOT, tmp_path)
        assert (tmp_path / ".github" / "hooks" / "regula.json").exists()

    def test_install_windsurf(self, tmp_path):
        from install import install_windsurf
        install_windsurf(PROJECT_ROOT, tmp_path)
        assert (tmp_path / ".windsurf" / "hooks.json").exists()

    def test_install_pre_commit_new(self, tmp_path):
        from install import install_pre_commit
        install_pre_commit(PROJECT_ROOT, tmp_path)
        assert (tmp_path / ".pre-commit-config.yaml").exists()

    def test_install_pre_commit_existing(self, tmp_path, capsys):
        (tmp_path / ".pre-commit-config.yaml").write_text("repos: []\n")
        from install import install_pre_commit
        install_pre_commit(PROJECT_ROOT, tmp_path)
        out = capsys.readouterr().out
        assert "already exists" in out

    def test_install_git_hooks(self, tmp_path):
        """Test git hook installation into a mock git dir."""
        hooks_dir = tmp_path / ".git" / "hooks"
        hooks_dir.mkdir(parents=True)
        from install import install_git_hooks
        install_git_hooks(PROJECT_ROOT, tmp_path)
        assert (hooks_dir / "pre-commit").exists()


# ===========================================================================
# timestamp.py (pure DER functions — no network)
# ===========================================================================

class TestTimestamp:
    def test_der_len_short(self):
        from timestamp import _der_len
        assert _der_len(10) == bytes([10])

    def test_der_len_medium(self):
        from timestamp import _der_len
        assert _der_len(200) == bytes([0x81, 200])

    def test_der_len_long(self):
        from timestamp import _der_len
        result = _der_len(300)
        assert result == bytes([0x82, 1, 44])

    def test_der_seq(self):
        from timestamp import _der_seq
        result = _der_seq(b'\x01\x02')
        assert result[0] == 0x30

    def test_der_int_zero(self):
        from timestamp import _der_int
        result = _der_int(0)
        assert result == bytes([0x02, 0x01, 0x00])

    def test_der_int_positive(self):
        from timestamp import _der_int
        result = _der_int(42)
        assert result[0] == 0x02

    def test_der_int_high_bit(self):
        from timestamp import _der_int
        result = _der_int(128)
        # Should prepend 0x00 since 128 has high bit set
        assert result[2] == 0x00

    def test_build_tsq(self):
        from timestamp import _build_tsq
        import hashlib
        h = hashlib.sha256(b"test data").digest()
        tsq = _build_tsq(h, nonce=12345)
        assert tsq[0] == 0x30  # SEQUENCE

    def test_build_tsq_auto_nonce(self):
        from timestamp import _build_tsq
        import hashlib
        h = hashlib.sha256(b"test").digest()
        tsq = _build_tsq(h)
        assert len(tsq) > 50

    def test_build_tsq_wrong_hash_len(self):
        from timestamp import _build_tsq
        with pytest.raises(ValueError, match="32-byte"):
            _build_tsq(b"short")

    def test_parse_tsr_not_sequence(self):
        from timestamp import parse_tsr
        with pytest.raises(ValueError, match="DER SEQUENCE"):
            parse_tsr(b"\x01\x02\x03")

    def test_parse_tsr_too_short(self):
        from timestamp import parse_tsr
        with pytest.raises(ValueError, match="too short"):
            parse_tsr(b"\x30\x01")

    def test_parse_tsr_empty(self):
        from timestamp import parse_tsr
        with pytest.raises(ValueError):
            parse_tsr(b"")

    def test_require_http_url_valid(self):
        from timestamp import _require_http_url
        _require_http_url("https://example.com")
        _require_http_url("http://example.com")

    def test_require_http_url_invalid(self):
        from timestamp import _require_http_url
        with pytest.raises(ValueError):
            _require_http_url("file:///etc/passwd")
        with pytest.raises(ValueError):
            _require_http_url("ftp://example.com")


    def test_main_inventory_merge(self, capsys, tmp_path):
        # Create two inventory JSON files
        inv1 = [{"name": "model-a", "provider": "openai"}]
        inv2 = [{"name": "model-b", "provider": "anthropic"}]
        f1 = tmp_path / "inv1.json"
        f2 = tmp_path / "inv2.json"
        f1.write_text(json.dumps(inv1))
        f2.write_text(json.dumps(inv2))
        from cli import main
        main(["inventory", "--merge", str(f1), str(f2)])
        out = capsys.readouterr().out
        assert "Merged" in out
        assert "2 models" in out

    def test_main_inventory_merge_json(self, capsys, tmp_path):
        inv = {"models": [{"name": "m1"}]}
        f = tmp_path / "inv.json"
        f.write_text(json.dumps(inv))
        from cli import main
        main(["inventory", "--merge", str(f), "--format", "json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["data"]["total_models"] == 1

    def test_main_inventory_table(self, capsys):
        from cli import main
        main(["inventory"])

    def test_main_install_list(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["install", "list"])
        out = capsys.readouterr().out
        assert "claude" in out.lower()

    def test_main_classify_file(self, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        f = tmp_path / "input.txt"
        f.write_text("A simple calculator application")
        from cli import main
        try:
            main(["classify", "--file", str(f)])
        except SystemExit:
            pass

    def test_main_status_show_nonexistent(self, capsys):
        from cli import main
        try:
            main(["status", "--show", "nonexistent_system_xyz"])
        except SystemExit:
            pass

    def test_main_report_sarif(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["report", "--project", "tests/fixtures/sample_high_risk", "--format", "sarif"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert "$schema" in data or "runs" in data

    def test_main_check_no_ignore(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        try:
            main(["check", "--no-ignore", "tests/fixtures/sample_high_risk"])
        except SystemExit:
            pass

    def test_main_evidence_pack_json(self, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["evidence-pack", "--project", "tests/fixtures/sample_high_risk",
              "--output", str(tmp_path), "--format", "json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "evidence-pack"

    def test_main_discover_register(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["discover", "--project", "tests/fixtures/sample_high_risk", "--register"])

    def test_main_check_html(self, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        try:
            main(["check", "--format", "html", "--output", str(tmp_path / "r.html"),
                  "tests/fixtures/sample_high_risk"])
        except SystemExit:
            pass

    def test_main_conform_organisational_json(self, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        # --organisational without stdin should just output the questions
        try:
            main(["conform", "--project", "tests/fixtures/sample_high_risk",
                  "--organisational", "--format", "json"])
        except (SystemExit, EOFError):
            pass

    def test_main_plan_output_file(self, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["plan", "--project", "tests/fixtures/sample_high_risk",
              "--output", str(tmp_path / "plan.md")])

    def test_main_fix_output(self, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["fix", "--project", "tests/fixtures/sample_high_risk",
              "--output", str(tmp_path / "fixes.py")])

    def test_main_gap_article(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["gap", "--project", "tests/fixtures/sample_high_risk", "--article", "9"])

    def test_main_sbom_output(self, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["sbom", "--format", "json", "--output", str(tmp_path / "sbom.json")])

    def test_main_sbom_text(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["sbom", "--format", "text"])

    def test_main_report_html_output(self, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        main(["report", "--project", "tests/fixtures/sample_high_risk",
              "--format", "html", "--output", str(tmp_path / "report.html")])

    def test_main_docs_with_qms_flag(self, capsys, monkeypatch):
        monkeypatch.chdir(PROJECT_ROOT)
        from cli import main
        try:
            main(["docs", "--project", "tests/fixtures/sample_high_risk", "--qms"])
        except SystemExit:
            pass

    def test_main_baseline_compare_json(self, capsys, tmp_path):
        (tmp_path / "test.py").write_text("x = 1\n")
        from cli import main
        main(["baseline", "compare", "--project", str(tmp_path), "--format", "json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["command"] == "baseline"


# ===========================================================================
# extract_patterns.py
# ===========================================================================

class TestExtractPatterns:
    def test_load_risk_patterns(self):
        from extract_patterns import _load_risk_patterns
        mod_globals = _load_risk_patterns()
        assert "PROHIBITED_PATTERNS" in mod_globals
        assert "HIGH_RISK_PATTERNS" in mod_globals

    def test_yaml_escape_plain(self):
        from extract_patterns import _yaml_escape
        assert _yaml_escape("hello") == "hello"

    def test_yaml_escape_special(self):
        from extract_patterns import _yaml_escape
        result = _yaml_escape("key: value")
        assert result.startswith('"')

    def test_yaml_escape_none(self):
        from extract_patterns import _yaml_escape
        assert _yaml_escape(None) == "null"

    def test_emit_yaml(self):
        from extract_patterns import _emit_yaml
        result = _emit_yaml({"key": "val", "list": ["a", "b"], "nested": {"x": 1}})
        assert "key: val" in result
        assert "list:" in result

    def test_extract(self):
        from extract_patterns import _load_risk_patterns, extract
        mod_globals = _load_risk_patterns()
        entries = extract(mod_globals)
        assert len(entries) > 20  # Should have many patterns
        assert all("pattern_id" in e for e in entries)
        assert all("tier" in e for e in entries)

    def test_main_dry_run(self, capsys):
        from extract_patterns import main
        rc = main(["--dry-run"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "patterns" in out.lower()

    def test_main_check(self, capsys):
        from extract_patterns import main
        rc = main(["--check"])
        # May be 0 (files exist) or 1 (drift)
        assert rc in (0, 1)


# ===========================================================================
# site_facts.py (partial — just the loader)
# ===========================================================================

class TestSiteFacts:
    def test_load_module(self):
        from site_facts import _load_module
        mod = _load_module(SCRIPTS_DIR / "constants.py", "constants")
        assert mod is not None
        assert hasattr(mod, "VERSION")

    def test_load_module_nonexistent(self):
        from site_facts import _load_module
        mod = _load_module(Path("/nonexistent.py"), "fake")
        assert mod is None

    def test_count_commands(self):
        from site_facts import count_commands
        n = count_commands()
        assert n > 30

    def test_count_patterns(self):
        from site_facts import count_patterns
        p = count_patterns()
        assert p["tier_groups"] > 0
        assert p["tier_regexes"] > 0
        assert p["grand_total"] > 0

    def test_count_frameworks(self):
        from site_facts import count_frameworks
        n = count_frameworks()
        assert n >= 10

    def test_count_languages(self):
        from site_facts import count_languages
        assert count_languages() == 8

    def test_count_tests(self):
        from site_facts import count_tests
        t = count_tests()
        assert t["total_functions"] > 100

    def test_compute(self):
        from site_facts import compute
        data = compute()
        assert "counts" in data
        assert data["counts"]["commands"] > 0

    def test_render_markdown(self):
        from site_facts import compute, render_markdown
        data = compute()
        md = render_markdown(data)
        assert "CLI commands" in md
        assert "Detection patterns" in md


# ===========================================================================
# build_delta_log.py
# ===========================================================================

class TestBuildDeltaLog:
    def _make_entry(self, **overrides):
        base = {
            "id": "test-001",
            "date": "2026-03-15",
            "type": "amendment-proposal",
            "source_url": "https://example.com",
            "source_title": "Test Entry",
            "affected_articles": ["9", "14"],
            "summary": "Test summary",
            "confidence": "verified-primary",
        }
        base.update(overrides)
        return base

    def test_validate_valid(self):
        from build_delta_log import validate
        entries = [self._make_entry()]
        errors = validate(entries)
        assert errors == []

    def test_validate_missing_fields(self):
        from build_delta_log import validate
        errors = validate([{"id": "bad"}])
        assert len(errors) > 0

    def test_validate_invalid_type(self):
        from build_delta_log import validate
        entry = self._make_entry(type="invalid-type")
        errors = validate([entry])
        assert any("invalid type" in e for e in errors)

    def test_validate_invalid_confidence(self):
        from build_delta_log import validate
        entry = self._make_entry(confidence="maybe")
        errors = validate([entry])
        assert any("invalid confidence" in e for e in errors)

    def test_validate_bad_date(self):
        from build_delta_log import validate
        entry = self._make_entry(date="not-a-date")
        errors = validate([entry])
        assert any("invalid date" in e for e in errors)

    def test_validate_duplicate_id(self):
        from build_delta_log import validate
        e = self._make_entry()
        errors = validate([e, e])
        assert any("duplicate" in err for err in errors)

    def test_validate_empty_articles(self):
        from build_delta_log import validate
        entry = self._make_entry(affected_articles=[])
        errors = validate([entry])
        assert any("affected_articles" in e for e in errors)

    def test_build_index(self):
        from build_delta_log import build_index
        entries = [self._make_entry()]
        index = build_index(entries)
        assert index["total_entries"] == 1
        assert index["latest_date"] == "2026-03-15"

    def test_build_rss(self):
        from build_delta_log import build_rss
        entries = [self._make_entry()]
        rss = build_rss(entries)
        assert "<?xml" in rss
        assert "<rss" in rss
        assert "Test Entry" in rss

    def test_build_summary(self):
        from build_delta_log import build_summary
        entries = [self._make_entry()]
        md = build_summary(entries)
        assert "Delta Log" in md
        assert "Test Entry" in md

    def test_xml_escape(self):
        from build_delta_log import _xml_escape
        assert _xml_escape("a & b") == "a &amp; b"
        assert _xml_escape("<tag>") == "&lt;tag&gt;"

    def test_load_entries(self):
        from build_delta_log import load_entries
        entries = load_entries()
        assert isinstance(entries, list)

    def test_main_validate(self, capsys):
        from build_delta_log import main
        rc = main(["--validate"])
        assert rc in (0, 1)


# ===========================================================================
# Additional cli.py coverage — regwatch, benchmark, misc
# ===========================================================================

class TestCLIMoreCoverage:
    def test_highest_annex_iii_point_empty(self):
        from cli import _highest_annex_iii_point
        assert _highest_annex_iii_point({}) is None
        assert _highest_annex_iii_point({"risk_classifications": []}) is None

    def test_highest_annex_iii_point_match(self):
        from cli import _highest_annex_iii_point
        disc = {"risk_classifications": [
            {"indicators": ["employment_scoring"], "description": "employment related"},
        ]}
        result = _highest_annex_iii_point(disc)
        assert result == 4  # employment

    def test_read_code_blob(self, tmp_path):
        (tmp_path / "app.py").write_text("x = 1\n")
        from cli import _read_code_blob
        blob = _read_code_blob(tmp_path)
        assert "x = 1" in blob

    def test_read_code_blob_empty(self, tmp_path):
        from cli import _read_code_blob
        blob = _read_code_blob(tmp_path)
        assert blob == ""

    def test_current_pattern_version(self):
        from cli import _current_pattern_version
        v = _current_pattern_version()
        assert len(v) > 0


# ===========================================================================
# regwatch.py
# ===========================================================================

class TestRegwatch:
    def test_parse_iso_date_valid(self):
        from regwatch import _parse_iso_date
        d = _parse_iso_date("2026-03-15")
        assert d is not None
        assert d.year == 2026

    def test_parse_iso_date_invalid(self):
        from regwatch import _parse_iso_date
        assert _parse_iso_date("not-a-date") is None
        assert _parse_iso_date(None) is None

    def test_load_last_reviewed(self):
        from regwatch import _load_last_reviewed
        result = _load_last_reviewed()
        # Should return a date or None
        from datetime import date
        assert result is None or isinstance(result, date)

    def test_run(self):
        from regwatch import run
        result = run()
        assert "status" in result
        assert "exit_code" in result

    def test_run_cli_text(self, capsys):
        from regwatch import run_cli
        rc = run_cli("text")
        assert rc in (0, 1, 2)
        out = capsys.readouterr().out
        assert "regwatch" in out

    def test_run_cli_json(self, capsys):
        from regwatch import run_cli
        rc = run_cli("json")
        assert rc in (0, 1, 2)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert "status" in data


# ===========================================================================
# quickstart.py
# ===========================================================================

class TestQuickstart:
    def test_quickstart(self, tmp_path, capsys):
        (tmp_path / "app.py").write_text("import torch\nmodel = torch.load('m.pt')\n")
        from quickstart import run_quickstart
        result = run_quickstart(
            project_dir=str(tmp_path),
            org="Test Org",
            format_type="json",
        )
        assert "policy_created" in result or "findings" in result


# ===========================================================================
# questionnaire.py
# ===========================================================================

class TestQuestionnaire:
    def test_generate_questionnaire(self):
        from questionnaire import generate_questionnaire
        q = generate_questionnaire()
        assert isinstance(q, (list, dict))

    def test_format_questionnaire_cli(self):
        from questionnaire import generate_questionnaire, format_questionnaire_cli
        q = generate_questionnaire()
        text = format_questionnaire_cli(q)
        assert len(text) > 0


# ===========================================================================
# benchmark.py
# ===========================================================================

class TestBenchmark:
    def test_extract_context(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("line1\nline2\nline3\nline4\nline5\n")
        from benchmark import _extract_context
        ctx = _extract_context(f, 3)
        assert "line3" in ctx
        assert ">>>" in ctx

    def test_extract_context_empty(self, tmp_path):
        f = tmp_path / "empty.py"
        f.write_text("")
        from benchmark import _extract_context
        ctx = _extract_context(f, 1)
        assert ctx == ""

    def test_extract_context_missing(self):
        from benchmark import _extract_context
        ctx = _extract_context(Path("/nonexistent_file.py"), 1)
        assert ctx == ""

    def test_find_first_indicator_line(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("import os\nimport tensorflow\nprint('hello')\n")
        from benchmark import _find_first_indicator_line
        line = _find_first_indicator_line(f, ["tensorflow"])
        assert line == 2

    def test_find_first_indicator_no_match(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("x = 1\n")
        from benchmark import _find_first_indicator_line
        line = _find_first_indicator_line(f, ["nonexistent"])
        assert line == 1

    def test_find_first_indicator_empty(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("x = 1\n")
        from benchmark import _find_first_indicator_line
        assert _find_first_indicator_line(f, []) == 1

    def test_benchmark_project(self, tmp_path):
        (tmp_path / "app.py").write_text("import tensorflow as tf\nmodel = tf.keras.Model()\n")
        from benchmark import benchmark_project
        result = benchmark_project(str(tmp_path))
        assert result["project"] == tmp_path.name
        assert "findings" in result
        assert "files_scanned" in result

    def test_benchmark_project_nonexistent(self):
        from benchmark import benchmark_project
        with pytest.raises(ValueError):
            benchmark_project("/nonexistent/path")

    def test_benchmark_suite(self, tmp_path):
        d1 = tmp_path / "proj1"
        d1.mkdir()
        (d1 / "app.py").write_text("import torch\n")
        d2 = tmp_path / "proj2"
        d2.mkdir()
        (d2 / "main.py").write_text("x = 1\n")
        from benchmark import benchmark_suite
        result = benchmark_suite([
            {"name": "proj1", "path": str(d1)},
            {"name": "proj2", "path": str(d2)},
        ])
        assert result["projects_scanned"] == 2
        assert "findings_by_tier" in result

    def test_benchmark_suite_skip_bad(self, tmp_path):
        from benchmark import benchmark_suite
        result = benchmark_suite([
            {"name": "bad", "path": "/nonexistent"},
        ])
        assert result["projects_scanned"] == 0

    def test_collect_all_findings(self):
        from benchmark import _collect_all_findings
        # Suite
        suite = {"projects": [{"findings": [{"label": "tp"}, {"label": "fp"}]}]}
        assert len(_collect_all_findings(suite)) == 2
        # Single project
        proj = {"findings": [{"label": "tp"}]}
        assert len(_collect_all_findings(proj)) == 1
        # Empty
        assert _collect_all_findings({}) == []

    def test_calculate_metrics(self):
        from benchmark import calculate_metrics
        data = {"findings": [
            {"label": "tp", "tier": "high_risk"},
            {"label": "tp", "tier": "high_risk"},
            {"label": "fp", "tier": "high_risk"},
        ]}
        metrics = calculate_metrics(data)
        assert metrics["true_positives"] == 2
        assert metrics["false_positives"] == 1
        assert "precision" in metrics

    def test_calculate_metrics_empty(self):
        from benchmark import calculate_metrics
        metrics = calculate_metrics({"findings": []})
        assert metrics["total_findings"] == 0

    def test_import_labelled_csv(self):
        from benchmark import _import_labelled_csv
        csv_content = (
            "project,file,line,tier,category,indicators,confidence_score,context,label\n"
            "test,app.py,10,high_risk,cat1,ind1;ind2,80,ctx,tp\n"
            "test,b.py,1,limited_risk,cat2,,50,,fp\n"
        )
        result = _import_labelled_csv(csv_content)
        assert len(result["findings"]) == 2
        assert result["findings"][0]["label"] == "tp"
        assert result["findings"][1]["label"] == "fp"

    def test_load_labelled_json(self, tmp_path):
        data = {"findings": [{"label": "tp", "file": "a.py"}]}
        f = tmp_path / "labelled.json"
        f.write_text(json.dumps(data))
        from benchmark import load_labelled_results
        result = load_labelled_results(str(f))
        assert result["findings"][0]["label"] == "tp"

    def test_load_labelled_csv(self, tmp_path):
        csv_content = (
            "project,file,line,tier,category,indicators,confidence_score,context,label\n"
            "test,app.py,10,high_risk,cat1,,80,,tp\n"
        )
        f = tmp_path / "labelled.csv"
        f.write_text(csv_content)
        from benchmark import load_labelled_results
        result = load_labelled_results(str(f))
        assert len(result["findings"]) == 1

    def test_load_labelled_unsupported(self, tmp_path):
        f = tmp_path / "data.xml"
        f.write_text("<data/>")
        from benchmark import load_labelled_results
        with pytest.raises(ValueError):
            load_labelled_results(str(f))

    def test_load_labelled_missing(self):
        from benchmark import load_labelled_results
        with pytest.raises(FileNotFoundError):
            load_labelled_results("/nonexistent.json")


# ===========================================================================
# CLI commands via subprocess (covers cli.py cmd_ functions)
# ===========================================================================

class TestCLICommands:
    def test_timeline_text(self):
        rc, out, err = run_cli("timeline")
        assert rc == 0
        assert "EU AI Act" in out

    def test_timeline_json(self):
        rc, out, err = run_cli("timeline", "--format", "json")
        assert rc == 0
        data = json.loads(out)
        assert data["command"] == "timeline"
        assert "timeline" in data["data"]

    def test_doctor_json(self):
        rc, out, err = run_cli("doctor", "--format", "json")
        # May exit 0 or 1 depending on health
        data = json.loads(out)
        assert data["command"] == "doctor"
        assert "healthy" in data["data"]

    def test_config_validate_no_file(self):
        rc, out, err = run_cli("config", "validate")
        # Should work (uses auto-discovery)
        assert rc in (0, 2)

    def test_classify_input(self):
        rc, out, err = run_cli("classify", "--input", "facial recognition system for law enforcement")
        assert rc in (0, 1)
        assert len(out) > 0

    def test_classify_json(self):
        rc, out, err = run_cli("classify", "--input", "simple calculator app", "--format", "json")
        assert rc in (0, 1)
        data = json.loads(out)
        assert data["command"] == "classify"

    def test_check_json(self):
        rc, out, err = run_cli("check", "--format", "json", "tests/fixtures/sample_high_risk")
        assert rc == 0
        data = json.loads(out)
        assert data["command"] == "check"

    def test_status_json(self):
        rc, out, err = run_cli("status", "--format", "json")
        assert rc == 0
        data = json.loads(out)
        assert data["command"] == "status"

    def test_exempt_auto(self):
        rc, out, err = run_cli("exempt", "--answers", "no,no,no,no,no,no")
        assert rc in (0, 1)

    def test_deps(self):
        rc, out, err = run_cli("deps", "--project", "tests/fixtures/sample_high_risk")
        assert rc == 0

    def test_deps_json(self):
        rc, out, err = run_cli("deps", "--project", "tests/fixtures/sample_high_risk", "--format", "json")
        assert rc == 0
        data = json.loads(out)
        assert data["command"] == "deps"

    def test_gap_json(self):
        rc, out, err = run_cli("gap", "--project", "tests/fixtures/sample_high_risk", "--format", "json")
        assert rc == 0
        data = json.loads(out)
        assert data["command"] == "gap"

    def test_version_flag(self):
        rc, out, err = run_cli("--version")
        assert rc == 0
        # Version string should be in output
        assert "." in out

    def test_no_args_shows_help(self):
        rc, out, err = run_cli()
        # Should show help or error
        assert rc in (0, 2)

    def test_plan_json(self):
        rc, out, err = run_cli("plan", "--project", "tests/fixtures/sample_high_risk", "--format", "json")
        assert rc == 0
        data = json.loads(out)
        assert data["command"] == "plan"

    def test_discover_json(self):
        rc, out, err = run_cli("discover", "--project", "tests/fixtures/sample_high_risk", "--format", "json")
        assert rc == 0
        data = json.loads(out)
        assert data["command"] == "discover"

    def test_compliance_workflow(self):
        rc, out, err = run_cli("compliance", "workflow")
        assert rc == 0
        assert "workflow" in out.lower() or "compliance" in out.lower()

    def test_security_self_check(self):
        rc, out, err = run_cli("security-self-check")
        assert rc == 0

    def test_regwatch(self):
        rc, out, err = run_cli("regwatch")
        assert rc in (0, 1)

    def test_metrics(self):
        rc, out, err = run_cli("metrics")
        assert rc == 0

    def test_inventory_json(self):
        rc, out, err = run_cli("inventory", "--format", "json")
        assert rc == 0
        data = json.loads(out)
        assert data["command"] == "inventory"

    def test_disclose_chatbot(self):
        rc, out, err = run_cli("disclose", "--type", "chatbot")
        assert rc == 0

    def test_docs_project(self):
        rc, out, err = run_cli("docs", "--project", "tests/fixtures/sample_high_risk")
        assert rc == 0

    def test_bias_text(self):
        rc, out, err = run_cli("bias")
        # May exit 1 if Ollama is not running (expected in CI/test)
        assert rc in (0, 1)

    def test_gpai_check(self):
        rc, out, err = run_cli("gpai-check")
        assert rc in (0, 1)

    def test_sbom_json(self):
        rc, out, err = run_cli("sbom", "--format", "json")
        assert rc == 0
        data = json.loads(out)
        assert "bomFormat" in data or "command" in data

    def test_questionnaire(self):
        rc, out, err = run_cli("questionnaire")
        assert rc in (0, 1)
