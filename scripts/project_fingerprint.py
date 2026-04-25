# regula-ignore
"""
Project-level import fingerprinting for domain auto-detection.

Scans all Python files in a project for import statements and matches
against known domain-specific libraries. Used to automatically gate
high_risk findings that would otherwise produce false positives.

Run once per project scan, not per file.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from constants import CODE_EXTENSIONS, SKIP_DIRS

__all__ = ["scan_project_imports"]

# Libraries that indicate a specific regulatory domain.
# When detected, the corresponding high_risk subcategories are activated.
DOMAIN_FINGERPRINTS = {
    "medical": {
        "imports": {"monai", "nibabel", "pydicom", "simpleitk", "medpy",
                    "torchio", "dicom", "hl7", "fhir", "medcat"},
        "activates": {"medical_devices"},
    },
    "employment": {
        "imports": {"resume_parser", "pyresparser", "job_parser",
                    "ats_parser", "hr_toolkit"},
        "activates": {"employment", "high_risk__worker_management"},
    },
    "finance": {
        "imports": {"yfinance", "fredapi", "ta", "zipline",
                    "quantlib", "pyalgotrade", "bt"},
        "activates": {"essential_services"},
    },
    "biometrics": {
        "imports": {"deepface", "face_recognition", "insightface",
                    "arcface"},
        "activates": {"biometrics"},
    },
    "education": {
        "imports": {"edx_platform", "canvas_api", "gradescope",
                    "moodle_api"},
        "activates": {"education"},
    },
    "law_enforcement": {
        "imports": {"crime_analysis", "forensic_toolkit", "ballistics"},
        "activates": {"law_enforcement"},
    },
    "infrastructure": {
        "imports": {"pymodbus", "opcua", "pycomm3", "openplc",
                    "scada_toolkit"},
        "activates": {"critical_infrastructure"},
    },
}

# Libraries that indicate the project is NOT in a regulated domain.
# When detected, specific high_risk subcategories are suppressed
# even if domain keywords appear in the code.
SUPPRESS_FINGERPRINTS = {
    "ml_framework": {
        "imports": {"diffusers", "controlnet_aux", "stable_diffusion",
                    "accelerate", "peft", "trl"},
        "suppresses": {"critical_infrastructure", "safety_components"},
    },
    "compute_infra": {
        "imports": {"celery", "ray", "dask", "joblib"},
        "suppresses": {"high_risk__worker_management"},
    },
    "speech_audio": {
        "imports": {"lhotse", "speechbrain", "espnet", "kaldi",
                    "pyaudioanalysis", "librosa"},
        "suppresses": {"biometrics"},
    },
    "physics_simulation": {
        "imports": {"deepmd", "ase", "lammps", "gromacs",
                    "openmm", "mdtraj"},
        # employment suppressed: molecular dynamics / physics sim code uses
        # "worker" for compute processes and "validation" for model checks,
        # not for employment decisions (benchmark: 0 TP, 1 FP on deepmd).
        "suppresses": {"safety_components", "critical_infrastructure",
                       "high_risk__worker_management", "employment"},
    },
}

_IMPORT_RE = re.compile(
    r"^\s*(?:import|from)\s+([\w.]+)", re.MULTILINE
)
_PYPROJECT_NAME_RE = re.compile(
    r'^\s*name\s*=\s*["\']([^"\']+)["\']', re.MULTILINE
)


def _get_project_name(project_path):
    """Extract package name from pyproject.toml or setup.py.

    Used for library self-detection: when a library is scanning its own
    source tree, internal files often use relative imports and won't appear
    in the import fingerprint. Reading the package name directly avoids this.
    """
    p = Path(project_path)
    for candidate in (p / "pyproject.toml", p / "setup.py", p / "setup.cfg"):
        if candidate.exists():
            try:
                content = candidate.read_text(encoding="utf-8", errors="replace")
                m = _PYPROJECT_NAME_RE.search(content)
                if m:
                    return m.group(1).lower().replace("-", "_")
            except OSError:
                pass
    return None


def _extract_imports(filepath):
    """Extract top-level module names from import statements."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return set()

    modules = set()
    for match in _IMPORT_RE.finditer(content):
        top_module = match.group(1).split(".")[0].lower()
        modules.add(top_module)
    return modules


def scan_project_imports(project_path):
    """Scan project imports and return domain detection results.

    Returns:
        {
            "domains_detected": set of domain names,
            "activate": set of high_risk subcategories to activate,
            "suppress": set of high_risk subcategories to suppress,
            "imports_found": set of all top-level imports,
        }
    """
    project = Path(project_path).resolve()
    all_imports = set()

    for ext in CODE_EXTENSIONS:
        if ext != ".py":
            continue  # Fingerprinting is Python-only for now
        for filepath in project.rglob(f"*{ext}"):
            # Skip directories we always skip
            if any(skip in filepath.parts for skip in SKIP_DIRS):
                continue
            all_imports.update(_extract_imports(filepath))

    # Detect domains
    domains_detected = set()
    activate = set()
    for domain, cfg in DOMAIN_FINGERPRINTS.items():
        if all_imports & cfg["imports"]:
            domains_detected.add(domain)
            activate.update(cfg["activates"])

    # Detect suppressions from import fingerprint
    suppress = set()
    for name, cfg in SUPPRESS_FINGERPRINTS.items():
        if all_imports & cfg["imports"]:
            suppress.update(cfg["suppresses"])

    # Library self-detection: when a library scans its own source tree,
    # internal files use relative imports that won't appear in the fingerprint.
    # Reading the package name from pyproject.toml / setup.py catches this case.
    # Example: lhotse scanning itself won't have `import lhotse` in its own files,
    # but its pyproject.toml says name = "lhotse" → speech_audio suppression applies.
    project_name = _get_project_name(str(project))
    if project_name:
        for cfg in SUPPRESS_FINGERPRINTS.values():
            norm_imports = {i.replace("-", "_") for i in cfg["imports"]}
            if project_name in norm_imports:
                suppress.update(cfg["suppresses"])

    # Activations override suppressions (explicit domain signal wins)
    suppress -= activate

    return {
        "domains_detected": domains_detected,
        "activate": activate,
        "suppress": suppress,
        "imports_found": all_imports,
    }
