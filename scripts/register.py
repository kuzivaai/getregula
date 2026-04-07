# regula-ignore
"""Annex VIII registration packet generator.

Builds Annex VIII Section A/B/C registration packets for an AI project,
auto-filling fields from existing Regula scan artifacts and emitting an
explicit gap list for fields the scanner cannot derive.

No network calls. No interactive flow. See
docs/superpowers/specs/2026-04-07-regula-register-annex-viii-design.md
for the full design and primary-source verification.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "references" / "annex_viii_sections.json"


def load_schema() -> dict:
    """Load the Annex VIII section schema from the reference JSON file."""
    with open(_SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# Annex III point → (target, article, fields_excluded) for providers.
# Point 1 = biometrics, 2 = critical infra, 3 = education, 4 = employment,
# 5 = essential services, 6 = law enforcement, 7 = migration/asylum/border, 8 = justice/democracy.
# See spec §4.2 and primary sources at references/annex_viii_sections.json.

_PROVIDER_NON_PUBLIC_POINTS = {1, 6, 7}      # Art 49(4) — non-public EU section
_PROVIDER_NATIONAL_POINTS = {2}              # Art 49(5) — national-level registration
_NON_PUBLIC_EXCLUDED_FIELDS = [6, 8, 9]      # Section A points excluded under Art 49(4)


def detect_section_and_target(role: str, annex_iii_point: int | None,
                              deployer_type: str, art_6_3_exempted: bool) -> dict:
    """Determine which Annex VIII section and submission target apply.

    Args:
        role: "provider", "deployer", or "unclear" (from explain.detect_provider_deployer)
        annex_iii_point: 1-8 if a high-risk Annex III area was detected, else None
        deployer_type: "public_authority" or "none"
        art_6_3_exempted: True if the provider has self-assessed as non-high-risk under Art 6(3)

    Returns:
        {"section", "target", "article", "fields_excluded", "kind"}

        "kind" is one of: "registration_required", "not_applicable",
        "no_registration_required".
    """
    # Provider self-exemption (Art 6(3)) — Section B regardless of Annex III point
    if role == "provider" and art_6_3_exempted:
        return {
            "section": "B",
            "target": "eu_database_public",
            "article": "49(2)",
            "fields_excluded": [],
            "kind": "registration_required",
        }

    if role == "provider" and annex_iii_point is not None:
        if annex_iii_point in _PROVIDER_NATIONAL_POINTS:
            return {
                "section": "A",
                "target": "national_authority",
                "article": "49(5)",
                "fields_excluded": [],
                "kind": "registration_required",
            }
        if annex_iii_point in _PROVIDER_NON_PUBLIC_POINTS:
            return {
                "section": "A",
                "target": "eu_database_non_public",
                "article": "49(4)",
                "fields_excluded": list(_NON_PUBLIC_EXCLUDED_FIELDS),
                "kind": "registration_required",
            }
        return {
            "section": "A",
            "target": "eu_database_public",
            "article": "49(1)",
            "fields_excluded": [],
            "kind": "registration_required",
        }

    # Deployer branches
    if role == "deployer" and annex_iii_point is not None:
        if deployer_type == "public_authority":
            target = ("eu_database_non_public"
                      if annex_iii_point in _PROVIDER_NON_PUBLIC_POINTS
                      else "eu_database_public")
            return {
                "section": "C",
                "target": target,
                "article": "49(3)",
                "fields_excluded": [],
                "kind": "registration_required",
            }
        # Private-sector deployer — out of Art 49 scope
        return {
            "section": None,
            "target": None,
            "article": None,
            "fields_excluded": [],
            "kind": "not_applicable",
        }

    # Anything else (no Annex III area, unclear role) → not applicable
    return {
        "section": None,
        "target": None,
        "article": None,
        "fields_excluded": [],
        "kind": "not_applicable",
    }


def build_redirects(kind: str) -> list[str]:
    """Return user-facing next-step suggestions for non-registration cases.

    NEVER references `regula explain` — that command does not exist
    (verified by grep of cli.py during planning).
    """
    if kind == "not_applicable":
        return [
            "regula gap        — Article 26 deployer obligations gap assessment",
            "regula oversight  — human oversight checks (Article 14)",
        ]
    if kind == "no_registration_required":
        return [
            "regula check      — keep scanning for risk indicators",
            "regula classify   — confirm classification on individual files",
        ]
    return []


def resolve_autofill(fields_def: list, discovery: dict,
                     exclude_points: list | None = None) -> tuple:
    """Build the {field_key: {value, source, verified}} dict and the gap list.

    Args:
        fields_def: list of field definitions from the schema (one section's "fields")
        discovery: result of discover_ai_systems.discover() for the project
        exclude_points: section point numbers to skip entirely (Art 49(4) exclusions)

    Returns:
        (filled_fields, gaps) — filled_fields is a dict keyed by field "key";
        gaps is a list of {field, section_point, label, why} dicts for fields
        whose value could not be derived.
    """
    exclude = set(exclude_points or [])
    filled = {}
    gaps = []

    # Pull policy lazily so tests can monkeypatch
    from policy_config import get_policy
    policy = get_policy() or {}

    for fd in fields_def:
        if fd["point"] in exclude:
            continue

        key = fd["key"]
        source = fd.get("autofill_source")
        value = _resolve_one(key, source, policy, discovery)

        if value is not None:
            filled[key] = {"value": value, "source": source, "verified": True}
        else:
            filled[key] = {"value": None, "source": source, "verified": False}
            gaps.append({
                "field": key,
                "section_point": fd["point"],
                "label": fd["label"],
                "why": _gap_reason(source),
            })

    return filled, gaps


def _resolve_one(key: str, source, policy: dict, discovery: dict):
    """Resolve a single field value from the named source. Returns None if unresolvable."""
    if source is None:
        return None

    if source == "policy_config":
        if key in ("provider_identity", "deployer_identity"):
            org = policy.get("organisation")
            email = (policy.get("governance_contacts", {}).get("ai_officer", {}) or {}).get("email")
            if org and email:
                return f"{org} <{email}>"
            if org:
                return org
            return None
        if key == "authorised_representative_identity":
            return policy.get("authorised_representative")
        return None

    if source == "discover":
        if key == "ai_system_trade_name":
            return discovery.get("project_name")
        if key == "system_status":
            return _map_status(discovery.get("compliance_status", "not_started"))
        return None

    if source == "model_inventory":
        if key == "data_inputs_and_logic":
            libs = discovery.get("ai_libraries") or []
            models = discovery.get("model_files") or []
            if libs or models:
                parts = []
                if libs:
                    parts.append(f"AI libraries: {', '.join(libs)}")
                if models:
                    parts.append(f"Model files: {len(models)}")
                return "; ".join(parts)
            return None
        return None

    if source == "conform":
        # Reference path only — present if .regula/conform/ exists
        from pathlib import Path as _P
        cp = _P(".regula") / "conform" / "evidence_pack.json"
        return str(cp) if cp.exists() else None

    if source == "evidence_pack":
        from pathlib import Path as _P
        ep = _P(".regula") / "evidence" / "README.md"
        return str(ep) if ep.exists() else None

    if source == "assess":
        from pathlib import Path as _P
        ap = _P(".regula") / "assess" / "fria.json"
        return str(ap) if ap.exists() else None

    return None


def _map_status(compliance_status: str) -> str:
    return {
        "not_started": "in development",
        "in_progress": "in development",
        "completed": "on market",
    }.get(compliance_status, "in development")


def _gap_reason(source) -> str:
    if source is None:
        return "Cannot be derived from code — manual entry required"
    return f"Source '{source}' did not return a value for this project"




def build_packet(discovery: dict, role: str, annex_iii_point,
                 deployer_type: str = "none", art_6_3_exempted: bool = False) -> dict:
    """Build the full Annex VIII packet `data` block (the inside of json_output's envelope).

    Returns one of three packet shapes depending on the input:

    1. ``kind="no_registration_required"`` — when discovery's highest_risk is
       not_ai or minimal_risk. Contains: system_id, system_name, kind, reason,
       redirects, schema_provenance, deadlines.

    2. ``kind="not_applicable"`` — when the section detector returns not_applicable
       (e.g., private-sector deployer outside Article 49 scope). Contains:
       system_id, system_name, kind, reason, redirects, schema_provenance,
       deadlines.

    3. ``kind="registration_required"`` — the full registration packet. Contains:
       system_id, system_name, annex_viii_section, article, submission_target,
       submission_status, fields_excluded_under_49_4, fields, _gaps,
       completeness, deadlines, schema_provenance, kind.
    """
    schema = load_schema()
    decision = detect_section_and_target(role=role, annex_iii_point=annex_iii_point,
                                         deployer_type=deployer_type,
                                         art_6_3_exempted=art_6_3_exempted)

    project_name = discovery.get("project_name", "<unknown>")
    project_path = discovery.get("project_path", "")
    system_id = hashlib.sha256(project_path.encode("utf-8")).hexdigest()[:16]

    # Edge cases — not_applicable / no_registration_required
    highest_risk = discovery.get("highest_risk", "minimal_risk")
    if highest_risk in ("not_ai", "minimal_risk"):
        return {
            "system_id": system_id,
            "system_name": project_name,
            "kind": "no_registration_required",
            "reason": f"Project classified as {highest_risk}; Annex VIII registration does not apply.",
            "redirects": build_redirects("no_registration_required"),
            "schema_provenance": _provenance(schema),
            "deadlines": schema["deadlines"],
        }

    if decision["kind"] == "not_applicable":
        return {
            "system_id": system_id,
            "system_name": project_name,
            "kind": "not_applicable",
            "reason": "Private-sector deployer — outside Article 49 scope. "
                      "Article 26 obligations still apply.",
            "redirects": build_redirects("not_applicable"),
            "schema_provenance": _provenance(schema),
            "deadlines": schema["deadlines"],
        }

    section = decision["section"]
    section_def = schema["sections"][section]
    fields_def = section_def["fields"]

    filled, gaps = resolve_autofill(fields_def, discovery=discovery,
                                    exclude_points=decision["fields_excluded"])

    total = len(fields_def) - len(decision["fields_excluded"])
    filled_count = sum(1 for f in filled.values() if f["verified"])

    submission_status = section_def.get("submission_status", "mandatory")

    return {
        "system_id": system_id,
        "system_name": project_name,
        "annex_viii_section": section,
        "article": decision["article"],
        "submission_target": decision["target"],
        "submission_status": submission_status,
        "fields_excluded_under_49_4": decision["fields_excluded"],
        "fields": filled,
        "_gaps": gaps,
        "completeness": {
            "filled": filled_count,
            "total": total,
            "percentage": int(round(100 * filled_count / total)) if total else 0,
        },
        "deadlines": schema["deadlines"],
        "schema_provenance": _provenance(schema),
        "kind": "registration_required",
    }


def _provenance(schema: dict) -> dict:
    md = schema["metadata"]
    return {
        "verified_date": md["verified_date"],
        "verification_method": md["verification_method"],
        "sources": list(md["sources"]),
    }


REGISTRY_RELATIVE = Path(".regula") / "registry"


def write_packet(packet: dict, output_dir=None, force: bool = False) -> Path:
    """Write the canonical packet JSON to <output_dir>/<system_id>.json.

    Defaults output_dir to .regula/registry under the current working directory.
    Raises FileExistsError if the file exists and force=False.
    """
    out_dir = Path(output_dir) if output_dir else REGISTRY_RELATIVE
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{packet['system_id']}.json"

    if out_file.exists() and not force:
        raise FileExistsError(
            f"Packet already exists at {out_file}. Re-run with --force to overwrite."
        )

    out_file.write_text(json.dumps(packet, indent=2, default=str), encoding="utf-8")
    return out_file


def write_gaps_yaml(packet: dict, output_dir=None) -> Path:
    """Write the companion gaps YAML containing only gap fields, for hand-editing.

    YAML is hand-emitted (no PyYAML), keeping with Regula's stdlib-only stance.
    Format is intentionally minimal: one key per gap with an empty value: slot
    and the label/why as comments.
    """
    out_dir = Path(output_dir) if output_dir else REGISTRY_RELATIVE
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{packet['system_id']}.gaps.yaml"

    lines = [
        f"# Annex VIII gaps for system_id={packet['system_id']}",
        "# Edit each `value:` slot in place. Lines starting with # are comments.",
        "# After editing, the canonical JSON packet at <system_id>.json remains",
        "# the source of truth — fold values back manually for v1.",
        "",
    ]
    for gap in packet.get("_gaps", []):
        lines.append(f"# Section point {gap['section_point']}: {gap['label']}")
        lines.append(f"# Why gap: {gap['why']}")
        lines.append(f"{gap['field']}:")
        lines.append("  value:")
        lines.append("")

    out_file.write_text("\n".join(lines), encoding="utf-8")
    return out_file
