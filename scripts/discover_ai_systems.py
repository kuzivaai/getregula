#!/usr/bin/env python3
# regula-ignore
"""
Regula System Registry — AI System Discovery and Inventory
Scans projects for AI components and maintains a persistent registry.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from degradation import check_optional

from classify_risk import classify, RiskTier, is_ai_related, AI_INDICATORS


REGISTRY_PATH = Path(os.environ.get("REGULA_REGISTRY", Path.home() / ".regula" / "registry.json"))

# Compliance status workflow
# not_started → assessment → implementing → compliant → review_due
COMPLIANCE_STATUSES = ["not_started", "assessment", "implementing", "compliant", "review_due"]
COMPLIANCE_TRANSITIONS = {
    "not_started": ["assessment"],
    "assessment": ["implementing", "not_started"],
    "implementing": ["compliant", "assessment"],
    "compliant": ["review_due"],
    "review_due": ["assessment", "compliant"],
}

DEPENDENCY_FILES = {
    "requirements.txt": "python",
    "requirements-dev.txt": "python",
    "setup.py": "python",
    "pyproject.toml": "python",
    "Pipfile": "python",
    "package.json": "javascript",
    "package-lock.json": "javascript",
}

AI_DEPENDENCY_PATTERNS = {
    "python": [
        "tensorflow", "torch", "pytorch", "transformers", "langchain",
        "openai", "anthropic", "sklearn", "scikit-learn", "xgboost",
        "lightgbm", "keras", "huggingface-hub", "spacy", "nltk",
        "onnx", "onnxruntime",
    ],
    "javascript": [
        "@tensorflow/tfjs", "openai", "@anthropic-ai/sdk", "langchain",
        "@langchain", "brain.js", "@xenova/transformers",
    ],
}

MODEL_EXTENSIONS = {".onnx", ".pt", ".pth", ".pkl", ".joblib", ".h5", ".hdf5", ".safetensors", ".gguf", ".ggml"}
CODE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs", ".java", ".go", ".rs", ".c", ".cpp"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", "venv", ".venv", "dist", "build", ".next", ".tox", "egg-info"}


def load_registry() -> dict:
    """Load the persistent registry."""
    if REGISTRY_PATH.exists():
        try:
            return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"version": "1.0", "systems": {}}


def save_registry(registry: dict) -> None:
    """Save the persistent registry."""
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2, default=str), encoding="utf-8")


def scan_dependencies(project_path: Path) -> dict:
    """Scan dependency files for AI libraries."""
    findings = {"libraries": [], "language": None}

    for dep_file, language in DEPENDENCY_FILES.items():
        filepath = project_path / dep_file
        if not filepath.exists():
            continue

        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore").lower()
        except (PermissionError, OSError):
            continue

        for lib in AI_DEPENDENCY_PATTERNS.get(language, []):
            if lib.lower() in content:
                findings["libraries"].append(lib)
                findings["language"] = language

    return findings


def scan_model_files(project_path: Path) -> list:
    """Find model files in the project."""
    model_files = []
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in files:
            filepath = Path(root) / filename
            if filepath.suffix.lower() in MODEL_EXTENSIONS:
                rel_path = filepath.relative_to(project_path)
                size_mb = filepath.stat().st_size / (1024 * 1024)
                model_files.append({
                    "path": str(rel_path),
                    "extension": filepath.suffix,
                    "size_mb": round(size_mb, 2),
                })
    return model_files


def scan_code_files(project_path: Path) -> dict:
    """Scan code files for AI patterns and risk indicators."""
    findings = {
        "ai_files": [],
        "api_endpoints": set(),
        "risk_classifications": [],
    }

    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in files:
            filepath = Path(root) / filename
            if filepath.suffix not in CODE_EXTENSIONS:
                continue

            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
            except (PermissionError, OSError):
                continue

            if not is_ai_related(content):
                continue

            rel_path = str(filepath.relative_to(project_path))
            findings["ai_files"].append(rel_path)

            # Check for API endpoints
            for pattern in AI_INDICATORS["api_endpoints"]:
                if re.search(pattern, content, re.IGNORECASE):
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        findings["api_endpoints"].add(match.group(0))

            # Classify the file
            result = classify(content)
            if result.tier != RiskTier.MINIMAL_RISK:
                findings["risk_classifications"].append({
                    "file": rel_path,
                    "tier": result.tier.value,
                    "indicators": result.indicators_matched,
                    "description": result.description,
                })

    findings["api_endpoints"] = sorted(findings["api_endpoints"])
    return findings


def discover(project_path: str) -> dict:
    """Run full discovery on a project."""
    project = Path(project_path).resolve()
    project_name = project.name

    deps = scan_dependencies(project)
    models = scan_model_files(project)
    code = scan_code_files(project)

    # Determine highest risk
    risk_order = {"not_ai": 0, "minimal_risk": 1, "limited_risk": 2, "high_risk": 3, "prohibited": 4}
    highest_risk = "minimal_risk" if (deps["libraries"] or models or code["ai_files"]) else "not_ai"
    for rc in code["risk_classifications"]:
        if risk_order.get(rc["tier"], 0) > risk_order.get(highest_risk, 0):
            highest_risk = rc["tier"]

    return {
        "project_name": project_name,
        "project_path": str(project),
        "discovered_at": datetime.now(timezone.utc).isoformat(),
        "ai_libraries": deps["libraries"],
        "primary_language": deps["language"],
        "model_files": models,
        "ai_code_files": code["ai_files"],
        "api_endpoints": code["api_endpoints"],
        "risk_classifications": code["risk_classifications"],
        "highest_risk": highest_risk,
        "compliance_status": "not_started",
    }


def register_system(discovery: dict) -> dict:
    """Register a discovered system in the persistent registry."""
    registry = load_registry()
    project_name = discovery["project_name"]

    # Update or create entry
    if project_name in registry["systems"]:
        existing = registry["systems"][project_name]
        # Track risk trend before overwriting
        old_risk = existing.get("highest_risk")
        new_risk = discovery["highest_risk"]
        if old_risk and old_risk != new_risk:
            existing["previous_highest_risk"] = old_risk
        existing.update({
            "last_scanned": discovery["discovered_at"],
            "ai_libraries": discovery["ai_libraries"],
            "model_files": discovery["model_files"],
            "ai_code_files": discovery["ai_code_files"],
            "api_endpoints": discovery["api_endpoints"],
            "risk_classifications": discovery["risk_classifications"],
            "highest_risk": new_risk,
        })
        # Preserve compliance_status if already set
    else:
        registry["systems"][project_name] = {
            "registered_at": discovery["discovered_at"],
            "last_scanned": discovery["discovered_at"],
            "project_path": discovery["project_path"],
            "ai_libraries": discovery["ai_libraries"],
            "primary_language": discovery["primary_language"],
            "model_files": discovery["model_files"],
            "ai_code_files": discovery["ai_code_files"],
            "api_endpoints": discovery["api_endpoints"],
            "risk_classifications": discovery["risk_classifications"],
            "highest_risk": discovery["highest_risk"],
            "compliance_status": "not_started",
            "notes": "",
        }

    save_registry(registry)
    return registry


def scan_organization(base_path: str, register: bool = True) -> dict:
    """Scan all directories under base_path for AI systems.

    Walks one level deep looking for project directories (those with
    .git, package.json, pyproject.toml, Cargo.toml, etc.)

    Returns:
        {
            "scan_date": str,
            "base_path": str,
            "projects_scanned": int,
            "ai_projects_found": int,
            "risk_distribution": {"prohibited": N, "high_risk": N, "limited_risk": N, "minimal_risk": N, "not_ai": N},
            "projects": [discovery_dict, ...]
        }
    """
    results = []
    project_indicators = {".git", "package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml", "setup.py"}

    base = Path(base_path).resolve()
    for entry in sorted(base.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue
        # Check if this looks like a project
        if any((entry / indicator).exists() for indicator in project_indicators):
            try:
                discovery = discover(str(entry))
                results.append(discovery)
                if register:
                    register_system(discovery)
            except Exception:  # Intentional: multiple error sources
                continue

    risk_dist = Counter()
    for r in results:
        risk_dist[r.get("highest_risk", "not_ai")] += 1

    return {
        "scan_date": datetime.now(timezone.utc).isoformat(),
        "base_path": str(base),
        "projects_scanned": len(results),
        "ai_projects_found": sum(1 for r in results if r.get("highest_risk", "not_ai") != "not_ai"),
        "risk_distribution": dict(risk_dist),
        "projects": results,
    }


def generate_eu_registration(project_name: str) -> dict:
    """Generate EU AI Database registration format for a registered system.

    Per Article 49(1), providers of high-risk AI systems must register
    the system in the EU database before placing it on the market.

    Returns a dict with the required registration fields.
    """
    registry = load_registry()
    system = registry.get("systems", {}).get(project_name)
    if not system:
        return {"error": f"System '{project_name}' not found in registry"}

    # Load governance contacts from policy
    if check_optional("classify_risk", "governance contacts for registry", "included with regula"):
        from classify_risk import get_governance_contacts, get_policy
        contacts = get_governance_contacts()
        policy = get_policy()
    else:
        contacts = {}
        policy = {}

    ai_officer = contacts.get("ai_officer", {})
    organisation = policy.get("organisation", "")

    return {
        "registration_type": "high_risk_ai_system",
        "article": "49(1)",
        "system_name": project_name,
        "provider_name": organisation or "[TO BE COMPLETED]",
        "provider_contact": ai_officer.get("email", "[TO BE COMPLETED]"),
        "intended_purpose": "[TO BE COMPLETED — describe the system's intended purpose]",
        "risk_classification": system.get("highest_risk", "unknown"),
        "ai_libraries": system.get("ai_libraries", []),
        "model_files": [m.get("path", "") for m in system.get("model_files", [])],
        "compliance_status": system.get("compliance_status", "not_started"),
        "last_scanned": system.get("last_scanned", ""),
        "registration_date": datetime.now(timezone.utc).isoformat(),
        "note": "Auto-generated by Regula. Fields marked [TO BE COMPLETED] require manual input before submission.",
    }


def format_registry_csv(registry: dict = None) -> str:
    """Export the full registry as CSV for DPO inventory management."""
    import csv, io

    if registry is None:
        registry = load_registry()

    systems = registry.get("systems", {})
    if not systems:
        return "No systems registered.\n"

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "System Name", "Risk Classification", "Compliance Status",
        "AI Libraries", "Model Files", "Last Scanned", "Project Path"
    ])

    for name, info in systems.items():
        writer.writerow([
            name,
            info.get("highest_risk", "unknown").upper().replace("_", "-"),
            info.get("compliance_status", "not_started"),
            "; ".join(info.get("ai_libraries", [])),
            str(len(info.get("model_files", []))),
            info.get("last_scanned", "")[:10],
            info.get("project_path", ""),
        ])

    return output.getvalue()


def print_discovery(discovery: dict) -> None:
    """Print discovery results in human-readable format."""
    print(f"\n{'=' * 60}")
    print(f"  Regula System Discovery: {discovery['project_name']}")
    print(f"{'=' * 60}")
    print(f"  Path:           {discovery['project_path']}")
    print(f"  Language:        {discovery['primary_language'] or 'Unknown'}")
    print(f"  Highest Risk:    {discovery['highest_risk'].upper().replace('_', '-')}")
    print(f"  AI Libraries:    {len(discovery['ai_libraries'])}")
    print(f"  Model Files:     {len(discovery['model_files'])}")
    print(f"  AI Code Files:   {len(discovery['ai_code_files'])}")
    print(f"  API Endpoints:   {len(discovery['api_endpoints'])}")

    if discovery["ai_libraries"]:
        print(f"\n  Libraries: {', '.join(discovery['ai_libraries'])}")

    if discovery["model_files"]:
        print(f"\n  Model Files:")
        for mf in discovery["model_files"]:
            print(f"    - {mf['path']} ({mf['size_mb']} MB)")

    if discovery["api_endpoints"]:
        print(f"\n  API Endpoints: {', '.join(discovery['api_endpoints'])}")

    if discovery["risk_classifications"]:
        print(f"\n  Risk Classifications:")
        for rc in discovery["risk_classifications"]:
            tier = rc['tier'].upper().replace('_', '-')
            print(f"    - {rc['file']}: {tier} ({rc['description']})")

    print(f"{'=' * 60}\n")


def update_compliance_status(project_name: str, new_status: str, note: str = "") -> dict:
    """Update the compliance status of a registered system.

    Returns the updated registry entry or raises ValueError for invalid transitions.
    """
    if new_status not in COMPLIANCE_STATUSES:
        raise ValueError(f"Invalid status '{new_status}'. Valid: {', '.join(COMPLIANCE_STATUSES)}")

    registry = load_registry()
    systems = registry.get("systems", {})

    if project_name not in systems:
        raise ValueError(f"System '{project_name}' not found in registry. Run 'regula discover --register' first.")

    current = systems[project_name].get("compliance_status", "not_started")
    allowed = COMPLIANCE_TRANSITIONS.get(current, [])

    if new_status not in allowed and new_status != current:
        raise ValueError(
            f"Cannot transition from '{current}' to '{new_status}'. "
            f"Allowed transitions: {', '.join(allowed)}"
        )

    systems[project_name]["compliance_status"] = new_status
    systems[project_name]["compliance_updated"] = datetime.now(timezone.utc).isoformat()

    # Maintain a compliance history log
    history = systems[project_name].get("compliance_history", [])
    history.append({
        "from": current,
        "to": new_status,
        "date": datetime.now(timezone.utc).isoformat(),
        "note": note,
    })
    systems[project_name]["compliance_history"] = history

    if note:
        systems[project_name]["notes"] = note

    save_registry(registry)

    try:
        from log_event import log_event
        log_event("compliance_status_change", {
            "project": project_name,
            "from_status": current,
            "to_status": new_status,
            "note": note,
        })
    except (OSError,):
        pass

    return systems[project_name]


def print_registry_status() -> None:
    """Print the full registry status."""
    registry = load_registry()
    systems = registry.get("systems", {})

    if not systems:
        print("No systems registered. Run with --register to add systems.")
        return

    print(f"\n{'=' * 60}")
    print(f"  Regula System Registry — {len(systems)} system(s)")
    print(f"{'=' * 60}")

    for name, info in systems.items():
        risk = info.get("highest_risk", "unknown").upper().replace("_", "-")
        status = info.get("compliance_status", "unknown")
        libs = len(info.get("ai_libraries", []))
        last = info.get("last_scanned", "never")[:10]
        print(f"  {name:<30} {risk:<15} {status:<15} {libs} libs  (scanned: {last})")

    print(f"{'=' * 60}\n")


def main():
    parser = argparse.ArgumentParser(description="Discover and register AI systems")
    parser.add_argument("--project", "-p", default=".", help="Project directory to scan")
    parser.add_argument("--register", "-r", action="store_true", help="Register in persistent registry")
    parser.add_argument("--status", "-s", action="store_true", help="Show registry status")
    parser.add_argument("--compliance", help="Update compliance status: SYSTEM_NAME:STATUS[:NOTE]")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    if args.compliance:
        parts = args.compliance.split(":", 2)
        name = parts[0]
        status = parts[1] if len(parts) > 1 else ""
        note = parts[2] if len(parts) > 2 else ""

        if not status:
            # Show current status and allowed transitions
            registry = load_registry()
            system = registry.get("systems", {}).get(name)
            if not system:
                print(f"System '{name}' not found.", file=sys.stderr)
                sys.exit(1)
            current = system.get("compliance_status", "not_started")
            allowed = COMPLIANCE_TRANSITIONS.get(current, [])
            print(f"\n  System: {name}")
            print(f"  Current status: {current}")
            print(f"  Allowed transitions: {', '.join(allowed)}")
            print(f"\n  Workflow: not_started → assessment → implementing → compliant → review_due")
            history = system.get("compliance_history", [])
            if history:
                print(f"\n  History:")
                for h in history[-5:]:
                    print(f"    {h['date'][:10]}: {h['from']} → {h['to']}{' — ' + h['note'] if h.get('note') else ''}")
            print()
            return

        try:
            entry = update_compliance_status(name, status, note)
            print(f"Updated '{name}' compliance status to '{status}'")
            if note:
                print(f"Note: {note}")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    if args.status:
        print_registry_status()
        return

    discovery = discover(args.project)

    if args.format == "json":
        print(json.dumps(discovery, indent=2))
    else:
        print_discovery(discovery)

    if args.register:
        register_system(discovery)
        print(f"System '{discovery['project_name']}' registered in {REGISTRY_PATH}")


if __name__ == "__main__":
    main()
