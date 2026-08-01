"""Class-wide controls for active high-consequence public claims."""
from __future__ import annotations

import json
import re
import subprocess
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTRACT = REPO / "data" / "public_claim_surfaces.json"

PROHIBITED = {
    "legal classification": re.compile(r"(?:classif(?:y|ies)(?!-ai-system\.html).*(?:system|snippet).*risk tier|classifies risk tier)", re.I),
    "compliance scan": re.compile(r"(?:compliance scanner|compliance issues|assess compliance gaps)", re.I),
    "obligation determination": re.compile(r"tells? you which obligations apply", re.I),
    "universal network": re.compile(r"(?:zero network calls|no API calls|no data leaves)", re.I),
    "DPA determination": re.compile(r"no DPA (?:is )?required", re.I),
    "auditor completeness": re.compile(r"auditor.ready|audit.ready", re.I),
    "universal reproducibility": re.compile(r"every (?:metric|number).*(?:reproduc|CI.enforced)", re.I),
    "unbounded runtime": re.compile(r"(?:in|under|takes?) (?:10|30) seconds", re.I),
    "zero security findings": re.compile(r"zero known security findings|0 known security findings", re.I),
}


def contract(root: Path = REPO) -> dict:
    return json.loads((root / "data/public_claim_surfaces.json").read_text(encoding="utf-8"))


def active_paths(root: Path = REPO) -> list[str]:
    return [row["path"] for row in contract(root)["active_surfaces"]]


def violations(root: Path = REPO) -> list[tuple[str, str]]:
    found = []
    for rel in active_paths(root):
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
        for claim_class, pattern in PROHIBITED.items():
            if pattern.search(text):
                found.append((rel, claim_class))
    return found


def test_contract_is_bidirectional_and_non_vacuous():
    rows = contract()["active_surfaces"]
    paths = [row["path"] for row in rows]
    assert len(paths) == len(set(paths)) and len(paths) >= 14
    assert all((REPO / rel).is_file() for rel in paths)
    discovered = {
        p.as_posix() for p in (
            Path("README.md"), Path("SECURITY.md"), Path("docs/TRUST.md"),
            Path("docs/MODEL_CARD.md"), Path("docs/what-regula-does-not-do.md"),
            Path("mcp-server.json"), Path("pyproject.toml"), Path("scripts/cli.py"),
            Path("scripts/cli_compliance.py"), Path("scripts/cli_scan.py"),
            Path("docs/QUICKSTART.md"), Path("site/index.html"), Path("site/about.html"),
            Path("site/assess/index.html"), Path("site/pricing.html"),
            Path("site/sample-report.html"), Path("site/blog/blog-classify-ai-system.html"),
            Path("site/llms.txt"), Path("site/llms-full.txt"),
            Path("site/regions/uae.html"), Path("site/locales/de.html"),
            Path("site/locales/pt-br.html"))}
    assert set(paths) == discovered


def test_active_surfaces_do_not_publish_prohibited_claims():
    assert violations() == []


def test_required_limitation_concepts_are_translated():
    required = {
        "site/index.html": ("does not determine legal classification", "human review"),
        "site/locales/de.html": ("bestimmt weder die rechtliche Einstufung", "menschliche Prüfung"),
        "site/locales/pt-br.html": ("não determina a classificação jurídica", "revisão humana"),
    }
    for rel, phrases in required.items():
        text = (REPO / rel).read_text(encoding="utf-8", errors="replace").lower()
        assert all(phrase.lower() in text for phrase in phrases), (rel, phrases)


def test_package_description_source_is_readme():
    pyproject = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    source = contract()["package_description_source"]
    assert f'readme = "{source}"' in pyproject


def metadata_violations(wheel: Path) -> list[str]:
    with zipfile.ZipFile(wheel) as archive:
        names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        assert len(names) == 1, names
        body = archive.read(names[0]).decode("utf-8", errors="replace")
    return [name for name, pattern in PROHIBITED.items() if pattern.search(body)]


def test_wheel_metadata_inspector_detects_prohibited_copy(tmp_path):
    wheel = tmp_path / "regula_ai-1.9.0-py3-none-any.whl"
    metadata = "Metadata-Version: 2.4\nName: regula-ai\nVersion: 1.9.0\n\n" + (
        REPO / "README.md").read_text(encoding="utf-8")
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("regula_ai-1.9.0.dist-info/METADATA", metadata)
    assert metadata_violations(wheel) == []
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("regula_ai-1.9.0.dist-info/METADATA", metadata + "\nRegula is a compliance scanner.\n")
    assert "compliance scan" in metadata_violations(wheel)


def test_negative_controls_prove_each_guard_can_fail(tmp_path):
    payload = contract()
    for row in payload["active_surfaces"]:
        src = REPO / row["path"]
        dst = tmp_path / row["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    dst = tmp_path / "data/public_claim_surfaces.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(payload), encoding="utf-8")
    readme = tmp_path / "README.md"
    original = readme.read_text(encoding="utf-8")
    for planted in (
        "Regula classifies your system into a risk tier.",
        "Regula tells you which obligations apply.",
        "Regula makes zero network calls.",
        "No DPA is required.",
        "Auditor-ready evidence.",
        "Every metric is reproducible.",
        "The scan takes 30 seconds.",
        "Zero known security findings.",
        "Regula is a compliance scanner.",
    ):
        readme.write_text(original + "\n" + planted, encoding="utf-8")
        assert violations(tmp_path), planted
    payload["active_surfaces"].pop()
    dst.write_text(json.dumps(payload), encoding="utf-8")
    assert set(active_paths(tmp_path)) != set(active_paths(REPO))


def test_git_enumeration_succeeded():
    run = subprocess.run(["git", "ls-files", "--error-unmatch", *active_paths()],
                         cwd=REPO, capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr
