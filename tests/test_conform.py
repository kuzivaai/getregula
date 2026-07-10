# regula-ignore
"""Comprehensive tests for the conformity assessment evidence pack generator.

Covers:
1. ARTICLES registry structure and completeness
2. Helper functions: _sha256, _write_and_record, _make_coverage,
   _derive_deadline_summary
3. Declaration of conformity template generation
4. README generation
5. Full generate_conformity_pack with mocked dependencies
6. SME simplified pack generation with mocked dependencies
7. Edge cases: empty findings, missing gap data, timestamp-without-sign,
   optional module import failures (SBOM, audit, dependency scan, bias,
   oversight), signing integration
8. File integrity (SHA-256 records match written content)
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from conform import (
    ARTICLES,
    _derive_deadline_summary,
    _generate_declaration_template,
    _generate_readme,
    _make_coverage,
    _sha256,
    _write_and_record,
    generate_conformity_pack,
    generate_sme_simplified_pack,
)
from constants import VERSION


# ---------------------------------------------------------------------------
# 1. ARTICLES registry
# ---------------------------------------------------------------------------


class TestArticlesRegistry:
    """Verify the ARTICLES dict is well-formed and covers Articles 9-15."""

    def test_articles_covers_9_through_15(self):
        expected = {"9", "10", "11", "12", "13", "14", "15"}
        assert set(ARTICLES.keys()) == expected

    def test_every_article_has_required_keys(self):
        required_keys = {"title", "folder", "auto_detected_keys", "requires_human"}
        for art_num, meta in ARTICLES.items():
            for key in required_keys:
                assert key in meta, f"Article {art_num} missing key {key!r}"

    def test_folder_names_are_unique(self):
        folders = [meta["folder"] for meta in ARTICLES.values()]
        assert len(folders) == len(set(folders)), "Duplicate folder names"

    def test_requires_human_is_nonempty_for_every_article(self):
        for art_num, meta in ARTICLES.items():
            assert len(meta["requires_human"]) > 0, (
                f"Article {art_num} has no human-required items"
            )

    def test_auto_detected_keys_is_nonempty_for_every_article(self):
        for art_num, meta in ARTICLES.items():
            assert len(meta["auto_detected_keys"]) > 0, (
                f"Article {art_num} has no auto-detected keys"
            )

    def test_article_titles_are_strings(self):
        for art_num, meta in ARTICLES.items():
            assert isinstance(meta["title"], str) and len(meta["title"]) > 0

    def test_article_9_is_risk_management(self):
        assert ARTICLES["9"]["title"] == "Risk Management"

    def test_article_15_is_accuracy_robustness_cybersecurity(self):
        assert ARTICLES["15"]["title"] == "Accuracy, Robustness, Cybersecurity"


# ---------------------------------------------------------------------------
# 2. Helper functions
# ---------------------------------------------------------------------------


class TestSha256:
    """Tests for _sha256 helper."""

    def test_known_hash(self):
        result = _sha256("hello")
        expected = hashlib.sha256(b"hello").hexdigest()
        assert result == expected

    def test_empty_string(self):
        result = _sha256("")
        expected = hashlib.sha256(b"").hexdigest()
        assert result == expected

    def test_unicode_content(self):
        content = "Caf\u00e9 R\u00e9gulation"
        result = _sha256(content)
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert result == expected

    def test_returns_hex_string(self):
        result = _sha256("test")
        assert isinstance(result, str)
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)


class TestWriteAndRecord:
    """Tests for _write_and_record helper."""

    def test_writes_file_content(self, tmp_path):
        records = []
        path = tmp_path / "test.txt"
        _write_and_record(path, "hello world", records, tmp_path)
        assert path.read_text(encoding="utf-8") == "hello world"

    def test_appends_record(self, tmp_path):
        records = []
        path = tmp_path / "test.txt"
        _write_and_record(path, "hello world", records, tmp_path)
        assert len(records) == 1

    def test_record_has_required_fields(self, tmp_path):
        records = []
        path = tmp_path / "test.txt"
        _write_and_record(path, "hello world", records, tmp_path)
        rec = records[0]
        assert "filename" in rec
        assert "sha256" in rec
        assert "size_bytes" in rec

    def test_record_sha256_matches_content(self, tmp_path):
        records = []
        content = "test content for hashing"
        path = tmp_path / "test.txt"
        _write_and_record(path, content, records, tmp_path)
        expected_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert records[0]["sha256"] == expected_hash

    def test_record_size_bytes_matches_utf8(self, tmp_path):
        records = []
        content = "Caf\u00e9"  # e-acute = 2 bytes in UTF-8
        path = tmp_path / "test.txt"
        _write_and_record(path, content, records, tmp_path)
        assert records[0]["size_bytes"] == len(content.encode("utf-8"))

    def test_creates_parent_directories(self, tmp_path):
        records = []
        path = tmp_path / "deep" / "nested" / "dir" / "file.txt"
        _write_and_record(path, "nested", records, tmp_path)
        assert path.exists()
        assert path.read_text(encoding="utf-8") == "nested"

    def test_relative_path_in_record(self, tmp_path):
        records = []
        subdir = tmp_path / "sub"
        subdir.mkdir()
        path = subdir / "file.txt"
        _write_and_record(path, "data", records, tmp_path)
        assert records[0]["filename"] == "sub/file.txt"

    def test_filename_only_when_no_pack_dir(self, tmp_path):
        records = []
        path = tmp_path / "file.txt"
        _write_and_record(path, "data", records, pack_dir=None)
        assert records[0]["filename"] == "file.txt"

    def test_multiple_records_accumulate(self, tmp_path):
        records = []
        _write_and_record(tmp_path / "a.txt", "aaa", records, tmp_path)
        _write_and_record(tmp_path / "b.txt", "bbb", records, tmp_path)
        _write_and_record(tmp_path / "c.txt", "ccc", records, tmp_path)
        assert len(records) == 3
        filenames = {r["filename"] for r in records}
        assert filenames == {"a.txt", "b.txt", "c.txt"}


class TestMakeCoverage:
    """Tests for _make_coverage helper."""

    def test_basic_coverage_structure(self):
        auto = ["Some auto-detected item"]
        gap = {"score": 42}
        result = _make_coverage("9", auto, gap)
        assert result["article"] == 9
        assert result["title"] == "Risk Management"
        assert result["auto_detected"] == auto
        assert result["requires_human_input"] == ARTICLES["9"]["requires_human"]
        assert result["readiness"] == "42%"

    def test_zero_score_when_no_gap_data(self):
        result = _make_coverage("10", [], None)
        assert result["readiness"] == "0%"

    def test_zero_score_when_gap_has_no_score(self):
        result = _make_coverage("11", [], {})
        assert result["readiness"] == "0%"

    def test_all_articles_produce_valid_coverage(self):
        for art_num in ARTICLES:
            result = _make_coverage(art_num, ["item"], {"score": 50})
            assert result["article"] == int(art_num)
            assert result["title"] == ARTICLES[art_num]["title"]

    def test_coverage_includes_human_items_from_article(self):
        result = _make_coverage("13", [], {"score": 10})
        assert result["requires_human_input"] == ARTICLES["13"]["requires_human"]
        assert "Instructions for use document" in result["requires_human_input"]


class TestDeriveDeadlineSummary:
    """Tests for _derive_deadline_summary."""

    def test_defaults_when_no_findings(self):
        result = _derive_deadline_summary([])
        assert result["earliest_enforceable"] == "2026-08-02"
        assert result["omnibus_proposed_range"] == ["2027-12-02"]
        assert "note" in result

    def test_defaults_when_findings_lack_deadlines(self):
        findings = [{"tier": "high_risk"}, {"tier": "limited_risk"}]
        result = _derive_deadline_summary(findings)
        assert result["earliest_enforceable"] == "2026-08-02"

    def test_extracts_earliest_deadline(self):
        findings = [
            {"deadline": "2026-08-02"},
            {"deadline": "2027-01-15"},
            {"deadline": "2026-06-01"},
        ]
        result = _derive_deadline_summary(findings)
        assert result["earliest_enforceable"] == "2026-06-01"

    def test_extracts_omnibus_deadlines_sorted(self):
        findings = [
            {"omnibus_deadline": "2028-01-01"},
            {"omnibus_deadline": "2027-06-15"},
            {"omnibus_deadline": "2027-12-02"},
        ]
        result = _derive_deadline_summary(findings)
        assert result["omnibus_proposed_range"] == [
            "2027-06-15", "2027-12-02", "2028-01-01"
        ]

    def test_mixed_findings_with_and_without_deadlines(self):
        findings = [
            {"tier": "high_risk", "deadline": "2026-08-02"},
            {"tier": "limited_risk"},
            {"tier": "prohibited", "deadline": "2025-02-02"},
        ]
        result = _derive_deadline_summary(findings)
        assert result["earliest_enforceable"] == "2025-02-02"


# ---------------------------------------------------------------------------
# 3. Declaration template
# ---------------------------------------------------------------------------


class TestDeclarationTemplate:
    """Tests for _generate_declaration_template."""

    def test_contains_project_name(self):
        now = datetime(2026, 5, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = _generate_declaration_template("my-ai-system", now, 75, "high_risk")
        assert "my-ai-system" in result

    def test_contains_article_47_reference(self):
        now = datetime(2026, 5, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = _generate_declaration_template("test", now, 50, "high_risk")
        assert "Article 47" in result

    def test_contains_all_articles_9_to_15(self):
        now = datetime(2026, 5, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = _generate_declaration_template("test", now, 50, "high_risk")
        for art in [9, 10, 11, 12, 13, 14, 15]:
            assert f"Article {art}" in result

    def test_contains_date(self):
        now = datetime(2026, 5, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = _generate_declaration_template("test", now, 50, "high_risk")
        assert "2026-05-01" in result

    def test_contains_score(self):
        now = datetime(2026, 5, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = _generate_declaration_template("test", now, 88, "high_risk")
        assert "88%" in result

    def test_contains_regula_version(self):
        now = datetime(2026, 5, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = _generate_declaration_template("test", now, 50, "high_risk")
        assert VERSION in result

    def test_contains_risk_tier(self):
        now = datetime(2026, 5, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = _generate_declaration_template("test", now, 50, "limited_risk")
        assert "limited_risk" in result

    def test_contains_module_a_reference(self):
        now = datetime(2026, 5, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = _generate_declaration_template("test", now, 50, "high_risk")
        assert "Module A" in result

    def test_contains_to_be_completed_placeholders(self):
        now = datetime(2026, 5, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = _generate_declaration_template("test", now, 50, "high_risk")
        assert "[TO BE COMPLETED]" in result

    def test_honesty_disclaimer(self):
        now = datetime(2026, 5, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = _generate_declaration_template("test", now, 50, "high_risk")
        assert "not constitute a legal determination" in result


# ---------------------------------------------------------------------------
# 4. README generation
# ---------------------------------------------------------------------------


class TestReadmeGeneration:
    """Tests for _generate_readme."""

    def test_contains_project_name(self):
        result = _generate_readme("my-project", "2026-05-01", 65)
        assert "my-project" in result

    def test_contains_date(self):
        result = _generate_readme("test", "2026-05-01", 65)
        assert "2026-05-01" in result

    def test_contains_score(self):
        result = _generate_readme("test", "2026-05-01", 65)
        assert "65%" in result

    def test_contains_regula_version(self):
        result = _generate_readme("test", "2026-05-01", 65)
        assert VERSION in result

    def test_contains_honesty_note(self):
        result = _generate_readme("test", "2026-05-01", 65)
        assert "Honesty note" in result

    def test_contains_auditor_instructions(self):
        result = _generate_readme("test", "2026-05-01", 65)
        assert "auditors" in result.lower()

    def test_contains_manifest_reference(self):
        result = _generate_readme("test", "2026-05-01", 65)
        assert "manifest.json" in result

    def test_contains_annex_vi_module_a_reference(self):
        result = _generate_readme("test", "2026-05-01", 65)
        assert "Annex VI" in result

    def test_contains_regulation_reference(self):
        result = _generate_readme("test", "2026-05-01", 65)
        assert "2024/1689" in result


# ---------------------------------------------------------------------------
# 5. generate_conformity_pack — mocked integration
# ---------------------------------------------------------------------------

# Mock return values for the modules that conform.py imports lazily.

_MOCK_FINDINGS = [
    {
        "file": "model.py",
        "tier": "high_risk",
        "indicators": ["credit scoring"],
        "deadline": "2026-08-02",
        "omnibus_deadline": "2027-12-02",
    },
    {
        "file": "utils.py",
        "tier": "limited_risk",
        "indicators": ["chatbot"],
    },
]

_MOCK_GAP = {
    "overall_score": 42,
    "highest_risk": "high_risk",
    "articles": {
        "9": {"score": 35, "status": "partial", "evidence": ["risk log found"], "gaps": ["no risk matrix"]},
        "10": {"score": 50, "status": "partial", "evidence": [{"description": "data pipeline detected"}], "gaps": []},
        "11": {"score": 20, "status": "partial", "evidence": [], "gaps": ["missing docs"]},
        "12": {"score": 10, "status": "not_found", "evidence": [], "gaps": ["no logging"]},
        "13": {"score": 60, "status": "partial", "evidence": ["transparency info found"], "gaps": []},
        "14": {"score": 30, "status": "partial", "evidence": [], "gaps": ["no oversight gate"]},
        "15": {"score": 45, "status": "partial", "evidence": ["sbom detected"], "gaps": ["no pen test"]},
    },
}

_MOCK_DOC_FINDINGS = {
    "ai_files": ["model.py"],
    "model_files": [],
    "highest_risk": "high_risk",
}

_MOCK_ANNEX_IV = "# Annex IV Draft\n\nAutogenerated technical documentation."

_MOCK_PLAN = {
    "project": "test-project",
    "generated_at": "2026-05-01T00:00:00+00:00",
    "total_tasks": 5,
    "tasks": [],
}

_MOCK_PLAN_TEXT = "# Remediation Plan\n\nNo critical gaps."


def _patch_conform_dependencies():
    """Return a stack of patches for all lazily-imported dependencies."""
    scan_files_mock = MagicMock(return_value=_MOCK_FINDINGS)
    assess_compliance_mock = MagicMock(return_value=_MOCK_GAP)
    scan_project_mock = MagicMock(return_value=_MOCK_DOC_FINDINGS)
    generate_annex_iv_mock = MagicMock(return_value=_MOCK_ANNEX_IV)
    generate_plan_mock = MagicMock(return_value=_MOCK_PLAN)
    format_plan_text_mock = MagicMock(return_value=_MOCK_PLAN_TEXT)

    patches = [
        patch("conform.scan_files", scan_files_mock, create=True),
        patch("conform.assess_compliance", assess_compliance_mock, create=True),
        patch("conform.scan_project", scan_project_mock, create=True),
        patch("conform.generate_annex_iv", generate_annex_iv_mock, create=True),
        patch("conform.generate_plan", generate_plan_mock, create=True),
        patch("conform.format_plan_text", format_plan_text_mock, create=True),
    ]
    return patches


@pytest.fixture
def mock_conform_deps():
    """Fixture that patches all lazy imports in conform.generate_conformity_pack.

    We patch the import mechanism itself (builtins.__import__) so that when
    conform.py does `from report import scan_files` etc., it gets our mocks.
    """
    import builtins
    real_import = builtins.__import__

    mock_modules = {
        "report": MagicMock(scan_files=MagicMock(return_value=_MOCK_FINDINGS)),
        "compliance_check": MagicMock(assess_compliance=MagicMock(return_value=_MOCK_GAP)),
        "generate_documentation": MagicMock(
            scan_project=MagicMock(return_value=_MOCK_DOC_FINDINGS),
            generate_annex_iv=MagicMock(return_value=_MOCK_ANNEX_IV),
            generate_sme_simplified_annex_iv=MagicMock(return_value="# SME Simplified\n\nContent."),
        ),
        "remediation_plan": MagicMock(
            generate_plan=MagicMock(return_value=_MOCK_PLAN),
            format_plan_text=MagicMock(return_value=_MOCK_PLAN_TEXT),
        ),
    }

    # These optional modules should raise ImportError to exercise graceful degradation.
    optional_fail_modules = {"sbom", "log_event", "dependency_scan", "bias_eval", "bias_bbq",
                             "bias_report", "cross_file_flow", "signing", "timestamp"}

    def mock_import(name, *args, **kwargs):
        if name in mock_modules:
            return mock_modules[name]
        if name in optional_fail_modules:
            raise ImportError(f"Mocked: {name} not available")
        return real_import(name, *args, **kwargs)

    with patch.object(builtins, "__import__", side_effect=mock_import):
        yield mock_modules


@pytest.fixture
def project_dir(tmp_path):
    """Create a minimal project directory with a Python file."""
    proj = tmp_path / "test-project"
    proj.mkdir()
    (proj / "model.py").write_text("import tensorflow as tf\n")
    return proj


class TestGenerateConformityPack:
    """Integration tests for generate_conformity_pack with mocked deps."""

    def test_returns_expected_keys(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test-project",
        )
        assert "pack_dirname" in result
        assert "pack_path" in result
        assert "manifest" in result
        assert "summary" in result

    def test_pack_dirname_contains_project_name(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="my-system",
        )
        assert "my-system" in result["pack_dirname"]

    def test_pack_dirname_contains_date(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        # Date format: YYYY-MM-DD
        import re
        assert re.search(r"\d{4}-\d{2}-\d{2}", result["pack_dirname"])

    def test_pack_directory_exists(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        assert Path(result["pack_path"]).is_dir()

    def test_manifest_has_v1_format(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        manifest = result["manifest"]
        assert manifest["format"] == "regula.evidence.v1"
        assert manifest["format_version"] == "1.0"
        assert manifest["hash_algorithm"] == "sha256"

    def test_manifest_has_schema_uri(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        assert result["manifest"]["schema_uri"].endswith("regula.manifest.v1.schema.json")

    def test_manifest_has_regula_version(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        assert result["manifest"]["regula_version"] == VERSION

    def test_manifest_files_are_nonempty(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        files = result["manifest"]["files"]
        assert len(files) > 0
        for f in files:
            assert "filename" in f
            assert "sha256" in f
            assert "size_bytes" in f

    def test_manifest_json_written_to_disk(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        manifest_path = Path(result["pack_path"]) / "manifest.json"
        assert manifest_path.exists()
        parsed = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert parsed["format"] == "regula.evidence.v1"

    def test_summary_has_overall_readiness(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        summary = result["summary"]
        assert summary["overall_readiness"] == "42%"

    def test_summary_has_project_name(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="my-ai",
        )
        assert result["summary"]["project"] == "my-ai"

    def test_summary_has_conformity_type(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        assert "Module A" in result["summary"]["conformity_type"]

    def test_summary_has_human_required_items(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        human = result["summary"]["human_required"]
        assert len(human) > 0
        assert "Intended purpose description" in human

    def test_summary_has_auto_generated_items(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        auto = result["summary"]["auto_generated"]
        assert len(auto) > 0
        assert "Risk classification" in auto

    def test_summary_has_deadline_info(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        deadline = result["summary"]["deadline"]
        assert "earliest_enforceable" in deadline
        assert "note" in deadline

    def test_summary_articles_cover_9_to_15(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        articles = result["summary"]["articles"]
        for art_num in ["9", "10", "11", "12", "13", "14", "15"]:
            assert art_num in articles
            assert "title" in articles[art_num]
            assert "status" in articles[art_num]
            assert "auto_coverage" in articles[art_num]

    # --- Directory structure ---

    def test_creates_risk_classification_dir(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        assert (pack / "01-risk-classification").is_dir()

    def test_creates_all_article_dirs(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        for art_num, meta in ARTICLES.items():
            assert (pack / meta["folder"]).is_dir(), f"Missing dir for Article {art_num}"

    def test_creates_supply_chain_dir(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        assert (pack / "09-supply-chain").is_dir()

    def test_creates_declaration_dir(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        assert (pack / "10-declaration-of-conformity").is_dir()

    def test_creates_remediation_dir(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        assert (pack / "11-remediation").is_dir()

    # --- Key files ---

    def test_risk_classification_has_findings_json(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        findings_path = pack / "01-risk-classification" / "findings.json"
        assert findings_path.exists()
        data = json.loads(findings_path.read_text(encoding="utf-8"))
        assert isinstance(data, list)
        assert len(data) == 2  # matches _MOCK_FINDINGS

    def test_risk_classification_has_coverage_json(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        coverage_path = pack / "01-risk-classification" / "coverage.json"
        assert coverage_path.exists()
        data = json.loads(coverage_path.read_text(encoding="utf-8"))
        assert data["article"] == "classification"

    def test_each_article_has_evidence_json(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        for art_num, meta in ARTICLES.items():
            ev_path = pack / meta["folder"] / "evidence.json"
            assert ev_path.exists(), f"Missing evidence.json for Article {art_num}"
            data = json.loads(ev_path.read_text(encoding="utf-8"))
            assert data["article"] == int(art_num)
            assert data["title"] == meta["title"]

    def test_each_article_has_coverage_json(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        for art_num, meta in ARTICLES.items():
            cov_path = pack / meta["folder"] / "coverage.json"
            assert cov_path.exists(), f"Missing coverage.json for Article {art_num}"
            data = json.loads(cov_path.read_text(encoding="utf-8"))
            assert data["article"] == int(art_num)

    def test_article_11_has_annex_iv_draft(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        annex = pack / "04-technical-documentation-art11" / "annex-iv-draft.md"
        assert annex.exists()
        content = annex.read_text(encoding="utf-8")
        assert "Annex IV" in content

    def test_declaration_template_generated(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        decl = pack / "10-declaration-of-conformity" / "declaration-template.md"
        assert decl.exists()
        content = decl.read_text(encoding="utf-8")
        assert "Article 47" in content

    def test_remediation_plan_generated(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        plan = pack / "11-remediation" / "remediation-plan.md"
        assert plan.exists()

    def test_readme_generated(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        readme = pack / "README.md"
        assert readme.exists()
        content = readme.read_text(encoding="utf-8")
        assert "test" in content

    def test_assessment_summary_generated(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        summary_path = pack / "00-assessment-summary.json"
        assert summary_path.exists()
        data = json.loads(summary_path.read_text(encoding="utf-8"))
        assert data["overall_readiness"] == "42%"
        assert data["conformity_type"] == "internal (Annex VI, Module A)"

    # --- Project name fallback ---

    def test_defaults_project_name_to_dir_name(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
        )
        assert result["summary"]["project"] == project_dir.name


# ---------------------------------------------------------------------------
# 6. File integrity — SHA-256 records match written content
# ---------------------------------------------------------------------------


class TestFileIntegrity:
    """Verify manifest file records match the actual files on disk."""

    def test_all_manifest_files_exist_and_match_hash(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        for record in result["manifest"]["files"]:
            file_path = pack / record["filename"]
            assert file_path.exists(), f"File missing: {record['filename']}"
            content = file_path.read_text(encoding="utf-8")
            actual_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            assert actual_hash == record["sha256"], (
                f"Hash mismatch for {record['filename']}"
            )
            assert len(content.encode("utf-8")) == record["size_bytes"], (
                f"Size mismatch for {record['filename']}"
            )


# ---------------------------------------------------------------------------
# 7. Edge cases and error handling
# ---------------------------------------------------------------------------


class TestTimestampWithoutSign:
    """timestamp=True without sign=True must raise ValueError."""

    def test_raises_value_error(self, tmp_path, project_dir):
        with pytest.raises(ValueError, match="--timestamp requires --sign"):
            generate_conformity_pack(
                str(project_dir),
                output_dir=str(tmp_path / "output"),
                project_name="test",
                timestamp=True,
                sign=False,
            )


class TestEmptyFindings:
    """Test pack generation when the scan returns zero findings."""

    @pytest.fixture
    def mock_empty_deps(self):
        import builtins
        real_import = builtins.__import__

        mock_modules = {
            "report": MagicMock(scan_files=MagicMock(return_value=[])),
            "compliance_check": MagicMock(assess_compliance=MagicMock(return_value={
                "overall_score": 0,
                "highest_risk": "unknown",
                "articles": {},
            })),
            "generate_documentation": MagicMock(
                scan_project=MagicMock(return_value={
                    "ai_files": [], "model_files": [], "highest_risk": "none",
                }),
                generate_annex_iv=MagicMock(return_value="# Annex IV\n\nNo AI detected."),
            ),
            "remediation_plan": MagicMock(
                generate_plan=MagicMock(return_value={
                    "project": "empty",
                    "generated_at": "2026-05-01T00:00:00+00:00",
                    "total_tasks": 0,
                    "tasks": [],
                }),
                format_plan_text=MagicMock(return_value="# Remediation\nNothing to do."),
            ),
        }

        optional_fail = {"sbom", "log_event", "dependency_scan", "bias_eval",
                         "bias_bbq", "bias_report", "cross_file_flow", "signing", "timestamp"}

        def mock_import(name, *args, **kwargs):
            if name in mock_modules:
                return mock_modules[name]
            if name in optional_fail:
                raise ImportError(f"Mocked: {name}")
            return real_import(name, *args, **kwargs)

        with patch.object(builtins, "__import__", side_effect=mock_import):
            yield

    def test_empty_findings_pack_succeeds(self, tmp_path, project_dir, mock_empty_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="empty-project",
        )
        assert result["summary"]["overall_readiness"] == "0%"

    def test_risk_classification_readiness_is_not_run(self, tmp_path, project_dir, mock_empty_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="empty-project",
        )
        pack = Path(result["pack_path"])
        coverage = json.loads(
            (pack / "01-risk-classification" / "coverage.json").read_text(encoding="utf-8")
        )
        assert coverage["readiness"] == "not-run"

    def test_article_gaps_default_to_zero(self, tmp_path, project_dir, mock_empty_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="empty-project",
        )
        pack = Path(result["pack_path"])
        for art_num, meta in ARTICLES.items():
            ev = json.loads(
                (pack / meta["folder"] / "evidence.json").read_text(encoding="utf-8")
            )
            assert ev["gap_score"] == 0
            assert ev["status"] == "not_found"

    def test_supply_chain_placeholder_when_no_deps(self, tmp_path, project_dir, mock_empty_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="empty-project",
        )
        pack = Path(result["pack_path"])
        dep_report = json.loads(
            (pack / "09-supply-chain" / "dependency-report.json").read_text(encoding="utf-8")
        )
        assert "note" in dep_report


class TestOptionalModuleGracefulDegradation:
    """Verify that optional module failures do not crash pack generation."""

    def test_sbom_import_error_handled(self, tmp_path, project_dir, mock_conform_deps):
        # mock_conform_deps already raises ImportError for sbom
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        # Pack should still be generated successfully
        assert Path(result["pack_path"]).is_dir()

    def test_audit_import_error_handled(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        # No audit-trail.json should be present under article 12
        pack = Path(result["pack_path"])
        audit_path = pack / "05-record-keeping-art12" / "audit-trail.json"
        assert not audit_path.exists()

    def test_cross_file_flow_import_error_handled(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        oversight_path = pack / "07-human-oversight-art14" / "oversight-analysis.json"
        assert not oversight_path.exists()

    def test_bias_import_error_handled(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        bias_path = pack / "03-data-governance-art10" / "bias-evaluation.md"
        assert not bias_path.exists()


class TestWithOptionalModulesPresent:
    """Test pack generation when optional modules ARE available."""

    @pytest.fixture
    def mock_with_sbom_and_audit(self):
        import builtins
        real_import = builtins.__import__

        mock_sbom_data = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.7",
            "components": [{"name": "numpy", "version": "1.24.0"}],
        }
        mock_audit_events = [{"event": "scan_started", "ts": "2026-05-01T00:00:00Z"}]
        mock_dep_report = {
            "dependencies": [{"name": "numpy", "version": "1.24.0", "license": "BSD"}],
        }

        mock_modules = {
            "report": MagicMock(scan_files=MagicMock(return_value=_MOCK_FINDINGS)),
            "compliance_check": MagicMock(assess_compliance=MagicMock(return_value=_MOCK_GAP)),
            "generate_documentation": MagicMock(
                scan_project=MagicMock(return_value=_MOCK_DOC_FINDINGS),
                generate_annex_iv=MagicMock(return_value=_MOCK_ANNEX_IV),
            ),
            "remediation_plan": MagicMock(
                generate_plan=MagicMock(return_value=_MOCK_PLAN),
                format_plan_text=MagicMock(return_value=_MOCK_PLAN_TEXT),
            ),
            "sbom": MagicMock(
                generate_sbom=MagicMock(return_value=mock_sbom_data),
            ),
            "log_event": MagicMock(
                query_events=MagicMock(return_value=mock_audit_events),
                verify_chain=MagicMock(return_value=(True, "Chain valid")),
            ),
            "dependency_scan": MagicMock(
                scan_dependencies=MagicMock(return_value=mock_dep_report),
            ),
        }

        optional_fail = {"bias_eval", "bias_bbq", "bias_report",
                         "cross_file_flow", "signing", "timestamp"}

        def mock_import(name, *args, **kwargs):
            if name in mock_modules:
                return mock_modules[name]
            if name in optional_fail:
                raise ImportError(f"Mocked: {name}")
            return real_import(name, *args, **kwargs)

        with patch.object(builtins, "__import__", side_effect=mock_import):
            yield mock_modules

    def test_sbom_in_article_15(self, tmp_path, project_dir, mock_with_sbom_and_audit):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        sbom_path = pack / "08-accuracy-robustness-art15" / "sbom.json"
        assert sbom_path.exists()
        data = json.loads(sbom_path.read_text(encoding="utf-8"))
        assert data["bomFormat"] == "CycloneDX"

    def test_sbom_in_supply_chain(self, tmp_path, project_dir, mock_with_sbom_and_audit):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        sbom_path = pack / "09-supply-chain" / "sbom.json"
        assert sbom_path.exists()

    def test_audit_trail_in_article_12(self, tmp_path, project_dir, mock_with_sbom_and_audit):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        audit_path = pack / "05-record-keeping-art12" / "audit-trail.json"
        assert audit_path.exists()
        data = json.loads(audit_path.read_text(encoding="utf-8"))
        assert data["chain_valid"] is True
        assert data["event_count"] == 1

    def test_dependency_report_in_supply_chain(self, tmp_path, project_dir, mock_with_sbom_and_audit):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        dep_path = pack / "09-supply-chain" / "dependency-report.json"
        assert dep_path.exists()
        data = json.loads(dep_path.read_text(encoding="utf-8"))
        assert "dependencies" in data


class TestWithOversightAnalysis:
    """Test Article 14 oversight analysis when cross_file_flow is available."""

    @pytest.fixture
    def mock_with_oversight(self):
        import builtins
        real_import = builtins.__import__

        mock_oversight_result = {
            "analysed": True,
            "summary": {
                "total_paths": 5,
                "reviewed": 3,
                "unreviewed": 2,
            },
            "paths": [],
        }

        mock_modules = {
            "report": MagicMock(scan_files=MagicMock(return_value=_MOCK_FINDINGS)),
            "compliance_check": MagicMock(assess_compliance=MagicMock(return_value=_MOCK_GAP)),
            "generate_documentation": MagicMock(
                scan_project=MagicMock(return_value=_MOCK_DOC_FINDINGS),
                generate_annex_iv=MagicMock(return_value=_MOCK_ANNEX_IV),
            ),
            "remediation_plan": MagicMock(
                generate_plan=MagicMock(return_value=_MOCK_PLAN),
                format_plan_text=MagicMock(return_value=_MOCK_PLAN_TEXT),
            ),
            "cross_file_flow": MagicMock(
                analyse_project_oversight=MagicMock(return_value=mock_oversight_result),
            ),
        }

        optional_fail = {"sbom", "log_event", "dependency_scan",
                         "bias_eval", "bias_bbq", "bias_report",
                         "signing", "timestamp"}

        def mock_import(name, *args, **kwargs):
            if name in mock_modules:
                return mock_modules[name]
            if name in optional_fail:
                raise ImportError(f"Mocked: {name}")
            return real_import(name, *args, **kwargs)

        with patch.object(builtins, "__import__", side_effect=mock_import):
            yield

    def test_oversight_analysis_file_created(self, tmp_path, project_dir, mock_with_oversight):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        oversight_path = pack / "07-human-oversight-art14" / "oversight-analysis.json"
        assert oversight_path.exists()

    def test_oversight_coverage_reports_paths(self, tmp_path, project_dir, mock_with_oversight):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        coverage = json.loads(
            (pack / "07-human-oversight-art14" / "coverage.json").read_text(encoding="utf-8")
        )
        # Should mention the 3/5 ratio from mock data
        auto = " ".join(coverage["auto_detected"])
        assert "3/5" in auto

    def test_oversight_warns_about_unreviewed(self, tmp_path, project_dir, mock_with_oversight):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        coverage = json.loads(
            (pack / "07-human-oversight-art14" / "coverage.json").read_text(encoding="utf-8")
        )
        auto = " ".join(coverage["auto_detected"])
        assert "WARNING" in auto
        assert "2" in auto


class TestOversightNotAnalysed:
    """Test the 'not analysed' branch of oversight logic."""

    @pytest.fixture
    def mock_with_unanalysed_oversight(self):
        import builtins
        real_import = builtins.__import__

        mock_modules = {
            "report": MagicMock(scan_files=MagicMock(return_value=_MOCK_FINDINGS)),
            "compliance_check": MagicMock(assess_compliance=MagicMock(return_value=_MOCK_GAP)),
            "generate_documentation": MagicMock(
                scan_project=MagicMock(return_value=_MOCK_DOC_FINDINGS),
                generate_annex_iv=MagicMock(return_value=_MOCK_ANNEX_IV),
            ),
            "remediation_plan": MagicMock(
                generate_plan=MagicMock(return_value=_MOCK_PLAN),
                format_plan_text=MagicMock(return_value=_MOCK_PLAN_TEXT),
            ),
            "cross_file_flow": MagicMock(
                analyse_project_oversight=MagicMock(return_value={
                    "analysed": False,
                    "reason": "No entry points found",
                    "summary": {"total_paths": 0, "reviewed": 0, "unreviewed": 0},
                }),
            ),
        }

        optional_fail = {"sbom", "log_event", "dependency_scan",
                         "bias_eval", "bias_bbq", "bias_report",
                         "signing", "timestamp"}

        def mock_import(name, *args, **kwargs):
            if name in mock_modules:
                return mock_modules[name]
            if name in optional_fail:
                raise ImportError(f"Mocked: {name}")
            return real_import(name, *args, **kwargs)

        with patch.object(builtins, "__import__", side_effect=mock_import):
            yield

    def test_not_analysed_message(self, tmp_path, project_dir, mock_with_unanalysed_oversight):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        coverage = json.loads(
            (pack / "07-human-oversight-art14" / "coverage.json").read_text(encoding="utf-8")
        )
        auto = " ".join(coverage["auto_detected"])
        assert "NOT ANALYSED" in auto


class TestOversightNoSources:
    """Test the 'no AI output sources detected' branch."""

    @pytest.fixture
    def mock_with_no_ai_sources(self):
        import builtins
        real_import = builtins.__import__

        mock_modules = {
            "report": MagicMock(scan_files=MagicMock(return_value=_MOCK_FINDINGS)),
            "compliance_check": MagicMock(assess_compliance=MagicMock(return_value=_MOCK_GAP)),
            "generate_documentation": MagicMock(
                scan_project=MagicMock(return_value=_MOCK_DOC_FINDINGS),
                generate_annex_iv=MagicMock(return_value=_MOCK_ANNEX_IV),
            ),
            "remediation_plan": MagicMock(
                generate_plan=MagicMock(return_value=_MOCK_PLAN),
                format_plan_text=MagicMock(return_value=_MOCK_PLAN_TEXT),
            ),
            "cross_file_flow": MagicMock(
                analyse_project_oversight=MagicMock(return_value={
                    "analysed": True,
                    "summary": {"total_paths": 0, "reviewed": 0, "unreviewed": 0},
                    "paths": [],
                }),
            ),
        }

        optional_fail = {"sbom", "log_event", "dependency_scan",
                         "bias_eval", "bias_bbq", "bias_report",
                         "signing", "timestamp"}

        def mock_import(name, *args, **kwargs):
            if name in mock_modules:
                return mock_modules[name]
            if name in optional_fail:
                raise ImportError(f"Mocked: {name}")
            return real_import(name, *args, **kwargs)

        with patch.object(builtins, "__import__", side_effect=mock_import):
            yield

    def test_no_sources_message(self, tmp_path, project_dir, mock_with_no_ai_sources):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        coverage = json.loads(
            (pack / "07-human-oversight-art14" / "coverage.json").read_text(encoding="utf-8")
        )
        auto = " ".join(coverage["auto_detected"])
        assert "no AI output sources detected" in auto


class TestRiskClassificationCoverage:
    """Test the risk classification coverage summary logic."""

    @pytest.fixture
    def mock_with_mixed_findings(self):
        import builtins
        real_import = builtins.__import__

        mixed_findings = [
            {"file": "a.py", "tier": "prohibited", "indicators": ["social scoring"]},
            {"file": "b.py", "tier": "high_risk", "indicators": ["credit scoring"]},
            {"file": "c.py", "tier": "high_risk", "indicators": ["biometric"]},
            {"file": "d.py", "tier": "limited_risk", "indicators": ["chatbot"]},
        ]

        mock_modules = {
            "report": MagicMock(scan_files=MagicMock(return_value=mixed_findings)),
            "compliance_check": MagicMock(assess_compliance=MagicMock(return_value=_MOCK_GAP)),
            "generate_documentation": MagicMock(
                scan_project=MagicMock(return_value=_MOCK_DOC_FINDINGS),
                generate_annex_iv=MagicMock(return_value=_MOCK_ANNEX_IV),
            ),
            "remediation_plan": MagicMock(
                generate_plan=MagicMock(return_value=_MOCK_PLAN),
                format_plan_text=MagicMock(return_value=_MOCK_PLAN_TEXT),
            ),
        }

        optional_fail = {"sbom", "log_event", "dependency_scan",
                         "bias_eval", "bias_bbq", "bias_report",
                         "cross_file_flow", "signing", "timestamp"}

        def mock_import(name, *args, **kwargs):
            if name in mock_modules:
                return mock_modules[name]
            if name in optional_fail:
                raise ImportError(f"Mocked: {name}")
            return real_import(name, *args, **kwargs)

        with patch.object(builtins, "__import__", side_effect=mock_import):
            yield

    def test_rc_coverage_counts_tiers(self, tmp_path, project_dir, mock_with_mixed_findings):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        coverage = json.loads(
            (pack / "01-risk-classification" / "coverage.json").read_text(encoding="utf-8")
        )
        auto_text = " ".join(coverage["auto_detected"])
        assert "4 findings" in auto_text
        assert "1 prohibited" in auto_text
        assert "2 high-risk" in auto_text
        assert "1 limited" in auto_text

    def test_rc_coverage_readiness_is_complete_with_findings(self, tmp_path, project_dir, mock_with_mixed_findings):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        coverage = json.loads(
            (pack / "01-risk-classification" / "coverage.json").read_text(encoding="utf-8")
        )
        assert coverage["readiness"] == "complete"


class TestEvidenceJsonStructure:
    """Test the evidence.json structure for articles with gap data."""

    def test_evidence_contains_gap_score(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        ev = json.loads(
            (pack / "02-risk-management-art9" / "evidence.json").read_text(encoding="utf-8")
        )
        assert ev["gap_score"] == 35
        assert ev["status"] == "partial"

    def test_evidence_contains_string_evidence(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        ev = json.loads(
            (pack / "02-risk-management-art9" / "evidence.json").read_text(encoding="utf-8")
        )
        assert "risk log found" in ev["evidence_found"]

    def test_evidence_contains_gaps(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        ev = json.loads(
            (pack / "02-risk-management-art9" / "evidence.json").read_text(encoding="utf-8")
        )
        assert "no risk matrix" in ev["gaps_identified"]


class TestCoverageAutoDetectedFromGap:
    """Test that coverage auto_detected list picks up evidence from gap data."""

    def test_string_evidence_in_auto_detected(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        cov = json.loads(
            (pack / "02-risk-management-art9" / "coverage.json").read_text(encoding="utf-8")
        )
        auto = " ".join(cov["auto_detected"])
        assert "risk log found" in auto

    def test_dict_evidence_description_in_auto_detected(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        cov = json.loads(
            (pack / "03-data-governance-art10" / "coverage.json").read_text(encoding="utf-8")
        )
        auto = " ".join(cov["auto_detected"])
        assert "data pipeline detected" in auto

    def test_article_11_auto_detected_includes_annex_iv(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        pack = Path(result["pack_path"])
        cov = json.loads(
            (pack / "04-technical-documentation-art11" / "coverage.json").read_text(encoding="utf-8")
        )
        auto = " ".join(cov["auto_detected"])
        assert "Annex IV" in auto


# ---------------------------------------------------------------------------
# 8. SME simplified pack
# ---------------------------------------------------------------------------


class TestSmeSimplifiedPack:
    """Tests for generate_sme_simplified_pack."""

    @pytest.fixture
    def mock_sme_deps(self):
        import builtins
        real_import = builtins.__import__

        mock_modules = {
            "generate_documentation": MagicMock(
                scan_project=MagicMock(return_value=_MOCK_DOC_FINDINGS),
                generate_sme_simplified_annex_iv=MagicMock(
                    return_value="# SME Simplified Annex IV\n\nSimplified content."
                ),
            ),
        }

        def mock_import(name, *args, **kwargs):
            if name in mock_modules:
                return mock_modules[name]
            return real_import(name, *args, **kwargs)

        with patch.object(builtins, "__import__", side_effect=mock_import):
            yield

    def test_returns_expected_keys(self, tmp_path, project_dir, mock_sme_deps):
        result = generate_sme_simplified_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="sme-test",
        )
        assert "pack_dirname" in result
        assert "pack_path" in result
        assert "manifest" in result
        assert "summary" in result

    def test_output_file_exists(self, tmp_path, project_dir, mock_sme_deps):
        result = generate_sme_simplified_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="sme-test",
        )
        assert Path(result["pack_path"]).exists()

    def test_manifest_form_is_sme_simplified(self, tmp_path, project_dir, mock_sme_deps):
        result = generate_sme_simplified_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="sme-test",
        )
        assert result["manifest"]["form"] == "sme_simplified_annex_iv"

    def test_manifest_has_interim_disclosure(self, tmp_path, project_dir, mock_sme_deps):
        result = generate_sme_simplified_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="sme-test",
        )
        assert "interim_format_disclosure" in result["manifest"]
        assert "Article 11" in result["manifest"]["interim_format_disclosure"]

    def test_manifest_has_file_record_with_sha256(self, tmp_path, project_dir, mock_sme_deps):
        result = generate_sme_simplified_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="sme-test",
        )
        files = result["manifest"]["files"]
        assert len(files) == 1
        assert "sha256" in files[0]
        assert "size_bytes" in files[0]

    def test_summary_form_is_sme(self, tmp_path, project_dir, mock_sme_deps):
        result = generate_sme_simplified_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="sme-test",
        )
        assert result["summary"]["form"] == "sme_simplified_annex_iv"

    def test_summary_readiness_is_interim(self, tmp_path, project_dir, mock_sme_deps):
        result = generate_sme_simplified_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="sme-test",
        )
        assert "interim" in result["summary"]["overall_readiness"]

    def test_summary_has_regula_version(self, tmp_path, project_dir, mock_sme_deps):
        result = generate_sme_simplified_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="sme-test",
        )
        assert result["summary"]["regula_version"] == VERSION

    def test_defaults_name_to_directory_name(self, tmp_path, project_dir, mock_sme_deps):
        result = generate_sme_simplified_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
        )
        assert result["summary"]["project"] == project_dir.name

    def test_file_sha256_matches_content(self, tmp_path, project_dir, mock_sme_deps):
        result = generate_sme_simplified_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="sme-test",
        )
        content = Path(result["pack_path"]).read_text(encoding="utf-8")
        expected_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert result["manifest"]["files"][0]["sha256"] == expected_hash

    def test_manifest_has_evidence_v1_format(self, tmp_path, project_dir, mock_sme_deps):
        result = generate_sme_simplified_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="sme-test",
        )
        assert result["manifest"]["format"] == "regula.evidence.v1"
        assert result["manifest"]["format_version"] == "1.0"


# ---------------------------------------------------------------------------
# 9. Format version bumps with signing
# ---------------------------------------------------------------------------


class TestFormatVersionBump:
    """Test that format_version is 1.1 when sign=True."""

    @pytest.fixture
    def mock_with_signing(self):
        import builtins
        real_import = builtins.__import__

        mock_modules = {
            "report": MagicMock(scan_files=MagicMock(return_value=_MOCK_FINDINGS)),
            "compliance_check": MagicMock(assess_compliance=MagicMock(return_value=_MOCK_GAP)),
            "generate_documentation": MagicMock(
                scan_project=MagicMock(return_value=_MOCK_DOC_FINDINGS),
                generate_annex_iv=MagicMock(return_value=_MOCK_ANNEX_IV),
            ),
            "remediation_plan": MagicMock(
                generate_plan=MagicMock(return_value=_MOCK_PLAN),
                format_plan_text=MagicMock(return_value=_MOCK_PLAN_TEXT),
            ),
            "signing": MagicMock(
                sign_manifest=MagicMock(return_value={
                    "algorithm": "ed25519",
                    "public_key": "mock_pub_key",
                    "signature": "mock_signature",
                }),
                # conform calls signing.apply_manifest_security (the shared
                # sign→timestamp sequence); the mock must honour its
                # contract of mutating the manifest, not just return a Mock.
                apply_manifest_security=MagicMock(
                    side_effect=lambda manifest, *, sign=False,
                    signing_key_path=None, timestamp=False, tsa_url=None: (
                        manifest.update({
                            "format_version": "1.1",
                            "signing": {
                                "algorithm": "ed25519",
                                "public_key": "mock_pub_key",
                                "signature": "mock_signature",
                            },
                        }) or manifest
                    ) if sign else manifest
                ),
            ),
        }

        optional_fail = {"sbom", "log_event", "dependency_scan",
                         "bias_eval", "bias_bbq", "bias_report",
                         "cross_file_flow", "timestamp"}

        def mock_import(name, *args, **kwargs):
            if name in mock_modules:
                return mock_modules[name]
            if name in optional_fail:
                raise ImportError(f"Mocked: {name}")
            return real_import(name, *args, **kwargs)

        with patch.object(builtins, "__import__", side_effect=mock_import):
            yield

    def test_format_version_is_1_1_when_signed(self, tmp_path, project_dir, mock_with_signing):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
            sign=True,
        )
        assert result["manifest"]["format_version"] == "1.1"

    def test_signing_block_present(self, tmp_path, project_dir, mock_with_signing):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
            sign=True,
        )
        assert "signing" in result["manifest"]
        assert result["manifest"]["signing"]["algorithm"] == "ed25519"


# ---------------------------------------------------------------------------
# 10. Article summary structure
# ---------------------------------------------------------------------------


class TestArticleSummaryStructure:
    """Verify the per-article summary dict in the overall summary."""

    def test_article_summary_has_evidence_files(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        for art_num in ["9", "10", "11", "12", "13", "14", "15"]:
            art = result["summary"]["articles"][art_num]
            assert "evidence_files" in art
            # Each article should reference at least evidence.json and coverage.json
            assert len(art["evidence_files"]) >= 2

    def test_article_summary_auto_coverage_matches_gap(self, tmp_path, project_dir, mock_conform_deps):
        result = generate_conformity_pack(
            str(project_dir),
            output_dir=str(tmp_path / "output"),
            project_name="test",
        )
        art9 = result["summary"]["articles"]["9"]
        assert art9["auto_coverage"] == "35%"
        assert art9["status"] == "partial"
