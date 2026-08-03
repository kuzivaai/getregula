"""Mutation and legitimate-negative controls for delivery-derived surfaces."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tarfile
import zipfile
import io
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import public_surface_inventory as psi


REPO = Path(__file__).resolve().parent.parent


def _site_root(tmp_path: Path) -> tuple[Path, set[str]]:
    workflow = tmp_path / ".github/workflows/pages.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text("uses: actions/upload-pages-artifact@v5\nwith:\n  path: site\n", encoding="utf-8")
    (tmp_path / "site").mkdir()
    files = {".github/workflows/pages.yml"}
    return tmp_path, files


@pytest.mark.parametrize("rel", [
    "site/new.html", "site/guides/new.html", "site/blog/new.html",
    "site/course/new.html", "site/regions/new.html", "site/locales/fr.html",
    "site/sitemap-new.xml", "site/feed.xml", "site/llms-extra.txt",
])
def test_new_web_delivery_candidates_are_discovered(tmp_path, rel):
    root, files = _site_root(tmp_path)
    path = root / rel; path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("public", encoding="utf-8"); files.add(rel)
    rows = psi.website_records(root, files)
    assert any(row["source"] == rel and row["classification"] == "active_product" for row in rows)


def test_readme_link_addition_and_rename_are_bidirectional(tmp_path):
    (tmp_path / "README.md").write_text("[Guide](docs/guide.md)\n", encoding="utf-8")
    (tmp_path / "docs").mkdir(); (tmp_path / "docs/guide.md").write_text("guide", encoding="utf-8")
    files = {"README.md", "docs/guide.md"}
    assert {r["source"] for r in psi.docs_records(tmp_path, files)} == files
    (tmp_path / "README.md").write_text("[Guide](docs/renamed.md)\n", encoding="utf-8")
    assert {r["source"] for r in psi.docs_records(tmp_path, files)} == {"README.md"}


def test_unlinked_internal_note_and_internal_python_are_legitimate_negatives(tmp_path):
    (tmp_path / "README.md").write_text("public", encoding="utf-8")
    (tmp_path / "notes.md").write_text("internal", encoding="utf-8")
    assert {r["source"] for r in psi.docs_records(tmp_path, {"README.md", "notes.md"})} == {"README.md"}
    assert not any(r["source"] == "scripts/internal.py" for r in psi.discover()["records"])


def test_binary_asset_is_non_claim_asset(tmp_path):
    root, files = _site_root(tmp_path)
    (root / "site/image.png").write_bytes(b"PNG")
    rows = psi.website_records(root, files | {"site/image.png"})
    row = next(r for r in rows if r["source"] == "site/image.png")
    assert row["classification"] == "non_claim_asset" and not row["claim_capable"]


def test_cli_registry_mutation_is_detected(monkeypatch):
    parser = argparse.ArgumentParser(prog="regula")
    commands = parser.add_subparsers(dest="command")
    child = commands.add_parser("new-command", help="new help")
    child.add_argument("--new-option", help="new option help")
    monkeypatch.setattr(psi, "_real_parser", lambda root: parser)
    destinations = {r["destination"] for r in psi.cli_records(REPO, set())}
    assert "regula new-command" in destinations
    assert "regula new-command --new-option" in destinations


def test_cli_parser_failure_fails_closed(monkeypatch):
    monkeypatch.setattr(psi, "_real_parser", lambda root: (_ for _ in ()).throw(psi.DiscoveryError("broken")))
    with pytest.raises(psi.DiscoveryError, match="broken"):
        psi.cli_records(REPO, set())


def test_mcp_registry_mutation_and_order_control(monkeypatch):
    module = __import__("mcp_server")
    original = module.TOOLS
    monkeypatch.setattr(module, "TOOLS", original + [{"name": "zz_new", "description": "new", "inputSchema": {}}])
    assert any(r["destination"] == "tools/list:zz_new" for r in psi.mcp_records(REPO, set()))
    monkeypatch.setattr(module, "TOOLS", list(reversed(original)))
    with pytest.raises(psi.DiscoveryError, match="deterministic"):
        psi.mcp_records(REPO, set())


def test_action_input_output_and_metadata_descriptions_are_discovered(tmp_path):
    action = tmp_path / "action.yml"
    action.write_text("name: X\ndescription: Y\ninputs:\n  new:\n    description: Input claim\noutputs:\n  result:\n    description: Output claim\n", encoding="utf-8")
    rows = psi.action_records(tmp_path, {"action.yml"})
    reasons = {r["reason"] for r in rows}
    assert "description: Input claim" in reasons and "description: Output claim" in reasons


def test_package_summary_and_long_description_are_derived(tmp_path):
    (tmp_path / "README-new.md").write_text("new long description", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname="x"\nversion="1"\ndescription="changed summary"\nreadme="README-new.md"\n', encoding="utf-8")
    rows = psi.package_records(tmp_path, {"pyproject.toml", "README-new.md"})
    assert {r["source"] for r in rows} == {"pyproject.toml#project.description", "README-new.md"}


@pytest.mark.parametrize("readme_value", ['"README.md"', '{file = "README.md", content-type = "text/markdown"}'])
def test_package_readme_discovery_supports_python_310(tmp_path, monkeypatch, readme_value):
    (tmp_path / "README.md").write_text("long description", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        f'[project]\nname="x"\nversion="1"\ndescription="Summary"\nreadme={readme_value}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(psi, "tomllib", None)
    rows = psi.package_records(tmp_path, {"pyproject.toml", "README.md"})
    assert any(row["source"] == "README.md" for row in rows)


def test_wheel_metadata_and_sdist_pkg_info_are_verified(tmp_path):
    root = tmp_path / "repo"; dist = root / "dist"; dist.mkdir(parents=True)
    (root / "README.md").write_text("Long description\n", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        '[project]\nname="x"\nversion="1"\ndescription="Summary"\nreadme="README.md"\n', encoding="utf-8")
    metadata = b"Metadata-Version: 2.4\nName: x\nVersion: 1\nSummary: Summary\n\nLong description\n"
    with zipfile.ZipFile(dist / "x-1-py3-none-any.whl", "w") as archive:
        archive.writestr("x-1.dist-info/METADATA", metadata)
    with tarfile.open(dist / "x-1.tar.gz", "w:gz") as archive:
        info = tarfile.TarInfo("x-1/PKG-INFO"); info.size = len(metadata)
        archive.addfile(info, io.BytesIO(metadata))
    psi.verify_package_artifacts(root, dist)
    (root / "README.md").write_text("Changed\n", encoding="utf-8")
    with pytest.raises(psi.DiscoveryError, match="long description"):
        psi.verify_package_artifacts(root, dist)


def test_stale_duplicate_and_invalid_policy_dispositions_fail(tmp_path):
    (tmp_path / "data").mkdir()
    row = psi.record("website", "site/x.html", "/x.html", "test", "web-page", True, "active_product", "test")
    for dispositions, match in [
        ([{"source": "missing", "classification": "historical_record", "reason": "x"}], "stale"),
        ([{"source": "site/x.html", "classification": "historical_record", "reason": "x"}] * 2, "duplicate"),
        ([{"source": "site/x.html", "classification": "active_product", "reason": "x"}], "invalid"),
    ]:
        (tmp_path / "data/public_surface_policy.json").write_text(json.dumps({"dispositions": dispositions}), encoding="utf-8")
        with pytest.raises(psi.DiscoveryError, match=match): psi.apply_policy(tmp_path, [row.copy()])


def test_missing_policy_disposition_fails(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/public_surface_policy.json").write_text('{"dispositions": []}', encoding="utf-8")
    row = psi.record("repository_docs", "CHANGELOG.md", "public", "link", "document", True,
                     "needs_policy", "requires disposition")
    with pytest.raises(psi.DiscoveryError, match="missing policy disposition"):
        psi.apply_policy(tmp_path, [row])


def test_duplicate_stable_id_control():
    payload = psi.discover()
    ids = [r["stable_id"] for r in payload["records"]]
    assert len(ids) == len(set(ids))
    clone = payload["records"][0].copy()
    assert clone["stable_id"] in ids


def test_git_unavailable_and_ignored_or_untracked_inputs_fail_safe(monkeypatch, tmp_path):
    def unavailable(*args, **kwargs): raise OSError("missing git")
    monkeypatch.setattr(subprocess, "run", unavailable)
    with pytest.raises(psi.DiscoveryError, match="git unavailable"): psi.tracked(tmp_path)
    root, files = _site_root(tmp_path)
    (root / "site/untracked.html").write_text("not shipped", encoding="utf-8")
    assert not any(r["source"] == "site/untracked.html" for r in psi.website_records(root, files))


def test_historical_record_and_valid_narrow_exclusion():
    payload = psi.discover()
    excluded = next(r for r in payload["records"] if r["source"] == "site/assets/demo/landing-page.png")
    assert excluded["classification"] == "non_claim_asset"
    historical = psi.record("repository_docs", "CHANGELOG.md", "public", "link", "document", True,
                            "historical_record", "version history is not current product positioning")
    assert historical["classification"] == "historical_record"


def test_generated_inventory_and_report_are_current():
    assert psi.main(["--check"]) == 0
