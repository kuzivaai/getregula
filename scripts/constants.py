# regula-ignore
"""
Shared constants for Regula.

Single source of truth for version, file extensions, skip directories, and
model file types. All scanner modules import from here to prevent divergence.

History: CODE_EXTENSIONS was defined in 4 separate files and diverged —
report.py had 12 extensions while discover_ai_systems.py had 7, causing
Regula to claim "8 languages" while actually scanning fewer.
"""

__all__ = ["VERSION", "CODE_EXTENSIONS", "SKIP_DIRS", "MODEL_EXTENSIONS"]

VERSION = "1.7.0"

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
}

# Model file extensions (binary ML model files).
MODEL_EXTENSIONS = {
    ".onnx", ".pt", ".pth", ".pkl", ".joblib",
    ".h5", ".hdf5", ".safetensors",
    ".gguf", ".ggml",
}
