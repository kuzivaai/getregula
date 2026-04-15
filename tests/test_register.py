"""Tests for regula register (Annex VIII packet generator)."""
import sys
from pathlib import Path

# Reuse the same sys.path setup as test_classification.py
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def test_register_schema_loads_with_correct_field_counts():
    """The Annex VIII schema file loads and reports A=13, B=9, C=5 fields."""
    from register import load_schema

    schema = load_schema()
    assert "metadata" in schema, f"missing metadata: {list(schema.keys())}"
    assert "sections" in schema, f"missing sections: {list(schema.keys())}"

    sections = schema["sections"]
    assert set(sections.keys()) == {"A", "B", "C"}, f"sections: {list(sections.keys())}"

    assert len(sections["A"]["fields"]) == 13, \
        f"Section A must have 13 fields, got {len(sections['A']['fields'])}"
    assert len(sections["B"]["fields"]) == 9, \
        f"Section B must have 9 fields, got {len(sections['B']['fields'])}"
    assert len(sections["C"]["fields"]) == 5, \
        f"Section C must have 5 fields, got {len(sections['C']['fields'])}"

    assert sections["A"]["article"] == "49(1)"
    assert sections["B"]["article"] == "49(2)"
    assert sections["C"]["article"] == "49(3)"

    md = schema["metadata"]
    assert md["regulation"] == "Regulation (EU) 2024/1689"
    assert md["verified_date"] == "2026-04-07"
    assert "verification_method" in md
    assert "sources" in md and len(md["sources"]) >= 3
    print("✓ register: schema loads with A=13, B=9, C=5")


def test_register_schema_excluded_under_49_4_flags_are_correct():
    """Section A points 6, 8, 9 are excluded under Art 49(4); all other A points and all B/C points are not."""
    from register import load_schema

    schema = load_schema()

    # Section A: every field must carry the flag, exactly points 6/8/9 are True
    a_fields = schema["sections"]["A"]["fields"]
    excluded_a_points = sorted(f["point"] for f in a_fields if f["excluded_under_49_4"])
    assert excluded_a_points == [6, 8, 9], \
        f"Section A excluded points must be [6, 8, 9], got {excluded_a_points}"
    for f in a_fields:
        assert "excluded_under_49_4" in f, \
            f"Section A point {f['point']} missing excluded_under_49_4"
        assert isinstance(f["excluded_under_49_4"], bool)

    # Sections B and C: every field must carry the flag, all values must be False
    for sec in ("B", "C"):
        for f in schema["sections"][sec]["fields"]:
            assert "excluded_under_49_4" in f, \
                f"Section {sec} point {f['point']} missing excluded_under_49_4"
            assert f["excluded_under_49_4"] is False, \
                f"Section {sec} point {f['point']} must be False, got {f['excluded_under_49_4']}"

    print("✓ register: excluded_under_49_4 flags correct (A: 6/8/9 only, B/C: all False)")


def test_register_detects_section_a_for_provider_annex3_point4_employment():
    """Provider building an Annex III point 4 (employment) system → Section A, eu_database_public, Art 49(1)."""
    from register import detect_section_and_target
    decision = detect_section_and_target(role="provider", annex_iii_point=4, deployer_type="none", art_6_3_exempted=False)
    assert decision["section"] == "A", f"section: {decision}"
    assert decision["target"] == "eu_database_public", f"target: {decision}"
    assert decision["article"] == "49(1)", f"article: {decision}"
    assert decision["fields_excluded"] == [], f"exclusions: {decision}"
    print("✓ register: provider point 4 → A / public")


def test_register_detects_critical_infra_routes_to_national():
    """Provider of Annex III point 2 (critical infrastructure) → national_authority per Art. 49(5)."""
    from register import detect_section_and_target
    decision = detect_section_and_target(role="provider", annex_iii_point=2, deployer_type="none", art_6_3_exempted=False)
    assert decision["section"] == "A"
    assert decision["target"] == "national_authority", f"target: {decision}"
    assert decision["article"] == "49(5)"
    print("✓ register: critical infra → national")


def test_register_detects_biometrics_routes_to_non_public():
    """Provider of Annex III point 1 (biometrics) → eu_database_non_public, fields 6/8/9 excluded (Art 49(4))."""
    from register import detect_section_and_target
    decision = detect_section_and_target(role="provider", annex_iii_point=1, deployer_type="none", art_6_3_exempted=False)
    assert decision["section"] == "A"
    assert decision["target"] == "eu_database_non_public", f"target: {decision}"
    assert decision["article"] == "49(4)"
    assert sorted(decision["fields_excluded"]) == [6, 8, 9], f"exclusions: {decision}"
    print("✓ register: biometrics → non_public, excludes 6,8,9")


def test_register_detects_law_enforcement_routes_to_non_public():
    """Provider of Annex III point 6 (law enforcement) → eu_database_non_public + same exclusions."""
    from register import detect_section_and_target
    decision = detect_section_and_target(role="provider", annex_iii_point=6, deployer_type="none", art_6_3_exempted=False)
    assert decision["target"] == "eu_database_non_public"
    assert decision["article"] == "49(4)"
    assert sorted(decision["fields_excluded"]) == [6, 8, 9]
    print("✓ register: law enforcement → non_public")


def test_register_detects_migration_routes_to_non_public():
    """Provider of Annex III point 7 (migration/asylum/border) → eu_database_non_public + same exclusions."""
    from register import detect_section_and_target
    decision = detect_section_and_target(role="provider", annex_iii_point=7, deployer_type="none", art_6_3_exempted=False)
    assert decision["target"] == "eu_database_non_public"
    assert decision["article"] == "49(4)"
    assert sorted(decision["fields_excluded"]) == [6, 8, 9]
    print("✓ register: migration → non_public")


def test_register_section_b_for_provider_with_art_6_3_self_exemption():
    """Provider self-exempted via Art 6(3) → Section B, mandatory, omnibus note present in schema."""
    from register import detect_section_and_target, load_schema
    decision = detect_section_and_target(role="provider", annex_iii_point=4, deployer_type="none", art_6_3_exempted=True)
    assert decision["section"] == "B"
    assert decision["article"] == "49(2)"
    assert decision["target"] == "eu_database_public"
    schema_b = load_schema()["sections"]["B"]
    assert schema_b["submission_status"] == "mandatory"
    assert "pending_trilogue" in schema_b["omnibus_field_simplification"]
    print("✓ register: Art 6(3) exemption → B mandatory")


def test_register_section_c_for_public_authority_deployer():
    """Public-authority deployer of any Annex III high-risk → Section C, Art 49(3)."""
    from register import detect_section_and_target
    decision = detect_section_and_target(role="deployer", annex_iii_point=4, deployer_type="public_authority", art_6_3_exempted=False)
    assert decision["section"] == "C"
    assert decision["article"] == "49(3)"
    assert decision["target"] == "eu_database_public"
    print("✓ register: public-authority deployer → C / public")


def test_register_section_c_public_authority_biometrics_routes_non_public():
    """Public authority deploying an Annex III point 1/6/7 system → Section C with non-public target."""
    from register import detect_section_and_target
    decision = detect_section_and_target(role="deployer", annex_iii_point=1, deployer_type="public_authority", art_6_3_exempted=False)
    assert decision["section"] == "C"
    assert decision["target"] == "eu_database_non_public"
    print("✓ register: public-authority biometrics → C / non_public")


def test_register_not_applicable_for_private_sector_deployer():
    """Private-sector deployer of high-risk → kind=not_applicable, redirects to gap+oversight."""
    from register import detect_section_and_target, build_redirects
    decision = detect_section_and_target(role="deployer", annex_iii_point=4, deployer_type="none", art_6_3_exempted=False)
    assert decision["kind"] == "not_applicable"
    redirects = build_redirects(decision["kind"])
    assert any("regula gap" in r for r in redirects)
    assert any("regula oversight" in r for r in redirects)
    assert not any("regula explain" in r for r in redirects), "must NOT reference non-existent explain command"
    print("✓ register: private deployer → not_applicable + correct redirects")


def test_register_resolve_autofill_fills_provider_identity_from_policy(monkeypatch):
    """resolve_autofill() pulls provider_identity from policy_config when source='policy_config'."""
    from register import resolve_autofill, load_schema
    import policy_config

    fake_policy = {
        "organisation": "Acme AI Ltd",
        "governance_contacts": {"ai_officer": {"email": "officer@acme.example"}},
    }
    monkeypatch.setattr(policy_config, "_POLICY", fake_policy)
    monkeypatch.setattr(policy_config, "get_policy", lambda path=None: fake_policy)

    schema = load_schema()
    section_a_fields = schema["sections"]["A"]["fields"]
    discovery = {"project_name": "demo-system", "compliance_status": "in_progress",
                 "ai_libraries": ["openai"], "model_files": []}

    fields, gaps = resolve_autofill(section_a_fields, discovery=discovery, exclude_points=[])

    assert fields["provider_identity"]["value"] is not None
    assert "Acme AI Ltd" in fields["provider_identity"]["value"]
    assert fields["provider_identity"]["source"] == "policy_config"
    assert fields["provider_identity"]["verified"] is True
    print("✓ register: autofill fills provider_identity from policy")


def test_register_resolve_autofill_lists_undriveable_fields_in_gaps():
    """Fields with autofill_source=null land in _gaps with the section_point and label."""
    from register import resolve_autofill, load_schema

    schema = load_schema()
    section_a_fields = schema["sections"]["A"]["fields"]
    discovery = {"project_name": "demo", "compliance_status": "not_started",
                 "ai_libraries": [], "model_files": []}

    fields, gaps = resolve_autofill(section_a_fields, discovery=discovery, exclude_points=[])

    gap_keys = {g["field"] for g in gaps}
    # intended_purpose, member_states are autofill_source=null in Section A
    assert "intended_purpose" in gap_keys, f"gaps: {gap_keys}"
    assert "member_states" in gap_keys, f"gaps: {gap_keys}"

    # Each gap entry has section_point, label, why
    for g in gaps:
        assert "field" in g and "section_point" in g and "label" in g and "why" in g
    print(f"✓ register: gap list contains {len(gaps)} undriveable fields")


def test_register_build_packet_envelope_shape(monkeypatch):
    """build_packet() returns a dict with all required top-level keys."""
    from register import build_packet
    import policy_config
    monkeypatch.setattr(policy_config, "get_policy",
                        lambda path=None: {"organisation": "Acme",
                                           "governance_contacts": {"ai_officer": {"email": "a@b.c"}}})

    discovery = {"project_name": "demo", "project_path": "/tmp/demo",
                 "compliance_status": "in_progress",
                 "ai_libraries": ["openai"], "model_files": [],
                 "highest_risk": "high_risk"}

    packet = build_packet(discovery=discovery, role="provider", annex_iii_point=4,
                          deployer_type="none", art_6_3_exempted=False)

    required = {"system_id", "system_name", "annex_viii_section", "article",
                "submission_target", "submission_status", "fields", "_gaps",
                "completeness", "deadlines", "schema_provenance", "kind",
                "fields_excluded_under_49_4"}
    missing = required - set(packet.keys())
    assert not missing, f"missing keys: {missing}"
    assert packet["annex_viii_section"] == "A"
    assert packet["article"] == "49(1)"
    assert packet["completeness"]["total"] == 13
    assert packet["completeness"]["filled"] >= 1
    print(f"✓ register: build_packet envelope shape ({packet['completeness']})")


def test_register_build_packet_dual_timeline_present(monkeypatch):
    """Every packet carries both the current law and the Omnibus proposed deadlines."""
    import policy_config
    monkeypatch.setattr(policy_config, "get_policy",
                        lambda path=None: {"organisation": "Acme",
                                           "governance_contacts": {"ai_officer": {"email": "a@b.c"}}})
    from register import build_packet
    discovery = {"project_name": "x", "project_path": "/tmp/x",
                 "compliance_status": "not_started", "ai_libraries": [],
                 "model_files": [], "highest_risk": "high_risk"}
    packet = build_packet(discovery=discovery, role="provider", annex_iii_point=4,
                          deployer_type="none", art_6_3_exempted=False)
    d = packet["deadlines"]
    assert d["applicable_deadline"] == "2026-08-02"
    assert d["omnibus_proposed_deadline"] == "2027-12-02"
    assert "trilogue_in_progress" in d["omnibus_status"]
    print("✓ register: dual timeline present")


def test_register_build_packet_schema_provenance_present(monkeypatch):
    """Every packet carries schema provenance (sources + verified date)."""
    import policy_config
    monkeypatch.setattr(policy_config, "get_policy",
                        lambda path=None: {"organisation": "Acme",
                                           "governance_contacts": {"ai_officer": {"email": "a@b.c"}}})
    from register import build_packet
    discovery = {"project_name": "x", "project_path": "/tmp/x",
                 "compliance_status": "not_started", "ai_libraries": [],
                 "model_files": [], "highest_risk": "high_risk"}
    packet = build_packet(discovery=discovery, role="provider", annex_iii_point=4,
                          deployer_type="none", art_6_3_exempted=False)
    p = packet["schema_provenance"]
    assert p["verified_date"] == "2026-04-07"
    assert isinstance(p["sources"], list) and len(p["sources"]) >= 3
    print("✓ register: schema provenance present")


def test_register_write_packet_creates_canonical_json(tmp_path):
    """write_packet() creates the .json file under output_dir/<system-id>.json."""
    from register import write_packet
    packet = {
        "system_id": "abc123",
        "system_name": "demo",
        "annex_viii_section": "A",
        "_gaps": [],
        "kind": "registration_required",
    }
    out = write_packet(packet, output_dir=tmp_path, force=False)
    assert out.exists()
    assert out.name == "abc123.json"

    import json as _json
    loaded = _json.loads(out.read_text())
    assert loaded["system_id"] == "abc123"
    print(f"✓ register: write_packet wrote {out}")


def test_register_write_gaps_yaml_only_contains_gap_fields(tmp_path):
    """The companion .gaps.yaml lists every gap field with an empty value: slot."""
    from register import write_gaps_yaml
    packet = {
        "system_id": "abc123",
        "_gaps": [
            {"field": "intended_purpose", "section_point": 5,
             "label": "Description of intended purpose", "why": "manual entry required"},
            {"field": "member_states", "section_point": 10,
             "label": "Member States...", "why": "manual entry required"},
        ],
    }
    out = write_gaps_yaml(packet, output_dir=tmp_path)
    assert out.exists()
    text = out.read_text()
    assert "intended_purpose:" in text
    assert "member_states:" in text
    assert "value:" in text   # empty slots
    assert "Description of intended purpose" in text  # label as comment
    print(f"✓ register: gaps.yaml written ({len(text)} bytes)")


def test_register_cli_json_format_emits_envelope(tmp_path, monkeypatch, capsys):
    """`regula register --format json` emits a json_output envelope with command='register'."""
    import policy_config
    monkeypatch.setattr(policy_config, "get_policy",
                        lambda path=None: {"organisation": "Acme",
                                           "governance_contacts": {"ai_officer": {"email": "a@b.c"}}})

    # Build a tiny fake project that classifies as high-risk via openai usage
    proj = tmp_path / "demo_proj"
    proj.mkdir()
    (proj / "main.py").write_text(
        "import openai\nclient = openai.OpenAI()\n"
        "# screening candidates for hire\n"
        "def screen(cv): return client.chat.completions.create(model='gpt-4', messages=[])\n"
    )

    monkeypatch.chdir(tmp_path)
    from cli import cmd_register
    import argparse
    args = argparse.Namespace(
        path=str(proj), section="auto", target="auto", deployer_type="none",
        output=None, format="json", force=False, no_gaps_yaml=True,
        art_6_3_exempted=False,
    )
    cmd_register(args)
    out = capsys.readouterr().out
    assert '"command": "register"' in out
    assert '"format_version": "1.0"' in out
    print("✓ register: CLI json envelope emitted")


def test_register_cli_force_overwrites_existing(tmp_path, monkeypatch):
    """Second run without --force fails (sys.exit 2); with --force succeeds."""
    import policy_config
    monkeypatch.setattr(policy_config, "get_policy",
                        lambda path=None: {"organisation": "Acme",
                                           "governance_contacts": {"ai_officer": {"email": "a@b.c"}}})

    proj = tmp_path / "p2"
    proj.mkdir()
    (proj / "main.py").write_text("import openai\nopenai.OpenAI()\n")
    monkeypatch.chdir(tmp_path)

    from cli import cmd_register
    import argparse
    base_kwargs = dict(path=str(proj), section="auto", target="auto",
                       deployer_type="none", output=None, format="text",
                       no_gaps_yaml=True, art_6_3_exempted=False)

    # First run — succeeds
    cmd_register(argparse.Namespace(**base_kwargs, force=False))

    # Second run — must raise SystemExit because the file already exists
    import pytest as _pt
    with _pt.raises(SystemExit) as exc_info:
        cmd_register(argparse.Namespace(**base_kwargs, force=False))
    assert exc_info.value.code == 2, f"expected exit code 2, got {exc_info.value.code}"

    # Third run with --force — succeeds
    cmd_register(argparse.Namespace(**base_kwargs, force=True))
    print("✓ register: --force overwrite semantics correct")


def test_register_legacy_shim_returns_compatible_dict(monkeypatch, tmp_path):
    """discover_ai_systems.generate_eu_registration() still returns the legacy keys
    so existing callers don't break, but the implementation delegates to register.build_packet."""
    monkeypatch.setenv("REGULA_REGISTRY", str(tmp_path / "registry.json"))

    import policy_config
    monkeypatch.setattr(policy_config, "get_policy",
                        lambda path=None: {"organisation": "Acme",
                                           "governance_contacts": {"ai_officer": {"email": "a@b.c"}}})

    import importlib
    import discover_ai_systems
    importlib.reload(discover_ai_systems)

    from discover_ai_systems import register_system, generate_eu_registration

    fake_discovery = {
        "project_name": "legacy_demo",
        "project_path": str(tmp_path),
        "discovered_at": "2026-04-07T00:00:00Z",
        "ai_libraries": ["openai"],
        "primary_language": "python",
        "model_files": [],
        "ai_code_files": [],
        "api_endpoints": [],
        "risk_classifications": [{"tier": "high_risk", "category": "employment"}],
        "highest_risk": "high_risk",
    }
    register_system(fake_discovery)
    result = generate_eu_registration("legacy_demo")

    # Legacy keys must still be present for back-compat
    for legacy_key in ("registration_type", "article", "system_name",
                       "provider_name", "intended_purpose", "risk_classification"):
        assert legacy_key in result, f"missing legacy key {legacy_key}: {list(result.keys())}"
    assert result["article"] == "49(1)"

    # New-style packet should be available under _packet
    assert "_packet" in result
    assert result["_packet"]["kind"] == "registration_required"
    print("✓ register: legacy generate_eu_registration shim still returns expected keys")


def test_register_highest_annex_iii_point_reads_indicators_and_description():
    """Regression: _highest_annex_iii_point must read the actual discover() shape
    (indicators + description), not the non-existent category/patterns keys.

    Bug shipped in Task 7, caught at end-of-branch review: with the wrong keys
    the helper always returned None and every packet fell through to not_applicable
    even for unambiguous high-risk provider projects.
    """
    from cli import _highest_annex_iii_point

    discovery = {
        "risk_classifications": [
            {
                "file": "train.py",
                "tier": "high_risk",
                "indicators": ["employment"],
                "description": "Employment and workers management",
            }
        ],
    }
    assert _highest_annex_iii_point(discovery) == 4

    d2 = {"risk_classifications": [{"indicators": ["biometrics"], "description": "Remote biometric ID"}]}
    assert _highest_annex_iii_point(d2) == 1

    assert _highest_annex_iii_point({"risk_classifications": []}) is None
    assert _highest_annex_iii_point({}) is None

    print("✓ register: _highest_annex_iii_point reads indicators+description (regression)")
