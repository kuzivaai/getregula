"""Class-wide controls for active high-consequence public claims."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from public_surface_inventory import (
    CLAIM_LANGUAGES,
    PROHIBITED_CLAIMS,
    claim_violations,
    discover,
    fold_for_claim_match,
)

REPO = Path(__file__).resolve().parent.parent
CONTRACT = REPO / "data" / "public_claim_surfaces.json"

PROHIBITED = PROHIBITED_CLAIMS

# One planted claim per (class, language). Each must fire its own arm, so a
# translation that is wrong, or a language arm that was never written, shows up
# as a failing control rather than as a quietly green guard.
PLANTED_CLAIMS = {
    ("legal classification", "en"): "Regula classifies your system into a risk tier.",
    ("legal classification", "de"): "Regula klassifiziert Ihr System.",
    ("legal classification", "pt"): "A Regula classifica o seu sistema.",
    ("compliance scan", "en"): "Regula is a compliance scanner.",
    ("compliance scan", "de"): "Regula ist ein Konformitätsscanner.",
    ("compliance scan", "pt"): "A Regula é um scanner de conformidade.",
    ("obligation determination", "en"): "Regula tells you which obligations apply.",
    ("obligation determination", "de"): "Regula sagt Ihnen, welche Pflichten gelten.",
    ("obligation determination", "pt"): "A Regula diz quais obrigações se aplicam.",
    ("universal network", "en"): "Regula makes zero network calls.",
    ("universal network", "de"): "Regula macht null Netzwerkaufrufe.",
    ("universal network", "pt"): "A Regula faz zero chamadas de rede.",
    ("DPA determination", "en"): "No DPA is required.",
    ("DPA determination", "de"): "Kein AVV ist erforderlich.",
    ("DPA determination", "pt"): "Nenhum DPA é necessário.",
    ("auditor completeness", "en"): "Auditor-ready evidence.",
    ("auditor completeness", "de"): "Auditbereite Nachweise.",
    ("auditor completeness", "pt"): "Evidências prontas para auditoria.",
    ("universal reproducibility", "en"): "Every metric is reproducible.",
    ("universal reproducibility", "de"): "Jede Kennzahl ist reproduzierbar.",
    ("universal reproducibility", "pt"): "Cada métrica é reproduzível.",
    ("unbounded runtime", "en"): "The scan takes 30 seconds.",
    ("unbounded runtime", "de"): "Der Scan dauert 30 Sekunden.",
    ("unbounded runtime", "pt"): "A verificação leva 30 segundos.",
    ("zero security findings", "en"): "Zero known security findings.",
    ("zero security findings", "de"): "Null bekannte Sicherheitsbefunde.",
    ("zero security findings", "pt"): "Zero vulnerabilidades de segurança conhecidas.",
}

# The corrected, bounded wording that replaced each prohibited claim. These must
# stay clean, or the guard is failing closed on honest copy and will be worked
# around rather than obeyed.
HEDGED_COPY = (
    "the local core does not upload scanned files",
    "der lokale Kern lädt gescannte Dateien nicht hoch",
    "o núcleo local não envia os arquivos analisados",
    "Regula :  EU AI Act code-indicator scanner",
    "Regula :  EU-KI-Gesetz-Indikator-Scanner für Code",
    "Regula :  scanner de indicadores da Lei de IA da UE para código",
    "0 unexpected security findings",
    "0 unerwartete Sicherheitsbefunde",
    "0 vulnerabilidades inesperadas",
)


def shipped_languages(root: Path = REPO) -> set[str]:
    """Languages the tracked site actually ships, from each page's lang attribute.

    Enumerated from git rather than read off a list, per measurement rule 4c:
    a completeness claim about locale coverage has to be produced by
    enumeration. Untracked pages are not surfaces and are excluded.
    """
    run = subprocess.run(["git", "ls-files", "site"], cwd=root,
                         capture_output=True, text=True, check=True)
    languages = set()
    for rel in run.stdout.split():
        if not rel.endswith((".html", ".htm")):
            continue
        match = re.search(r'<html[^>]*\blang="([A-Za-z]{2})',
                          (root / rel).read_text(encoding="utf-8", errors="replace"))
        if match:
            languages.add(match.group(1).lower())
    return languages


def contract(root: Path = REPO) -> dict:
    return json.loads((root / "data/public_claim_surfaces.json").read_text(encoding="utf-8"))


def active_paths(root: Path = REPO) -> list[str]:
    return sorted({row["source"].split("#", 1)[0]
                   for row in contract(root)["records"]
                   if row["classification"] == "active_product"
                   and row["claim_capable"]
                   and (root / row["source"].split("#", 1)[0]).is_file()})


def violations(root: Path = REPO) -> list[tuple[str, str, str]]:
    found = []
    for rel in active_paths(root):
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
        found.extend((rel, claim_class, language)
                     for claim_class, language in claim_violations(text))
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
    pricing = (REPO / "site/pricing.html").read_text(encoding="utf-8")
    assert "Payment gate not active" in pricing
    assert "Start free assessment" in pricing
    assert "EUR 49" not in pricing and "EUR 149" not in pricing
    assert "Compliance score with per-article breakdown" not in pricing


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
        "site/pricing.html",
    )
    for rel in paths:
        text = (REPO / rel).read_text(encoding="utf-8", errors="replace")
        assert "—" not in text and "&mdash;" not in text.lower(), rel


def test_mobile_navigation_supports_pointer_and_escape_close():
    paths = (
        "site/index.html",
        "site/locales/de.html",
        "site/locales/pt-br.html",
        "site/assess/index.html",
        "site/assess/de.html",
        "site/assess/pt-br.html",
        "site/pricing.html",
    )
    for rel in paths:
        text = (REPO / rel).read_text(encoding="utf-8", errors="replace")
        assert ".showModal()" not in text, rel
        assert ".show()" in text, rel
        assert "event.key==='Escape'" in text, rel
        assert "event.preventDefault();this.close()" in text, rel
        assert "b.focus()" in text, rel


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
    return [name for name, _language in claim_violations(body)]


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
    for (claim_class, language), planted in PLANTED_CLAIMS.items():
        readme.write_text(original + "\n" + planted, encoding="utf-8")
        hits = claim_violations(readme.read_text(encoding="utf-8"))
        assert (claim_class, language) in hits, (claim_class, language, planted, hits)


def test_every_claim_class_has_an_arm_for_every_shipped_language():
    # The failure this prevents, recorded because it shipped: every wording
    # guard here was written in English while the site ships three languages,
    # so site/locales/pt-br.html carried an absolute offline claim that the
    # English page correctly hedged, and no guard could see it. Adding a fourth
    # locale now fails this test until its patterns are written.
    languages = shipped_languages()
    assert languages, "enumeration found no lang attribute; the check would pass vacuously"
    assert set(CLAIM_LANGUAGES) == languages, (sorted(CLAIM_LANGUAGES), sorted(languages))
    for claim_class, arms in PROHIBITED.items():
        assert languages <= set(arms), (claim_class, sorted(languages - set(arms)))


def test_planted_controls_cover_every_class_and_language_pair():
    # Without this, a claim class could gain a language arm that no control
    # exercises, which is the "green because it tests nothing" failure.
    expected = {(claim_class, language)
                for claim_class in PROHIBITED
                for language in CLAIM_LANGUAGES}
    assert set(PLANTED_CLAIMS) == expected, sorted(expected ^ set(PLANTED_CLAIMS))


def test_claim_patterns_are_written_in_folded_form():
    # Matching happens against accent-folded, casefolded text, so an accented
    # or non-ASCII pattern can never fire. That would be a guard that looks
    # present and is inert.
    for claim_class, arms in PROHIBITED.items():
        for language, pattern in arms.items():
            assert pattern.pattern.isascii(), (claim_class, language, pattern.pattern)


def test_matching_survives_markup_entities_and_accents():
    # The three defects that made the previous raw-text match unsound. Each
    # string below returned no hit before normalisation was added.
    assert ("universal network", "en") in claim_violations(
        "Regula makes zero <strong>network</strong> calls."), "markup split must not evade"
    assert ("universal network", "pt") in claim_violations(
        "seu c&oacute;digo nunca sai da sua m&aacute;quina"), "HTML entities must not evade"
    assert ("universal network", "pt") in claim_violations(
        "seu código nunca sai da sua máquina"), "accents must not evade"
    # Attribute text was covered by the old raw match and must stay covered.
    assert ("compliance scan", "en") in claim_violations(
        '<meta property="og:image:alt" content="Regula is a compliance scanner">'
    ), "claims in attribute values must still be caught"


def test_hedged_copy_does_not_trip_the_guard():
    # Proves the guard discriminates a bounded statement from an absolute one,
    # rather than banning the subject matter outright.
    for copy in HEDGED_COPY:
        assert claim_violations(copy) == [], copy


def test_folding_is_idempotent_and_strips_accents():
    assert fold_for_claim_match("C&Oacute;DIGO\n\tNunca") == "codigo nunca"
    once = fold_for_claim_match("Máquina &middot; Ihr Code verlässt")
    assert fold_for_claim_match(once) == once


def test_git_enumeration_succeeded():
    run = subprocess.run(["git", "ls-files", "--error-unmatch", *active_paths()],
                         cwd=REPO, capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr
