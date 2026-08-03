"""Class-wide controls for active high-consequence public claims."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from public_surface_inventory import PROHIBITED_CLAIMS, discover

REPO = Path(__file__).resolve().parent.parent
CONTRACT = REPO / "data" / "public_claim_surfaces.json"

PROHIBITED = PROHIBITED_CLAIMS


def contract(root: Path = REPO) -> dict:
    return json.loads((root / "data/public_claim_surfaces.json").read_text(encoding="utf-8"))


def active_paths(root: Path = REPO) -> list[str]:
    return sorted({row["source"].split("#", 1)[0]
                   for row in contract(root)["records"]
                   if row["classification"] == "active_product"
                   and row["claim_capable"]
                   and (root / row["source"].split("#", 1)[0]).is_file()})


def violations(root: Path = REPO) -> list[tuple[str, str]]:
    found = []
    for rel in active_paths(root):
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
        for claim_class, pattern in PROHIBITED.items():
            if pattern.search(text):
                found.append((rel, claim_class))
    return found


def test_contract_is_bidirectional_and_non_vacuous():
    payload = contract()
    derived = discover()
    assert payload == derived
    ids = [row["stable_id"] for row in payload["records"]]
    assert len(ids) == len(set(ids)) and len(ids) > 22
    assert all(set(row) == {"stable_id", "channel", "source", "destination",
                           "discovery_basis", "content_kind", "claim_capable",
                           "classification", "reason"}
               for row in payload["records"])


def test_active_surfaces_do_not_publish_prohibited_claims():
    # Every discovered active, claim-capable delivery surface is enforced.
    # The negative controls below prove this is green because the copy was
    # corrected, not because the guards became inert.
    assert violations() == []


def test_required_limitation_concepts_are_translated():
    required = {
        "site/index.html": ("does not determine legal classification", "human review"),
        "site/locales/de.html": ("bestimmt weder die rechtliche klassifizierung", "menschliche kontextprüfung"),
        "site/locales/pt-br.html": ("não determina classificação jurídica", "revisão humana"),
    }
    for rel, phrases in required.items():
        text = (REPO / rel).read_text(encoding="utf-8", errors="replace").lower()
        assert all(phrase.lower() in text for phrase in phrases), (rel, phrases)


def test_public_homepages_do_not_expose_internal_programme_gates():
    forbidden = {
        "site/index.html": ("commercial evaluation remains stop", "customer pilot is not approved"),
        "site/locales/de.html": ("kommerzielle bewertung bleibt stop", "kundenpilot ist nicht freigegeben"),
        "site/locales/pt-br.html": ("avaliação comercial atual permanece stop", "piloto com clientes não está aprovado"),
    }
    for rel, phrases in forbidden.items():
        text = (REPO / rel).read_text(encoding="utf-8", errors="replace").lower()
        assert not any(phrase in text for phrase in phrases), (rel, phrases)


def test_public_entry_points_do_not_use_em_dashes():
    paths = (
        "README.md",
        "site/index.html",
        "site/locales/de.html",
        "site/locales/pt-br.html",
        "site/assess/index.html",
        "site/assess/de.html",
        "site/assess/pt-br.html",
        "site/about.html",
    )
    for rel in paths:
        text = (REPO / rel).read_text(encoding="utf-8", errors="replace")
        assert "—" not in text and "&mdash;" not in text.lower(), rel


def test_mobile_navigation_toggle_remains_pointer_accessible():
    paths = (
        "site/index.html",
        "site/locales/de.html",
        "site/locales/pt-br.html",
        "site/assess/index.html",
        "site/assess/de.html",
        "site/assess/pt-br.html",
    )
    for rel in paths:
        text = (REPO / rel).read_text(encoding="utf-8", errors="replace")
        assert ".showModal()" not in text, rel
        assert ".show()" in text, rel


def test_package_description_source_is_readme():
    pyproject = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    package_rows = [row for row in contract()["records"]
                    if row["content_kind"] == "package-long-description"]
    assert len(package_rows) == 1
    assert f'readme = "{package_rows[0]["source"]}"' in pyproject


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
    readme = tmp_path / "README.md"
    original = (REPO / "README.md").read_text(encoding="utf-8")
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
        assert any(pattern.search(readme.read_text(encoding="utf-8"))
                   for pattern in PROHIBITED.values()), planted


def test_git_enumeration_succeeded():
    run = subprocess.run(["git", "ls-files", "--error-unmatch", *active_paths()],
                         cwd=REPO, capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr
