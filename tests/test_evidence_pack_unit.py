# regula-ignore
"""Comprehensive unit tests for scripts/evidence_pack.py.

Tests cover:
- _sha256 hashing
- _write_and_record file writing and record keeping
- _generate_summary executive summary generation
- _generate_readme README generation
- generate_bundle ZIP bundle creation and integrity
- generate_evidence_pack end-to-end with mocked sub-modules
- Path sanitisation (traversal prevention)
- Error handling (missing manifest, missing directories)
- Format version compliance
"""

import hashlib
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from evidence_pack import (
    _sha256,
    _write_and_record,
    _generate_summary,
    _generate_readme,
    generate_bundle,
    generate_evidence_pack,
    _VERIFY_SCRIPT,
)
from constants import VERSION


# ── _sha256 ──────────────────────────────────────────────────────────


class TestSha256:
    """Tests for the _sha256 helper."""

    def test_empty_string(self):
        expected = hashlib.sha256(b"").hexdigest()
        assert _sha256("") == expected

    def test_known_value(self):
        content = "hello world"
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert _sha256(content) == expected

    def test_unicode_content(self):
        content = "Verordnung \u00fc\u00e4\u00f6 \u2014 EU AI Act \u00a7 42"
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert _sha256(content) == expected

    def test_multiline_json(self):
        data = json.dumps({"key": "value", "nested": [1, 2, 3]}, indent=2)
        expected = hashlib.sha256(data.encode("utf-8")).hexdigest()
        assert _sha256(data) == expected

    def test_deterministic(self):
        content = "same input should produce same output"
        assert _sha256(content) == _sha256(content)

    def test_different_inputs_differ(self):
        assert _sha256("a") != _sha256("b")


# ── _write_and_record ────────────────────────────────────────────────


class TestWriteAndRecord:
    """Tests for file writing with hash recording."""

    def test_creates_file(self, tmp_path):
        records = []
        _write_and_record(tmp_path, "test.txt", "hello", records)
        assert (tmp_path / "test.txt").exists()
        assert (tmp_path / "test.txt").read_text(encoding="utf-8") == "hello"

    def test_records_hash(self, tmp_path):
        records = []
        content = "content for hashing"
        _write_and_record(tmp_path, "test.txt", content, records)
        assert len(records) == 1
        assert records[0]["filename"] == "test.txt"
        assert records[0]["sha256"] == hashlib.sha256(content.encode("utf-8")).hexdigest()

    def test_records_size_bytes(self, tmp_path):
        records = []
        content = "ASCII content"
        _write_and_record(tmp_path, "test.txt", content, records)
        assert records[0]["size_bytes"] == len(content.encode("utf-8"))

    def test_records_size_bytes_unicode(self, tmp_path):
        records = []
        # Multi-byte chars: each of these is 2 bytes in UTF-8
        content = "\u00e4\u00f6\u00fc"
        _write_and_record(tmp_path, "test.txt", content, records)
        assert records[0]["size_bytes"] == len(content.encode("utf-8"))
        # 3 chars but 6 bytes
        assert records[0]["size_bytes"] == 6

    def test_multiple_files_append(self, tmp_path):
        records = []
        _write_and_record(tmp_path, "a.txt", "aaa", records)
        _write_and_record(tmp_path, "b.txt", "bbb", records)
        _write_and_record(tmp_path, "c.txt", "ccc", records)
        assert len(records) == 3
        assert [r["filename"] for r in records] == ["a.txt", "b.txt", "c.txt"]

    def test_overwrites_existing_file(self, tmp_path):
        records = []
        (tmp_path / "test.txt").write_text("old content", encoding="utf-8")
        _write_and_record(tmp_path, "test.txt", "new content", records)
        assert (tmp_path / "test.txt").read_text(encoding="utf-8") == "new content"

    def test_empty_content(self, tmp_path):
        records = []
        _write_and_record(tmp_path, "empty.txt", "", records)
        assert (tmp_path / "empty.txt").read_text(encoding="utf-8") == ""
        assert records[0]["size_bytes"] == 0
        assert records[0]["sha256"] == hashlib.sha256(b"").hexdigest()


# ── _generate_summary ────────────────────────────────────────────────


class TestGenerateSummary:
    """The handoff summary must fail closed when no facts were supplied."""

    def _make_findings(self, prohibited=0, high_risk=0, limited=0, minimal=0):
        findings = []
        for _ in range(prohibited):
            findings.append({"tier": "prohibited"})
        for _ in range(high_risk):
            findings.append({"tier": "high_risk"})
        for _ in range(limited):
            findings.append({"tier": "limited_risk"})
        for _ in range(minimal):
            findings.append({"tier": "minimal_risk"})
        return findings

    def _decision(self):
        from decision_adapters import empty_decision
        return empty_decision("eu", "test:evidence-summary")

    def test_contains_project_name(self):
        now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
        summary = _generate_summary("my-project", now, [], self._decision())
        assert "my-project" in summary

    def test_contains_version(self):
        now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
        summary = _generate_summary("proj", now, [], self._decision())
        assert f"v{VERSION}" in summary

    def test_contains_date(self):
        now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
        summary = _generate_summary("proj", now, [], self._decision())
        assert "2026-05-01 12:00 UTC" in summary

    def test_risk_counts(self):
        now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
        findings = self._make_findings(prohibited=2, high_risk=5, limited=3)
        summary = _generate_summary("proj", now, findings, self._decision())
        assert "| Article 5 pattern observations | 2 |" in summary
        assert "| Annex III pattern observations | 5 |" in summary
        assert "| Article 50 pattern observations | 3 |" in summary
        assert "| Total detector observations | 10 |" in summary

    def test_scan_coverage_names_what_was_not_read(self):
        """N146 applied to the pack: a count of observations must not be
        printed without the population it was drawn from.

        Measured on ageitgey/face_recognition at 9f3061a: the default scan reads
        8 files and 23 code files under `examples/` are pruned, and until
        2026-08-17 the pack said neither.
        """
        now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
        stats = {"files_scanned": 8, "pruned_code_files": 23,
                 "pruned_dirs": [{"path": "examples", "skipped_because": "examples"}],
                 "skipped_total": 0}
        summary = _generate_summary("proj", now, [], self._decision(), stats)
        assert "## Scan coverage" in summary
        assert "**Files read:** 8" in summary
        assert "23 code file(s)" in summary
        assert "examples" in summary
        # And it must come BEFORE the counts it qualifies.
        assert summary.index("## Scan coverage") < summary.index("## Detector observations")

    def test_scan_coverage_says_so_when_nothing_was_excluded(self):
        """The other direction: without it the section could pass by always
        claiming an exclusion."""
        now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
        stats = {"files_scanned": 12, "pruned_code_files": 0,
                 "pruned_dirs": [], "skipped_total": 0}
        summary = _generate_summary("proj", now, [], self._decision(), stats)
        assert "**Files read:** 12" in summary
        assert "No code file was excluded" in summary
        assert "code file(s) in" not in summary

    def test_scan_coverage_fails_loud_when_stats_are_absent(self):
        """Rule 4: an absent signal is not a passing signal. A pack built
        without statistics must say the population is unstated rather than
        imply full coverage."""
        now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
        summary = _generate_summary("proj", now, [], self._decision())
        assert "**Not recorded.**" in summary
        assert "unstated" in summary

    def test_scan_coverage_reports_an_unreadable_file_as_a_partial_scan(self):
        now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
        stats = {"files_scanned": 5, "pruned_code_files": 0,
                 "pruned_dirs": [], "skipped_total": 2}
        summary = _generate_summary("proj", now, [], self._decision(), stats)
        assert "PARTIAL" in summary
        assert "2 eligible file(s)" in summary

    def test_compliance_score(self):
        now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
        summary = _generate_summary("proj", now, [], self._decision())
        assert "readiness percentage" in summary
        assert "42%" not in summary

    def test_highest_risk_tier_formatting(self):
        now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
        summary = _generate_summary("proj", now, [], self._decision())
        assert "Highest risk tier" not in summary
        assert "insufficient_information" in summary

    def test_article_table(self):
        now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
        summary = _generate_summary("proj", now, [], self._decision())
        assert "| Article | Requirement | Score | Status |" not in summary
        assert "article duty" in summary

    def test_effort_estimate(self):
        now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
        summary = _generate_summary("proj", now, [], self._decision())
        assert "effort estimate" in summary
        assert "hours" not in summary

    def test_total_tasks(self):
        now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
        summary = _generate_summary("proj", now, [], self._decision())
        assert "**Total tasks:**" not in summary

    def test_deadline_present(self):
        now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
        summary = _generate_summary("proj", now, [], self._decision())
        assert "Primary deadline" not in summary
        assert "before relying" in summary

    def test_disclaimer_present(self):
        now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
        summary = _generate_summary("proj", now, [], self._decision())
        assert "no legal classification" in summary.lower()

    def test_zero_findings(self):
        now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
        summary = _generate_summary("proj", now, [], self._decision())
        assert "| Article 5 pattern observations | 0 |" in summary
        assert "| Total detector observations | 0 |" in summary

    def test_effort_with_no_tasks(self):
        now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
        summary = _generate_summary("proj", now, [], self._decision())
        assert "~0-0 hours" not in summary

    def test_tasks_without_effort_hours_ignored(self):
        """Tasks that lack effort_hours (or have non-list) should not crash."""
        now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
        summary = _generate_summary("proj", now, [], self._decision())
        assert "~2-4 hours" not in summary
        assert "06-resolvable-facts.md" in summary


# ── _generate_readme ─────────────────────────────────────────────────


class TestGenerateReadme:
    """Tests for README generation."""

    def test_contains_project_name(self):
        readme = _generate_readme("my-project", "2026-05-01")
        assert "my-project" in readme

    def test_contains_date(self):
        readme = _generate_readme("proj", "2026-05-01")
        assert "2026-05-01" in readme

    def test_contains_version(self):
        readme = _generate_readme("proj", "2026-05-01")
        assert f"v{VERSION}" in readme

    def test_contains_verification_instructions(self):
        readme = _generate_readme("proj", "2026-05-01")
        assert "manifest.json" in readme
        assert "sha256" in readme.lower()

    def test_contains_usage_guidance_consultants(self):
        readme = _generate_readme("proj", "2026-05-01")
        assert "00-summary.md" in readme
        assert "02-gap-assessment.json" in readme

    def test_contains_usage_guidance_developers(self):
        readme = _generate_readme("proj", "2026-05-01")
        assert "06-resolvable-facts.md" in readme

    def test_disclaimer(self):
        readme = _generate_readme("proj", "2026-05-01")
        assert "not legal determinations" in readme.lower()


# ── generate_bundle ──────────────────────────────────────────────────


class TestGenerateBundle:
    """Tests for ZIP bundle creation."""

    def _make_pack(self, tmp_path, name="evidence-pack-test-2026-05-01"):
        pack_dir = tmp_path / name
        pack_dir.mkdir()
        content = "# Summary\nTest content."
        sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
        (pack_dir / "00-summary.md").write_text(content, encoding="utf-8")
        manifest = {
            "schema_version": "1.0",
            "regula_version": VERSION,
            "generated_at": "2026-05-01T00:00:00+00:00",
            "project": "test",
            "project_path": "/tmp/test",
            "files": [
                {
                    "filename": "00-summary.md",
                    "sha256": sha,
                    "size_bytes": len(content.encode("utf-8")),
                }
            ],
        }
        (pack_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        return pack_dir

    def test_creates_zip_file(self, tmp_path):
        pack_dir = self._make_pack(tmp_path)
        bundle_path = generate_bundle(str(pack_dir))
        assert Path(bundle_path).exists()

    def test_zip_extension(self, tmp_path):
        pack_dir = self._make_pack(tmp_path)
        bundle_path = generate_bundle(str(pack_dir))
        assert bundle_path.endswith(".regula-evidence.zip")

    def test_zip_path_derives_from_pack_dir(self, tmp_path):
        pack_dir = self._make_pack(tmp_path, "evidence-pack-myproj-2026-05-01")
        bundle_path = generate_bundle(str(pack_dir))
        expected = str(pack_dir) + ".regula-evidence.zip"
        assert bundle_path == expected

    def test_zip_contains_pack_files(self, tmp_path):
        pack_dir = self._make_pack(tmp_path)
        bundle_path = generate_bundle(str(pack_dir))
        with zipfile.ZipFile(bundle_path, "r") as zf:
            names = zf.namelist()
            assert "00-summary.md" in names
            assert "manifest.json" in names

    def test_zip_contains_verify_script(self, tmp_path):
        pack_dir = self._make_pack(tmp_path)
        bundle_path = generate_bundle(str(pack_dir))
        with zipfile.ZipFile(bundle_path, "r") as zf:
            assert "verify.py" in zf.namelist()

    def test_verify_script_content(self, tmp_path):
        pack_dir = self._make_pack(tmp_path)
        bundle_path = generate_bundle(str(pack_dir))
        with zipfile.ZipFile(bundle_path, "r") as zf:
            script = zf.read("verify.py").decode("utf-8")
            assert script == _VERIFY_SCRIPT

    def test_zip_uses_deflate(self, tmp_path):
        pack_dir = self._make_pack(tmp_path)
        bundle_path = generate_bundle(str(pack_dir))
        with zipfile.ZipFile(bundle_path, "r") as zf:
            for info in zf.infolist():
                assert info.compress_type == zipfile.ZIP_DEFLATED

    def test_missing_manifest_raises(self, tmp_path):
        pack_dir = tmp_path / "no-manifest"
        pack_dir.mkdir()
        (pack_dir / "some-file.txt").write_text("data")
        import pytest
        with pytest.raises(FileNotFoundError):
            generate_bundle(str(pack_dir))

    def test_missing_manifest_error_message(self, tmp_path):
        pack_dir = tmp_path / "no-manifest"
        pack_dir.mkdir()
        (pack_dir / "some-file.txt").write_text("data")
        import pytest
        with pytest.raises(FileNotFoundError, match="No manifest.json"):
            generate_bundle(str(pack_dir))

    def test_multiple_files(self, tmp_path):
        pack_dir = tmp_path / "multi"
        pack_dir.mkdir()
        files = {
            "00-summary.md": "# Summary",
            "01-scan-results.json": "[]",
            "02-gap-assessment.json": "{}",
            "06-remediation-plan.md": "# Plan",
        }
        manifest_files = []
        for fname, content in files.items():
            (pack_dir / fname).write_text(content, encoding="utf-8")
            manifest_files.append({
                "filename": fname,
                "sha256": _sha256(content),
                "size_bytes": len(content.encode("utf-8")),
            })
        manifest = {
            "schema_version": "1.0",
            "regula_version": VERSION,
            "generated_at": "2026-05-01T00:00:00+00:00",
            "project": "multi",
            "project_path": "/tmp/multi",
            "files": manifest_files,
        }
        (pack_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        bundle_path = generate_bundle(str(pack_dir))
        with zipfile.ZipFile(bundle_path, "r") as zf:
            names = zf.namelist()
            for fname in files:
                assert fname in names
            assert "manifest.json" in names
            assert "verify.py" in names

    def test_subdirectories_skipped(self, tmp_path):
        """Subdirectories inside the pack should not be included."""
        pack_dir = self._make_pack(tmp_path)
        subdir = pack_dir / "nested"
        subdir.mkdir()
        (subdir / "nested-file.txt").write_text("should not appear")
        bundle_path = generate_bundle(str(pack_dir))
        with zipfile.ZipFile(bundle_path, "r") as zf:
            names = zf.namelist()
            assert "nested-file.txt" not in names
            assert "nested/nested-file.txt" not in names

    def test_files_sorted_in_zip(self, tmp_path):
        """Files in the ZIP should be sorted (from sorted(pack.iterdir()))."""
        pack_dir = tmp_path / "sorted-test"
        pack_dir.mkdir()
        for fname in ["c.txt", "a.txt", "b.txt"]:
            (pack_dir / fname).write_text(fname)
        manifest = {"schema_version": "1.0", "files": []}
        (pack_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        bundle_path = generate_bundle(str(pack_dir))
        with zipfile.ZipFile(bundle_path, "r") as zf:
            names = zf.namelist()
            # verify.py is appended last, so remove it for sort check
            pack_names = [n for n in names if n != "verify.py"]
            assert pack_names == sorted(pack_names)

    def test_file_content_preserved(self, tmp_path):
        """Content in the ZIP should match what was written."""
        pack_dir = self._make_pack(tmp_path)
        original = (pack_dir / "00-summary.md").read_text(encoding="utf-8")
        bundle_path = generate_bundle(str(pack_dir))
        with zipfile.ZipFile(bundle_path, "r") as zf:
            extracted = zf.read("00-summary.md").decode("utf-8")
            assert extracted == original


# ── _VERIFY_SCRIPT ───────────────────────────────────────────────────


class TestVerifyScript:
    """Tests for the embedded verify.py script."""

    def test_is_valid_python(self):
        """The embedded script should compile without syntax errors."""
        compile(_VERIFY_SCRIPT, "verify.py", "exec")

    def test_contains_sha256(self):
        assert "sha256" in _VERIFY_SCRIPT

    def test_contains_main_guard(self):
        assert '__name__ == "__main__"' in _VERIFY_SCRIPT

    def test_contains_manifest_loading(self):
        assert "manifest.json" in _VERIFY_SCRIPT

    def test_handles_path_traversal(self):
        """The verify script skips paths containing '..'."""
        assert '".."' in _VERIFY_SCRIPT or "'..' in" in _VERIFY_SCRIPT


# ── generate_evidence_pack (integration with mocks) ──────────────────


class TestGenerateEvidencePack:
    """Tests for the top-level generate_evidence_pack function.

    All sub-module calls (scan_files, assess_compliance, etc.) are mocked
    so these tests exercise pack assembly, not the underlying scanners.
    """

    def _mock_scan_files(self, *args, **kwargs):
        return [
            {
                "file": "model.py",
                "line": 10,
                "pattern": "import torch",
                "tier": "high_risk",
                "category": "ml_framework",
            },
            {
                "file": "filter.py",
                "line": 5,
                "pattern": "profiling_score",
                "tier": "prohibited",
                "category": "social_scoring",
            },
        ]

    def _mock_assess_compliance(self, *args, **kwargs):
        return {
            "overall_score": 55,
            "highest_risk": "prohibited",
            "articles": {
                "5": {"title": "Prohibited Practices", "score": 0, "status": "fail"},
                "9": {"title": "Risk Management", "score": 70, "status": "partial"},
            },
        }

    def _mock_scan_project(self, *args, **kwargs):
        return {
            "ai_files": ["model.py"],
            "model_files": [],
            "highest_risk": "high_risk",
            "patterns": [],
        }

    def _mock_generate_annex_iv(self, *args, **kwargs):
        return "# Annex IV Draft\n\nGenerated documentation."

    def _mock_generate_plan(self, findings, gap, project_name="project"):
        return {
            "project": project_name,
            "generated_at": "2026-05-01T12:00:00+00:00",
            "total_tasks": 2,
            "tasks": [
                {"title": "Address prohibited practice", "effort_hours": [4, 8], "priority": "P0"},
                {"title": "Improve risk management", "effort_hours": [2, 4], "priority": "P1"},
            ],
        }

    def _mock_format_plan_text(self, plan):
        return f"# Remediation Plan \u2014 {plan['project']}\nTasks: {plan['total_tasks']}"

    def _apply_mocks(self):
        """Return a dict of patch targets for use in with statements."""
        return {
            "report.scan_files": self._mock_scan_files,
            "compliance_check.assess_compliance": self._mock_assess_compliance,
            "generate_documentation.scan_project": self._mock_scan_project,
            "generate_documentation.generate_annex_iv": self._mock_generate_annex_iv,
            "remediation_plan.generate_plan": self._mock_generate_plan,
            "remediation_plan.format_plan_text": self._mock_format_plan_text,
        }

    def _run_with_mocks(self, tmp_path, project_name=None, **kwargs):
        project_dir = tmp_path / "fake-project"
        project_dir.mkdir()
        (project_dir / "model.py").write_text("import torch")
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        mocks = self._apply_mocks()
        with patch.dict("sys.modules", {
            "report": MagicMock(scan_files=mocks["report.scan_files"]),
            "compliance_check": MagicMock(assess_compliance=mocks["compliance_check.assess_compliance"]),
            "generate_documentation": MagicMock(
                scan_project=mocks["generate_documentation.scan_project"],
                generate_annex_iv=mocks["generate_documentation.generate_annex_iv"],
            ),
            "remediation_plan": MagicMock(
                generate_plan=mocks["remediation_plan.generate_plan"],
                format_plan_text=mocks["remediation_plan.format_plan_text"],
            ),
            "dependency_scan": MagicMock(
                scan_dependencies=lambda *a, **kw: {"dependencies": [], "score": 100},
            ),
            "log_event": MagicMock(
                query_events=lambda **kw: [{"event": "test"}],
                verify_chain=lambda: (True, "Chain valid"),
            ),
        }):
            result = generate_evidence_pack(
                str(project_dir),
                output_dir=str(output_dir),
                project_name=project_name,
                **kwargs,
            )
        return result, output_dir

    def test_returns_dict(self, tmp_path):
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        assert isinstance(result, dict)

    def test_return_keys(self, tmp_path):
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        assert "pack_dirname" in result
        assert "pack_path" in result
        assert "manifest" in result

    def test_pack_dirname_format(self, tmp_path):
        result, _ = self._run_with_mocks(tmp_path, project_name="myproject")
        dirname = result["pack_dirname"]
        assert dirname.startswith("evidence-pack-myproject-")
        # Should contain a date component
        assert "2026" in dirname or "202" in dirname

    def test_pack_directory_created(self, tmp_path):
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        assert Path(result["pack_path"]).is_dir()

    def test_manifest_written(self, tmp_path):
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        manifest_path = Path(result["pack_path"]) / "manifest.json"
        assert manifest_path.exists()

    def test_manifest_schema_version(self, tmp_path):
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        manifest = result["manifest"]
        assert manifest["schema_version"] == "1.0"

    def test_manifest_regula_version(self, tmp_path):
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        manifest = result["manifest"]
        assert manifest["regula_version"] == VERSION

    def test_manifest_has_project(self, tmp_path):
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        manifest = result["manifest"]
        assert manifest["project"] == "test-proj"

    def test_manifest_has_generated_at(self, tmp_path):
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        manifest = result["manifest"]
        assert "generated_at" in manifest
        # Should be ISO format
        datetime.fromisoformat(manifest["generated_at"])

    def test_manifest_has_project_path(self, tmp_path):
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        manifest = result["manifest"]
        assert "project_path" in manifest
        assert "fake-project" in manifest["project_path"]

    def test_manifest_files_list(self, tmp_path):
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        manifest = result["manifest"]
        files = manifest["files"]
        assert isinstance(files, list)
        assert len(files) > 0

    def test_manifest_file_entries_structure(self, tmp_path):
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        for entry in result["manifest"]["files"]:
            assert "filename" in entry
            assert "sha256" in entry
            assert "size_bytes" in entry
            assert isinstance(entry["sha256"], str)
            assert len(entry["sha256"]) == 64  # SHA-256 hex length
            assert isinstance(entry["size_bytes"], int)

    def test_expected_files_created(self, tmp_path):
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        pack_path = Path(result["pack_path"])
        expected = [
            "00-summary.md",
            "01-scan-results.json",
            "02-gap-assessment.json",
            "03-annex-iv-draft.md",
            "04-dependency-report.json",
            "05-audit-trail.json",
            "06-resolvable-facts.md",
            "07-risk-decisions.json",
            "README.md",
            "manifest.json",
        ]
        for fname in expected:
            assert (pack_path / fname).exists(), f"Missing: {fname}"

    def test_scan_results_valid_json(self, tmp_path):
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        pack_path = Path(result["pack_path"])
        data = json.loads((pack_path / "01-scan-results.json").read_text(encoding="utf-8"))
        assert isinstance(data, list)
        assert len(data) == 2

    def test_gap_assessment_valid_json(self, tmp_path):
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        pack_path = Path(result["pack_path"])
        data = json.loads((pack_path / "02-gap-assessment.json").read_text(encoding="utf-8"))
        assert data["decision"]["result_type"] == "insufficient_information"
        assert data["evidence"]["article_observations"] == {}
        assert "overall_score" not in data

    def test_annex_iv_content(self, tmp_path):
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        pack_path = Path(result["pack_path"])
        content = (pack_path / "03-annex-iv-draft.md").read_text(encoding="utf-8")
        assert "Annex IV" in content

    def test_remediation_plan_content(self, tmp_path):
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        pack_path = Path(result["pack_path"])
        content = (pack_path / "06-resolvable-facts.md").read_text(encoding="utf-8")
        assert "Facts required" in content
        assert "provenance" in content

    def test_risk_decisions_structure(self, tmp_path):
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        pack_path = Path(result["pack_path"])
        data = json.loads((pack_path / "07-risk-decisions.json").read_text(encoding="utf-8"))
        assert data["schema_version"] == "1.0"
        assert "suppressed_findings" in data
        assert "accepted_risks" in data
        assert "summary" in data

    def test_risk_decisions_counts(self, tmp_path):
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        pack_path = Path(result["pack_path"])
        data = json.loads((pack_path / "07-risk-decisions.json").read_text(encoding="utf-8"))
        # No risk_decision fields in our mock findings
        assert data["summary"]["total_suppressed"] == 0
        assert data["summary"]["total_accepted"] == 0
        assert data["summary"]["accepted_overdue"] == 0

    def test_manifest_hashes_match_files(self, tmp_path):
        """Every hash in the manifest should match the actual file content."""
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        pack_path = Path(result["pack_path"])
        for entry in result["manifest"]["files"]:
            fpath = pack_path / entry["filename"]
            content = fpath.read_text(encoding="utf-8")
            actual_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            assert actual_hash == entry["sha256"], (
                f"Hash mismatch for {entry['filename']}: "
                f"manifest={entry['sha256']}, actual={actual_hash}"
            )

    def test_manifest_sizes_match_files(self, tmp_path):
        """Every size in the manifest should match the actual file size."""
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        pack_path = Path(result["pack_path"])
        for entry in result["manifest"]["files"]:
            fpath = pack_path / entry["filename"]
            content = fpath.read_text(encoding="utf-8")
            actual_size = len(content.encode("utf-8"))
            assert actual_size == entry["size_bytes"], (
                f"Size mismatch for {entry['filename']}: "
                f"manifest={entry['size_bytes']}, actual={actual_size}"
            )

    def test_manifest_json_readable(self, tmp_path):
        """The manifest.json on disk should be valid JSON."""
        result, _ = self._run_with_mocks(tmp_path, project_name="test-proj")
        pack_path = Path(result["pack_path"])
        manifest_on_disk = json.loads(
            (pack_path / "manifest.json").read_text(encoding="utf-8")
        )
        assert manifest_on_disk["schema_version"] == "1.0"


# ── Path sanitisation ────────────────────────────────────────────────


class TestPathSanitisation:
    """Tests for project name sanitisation in generate_evidence_pack."""

    def _run_with_name(self, tmp_path, project_name):
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        output_dir = tmp_path / "out"
        output_dir.mkdir()

        with patch.dict("sys.modules", {
            "report": MagicMock(scan_files=lambda *a, **kw: []),
            "compliance_check": MagicMock(assess_compliance=lambda *a, **kw: {
                "overall_score": 0, "highest_risk": "minimal_risk", "articles": {},
            }),
            "generate_documentation": MagicMock(
                scan_project=lambda *a, **kw: {
                    "ai_files": [], "model_files": [],
                    "highest_risk": "minimal_risk", "patterns": [],
                },
                generate_annex_iv=lambda *a, **kw: "# Annex IV",
            ),
            "remediation_plan": MagicMock(
                generate_plan=lambda *a, **kw: {
                    "project": "proj", "generated_at": "now",
                    "total_tasks": 0, "tasks": [],
                },
                format_plan_text=lambda *a, **kw: "# Plan",
            ),
        }):
            result = generate_evidence_pack(
                str(project_dir),
                output_dir=str(output_dir),
                project_name=project_name,
            )
        return result

    def test_dots_sanitised(self, tmp_path):
        result = self._run_with_name(tmp_path, "../../../etc/passwd")
        dirname = result["pack_dirname"]
        assert ".." not in dirname
        assert "/" not in dirname

    def test_slashes_sanitised(self, tmp_path):
        result = self._run_with_name(tmp_path, "my/project/name")
        dirname = result["pack_dirname"]
        assert "/" not in dirname

    def test_spaces_sanitised(self, tmp_path):
        result = self._run_with_name(tmp_path, "my project name")
        dirname = result["pack_dirname"]
        assert " " not in dirname

    def test_special_chars_sanitised(self, tmp_path):
        result = self._run_with_name(tmp_path, "proj<>:\"?*|name")
        dirname = result["pack_dirname"]
        # Only alphanumeric, underscore, hyphen allowed
        name_part = dirname.replace("evidence-pack-", "").rsplit("-", 3)[0]
        import re
        assert re.match(r'^[a-zA-Z0-9_\-]+$', name_part)

    def test_clean_name_unchanged(self, tmp_path):
        result = self._run_with_name(tmp_path, "my-clean-project_v2")
        assert "my-clean-project_v2" in result["pack_dirname"]

    def test_default_name_from_directory(self, tmp_path):
        """When project_name is None, use directory name."""
        result = self._run_with_name(tmp_path, None)
        # The project dir is named "proj"
        assert "proj" in result["pack_dirname"]


# ── Optional sections ────────────────────────────────────────────────


class TestOptionalSections:
    """Tests for optional evidence pack sections (dependency, audit, runtime)."""

    def _base_mocks(self):
        return {
            "report": MagicMock(scan_files=lambda *a, **kw: []),
            "compliance_check": MagicMock(assess_compliance=lambda *a, **kw: {
                "overall_score": 0, "highest_risk": "minimal_risk", "articles": {},
            }),
            "generate_documentation": MagicMock(
                scan_project=lambda *a, **kw: {
                    "ai_files": [], "model_files": [],
                    "highest_risk": "minimal_risk", "patterns": [],
                },
                generate_annex_iv=lambda *a, **kw: "# Annex IV",
            ),
            "remediation_plan": MagicMock(
                generate_plan=lambda *a, **kw: {
                    "project": "proj", "generated_at": "now",
                    "total_tasks": 0, "tasks": [],
                },
                format_plan_text=lambda *a, **kw: "# Plan",
            ),
        }

    def test_dependency_scan_skipped_on_error(self, tmp_path):
        """If scan_dependencies raises OSError, section 04 is skipped."""
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        output_dir = tmp_path / "out"
        output_dir.mkdir()

        mocks = self._base_mocks()
        dep_mod = MagicMock()
        dep_mod.scan_dependencies = MagicMock(side_effect=OSError("scan failed"))
        mocks["dependency_scan"] = dep_mod
        with patch.dict("sys.modules", mocks):
            result = generate_evidence_pack(
                str(project_dir), output_dir=str(output_dir),
                project_name="test",
            )
        pack_path = Path(result["pack_path"])
        assert not (pack_path / "04-dependency-report.json").exists()

    def test_audit_trail_skipped_on_error(self, tmp_path):
        """If query_events raises ValueError, section 05 is skipped."""
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        output_dir = tmp_path / "out"
        output_dir.mkdir()

        mocks = self._base_mocks()
        log_mod = MagicMock()
        log_mod.collect_audit_trail = MagicMock(side_effect=ValueError("bad data"))
        mocks["log_event"] = log_mod
        with patch.dict("sys.modules", mocks):
            result = generate_evidence_pack(
                str(project_dir), output_dir=str(output_dir),
                project_name="test",
            )
        pack_path = Path(result["pack_path"])
        assert not (pack_path / "05-audit-trail.json").exists()

    def test_runtime_monitor_skipped_without_kwarg(self, tmp_path):
        """Section 08 is only generated when runtime_system_id is passed."""
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        output_dir = tmp_path / "out"
        output_dir.mkdir()

        mocks = self._base_mocks()
        with patch.dict("sys.modules", mocks):
            result = generate_evidence_pack(
                str(project_dir), output_dir=str(output_dir),
                project_name="test",
            )
        pack_path = Path(result["pack_path"])
        assert not (pack_path / "08-runtime-monitor.json").exists()

    def test_dependency_scan_included_when_available(self, tmp_path):
        """Section 04 is written when dependency_scan is importable."""
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        output_dir = tmp_path / "out"
        output_dir.mkdir()

        mocks = self._base_mocks()
        mocks["dependency_scan"] = MagicMock(
            scan_dependencies=lambda *a, **kw: {"dependencies": [], "score": 100},
        )
        with patch.dict("sys.modules", mocks):
            result = generate_evidence_pack(
                str(project_dir), output_dir=str(output_dir),
                project_name="test",
            )
        pack_path = Path(result["pack_path"])
        assert (pack_path / "04-dependency-report.json").exists()

    def test_audit_trail_included_when_available(self, tmp_path):
        """Section 05 is written when log_event is importable."""
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        output_dir = tmp_path / "out"
        output_dir.mkdir()

        mocks = self._base_mocks()
        mocks["log_event"] = MagicMock(
            collect_audit_trail=lambda project_path, **kw: {
                "scope": "project",
                "project": "test",
                "project_slug": "test-00000000",
                "chain_valid": True,
                "chain_message": "Chain valid",
                "event_count": 1,
                "limit_reached": False,
                "scope_note": "test",
                "events": [{"event": "test"}],
            },
        )
        with patch.dict("sys.modules", mocks):
            result = generate_evidence_pack(
                str(project_dir), output_dir=str(output_dir),
                project_name="test",
            )
        pack_path = Path(result["pack_path"])
        assert (pack_path / "05-audit-trail.json").exists()
        data = json.loads((pack_path / "05-audit-trail.json").read_text(encoding="utf-8"))
        assert data["chain_valid"] is True
        assert data["event_count"] == 1


# ── Risk decisions with data ─────────────────────────────────────────


class TestRiskDecisions:
    """Tests for section 07 risk decisions with populated data."""

    def test_suppressed_findings_collected(self, tmp_path):
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        output_dir = tmp_path / "out"
        output_dir.mkdir()

        findings_with_decisions = [
            {
                "tier": "high_risk",
                "risk_decision": {"type": "ignore", "reason": "false positive"},
            },
            {
                "tier": "limited_risk",
                "risk_decision": {"type": "accept", "reason": "low impact", "overdue": False},
            },
            {
                "tier": "high_risk",
                "risk_decision": {"type": "accept", "reason": "planned fix", "overdue": True},
            },
            {"tier": "minimal_risk"},  # no decision
        ]

        with patch.dict("sys.modules", {
            "report": MagicMock(scan_files=lambda *a, **kw: findings_with_decisions),
            "compliance_check": MagicMock(assess_compliance=lambda *a, **kw: {
                "overall_score": 50, "highest_risk": "high_risk", "articles": {},
            }),
            "generate_documentation": MagicMock(
                scan_project=lambda *a, **kw: {
                    "ai_files": [], "model_files": [],
                    "highest_risk": "high_risk", "patterns": [],
                },
                generate_annex_iv=lambda *a, **kw: "# Annex IV",
            ),
            "remediation_plan": MagicMock(
                generate_plan=lambda *a, **kw: {
                    "project": "test", "generated_at": "now",
                    "total_tasks": 0, "tasks": [],
                },
                format_plan_text=lambda *a, **kw: "# Plan",
            ),
        }):
            result = generate_evidence_pack(
                str(project_dir), output_dir=str(output_dir),
                project_name="test",
            )

        pack_path = Path(result["pack_path"])
        data = json.loads((pack_path / "07-risk-decisions.json").read_text(encoding="utf-8"))
        assert data["summary"]["total_suppressed"] == 1
        assert data["summary"]["total_accepted"] == 2
        assert data["summary"]["accepted_overdue"] == 1
        assert len(data["suppressed_findings"]) == 1
        assert len(data["accepted_risks"]) == 2


# ── Edge cases ───────────────────────────────────────────────────────


class TestEdgeCases:
    """Edge case tests."""

    def test_output_dir_created_if_missing(self, tmp_path):
        """output_dir with parents=True should create intermediate dirs."""
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        output_dir = tmp_path / "deep" / "nested" / "output"

        with patch.dict("sys.modules", {
            "report": MagicMock(scan_files=lambda *a, **kw: []),
            "compliance_check": MagicMock(assess_compliance=lambda *a, **kw: {
                "overall_score": 0, "highest_risk": "minimal_risk", "articles": {},
            }),
            "generate_documentation": MagicMock(
                scan_project=lambda *a, **kw: {
                    "ai_files": [], "model_files": [],
                    "highest_risk": "minimal_risk", "patterns": [],
                },
                generate_annex_iv=lambda *a, **kw: "# Annex IV",
            ),
            "remediation_plan": MagicMock(
                generate_plan=lambda *a, **kw: {
                    "project": "proj", "generated_at": "now",
                    "total_tasks": 0, "tasks": [],
                },
                format_plan_text=lambda *a, **kw: "# Plan",
            ),
        }):
            result = generate_evidence_pack(
                str(project_dir), output_dir=str(output_dir),
                project_name="test",
            )
        assert Path(result["pack_path"]).is_dir()

    def test_idempotent_rerun(self, tmp_path):
        """Running twice to the same output_dir should not fail."""
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        output_dir = tmp_path / "out"
        output_dir.mkdir()

        mocks = {
            "report": MagicMock(scan_files=lambda *a, **kw: []),
            "compliance_check": MagicMock(assess_compliance=lambda *a, **kw: {
                "overall_score": 0, "highest_risk": "minimal_risk", "articles": {},
            }),
            "generate_documentation": MagicMock(
                scan_project=lambda *a, **kw: {
                    "ai_files": [], "model_files": [],
                    "highest_risk": "minimal_risk", "patterns": [],
                },
                generate_annex_iv=lambda *a, **kw: "# Annex IV",
            ),
            "remediation_plan": MagicMock(
                generate_plan=lambda *a, **kw: {
                    "project": "proj", "generated_at": "now",
                    "total_tasks": 0, "tasks": [],
                },
                format_plan_text=lambda *a, **kw: "# Plan",
            ),
        }

        with patch.dict("sys.modules", mocks):
            result1 = generate_evidence_pack(
                str(project_dir), output_dir=str(output_dir),
                project_name="test",
            )
        with patch.dict("sys.modules", mocks):
            result2 = generate_evidence_pack(
                str(project_dir), output_dir=str(output_dir),
                project_name="test",
            )
        # Both should succeed and produce the same dirname
        assert result1["pack_dirname"] == result2["pack_dirname"]

    def test_empty_findings(self, tmp_path):
        """An empty scan should still produce a valid pack."""
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        output_dir = tmp_path / "out"
        output_dir.mkdir()

        with patch.dict("sys.modules", {
            "report": MagicMock(scan_files=lambda *a, **kw: []),
            "compliance_check": MagicMock(assess_compliance=lambda *a, **kw: {
                "overall_score": 100, "highest_risk": "minimal_risk", "articles": {},
            }),
            "generate_documentation": MagicMock(
                scan_project=lambda *a, **kw: {
                    "ai_files": [], "model_files": [],
                    "highest_risk": "minimal_risk", "patterns": [],
                },
                generate_annex_iv=lambda *a, **kw: "# Annex IV\nNo AI detected.",
            ),
            "remediation_plan": MagicMock(
                generate_plan=lambda *a, **kw: {
                    "project": "clean", "generated_at": "now",
                    "total_tasks": 0, "tasks": [],
                },
                format_plan_text=lambda *a, **kw: "# No tasks needed.",
            ),
        }):
            result = generate_evidence_pack(
                str(project_dir), output_dir=str(output_dir),
                project_name="clean",
            )
        pack_path = Path(result["pack_path"])
        assert (pack_path / "manifest.json").exists()
        manifest = json.loads((pack_path / "manifest.json").read_text(encoding="utf-8"))
        assert manifest["schema_version"] == "1.0"
        # Scan results should be empty list
        scan = json.loads((pack_path / "01-scan-results.json").read_text(encoding="utf-8"))
        assert scan == []
