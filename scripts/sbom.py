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

# ── Regula version (imported from single source of truth) ─────────
from constants import VERSION as REGULA_VERSION

# ── Import existing Regula modules with fallbacks ─────────────────

sys.path.insert(0, str(Path(__file__).parent))
from degradation import check_optional

if check_optional("ast_engine", "AST analysis for SBOM", "included with regula"):
    from ast_engine import analyse_project
else:
    def analyse_project(project_path: str) -> list:
        return []

if check_optional("dependency_scan", "dependency scanning for SBOM", "included with regula"):
    from dependency_scan import (
        scan_dependencies,
        is_ai_dependency,
        AI_LIBRARIES,
        _normalize,
        check_compromised,
    )
else:
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

if check_optional("classify_risk", "risk classification for SBOM", "included with regula"):
    from classify_risk import classify
else:
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
    except (subprocess.SubprocessError, OSError):
        pass
    return "0.0.0"


# ── GPAI tier → EU AI Act article mapping ────────────────────────

_GPAI_TIER_ARTICLES = {
    "frontier": "Art 51, Art 53, Art 54, Art 55",
    "open_weight": "Art 53(1)(c), Art 53(1)(d), Art 53(2)",
    "unknown": "Art 53 (tier unconfirmed — manual review required)",
}

# ── Dataset detection patterns ───────────────────────────────────

_DATASET_PATTERNS = [
    # (regex, source_label)
    (re.compile(r'''datasets\.load_dataset\(\s*["']([^"']+)["']'''), "huggingface-datasets"),
    (re.compile(r'''pd\.read_csv\(\s*["']([^"']+)["']'''), "pandas-csv"),
    (re.compile(r'''pd\.read_parquet\(\s*["']([^"']+)["']'''), "pandas-parquet"),
    # DataLoader takes a variable, not a string literal — capture for context only
    (re.compile(r'''DataLoader\(\s*(\w+)'''), "pytorch-dataloader-var"),
    (re.compile(r'''tf\.data\.Dataset'''), "tensorflow-dataset"),
]

_DATASET_SCAN_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs"}
_DATASET_SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "env", ".env", "dist", "build", ".next", ".nuxt",
    "coverage", ".tox", ".mypy_cache",
}


def _scan_datasets(project_path: str) -> list[dict]:
    """Scan project for dataset loading patterns."""
    root = Path(project_path)
    datasets: list[dict] = []
    seen: set[str] = set()

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _DATASET_SKIP_DIRS]
        for fname in filenames:
            ext = Path(fname).suffix.lower()
            if ext not in _DATASET_SCAN_EXTENSIONS:
                continue
            fpath = Path(dirpath, fname)
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            rel = str(fpath.relative_to(root))
            for lineno, line in enumerate(content.splitlines(), 1):
                for pattern, source_label in _DATASET_PATTERNS:
                    m = pattern.search(line)
                    if m:
                        dataset_name = m.group(1) if m.lastindex else source_label
                        key = f"{source_label}:{dataset_name}"
                        if key not in seen:
                            seen.add(key)
                            datasets.append({
                                "name": dataset_name,
                                "source_pattern": source_label,
                                "file": rel,
                                "line": lineno,
                            })
    return datasets


def _enrich_ai_bom(project_path: str, components: list[dict],
                   seen_names: set[str]) -> tuple[list[dict], list[dict]]:
    """Enrich SBOM components with AI BOM data.

    Returns (updated_components, extra_metadata_properties).
    """
    extra_meta: list[dict] = []

    # ── Model provenance ─────────────────────────────────────────
    try:
        from model_inventory import scan_for_models
        model_result = scan_for_models(project_path)
    except ImportError:
        model_result = {"models": [], "summary": {"total": 0}}

    # Filter models: skip those only found in regula-ignore files (e.g. catalogues)
    root = Path(project_path).resolve()
    models_found = model_result.get("models", [])
    for model in models_found:
        model_id = model["model_id"]
        comp_key = f"ai-model:{model_id}"
        if comp_key in seen_names:
            continue

        # Check if ALL occurrences are in regula-ignore files
        occurrences = model.get("occurrences", [])
        real_occurrences = []
        for occ in occurrences:
            occ_path = root / occ.get("file", "")
            try:
                first_lines = "\n".join(occ_path.read_text(encoding="utf-8", errors="ignore").split("\n")[:10])
                if "regula-ignore" in first_lines and "regula-ignore:" not in first_lines:
                    continue  # This occurrence is in a catalogue/config file
            except (OSError, PermissionError):
                pass
            real_occurrences.append(occ)

        if not real_occurrences:
            continue  # All occurrences were in regula-ignore files — skip this model

        seen_names.add(comp_key)

        gpai_tier = model.get("gpai_tier", "unknown")
        provider = model.get("provider", "unknown")
        eu_note = model.get("eu_note", "")
        eu_articles = _GPAI_TIER_ARTICLES.get(gpai_tier, _GPAI_TIER_ARTICLES["unknown"])
        occurrences = real_occurrences  # Use filtered list, not original

        # Build properties
        props = [
            {"name": "regula:gpai-tier", "value": gpai_tier},
            {"name": "regula:provider", "value": provider},
            {"name": "regula:eu-note", "value": eu_note},
            {"name": "regula:eu-ai-act-articles", "value": eu_articles},
        ]
        # Add first occurrence as source reference
        if occurrences:
            props.append({"name": "regula:source-file", "value": occurrences[0]["file"]})
            props.append({"name": "regula:source-line", "value": str(occurrences[0]["line"])})

        component: dict = {
            "type": "machine-learning-model",
            "name": model_id,
            "properties": props,
        }

        # CycloneDX 1.6 modelCard — approach.type must be from the spec enum
        model_params: dict = {}
        if provider != "unknown":
            model_params["owner"] = provider
        model_card: dict = {"modelParameters": model_params} if model_params else {}
        component["modelCard"] = model_card

        components.append(component)

    extra_meta.append({
        "name": "regula:ai-bom-models-detected",
        "value": str(len(models_found)),
    })

    # ── Dataset detection ────────────────────────────────────────
    datasets = _scan_datasets(project_path)
    for ds in datasets:
        ds_key = f"dataset:{ds['source_pattern']}:{ds['name']}"
        if ds_key in seen_names:
            continue
        seen_names.add(ds_key)

        components.append({
            "type": "data",
            "name": ds["name"],
            "properties": [
                {"name": "regula:source-pattern", "value": ds["source_pattern"]},
                {"name": "regula:source-file", "value": ds["file"]},
                {"name": "regula:source-line", "value": str(ds["line"])},
            ],
        })

    extra_meta.append({
        "name": "regula:ai-bom-datasets-detected",
        "value": str(len(datasets)),
    })

    return components, extra_meta


# ── Main SBOM generation ─────────────────────────────────────────

def generate_sbom(project_path: str, project_name: str | None = None,
                   ai_bom: bool = False) -> dict:
    """Generate a CycloneDX 1.6 AI SBOM for a project.

    Parameters
    ----------
    project_path : str
        Path to the project root directory.
    project_name : str, optional
        Human-readable project name. Defaults to directory name.
    ai_bom : bool
        When True, enrich with model provenance, GPAI tiers, and dataset
        detection (AI Bill of Materials mode).

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
                except (ValueError, TypeError):
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

    # ── AI BOM enrichment ─────────────────────────────────────────
    if ai_bom:
        components, bom_meta_extra = _enrich_ai_bom(str(root), components, seen_names)

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
    meta_props = [
        {"name": "regula:pinning-score", "value": str(pinning_score)},
        {"name": "regula:ai-files-scanned", "value": str(len(ast_results))},
    ]
    if ai_bom:
        meta_props.append({"name": "regula:ai-bom", "value": "true"})
        for p in bom_meta_extra:
            meta_props.append(p)
    bom["metadata"]["properties"] = meta_props

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
