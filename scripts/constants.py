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

VERSION = "1.5.1"

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
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__",
    "venv", ".venv",
    "dist", "build",
    ".next", ".tox",
    "egg-info",
}

# Model file extensions (binary ML model files).
MODEL_EXTENSIONS = {
    ".onnx", ".pt", ".pth", ".pkl", ".joblib",
    ".h5", ".hdf5", ".safetensors",
    ".gguf", ".ggml",
}
