"""Tests for Regula Evidence Format v1.

Covers:
- `regula conform` emits a manifest conforming to regula.manifest.v1.schema.json
- `regula verify` reads v1 manifests and returns success/failure correctly
- `regula verify --strict` fails on packs without `format=regula.evidence.v1`
- `regula verify --report` writes a regula.verify.v1.json report
- `regula conform --zip` emits a .regula.zip bundle that `verify` accepts
- Tampering with a pack file is caught by verify (MODIFIED status)
- Deleting a pack file is caught by verify (MISSING status)

Stdlib only.
"""
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(*args, check=False):
    return subprocess.run(
        [sys.executable, "-m", "scripts.cli", *args],
        capture_output=True, text=True, cwd=ROOT, check=check, timeout=90,
    )


def _generate_pack(tmp_path, name="cv-screening-app", zip_bundle=False):
    """Run `regula conform` on the fixture example, return (pack_dir, bundle_path|None)."""
    out_dir = tmp_path / "out"
    args = [
        "conform", "--project", "examples/cv-screening-app",
        "--output", str(out_dir), "--name", name,
    ]
    if zip_bundle:
        args.append("--zip")
    result = _run(*args)
    assert result.returncode == 0, f"conform failed: {result.stdout}\n{result.stderr}"

    # Find the pack dir — conform appends the date
    packs = list(out_dir.glob(f"conformity-evidence-{name}-*"))
    pack_dirs = [p for p in packs if p.is_dir()]
    assert len(pack_dirs) == 1, f"expected one pack dir, got: {packs}"
    pack_dir = pack_dirs[0]

    bundle = None
    if zip_bundle:
        bundles = list(out_dir.glob(f"conformity-evidence-{name}-*.regula.zip"))
        assert len(bundles) == 1, f"expected one bundle, got: {bundles}"
        bundle = bundles[0]

    return pack_dir, bundle


def test_conform_manifest_declares_v1_format(tmp_path):
    """The manifest.json emitted by `regula conform` MUST declare v1 format fields."""
    pack_dir, _ = _generate_pack(tmp_path)
    manifest = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))

    assert manifest["format"] == "regula.evidence.v1"
    assert re.match(r"^1\.\d+$", manifest["format_version"]), manifest["format_version"]
    assert manifest["hash_algorithm"] == "sha256"
    assert manifest["schema_uri"].endswith("regula.manifest.v1.schema.json")
    # Semver of Regula itself
    assert re.match(r"^\d+\.\d+\.\d+", manifest["regula_version"])
    # Required fields from spec §4.1
    for required in ("generated_at", "project", "project_directory", "files"):
        assert required in manifest, f"manifest missing required field {required!r}"


def test_conform_manifest_file_records_have_required_fields(tmp_path):
    """Every entry in manifest.files MUST have filename, sha256, size_bytes."""
    pack_dir, _ = _generate_pack(tmp_path)
    manifest = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["files"]) > 0
    for entry in manifest["files"]:
        assert "filename" in entry, f"file record missing filename: {entry}"
        assert re.match(r"^[a-f0-9]{64}$", entry["sha256"]), entry
        assert isinstance(entry["size_bytes"], int) and entry["size_bytes"] >= 0


def test_conform_manifest_validates_against_schema(tmp_path):
    """The manifest MUST validate against docs/spec/regula.manifest.v1.schema.json.

    Uses jsonschema if available; otherwise falls back to a minimal structural
    check (stdlib-only).
    """
    pack_dir, _ = _generate_pack(tmp_path)
    manifest = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "docs/spec/regula.manifest.v1.schema.json").read_text())

    try:
        import jsonschema
        jsonschema.validate(manifest, schema)
    except ImportError:
        # Minimal structural check when jsonschema is not installed
        for required in schema["required"]:
            assert required in manifest
        for entry in manifest["files"]:
            for required in schema["properties"]["files"]["items"]["required"]:
                assert required in entry


def test_verify_accepts_v1_pack_and_exits_zero(tmp_path):
    """`regula verify <pack_dir>` on a freshly-generated pack MUST exit 0."""
    pack_dir, _ = _generate_pack(tmp_path)
    result = _run("verify", str(pack_dir))
    assert result.returncode == 0, result.stdout
    assert "Pack integrity confirmed" in result.stdout


def test_verify_strict_mode_on_v1_pack_exits_zero(tmp_path):
    """Strict mode MUST pass for a conforming v1 pack."""
    pack_dir, _ = _generate_pack(tmp_path)
    result = _run("verify", str(pack_dir), "--strict")
    assert result.returncode == 0, result.stdout


def test_verify_strict_mode_rejects_v0_pack(tmp_path):
    """A pack without format=regula.evidence.v1 MUST be rejected under --strict."""
    pack_dir, _ = _generate_pack(tmp_path)
    manifest = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))
    manifest.pop("format", None)  # simulate a pre-v1 pack
    manifest.pop("format_version", None)
    (pack_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    result = _run("verify", str(pack_dir), "--strict")
    assert result.returncode == 2, f"expected exit 2, got {result.returncode}: {result.stdout}"
    assert "strict" in result.stdout.lower() or "does not declare" in result.stdout.lower()


def test_verify_non_strict_warns_on_v0_pack_but_succeeds(tmp_path):
    """Without --strict, a pre-v1 pack verifies with a warning printed."""
    pack_dir, _ = _generate_pack(tmp_path)
    # Strip format fields to simulate a pre-v1 pack, but file integrity stays intact
    manifest_file = pack_dir / "manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    manifest.pop("format", None)
    manifest.pop("format_version", None)
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    # Regenerate the one-line manifest hash? No — verify doesn't check the manifest itself
    # against itself; it reads file list and hashes each.

    result = _run("verify", str(pack_dir))
    assert result.returncode == 0, result.stdout
    assert "best-effort" in result.stdout.lower() or "warning" in result.stdout.lower() or "⚠" in result.stdout


def test_verify_catches_modified_file(tmp_path):
    """Tampering with any pack file MUST cause verify to return MODIFIED + exit 1."""
    pack_dir, _ = _generate_pack(tmp_path)
    target = pack_dir / "01-risk-classification" / "findings.json"
    target.write_text(target.read_text() + "\n# sneaky edit\n", encoding="utf-8")

    result = _run("verify", str(pack_dir))
    assert result.returncode == 1, f"expected exit 1 on tamper, got {result.returncode}"
    assert "MODIFIED" in result.stdout
    assert "integrity compromised" in result.stdout.lower() or "do not submit" in result.stdout.lower()


def test_verify_catches_missing_file(tmp_path):
    """Deleting a pack file MUST cause verify to return MISSING + exit 1."""
    pack_dir, _ = _generate_pack(tmp_path)
    target = pack_dir / "01-risk-classification" / "findings.json"
    target.unlink()

    result = _run("verify", str(pack_dir))
    assert result.returncode == 1
    assert "MISSING" in result.stdout


def test_verify_emits_v1_report(tmp_path):
    """`regula verify --report <path>` MUST write a regula.verify.v1.json report."""
    pack_dir, _ = _generate_pack(tmp_path)
    report_path = tmp_path / "verify-report.json"

    result = _run("verify", str(pack_dir), "--report", str(report_path))
    assert result.returncode == 0
    assert report_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["format"] == "regula.verify.v1"
    assert re.match(r"^1\.\d+$", report["format_version"])
    assert report["pack_format"] == "regula.evidence.v1"
    assert report["total"] == report["passed"]
    assert report["failed"] == 0
    assert all(r["status"] == "OK" for r in report["results"])


def test_conform_zip_emits_bundle_and_verify_accepts_it(tmp_path):
    """`regula conform --zip` writes a .regula.zip; verify accepts it directly."""
    pack_dir, bundle = _generate_pack(tmp_path, zip_bundle=True)
    assert bundle is not None
    assert bundle.suffix == ".zip"
    assert bundle.name.endswith(".regula.zip")

    # The zip should be a valid archive containing the pack directory at root
    with zipfile.ZipFile(bundle) as zf:
        names = zf.namelist()
        assert any(n.endswith("manifest.json") for n in names)
        assert any(n.endswith("00-assessment-summary.json") for n in names)

    # verify on the bundle directly
    result = _run("verify", str(bundle))
    assert result.returncode == 0, result.stdout
    assert "Pack integrity confirmed" in result.stdout


def test_verify_json_output_includes_format_metadata(tmp_path):
    """`regula verify --format json` MUST surface pack_format + verifier_version."""
    pack_dir, _ = _generate_pack(tmp_path)
    result = _run("verify", str(pack_dir), "--format", "json")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    data = payload.get("data", payload)
    assert data["pack_format"] == "regula.evidence.v1"
    assert data["verifier_version"]
    assert data["total"] == data["passed"]


def test_file_sha256s_are_computed_correctly(tmp_path):
    """Every sha256 in the manifest MUST match a direct hash of the pointed-at file."""
    pack_dir, _ = _generate_pack(tmp_path)
    manifest = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        target = pack_dir / entry["filename"]
        assert target.exists(), f"manifest lists missing file: {entry['filename']}"
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        assert digest == entry["sha256"], f"hash mismatch on {entry['filename']}"
