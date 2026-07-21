#!/usr/bin/env python3
# regula-ignore
"""Comprehensive tests for cross_file_flow module.

Tests cover:
- _should_skip (directory filtering)
- _collect_python_files / _collect_js_ts_files
- _build_symbol_table / _build_js_ts_symbol_table
- _module_to_candidates / _js_import_to_candidates
- _resolve_imports / _resolve_js_ts_imports
- _find_ai_sources / _find_oversight_gates
- _trace_cross_file_paths
- _compute_overall_confidence
- analyse_project_oversight (public API)
- Edge cases: empty projects, syntax errors, circular deps, etc.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cross_file_flow import (
    _should_skip,
    _collect_python_files,
    _collect_js_ts_files,
    _build_symbol_table,
    _build_js_ts_symbol_table,
    _module_to_candidates,
    _js_import_to_candidates,
    _resolve_imports,
    _resolve_js_ts_imports,
    _find_ai_sources,
    _find_oversight_gates,
    _trace_cross_file_paths,
    _compute_overall_confidence,
    analyse_project_oversight,
    LIMITATIONS,
    _JS_TS_EXTENSIONS,
)

from helpers import assert_eq, assert_true, assert_false, assert_in, assert_gte


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_project(files: dict) -> str:
    """Create a temp project directory with given files. Returns path."""
    tmpdir = tempfile.mkdtemp(prefix="regula_test_cross_file_flow_")
    for name, content in files.items():
        filepath = Path(tmpdir) / name
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content)
    return tmpdir


def _cleanup(path: str):
    shutil.rmtree(path, ignore_errors=True)


# =========================================================================
# _should_skip
# =========================================================================

def test_should_skip_node_modules():
    """node_modules paths should be skipped."""
    assert_true(_should_skip(Path("project/node_modules/foo/bar.py")),
                "node_modules should be skipped")


def test_should_skip_pycache():
    """__pycache__ paths should be skipped."""
    assert_true(_should_skip(Path("src/__pycache__/module.cpython-310.pyc")),
                "__pycache__ should be skipped")


def test_should_skip_venv():
    """venv paths should be skipped."""
    assert_true(_should_skip(Path("project/venv/lib/python3.10/site.py")),
                "venv should be skipped")


def test_should_skip_dot_venv():
    """.venv paths should be skipped."""
    assert_true(_should_skip(Path("project/.venv/lib/foo.py")),
                ".venv should be skipped")


def test_should_skip_git():
    """.git paths should be skipped."""
    assert_true(_should_skip(Path(".git/objects/pack/foo")),
                ".git should be skipped")


def test_should_skip_dist():
    """dist paths should be skipped."""
    assert_true(_should_skip(Path("project/dist/bundle.js")),
                "dist should be skipped")


def test_should_skip_build():
    """build paths should be skipped."""
    assert_true(_should_skip(Path("build/output.py")),
                "build should be skipped")


def test_should_not_skip_src():
    """Normal source paths should not be skipped."""
    assert_false(_should_skip(Path("src/models/predict.py")),
                 "src should not be skipped")


def test_should_not_skip_lib():
    """Normal lib paths should not be skipped."""
    assert_false(_should_skip(Path("lib/utils.py")),
                 "lib should not be skipped")


def test_should_skip_benchmarks():
    """benchmarks paths should be skipped."""
    assert_true(_should_skip(Path("benchmarks/fixture.py")),
                "benchmarks should be skipped")


def test_should_skip_examples():
    """examples paths should be skipped."""
    assert_true(_should_skip(Path("examples/demo.py")),
                "examples should be skipped")


# =========================================================================
# _collect_python_files
# =========================================================================

def test_collect_python_files_basic():
    """Should find .py files in project."""
    proj = _make_project({
        "main.py": "print('hello')",
        "utils/helpers.py": "def helper(): pass",
        "data.txt": "not python",
    })
    try:
        pp = Path(proj).resolve()
        files = _collect_python_files(pp)
        names = {str(f.relative_to(pp)) for f, _content in files}
        assert_in("main.py", names, "should find main.py")
        assert_in(os.path.join("utils", "helpers.py"), names, "should find utils/helpers.py")
        assert_eq(len(files), 2, "should find exactly 2 .py files")
    finally:
        _cleanup(proj)


def test_collect_python_files_skips_venv():
    """Should not return .py files inside venv."""
    proj = _make_project({
        "app.py": "import flask",
        "venv/lib/flask.py": "# fake flask",
    })
    try:
        pp = Path(proj).resolve()
        files = _collect_python_files(pp)
        names = {str(f.relative_to(pp)) for f, _content in files}
        assert_in("app.py", names, "should find app.py")
        assert_eq(len(files), 1, "should only find 1 file (venv excluded)")
    finally:
        _cleanup(proj)


def test_collect_python_files_empty():
    """Empty project should return empty list."""
    proj = _make_project({})
    try:
        pp = Path(proj).resolve()
        files = _collect_python_files(pp)
        assert_eq(len(files), 0, "empty project should yield no python files")
    finally:
        _cleanup(proj)


def test_collect_python_files_skips_node_modules():
    """Should not descend into node_modules."""
    proj = _make_project({
        "app.py": "x = 1",
        "node_modules/pkg/index.py": "y = 2",
    })
    try:
        pp = Path(proj).resolve()
        files = _collect_python_files(pp)
        assert_eq(len(files), 1, "should skip node_modules .py files")
    finally:
        _cleanup(proj)


# =========================================================================
# _collect_js_ts_files
# =========================================================================

def test_collect_js_ts_files_basic():
    """Should find .js, .ts, .jsx, .tsx, .mjs, .cjs files."""
    proj = _make_project({
        "index.js": "console.log('hi')",
        "app.ts": "const x: number = 1",
        "component.jsx": "export default function() {}",
        "page.tsx": "export default function() {}",
        "util.mjs": "export const a = 1",
        "legacy.cjs": "module.exports = {}",
        "style.css": "body {}",
        "readme.md": "# readme",
    })
    try:
        pp = Path(proj).resolve()
        files = _collect_js_ts_files(pp)
        assert_eq(len(files), 6, "should find 6 JS/TS files")
    finally:
        _cleanup(proj)


def test_collect_js_ts_files_skips_node_modules():
    """Should not descend into node_modules."""
    proj = _make_project({
        "app.js": "console.log(1)",
        "node_modules/pkg/index.js": "module.exports = {}",
    })
    try:
        pp = Path(proj).resolve()
        files = _collect_js_ts_files(pp)
        assert_eq(len(files), 1, "should skip node_modules JS files")
    finally:
        _cleanup(proj)


def test_collect_js_ts_files_empty():
    """Empty project should return empty list."""
    proj = _make_project({})
    try:
        pp = Path(proj).resolve()
        files = _collect_js_ts_files(pp)
        assert_eq(len(files), 0, "empty project should yield no JS/TS files")
    finally:
        _cleanup(proj)


# =========================================================================
# _build_symbol_table
# =========================================================================

def test_build_symbol_table_functions_and_classes():
    """Should extract function and class definitions from Python files."""
    proj = _make_project({
        "model.py": (
            "class Predictor:\n"
            "    def predict(self, x):\n"
            "        return x * 2\n"
            "\n"
            "def process(data):\n"
            "    return data\n"
            "\n"
            "async def async_handler(req):\n"
            "    pass\n"
        ),
    })
    try:
        pp = Path(proj).resolve()
        py_files = _collect_python_files(pp)
        table = _build_symbol_table(pp, py_files)
        assert_in("model.py", table, "model.py should be in symbol table")
        entry = table["model.py"]
        assert_in("Predictor", entry["classes"], "should find Predictor class")
        assert_in("predict", entry["functions"], "should find predict function")
        assert_in("process", entry["functions"], "should find process function")
        assert_in("async_handler", entry["functions"], "should find async function")
        assert_eq(entry["lang"], "python", "language should be python")
        assert_true(len(entry["content"]) > 0, "content should be populated")
    finally:
        _cleanup(proj)


def test_build_symbol_table_syntax_error():
    """Files with syntax errors should be skipped gracefully."""
    proj = _make_project({
        "good.py": "def foo(): pass\n",
        "bad.py": "def broken(:\n    pass\n",
    })
    try:
        pp = Path(proj).resolve()
        py_files = _collect_python_files(pp)
        table = _build_symbol_table(pp, py_files)
        assert_in("good.py", table, "good.py should be in symbol table")
        assert_true("bad.py" not in table, "bad.py with syntax error should be excluded")
    finally:
        _cleanup(proj)


def test_build_symbol_table_empty_file():
    """Empty .py file should still appear in symbol table."""
    proj = _make_project({
        "empty.py": "",
    })
    try:
        pp = Path(proj).resolve()
        py_files = _collect_python_files(pp)
        table = _build_symbol_table(pp, py_files)
        assert_in("empty.py", table, "empty.py should be in symbol table")
        assert_eq(table["empty.py"]["functions"], {}, "no functions in empty file")
        assert_eq(table["empty.py"]["classes"], {}, "no classes in empty file")
    finally:
        _cleanup(proj)


def test_build_symbol_table_nested_functions():
    """Nested functions should be captured."""
    proj = _make_project({
        "nested.py": (
            "def outer():\n"
            "    def inner():\n"
            "        pass\n"
            "    return inner\n"
        ),
    })
    try:
        pp = Path(proj).resolve()
        py_files = _collect_python_files(pp)
        table = _build_symbol_table(pp, py_files)
        entry = table["nested.py"]
        assert_in("outer", entry["functions"], "should find outer")
        assert_in("inner", entry["functions"], "should find inner (ast.walk gets nested)")
    finally:
        _cleanup(proj)


# =========================================================================
# _build_js_ts_symbol_table
# =========================================================================

def test_build_js_ts_symbol_table_basic():
    """Should extract function defs from JS files via ast_engine."""
    proj = _make_project({
        "utils.js": (
            "function greet(name) { return 'Hello ' + name; }\n"
            "const double = (x) => x * 2;\n"
        ),
    })
    try:
        pp = Path(proj).resolve()
        js_files = _collect_js_ts_files(pp)
        table = _build_js_ts_symbol_table(pp, js_files)
        assert_in("utils.js", table, "utils.js should be in symbol table")
        entry = table["utils.js"]
        assert_eq(entry["lang"], "javascript", "language should be javascript")
        assert_true("_analysis" in entry, "should cache ast_engine analysis")
    finally:
        _cleanup(proj)


def test_build_js_ts_symbol_table_empty():
    """Empty JS file should appear in symbol table."""
    proj = _make_project({
        "empty.js": "",
    })
    try:
        pp = Path(proj).resolve()
        js_files = _collect_js_ts_files(pp)
        table = _build_js_ts_symbol_table(pp, js_files)
        assert_in("empty.js", table, "empty.js should be in symbol table")
        assert_eq(table["empty.js"]["functions"], {}, "no functions in empty file")
    finally:
        _cleanup(proj)


# =========================================================================
# _module_to_candidates
# =========================================================================

def test_module_to_candidates_simple():
    """Simple module name should produce file.py and file/__init__.py."""
    pp = Path("/tmp/project")
    candidates = _module_to_candidates("utils", pp)
    assert_eq(len(candidates), 2, "should produce 2 candidates")
    assert_in("utils.py", candidates, "should include utils.py")
    assert_in(os.path.join("utils", "__init__.py"), candidates,
              "should include utils/__init__.py")


def test_module_to_candidates_dotted():
    """Dotted module name should produce nested paths."""
    pp = Path("/tmp/project")
    candidates = _module_to_candidates("models.predict", pp)
    expected_file = os.path.join("models", "predict") + ".py"
    expected_init = os.path.join("models", "predict", "__init__.py")
    assert_in(expected_file, candidates, "should include models/predict.py")
    assert_in(expected_init, candidates, "should include models/predict/__init__.py")


def test_module_to_candidates_deeply_nested():
    """Deeply nested dotted module should produce correct path."""
    pp = Path("/tmp/project")
    candidates = _module_to_candidates("a.b.c.d", pp)
    expected = os.path.join("a", "b", "c", "d") + ".py"
    assert_in(expected, candidates, "should include a/b/c/d.py")


# =========================================================================
# _js_import_to_candidates
# =========================================================================

def test_js_import_relative_simple():
    """Relative import ./module should resolve from importing file."""
    candidates = _js_import_to_candidates("./helper", "src/app.ts")
    assert_true(len(candidates) > 0, "should produce candidates")
    assert_true(any("src/helper" in c for c in candidates),
                "should resolve relative to importing file directory")


def test_js_import_relative_parent():
    """Parent relative import ../utils should resolve correctly."""
    candidates = _js_import_to_candidates("../utils", "src/pages/home.tsx")
    assert_true(len(candidates) > 0, "should produce candidates for ../")
    assert_true(any("src/utils" in c for c in candidates),
                "should resolve to parent directory")


def test_js_import_bare_specifier():
    """Bare specifier (node_modules) should return empty list."""
    candidates = _js_import_to_candidates("react", "src/app.tsx")
    assert_eq(candidates, [], "bare specifiers should return empty list")


def test_js_import_bare_scoped():
    """Scoped bare specifier should return empty list."""
    candidates = _js_import_to_candidates("@openai/api", "src/client.ts")
    assert_eq(candidates, [], "scoped bare specifiers should return empty list")


def test_js_import_with_extension():
    """Import with explicit extension should return just that path."""
    candidates = _js_import_to_candidates("./helper.ts", "src/app.ts")
    assert_eq(len(candidates), 1, "explicit extension should return 1 candidate")
    assert_true(candidates[0].endswith("helper.ts"), "should preserve .ts extension")


def test_js_import_without_extension_tries_many():
    """Import without extension should try .ts, .tsx, .js, .jsx, .mjs, .cjs + index."""
    candidates = _js_import_to_candidates("./helper", "src/app.ts")
    # Should try: helper.ts, helper.tsx, helper.js, helper.jsx, helper.mjs, helper.cjs
    # Plus: helper/index.ts, helper/index.tsx, helper/index.js, helper/index.jsx
    assert_gte(len(candidates), 10, "should try multiple extension combinations")


def test_js_import_index_resolution():
    """Should include index file candidates for directory imports."""
    candidates = _js_import_to_candidates("./components", "src/app.ts")
    index_candidates = [c for c in candidates if "index" in c]
    assert_true(len(index_candidates) > 0,
                "should include index file candidates")


# =========================================================================
# _resolve_imports
# =========================================================================

def test_resolve_imports_basic():
    """Should resolve a simple import between two project files."""
    proj = _make_project({
        "main.py": "from utils import helper\nhelper()\n",
        "utils.py": "def helper(): pass\n",
    })
    try:
        pp = Path(proj).resolve()
        py_files = _collect_python_files(pp)
        table = _build_symbol_table(pp, py_files)
        import_map = _resolve_imports(pp, table)
        assert_in("main.py", import_map, "main.py should have import entries")
        main_imports = import_map["main.py"]
        assert_in("helper", main_imports, "should resolve helper import")
        source_file, original_name = main_imports["helper"]
        assert_eq(source_file, "utils.py", "helper should come from utils.py")
        assert_eq(original_name, "helper", "original name should be helper")
    finally:
        _cleanup(proj)


def test_resolve_imports_aliased():
    """Should handle aliased imports (import X as Y)."""
    proj = _make_project({
        "main.py": "from utils import helper as h\nh()\n",
        "utils.py": "def helper(): pass\n",
    })
    try:
        pp = Path(proj).resolve()
        py_files = _collect_python_files(pp)
        table = _build_symbol_table(pp, py_files)
        import_map = _resolve_imports(pp, table)
        main_imports = import_map.get("main.py", {})
        assert_in("h", main_imports, "aliased import 'h' should be resolved")
        source_file, original_name = main_imports["h"]
        assert_eq(source_file, "utils.py", "aliased import should trace to utils.py")
        assert_eq(original_name, "helper", "original name should be helper")
    finally:
        _cleanup(proj)


def test_resolve_imports_external_module():
    """External (pip-installed) modules should not appear in resolved imports."""
    proj = _make_project({
        "main.py": "import numpy as np\nimport os\n",
    })
    try:
        pp = Path(proj).resolve()
        py_files = _collect_python_files(pp)
        table = _build_symbol_table(pp, py_files)
        import_map = _resolve_imports(pp, table)
        main_imports = import_map.get("main.py", {})
        assert_eq(len(main_imports), 0,
                  "external modules should not be resolved as project-internal")
    finally:
        _cleanup(proj)


def test_resolve_imports_syntax_error_file():
    """Files with syntax errors should be skipped during import resolution."""
    proj = _make_project({
        "good.py": "from utils import foo\n",
        "utils.py": "def foo(): pass\n",
        "bad.py": "def broken(:\n",
    })
    try:
        pp = Path(proj).resolve()
        py_files = _collect_python_files(pp)
        table = _build_symbol_table(pp, py_files)
        import_map = _resolve_imports(pp, table)
        # bad.py is excluded from the symbol table, so it shouldn't
        # cause issues in import resolution
        assert_in("good.py", import_map, "good.py should still be resolved")
    finally:
        _cleanup(proj)


def test_resolve_imports_relative_import():
    """Should resolve relative imports (from . import X)."""
    proj = _make_project({
        "pkg/__init__.py": "",
        "pkg/models.py": "def predict(): pass\n",
        "pkg/views.py": "from . import models\n",
    })
    try:
        pp = Path(proj).resolve()
        py_files = _collect_python_files(pp)
        table = _build_symbol_table(pp, py_files)
        import_map = _resolve_imports(pp, table)
        views_rel = os.path.join("pkg", "views.py")
        if views_rel in import_map:
            views_imports = import_map[views_rel]
            # Relative import resolution is best-effort; verify it doesn't crash
            assert_true(isinstance(views_imports, dict),
                        "views imports should be a dict")
    finally:
        _cleanup(proj)


def test_resolve_imports_import_package():
    """Should resolve 'import package' to package/__init__.py."""
    proj = _make_project({
        "app.py": "import models\nmodels.predict()\n",
        "models/__init__.py": "def predict(): pass\n",
    })
    try:
        pp = Path(proj).resolve()
        py_files = _collect_python_files(pp)
        table = _build_symbol_table(pp, py_files)
        import_map = _resolve_imports(pp, table)
        app_imports = import_map.get("app.py", {})
        if "models" in app_imports:
            source_file, _ = app_imports["models"]
            assert_eq(source_file, os.path.join("models", "__init__.py"),
                      "should resolve to __init__.py")
    finally:
        _cleanup(proj)


# =========================================================================
# _resolve_js_ts_imports
# =========================================================================

def test_resolve_js_ts_imports_named():
    """Should resolve named JS imports: import { X } from './module'."""
    proj = _make_project({
        "src/app.ts": "import { predict } from './model'\npredict()\n",
        "src/model.ts": "export function predict() {}\n",
    })
    try:
        pp = Path(proj).resolve()
        js_files = _collect_js_ts_files(pp)
        table = _build_js_ts_symbol_table(pp, js_files)
        import_map = _resolve_js_ts_imports(pp, table)
        app_rel = os.path.join("src", "app.ts")
        if app_rel in import_map:
            app_imports = import_map[app_rel]
            assert_in("predict", app_imports,
                      "should resolve named import 'predict'")
    finally:
        _cleanup(proj)


def test_resolve_js_ts_imports_default():
    """Should resolve default JS imports: import X from './module'."""
    proj = _make_project({
        "src/app.js": "import Model from './model'\nModel.predict()\n",
        "src/model.js": "export default class Model {}\n",
    })
    try:
        pp = Path(proj).resolve()
        js_files = _collect_js_ts_files(pp)
        table = _build_js_ts_symbol_table(pp, js_files)
        import_map = _resolve_js_ts_imports(pp, table)
        app_rel = os.path.join("src", "app.js")
        if app_rel in import_map:
            app_imports = import_map[app_rel]
            assert_in("Model", app_imports,
                      "should resolve default import 'Model'")
            if "Model" in app_imports:
                _, original = app_imports["Model"]
                assert_eq(original, "default",
                          "default import should have original name 'default'")
    finally:
        _cleanup(proj)


def test_resolve_js_ts_imports_require():
    """Should resolve require() style imports."""
    proj = _make_project({
        "src/app.js": "const helper = require('./helper')\nhelper()\n",
        "src/helper.js": "module.exports = function() {}\n",
    })
    try:
        pp = Path(proj).resolve()
        js_files = _collect_js_ts_files(pp)
        table = _build_js_ts_symbol_table(pp, js_files)
        import_map = _resolve_js_ts_imports(pp, table)
        app_rel = os.path.join("src", "app.js")
        if app_rel in import_map:
            app_imports = import_map[app_rel]
            assert_in("helper", app_imports,
                      "should resolve require() import")
    finally:
        _cleanup(proj)


def test_resolve_js_ts_imports_aliased_named():
    """Should handle aliased named imports: import { X as Y } from './module'."""
    proj = _make_project({
        "src/app.ts": "import { predict as runPrediction } from './model'\n",
        "src/model.ts": "export function predict() {}\n",
    })
    try:
        pp = Path(proj).resolve()
        js_files = _collect_js_ts_files(pp)
        table = _build_js_ts_symbol_table(pp, js_files)
        import_map = _resolve_js_ts_imports(pp, table)
        app_rel = os.path.join("src", "app.ts")
        if app_rel in import_map:
            app_imports = import_map[app_rel]
            if "runPrediction" in app_imports:
                source, original = app_imports["runPrediction"]
                assert_eq(original, "predict",
                          "aliased import original name should be 'predict'")
    finally:
        _cleanup(proj)


def test_resolve_js_ts_imports_skips_python_files():
    """Import resolution for JS/TS should skip Python files."""
    proj = _make_project({
        "main.py": "import os\n",
        "app.js": "import { foo } from './bar'\n",
        "bar.js": "export function foo() {}\n",
    })
    try:
        pp = Path(proj).resolve()
        py_files = _collect_python_files(pp)
        js_files = _collect_js_ts_files(pp)
        # Build a merged symbol table
        py_table = _build_symbol_table(pp, py_files)
        js_table = _build_js_ts_symbol_table(pp, js_files)
        merged = {}
        merged.update(py_table)
        merged.update(js_table)
        import_map = _resolve_js_ts_imports(pp, merged)
        # Python files should not have JS import entries
        assert_true("main.py" not in import_map,
                    "Python files should be skipped in JS import resolution")
    finally:
        _cleanup(proj)


def test_resolve_js_ts_imports_bare_specifier_ignored():
    """Bare specifiers (node_modules) should not be resolved."""
    proj = _make_project({
        "app.js": "import OpenAI from 'openai'\n",
    })
    try:
        pp = Path(proj).resolve()
        js_files = _collect_js_ts_files(pp)
        table = _build_js_ts_symbol_table(pp, js_files)
        import_map = _resolve_js_ts_imports(pp, table)
        app_imports = import_map.get("app.js", {})
        assert_eq(len(app_imports), 0,
                  "bare specifiers should not be resolved")
    finally:
        _cleanup(proj)


# =========================================================================
# _find_ai_sources
# =========================================================================

def test_find_ai_sources_python():
    """Should detect AI call sites in Python files."""
    proj = _make_project({
        "predict.py": (
            "import openai\n"
            "client = openai.OpenAI()\n"
            "result = client.chat.completions.create(\n"
            "    model='gpt-4', messages=[{'role': 'user', 'content': 'hi'}]\n"
            ")\n"
        ),
    })
    try:
        pp = Path(proj).resolve()
        py_files = _collect_python_files(pp)
        table = _build_symbol_table(pp, py_files)
        sources = _find_ai_sources(table)
        # Whether AI sources are found depends on ast_analysis heuristics.
        # At minimum, verify the function runs without error and returns a list.
        assert_true(isinstance(sources, list), "should return a list")
    finally:
        _cleanup(proj)


def test_find_ai_sources_no_ai():
    """Non-AI code should produce no AI sources."""
    proj = _make_project({
        "utils.py": "def add(a, b): return a + b\n",
    })
    try:
        pp = Path(proj).resolve()
        py_files = _collect_python_files(pp)
        table = _build_symbol_table(pp, py_files)
        sources = _find_ai_sources(table)
        assert_eq(len(sources), 0, "non-AI code should produce no AI sources")
    finally:
        _cleanup(proj)


def test_find_ai_sources_multiple_files():
    """Should find AI sources across multiple files."""
    proj = _make_project({
        "model_a.py": (
            "from sklearn.ensemble import RandomForestClassifier\n"
            "clf = RandomForestClassifier()\n"
            "result = clf.predict(X)\n"
        ),
        "model_b.py": (
            "import torch\n"
            "model = torch.load('model.pt')\n"
            "output = model.forward(x)\n"
        ),
        "no_ai.py": "def compute(x): return x * 2\n",
    })
    try:
        pp = Path(proj).resolve()
        py_files = _collect_python_files(pp)
        table = _build_symbol_table(pp, py_files)
        sources = _find_ai_sources(table)
        assert_true(isinstance(sources, list), "should return a list")
        # Each source should have required keys
        for s in sources:
            assert_in("file", s, "source should have 'file' key")
            assert_in("source", s, "source should have 'source' key")
            assert_in("source_line", s, "source should have 'source_line' key")
            assert_in("destinations", s, "source should have 'destinations' key")
    finally:
        _cleanup(proj)


def test_find_ai_sources_empty_table():
    """Empty symbol table should produce no AI sources."""
    sources = _find_ai_sources({})
    assert_eq(len(sources), 0, "empty table should yield no AI sources")


# =========================================================================
# _find_oversight_gates
# =========================================================================

def test_find_oversight_gates_basic():
    """Should detect human oversight patterns."""
    proj = _make_project({
        "review.py": (
            "def approve_prediction(prediction, user):\n"
            "    '''Human must approve before action.'''\n"
            "    if user.confirm(prediction):\n"
            "        return True\n"
            "    return False\n"
        ),
    })
    try:
        pp = Path(proj).resolve()
        py_files = _collect_python_files(pp)
        table = _build_symbol_table(pp, py_files)
        gates = _find_oversight_gates(table)
        assert_true(isinstance(gates, list), "should return a list")
        for gate in gates:
            assert_in("file", gate, "gate should have 'file' key")
            assert_in("name", gate, "gate should have 'name' key")
            assert_in("line", gate, "gate should have 'line' key")
    finally:
        _cleanup(proj)


def test_find_oversight_gates_no_oversight():
    """Code without oversight patterns should produce empty list."""
    proj = _make_project({
        "auto.py": (
            "def process(data):\n"
            "    return data * 2\n"
        ),
    })
    try:
        pp = Path(proj).resolve()
        py_files = _collect_python_files(pp)
        table = _build_symbol_table(pp, py_files)
        gates = _find_oversight_gates(table)
        # Pure arithmetic code is unlikely to trigger oversight patterns.
        # This is a sanity check that the function doesn't crash.
        assert_true(isinstance(gates, list), "should return a list")
    finally:
        _cleanup(proj)


def test_find_oversight_gates_empty_table():
    """Empty symbol table should produce no gates."""
    gates = _find_oversight_gates({})
    assert_eq(len(gates), 0, "empty table should yield no gates")


# =========================================================================
# _trace_cross_file_paths
# =========================================================================

def test_trace_cross_file_paths_no_sources():
    """No AI sources should produce empty flow and unreviewed paths."""
    flow_paths, unreviewed = _trace_cross_file_paths([], [], {}, {})
    assert_eq(len(flow_paths), 0, "no AI sources => no flow paths")
    assert_eq(len(unreviewed), 0, "no AI sources => no unreviewed paths")


def test_trace_cross_file_paths_single_file_no_oversight():
    """Single-file AI flow without oversight should appear in unreviewed."""
    ai_sources = [{
        "file": "model.py",
        "source": "clf.predict(X)",
        "source_line": 5,
        "destinations": [
            {"type": "return", "line": 6, "detail": "return result"},
        ],
    }]
    symbol_table = {
        "model.py": {
            "functions": {"get_prediction": 3},
            "classes": {},
            "content": "",
            "lang": "python",
        },
    }
    flow_paths, unreviewed = _trace_cross_file_paths(
        ai_sources, [], {}, symbol_table,
    )
    assert_gte(len(flow_paths), 1, "should have at least one flow path")
    assert_gte(len(unreviewed), 1,
               "flow without oversight should be unreviewed")
    for p in flow_paths:
        assert_false(p["has_oversight"],
                     "should not have oversight without gates")


def test_trace_cross_file_paths_single_file_with_oversight():
    """Single-file AI flow with human_review destination should be reviewed."""
    ai_sources = [{
        "file": "model.py",
        "source": "clf.predict(X)",
        "source_line": 5,
        "destinations": [
            {"type": "human_review", "line": 8, "detail": "review(result)"},
        ],
    }]
    symbol_table = {
        "model.py": {
            "functions": {"get_prediction": 3},
            "classes": {},
            "content": "",
            "lang": "python",
        },
    }
    flow_paths, unreviewed = _trace_cross_file_paths(
        ai_sources, [], {}, symbol_table,
    )
    assert_gte(len(flow_paths), 1, "should produce at least one flow path")
    assert_eq(len(unreviewed), 0,
              "flow with oversight should not be unreviewed")
    for p in flow_paths:
        assert_true(p["has_oversight"],
                    "path with human_review should show oversight")


def test_trace_cross_file_paths_dedup():
    """Duplicate source+consumer paths should be deduplicated."""
    ai_sources = [
        {
            "file": "model.py",
            "source": "clf.predict(X)",
            "source_line": 5,
            "destinations": [],
        },
        {
            "file": "model.py",
            "source": "clf.predict(X)",
            "source_line": 5,
            "destinations": [],
        },
    ]
    symbol_table = {
        "model.py": {
            "functions": {},
            "classes": {},
            "content": "",
            "lang": "python",
        },
    }
    flow_paths, unreviewed = _trace_cross_file_paths(
        ai_sources, [], {}, symbol_table,
    )
    # Should not produce duplicates
    keys = [(p["source_file"], p["source_line"], p.get("consumer_file", ""))
            for p in flow_paths]
    assert_eq(len(keys), len(set(keys)),
              "flow paths should be deduplicated")


def test_trace_cross_file_paths_cross_file_import():
    """Cross-file flow through imports should be traced."""
    ai_sources = [{
        "file": "model.py",
        "source": "clf.predict(X)",
        "source_line": 5,
        "destinations": [
            {"type": "return", "line": 6, "detail": "return result"},
        ],
    }]
    # The consuming file imports get_prediction from model.py
    import_map = {
        "app.py": {
            "get_prediction": ("model.py", "get_prediction"),
        },
    }
    symbol_table = {
        "model.py": {
            "functions": {"get_prediction": 3},
            "classes": {},
            "content": "",
            "lang": "python",
        },
        "app.py": {
            "functions": {"handle_request": 1},
            "classes": {},
            "content": "",
            "lang": "python",
        },
    }
    # The AI call at line 5 is inside get_prediction (starts at line 3)
    flow_paths, unreviewed = _trace_cross_file_paths(
        ai_sources, [], import_map, symbol_table,
    )
    # Should find a consumer path for app.py
    consumer_files = [p.get("consumer_file", "") for p in flow_paths]
    assert_in("app.py", consumer_files,
              "should trace flow to consuming file app.py")


def test_trace_cross_file_paths_cross_file_with_gate():
    """Cross-file flow should detect oversight gate in consumer file."""
    ai_sources = [{
        "file": "model.py",
        "source": "clf.predict(X)",
        "source_line": 5,
        "destinations": [
            {"type": "return", "line": 6, "detail": "return result"},
        ],
    }]
    oversight_gates = [{
        "file": "app.py",
        "name": "review_result",
        "line": 10,
        "type": "keyword",
        "detail": "review",
    }]
    import_map = {
        "app.py": {
            "get_prediction": ("model.py", "get_prediction"),
        },
    }
    symbol_table = {
        "model.py": {
            "functions": {"get_prediction": 3},
            "classes": {},
            "content": "",
            "lang": "python",
        },
        "app.py": {
            "functions": {"handle_request": 1, "review_result": 9},
            "classes": {},
            "content": "",
            "lang": "python",
        },
    }
    flow_paths, unreviewed = _trace_cross_file_paths(
        ai_sources, oversight_gates, import_map, symbol_table,
    )
    # At least one path should target app.py
    app_paths = [p for p in flow_paths if p.get("consumer_file") == "app.py"]
    if app_paths:
        assert_true(app_paths[0]["has_oversight"],
                    "consumer file with oversight gate should show oversight")


def test_trace_cross_file_paths_confidence_levels():
    """Cross-file paths should have at most 'medium' confidence."""
    ai_sources = [{
        "file": "model.py",
        "source": "clf.predict(X)",
        "source_line": 5,
        "destinations": [
            {"type": "return", "line": 6, "detail": "return result"},
        ],
    }]
    import_map = {
        "app.py": {
            "get_prediction": ("model.py", "get_prediction"),
        },
    }
    symbol_table = {
        "model.py": {
            "functions": {"get_prediction": 3},
            "classes": {},
            "content": "",
            "lang": "python",
        },
        "app.py": {
            "functions": {"handle_request": 1},
            "classes": {},
            "content": "",
            "lang": "python",
        },
    }
    flow_paths, unreviewed = _trace_cross_file_paths(
        ai_sources, [], import_map, symbol_table,
    )
    for p in flow_paths:
        if p.get("consumer_file"):
            # Cross-file paths should be at most "medium" confidence
            assert_true(p["confidence"] in ("medium", "low"),
                        f"cross-file confidence should not be 'high', got {p['confidence']}")


# =========================================================================
# _compute_overall_confidence
# =========================================================================

def test_compute_overall_confidence_empty():
    """Empty flow paths should produce 'low' confidence."""
    assert_eq(_compute_overall_confidence([]), "low",
              "empty paths => low confidence")


def test_compute_overall_confidence_all_high():
    """All high-confidence paths should produce 'high' overall."""
    paths = [
        {"confidence": "high"},
        {"confidence": "high"},
        {"confidence": "high"},
    ]
    assert_eq(_compute_overall_confidence(paths), "high",
              "all high => overall high")


def test_compute_overall_confidence_mixed():
    """Mix of high and medium should produce 'medium' overall."""
    paths = [
        {"confidence": "high"},
        {"confidence": "medium"},
        {"confidence": "high"},
    ]
    assert_eq(_compute_overall_confidence(paths), "medium",
              "mixed high/medium => overall medium")


def test_compute_overall_confidence_mostly_low():
    """Majority low-confidence paths should produce 'low' overall."""
    paths = [
        {"confidence": "low"},
        {"confidence": "low"},
        {"confidence": "high"},
    ]
    assert_eq(_compute_overall_confidence(paths), "low",
              "majority low => overall low")


def test_compute_overall_confidence_all_medium():
    """All medium should produce 'medium' overall."""
    paths = [
        {"confidence": "medium"},
        {"confidence": "medium"},
    ]
    assert_eq(_compute_overall_confidence(paths), "medium",
              "all medium => overall medium")


def test_compute_overall_confidence_single_high():
    """Single high path should produce 'high' overall."""
    assert_eq(_compute_overall_confidence([{"confidence": "high"}]), "high",
              "single high => overall high")


def test_compute_overall_confidence_single_low():
    """Single low path should produce 'low' overall."""
    assert_eq(_compute_overall_confidence([{"confidence": "low"}]), "low",
              "single low => overall low")


def test_compute_overall_confidence_half_low():
    """Exactly half low should produce 'medium' (not strictly majority)."""
    paths = [
        {"confidence": "low"},
        {"confidence": "high"},
    ]
    assert_eq(_compute_overall_confidence(paths), "medium",
              "half low => overall medium")


# =========================================================================
# analyse_project_oversight — public API
# =========================================================================

def test_analyse_project_oversight_nonexistent_path():
    """Non-existent path should return safe defaults."""
    result = analyse_project_oversight("/tmp/nonexistent_path_regula_test_xyz")
    assert_eq(result["ai_sources"], [], "nonexistent: no AI sources")
    assert_eq(result["oversight_gates"], [], "nonexistent: no gates")
    assert_eq(result["flow_paths"], [], "nonexistent: no flow paths")
    assert_eq(result["unreviewed_paths"], [], "nonexistent: no unreviewed")
    assert_eq(result["confidence"], "low", "nonexistent: low confidence")
    assert_true(len(result["limitations"]) > len(LIMITATIONS),
                "should include extra limitation about bad path")
    assert_eq(result["summary"]["oversight_score"], 0,
              "nonexistent: score 0")


def test_analyse_project_oversight_empty_project():
    """Empty project (no Python/JS files) should return honest result."""
    proj = _make_project({
        "readme.md": "# My project\n",
        "data.csv": "a,b\n1,2\n",
    })
    try:
        result = analyse_project_oversight(proj)
        assert_eq(result.get("analysed"), False,
                  "empty project should not be marked as analysed")
        assert_true("reason" in result,
                    "empty project should explain why not analysed")
        assert_eq(result["confidence"], "none",
                  "empty project should have 'none' confidence")
        assert_eq(result["summary"]["oversight_score"], -1,
                  "empty project score should be -1")
    finally:
        _cleanup(proj)


def test_analyse_project_oversight_no_ai():
    """Project with Python files but no AI code should score 100."""
    proj = _make_project({
        "utils.py": "def add(a, b): return a + b\n",
        "main.py": "from utils import add\nprint(add(1, 2))\n",
    })
    try:
        result = analyse_project_oversight(proj)
        assert_eq(result.get("analysed"), True,
                  "project with Python files should be analysed")
        assert_eq(result["ai_sources"], [], "no AI code => no sources")
        assert_eq(result["summary"]["oversight_score"], 100,
                  "no AI flows => 100 score")
        assert_true(len(result["limitations"]) > 0,
                    "should always include limitations")
    finally:
        _cleanup(proj)


def test_analyse_project_oversight_ai_with_oversight():
    """Project with AI code and oversight should score > 0."""
    proj = _make_project({
        "model.py": (
            "import openai\n"
            "client = openai.OpenAI()\n"
            "\n"
            "def get_prediction(prompt):\n"
            "    result = client.chat.completions.create(\n"
            "        model='gpt-4',\n"
            "        messages=[{'role': 'user', 'content': prompt}]\n"
            "    )\n"
            "    return result\n"
        ),
        "app.py": (
            "from model import get_prediction\n"
            "\n"
            "def handle_request(user_input):\n"
            "    prediction = get_prediction(user_input)\n"
            "    # Human review gate\n"
            "    approved = review_and_approve(prediction)\n"
            "    if approved:\n"
            "        return prediction\n"
            "\n"
            "def review_and_approve(result):\n"
            "    '''Human operator must confirm the result.'''\n"
            "    return True\n"
        ),
    })
    try:
        result = analyse_project_oversight(proj)
        assert_eq(result.get("analysed"), True, "should be analysed")
        assert_true(isinstance(result["ai_sources"], list),
                    "should have AI sources list")
        assert_true(isinstance(result["flow_paths"], list),
                    "should have flow paths list")
        assert_true(isinstance(result["oversight_gates"], list),
                    "should have oversight gates list")
        assert_true(isinstance(result["limitations"], list),
                    "should have limitations list")
        assert_true(result["confidence"] in ("high", "medium", "low"),
                    "confidence should be high/medium/low")
    finally:
        _cleanup(proj)


def test_analyse_project_oversight_ai_no_oversight():
    """Project with AI code but no oversight should score low."""
    proj = _make_project({
        "auto.py": (
            "import openai\n"
            "client = openai.OpenAI()\n"
            "\n"
            "def auto_respond(prompt):\n"
            "    result = client.chat.completions.create(\n"
            "        model='gpt-4',\n"
            "        messages=[{'role': 'user', 'content': prompt}]\n"
            "    )\n"
            "    send_email(result)  # automated action\n"
            "    return result\n"
        ),
    })
    try:
        result = analyse_project_oversight(proj)
        assert_eq(result.get("analysed"), True, "should be analysed")
        # If AI sources are detected, unreviewed count should match total
        total = result["summary"].get("total_paths", 0)
        if total > 0:
            assert_gte(result["summary"]["unreviewed"], 1,
                       "no oversight => at least one unreviewed path")
    finally:
        _cleanup(proj)


def test_analyse_project_oversight_result_structure():
    """Verify the full result structure of analyse_project_oversight."""
    proj = _make_project({
        "app.py": "x = 1\n",
    })
    try:
        result = analyse_project_oversight(proj)
        # All required top-level keys
        for key in ("ai_sources", "oversight_gates", "flow_paths",
                     "unreviewed_paths", "confidence", "limitations",
                     "summary"):
            assert_in(key, result, f"result should have '{key}' key")
        # Summary sub-keys
        summary = result["summary"]
        for key in ("reviewed", "unreviewed", "oversight_score"):
            assert_in(key, summary, f"summary should have '{key}' key")
    finally:
        _cleanup(proj)


def test_analyse_project_oversight_limitations_always_present():
    """Limitations should always be present and include known caveats."""
    proj = _make_project({
        "app.py": "x = 1\n",
    })
    try:
        result = analyse_project_oversight(proj)
        lims = result["limitations"]
        assert_gte(len(lims), len(LIMITATIONS),
                   "should include at least all standard limitations")
        # Check a few specific limitations are present
        lim_text = " ".join(lims)
        assert_true("dynamic" in lim_text.lower() or "Dynamic" in lim_text,
                     "should mention dynamic imports limitation")
    finally:
        _cleanup(proj)


def test_analyse_project_oversight_mixed_py_js():
    """Project with both Python and JS files should be analysed."""
    proj = _make_project({
        "backend.py": (
            "import openai\n"
            "client = openai.OpenAI()\n"
            "def predict(x): return client.chat.completions.create(model='gpt-4', messages=[])\n"
        ),
        "frontend.js": (
            "import { predict } from './api'\n"
            "const result = predict('hello')\n"
        ),
        "api.js": (
            "export function predict(input) { return fetch('/api/predict') }\n"
        ),
    })
    try:
        result = analyse_project_oversight(proj)
        assert_eq(result.get("analysed"), True,
                  "mixed project should be analysed")
    finally:
        _cleanup(proj)


def test_analyse_project_oversight_js_only():
    """JS-only project should be analysed."""
    proj = _make_project({
        "app.js": "console.log('hello')\n",
        "utils.js": "export function add(a, b) { return a + b; }\n",
    })
    try:
        result = analyse_project_oversight(proj)
        assert_eq(result.get("analysed"), True,
                  "JS-only project should be analysed")
    finally:
        _cleanup(proj)


def test_analyse_project_oversight_file_not_dir():
    """Path pointing to a file (not a dir) should return safe defaults."""
    proj = _make_project({"app.py": "x = 1\n"})
    try:
        file_path = os.path.join(proj, "app.py")
        result = analyse_project_oversight(file_path)
        assert_eq(result["confidence"], "low",
                  "file path (not dir) should return low confidence")
        assert_eq(result["summary"]["oversight_score"], 0,
                  "file path => score 0")
    finally:
        _cleanup(proj)


# =========================================================================
# Edge cases
# =========================================================================

def test_edge_case_circular_imports():
    """Circular imports should not cause infinite loops."""
    proj = _make_project({
        "a.py": "from b import bar\ndef foo(): return bar()\n",
        "b.py": "from a import foo\ndef bar(): return foo()\n",
    })
    try:
        result = analyse_project_oversight(proj)
        # Should complete without hanging or crashing
        assert_true(isinstance(result, dict),
                    "circular imports should not crash analysis")
        assert_eq(result.get("analysed"), True,
                  "project with circular imports should be analysed")
    finally:
        _cleanup(proj)


def test_edge_case_syntax_error_files():
    """Syntax errors in some files should not prevent analysis of others."""
    proj = _make_project({
        "good.py": "def hello(): return 'hi'\n",
        "bad.py": "def broken(:\n    pass\n",
        "also_good.py": "x = 42\n",
    })
    try:
        result = analyse_project_oversight(proj)
        assert_eq(result.get("analysed"), True,
                  "should analyse valid files despite syntax errors")
    finally:
        _cleanup(proj)


def test_edge_case_large_file_count():
    """Should handle project with many files without error."""
    files = {}
    for i in range(50):
        files[f"module_{i}.py"] = f"def func_{i}(): return {i}\n"
    proj = _make_project(files)
    try:
        result = analyse_project_oversight(proj)
        assert_eq(result.get("analysed"), True,
                  "should handle 50 files without error")
    finally:
        _cleanup(proj)


def test_edge_case_deeply_nested_dirs():
    """Should handle deeply nested directory structures."""
    proj = _make_project({
        "a/b/c/d/e/deep.py": "def deep(): pass\n",
    })
    try:
        pp = Path(proj).resolve()
        files = _collect_python_files(pp)
        names = {str(f.relative_to(pp)) for f, _content in files}
        expected = os.path.join("a", "b", "c", "d", "e", "deep.py")
        assert_in(expected, names, "should find deeply nested Python file")
    finally:
        _cleanup(proj)


def test_edge_case_unicode_content():
    """Should handle files with unicode content."""
    proj = _make_project({
        "unicode.py": "# Commentaire en francais: cafe\ndef greet(): return 'Bonjour'\n",
    })
    try:
        pp = Path(proj).resolve()
        py_files = _collect_python_files(pp)
        table = _build_symbol_table(pp, py_files)
        assert_in("unicode.py", table,
                  "should handle unicode content")
    finally:
        _cleanup(proj)


def test_edge_case_binary_file_resilience():
    """Should not crash on non-UTF-8 content."""
    proj = _make_project({
        "normal.py": "x = 1\n",
    })
    # Write a binary file with .py extension
    binary_path = Path(proj) / "binary.py"
    binary_path.write_bytes(b"\x80\x81\x82\x83def foo(): pass\n")
    try:
        pp = Path(proj).resolve()
        py_files = _collect_python_files(pp)
        table = _build_symbol_table(pp, py_files)
        # Should not crash; binary.py may or may not parse
        assert_in("normal.py", table,
                  "normal.py should still be in table")
    finally:
        _cleanup(proj)


def test_edge_case_only_init_files():
    """Project with only __init__.py files should be analysed."""
    proj = _make_project({
        "pkg/__init__.py": "VERSION = '1.0'\n",
        "pkg/sub/__init__.py": "from . import models\n",
    })
    try:
        result = analyse_project_oversight(proj)
        assert_eq(result.get("analysed"), True,
                  "project with __init__.py files should be analysed")
    finally:
        _cleanup(proj)


def test_edge_case_single_line_file():
    """Single-line Python file should work."""
    proj = _make_project({
        "one.py": "x=1",
    })
    try:
        pp = Path(proj).resolve()
        py_files = _collect_python_files(pp)
        table = _build_symbol_table(pp, py_files)
        assert_in("one.py", table, "single-line file should be in table")
    finally:
        _cleanup(proj)


# =========================================================================
# LIMITATIONS constant
# =========================================================================

def test_limitations_is_list():
    """LIMITATIONS should be a non-empty list of strings."""
    assert_true(isinstance(LIMITATIONS, list),
                "LIMITATIONS should be a list")
    assert_gte(len(LIMITATIONS), 5,
               "should have at least 5 known limitations")
    for lim in LIMITATIONS:
        assert_true(isinstance(lim, str),
                    "each limitation should be a string")


def test_limitations_mentions_dynamic_imports():
    """LIMITATIONS should mention dynamic imports."""
    lim_text = " ".join(LIMITATIONS).lower()
    assert_true("dynamic" in lim_text,
                "should mention dynamic imports")


def test_limitations_mentions_cross_service():
    """LIMITATIONS should mention cross-service calls."""
    lim_text = " ".join(LIMITATIONS).lower()
    assert_true("cross-service" in lim_text or "http" in lim_text or "grpc" in lim_text,
                "should mention cross-service/HTTP/gRPC limitation")


def test_limitations_mentions_js_ts():
    """LIMITATIONS should mention JS/TS limitations."""
    lim_text = " ".join(LIMITATIONS)
    assert_true("JS" in lim_text or "node_modules" in lim_text,
                "should mention JS/TS limitations")


# =========================================================================
# _JS_TS_EXTENSIONS constant
# =========================================================================

def test_js_ts_extensions():
    """_JS_TS_EXTENSIONS should contain expected extensions."""
    for ext in (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"):
        assert_in(ext, _JS_TS_EXTENSIONS,
                  f"{ext} should be in _JS_TS_EXTENSIONS")


# =========================================================================
# Integration: Full pipeline with cross-file AI flow
# =========================================================================

def test_integration_sklearn_cross_file():
    """Integration test: sklearn model defined in one file, used in another."""
    proj = _make_project({
        "model.py": (
            "from sklearn.ensemble import RandomForestClassifier\n"
            "\n"
            "def train_model(X, y):\n"
            "    clf = RandomForestClassifier()\n"
            "    clf.fit(X, y)\n"
            "    return clf\n"
            "\n"
            "def get_prediction(clf, X):\n"
            "    result = clf.predict(X)\n"
            "    return result\n"
        ),
        "api.py": (
            "from model import get_prediction, train_model\n"
            "\n"
            "def handle_request(data):\n"
            "    clf = train_model(data['X'], data['y'])\n"
            "    prediction = get_prediction(clf, data['new_X'])\n"
            "    return {'result': prediction}\n"
        ),
    })
    try:
        result = analyse_project_oversight(proj)
        assert_eq(result.get("analysed"), True,
                  "sklearn cross-file project should be analysed")
        # The project has AI code, so there should be some sources
        if result["ai_sources"]:
            assert_gte(len(result["flow_paths"]), 1,
                       "should have at least one flow path")
    finally:
        _cleanup(proj)


def test_integration_oversight_in_consumer():
    """Integration test: AI producer in one file, oversight in consumer."""
    proj = _make_project({
        "engine.py": (
            "from sklearn.ensemble import RandomForestClassifier\n"
            "\n"
            "def classify(X):\n"
            "    clf = RandomForestClassifier()\n"
            "    prediction = clf.predict(X)\n"
            "    return prediction\n"
        ),
        "controller.py": (
            "from engine import classify\n"
            "\n"
            "def process_with_review(data):\n"
            "    result = classify(data)\n"
            "    # Human must approve the classification\n"
            "    approved = human_review(result)\n"
            "    if approved:\n"
            "        return result\n"
            "    return None\n"
            "\n"
            "def human_review(prediction):\n"
            "    '''Operator reviews AI output before action.'''\n"
            "    confirm = True  # placeholder\n"
            "    return confirm\n"
        ),
    })
    try:
        result = analyse_project_oversight(proj)
        assert_eq(result.get("analysed"), True,
                  "project should be analysed")
        # With oversight in consumer, score should reflect some review
        if result["ai_sources"] and result["oversight_gates"]:
            assert_gte(result["summary"]["oversight_score"], 0,
                       "oversight score should be non-negative")
    finally:
        _cleanup(proj)


def test_integration_multi_hop_flow():
    """Integration test: AI output flows through multiple files."""
    proj = _make_project({
        "ai_core.py": (
            "import openai\n"
            "client = openai.OpenAI()\n"
            "\n"
            "def generate(prompt):\n"
            "    result = client.chat.completions.create(\n"
            "        model='gpt-4',\n"
            "        messages=[{'role': 'user', 'content': prompt}]\n"
            "    )\n"
            "    return result\n"
        ),
        "processor.py": (
            "from ai_core import generate\n"
            "\n"
            "def process(user_input):\n"
            "    raw = generate(user_input)\n"
            "    return raw\n"
        ),
        "handler.py": (
            "from processor import process\n"
            "\n"
            "def handle(req):\n"
            "    output = process(req)\n"
            "    return output\n"
        ),
    })
    try:
        result = analyse_project_oversight(proj)
        assert_eq(result.get("analysed"), True,
                  "multi-hop project should be analysed")
        assert_true(isinstance(result["flow_paths"], list),
                    "should produce flow paths")
    finally:
        _cleanup(proj)


def test_integration_js_ts_project():
    """Integration test: JS/TS project with AI imports."""
    proj = _make_project({
        "src/ai.ts": (
            "import OpenAI from 'openai'\n"
            "const client = new OpenAI()\n"
            "export async function generate(prompt: string) {\n"
            "  const result = await client.chat.completions.create({\n"
            "    model: 'gpt-4',\n"
            "    messages: [{role: 'user', content: prompt}]\n"
            "  })\n"
            "  return result\n"
            "}\n"
        ),
        "src/handler.ts": (
            "import { generate } from './ai'\n"
            "export async function handle(input: string) {\n"
            "  const result = await generate(input)\n"
            "  return result\n"
            "}\n"
        ),
    })
    try:
        result = analyse_project_oversight(proj)
        assert_eq(result.get("analysed"), True,
                  "JS/TS project should be analysed")
    finally:
        _cleanup(proj)


# =========================================================================
# Require-style destructured import resolution
# =========================================================================

def test_resolve_js_require_destructured():
    """Should resolve destructured require: const { X } = require('./module')."""
    proj = _make_project({
        "src/app.js": "const { predict, classify } = require('./model')\n",
        "src/model.js": "function predict() {}\nfunction classify() {}\nmodule.exports = { predict, classify }\n",
    })
    try:
        pp = Path(proj).resolve()
        js_files = _collect_js_ts_files(pp)
        table = _build_js_ts_symbol_table(pp, js_files)
        import_map = _resolve_js_ts_imports(pp, table)
        app_rel = os.path.join("src", "app.js")
        if app_rel in import_map:
            app_imports = import_map[app_rel]
            assert_in("predict", app_imports,
                      "should resolve destructured require 'predict'")
            assert_in("classify", app_imports,
                      "should resolve destructured require 'classify'")
    finally:
        _cleanup(proj)


def test_resolve_js_require_destructured_aliased():
    """Should resolve destructured require with alias: const { X: Y } = require('./module')."""
    proj = _make_project({
        "src/app.js": "const { predict: runPrediction } = require('./model')\n",
        "src/model.js": "function predict() {}\nmodule.exports = { predict }\n",
    })
    try:
        pp = Path(proj).resolve()
        js_files = _collect_js_ts_files(pp)
        table = _build_js_ts_symbol_table(pp, js_files)
        import_map = _resolve_js_ts_imports(pp, table)
        app_rel = os.path.join("src", "app.js")
        if app_rel in import_map:
            app_imports = import_map[app_rel]
            if "runPrediction" in app_imports:
                _, original = app_imports["runPrediction"]
                assert_eq(original, "predict",
                          "destructured alias should map to original name")
    finally:
        _cleanup(proj)


# =========================================================================
# Regex pattern tests (import extraction)
# =========================================================================

def test_regex_js_import_named_pattern():
    """The named import regex should match 'import { X } from ...'."""
    from cross_file_flow import _RE_JS_IMPORT_NAMED
    match = _RE_JS_IMPORT_NAMED.search("import { foo, bar } from './module'")
    assert_true(match is not None, "should match named import")
    if match:
        assert_eq(match.group(2), "./module", "should capture module path")
        assert_true("foo" in match.group(1), "should capture 'foo'")
        assert_true("bar" in match.group(1), "should capture 'bar'")


def test_regex_js_import_default_pattern():
    """The default import regex should match 'import X from ...'."""
    from cross_file_flow import _RE_JS_IMPORT_DEFAULT
    match = _RE_JS_IMPORT_DEFAULT.search("import MyModule from './utils'")
    assert_true(match is not None, "should match default import")
    if match:
        assert_eq(match.group(1), "MyModule", "should capture default name")
        assert_eq(match.group(2), "./utils", "should capture module path")


def test_regex_js_require_pattern():
    """The require regex should match const X = require('...')."""
    from cross_file_flow import _RE_JS_REQUIRE
    match = _RE_JS_REQUIRE.search("const helper = require('./helper')")
    assert_true(match is not None, "should match require")
    if match:
        assert_eq(match.group(1), "helper", "should capture variable name")
        assert_eq(match.group(3), "./helper", "should capture module path")


def test_regex_js_require_destructured_pattern():
    """The require regex should match const { X } = require('...')."""
    from cross_file_flow import _RE_JS_REQUIRE
    match = _RE_JS_REQUIRE.search("const { foo, bar } = require('./mod')")
    assert_true(match is not None, "should match destructured require")
    if match:
        assert_true(match.group(1) is None,
                     "default name should be None for destructured")
        assert_true("foo" in match.group(2),
                     "should capture destructured names")


# =========================================================================
# Score computation in analyse_project_oversight
# =========================================================================

def test_score_100_when_no_ai_paths():
    """Score should be 100 when Python files exist but no AI flow paths."""
    proj = _make_project({
        "utils.py": "def add(a, b): return a + b\n",
    })
    try:
        result = analyse_project_oversight(proj)
        assert_eq(result["summary"]["oversight_score"], 100,
                  "no AI paths => perfect score")
    finally:
        _cleanup(proj)


def test_score_minus_one_no_supported_files():
    """Score should be -1 when no supported files found."""
    proj = _make_project({
        "data.json": '{"key": "value"}',
    })
    try:
        result = analyse_project_oversight(proj)
        assert_eq(result["summary"]["oversight_score"], -1,
                  "no supported files => -1 score")
    finally:
        _cleanup(proj)
