#!/usr/bin/env python3
# regula-ignore
"""
Cross-File AI Data Flow Analysis for Article 14 Human Oversight Detection.

Builds on ast_analysis.py's single-file analysis to trace AI model outputs
across module boundaries and determine whether human oversight gates exist
on each path from AI source to user-facing sink.

Supports Python and JavaScript/TypeScript projects.

Zero external dependencies — stdlib ast module only (JS/TS uses ast_engine).
"""

import ast
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).parent))

from ast_analysis import (
    trace_ai_data_flow,
    detect_human_oversight,
    parse_python_file,
    AI_LIBRARIES,
    HUMAN_OVERSIGHT_KEYWORDS,
)
from ast_engine import analyse_file as ast_engine_analyse_file
from constants import SKIP_DIRS

# JS/TS file extensions recognised for cross-file flow analysis
_JS_TS_EXTENSIONS = frozenset((".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"))

# -------------------------------------------------------------------------
# Mandatory limitations — always included in output
# -------------------------------------------------------------------------

LIMITATIONS = [
    "Dynamic imports (importlib, __import__) not analysed",
    "Decorator-wrapped routes not resolved",
    "Third-party library internals not traced",
    "Cross-service calls (HTTP/gRPC) not detected",
    "This detects code paths for oversight, not whether oversight is meaningfully exercised (ICO standard)",
    "JS/TS: node_modules imports not resolved (project-internal only)",
    "JS/TS: re-exports and barrel files partially supported",
]


# =========================================================================
# Phase 1 — Project-wide symbol table
# =========================================================================

def _should_skip(path: Path) -> bool:
    """Check if any path component is in SKIP_DIRS."""
    for part in path.parts:
        if part in SKIP_DIRS:
            return True
    return False


def _collect_python_files(project_path: Path) -> List[Path]:
    """Walk project and return all .py files, respecting SKIP_DIRS."""
    files = []
    for root, dirs, filenames in os.walk(project_path):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(".py"):
                fp = root_path / fn
                if not _should_skip(fp.relative_to(project_path)):
                    files.append(fp)
    return files


def _collect_js_ts_files(project_path: Path) -> List[Path]:
    """Walk project and return all JS/TS files, respecting SKIP_DIRS."""
    files = []
    for root, dirs, filenames in os.walk(project_path):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in filenames:
            ext = os.path.splitext(fn)[1]
            if ext in _JS_TS_EXTENSIONS:
                fp = root_path / fn
                if not _should_skip(fp.relative_to(project_path)):
                    files.append(fp)
    return files


def _build_symbol_table(
    project_path: Path, py_files: List[Path]
) -> Dict[str, Dict]:
    """Build a project-wide symbol table from Python files.

    Returns: {relative_path: {"functions": {name: line}, "classes": {name: line}, "content": str}}
    """
    table: Dict[str, Dict] = {}
    for fp in py_files:
        try:
            content = fp.read_text(encoding="utf-8", errors="replace")
        except (OSError, PermissionError):
            continue
        try:
            tree = ast.parse(content, filename=str(fp))
        except SyntaxError:
            continue

        rel = str(fp.relative_to(project_path))
        funcs: Dict[str, int] = {}
        classes: Dict[str, int] = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                funcs[node.name] = node.lineno
            elif isinstance(node, ast.ClassDef):
                classes[node.name] = node.lineno
        table[rel] = {
            "functions": funcs,
            "classes": classes,
            "content": content,
            "lang": "python",
        }
    return table


def _build_js_ts_symbol_table(
    project_path: Path, js_files: List[Path]
) -> Dict[str, Dict]:
    """Build a project-wide symbol table from JS/TS files using ast_engine.

    Returns same shape as _build_symbol_table so both can be merged.
    """
    table: Dict[str, Dict] = {}
    for fp in js_files:
        try:
            content = fp.read_text(encoding="utf-8", errors="replace")
        except (OSError, PermissionError):
            continue

        rel = str(fp.relative_to(project_path))
        analysis = ast_engine_analyse_file(content, fp.name)

        funcs: Dict[str, int] = {}
        for fdef in analysis.get("function_defs", []):
            name = fdef.get("name", "")
            if name:
                # ast_engine doesn't always give line numbers for functions;
                # use 0 as fallback
                funcs[name] = fdef.get("line", 0)

        classes: Dict[str, int] = {}
        for cdef in analysis.get("class_defs", []):
            name = cdef.get("name", "")
            if name:
                classes[name] = cdef.get("line", 0)

        table[rel] = {
            "functions": funcs,
            "classes": classes,
            "content": content,
            "lang": "javascript",
            "_analysis": analysis,  # cached ast_engine result
        }
    return table


# =========================================================================
# Phase 2 — Import resolution (project-internal only)
# =========================================================================

def _module_to_candidates(module_name: str, project_path: Path) -> List[str]:
    """Convert a dotted module name to candidate relative file paths."""
    parts = module_name.replace(".", os.sep)
    return [
        parts + ".py",
        os.path.join(parts, "__init__.py"),
    ]


def _js_import_to_candidates(import_path: str, importing_file_rel: str) -> List[str]:
    """Convert a JS/TS relative import to candidate relative file paths.

    Only handles project-internal imports (starting with './' or '../').
    Returns empty list for bare specifiers (node_modules).
    """
    if not import_path.startswith("."):
        return []

    # Resolve relative to the importing file's directory
    importing_dir = str(Path(importing_file_rel).parent)
    resolved = os.path.normpath(os.path.join(importing_dir, import_path))

    # Normalise path separators
    resolved = resolved.replace("\\", "/")

    # If it already has an extension that we recognise, just return it
    ext = os.path.splitext(resolved)[1]
    if ext in _JS_TS_EXTENSIONS:
        return [resolved]

    # Otherwise, try common extension resolutions
    candidates = []
    for e in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"):
        candidates.append(resolved + e)
    # index file in directory
    for e in (".ts", ".tsx", ".js", ".jsx"):
        candidates.append(os.path.join(resolved, "index" + e))
    return candidates


def _resolve_imports(
    project_path: Path,
    symbol_table: Dict[str, Dict],
) -> Dict[str, Dict[str, Tuple[str, str]]]:
    """For each file, resolve project-internal imports.

    Returns: {file_rel: {imported_name: (source_file_rel, original_name)}}
    """
    known_files = set(symbol_table.keys())
    result: Dict[str, Dict[str, Tuple[str, str]]] = {}

    for rel, info in symbol_table.items():
        content = info["content"]
        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue  # unparseable; skip import analysis

        mapping: Dict[str, Tuple[str, str]] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    local = alias.asname or alias.name
                    for cand in _module_to_candidates(alias.name, project_path):
                        if cand in known_files:
                            mapping[local] = (cand, alias.name)
                            break
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                # Resolve relative imports (from . import X, from ..utils import Y)
                level = getattr(node, "level", 0) or 0
                if level > 0:
                    current_parts = list(Path(rel).parent.parts)
                    base_parts = current_parts[:max(0, len(current_parts) - (level - 1))]
                    if module:
                        module = str(Path(*base_parts, *module.split("."))) if base_parts else module
                    elif base_parts:
                        module = str(Path(*base_parts))
                for alias in node.names:
                    local = alias.asname or alias.name
                    original = alias.name
                    # Try resolving the module, then look for the name in it
                    for cand in _module_to_candidates(module, project_path):
                        if cand in known_files:
                            mapping[local] = (cand, original)
                            break

        result[rel] = mapping
    return result


# Regex patterns for extracting JS/TS import specifiers
_RE_JS_IMPORT_FROM = re.compile(
    r"""import\s+(?:"""
    r"""(?:\{[^}]*\}|\*\s+as\s+\w+|\w+)"""
    r"""(?:\s*,\s*(?:\{[^}]*\}|\*\s+as\s+\w+))?"""
    r"""\s+from\s+)?"""
    r"""['"]([^'"]+)['"]""",
    re.MULTILINE,
)
_RE_JS_REQUIRE = re.compile(
    r"""(?:const|let|var)\s+(?:(\w+)|\{([^}]+)\})\s*=\s*require\s*\(\s*['"]([^'"]+)['"]\s*\)""",
    re.MULTILINE,
)
_RE_JS_IMPORT_NAMED = re.compile(
    r"""import\s+\{([^}]+)\}\s+from\s+['"]([^'"]+)['"]""",
    re.MULTILINE,
)
_RE_JS_IMPORT_DEFAULT = re.compile(
    r"""import\s+(\w+)\s+from\s+['"]([^'"]+)['"]""",
    re.MULTILINE,
)


def _resolve_js_ts_imports(
    project_path: Path,
    symbol_table: Dict[str, Dict],
) -> Dict[str, Dict[str, Tuple[str, str]]]:
    """For each JS/TS file, resolve project-internal imports.

    Returns: {file_rel: {imported_name: (source_file_rel, original_name)}}
    """
    known_files = set(symbol_table.keys())
    result: Dict[str, Dict[str, Tuple[str, str]]] = {}

    for rel, info in symbol_table.items():
        if info.get("lang") != "javascript":
            continue

        content = info["content"]
        mapping: Dict[str, Tuple[str, str]] = {}

        # Handle: import { X, Y as Z } from './module'
        for match in _RE_JS_IMPORT_NAMED.finditer(content):
            names_str = match.group(1)
            module_path = match.group(2)
            candidates = _js_import_to_candidates(module_path, rel)
            target = None
            for cand in candidates:
                if cand in known_files:
                    target = cand
                    break
            if target:
                for part in names_str.split(","):
                    part = part.strip()
                    if not part:
                        continue
                    if " as " in part:
                        original, _, local = part.partition(" as ")
                        mapping[local.strip()] = (target, original.strip())
                    else:
                        mapping[part] = (target, part)

        # Handle: import X from './module'
        for match in _RE_JS_IMPORT_DEFAULT.finditer(content):
            local_name = match.group(1)
            module_path = match.group(2)
            # Skip if already captured as named import
            if local_name in mapping:
                continue
            candidates = _js_import_to_candidates(module_path, rel)
            for cand in candidates:
                if cand in known_files:
                    mapping[local_name] = (cand, "default")
                    break

        # Handle: const X = require('./module')
        for match in _RE_JS_REQUIRE.finditer(content):
            default_name = match.group(1)
            destructured = match.group(2)
            module_path = match.group(3)
            candidates = _js_import_to_candidates(module_path, rel)
            target = None
            for cand in candidates:
                if cand in known_files:
                    target = cand
                    break
            if target:
                if default_name:
                    mapping[default_name] = (target, "default")
                elif destructured:
                    for part in destructured.split(","):
                        part = part.strip()
                        if not part:
                            continue
                        if ":" in part:
                            original, _, local = part.partition(":")
                            mapping[local.strip()] = (target, original.strip())
                        else:
                            mapping[part] = (target, part)

        result[rel] = mapping
    return result


# =========================================================================
# Phase 3 — AI source identification
# =========================================================================

def _find_ai_sources(
    symbol_table: Dict[str, Dict],
) -> List[Dict]:
    """Run trace_ai_data_flow on each file, collect AI output call sites.

    For Python files, uses ast_analysis.trace_ai_data_flow.
    For JS/TS files, uses cached ast_engine analysis data_flows.
    """
    sources = []
    for rel, info in symbol_table.items():
        lang = info.get("lang", "python")
        if lang == "python":
            flows = trace_ai_data_flow(info["content"])
            for flow in flows:
                sources.append({
                    "file": rel,
                    "source": flow["source"],
                    "source_line": flow["source_line"],
                    "destinations": flow["destinations"],
                })
        elif lang == "javascript":
            analysis = info.get("_analysis", {})
            for flow in analysis.get("data_flows", []):
                sources.append({
                    "file": rel,
                    "source": flow.get("source", ""),
                    "source_line": flow.get("source_line", 0),
                    "destinations": flow.get("destinations", []),
                })
    return sources


# =========================================================================
# Phase 4 — Cross-file flow tracing
# =========================================================================

def _find_oversight_gates(
    symbol_table: Dict[str, Dict],
) -> List[Dict]:
    """Run detect_human_oversight on each file, collect oversight patterns.

    For Python files, uses ast_analysis.detect_human_oversight.
    For JS/TS files, uses cached ast_engine analysis oversight data.
    """
    gates = []
    for rel, info in symbol_table.items():
        lang = info.get("lang", "python")
        if lang == "python":
            result = detect_human_oversight(info["content"])
            for pattern in result.get("oversight_patterns", []):
                gates.append({
                    "file": rel,
                    "name": pattern.get("name", ""),
                    "line": pattern.get("line", 0),
                    "type": pattern.get("type", ""),
                    "detail": pattern.get("detail", ""),
                })
        elif lang == "javascript":
            analysis = info.get("_analysis", {})
            oversight = analysis.get("oversight", {})
            for pattern in oversight.get("oversight_patterns", []):
                gates.append({
                    "file": rel,
                    "name": pattern.get("name", pattern.get("keyword", "")),
                    "line": pattern.get("line", 0),
                    "type": pattern.get("type", "keyword"),
                    "detail": pattern.get("detail", pattern.get("keyword", "")),
                })
    return gates


def _trace_cross_file_paths(
    ai_sources: List[Dict],
    oversight_gates: List[Dict],
    import_map: Dict[str, Dict[str, Tuple[str, str]]],
    symbol_table: Dict[str, Dict],
) -> Tuple[List[Dict], List[Dict]]:
    """Trace paths from AI sources through cross-file calls.

    Returns (flow_paths, unreviewed_paths).
    Each path dict has: source_file, source_line, source_expr, hops, has_oversight, confidence.
    """
    # Build a lookup: (file, func_name) -> bool (is oversight gate)
    gate_lookup: Set[Tuple[str, str]] = set()
    for gate in oversight_gates:
        gate_lookup.add((gate["file"], gate["name"]))

    # Build per-file oversight detection cache (boolean, not score)
    oversight_cache: Dict[str, bool] = {}
    for rel, info in symbol_table.items():
        lang = info.get("lang", "python")
        if lang == "python":
            result = detect_human_oversight(info["content"])
            oversight_cache[rel] = result.get("has_oversight", False)
        elif lang == "javascript":
            analysis = info.get("_analysis", {})
            oversight_cache[rel] = analysis.get("oversight", {}).get("has_oversight", False)

    # Build reverse import map: which files import each (file, function)?
    # {(source_file, func_name): [(importing_file, local_name), ...]}
    reverse_imports: Dict[Tuple[str, str], List[Tuple[str, str]]] = {}
    for importing_file, imports in import_map.items():
        for local_name, (source_file, original_name) in imports.items():
            key = (source_file, original_name)
            reverse_imports.setdefault(key, []).append((importing_file, local_name))

    # Identify AI-producing functions: functions in AI source files that
    # contain (directly or transitively) an AI call and return its result
    ai_producing_funcs: Set[Tuple[str, str]] = set()
    for src in ai_sources:
        file_rel = src["file"]
        # Find which function this AI call is in
        file_info = symbol_table.get(file_rel, {})
        funcs = file_info.get("functions", {})
        # Build sorted list of (start_line, name) to determine function ranges
        sorted_funcs = sorted(funcs.items(), key=lambda x: x[1])
        for i, (fname, fline) in enumerate(sorted_funcs):
            # Function range: from its start line to the next function's start line (exclusive), or EOF
            next_fline = sorted_funcs[i + 1][1] if i + 1 < len(sorted_funcs) else float("inf")
            if fline <= src["source_line"] < next_fline:
                ai_producing_funcs.add((file_rel, fname))
                break

    flow_paths = []
    unreviewed_paths = []
    seen_path_keys: Set[Tuple[str, int, str]] = set()  # dedup guard for circular imports

    def _add_path(entry: dict) -> None:
        """Add a flow path, deduplicating by (source_file, source_line, consumer)."""
        key = (entry["source_file"], entry["source_line"],
               entry.get("consumer_file", ""))
        if key in seen_path_keys:
            return
        seen_path_keys.add(key)
        flow_paths.append(entry)
        if not entry["has_oversight"]:
            unreviewed_paths.append(entry)

    for src in ai_sources:
        file_rel = src["file"]
        has_same_file_oversight = False
        same_file_confidence = "high"

        # Check destinations within the same file
        for dest in src["destinations"]:
            if dest["type"] == "human_review":
                has_same_file_oversight = True

        # Check if any destination calls a function in another file
        file_imports = import_map.get(file_rel, {})
        for dest in src["destinations"]:
            detail = dest.get("detail", "")
            for imported_name, (source_file, original_name) in file_imports.items():
                if imported_name in detail:
                    hop_oversight = False
                    hop_confidence = "high"
                    if (source_file, original_name) in gate_lookup:
                        hop_oversight = True
                    elif oversight_cache.get(source_file, False):
                        hop_oversight = True
                        hop_confidence = "medium"
                    path_entry = {
                        "source_file": file_rel,
                        "source_line": src["source_line"],
                        "source_expr": src["source"],
                        "hops": [{"from_file": file_rel, "to_file": source_file,
                                  "function": original_name, "line": dest.get("line", 0)}],
                        "has_oversight": hop_oversight or has_same_file_oversight,
                        "confidence": hop_confidence,
                    }
                    _add_path(path_entry)

        # REVERSE TRACE: create ONE path per consuming file that imports
        # an AI-producing function from this source file.
        found_consumers = False
        for ai_func in ai_producing_funcs:
            if ai_func[0] != file_rel:
                continue
            consumers = reverse_imports.get(ai_func, [])
            for consumer_file, local_name in consumers:
                found_consumers = True
                consumer_oversight = False
                consumer_confidence = "medium"  # cross-file = at best medium

                # Check if the consuming file has oversight patterns
                if oversight_cache.get(consumer_file, False):
                    consumer_oversight = True
                # Check if any named gate is in the consuming file
                for gate_file, gate_name in gate_lookup:
                    if gate_file == consumer_file:
                        consumer_oversight = True

                path_entry = {
                    "source_file": file_rel,
                    "source_line": src["source_line"],
                    "source_expr": src["source"],
                    "consumer_file": consumer_file,
                    "hops": [{"from_file": file_rel, "to_file": consumer_file,
                              "function": local_name, "line": 0}],
                    "has_oversight": consumer_oversight,
                    "confidence": consumer_confidence,
                }
                _add_path(path_entry)

        # If no consumers found and no same-file hops were added, add a single path
        if not found_consumers and not any(p["source_file"] == file_rel and p["source_line"] == src["source_line"] for p in flow_paths):
            confidence = "high"
            for dest in src["destinations"]:
                if dest["type"] in ("variable", "return"):
                    confidence = "medium"
            path_entry = {
                "source_file": file_rel,
                "source_line": src["source_line"],
                "source_expr": src["source"],
                "hops": [],
                "has_oversight": has_same_file_oversight,
                "confidence": confidence,
            }
            _add_path(path_entry)

    return flow_paths, unreviewed_paths


# =========================================================================
# Phase 5 — Verdict generation
# =========================================================================

def _compute_overall_confidence(flow_paths: List[Dict]) -> str:
    """Compute overall confidence from per-path confidence levels."""
    if not flow_paths:
        return "low"
    confidences = [p["confidence"] for p in flow_paths]
    if all(c == "high" for c in confidences):
        return "high"
    low_count = sum(1 for c in confidences if c == "low")
    if low_count > len(confidences) / 2:
        return "low"
    return "medium"


# =========================================================================
# Public API
# =========================================================================

def analyse_project_oversight(project_path: str) -> dict:
    """Cross-file Article 14 human oversight analysis.

    Returns:
        {
            "ai_sources": [...],      # All AI output call sites found
            "oversight_gates": [...],  # All human oversight functions found
            "flow_paths": [...],       # Traced paths from AI output to user-facing sinks
            "unreviewed_paths": [...], # Paths with NO oversight gate
            "confidence": "high"|"medium"|"low",
            "limitations": [...],      # What was NOT analysed
            "summary": {
                "total_ai_sources": int,
                "reviewed": int,
                "unreviewed": int,
                "oversight_score": int,  # 0-100
            }
        }
    """
    pp = Path(project_path).resolve()
    if not pp.is_dir():
        return {
            "ai_sources": [],
            "oversight_gates": [],
            "flow_paths": [],
            "unreviewed_paths": [],
            "confidence": "low",
            "limitations": LIMITATIONS + [f"Path is not a directory: {project_path}"],
            "summary": {
                "total_ai_sources": 0,
                "reviewed": 0,
                "unreviewed": 0,
                "oversight_score": 0,
            },
        }

    # Phase 1: collect source files (Python + JS/TS)
    py_files = _collect_python_files(pp)
    js_ts_files = _collect_js_ts_files(pp)

    # If no supported files found, return honest "not analysed" result
    if not py_files and not js_ts_files:
        return {
            "analysed": False,
            "reason": (
                "No Python or JavaScript/TypeScript files found — "
                "cross-file flow analysis supports Python and JS/TS"
            ),
            "ai_sources": [],
            "oversight_gates": [],
            "flow_paths": [],
            "unreviewed_paths": [],
            "confidence": "none",
            "limitations": list(LIMITATIONS),
            "summary": {
                "total_paths": 0,
                "reviewed": 0,
                "unreviewed": 0,
                "oversight_score": -1,
            },
        }

    # Phase 1 (cont.): build unified symbol table
    symbol_table = _build_symbol_table(pp, py_files)
    js_ts_symbol_table = _build_js_ts_symbol_table(pp, js_ts_files)
    symbol_table.update(js_ts_symbol_table)

    # Phase 2: import resolution (Python + JS/TS)
    import_map = _resolve_imports(pp, symbol_table)
    js_ts_import_map = _resolve_js_ts_imports(pp, symbol_table)
    # Merge JS/TS imports into the unified import map
    for rel, mapping in js_ts_import_map.items():
        if rel in import_map:
            import_map[rel].update(mapping)
        else:
            import_map[rel] = mapping

    # Phase 3: AI source identification
    ai_sources = _find_ai_sources(symbol_table)

    # Phase 4: oversight gates + cross-file tracing
    oversight_gates = _find_oversight_gates(symbol_table)
    flow_paths, unreviewed_paths = _trace_cross_file_paths(
        ai_sources, oversight_gates, import_map, symbol_table,
    )

    # Phase 5: verdict — count by flow paths, not AI sources
    total = len(flow_paths)
    unreviewed_count = len(unreviewed_paths)
    reviewed_count = total - unreviewed_count

    if total == 0:
        # Python files analysed, no AI flow paths — no oversight concern
        score = 100
    else:
        score = round((reviewed_count / total) * 100)

    confidence = _compute_overall_confidence(flow_paths)

    return {
        "analysed": True,
        "ai_sources": [
            {
                "file": s["file"],
                "source": s["source"],
                "source_line": s["source_line"],
            }
            for s in ai_sources
        ],
        "oversight_gates": oversight_gates,
        "flow_paths": flow_paths,
        "unreviewed_paths": unreviewed_paths,
        "confidence": confidence,
        "limitations": list(LIMITATIONS),
        "summary": {
            "total_paths": total,
            "reviewed": reviewed_count,
            "unreviewed": unreviewed_count,
            "oversight_score": score,
        },
    }
