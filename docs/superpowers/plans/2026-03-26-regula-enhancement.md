# Regula Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform Regula from a regex-based risk indicator into a production-grade, multi-language, multi-framework AI governance tool with dependency supply chain analysis, compliance gap assessment, and enterprise-quality reporting.

**Architecture:** 8 phases building bottom-up: AST engine (foundation) → dependency scanner → CLI unification → gap assessment enhancement → cross-framework mapper → report generator → policy configuration → test suite expansion. Each phase produces working, tested software. All existing 84 tests must continue passing at every step.

**Tech Stack:** Python 3.10+ stdlib, tree-sitter + tree-sitter-languages (JS/TS AST — the ONLY new external dependency), existing custom test framework (assert_eq/assert_true/assert_false pattern).

**Critical constraint:** The existing test framework in `tests/test_classification.py` uses a custom runner with global `passed`/`failed` counters, NOT pytest. All new tests MUST follow this pattern. The spec mentions pytest but the codebase does not use it — follow what exists.

**Working directory:** `/home/mkuziva/getregula/`

---

## File Map

### New Files
| File | Responsibility |
|------|---------------|
| `scripts/ast_engine.py` | Multi-language AST analysis (Python stdlib `ast` + tree-sitter for JS/TS) |
| `scripts/dependency_scan.py` | AI dependency supply chain security |
| `scripts/framework_mapper.py` | Cross-framework compliance mapping (EU AI Act / NIST AI RMF / ISO 42001) |
| `references/framework_crosswalk.yaml` | Mapping data for framework_mapper |
| `references/advisories/pypi/litellm/x_REGULA-2026-001.yaml` | Known-compromised AI package (OSV format) |
| `tests/fixtures/sample_high_risk/app.py` | Test fixture: employment screening AI |
| `tests/fixtures/sample_high_risk/requirements.txt` | Test fixture: unpinned AI deps |
| `tests/fixtures/sample_compliant/app.py` | Test fixture: well-documented AI system |
| `tests/fixtures/sample_compliant/requirements.txt` | Test fixture: pinned AI deps |
| `tests/fixtures/sample_compliant/model_card.md` | Test fixture: model documentation |
| `tests/fixtures/sample_unpinned/package.json` | Test fixture: JS project with unpinned deps |

### Modified Files
| File | Changes |
|------|---------|
| `scripts/cli.py` | Add `deps` command, enhance `check`/`gap`/`report` with framework and dependency options |
| `scripts/compliance_check.py` | Integrate AST engine and dependency scanner into Article 15 checks |
| `scripts/report.py` | Enhanced HTML with dependency section, framework tabs, compliance matrix |
| `scripts/classify_risk.py` | Add framework mapping output to Classification dataclass |
| `regula-policy.yaml` | Add thresholds, exclusions, approvals schema |
| `pyproject.toml` | Add tree-sitter optional dependency |
| `SKILL.md` | Document new commands and capabilities |
| `README.md` | Document new features |
| `tests/test_classification.py` | Add 66+ new tests (target 150+ total) |

---

## Phase 1: Multi-Language AST Engine

### Task 1.1: Python AST Wrapper

Wrap the existing `ast_analysis.py` into the new unified engine interface. Do NOT rewrite — delegate.

**Files:**
- Create: `scripts/ast_engine.py`
- Read: `scripts/ast_analysis.py` (existing, 870 lines)
- Test: `tests/test_classification.py` (append new tests)

- [ ] **Step 1: Write failing tests for the Python AST wrapper**

Add to `tests/test_classification.py` before the `if __name__ == "__main__":` block:

```python
# ── AST Engine Tests ───────────────────────────────────────────────

def test_ast_engine_python_parse():
    """AST engine parses Python and returns unified format"""
    from ast_engine import analyse_file
    code = '''
import openai
client = openai.Client()
result = client.chat.completions.create(model="gpt-4", messages=[])
print(result)
'''
    findings = analyse_file(code, "test.py", language="python")
    assert_true(isinstance(findings, dict), "returns dict")
    assert_true("imports" in findings, "has imports")
    assert_true("ai_imports" in findings, "has ai_imports")
    assert_true("data_flows" in findings, "has data_flows")
    assert_true("oversight" in findings, "has oversight")
    assert_true("logging" in findings, "has logging")
    assert_true("context" in findings, "has context classification")
    assert_true(findings["has_ai_code"], "detects AI code")
    print("✓ AST engine: Python parse returns unified format")
```

Add `test_ast_engine_python_parse` to the tests list.

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/mkuziva/getregula && python3 tests/test_classification.py 2>&1 | tail -5`
Expected: EXCEPTION or FAIL — `ast_engine` module not found.

- [ ] **Step 3: Create ast_engine.py with Python support**

Create `scripts/ast_engine.py`:

```python
#!/usr/bin/env python3
"""
Regula Multi-Language AST Engine

Unified interface for structure-aware code analysis across Python, JavaScript,
and TypeScript. Delegates to Python stdlib `ast` module for Python files and
tree-sitter for JS/TS (when available).

All public functions accept source code strings and return structured dicts.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

sys.path.insert(0, str(Path(__file__).parent))

from ast_analysis import (
    parse_python_file,
    classify_context,
    trace_ai_data_flow,
    detect_human_oversight,
    detect_logging_practices,
)

# Languages supported with full AST analysis
SUPPORTED_LANGUAGES = {"python"}

# Languages supported with tree-sitter (if installed)
TREE_SITTER_LANGUAGES = {"javascript", "typescript"}

# File extension to language mapping
EXTENSION_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".mjs": "javascript",
    ".cjs": "javascript",
}


def detect_language(filename: str) -> Optional[str]:
    """Detect language from file extension."""
    ext = Path(filename).suffix.lower()
    return EXTENSION_MAP.get(ext)


def analyse_file(content: str, filename: str, language: Optional[str] = None) -> dict:
    """Analyse a source file and return unified findings.

    Returns:
        {
            "language": str,
            "imports": list[str],
            "ai_imports": list[str],
            "has_ai_code": bool,
            "context": str,  # "implementation", "test", "configuration", "documentation", "not_parseable"
            "function_defs": list[dict],
            "class_defs": list[dict],
            "is_test_file": bool,
            "data_flows": list[dict],
            "oversight": dict,
            "logging": dict,
        }
    """
    lang = language or detect_language(filename) or "unknown"

    if lang == "python":
        return _analyse_python(content)
    elif lang in TREE_SITTER_LANGUAGES:
        return _analyse_tree_sitter(content, lang)
    else:
        return _empty_analysis(lang)


def _analyse_python(content: str) -> dict:
    """Full AST analysis for Python using stdlib ast module."""
    parsed = parse_python_file(content)
    context = classify_context(content)
    flows = trace_ai_data_flow(content)
    oversight = detect_human_oversight(content)
    logging = detect_logging_practices(content)

    return {
        "language": "python",
        "imports": parsed["imports"],
        "ai_imports": parsed["ai_imports"],
        "has_ai_code": parsed["has_ai_code"],
        "context": context,
        "function_defs": parsed["function_defs"],
        "class_defs": parsed["class_defs"],
        "is_test_file": parsed["is_test_file"],
        "data_flows": flows,
        "oversight": oversight,
        "logging": logging,
    }


def _analyse_tree_sitter(content: str, language: str) -> dict:
    """AST analysis for JS/TS using tree-sitter (if installed)."""
    try:
        return _tree_sitter_parse(content, language)
    except ImportError:
        # tree-sitter not installed — fall back to regex
        return _regex_fallback(content, language)


def _empty_analysis(language: str) -> dict:
    """Return empty analysis for unsupported languages."""
    return {
        "language": language,
        "imports": [],
        "ai_imports": [],
        "has_ai_code": False,
        "context": "not_parseable",
        "function_defs": [],
        "class_defs": [],
        "is_test_file": False,
        "data_flows": [],
        "oversight": {"has_oversight": False, "oversight_patterns": [], "automated_decisions": [], "oversight_score": 50},
        "logging": {"has_logging": False, "logging_patterns": [], "ai_operations_logged": 0, "ai_operations_unlogged": 0, "logging_score": 50},
    }


def _regex_fallback(content: str, language: str) -> dict:
    """Regex-based analysis for JS/TS when tree-sitter is unavailable.

    Less accurate than AST but catches imports and basic patterns.
    """
    import re

    JS_AI_IMPORTS = {
        "openai", "@openai", "anthropic", "@anthropic-ai/sdk",
        "langchain", "@langchain", "tensorflow", "@tensorflow/tfjs",
        "brain.js", "transformers", "@xenova/transformers",
        "@huggingface/inference", "replicate", "ai",
        "@pinecone-database/pinecone", "chromadb",
        "@qdrant/js-client-rest", "weaviate-ts-client",
        "litellm", "llamaindex",
    }

    IMPORT_PATTERNS = [
        r'''(?:import|require)\s*\(\s*['"]([^'"]+)['"]\s*\)''',  # require('x') / import('x')
        r'''from\s+['"]([^'"]+)['"]''',  # from 'x'
        r'''import\s+.*?\s+from\s+['"]([^'"]+)['"]''',  # import x from 'x'
        r'''import\s+['"]([^'"]+)['"]''',  # import 'x'
    ]

    imports = []
    for pattern in IMPORT_PATTERNS:
        for match in re.finditer(pattern, content):
            imports.append(match.group(1))

    ai_imports = [imp for imp in imports if any(
        imp == lib or imp.startswith(lib + "/")
        for lib in JS_AI_IMPORTS
    )]

    # Basic test file detection
    is_test = any(kw in content.lower() for kw in [
        "describe(", "it(", "test(", "expect(", "jest", "mocha", "vitest",
        ".spec.", ".test.",
    ]) and Path("").suffix in (".test.js", ".spec.js", ".test.ts", ".spec.ts", "")

    # Simple context classification
    context = "test" if is_test else ("implementation" if ai_imports else "not_parseable")

    return {
        "language": language,
        "imports": imports,
        "ai_imports": ai_imports,
        "has_ai_code": len(ai_imports) > 0,
        "context": context,
        "function_defs": [],
        "class_defs": [],
        "is_test_file": is_test,
        "data_flows": [],
        "oversight": {"has_oversight": False, "oversight_patterns": [], "automated_decisions": [], "oversight_score": 50},
        "logging": {"has_logging": False, "logging_patterns": [], "ai_operations_logged": 0, "ai_operations_unlogged": 0, "logging_score": 50},
    }


def _tree_sitter_parse(content: str, language: str) -> dict:
    """Full tree-sitter AST analysis for JavaScript/TypeScript.

    Raises ImportError if tree-sitter is not installed.
    """
    import tree_sitter_javascript as ts_js
    import tree_sitter_typescript as ts_ts
    from tree_sitter import Language, Parser

    if language == "javascript":
        lang = Language(ts_js.language())
    elif language == "typescript":
        lang = Language(ts_ts.language_typescript())
    else:
        raise ValueError(f"Unsupported tree-sitter language: {language}")

    parser = Parser(lang)
    tree = parser.parse(bytes(content, "utf-8"))
    root = tree.root_node

    imports = []
    ai_imports = []
    function_defs = []
    class_defs = []

    JS_AI_LIBRARIES = {
        "openai", "@openai", "anthropic", "@anthropic-ai/sdk",
        "langchain", "@langchain", "tensorflow", "@tensorflow/tfjs",
        "brain.js", "transformers", "@xenova/transformers",
        "@huggingface/inference", "replicate", "ai",
        "@pinecone-database/pinecone", "chromadb",
        "@qdrant/js-client-rest", "weaviate-ts-client",
        "litellm", "llamaindex",
    }

    def _walk(node):
        # Import declarations
        if node.type == "import_statement" or node.type == "import_declaration":
            source = node.child_by_field_name("source")
            if source:
                module = source.text.decode("utf-8").strip("'\"")
                imports.append(module)
                if any(module == lib or module.startswith(lib + "/") for lib in JS_AI_LIBRARIES):
                    ai_imports.append(module)

        # Require calls
        if node.type == "call_expression":
            func = node.child_by_field_name("function")
            if func and func.text == b"require":
                args = node.child_by_field_name("arguments")
                if args and args.child_count > 0:
                    for child in args.children:
                        if child.type == "string":
                            module = child.text.decode("utf-8").strip("'\"")
                            imports.append(module)
                            if any(module == lib or module.startswith(lib + "/") for lib in JS_AI_LIBRARIES):
                                ai_imports.append(module)

        # Function declarations
        if node.type in ("function_declaration", "method_definition", "arrow_function"):
            name_node = node.child_by_field_name("name")
            name = name_node.text.decode("utf-8") if name_node else "<anonymous>"
            params = node.child_by_field_name("parameters")
            args = []
            if params:
                for p in params.children:
                    if p.type in ("identifier", "required_parameter", "optional_parameter"):
                        args.append(p.text.decode("utf-8"))
            is_test = name.startswith("test") or name.startswith("it_") or name == "it"
            function_defs.append({
                "name": name,
                "args": args,
                "decorators": [],
                "is_test": is_test,
                "line": node.start_point[0] + 1,
            })

        # Class declarations
        if node.type == "class_declaration":
            name_node = node.child_by_field_name("name")
            name = name_node.text.decode("utf-8") if name_node else "<anonymous>"
            class_defs.append({
                "name": name,
                "bases": [],
                "methods": [],
            })

        for child in node.children:
            _walk(child)

    _walk(root)

    # Test file detection
    test_keywords = {"describe", "it", "test", "expect", "jest", "mocha", "vitest"}
    is_test_file = any(kw in content.lower() for kw in test_keywords) and len(function_defs) > 0

    has_ai = len(ai_imports) > 0
    context = "test" if is_test_file else ("implementation" if has_ai else "not_parseable")

    return {
        "language": language,
        "imports": imports,
        "ai_imports": ai_imports,
        "has_ai_code": has_ai,
        "context": context,
        "function_defs": function_defs,
        "class_defs": class_defs,
        "is_test_file": is_test_file,
        "data_flows": [],  # TODO: JS/TS data flow tracing (Phase 2 work)
        "oversight": {"has_oversight": False, "oversight_patterns": [], "automated_decisions": [], "oversight_score": 50},
        "logging": {"has_logging": False, "logging_patterns": [], "ai_operations_logged": 0, "ai_operations_unlogged": 0, "logging_score": 50},
    }


def analyse_project(project_path: str) -> List[dict]:
    """Analyse all supported source files in a project directory.

    Returns a list of per-file analysis dicts.
    """
    import os

    SKIP_DIRS = {".git", "node_modules", "__pycache__", "venv", ".venv",
                 "dist", "build", ".next", ".tox", "egg-info"}

    project = Path(project_path).resolve()
    results = []

    for root, dirs, files in os.walk(project):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in files:
            filepath = Path(root) / filename
            lang = detect_language(filename)
            if not lang:
                continue

            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
            except (PermissionError, OSError):
                continue

            analysis = analyse_file(content, filename, lang)
            analysis["file"] = str(filepath.relative_to(project))
            analysis["file_path"] = str(filepath)
            results.append(analysis)

    return results


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Multi-language AST analysis for AI governance")
    parser.add_argument("--file", "-f", help="Single file to analyse")
    parser.add_argument("--project", "-p", help="Project directory to analyse")
    parser.add_argument("--format", choices=["json", "text"], default="text")
    args = parser.parse_args()

    if args.file:
        content = Path(args.file).read_text(encoding="utf-8", errors="ignore")
        result = analyse_file(content, args.file)
        if args.format == "json":
            print(json.dumps(result, indent=2, default=str))
        else:
            lang = result["language"]
            ai = result["ai_imports"]
            ctx = result["context"]
            print(f"Language: {lang}")
            print(f"AI imports: {', '.join(ai) if ai else 'none'}")
            print(f"Context: {ctx}")
            print(f"Has AI code: {result['has_ai_code']}")
            if result["data_flows"]:
                print(f"Data flows: {len(result['data_flows'])} traced")
            print(f"Oversight score: {result['oversight']['oversight_score']}/100")
            print(f"Logging score: {result['logging']['logging_score']}/100")
    elif args.project:
        results = analyse_project(args.project)
        ai_files = [r for r in results if r["has_ai_code"]]
        if args.format == "json":
            print(json.dumps(results, indent=2, default=str))
        else:
            print(f"Files analysed: {len(results)}")
            print(f"AI files found: {len(ai_files)}")
            for r in ai_files:
                print(f"  {r['file']} ({r['language']}) — {', '.join(r['ai_imports'])}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/mkuziva/getregula && python3 tests/test_classification.py 2>&1 | tail -5`
Expected: All tests pass including the new one.

- [ ] **Step 5: Commit**

```bash
cd /home/mkuziva/getregula
git add scripts/ast_engine.py tests/test_classification.py
git commit -m "feat: add multi-language AST engine with Python support"
```

---

### Task 1.2: JavaScript/TypeScript Regex Fallback Tests

Test the JS/TS regex fallback (works without tree-sitter installed).

**Files:**
- Modify: `tests/test_classification.py`

- [ ] **Step 1: Write failing tests for JS/TS regex fallback**

```python
def test_ast_engine_js_regex_fallback():
    """AST engine handles JavaScript via regex when tree-sitter unavailable"""
    from ast_engine import analyse_file
    code = '''
import OpenAI from 'openai';
const client = new OpenAI();
const response = await client.chat.completions.create({model: "gpt-4"});
console.log(response);
'''
    findings = analyse_file(code, "app.js", language="javascript")
    assert_true(findings["has_ai_code"], "detects openai import in JS")
    assert_true("openai" in findings["ai_imports"], "identifies openai as AI import")
    assert_eq(findings["language"], "javascript", "correct language")
    print("✓ AST engine: JS regex fallback detects AI imports")


def test_ast_engine_ts_regex_fallback():
    """AST engine handles TypeScript via regex when tree-sitter unavailable"""
    from ast_engine import analyse_file
    code = '''
import Anthropic from '@anthropic-ai/sdk';
import { ChromaClient } from 'chromadb';
const client = new Anthropic();
'''
    findings = analyse_file(code, "service.ts", language="typescript")
    assert_true(findings["has_ai_code"], "detects AI imports in TS")
    assert_true(len(findings["ai_imports"]) >= 2, f"finds 2+ AI imports (got {len(findings['ai_imports'])})")
    print("✓ AST engine: TS regex fallback detects AI imports")


def test_ast_engine_non_ai_js():
    """AST engine correctly identifies non-AI JavaScript"""
    from ast_engine import analyse_file
    code = '''
import express from 'express';
const app = express();
app.get('/', (req, res) => res.send('hello'));
'''
    findings = analyse_file(code, "server.js", language="javascript")
    assert_false(findings["has_ai_code"], "express is not AI")
    assert_eq(len(findings["ai_imports"]), 0, "no AI imports")
    print("✓ AST engine: non-AI JS correctly identified")


def test_ast_engine_language_detection():
    """AST engine detects language from file extension"""
    from ast_engine import detect_language
    assert_eq(detect_language("app.py"), "python", ".py → python")
    assert_eq(detect_language("app.js"), "javascript", ".js → javascript")
    assert_eq(detect_language("app.ts"), "typescript", ".ts → typescript")
    assert_eq(detect_language("app.tsx"), "typescript", ".tsx → typescript")
    assert_eq(detect_language("app.jsx"), "javascript", ".jsx → javascript")
    assert_eq(detect_language("app.mjs"), "javascript", ".mjs → javascript")
    assert_eq(detect_language("app.rb"), None, ".rb → None")
    print("✓ AST engine: language detection from extensions")
```

Add all four to the tests list.

- [ ] **Step 2: Run tests to verify they fail then pass**

Run: `cd /home/mkuziva/getregula && python3 tests/test_classification.py 2>&1 | tail -5`
Expected: All tests pass (the regex fallback code is already in ast_engine.py).

- [ ] **Step 3: Commit**

```bash
cd /home/mkuziva/getregula
git add tests/test_classification.py
git commit -m "test: add JS/TS regex fallback and language detection tests"
```

---

### Task 1.3: Tree-Sitter Optional Dependency Setup

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add tree-sitter as optional dependency**

In `pyproject.toml`, add to `[project.optional-dependencies]`:

```toml
[project.optional-dependencies]
yaml = ["pyyaml>=6.0"]
ast = ["tree-sitter>=0.23", "tree-sitter-javascript>=0.23", "tree-sitter-typescript>=0.23"]
all = ["pyyaml>=6.0", "tree-sitter>=0.23", "tree-sitter-javascript>=0.23", "tree-sitter-typescript>=0.23"]
```

- [ ] **Step 2: Commit**

```bash
cd /home/mkuziva/getregula
git add pyproject.toml
git commit -m "build: add tree-sitter as optional dependency for JS/TS AST"
```

---

## Phase 2: Dependency Supply Chain Security

### Task 2.1: Core Dependency Parser

**Files:**
- Create: `scripts/dependency_scan.py`
- Test: `tests/test_classification.py`

- [ ] **Step 1: Write failing tests for dependency parsing**

```python
# ── Dependency Supply Chain Tests ──────────────────────────────────

def test_dep_scan_requirements_txt():
    """Parses requirements.txt and scores pinning quality"""
    from dependency_scan import parse_requirements_txt
    content = """
openai==1.52.0
torch>=2.0
langchain
litellm==1.82.7
numpy
"""
    deps = parse_requirements_txt(content)
    assert_true(len(deps) >= 4, f"finds 4+ deps (got {len(deps)})")
    # Check pinning quality
    openai_dep = [d for d in deps if d["name"] == "openai"][0]
    assert_eq(openai_dep["pinning"], "exact", "openai is exact-pinned")
    assert_eq(openai_dep["version"], "1.52.0", "correct version")
    torch_dep = [d for d in deps if d["name"] == "torch"][0]
    assert_eq(torch_dep["pinning"], "range", "torch is range-pinned")
    langchain_dep = [d for d in deps if d["name"] == "langchain"][0]
    assert_eq(langchain_dep["pinning"], "unpinned", "langchain is unpinned")
    print("✓ Dependency scan: parses requirements.txt pinning quality")


def test_dep_scan_ai_identification():
    """Identifies AI vs non-AI dependencies"""
    from dependency_scan import parse_requirements_txt, is_ai_dependency
    assert_true(is_ai_dependency("openai"), "openai is AI")
    assert_true(is_ai_dependency("torch"), "torch is AI")
    assert_true(is_ai_dependency("litellm"), "litellm is AI")
    assert_true(is_ai_dependency("langchain"), "langchain is AI")
    assert_false(is_ai_dependency("flask"), "flask is not AI")
    assert_false(is_ai_dependency("requests"), "requests is not AI")
    print("✓ Dependency scan: AI dependency identification")


def test_dep_scan_pinning_score():
    """Calculates overall pinning score"""
    from dependency_scan import calculate_pinning_score
    deps = [
        {"name": "openai", "pinning": "exact", "is_ai": True},
        {"name": "torch", "pinning": "range", "is_ai": True},
        {"name": "langchain", "pinning": "unpinned", "is_ai": True},
        {"name": "flask", "pinning": "exact", "is_ai": False},
    ]
    score = calculate_pinning_score(deps)
    assert_true(0 <= score <= 100, f"score in range (got {score})")
    assert_true(score < 70, f"mixed pinning scores below 70 (got {score})")
    print("✓ Dependency scan: pinning score calculation")


def test_dep_scan_lockfile_detection():
    """Detects lockfile presence"""
    import tempfile, shutil
    from dependency_scan import detect_lockfiles
    temp_dir = tempfile.mkdtemp()
    Path(temp_dir, "requirements.txt").write_text("openai==1.0\n")
    Path(temp_dir, "Pipfile.lock").write_text("{}\n")
    try:
        lockfiles = detect_lockfiles(temp_dir)
        assert_true(len(lockfiles) > 0, "detects Pipfile.lock")
        assert_true(any("Pipfile.lock" in lf for lf in lockfiles), "finds Pipfile.lock")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    print("✓ Dependency scan: lockfile detection")


def test_dep_scan_package_json():
    """Parses package.json dependencies"""
    from dependency_scan import parse_package_json
    content = json.dumps({
        "dependencies": {
            "openai": "^4.0.0",
            "@anthropic-ai/sdk": "0.25.0",
            "express": "~4.18.0"
        }
    })
    deps = parse_package_json(content)
    assert_true(len(deps) >= 3, f"finds 3 deps (got {len(deps)})")
    openai_dep = [d for d in deps if d["name"] == "openai"][0]
    assert_eq(openai_dep["pinning"], "range", "^ is range")
    anthropic_dep = [d for d in deps if d["name"] == "@anthropic-ai/sdk"][0]
    assert_eq(anthropic_dep["pinning"], "exact", "bare version is exact")
    print("✓ Dependency scan: parses package.json")
```

Add all five tests to the tests list.

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL — `dependency_scan` module not found.

- [ ] **Step 3: Create dependency_scan.py**

Create `scripts/dependency_scan.py` with the following functions:

- `AI_LIBRARIES`: set of 60+ AI library names (Python + JavaScript)
- `LOCKFILE_NAMES`: set of lockfile filenames to detect
- `is_ai_dependency(name: str) -> bool`
- `parse_requirements_txt(content: str) -> list[dict]`
- `parse_pyproject_toml(content: str) -> list[dict]`
- `parse_package_json(content: str) -> list[dict]`
- `parse_pipfile(content: str) -> list[dict]`
- `detect_lockfiles(project_path: str) -> list[str]`
- `calculate_pinning_score(deps: list[dict]) -> int`
- `scan_dependencies(project_path: str) -> dict` — orchestrator
- `format_dep_text(results: dict) -> str`
- `format_dep_json(results: dict) -> str`

Each dependency dict has: `name`, `version`, `pinning` (one of: "hash", "exact", "range", "unpinned"), `is_ai`, `file`, `line`.

Pinning detection rules:
- Hash: `--hash=sha256:` present
- Exact: `==X.Y.Z` (Python) or bare `"X.Y.Z"` (npm)
- Range: `>=`, `~=`, `^`, `~`, `>`, `<` present
- Unpinned: no version specifier, or `*`

Score calculation: AI deps weighted 3x. Hash=100, Exact=80, Range=30, Unpinned=0. Lockfile bonus: +20 if any lockfile present.

The full implementation should be ~400 lines. I will not paste the entire file here — the function signatures, types, and test expectations above define the contract completely. Build to pass the tests.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/mkuziva/getregula && python3 tests/test_classification.py 2>&1 | tail -5`

- [ ] **Step 5: Commit**

```bash
cd /home/mkuziva/getregula
git add scripts/dependency_scan.py tests/test_classification.py
git commit -m "feat: add dependency supply chain security scanner"
```

---

### Task 2.2: Known Compromised Package Detection

**Files:**
- Create: `references/advisories/pypi/litellm/x_REGULA-2026-001.yaml`
- Modify: `scripts/dependency_scan.py`
- Test: `tests/test_classification.py`

- [ ] **Step 1: Write failing test**

```python
def test_dep_scan_compromised_detection():
    """Detects known compromised package versions"""
    from dependency_scan import check_compromised
    deps = [
        {"name": "litellm", "version": "1.82.7", "pinning": "exact", "is_ai": True},
        {"name": "openai", "version": "1.52.0", "pinning": "exact", "is_ai": True},
    ]
    findings = check_compromised(deps)
    assert_true(len(findings) > 0, "finds compromised litellm")
    assert_eq(findings[0]["package"], "litellm", "identifies litellm")
    assert_eq(findings[0]["version"], "1.82.7", "identifies version")
    assert_true("credential" in findings[0]["description"].lower() or "malware" in findings[0]["description"].lower(),
                "description mentions the attack")
    print("✓ Dependency scan: detects known compromised versions")
```

- [ ] **Step 2: Create advisory file**

Create directory structure and `references/advisories/pypi/litellm/x_REGULA-2026-001.yaml` with OSV-format advisory (use the validated schema from the brainstorming session).

- [ ] **Step 3: Add `check_compromised()` and `_load_advisories()` to dependency_scan.py**

Load advisories from `references/advisories/` at scan time. Check each dependency's name + version against `affected[].package.name` and `affected[].versions`.

- [ ] **Step 4: Run tests, verify pass, commit**

```bash
cd /home/mkuziva/getregula
git add references/advisories/ scripts/dependency_scan.py tests/test_classification.py
git commit -m "feat: add known-compromised AI package detection (OSV format)"
```

---

### Task 2.3: Wire Dependency Scan into CLI

**Files:**
- Modify: `scripts/cli.py`

- [ ] **Step 1: Add `cmd_deps` function and `deps` subparser**

```python
def cmd_deps(args):
    """Dependency supply chain analysis."""
    from dependency_scan import scan_dependencies, format_dep_text, format_dep_json
    results = scan_dependencies(args.project)
    if args.format == "json":
        print(format_dep_json(results))
    else:
        print(format_dep_text(results))
    # Exit codes for CI
    if results.get("compromised_count", 0) > 0:
        sys.exit(2)
    elif args.strict and results.get("pinning_score", 100) < 50:
        sys.exit(1)
```

Add subparser:
```python
p_deps = subparsers.add_parser("deps", help="AI dependency supply chain analysis")
p_deps.add_argument("--project", "-p", default=".")
p_deps.add_argument("--format", "-f", choices=["text", "json"], default="text")
p_deps.add_argument("--strict", action="store_true", help="Exit 1 if pinning score < 50")
p_deps.set_defaults(func=cmd_deps)
```

- [ ] **Step 2: Test manually**

Run: `cd /home/mkuziva/getregula && python3 scripts/cli.py deps --project .`
Expected: Output showing dependency analysis for the getregula project itself.

- [ ] **Step 3: Commit**

```bash
cd /home/mkuziva/getregula
git add scripts/cli.py
git commit -m "feat: add 'regula deps' CLI command for supply chain analysis"
```

---

## Phase 3: CLI Unification

### Task 3.1: Add --framework and --ci Global Options

**Files:**
- Modify: `scripts/cli.py`

- [ ] **Step 1: Add global options to the main parser**

Add these to the `main()` function's parser, BEFORE the subparsers:

```python
parser.add_argument("--framework", choices=["eu-ai-act", "nist-ai-rmf", "iso-42001", "all"], default="eu-ai-act")
parser.add_argument("--ci", action="store_true", help="CI mode: exit 0=pass, 1=findings, 2=blocked")
parser.add_argument("--config", help="Custom policy configuration file")
```

- [ ] **Step 2: Update `cmd_check` to use the dependency scanner and AST engine**

Integrate dependency scan results into the `check` command output. When `--ci` is set, use appropriate exit codes.

- [ ] **Step 3: Run full test suite, commit**

```bash
cd /home/mkuziva/getregula
python3 tests/test_classification.py
git add scripts/cli.py
git commit -m "feat: add --framework, --ci, --config global CLI options"
```

---

## Phase 4: Compliance Gap Assessment Enhancement

### Task 4.1: Integrate AST Engine and Dependency Scanner into Gap Assessment

**Files:**
- Modify: `scripts/compliance_check.py`

- [ ] **Step 1: Write failing test for enhanced Article 15**

```python
def test_gap_article_15_dependency_pinning():
    """Article 15 gap assessment includes dependency pinning analysis"""
    import tempfile, shutil
    from compliance_check import assess_compliance
    temp_dir = tempfile.mkdtemp()
    Path(temp_dir, "app.py").write_text("import openai\nclient = openai.Client()\n")
    Path(temp_dir, "requirements.txt").write_text("openai\ntorch\nlangchain\n")  # all unpinned
    try:
        assessment = assess_compliance(temp_dir)
        art15 = assessment["articles"]["15"]
        gaps_str = " ".join(art15["gaps"])
        assert_true("pinning" in gaps_str.lower() or "unpinned" in gaps_str.lower(),
                    "Article 15 flags unpinned AI dependencies")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    print("✓ Gap assessment: Article 15 includes dependency pinning")
```

- [ ] **Step 2: Update `_check_article_15` in compliance_check.py**

Import `scan_dependencies` from `dependency_scan` (with ImportError fallback). Add pinning score to Article 15 evidence/gaps. Unpinned AI dependencies are a gap; lockfile presence is evidence.

- [ ] **Step 3: Run tests, verify pass, commit**

```bash
cd /home/mkuziva/getregula
python3 tests/test_classification.py
git add scripts/compliance_check.py tests/test_classification.py
git commit -m "feat: integrate dependency pinning into Article 15 gap assessment"
```

---

## Phase 5: Cross-Framework Compliance Mapping

### Task 5.1: Create Framework Crosswalk Data

**Files:**
- Create: `references/framework_crosswalk.yaml`

- [ ] **Step 1: Create the crosswalk mapping file**

This maps EU AI Act articles to NIST AI RMF functions/subcategories and ISO 42001 controls. The ISO 42001 mapping already exists in `references/iso_42001_mapping.yaml` — extend it with NIST.

```yaml
# Framework Crosswalk: EU AI Act ↔ NIST AI RMF 1.0 ↔ ISO 42001:2023
schema_version: "1.0"

mappings:
  article_9:
    eu_ai_act:
      article: "9"
      title: "Risk Management System"
      requirement: "Establish, implement, document and maintain a risk management system"
    nist_ai_rmf:
      functions: ["GOVERN", "MAP", "MANAGE"]
      subcategories:
        - "GOVERN 1.1: Legal and regulatory requirements are identified"
        - "MAP 1.1: Intended purposes, context of use, deployment, potentially benefits and costs are understood"
        - "MAP 5.1: Likelihood and magnitude of each identified AI risk is assessed"
        - "MANAGE 1.1: A determination is made as to whether the AI risk is manageable"
        - "MANAGE 2.1: Resources required to manage AI risks are taken into account"
    iso_42001:
      controls:
        - "6.1: Actions to address risks and opportunities"
        - "A.5.3: AI risk management"
        - "A.6.1: AI risk assessment"

  article_10:
    eu_ai_act:
      article: "10"
      title: "Data and Data Governance"
      requirement: "Training, validation and testing data sets shall be subject to appropriate data governance"
    nist_ai_rmf:
      functions: ["MAP", "MEASURE"]
      subcategories:
        - "MAP 2.1: The specific tasks and methods for the AI system are defined"
        - "MAP 2.2: Information about the AI system's knowledge limits is documented"
        - "MEASURE 2.6: AI system performance or assurance criteria are measured"
    iso_42001:
      controls:
        - "A.6.6: Data for AI systems"
        - "A.7.4: Documentation of data"

  article_11:
    eu_ai_act:
      article: "11"
      title: "Technical Documentation"
      requirement: "Technical documentation shall be drawn up before the system is placed on the market"
    nist_ai_rmf:
      functions: ["GOVERN", "MAP"]
      subcategories:
        - "GOVERN 1.2: Trustworthy AI characteristics are integrated into organizational policies"
        - "MAP 1.6: System requirements (e.g., accuracy, performance) are defined"
    iso_42001:
      controls:
        - "A.6.4: AI system documentation"
        - "7.5: Documented information"

  article_12:
    eu_ai_act:
      article: "12"
      title: "Record-Keeping"
      requirement: "High-risk AI systems shall technically allow for automatic recording of events"
    nist_ai_rmf:
      functions: ["MEASURE", "MANAGE"]
      subcategories:
        - "MEASURE 2.5: AI system is evaluated for runtime monitoring"
        - "MANAGE 3.1: AI risks and benefits from third-party resources are regularly monitored"
    iso_42001:
      controls:
        - "A.6.10: Logging and monitoring"

  article_13:
    eu_ai_act:
      article: "13"
      title: "Transparency and Provision of Information to Deployers"
      requirement: "High-risk AI systems shall be designed to ensure their operation is sufficiently transparent"
    nist_ai_rmf:
      functions: ["GOVERN", "MAP"]
      subcategories:
        - "GOVERN 4.1: Organizational practices are in place for transparency"
        - "MAP 1.5: Assumptions and limitations are documented"
    iso_42001:
      controls:
        - "A.6.8: Transparency and explainability"

  article_14:
    eu_ai_act:
      article: "14"
      title: "Human Oversight"
      requirement: "High-risk AI systems shall be designed so they can be effectively overseen by natural persons"
    nist_ai_rmf:
      functions: ["GOVERN", "MANAGE"]
      subcategories:
        - "GOVERN 1.3: Processes for human oversight are defined"
        - "MANAGE 2.2: Mechanisms are in place for human oversight of deployed AI"
    iso_42001:
      controls:
        - "A.6.3: Human oversight of AI systems"

  article_15:
    eu_ai_act:
      article: "15"
      title: "Accuracy, Robustness and Cybersecurity"
      requirement: "High-risk AI systems shall be designed to achieve an appropriate level of accuracy, robustness and cybersecurity"
    nist_ai_rmf:
      functions: ["MEASURE", "MANAGE"]
      subcategories:
        - "MEASURE 1.1: Approaches for measurement of AI risks are documented"
        - "MEASURE 2.6: AI system performance or assurance criteria are measured"
        - "MANAGE 2.4: Mechanisms are in place to address AI risks"
    iso_42001:
      controls:
        - "A.6.9: Performance and monitoring"
        - "A.8.1: Cybersecurity for AI"
```

- [ ] **Step 2: Commit**

```bash
cd /home/mkuziva/getregula
git add references/framework_crosswalk.yaml
git commit -m "data: add EU AI Act / NIST AI RMF / ISO 42001 crosswalk mapping"
```

---

### Task 5.2: Create Framework Mapper Module

**Files:**
- Create: `scripts/framework_mapper.py`
- Test: `tests/test_classification.py`

- [ ] **Step 1: Write failing tests**

```python
def test_framework_mapper_eu_to_nist():
    """Maps EU AI Act articles to NIST AI RMF functions"""
    from framework_mapper import map_to_frameworks
    mapping = map_to_frameworks(articles=["9", "14"], frameworks=["nist-ai-rmf"])
    assert_true("9" in mapping, "article 9 mapped")
    nist = mapping["9"]["nist_ai_rmf"]
    assert_true(len(nist["functions"]) > 0, "has NIST functions")
    assert_true("GOVERN" in nist["functions"], "Art 9 maps to GOVERN")
    print("✓ Framework mapper: EU AI Act to NIST AI RMF")


def test_framework_mapper_all_frameworks():
    """Maps to all three frameworks simultaneously"""
    from framework_mapper import map_to_frameworks
    mapping = map_to_frameworks(articles=["12"], frameworks=["all"])
    art12 = mapping["12"]
    assert_true("eu_ai_act" in art12, "has EU AI Act")
    assert_true("nist_ai_rmf" in art12, "has NIST AI RMF")
    assert_true("iso_42001" in art12, "has ISO 42001")
    print("✓ Framework mapper: all three frameworks mapped")
```

- [ ] **Step 2: Create framework_mapper.py**

Load crosswalk YAML (using existing YAML fallback parser), provide `map_to_frameworks(articles, frameworks)` function. Also provide `format_mapping_text()` and `format_mapping_json()`.

~150 lines. Loads `references/framework_crosswalk.yaml`, returns structured dicts filtered by requested frameworks.

- [ ] **Step 3: Run tests, verify pass, commit**

```bash
cd /home/mkuziva/getregula
git add scripts/framework_mapper.py tests/test_classification.py
git commit -m "feat: add cross-framework compliance mapper (EU AI Act / NIST / ISO 42001)"
```

---

## Phase 6: Enhanced HTML Report

### Task 6.1: Add Dependency and Framework Sections to HTML Report

**Files:**
- Modify: `scripts/report.py`
- Test: `tests/test_classification.py`

- [ ] **Step 1: Write failing test**

```python
def test_report_html_dependency_section():
    """HTML report includes dependency analysis section"""
    from report import generate_html_report
    findings = [{"file": "app.py", "tier": "high_risk", "category": "Employment",
                 "description": "CV screening", "confidence_score": 75, "suppressed": False}]
    dep_results = {"ai_dependencies": [{"name": "openai", "pinning": "exact"}],
                   "pinning_score": 80, "lockfiles": ["poetry.lock"], "compromised": []}
    html = generate_html_report(findings, "test-project", dependency_results=dep_results)
    assert_true("dependency" in html.lower() or "supply chain" in html.lower(),
                "HTML has dependency section")
    assert_true("openai" in html, "dependency listed")
    print("✓ Report: HTML includes dependency analysis section")
```

- [ ] **Step 2: Add optional `dependency_results` and `framework_mappings` parameters to `generate_html_report()`**

Add new HTML sections:
- Dependency analysis card (pinning score, AI library count, lockfile status)
- Dependency table (name, version, pinning quality, AI flag)
- Framework mapping tabs (EU AI Act / NIST / ISO 42001) if `framework_mappings` provided

Keep the existing report structure intact — these are additive sections.

- [ ] **Step 3: Run tests, verify pass, commit**

```bash
cd /home/mkuziva/getregula
git add scripts/report.py tests/test_classification.py
git commit -m "feat: add dependency and framework sections to HTML report"
```

---

## Phase 7: Policy Configuration Enhancement

### Task 7.1: Extend Policy Schema

**Files:**
- Modify: `regula-policy.yaml`
- Modify: `scripts/classify_risk.py`
- Test: `tests/test_classification.py`

- [ ] **Step 1: Write failing test**

```python
def test_policy_thresholds():
    """Policy thresholds are readable"""
    from classify_risk import get_policy
    policy = get_policy()
    # Should not crash even if thresholds are missing
    thresholds = policy.get("thresholds", {})
    assert_true(isinstance(thresholds, dict), "thresholds is dict or empty dict")
    print("✓ Policy: thresholds readable from policy")


def test_policy_exclusions():
    """Policy exclusions are readable"""
    from classify_risk import get_policy
    policy = get_policy()
    exclusions = policy.get("exclusions", {})
    assert_true(isinstance(exclusions, dict), "exclusions is dict or empty dict")
    print("✓ Policy: exclusions readable from policy")
```

- [ ] **Step 2: Update regula-policy.yaml with new schema fields**

Add `thresholds`, `exclusions`, and `approvals` sections per the spec.

- [ ] **Step 3: Run tests, verify pass, commit**

```bash
cd /home/mkuziva/getregula
git add regula-policy.yaml scripts/classify_risk.py tests/test_classification.py
git commit -m "feat: extend policy schema with thresholds, exclusions, approvals"
```

---

## Phase 8: Test Suite Expansion and Fixtures

### Task 8.1: Create Test Fixtures

**Files:**
- Create: `tests/fixtures/sample_high_risk/app.py`
- Create: `tests/fixtures/sample_high_risk/requirements.txt`
- Create: `tests/fixtures/sample_compliant/app.py`
- Create: `tests/fixtures/sample_compliant/requirements.txt`
- Create: `tests/fixtures/sample_compliant/model_card.md`
- Create: `tests/fixtures/sample_unpinned/package.json`

- [ ] **Step 1: Create sample_high_risk fixture**

`tests/fixtures/sample_high_risk/app.py`:
```python
import openai
from sklearn.ensemble import RandomForestClassifier

def screen_candidates(resumes):
    """Automated CV screening for hiring decisions."""
    model = RandomForestClassifier()
    model.fit(training_data, labels)
    predictions = model.predict(resumes)
    # No human review — directly filters candidates
    return [r for r, p in zip(resumes, predictions) if p == 1]
```

`tests/fixtures/sample_high_risk/requirements.txt`:
```
openai
scikit-learn
torch>=2.0
langchain
litellm
```

- [ ] **Step 2: Create sample_compliant fixture**

`tests/fixtures/sample_compliant/app.py`:
```python
import logging
import openai

logger = logging.getLogger(__name__)

def get_recommendation(data):
    """Get AI recommendation with human oversight."""
    client = openai.Client()
    result = client.chat.completions.create(model="gpt-4", messages=[{"role": "user", "content": str(data)}])
    logger.info("AI recommendation generated", extra={"input_hash": hash(str(data))})
    return result

def human_review(recommendation):
    """Human reviews and approves AI recommendation before action."""
    logger.info("Recommendation sent for human review")
    return {"status": "pending_review", "recommendation": recommendation}
```

`tests/fixtures/sample_compliant/requirements.txt`:
```
openai==1.52.0
```

`tests/fixtures/sample_compliant/model_card.md`:
```markdown
# Model Card: Recommendation System

## Intended Purpose
Internal recommendation system for document summarisation.

## Limitations
Not suitable for high-stakes decisions. May produce inaccurate summaries.

## Performance
Accuracy: 85% on internal benchmark.
```

- [ ] **Step 3: Create sample_unpinned fixture**

`tests/fixtures/sample_unpinned/package.json`:
```json
{
  "name": "ai-service",
  "dependencies": {
    "openai": "^4.0.0",
    "@anthropic-ai/sdk": "*",
    "@langchain/core": ">=0.1.0",
    "express": "~4.18.0"
  }
}
```

- [ ] **Step 4: Commit**

```bash
cd /home/mkuziva/getregula
git add tests/fixtures/
git commit -m "test: add sample project fixtures for integration testing"
```

---

### Task 8.2: Integration Tests Against Fixtures

**Files:**
- Modify: `tests/test_classification.py`

- [ ] **Step 1: Write integration tests**

```python
# ── Integration Tests ──────────────────────────────────────────────

def test_integration_high_risk_project():
    """Full scan of high-risk fixture project"""
    from report import scan_files
    fixture_path = str(Path(__file__).parent / "fixtures" / "sample_high_risk")
    if not Path(fixture_path).exists():
        print("✓ Integration: high-risk fixture (SKIPPED — fixture not found)")
        return
    findings = scan_files(fixture_path)
    tiers = [f["tier"] for f in findings if not f.get("suppressed")]
    assert_true("high_risk" in tiers, "detects high-risk in employment screening project")
    print("✓ Integration: high-risk fixture scanned correctly")


def test_integration_compliant_project():
    """Full scan of compliant fixture project"""
    from compliance_check import assess_compliance
    fixture_path = str(Path(__file__).parent / "fixtures" / "sample_compliant")
    if not Path(fixture_path).exists():
        print("✓ Integration: compliant fixture (SKIPPED — fixture not found)")
        return
    assessment = assess_compliance(fixture_path)
    assert_true(assessment["overall_score"] > 30,
                f"compliant project scores > 30 (got {assessment['overall_score']})")
    print("✓ Integration: compliant fixture assessed correctly")


def test_integration_unpinned_deps():
    """Dependency scan of unpinned fixture project"""
    from dependency_scan import scan_dependencies
    fixture_path = str(Path(__file__).parent / "fixtures" / "sample_unpinned")
    if not Path(fixture_path).exists():
        print("✓ Integration: unpinned fixture (SKIPPED — fixture not found)")
        return
    results = scan_dependencies(fixture_path)
    assert_true(results["pinning_score"] < 50,
                f"unpinned project scores < 50 (got {results['pinning_score']})")
    unpinned = [d for d in results.get("ai_dependencies", []) if d["pinning"] == "unpinned"]
    assert_true(len(unpinned) > 0, "finds unpinned AI deps")
    print("✓ Integration: unpinned dependency fixture scanned correctly")


def test_integration_full_check_cli():
    """CLI check command runs end-to-end on fixture"""
    import subprocess
    fixture_path = str(Path(__file__).parent / "fixtures" / "sample_high_risk")
    if not Path(fixture_path).exists():
        print("✓ Integration: CLI check (SKIPPED — fixture not found)")
        return
    result = subprocess.run(
        [sys.executable, "scripts/cli.py", "check", fixture_path, "--format", "json"],
        capture_output=True, text=True, timeout=30,
        cwd=str(Path(__file__).parent.parent),
    )
    try:
        findings = json.loads(result.stdout)
        assert_true(isinstance(findings, list), "CLI outputs JSON list")
        assert_true(len(findings) > 0, "CLI finds issues in high-risk project")
    except json.JSONDecodeError:
        assert_true(False, f"CLI output is not valid JSON: {result.stdout[:200]}")
    print("✓ Integration: CLI check runs end-to-end")
```

Add all four to the tests list.

- [ ] **Step 2: Run full test suite**

Run: `cd /home/mkuziva/getregula && python3 tests/test_classification.py 2>&1 | tail -10`
Expected: All tests pass (150+ total).

- [ ] **Step 3: Commit**

```bash
cd /home/mkuziva/getregula
git add tests/test_classification.py
git commit -m "test: add integration tests against fixture projects"
```

---

### Task 8.3: Update Documentation

**Files:**
- Modify: `SKILL.md`
- Modify: `README.md`

- [ ] **Step 1: Update SKILL.md with new commands**

Add to the commands table:
```markdown
| `/regula-deps` | AI dependency supply chain analysis |
```

Update limitations to note JS/TS support.

- [ ] **Step 2: Update README.md**

Add sections for:
- Dependency supply chain analysis (`regula deps`)
- Cross-framework mapping (`--framework` option)
- Sample output from each new feature
- Updated test count
- Updated architecture diagram

- [ ] **Step 3: Commit**

```bash
cd /home/mkuziva/getregula
git add SKILL.md README.md
git commit -m "docs: update documentation for new features"
```

---

## Final Verification

After all phases are complete:

- [ ] **Run full test suite**: `cd /home/mkuziva/getregula && python3 tests/test_classification.py`
  - Expected: 150+ tests, all passing

- [ ] **Test against a real project**: `python3 scripts/cli.py check /path/to/an/ai-project`
  - Verify output includes risk classification, dependency analysis, and compliance gaps

- [ ] **Verify SARIF output**: `python3 scripts/cli.py check . --format sarif | python3 -m json.tool`
  - Should be valid JSON matching SARIF 2.1.0 schema

- [ ] **Verify HTML report**: `python3 scripts/cli.py report --format html -o /tmp/test-report.html`
  - Open in browser, verify all sections render

- [ ] **Verify dependency scan**: `python3 scripts/cli.py deps --project .`
  - Should analyse getregula's own dependencies

- [ ] **Verify gap assessment**: `python3 scripts/cli.py gap --project .`
  - Should produce per-article scores with evidence

---

## Summary of Deliverables

| Phase | Files Created | Files Modified | Tests Added |
|-------|-------------|----------------|-------------|
| 1. AST Engine | `scripts/ast_engine.py` | `pyproject.toml` | 5 |
| 2. Dependency Scan | `scripts/dependency_scan.py`, `references/advisories/...` | `scripts/cli.py` | 6 |
| 3. CLI Unification | — | `scripts/cli.py` | — |
| 4. Gap Enhancement | — | `scripts/compliance_check.py` | 1 |
| 5. Framework Mapper | `scripts/framework_mapper.py`, `references/framework_crosswalk.yaml` | — | 2 |
| 6. HTML Report | — | `scripts/report.py` | 1 |
| 7. Policy Config | — | `regula-policy.yaml`, `scripts/classify_risk.py` | 2 |
| 8. Test Expansion | `tests/fixtures/*` (6 files) | `tests/test_classification.py` | 4 |
| **Total** | **10 new files** | **8 modified files** | **21 new tests** |

Combined with existing 84 tests → **105+ tests minimum** (plus any additional tests discovered during implementation).
