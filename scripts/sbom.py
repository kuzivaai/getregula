# regula-ignore
#!/usr/bin/env python3
"""CycloneDX 1.6 AI Software Bill of Materials (SBOM) generator.

Generates CycloneDX 1.6 JSON BOMs with AI-specific components, model file
detection, and vulnerability tracking for compromised packages.

No external dependencies required — stdlib only.
"""

import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ── Regula version ────────────────────────────────────────────────
REGULA_VERSION = "1.2.0"

# ── Import existing Regula modules with fallbacks ─────────────────

sys.path.insert(0, str(Path(__file__).parent))

try:
    from ast_engine import analyse_project
except ImportError:
    def analyse_project(project_path: str) -> list:
        return []

try:
    from dependency_scan import (
        scan_dependencies,
        is_ai_dependency,
        AI_LIBRARIES,
        _normalize,
        check_compromised,
    )
except ImportError:
    AI_LIBRARIES = set()

    def scan_dependencies(project_path: str) -> dict:
        return {
            "all_dependencies": [],
            "ai_dependencies": [],
            "lockfiles": [],
            "pinning_score": 100,
            "compromised": [],
        }

    def is_ai_dependency(name: str) -> bool:
        return False

    def _normalize(name: str) -> str:
        return re.sub(r"[-_.]+", "-", name.strip().lower())

    def check_compromised(deps: list) -> list:
        return []

try:
    from classify_risk import classify
except ImportError:
    classify = None


# ── Model file extensions ─────────────────────────────────────────

MODEL_EXTENSIONS = {
    ".onnx", ".pt", ".pth", ".pkl", ".safetensors",
    ".gguf", ".ggml", ".h5", ".hdf5", ".joblib",
}

# ── AI Frameworks (subset of AI_LIBRARIES that are frameworks) ────

AI_FRAMEWORKS = {
    "pytorch", "torch", "tensorflow", "jax", "keras", "flax",
}

# ── PURL ecosystem mapping ────────────────────────────────────────

# Map dependency file names to PURL type
_DEP_FILE_PURL_TYPE = {
    "requirements.txt": "pypi",
    "pyproject.toml": "pypi",
    "Pipfile": "pypi",
    "setup.py": "pypi",
    "setup.cfg": "pypi",
    "package.json": "npm",
    "Cargo.toml": "cargo",
    "go.mod": "golang",
    "pom.xml": "maven",
    "build.gradle": "maven",
}


def _guess_purl_type(project_path: str) -> str:
    """Guess the package URL type from files present in the project."""
    root = Path(project_path)
    # Check in priority order
    for fname, purl_type in _DEP_FILE_PURL_TYPE.items():
        if (root / fname).exists():
            return purl_type
    return "pypi"  # default


def _make_purl(name: str, version: str | None, purl_type: str) -> str | None:
    """Build a Package URL string."""
    if not name:
        return None
    # Handle npm scoped packages
    if purl_type == "npm" and name.startswith("@"):
        encoded = name.replace("@", "%40", 1).replace("/", "/", 1)
        base = f"pkg:{purl_type}/{encoded}"
    else:
        norm = _normalize(name)
        base = f"pkg:{purl_type}/{norm}"
    if version:
        return f"{base}@{version}"
    return base


# ── Model file scanner ────────────────────────────────────────────

def _scan_model_files(project_path: str) -> list[dict]:
    """Scan project for ML model files."""
    root = Path(project_path)
    models = []

    skip_dirs = {
        "node_modules", ".git", "__pycache__", ".venv", "venv",
        "env", ".env", "dist", "build", ".next", ".nuxt",
        "coverage", ".tox", ".mypy_cache",
    }

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fname in filenames:
            ext = Path(fname).suffix.lower()
            if ext in MODEL_EXTENSIONS:
                rel_path = str(Path(dirpath, fname).relative_to(root))
                models.append({
                    "name": fname,
                    "file_path": rel_path,
                    "extension": ext,
                })
    return models


# ── Project version detection ─────────────────────────────────────

def _detect_project_version(project_path: str) -> str:
    """Try to detect project version from git hash or fallback."""
    root = Path(project_path)
    # Try git
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(root), capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return "0.0.0"


# ── Main SBOM generation ─────────────────────────────────────────

def generate_sbom(project_path: str, project_name: str | None = None) -> dict:
    """Generate a CycloneDX 1.6 AI SBOM for a project.

    Parameters
    ----------
    project_path : str
        Path to the project root directory.
    project_name : str, optional
        Human-readable project name. Defaults to directory name.

    Returns
    -------
    dict
        A CycloneDX 1.6 compliant BOM dictionary.
    """
    root = Path(project_path).resolve()
    if project_name is None:
        project_name = root.name

    # ── Gather data ───────────────────────────────────────────────
    # AST engine: find AI source files
    ast_results = analyse_project(str(root))

    # Dependency scan: find dependency info
    dep_results = scan_dependencies(str(root))
    all_deps = dep_results.get("all_dependencies", [])
    pinning_score = dep_results.get("pinning_score", 100)

    # Model files
    model_files = _scan_model_files(str(root))

    # Compromised packages
    compromised = dep_results.get("compromised", [])

    # Detect PURL type
    purl_type = _guess_purl_type(str(root))

    # ── Build components ──────────────────────────────────────────
    components = []
    seen_names = set()  # avoid duplicates

    # 1. Dependencies
    for dep in all_deps:
        name = dep.get("name", "")
        if not name or name in seen_names:
            continue
        seen_names.add(name)

        norm_name = _normalize(name)
        is_ai = dep.get("is_ai", False)
        version = dep.get("version")
        pinning = dep.get("pinning", "unpinned")

        # Determine component type
        if norm_name in {_normalize(f) for f in AI_FRAMEWORKS}:
            comp_type = "framework"
        elif is_ai:
            comp_type = "library"
        else:
            comp_type = "library"

        component: dict = {
            "type": comp_type,
            "name": name,
        }
        if version:
            component["version"] = version

        purl = _make_purl(name, version, purl_type)
        if purl:
            component["purl"] = purl

        # Add regula properties for AI libraries
        if is_ai:
            props = [
                {"name": "regula:is-ai-library", "value": "true"},
                {"name": "regula:pinning-quality", "value": pinning},
            ]
            # Add risk tier if classifier is available
            if classify is not None:
                try:
                    risk_result = classify(f"import {name}")
                    props.append({
                        "name": "regula:risk-tier",
                        "value": risk_result.tier.value,
                    })
                except Exception:
                    pass
            component["properties"] = props

        components.append(component)

    # 2. Model files
    for model in model_files:
        mname = model["name"]
        if mname in seen_names:
            continue
        seen_names.add(mname)

        components.append({
            "type": "machine-learning-model",
            "name": mname,
            "properties": [
                {"name": "regula:file-path", "value": model["file_path"]},
                {"name": "regula:file-extension", "value": model["extension"]},
            ],
        })

    # ── Build vulnerabilities ─────────────────────────────────────
    vulnerabilities = []
    for i, finding in enumerate(compromised):
        adv_id = finding.get("advisory_id", f"REGULA-{i+1:04d}")
        pkg_name = finding.get("package", "unknown")
        pkg_version = finding.get("version", "")
        severity = finding.get("severity", "critical")
        description = finding.get("description", "")

        purl = _make_purl(pkg_name, pkg_version, purl_type)

        vuln: dict = {
            "id": adv_id,
            "source": {
                "name": "Regula Advisory Database",
                "url": "https://github.com/kuzivaai/getregula",
            },
            "description": description,
            "ratings": [{"severity": severity, "method": "other"}],
        }
        if purl:
            vuln["affects"] = [{"ref": purl}]

        vulnerabilities.append(vuln)

    # ── Assemble BOM ──────────────────────────────────────────────
    bom: dict = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "version": 1,
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "metadata": {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tools": {
                "components": [{
                    "type": "application",
                    "name": "regula",
                    "version": REGULA_VERSION,
                }],
            },
            "component": {
                "type": "application",
                "name": project_name,
                "version": _detect_project_version(str(root)),
            },
        },
        "components": components,
    }

    if vulnerabilities:
        bom["vulnerabilities"] = vulnerabilities

    # Store pinning score in metadata properties for summary use
    bom["metadata"]["properties"] = [
        {"name": "regula:pinning-score", "value": str(pinning_score)},
        {"name": "regula:ai-files-scanned", "value": str(len(ast_results))},
    ]

    return bom


# ── Formatters ────────────────────────────────────────────────────

def format_sbom_json(sbom: dict) -> str:
    """Pretty-print SBOM as JSON string."""
    return json.dumps(sbom, indent=2, default=str)


def format_sbom_summary(sbom: dict) -> str:
    """Generate a human-readable text summary of the SBOM."""
    lines: list[str] = []

    # Header
    meta = sbom.get("metadata", {})
    proj = meta.get("component", {})
    proj_name = proj.get("name", "unknown")
    timestamp = meta.get("timestamp", "unknown")
    tool_version = REGULA_VERSION
    tools = meta.get("tools", {}).get("components", [])
    if tools:
        tool_version = tools[0].get("version", REGULA_VERSION)

    lines.append(f"AI Software Bill of Materials: {proj_name}")
    lines.append(f"Generated: {timestamp} by Regula v{tool_version}")
    lines.append("")

    # Components breakdown
    components = sbom.get("components", [])
    ai_libs = []
    ml_models = []
    frameworks = []
    other = []

    for c in components:
        ctype = c.get("type", "")
        is_ai = any(
            p.get("name") == "regula:is-ai-library" and p.get("value") == "true"
            for p in c.get("properties", [])
        )
        if ctype == "machine-learning-model":
            ml_models.append(c)
        elif ctype == "framework":
            frameworks.append(c)
        elif is_ai:
            ai_libs.append(c)
        else:
            other.append(c)

    lines.append(f"Components: {len(components)}")
    if ai_libs:
        names = ", ".join(c["name"] for c in ai_libs)
        lines.append(f"  AI Libraries: {len(ai_libs)} ({names})")
    if ml_models:
        names = ", ".join(c["name"] for c in ml_models)
        lines.append(f"  ML Models: {len(ml_models)} ({names})")
    if frameworks:
        names = ", ".join(c["name"] for c in frameworks)
        lines.append(f"  Frameworks: {len(frameworks)} ({names})")
    if other:
        lines.append(f"  Other: {len(other)}")
    lines.append("")

    # Vulnerabilities
    vulns = sbom.get("vulnerabilities", [])
    if vulns:
        lines.append(f"Vulnerabilities: {len(vulns)}")
        for v in vulns:
            severity = "UNKNOWN"
            ratings = v.get("ratings", [])
            if ratings:
                severity = ratings[0].get("severity", "unknown").upper()
            affects = v.get("affects", [])
            ref = affects[0].get("ref", "") if affects else ""
            desc = v.get("description", "")
            # Extract package name and version from ref
            if ref:
                lines.append(f"  {severity}: {ref} — {desc}")
            else:
                lines.append(f"  {severity}: {desc}")
        lines.append("")

    # Pinning score
    meta_props = meta.get("properties", [])
    pinning = "N/A"
    for p in meta_props:
        if p.get("name") == "regula:pinning-score":
            pinning = p.get("value", "N/A")
            break
    lines.append(f"Pinning Score: {pinning}/100")

    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate CycloneDX 1.6 AI SBOM for a project"
    )
    parser.add_argument(
        "--project", "-p",
        default=".",
        help="Path to project directory (default: current directory)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "text"],
        default="json",
        help="Output format: json (CycloneDX BOM) or text (human summary)",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--name", "-n",
        help="Project name (default: directory name)",
    )
    args = parser.parse_args()

    project_path = os.path.abspath(args.project)
    if not os.path.isdir(project_path):
        print(f"Error: '{project_path}' is not a directory", file=sys.stderr)
        sys.exit(1)

    sbom = generate_sbom(project_path, project_name=args.name)

    if args.format == "json":
        output = format_sbom_json(sbom)
    else:
        output = format_sbom_summary(sbom)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"SBOM written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
