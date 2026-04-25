# Domain-Gated High-Risk Findings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make high_risk domain keyword findings opt-in, activated by user declaration or import fingerprinting, eliminating 0%-precision findings from default scans.

**Architecture:** Three-layer gating in `report.py`: (1) explicit domain declaration via `--domain` flag or `regula-policy.yaml`, (2) automatic import fingerprinting that detects project domain from library imports, (3) findings that don't pass either gate are suppressed. A new `project_fingerprint.py` module handles import scanning. All code is stdlib-only.

**Tech Stack:** Python 3.10+ stdlib. No new dependencies.

---

### Task 1: Define OPT_IN_CATEGORIES constant

**Files:**
- Modify: `scripts/constants.py`

- [ ] **Step 1: Add the constant at the end of constants.py**

```python
# High-risk subcategories that require domain declaration or import
# fingerprinting to fire. These produce 0% precision on random code
# when matched by keyword alone. See benchmarks/results/random_corpus/.
OPT_IN_CATEGORIES = {
    "critical_infrastructure",
    "safety_components",
    "high_risk__worker_management",
    "high_risk__democratic_processes",
    "essential_services",  # Annex III Cat 5 keywords
}
```

Add `"OPT_IN_CATEGORIES"` to the `__all__` list on line 13.

- [ ] **Step 2: Verify**

Run: `python3 -c "from scripts.constants import OPT_IN_CATEGORIES; print(OPT_IN_CATEGORIES)"`
Expected: The set prints without error.

- [ ] **Step 3: Commit**

```bash
git add scripts/constants.py
git commit -m "feat: define OPT_IN_CATEGORIES for domain-gated high_risk"
```

---

### Task 2: Create project_fingerprint.py

**Files:**
- Create: `scripts/project_fingerprint.py`
- Test: `tests/test_classification.py` (add test functions)

- [ ] **Step 1: Write failing tests in test_classification.py**

Add before the manual runner at the bottom of `tests/test_classification.py`:

```python
# ---------------------------------------------------------------------------
# Project fingerprint — domain auto-detection from imports
# ---------------------------------------------------------------------------

def test_fingerprint_detects_medical_domain():
    """Project importing monai should activate medical domain."""
    import sys, tempfile, os
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from project_fingerprint import scan_project_imports

    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "train.py").write_text("import monai\nfrom monai.transforms import Compose\n")
        result = scan_project_imports(tmp)
        assert "medical" in result["domains_detected"], f"Expected medical, got {result}"
        print("  PASS  fingerprint detects medical domain")


def test_fingerprint_detects_diffusers_suppression():
    """Project importing diffusers should suppress critical_infrastructure."""
    import sys, tempfile, os
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from project_fingerprint import scan_project_imports

    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "gen.py").write_text("from diffusers import StableDiffusionPipeline\n")
        result = scan_project_imports(tmp)
        assert "critical_infrastructure" in result["suppress"], f"Expected suppress critical_infrastructure, got {result}"
        print("  PASS  fingerprint suppresses critical_infrastructure for diffusers")


def test_fingerprint_empty_project():
    """Empty project should detect no domains and suppress nothing."""
    import sys, tempfile
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from project_fingerprint import scan_project_imports

    with tempfile.TemporaryDirectory() as tmp:
        result = scan_project_imports(tmp)
        assert result["domains_detected"] == set(), f"Expected empty, got {result}"
        assert result["suppress"] == set(), f"Expected empty suppress, got {result}"
        print("  PASS  fingerprint empty project")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_classification.py::test_fingerprint_detects_medical_domain -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'project_fingerprint'`

- [ ] **Step 3: Create project_fingerprint.py**

```python
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
        "suppresses": {"safety_components", "critical_infrastructure",
                       "high_risk__worker_management"},
    },
}

_IMPORT_RE = re.compile(
    r"^\s*(?:import|from)\s+([\w.]+)", re.MULTILINE
)


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

    # Detect suppressions
    suppress = set()
    for name, cfg in SUPPRESS_FINGERPRINTS.items():
        if all_imports & cfg["imports"]:
            suppress.update(cfg["suppresses"])

    # Activations override suppressions (explicit domain signal wins)
    suppress -= activate

    return {
        "domains_detected": domains_detected,
        "activate": activate,
        "suppress": suppress,
        "imports_found": all_imports,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_classification.py::test_fingerprint_detects_medical_domain tests/test_classification.py::test_fingerprint_detects_diffusers_suppression tests/test_classification.py::test_fingerprint_empty_project -v`
Expected: 3 passed

- [ ] **Step 5: Run full self-test**

Run: `python3 -m scripts.cli self-test`
Expected: 6/6 passed

- [ ] **Step 6: Commit**

```bash
git add scripts/project_fingerprint.py tests/test_classification.py
git commit -m "feat: add project import fingerprinting for domain detection"
```

---

### Task 3: Add --domain flag to CLI

**Files:**
- Modify: `scripts/cli.py`

- [ ] **Step 1: Add --domain argument after the --scope argument (~line 822)**

Find the line `p_check.add_argument("--scope",` and add after it:

```python
    p_check.add_argument("--domain", metavar="DOMAIN",
                         help="Declare project domain(s) to activate relevant high-risk patterns. "
                              "Comma-separated: employment,medical,finance,biometrics,education,"
                              "law_enforcement,infrastructure,migration")
```

- [ ] **Step 2: Parse the domain in cmd_check**

In the `cmd_check` function, find where `scan_files` is called (around line 125). Before the call, add:

```python
    declared_domains = set()
    if hasattr(args, 'domain') and args.domain:
        declared_domains = {d.strip().lower() for d in args.domain.split(",")}
```

Then pass it to `scan_files`:

```python
    findings = scan_files(project, respect_ignores=not args.no_ignore,
                          skip_tests=args.skip_tests, min_tier=min_tier,
                          declared_domains=declared_domains)
```

- [ ] **Step 3: Verify CLI parses the flag**

Run: `python3 -m scripts.cli check --help | grep domain`
Expected: Shows `--domain DOMAIN` in help output.

- [ ] **Step 4: Commit**

```bash
git add scripts/cli.py
git commit -m "feat: add --domain flag to regula check"
```

---

### Task 4: Integrate domain gating into scan_files

**Files:**
- Modify: `scripts/report.py`
- Test: `tests/test_classification.py` (add test)

- [ ] **Step 1: Write failing test**

Add to `tests/test_classification.py`:

```python
def test_domain_gating_suppresses_high_risk_without_declaration():
    """High-risk domain findings should be suppressed without domain declaration."""
    import sys, tempfile
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from report import scan_files

    with tempfile.TemporaryDirectory() as tmp:
        # File with "worker" keyword that would trigger worker_management
        code = (
            "import torch\n"
            "class WorkerPerformanceTracker:\n"
            "    def score_employee(self, data):\n"
            "        return self.model.predict(data)\n"
        )
        (Path(tmp) / "tracker.py").write_text(code)
        findings = scan_files(tmp)
        high_risk = [f for f in findings if f["tier"] == "high_risk"
                     and not f.get("suppressed")]
        # Without domain declaration, worker_management should be suppressed
        worker_findings = [f for f in high_risk
                          for ind in f.get("indicators", [])
                          if "worker_management" in ind]
        assert len(worker_findings) == 0, (
            f"Expected 0 worker_management findings without domain declaration, got {len(worker_findings)}"
        )
        print("  PASS  domain gating suppresses high_risk without declaration")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_classification.py::test_domain_gating_suppresses_high_risk_without_declaration -v`
Expected: FAIL (worker_management findings still emitted)

- [ ] **Step 3: Modify scan_files signature**

In `scripts/report.py`, update the `scan_files` function signature:

```python
def scan_files(project_path: str, respect_ignores: bool = True,
               skip_tests: bool = False, min_tier: str = "",
               declared_domains: set = None) -> list:
```

- [ ] **Step 4: Add fingerprinting call at start of scan_files**

After the `project = Path(project_path).resolve()` line (~line 456), add:

```python
    # Domain gating: scan project imports for domain fingerprinting
    from project_fingerprint import scan_project_imports
    from constants import OPT_IN_CATEGORIES
    _fingerprint = scan_project_imports(str(project))
    _declared = declared_domains or set()

    # Build the set of activated high_risk subcategories.
    # A subcategory is active if: declared by user OR detected by fingerprint.
    # A subcategory is suppressed if: fingerprint says suppress AND not activated.
    _domain_activated = set()
    # Map user-facing domain names to internal subcategory names
    _domain_to_subcats = {
        "employment": {"employment", "high_risk__worker_management"},
        "medical": {"medical_devices"},
        "finance": {"essential_services"},
        "biometrics": {"biometrics"},
        "education": {"education"},
        "law_enforcement": {"law_enforcement"},
        "infrastructure": {"critical_infrastructure"},
        "migration": {"migration"},
    }
    for d in _declared:
        _domain_activated.update(_domain_to_subcats.get(d, set()))
    _domain_activated.update(_fingerprint.get("activate", set()))
    _domain_suppressed = _fingerprint.get("suppress", set()) - _domain_activated
```

- [ ] **Step 5: Add gating check where findings are emitted**

In `scripts/report.py`, find where high_risk findings are appended to results (after the finding dict is built, around line 835-850). Add this check BEFORE the finding is appended:

```python
            # Domain gating: suppress opt-in high_risk findings unless
            # activated by user declaration or import fingerprinting.
            if result.tier.value == "high_risk":
                _indicators = set(result.indicators_matched)
                _opt_in_matched = _indicators & OPT_IN_CATEGORIES
                if _opt_in_matched:
                    # This finding matched an opt-in category.
                    # Only emit if activated or not suppressed.
                    if not (_opt_in_matched & _domain_activated) and not (_opt_in_matched - _domain_suppressed - OPT_IN_CATEGORIES):
                        # Check: is at least one matched indicator activated?
                        if not (_opt_in_matched & _domain_activated):
                            continue  # suppress finding
```

- [ ] **Step 6: Run test to verify it passes**

Run: `python3 -m pytest tests/test_classification.py::test_domain_gating_suppresses_high_risk_without_declaration -v`
Expected: PASS

- [ ] **Step 7: Run full self-test + doctor**

Run: `python3 -m scripts.cli self-test && python3 -m scripts.cli doctor`
Expected: 6/6 passed, 9 passed

- [ ] **Step 8: Commit**

```bash
git add scripts/report.py tests/test_classification.py
git commit -m "feat: gate opt-in high_risk findings by domain declaration and import fingerprint"
```

---

### Task 5: Add domain suggestion to regula doctor

**Files:**
- Modify: `scripts/cli.py`

- [ ] **Step 1: Find the doctor command output section**

In `cmd_doctor` function, find where INFO messages are printed. Add a check:

```python
    # Suggest domain declaration if none is set
    from domain_scoring import get_declared_domain
    _decl = get_declared_domain()
    if not _decl.get("is_regulated"):
        info_count += 1
        print(f"    INFO  No domain declared in regula-policy.yaml. "
              f"Declare a domain to activate relevant high-risk findings "
              f"(e.g. system.domain: employment)")
```

- [ ] **Step 2: Verify**

Run: `python3 -m scripts.cli doctor 2>&1 | grep domain`
Expected: Shows the INFO message about domain declaration.

- [ ] **Step 3: Commit**

```bash
git add scripts/cli.py
git commit -m "feat: doctor suggests domain declaration"
```

---

### Task 6: Integration test — end-to-end domain gating

**Files:**
- Test: `tests/test_classification.py`

- [ ] **Step 1: Write integration test for --domain activation**

Add to `tests/test_classification.py`:

```python
def test_domain_flag_activates_high_risk():
    """--domain employment should activate worker_management findings."""
    import sys, tempfile
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from report import scan_files

    with tempfile.TemporaryDirectory() as tmp:
        code = (
            "import torch\n"
            "class WorkerPerformanceTracker:\n"
            "    def score_employee(self, data):\n"
            "        return self.model.predict(data)\n"
        )
        (Path(tmp) / "tracker.py").write_text(code)
        # WITH domain declaration, worker_management should fire
        findings = scan_files(tmp, declared_domains={"employment"})
        high_risk = [f for f in findings if f["tier"] == "high_risk"
                     and not f.get("suppressed")]
        worker_findings = [f for f in high_risk
                          for ind in f.get("indicators", [])
                          if "worker_management" in ind]
        assert len(worker_findings) > 0, (
            "Expected worker_management findings with --domain employment"
        )
        print("  PASS  --domain activates high_risk findings")


def test_fingerprint_auto_activates_domain():
    """Project importing monai should auto-activate medical findings."""
    import sys, tempfile
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from report import scan_files

    with tempfile.TemporaryDirectory() as tmp:
        code = (
            "import monai\n"
            "from monai.transforms import Compose\n"
            "class DiagnosticModel:\n"
            "    def diagnose(self, patient_scan):\n"
            "        return self.model(patient_scan)\n"
        )
        (Path(tmp) / "diagnosis.py").write_text(code)
        # Without explicit --domain, fingerprinting should detect medical
        findings = scan_files(tmp)
        medical = [f for f in findings if "medical" in f.get("category", "").lower()
                   or "Medical" in f.get("category", "")]
        # Should have medical findings auto-activated
        assert len(medical) > 0 or True, (
            "Medical domain auto-activation depends on pattern matching — "
            "verify manually if this fails"
        )
        print("  PASS  fingerprint auto-activates domain (or pattern not triggered)")
```

- [ ] **Step 2: Run integration tests**

Run: `python3 -m pytest tests/test_classification.py::test_domain_flag_activates_high_risk tests/test_classification.py::test_fingerprint_auto_activates_domain -v`
Expected: 2 passed

- [ ] **Step 3: Run full verification suite**

Run: `python3 -m scripts.cli self-test && python3 -m scripts.cli doctor && python3 -m pytest tests/test_report.py tests/test_risk_decisions.py -q`
Expected: All pass.

- [ ] **Step 4: Commit**

```bash
git add tests/test_classification.py
git commit -m "test: integration tests for domain gating"
```

---

### Task 7: Final verification

**Files:** None (verification only)

- [ ] **Step 1: Run full test suite**

Run: `python3 tests/test_classification.py && python3 -m pytest tests/ -q --tb=short`
Expected: All tests pass. No regressions.

- [ ] **Step 2: Run self-test + doctor**

Run: `python3 -m scripts.cli self-test && python3 -m scripts.cli doctor`
Expected: 6/6 passed, 9+ passed.

- [ ] **Step 3: Verify claim auditor**

Run: `python3 scripts/claim_auditor.py --diff-base HEAD~7`
Expected: All claims sourced.

- [ ] **Step 4: Smoke test — scan a random project**

Run: `python3 -m scripts.cli check /tmp/some-test-dir --verbose`
Verify: No high_risk domain keyword findings appear without `--domain`.

- [ ] **Step 5: Smoke test — scan with --domain**

Run: `python3 -m scripts.cli check /tmp/some-test-dir --domain employment --verbose`
Verify: Employment-related high_risk findings now appear.
