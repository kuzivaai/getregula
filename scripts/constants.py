# regula-ignore
"""
Shared constants for Regula.

Single source of truth for version, file extensions, skip directories, and
model file types. All scanner modules import from here to prevent divergence.

History: CODE_EXTENSIONS was defined in 4 separate files and diverged —
report.py had 12 extensions while discover_ai_systems.py had 7, causing
Regula to claim "8 languages" while actually scanning fewer.
"""

__all__ = ["VERSION", "CODE_EXTENSIONS", "SKIP_DIRS", "MODEL_EXTENSIONS", "OPT_IN_CATEGORIES",
           "MAX_FILE_SIZE_BYTES", "MAX_CLASSIFY_CHARS"]

VERSION = "1.7.7"

# Threat model (Phase 5, 2026-07-13): a scanned repository is untrusted input
# (e.g. a third-party PR scanned in CI). Two controls close verified gaps:
#   1. File-size ceiling — filepath.read_bytes() previously had no limit, so
#      a single huge file (accidental or adversarial) could exhaust memory.
#      10 MB comfortably covers real-world source files (large minified
#      bundles usually live under dist/build, already in SKIP_DIRS) while
#      bounding worst-case memory use per file.
#   2. Symlink-escape check (see report.py:_resolve_safe) — a symlink inside
#      the scan root that points outside it let Regula read arbitrary files
#      reachable by the scanning process (CI secrets, SSH keys, etc.).
#      Verified via reproduction: a symlink to a file outside the project
#      root was followed and its content scanned before this fix.
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB per file

# Classification-time content cap (Phase 5 threat model, continued 2026-07-14).
# Empirically measured: several built-in prohibited/high-risk patterns use a
# `(?:word1|word2)[^"\n]{0,30}(?:word3|word4)` shape. Applied via re.search()
# against WHOLE-FILE content (not per-line), dense adversarial repetition of
# the leading trigger word degrades near-linearly with content length: a
# single such pattern took 2.48s against a 10MB file saturated with a
# trigger word, and the full 4-call classification pipeline
# (check_prohibited/check_high_risk/check_limited_risk/check_bias_risk) took
# 27.8s at MAX_FILE_SIZE_BYTES on adversarial content. This is bounded
# (not exponential ReDoS) but is a real CPU-exhaustion vector on a scanned
# repository, which must be treated as untrusted input.
#
# The largest legitimate source file in this codebase is ~95 KB. 1 MB is a
# generous ceiling for real code (10x+ margin) while keeping worst-case
# adversarial classification time to ~3s per file (empirically measured).
# Content beyond this cap is truncated for CLASSIFICATION PURPOSES ONLY
# (the file is still fully readable/hashable elsewhere); the truncation is
# recorded as a dangerous skip so the scan is honestly reported as partial —
# a pattern could be hiding past the cap, consistent with the DEF-004/DEF-005
# principle that partial analysis must never present as a clean completion.
MAX_CLASSIFY_CHARS = 1 * 1024 * 1024  # 1 MB

# File extensions scanned for AI patterns and risk classification.
# Covers: Python, JavaScript, TypeScript, Java, Go, Rust, C, C++, Jupyter notebooks
CODE_EXTENSIONS = {
    ".py",
    ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
    ".java",
    ".go",
    ".rs",
    ".c", ".cpp",
    ".ipynb",
}

# Directories skipped during recursive scanning.
#
# `benchmarks` is in this set because it contains test infrastructure:
# synthetic fixtures with intentional prohibited/high-risk patterns,
# and cached scan results for OSS projects. Including it in a default
# `regula check .` would produce noise for users and false high-risk
# findings on Regula's own repo. The synthetic-fixture runner passes
# the absolute fixture path explicitly, so it bypasses this skip.
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__",
    "venv", ".venv",
    "dist", "build",
    ".next", ".tox",
    "egg-info",
    "benchmarks",
    # Example/demo directories are not production code — scanning them
    # inflates false positives by 23% (benchmarked on 5 OSS projects).
    "examples", "example", "demos", "demo",
    # CI/CD infrastructure is not application code. Same rationale as
    # Semgrep's default .semgrepignore which excludes .github/.
    ".github", ".gitlab", ".circleci",
    # Tool caches and generated output — never production code. Folded in
    # from per-module copies during the July 2026 SKIP_DIRS consolidation;
    # every scanner path must import THIS set (plus explicit local unions),
    # never define its own. Six independently-drifted copies shipped once.
    "env", ".env", ".nuxt", "coverage", ".nyc_output", ".mypy_cache",
    ".ruff_cache", ".pytest_cache", ".nox", "site-packages",
}

# Model file extensions (binary ML model files).
MODEL_EXTENSIONS = {
    ".onnx", ".pt", ".pth", ".pkl", ".joblib",
    ".h5", ".hdf5", ".safetensors",
    ".gguf", ".ggml",
}

# High-risk subcategories that require domain declaration or import
# fingerprinting to fire. These produce 0% precision on random code
# when matched by keyword alone. See benchmarks/results/random_corpus/.
OPT_IN_CATEGORIES = {
    "critical_infrastructure",
    "safety_components",
    "high_risk__worker_management",
    "high_risk__democratic_processes",
    # "justice" is Annex III Cat 8 (judicial decisions, election influence).
    # Benchmark shows 0 TP / 3 FP on random code — keyword patterns fire on
    # legal-text NLP tools and translation software. Requires --domain
    # law_enforcement or explicit fingerprint to activate.
    "justice",
    "essential_services",
    # The three categories below had 0 true positives in the dev corpus benchmark
    # and only produced false positives (employment: 4 FP, law_enforcement: 3 FP,
    # migration: 0 FP but noisy). They are gated behind domain declaration or
    # import fingerprinting to prevent false positives on generic code.
    "employment",
    "law_enforcement",
    "migration",
}
