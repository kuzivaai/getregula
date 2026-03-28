# regula-ignore
#!/usr/bin/env python3
"""AI dependency supply chain security scanner.

Checks AI dependency pinning quality, lockfile presence, and generates
remediation commands. Addresses risks like the LiteLLM supply chain attack
(March 2026) where unpinned AI dependencies led to compromised packages.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from degradation import check_optional

# ── AI Library Registry ────────────────────────────────────────────

AI_LIBRARIES: set[str] = {
    # Python ML/DL frameworks
    "tensorflow", "torch", "pytorch", "keras", "jax", "flax",
    # Transformers ecosystem
    "transformers", "sentence-transformers", "peft", "trl",
    "accelerate", "datasets", "diffusers", "safetensors",
    "huggingface-hub", "tokenizers",
    # LLM providers / wrappers
    "openai", "anthropic", "cohere", "litellm", "vllm",
    "replicate", "together", "mistralai", "groq",
    # LangChain ecosystem
    "langchain", "langchain-core", "langchain-community",
    "langchain-openai", "langchain-anthropic", "langchain-google-genai",
    # LlamaIndex
    "llama-index", "llama-index-core",
    # Classical ML
    "sklearn", "scikit-learn", "xgboost", "lightgbm", "catboost",
    # NLP
    "spacy", "nltk", "gensim",
    # Local inference
    "llama-cpp-python", "ctransformers",
    # Structured generation / agents
    "instructor", "outlines", "dspy-ai", "guidance",
    "semantic-kernel", "autogen", "crewai", "phidata",
    # Vector databases
    "chromadb", "pinecone-client", "weaviate-client",
    "qdrant-client", "milvus",
    # Document processing
    "unstructured",
    # Model serving / UI
    "gradio", "streamlit", "bentoml",
    # Experiment tracking / MLOps
    "mlflow", "wandb", "optuna", "sagemaker", "ray",
    # ONNX
    "onnx", "onnxruntime",
    # Haystack
    "haystack-ai",
    # JavaScript / TypeScript (npm names)
    "@anthropic-ai/sdk", "@tensorflow/tfjs",
    "@langchain/core", "brain.js", "@xenova/transformers",
    "@huggingface/inference",
    "@pinecone-database/pinecone",
    "@qdrant/js-client-rest", "weaviate-ts-client",
    "ai",
    # Rust crates (use hyphens, the Cargo.toml format)
    "candle-core", "candle-nn", "candle-transformers",
    "burn", "burn-core", "burn-tch", "burn-ndarray",
    "tch", "ort", "rust-bert",
    "async-openai", "anthropic", "misanthropic",
    "langchain-rust", "llm-chain",
    "tokenizers", "safetensors", "hf-hub",
    "linfa", "smartcore",
    "qdrant-client",
    # C++ packages (vcpkg/conan names)
    "libtorch", "tensorflow-lite",
    "mlpack", "dlib", "faiss",
}

# Alias mapping for normalized names that should match
_AI_ALIASES: dict[str, str] = {
    "pytorch": "torch",
    "sklearn": "scikit-learn",
}

LOCKFILE_NAMES: set[str] = {
    "Pipfile.lock",
    "poetry.lock",
    "uv.lock",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lockb",
    ".conda-lock.yml",
    "conda-lock.yml",
    "Cargo.lock",
}

# ── Helpers ────────────────────────────────────────────────────────

def _normalize(name: str) -> str:
    """Normalize package name: lowercase, replace underscores with hyphens."""
    return re.sub(r"[-_.]+", "-", name.strip().lower())


def is_ai_dependency(name: str) -> bool:
    """Check whether a package name is a known AI library."""
    norm = _normalize(name)
    # Direct match
    if norm in {_normalize(lib) for lib in AI_LIBRARIES}:
        return True
    # Alias match
    if norm in {_normalize(k) for k in _AI_ALIASES}:
        return True
    canonical = _AI_ALIASES.get(norm)
    if canonical and _normalize(canonical) in {_normalize(lib) for lib in AI_LIBRARIES}:
        return True
    return False


# Pre-compute normalised set for performance
_NORMALISED_AI: set[str] | None = None

def _get_normalised_ai() -> set[str]:
    global _NORMALISED_AI
    if _NORMALISED_AI is None:
        _NORMALISED_AI = {_normalize(lib) for lib in AI_LIBRARIES}
        _NORMALISED_AI.update(_normalize(k) for k in _AI_ALIASES)
    return _NORMALISED_AI


def is_ai_dependency(name: str) -> bool:  # noqa: F811 — intentional redefinition
    """Check whether a package name is a known AI library."""
    return _normalize(name) in _get_normalised_ai()


# ── Pinning detection ──────────────────────────────────────────────

_REQ_SPEC_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9_@/.][A-Za-z0-9_\-@/. ]*?)(?:\[.*?\])?\s*"
    r"(?P<spec>(?:--hash=|==|~=|!=|>=|<=|>|<).*)?$"
)


def _classify_pinning_req(spec: str | None) -> tuple[str, str | None]:
    """Return (pinning_level, version_or_None) for a requirement specifier."""
    if not spec:
        return "unpinned", None
    spec = spec.strip()
    if spec.startswith("--hash="):
        return "hash", None
    if spec.startswith("=="):
        return "exact", spec[2:].strip()
    if spec.startswith("~="):
        return "compatible", spec[2:].strip()
    # Any other specifier is a range
    for op in (">=", "<=", "!=", ">", "<"):
        if op in spec:
            ver = spec.split(op, 1)[1].split(",")[0].strip()
            return "range", ver
    return "unpinned", None


# ── Parsers ────────────────────────────────────────────────────────

def parse_requirements_txt(content: str) -> list[dict]:
    """Parse a requirements.txt file content."""
    deps: list[dict] = []
    line_num = 0
    continued = ""
    for raw_line in content.splitlines():
        line_num += 1
        line = raw_line.strip()
        # Handle continuation
        if continued:
            line = continued + line
            continued = ""
        if line.endswith("\\"):
            continued = line[:-1].strip() + " "
            continue
        # Skip blanks, comments, options
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        # Remove inline comments
        if " #" in line:
            line = line[:line.index(" #")].strip()
        # Handle hash pinning
        has_hash = "--hash=" in line
        if has_hash:
            # Extract name and spec before hash options
            parts = line.split("--hash=")[0].strip()
            line = parts

        m = _REQ_SPEC_RE.match(line)
        if not m:
            continue

        name = m.group("name").strip()
        spec_str = m.group("spec")

        if has_hash:
            pinning = "hash"
            version = None
            if spec_str and spec_str.startswith("=="):
                version = spec_str[2:].strip()
        else:
            pinning, version = _classify_pinning_req(spec_str)

        deps.append({
            "name": name,
            "version": version,
            "pinning": pinning,
            "is_ai": is_ai_dependency(name),
            "line": line_num,
        })
    return deps


def parse_pyproject_toml(content: str) -> list[dict]:
    """Parse dependencies from pyproject.toml using regex (no tomllib)."""
    deps: list[dict] = []
    line_num = 0

    # Find [project.dependencies] array
    dep_pattern = re.compile(
        r'\[project\].*?dependencies\s*=\s*\[(.*?)\]',
        re.DOTALL
    )
    # Also try [project.dependencies] directly
    dep_pattern2 = re.compile(
        r'\[project\.dependencies\]',
    )

    # Strategy: find dependencies = [...] in [project] section
    # and [project.optional-dependencies.*] sections
    all_dep_strings: list[tuple[str, int]] = []

    # Match dependencies = [ ... ]  (multiline)
    for m in re.finditer(r'dependencies\s*=\s*\[([^\]]*)\]', content, re.DOTALL):
        block = m.group(1)
        start_line = content[:m.start()].count('\n') + 1
        for i, raw in enumerate(block.splitlines()):
            line = raw.strip().strip(',').strip()
            if not line or line.startswith('#'):
                continue
            # Remove quotes
            line = line.strip('"').strip("'")
            if line:
                all_dep_strings.append((line, start_line + i))

    # Match optional-dependencies sections
    for m in re.finditer(
        r'\[project\.optional-dependencies\.(\w+)\]\s*\n(.*?)(?=\n\[|\Z)',
        content, re.DOTALL
    ):
        # This format isn't standard TOML for arrays, try the = [...] form
        pass

    for m in re.finditer(
        r'\[project\.optional-dependencies\]\s*\n(.*?)(?=\n\[|\Z)',
        content, re.DOTALL
    ):
        block = m.group(1)
        start_line = content[:m.start()].count('\n') + 1
        # Parse key = [...] entries
        for km in re.finditer(r'\w+\s*=\s*\[([^\]]*)\]', block, re.DOTALL):
            sub = km.group(1)
            sub_start = start_line + block[:km.start()].count('\n')
            for i, raw in enumerate(sub.splitlines()):
                line = raw.strip().strip(',').strip()
                if not line or line.startswith('#'):
                    continue
                line = line.strip('"').strip("'")
                if line:
                    all_dep_strings.append((line, sub_start + i))

    # Parse each dependency string like "openai>=1.0" or "torch"
    for dep_str, ln in all_dep_strings:
        m2 = _REQ_SPEC_RE.match(dep_str)
        if not m2:
            continue
        name = m2.group("name").strip()
        spec_str = m2.group("spec")
        pinning, version = _classify_pinning_req(spec_str)
        deps.append({
            "name": name,
            "version": version,
            "pinning": pinning,
            "is_ai": is_ai_dependency(name),
            "line": ln,
        })
    return deps


def parse_package_json(content: str) -> list[dict]:
    """Parse dependencies from package.json content."""
    deps: list[dict] = []
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return deps

    for section in ("dependencies", "devDependencies"):
        entries = data.get(section, {})
        if not isinstance(entries, dict):
            continue
        for name, ver_str in entries.items():
            ver_str = str(ver_str).strip()
            if ver_str in ("*", "latest", ""):
                pinning = "unpinned"
                version = None
            elif ver_str.startswith("^") or ver_str.startswith("~"):
                pinning = "range"
                version = ver_str[1:]
            elif ver_str.startswith(">=") or ver_str.startswith("<=") or ver_str.startswith(">") or ver_str.startswith("<"):
                pinning = "range"
                version = ver_str.lstrip(">=<").strip()
            elif re.match(r'^\d', ver_str):
                pinning = "exact"
                version = ver_str
            else:
                pinning = "range"
                version = ver_str

            deps.append({
                "name": name,
                "version": version,
                "pinning": pinning,
                "is_ai": is_ai_dependency(name),
                "line": 0,
            })
    return deps


def parse_pipfile(content: str) -> list[dict]:
    """Parse dependencies from Pipfile content."""
    deps: list[dict] = []
    current_section: str | None = None
    line_num = 0

    for raw_line in content.splitlines():
        line_num += 1
        line = raw_line.strip()

        # Section headers
        if line.startswith("["):
            section = line.strip("[]").strip().lower()
            if section in ("packages", "dev-packages"):
                current_section = section
            else:
                current_section = None
            continue

        if current_section is None:
            continue

        if not line or line.startswith("#"):
            continue

        # Parse key = value
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        name = key.strip().strip('"').strip("'")
        val = val.strip().strip('"').strip("'")

        if val == "*":
            pinning, version = "unpinned", None
        elif val.startswith("=="):
            pinning, version = "exact", val[2:].strip()
        elif val.startswith("~="):
            pinning, version = "compatible", val[2:].strip()
        elif any(val.startswith(op) for op in (">=", "<=", "!=", ">", "<")):
            for op in (">=", "<=", "!=", ">", "<"):
                if val.startswith(op):
                    version = val[len(op):].split(",")[0].strip()
                    break
            pinning = "range"
        else:
            # Could be a dict-like spec: {version = "==1.0"}
            vm = re.search(r'version\s*=\s*"([^"]*)"', val)
            if vm:
                spec = vm.group(1)
                pinning, version = _classify_pinning_req(spec)
            else:
                pinning, version = "unpinned", None

        deps.append({
            "name": name,
            "version": version,
            "pinning": pinning,
            "is_ai": is_ai_dependency(name),
            "line": line_num,
        })
    return deps


# ── Cargo.toml parser ──────────────────────────────────────────────

def parse_cargo_toml(content: str) -> list[dict]:
    """Parse dependencies from Cargo.toml content.

    Handles both:
      crate-name = "version"
      crate-name = { version = "version", features = [...] }
    """
    deps: list[dict] = []
    in_dependencies = False
    line_num = 0

    for raw_line in content.splitlines():
        line_num += 1
        line = raw_line.strip()

        # Section detection
        if line.startswith("["):
            section = line.strip("[]").strip().lower()
            # Match [dependencies], [dev-dependencies], [build-dependencies]
            # but NOT [package] or other sections
            in_dependencies = section in (
                "dependencies", "dev-dependencies", "build-dependencies",
            )
            continue

        if not in_dependencies:
            continue

        if not line or line.startswith("#"):
            continue

        # Parse  name = "version"  or  name = { version = "...", ... }
        if "=" not in line:
            continue

        key, _, val = line.partition("=")
        name = key.strip().strip('"').strip("'")
        val = val.strip()

        if not name:
            continue

        # Inline table: { version = "...", ... }
        if val.startswith("{"):
            vm = re.search(r'version\s*=\s*["\']([^"\']*)["\']', val)
            version_str = vm.group(1) if vm else None
        else:
            # Simple string value
            version_str = val.strip('"').strip("'")

        # Classify pinning
        if version_str is None or version_str == "*":
            pinning = "unpinned"
            version = None
        elif version_str.startswith("="):
            # Exact: "=1.2.3"
            pinning = "exact"
            version = version_str[1:].strip()
        elif version_str.startswith("^") or version_str.startswith("~"):
            pinning = "range"
            version = version_str[1:].strip()
        elif any(version_str.startswith(op) for op in (">=", "<=", ">", "<")):
            pinning = "range"
            version = re.sub(r'^[><=]+', '', version_str).split(",")[0].strip()
        else:
            # Plain semver like "1.0" or "0.8.0" — semver compatible, treat as range
            pinning = "range"
            version = version_str

        # Normalise hyphens to underscores for AI library matching
        # (Cargo uses hyphens, Rust source uses underscores — keep original name)
        deps.append({
            "name": name,
            "version": version,
            "pinning": pinning,
            "is_ai": is_ai_dependency(name),
            "line": line_num,
        })

    return deps


# ── CMakeLists.txt parser ───────────────────────────────────────────

# CMake: cpp package names that map to AI libraries
_CMAKE_AI_PACKAGES = {
    "torch", "libtorch", "caffe2", "opencv", "onnxruntime",
    "tensorflow", "mlpack", "dlib", "faiss", "xgboost", "lightgbm",
    "flashlight", "ncnn", "mxnet", "openvino",
}

_RE_CMAKE_FIND_PACKAGE = re.compile(
    r'find_package\s*\(\s*([A-Za-z0-9_\-]+)',
    re.IGNORECASE,
)
_RE_CMAKE_TARGET_LINK = re.compile(
    r'target_link_libraries\s*\([^)]+\)',
    re.IGNORECASE | re.DOTALL,
)
_RE_CMAKE_LINK_LIB = re.compile(r'[A-Za-z0-9_:\-\.]+')


def _is_cmake_ai_lib(name: str) -> bool:
    """Check whether a CMake package/library name is AI-related."""
    lower = name.lower().replace("::", "").replace("_", "-")
    # Direct match against our cmake AI set
    for pkg in _CMAKE_AI_PACKAGES:
        if lower.startswith(pkg.lower()):
            return True
    # Also check against the main AI library registry
    return is_ai_dependency(name)


def parse_cmake(content: str) -> list[dict]:
    """Parse AI-relevant packages from a CMakeLists.txt file."""
    deps: list[dict] = []
    seen: set[str] = set()
    line_num = 0

    lines = content.splitlines()

    # find_package entries
    for i, line in enumerate(lines, 1):
        m = _RE_CMAKE_FIND_PACKAGE.search(line)
        if m:
            name = m.group(1)
            if name not in seen:
                seen.add(name)
                deps.append({
                    "name": name,
                    "version": None,
                    "pinning": "unpinned",
                    "is_ai": _is_cmake_ai_lib(name),
                    "line": i,
                })

    # target_link_libraries — extract library names
    for m in _RE_CMAKE_TARGET_LINK.finditer(content):
        block = m.group(0)
        # Line number of the start of the match
        ln = content[:m.start()].count('\n') + 1
        tokens = _RE_CMAKE_LINK_LIB.findall(block)
        # First token is "target_link_libraries", second is target name, rest are libs
        for tok in tokens[2:]:
            if tok.upper() in ("PUBLIC", "PRIVATE", "INTERFACE", "TARGET_LINK_LIBRARIES"):
                continue
            if tok not in seen:
                seen.add(tok)
                deps.append({
                    "name": tok,
                    "version": None,
                    "pinning": "unpinned",
                    "is_ai": _is_cmake_ai_lib(tok),
                    "line": ln,
                })

    return deps


# ── vcpkg.json parser ───────────────────────────────────────────────

_VCPKG_AI_PACKAGES = {
    "libtorch", "onnxruntime", "opencv4", "opencv", "mlpack", "dlib",
    "xgboost", "lightgbm", "tensorflow-lite", "faiss",
}


def _is_vcpkg_ai(name: str) -> bool:
    """Check whether a vcpkg package name is AI-related."""
    lower = name.lower()
    for pkg in _VCPKG_AI_PACKAGES:
        if lower == pkg or lower.startswith(pkg + "-"):
            return True
    return is_ai_dependency(name)


def parse_vcpkg_json(content: str) -> list[dict]:
    """Parse dependencies from a vcpkg.json file."""
    deps: list[dict] = []
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return deps

    raw_deps = data.get("dependencies", [])
    if not isinstance(raw_deps, list):
        return deps

    for entry in raw_deps:
        if isinstance(entry, str):
            name = entry
            version = None
        elif isinstance(entry, dict):
            name = entry.get("name", "")
            version = entry.get("version") or entry.get("version-string") or None
        else:
            continue

        if not name:
            continue

        # vcpkg doesn't have semver pinning in the same sense;
        # if a version is specified treat as exact, otherwise unpinned
        pinning = "exact" if version else "unpinned"

        deps.append({
            "name": name,
            "version": version,
            "pinning": pinning,
            "is_ai": _is_vcpkg_ai(name),
            "line": 0,
        })

    return deps


# ── Lockfile detection ─────────────────────────────────────────────

def detect_lockfiles(project_path: str) -> list[str]:
    """Return list of lockfile paths found in project root."""
    found: list[str] = []
    root = Path(project_path)
    for name in sorted(LOCKFILE_NAMES):
        p = root / name
        if p.exists():
            found.append(str(p))
    return found


# ── Pinning score ──────────────────────────────────────────────────

_PINNING_WEIGHTS: dict[str, int] = {
    "hash": 100,
    "exact": 80,
    "compatible": 60,
    "range": 30,
    "unpinned": 0,
}


def calculate_pinning_score(deps: list[dict], has_lockfile: bool = False) -> int:
    """Calculate 0-100 pinning quality score. AI deps weighted 3x."""
    if not deps:
        base = 100
    else:
        total_weight = 0
        weighted_score = 0
        for d in deps:
            w = 3 if d.get("is_ai") else 1
            total_weight += w
            weighted_score += w * _PINNING_WEIGHTS.get(d.get("pinning", "unpinned"), 0)
        base = round(weighted_score / total_weight) if total_weight else 100

    if has_lockfile:
        base += 20
    return min(base, 100)


# ── Advisory loading ───────────────────────────────────────────────

def _load_advisories() -> list[dict]:
    """Load all OSV-format advisory YAML files from references/advisories/ recursively.

    Uses pyyaml if available, otherwise falls back to _parse_yaml_fallback from
    classify_risk.  Returns a list of advisory dicts (empty list on any failure).
    """
    # Locate the references/advisories directory relative to this file
    here = Path(__file__).resolve().parent
    advisories_dir = here.parent / "references" / "advisories"

    if not advisories_dir.exists():
        return []

    # YAML parser — prefer pyyaml, fall back to classify_risk helper
    yaml_load = None
    if check_optional("yaml", "using fallback YAML parser", "pip install pyyaml"):
        import yaml
        yaml_load = lambda text: yaml.safe_load(text) or {}  # noqa: E731

    if yaml_load is None:
        if check_optional("classify_risk", "YAML fallback parser", "included with regula"):
            from classify_risk import _parse_yaml_fallback
            yaml_load = _parse_yaml_fallback
        else:
            # No YAML parser available — cannot load advisories
            return []

    advisories: list[dict] = []
    for yaml_file in advisories_dir.rglob("*.yaml"):
        try:
            text = yaml_file.read_text(encoding="utf-8")
            data = yaml_load(text)
            if isinstance(data, dict):
                advisories.append(data)
        except Exception:  # Intentional: multiple error sources
            continue
    return advisories


def check_compromised(deps: list[dict]) -> list[dict]:
    """Check each dependency against loaded advisories for known compromised versions.

    Args:
        deps: list of dependency dicts with at minimum 'name' and 'version' keys.

    Returns:
        list of finding dicts, one per compromised dep found, each containing:
          package, version, advisory_id, description, remediation, severity.
    """
    advisories = _load_advisories()
    if not advisories:
        return []

    findings: list[dict] = []

    for dep in deps:
        dep_name = _normalize(dep.get("name", ""))
        dep_version = (dep.get("version") or "").strip()
        if not dep_name or not dep_version:
            continue

        for advisory in advisories:
            affected_list = advisory.get("affected")
            if not isinstance(affected_list, list):
                continue

            for affected in affected_list:
                if not isinstance(affected, dict):
                    continue
                pkg = affected.get("package", {})
                if not isinstance(pkg, dict):
                    continue

                adv_name = _normalize(pkg.get("name", ""))
                if adv_name != dep_name:
                    continue

                # Check explicit versions list first
                versions = affected.get("versions", [])
                if isinstance(versions, list) and dep_version in versions:
                    db = advisory.get("database_specific", {})
                    findings.append({
                        "package": dep.get("name", dep_name),
                        "version": dep_version,
                        "advisory_id": advisory.get("id", "unknown"),
                        "description": advisory.get("summary", advisory.get("details", "")),
                        "remediation": db.get("remediation", "") if isinstance(db, dict) else "",
                        "severity": "critical",
                    })
                    break  # one finding per dep per advisory is enough

    return findings


# ── Orchestrator ───────────────────────────────────────────────────

def scan_dependencies(project_path: str) -> dict:
    """Scan a project for dependency pinning quality."""
    root = Path(project_path)
    all_deps: list[dict] = []

    # requirements.txt
    req_txt = root / "requirements.txt"
    if req_txt.exists():
        all_deps.extend(parse_requirements_txt(req_txt.read_text(encoding="utf-8")))

    # pyproject.toml
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        all_deps.extend(parse_pyproject_toml(pyproject.read_text(encoding="utf-8")))

    # package.json
    pkg_json = root / "package.json"
    if pkg_json.exists():
        all_deps.extend(parse_package_json(pkg_json.read_text(encoding="utf-8")))

    # Pipfile
    pipfile = root / "Pipfile"
    if pipfile.exists():
        all_deps.extend(parse_pipfile(pipfile.read_text(encoding="utf-8")))

    # Cargo.toml (Rust)
    cargo_toml = root / "Cargo.toml"
    if cargo_toml.exists():
        all_deps.extend(parse_cargo_toml(cargo_toml.read_text(encoding="utf-8")))

    # CMakeLists.txt (C/C++)
    cmake_lists = root / "CMakeLists.txt"
    if cmake_lists.exists():
        all_deps.extend(parse_cmake(cmake_lists.read_text(encoding="utf-8")))

    # vcpkg.json (C/C++)
    vcpkg_json = root / "vcpkg.json"
    if vcpkg_json.exists():
        all_deps.extend(parse_vcpkg_json(vcpkg_json.read_text(encoding="utf-8")))

    lockfiles = detect_lockfiles(project_path)
    ai_deps = [d for d in all_deps if d.get("is_ai")]
    score = calculate_pinning_score(all_deps, has_lockfile=bool(lockfiles))

    # Summary
    unpinned_ai = [d for d in ai_deps if d.get("pinning") == "unpinned"]
    if unpinned_ai:
        summary = (
            f"CRITICAL: {len(unpinned_ai)} AI dependenc{'y' if len(unpinned_ai) == 1 else 'ies'} "
            f"unpinned. Supply chain attack risk."
        )
    elif score < 60:
        summary = "WARNING: Weak dependency pinning. Consider exact-pinning AI libraries."
    elif score < 80:
        summary = "MODERATE: Some dependencies could use stricter pinning."
    else:
        summary = "GOOD: Dependencies are well-pinned."

    compromised = check_compromised(all_deps)

    return {
        "project": str(root.resolve()),
        "scan_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "all_dependencies": all_deps,
        "ai_dependencies": ai_deps,
        "lockfiles": lockfiles,
        "pinning_score": score,
        "compromised": compromised,
        "compromised_count": len(compromised),
        "summary": summary,
    }


# ── Formatters ─────────────────────────────────────────────────────

def format_dep_text(results: dict) -> str:
    """Format scan results as human-readable text."""
    lines: list[str] = []
    lines.append(f"Dependency Supply Chain Scan")
    lines.append(f"Project: {results['project']}")
    lines.append(f"Scanned: {results['scan_date']}")
    lines.append(f"Pinning Score: {results['pinning_score']}/100")
    lines.append("")
    lines.append(f"Total dependencies: {len(results['all_dependencies'])}")
    lines.append(f"AI dependencies: {len(results['ai_dependencies'])}")
    lines.append(f"Lockfiles found: {len(results['lockfiles'])}")
    if results["lockfiles"]:
        for lf in results["lockfiles"]:
            lines.append(f"  - {lf}")
    lines.append("")
    lines.append(f"Summary: {results['summary']}")
    lines.append("")

    if results["ai_dependencies"]:
        lines.append("AI Dependencies:")
        for d in results["ai_dependencies"]:
            ver = d.get("version") or "unspecified"
            lines.append(f"  {d['name']:30s} {d['pinning']:12s} {ver}")

    if results["compromised"]:
        lines.append("")
        lines.append(f"COMPROMISED PACKAGES ({results['compromised_count']}):")
        for c in results["compromised"]:
            lines.append(f"  {c.get('name', 'unknown')}: {c.get('detail', '')}")

    return "\n".join(lines)


def format_dep_json(results: dict) -> str:
    """Format scan results as JSON string."""
    return json.dumps(results, indent=2, default=str)
