#!/usr/bin/env python3
"""
Regula System Registry — AI System Discovery and Inventory
Scans projects for AI components and maintains a persistent registry.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from classify_risk import classify, RiskTier, is_ai_related, AI_INDICATORS


REGISTRY_PATH = Path(os.environ.get("REGULA_REGISTRY", Path.home() / ".regula" / "registry.json"))

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
CODE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs"}
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
        existing.update({
            "last_scanned": discovery["discovered_at"],
            "ai_libraries": discovery["ai_libraries"],
            "model_files": discovery["model_files"],
            "ai_code_files": discovery["ai_code_files"],
            "api_endpoints": discovery["api_endpoints"],
            "risk_classifications": discovery["risk_classifications"],
            "highest_risk": discovery["highest_risk"],
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
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

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
