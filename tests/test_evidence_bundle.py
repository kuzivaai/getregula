"""Tests for self-verifying evidence bundle generation."""
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))


def test_bundle_creates_zip(tmp_path):
    from evidence_pack import generate_bundle
    pack_dir = tmp_path / "evidence-pack-test-2026-04-18"
    pack_dir.mkdir()
    (pack_dir / "00-summary.md").write_text("# Summary\nTest.")
    manifest = {
        "regula_version": "1.7.0",
        "generated_at": "2026-04-18T00:00:00Z",
        "project": "test",
        "project_path": "/tmp/test",
        "files": [{"filename": "00-summary.md", "sha256": "abc123", "size_bytes": 16}],
    }
    (pack_dir / "manifest.json").write_text(json.dumps(manifest))
    bundle_path = generate_bundle(str(pack_dir))
    assert Path(bundle_path).exists()
    assert bundle_path.endswith(".regula-evidence.zip")


def test_bundle_contains_verify_script(tmp_path):
    from evidence_pack import generate_bundle
    pack_dir = tmp_path / "evidence-pack-test-2026-04-18"
    pack_dir.mkdir()
    (pack_dir / "00-summary.md").write_text("# Summary\nTest.")
    manifest = {
        "regula_version": "1.7.0",
        "generated_at": "2026-04-18T00:00:00Z",
        "project": "test",
        "project_path": "/tmp/test",
        "files": [{"filename": "00-summary.md", "sha256": "abc123", "size_bytes": 16}],
    }
    (pack_dir / "manifest.json").write_text(json.dumps(manifest))
    bundle_path = generate_bundle(str(pack_dir))
    with zipfile.ZipFile(bundle_path, "r") as zf:
        assert "verify.py" in zf.namelist()


def test_bundle_contains_all_pack_files(tmp_path):
    from evidence_pack import generate_bundle
    pack_dir = tmp_path / "evidence-pack-test-2026-04-18"
    pack_dir.mkdir()
    (pack_dir / "00-summary.md").write_text("# Summary")
    (pack_dir / "01-scan-results.json").write_text("{}")
    manifest = {
        "regula_version": "1.7.0",
        "generated_at": "2026-04-18T00:00:00Z",
        "project": "test",
        "project_path": "/tmp/test",
        "files": [
            {"filename": "00-summary.md", "sha256": "a", "size_bytes": 9},
            {"filename": "01-scan-results.json", "sha256": "b", "size_bytes": 2},
        ],
    }
    (pack_dir / "manifest.json").write_text(json.dumps(manifest))
    bundle_path = generate_bundle(str(pack_dir))
    with zipfile.ZipFile(bundle_path, "r") as zf:
        names = zf.namelist()
        assert "00-summary.md" in names
        assert "01-scan-results.json" in names
        assert "manifest.json" in names


def test_bundle_verify_script_runs(tmp_path):
    from evidence_pack import generate_bundle
    pack_dir = tmp_path / "evidence-pack-test-2026-04-18"
    pack_dir.mkdir()
    content = "# Summary\nTest content."
    sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
    (pack_dir / "00-summary.md").write_text(content)
    manifest = {
        "regula_version": "1.7.0",
        "generated_at": "2026-04-18T00:00:00Z",
        "project": "test",
        "project_path": "/tmp/test",
        "files": [{"filename": "00-summary.md", "sha256": sha, "size_bytes": len(content.encode())}],
    }
    (pack_dir / "manifest.json").write_text(json.dumps(manifest))
    bundle_path = generate_bundle(str(pack_dir))
    extract_dir = tmp_path / "extracted"
    with zipfile.ZipFile(bundle_path, "r") as zf:
        zf.extractall(extract_dir)
    result = subprocess.run(
        [sys.executable, str(extract_dir / "verify.py")],
        capture_output=True, text=True, cwd=str(extract_dir),
    )
    assert result.returncode == 0, f"verify.py failed: {result.stderr}"
