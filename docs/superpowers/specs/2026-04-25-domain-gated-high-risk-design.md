# Domain-Gated High-Risk Findings

**Date:** 2026-04-25
**Status:** Approved
**Problem:** High-risk domain keyword patterns produce 0% precision on random Python AI projects (verified on 50-repo blind-labelled benchmark). Five of six high_risk subcategories generate zero true positives on random code. The word "worker" means "compute process" in 99% of Python AI repos. The word "pipeline" means "ML pipeline" not "gas pipeline."

## Design

### Principle

Domain-specific high_risk findings are noise unless the project actually operates in that domain. Make them **opt-in**: disabled by default, activated when the user declares their domain or when import fingerprinting detects it automatically.

### What stays enabled by default (no declaration needed)

These tiers have >40% precision on random code using code-pattern matching (not keywords):

| Tier | Default precision | Why it works |
|------|-------------------|--------------|
| `prohibited` | Always on | Article 5 — cannot be suppressed |
| `ai_security` | 80% | Matches on deserialization, API calls, prompt patterns |
| `agent_autonomy` | 83% | Matches on subprocess, HTTP, file writes near AI code |
| `limited_risk` | 88% | Matches on synthetic content generation, chatbot patterns |
| `minimal_risk` | 100% | Matches on model file extensions |
| `credential_exposure` | 100% | Matches on key/token patterns |
| `biometrics` (Category 1) | 40% | Only high_risk subcategory with TPs on random code |

### What becomes opt-in

These subcategories have 0% precision on random code — domain keywords match without semantic context:

| Subcategory | Pattern | Why it fails on random code |
|-------------|---------|----------------------------|
| `critical_infrastructure` (Cat 2) | "pipeline", "grid", "control" | ML pipelines, CSS grids, ControlNet |
| `safety_components` | "safety" | Model safety, not EU harmonisation |
| `worker_management` (Cat 4b) | "worker", "task allocation" | Compute workers, ML task queues |
| `employment` (Cat 4) | "hiring", "performance review" | Code review, ML performance |
| `democratic_processes` (Cat 8) | "justice", "vote" | Translation content, NMS voting |
| `education` (Cat 3) | "student", "grade", "exam" | Gradient, examination of data |
| `law_enforcement` (Cat 6) | "evidence", "investigation" | Debug investigation, test evidence |
| `migration` (Cat 7) | "migration", "border" | Database migration, tensor border |

### Three activation layers

**Layer 1: Explicit domain declaration (immediate implementation)**

Users declare their domain via CLI flag or policy file. Only declared-relevant high_risk patterns fire.

```bash
# CLI flag
regula check . --domain employment
regula check . --domain medical,employment

# Policy file (regula-policy.yaml)
system:
  domain: employment
  risk_level: high
```

When domain is declared:
- All opt-in patterns for that domain are activated
- Other opt-in patterns remain suppressed
- All default-on tiers continue as normal

When no domain is declared:
- Opt-in patterns are suppressed
- Default-on tiers fire normally
- `regula doctor` suggests: "Consider declaring your domain for more relevant findings"

**Layer 2: Import fingerprinting (auto-detection)**

Scan project imports once at start of scan. If domain-specific libraries are detected, auto-enable relevant high_risk patterns without user declaration.

```python
# Hardcoded in project_fingerprint.py (new file)
DOMAIN_FINGERPRINTS = {
    "medical": {
        "imports": ["monai", "nibabel", "pydicom", "SimpleITK", "medpy",
                     "torchio", "dicom", "hl7"],
        "activates": ["medical_devices"],
    },
    "employment": {
        "imports": ["resume_parser", "pyresparser", "spacy_ke",
                     "job_parser", "ats_parser"],
        "activates": ["employment", "worker_management"],
    },
    "finance": {
        "imports": ["yfinance", "fredapi", "ta", "bt", "zipline",
                     "pyalgotrade", "quantlib"],
        "activates": ["finance"],
    },
    "biometrics": {
        "imports": ["deepface", "face_recognition", "dlib",
                     "insightface", "arcface"],
        "activates": ["biometrics"],
    },
    "education": {
        "imports": ["edx_platform", "moodle", "canvas_api",
                     "blackboard", "gradescope"],
        "activates": ["education"],
    },
    "law_enforcement": {
        "imports": ["crime_analysis", "forensic", "ballistics"],
        "activates": ["law_enforcement"],
    },
    "infrastructure": {
        "imports": ["pymodbus", "opcua", "scada", "pycomm3",
                     "openplc"],
        "activates": ["critical_infrastructure"],
    },
}

# Negative fingerprints — suppress domain even if keywords match
SUPPRESS_FINGERPRINTS = {
    "NOT_infrastructure": {
        "imports": ["diffusers", "controlnet_aux", "stable_diffusion",
                     "transformers", "accelerate"],
        "suppresses": ["critical_infrastructure", "safety_components"],
    },
    "NOT_employment": {
        "imports": ["multiprocessing", "celery", "ray", "dask",
                     "joblib", "concurrent.futures"],
        "suppresses": ["employment", "worker_management"],
    },
}
```

Import fingerprinting runs automatically — no user action needed. It supplements, not replaces, explicit domain declaration. Explicit declaration always takes priority.

**Layer 3: LLM triage (optional, future)**

For findings that survive layers 1 and 2, optional `--smart` flag pipes finding + code context through an LLM for semantic validation. This is a future enhancement, not part of the initial implementation.

### Integration point

In `report.py`, after a high_risk finding is generated but before it's added to results:

```python
# Pseudocode for the gating logic
if finding.tier == "high_risk" and finding.category in OPT_IN_CATEGORIES:
    # Layer 1: check explicit declaration
    if declared_domain and finding.category in domain_to_categories[declared_domain]:
        pass  # emit finding
    # Layer 2: check import fingerprint
    elif project_fingerprint.activates(finding.category):
        pass  # emit finding
    else:
        continue  # suppress finding
```

### What changes in the codebase

| File | Change |
|------|--------|
| `scripts/project_fingerprint.py` | **New.** Import scanning + domain fingerprint logic |
| `scripts/report.py` | Add fingerprint call at scan start. Gate high_risk findings. |
| `scripts/domain_scoring.py` | Connect declared domain to gating (partially exists) |
| `scripts/cli.py` | Add `--domain` flag to `check` command |
| `scripts/constants.py` | Add `OPT_IN_CATEGORIES` set |
| `tests/test_classification.py` | Tests for domain gating + fingerprint logic |

### What does NOT change

- `cli.py` monolith structure
- `risk_patterns.py` pattern definitions (patterns still exist, just gated)
- `json_output()` envelope format
- Bare import convention
- `regula assess` questionnaire (it already sets domain)

### Success criteria

1. Default `regula check` on a random AI project produces zero high_risk domain keyword FPs
2. `regula check --domain employment` on Resume-Matcher produces employment findings
3. Import fingerprinting auto-enables medical findings on MONAI without `--domain`
4. Existing tests continue to pass
5. `regula doctor` suggests domain declaration when none is set

### Limitations

- Import fingerprinting requires maintaining a library-to-domain mapping. New frameworks need mapping additions.
- Some projects use ambiguous imports. Import fingerprinting is best-effort, not guaranteed.
- Biometrics (Category 1) stays on by default at 40% precision — this is a judgment call. It catches real facial recognition code (DeepFace, dlib) but also matches on speech processing libraries. If precision is unacceptable, it can be moved to opt-in in a future iteration.
- The 70% benchmark number was measured BEFORE this change. Post-implementation precision must be re-measured to make claims.

### Data backing

All design decisions are based on the blind-labelled random corpus benchmark (50 repos, 201 findings, 140 production). Specific data points:

- 5 of 6 high_risk subcategories: 0 TPs on random code (verified)
- Biometrics: 2 TPs, 3 FPs = 40% (verified)
- 20 of 34 mixed-project FPs caused by project-level domain mismatch (verified)
- Import fingerprinting catches all 20 project-context FPs in the benchmark (verified)
- Phase 0 fixes (pipeline_controlnet, worker exclusion, LLM import gating) are deployed but not yet re-measured
