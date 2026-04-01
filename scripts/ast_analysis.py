#!/usr/bin/env python3
# regula-ignore
"""
Regula AST Analysis Engine — Structure-Aware Python Code Analysis

Replaces regex-only detection with actual code understanding using Python's
stdlib `ast` module. Provides import analysis, context classification,
single-file data flow tracing, and EU AI Act compliance checks (Articles 12
and 14) without any external dependencies.

All public functions accept a source string and return structured dicts/lists.
No file I/O is performed inside analysis functions.
"""

import argparse
import ast
import json
import sys
import textwrap
from typing import Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

AI_LIBRARIES: Set[str] = {
    # Deep learning
    "tensorflow", "tf", "keras", "torch", "pytorch", "jax", "flax",
    "paddle", "paddlepaddle", "mxnet", "caffe", "caffe2", "theano",
    "onnx", "onnxruntime",
    # ML / classical
    "sklearn", "scikit-learn", "xgboost", "lightgbm", "catboost",
    "statsmodels", "scipy.stats",
    # NLP
    "transformers", "huggingface_hub", "spacy", "nltk", "gensim",
    "sentence_transformers", "tokenizers", "flair",
    # LLM providers / wrappers
    "openai", "anthropic", "cohere", "google.generativeai",
    "google.cloud.aiplatform", "vertexai", "langchain", "langchain_core",
    "langchain_community", "langchain_openai", "langchain_anthropic",
    "llama_index", "llamaindex", "litellm", "guidance", "autogen",
    "crewai", "haystack",
    # Computer vision
    "cv2", "opencv", "torchvision", "detectron2", "ultralytics",
    "mediapipe", "mmdet", "mmcv",
    # Data / feature engineering (AI-adjacent)
    "pandas", "numpy", "polars", "dask",
    # MLOps
    "mlflow", "wandb", "optuna", "ray", "ray.tune",
    "sagemaker", "bentoml", "kubeflow",
}

# Top-level package names that unambiguously signal AI code even when the
# import is just `import X`.
_AI_TOP_LEVEL: Set[str] = {
    "tensorflow", "keras", "torch", "jax", "sklearn",
    "xgboost", "lightgbm", "catboost", "transformers",
    "openai", "anthropic", "cohere", "langchain", "llama_index",
    "litellm", "spacy", "nltk", "gensim", "cv2",
    "detectron2", "ultralytics", "mediapipe", "mlflow", "wandb",
    "optuna", "sagemaker", "bentoml", "autogen", "crewai", "haystack",
}

# Method names that represent AI operations whose outputs we want to trace.
AI_CALL_PATTERNS: Set[str] = {
    "predict", "fit", "transform", "fit_transform", "fit_predict",
    "predict_proba", "decision_function", "score",
    "invoke", "ainvoke", "run", "arun",
    "generate", "chat", "complete", "embed",
    "create",  # openai-style: client.chat.completions.create(...)
    "call", "__call__",
    "forward", "infer", "classify", "detect",
}

# Words that suggest human-in-the-loop oversight.
HUMAN_OVERSIGHT_KEYWORDS: Set[str] = {
    "review", "approve", "approval", "confirm", "confirmation",
    "verify", "verification", "override", "escalate", "escalation",
    "human", "manual", "operator", "supervisor", "moderator",
    "flag_for_review", "queue_for_review", "send_for_approval",
    "human_in_the_loop", "hitl", "manual_check", "manual_review",
}

LOGGING_CALL_NAMES: Set[str] = {
    "log", "info", "debug", "warning", "error", "critical",
    "exception", "log_event", "log_prediction", "log_input",
    "log_output", "log_decision", "audit", "audit_log",
    "track", "record", "emit",
}


# =========================================================================
# Phase 1 — Import and Function Analysis
# =========================================================================

def _is_ai_import(module_name: str) -> bool:
    """Check whether *module_name* (dotted) belongs to a known AI library."""
    if module_name in AI_LIBRARIES or module_name in _AI_TOP_LEVEL:
        return True
    top = module_name.split(".")[0]
    return top in _AI_TOP_LEVEL or top in AI_LIBRARIES


class _StructureVisitor(ast.NodeVisitor):
    """Collect imports, function definitions and class definitions."""

    def __init__(self) -> None:
        self.imports: List[str] = []
        self.ai_imports: List[str] = []
        self.function_defs: List[Dict] = []
        self.class_defs: List[Dict] = []
        self._class_stack: List[str] = []

    # -- imports ----------------------------------------------------------

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            name = alias.name
            self.imports.append(name)
            if _is_ai_import(name):
                self.ai_imports.append(name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        for alias in node.names:
            full = f"{module}.{alias.name}" if module else alias.name
            self.imports.append(full)
            if _is_ai_import(module) or _is_ai_import(full):
                self.ai_imports.append(full)
        self.generic_visit(node)

    # -- functions --------------------------------------------------------

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._record_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._record_function(node)

    def _record_function(self, node) -> None:
        decorators = []
        for dec in node.decorator_list:
            decorators.append(_unparse_safe(dec))

        args = []
        for arg in node.args.args:
            ann = _unparse_safe(arg.annotation) if arg.annotation else None
            args.append(arg.arg if not ann else f"{arg.arg}: {ann}")

        # Return type annotation
        return_type = _unparse_safe(node.returns) if node.returns else None

        # Docstring extraction
        docstring = None
        if (node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, (ast.Constant, ast.Str))):
            val = node.body[0].value
            raw = val.value if isinstance(val, ast.Constant) else val.s
            if isinstance(raw, str):
                # Take first line only for brevity
                docstring = raw.strip().split("\n")[0]

        in_test_class = any(c.startswith("Test") for c in self._class_stack)
        is_test = node.name.startswith("test_") or in_test_class

        self.function_defs.append({
            "name": node.name,
            "args": args,
            "decorators": decorators,
            "is_test": is_test,
            "line": node.lineno,
            "return_type": return_type,
            "docstring": docstring,
        })
        self.generic_visit(node)

    # -- classes ----------------------------------------------------------

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        bases = [_unparse_safe(b) for b in node.bases]
        methods: List[str] = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(item.name)

        self.class_defs.append({
            "name": node.name,
            "bases": bases,
            "methods": methods,
        })

        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()


def _unparse_safe(node: ast.AST) -> str:
    """Return source text for an AST node, with graceful fallback."""
    try:
        return ast.unparse(node)
    except (ValueError, TypeError):
        return "<unknown>"


def parse_python_file(content: str) -> dict:
    """Parse Python source into structured analysis.

    Returns a dict with keys:
        imports         — list of all imported module/name strings
        ai_imports      — subset that are AI/ML libraries
        function_defs   — list of dicts (name, args, decorators, is_test)
        class_defs      — list of dicts (name, bases, methods)
        is_test_file    — bool, True when the file is predominantly tests
        has_ai_code     — bool, True when real AI imports are present
    """
    try:
        tree = ast.parse(content, mode="exec")
    except SyntaxError:
        return {
            "imports": [],
            "ai_imports": [],
            "function_defs": [],
            "class_defs": [],
            "is_test_file": False,
            "has_ai_code": False,
        }

    visitor = _StructureVisitor()
    visitor.visit(tree)

    # Determine is_test_file: majority of functions are tests, or all
    # top-level classes are test classes.
    total_fns = len(visitor.function_defs)
    test_fns = sum(1 for f in visitor.function_defs if f["is_test"])
    test_classes = sum(1 for c in visitor.class_defs if c["name"].startswith("Test"))

    is_test_file = False
    if total_fns > 0 and test_fns / total_fns > 0.5:
        is_test_file = True
    elif len(visitor.class_defs) > 0 and test_classes == len(visitor.class_defs):
        is_test_file = True

    return {
        "imports": visitor.imports,
        "ai_imports": visitor.ai_imports,
        "function_defs": visitor.function_defs,
        "class_defs": visitor.class_defs,
        "is_test_file": is_test_file,
        "has_ai_code": len(visitor.ai_imports) > 0,
    }


def classify_context(content: str) -> str:
    """Classify the role of a Python source file.

    Returns one of:
        "implementation"  — implements AI functionality
        "test"            — tests AI functionality
        "configuration"   — configures AI systems (settings, config dicts)
        "documentation"   — discusses AI only in comments/docstrings
        "not_python"      — cannot be parsed as Python
    """
    try:
        tree = ast.parse(content, mode="exec")
    except SyntaxError:
        return "not_python"

    analysis = parse_python_file(content)

    # Test file?
    if analysis["is_test_file"]:
        return "test"

    # Has real AI imports → implementation.
    if analysis["has_ai_code"]:
        return "implementation"

    # Configuration heuristic: file is mostly assignments / dicts / dataclass
    # definitions with AI-related string literals, but no AI imports.
    ai_config_keywords = {
        "model", "endpoint", "api_key", "temperature", "max_tokens",
        "prompt", "system_prompt", "deployment", "model_name",
        "model_id", "engine", "provider",
    }
    string_literals = _extract_string_literals(tree)
    assignment_names = _extract_assignment_names(tree)
    config_hits = assignment_names & ai_config_keywords
    if config_hits and not analysis["has_ai_code"]:
        return "configuration"

    # Documentation heuristic: AI keywords appear only in docstrings or
    # comments (comments aren't in the AST, but docstrings are).
    docstrings = _extract_docstrings(tree)
    ai_mention_in_docs = any(
        kw in ds.lower()
        for ds in docstrings
        for kw in ("model", "ai", "machine learning", "neural", "llm", "predict")
    )
    if ai_mention_in_docs and not analysis["has_ai_code"]:
        return "documentation"

    # Default: implementation (even if no AI — the caller should combine
    # this with has_ai_code to decide relevance).
    return "implementation"


def _extract_string_literals(tree: ast.Module) -> List[str]:
    """Return all string literal values in the AST."""
    strings: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            strings.append(node.value)
    return strings


def _extract_assignment_names(tree: ast.Module) -> Set[str]:
    """Return names on the left-hand side of top-level assignments."""
    names: Set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id.lower())
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id.lower())
    return names


def _extract_docstrings(tree: ast.Module) -> List[str]:
    """Return docstrings from module, classes and functions."""
    docstrings: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            ds = ast.get_docstring(node)
            if ds:
                docstrings.append(ds)
    return docstrings


# =========================================================================
# Phase 2 — Single-File Data Flow Tracing
# =========================================================================

class _AICallCollector(ast.NodeVisitor):
    """Find AI-related call expressions and their enclosing context."""

    def __init__(self) -> None:
        self.ai_calls: List[Dict] = []
        self._ai_imports: Set[str] = set()

    def set_ai_imports(self, imports: List[str]) -> None:
        """Provide the AI import names so we can scope call detection."""
        for imp in imports:
            parts = imp.split(".")
            # Register all prefixes: "openai.ChatCompletion" → {"openai", "ChatCompletion"}
            for p in parts:
                self._ai_imports.add(p)

    def visit_Call(self, node: ast.Call) -> None:
        method_name = self._call_method_name(node)
        if method_name and self._is_ai_call(node, method_name):
            self.ai_calls.append({
                "node": node,
                "source": _unparse_safe(node),
                "source_line": node.lineno,
                "method": method_name,
            })
        self.generic_visit(node)

    @staticmethod
    def _call_method_name(node: ast.Call) -> Optional[str]:
        func = node.func
        if isinstance(func, ast.Attribute):
            return func.attr
        if isinstance(func, ast.Name):
            return func.id
        return None

    def _is_ai_call(self, node: ast.Call, method_name: str) -> bool:
        """Determine whether a call is an AI operation worth tracing."""
        if method_name not in AI_CALL_PATTERNS:
            return False
        # Check if the object has an AI-related name in its chain.
        return self._chain_has_ai_name(node.func)

    def _chain_has_ai_name(self, node: ast.AST) -> bool:
        """Walk the attribute chain looking for an AI-related identifier."""
        if isinstance(node, ast.Name):
            return node.id.lower() in self._ai_imports or node.id.lower() in {
                "model", "llm", "client", "chain", "agent", "pipeline",
                "classifier", "predictor", "estimator", "detector",
                "chat", "completion", "embedding",
            }
        if isinstance(node, ast.Attribute):
            if node.attr.lower() in self._ai_imports:
                return True
            return self._chain_has_ai_name(node.value)
        if isinstance(node, ast.Call):
            return self._chain_has_ai_name(node.func)
        return False


class _CallGraphBuilder(ast.NodeVisitor):
    """Build a per-file function call graph and resolve transitive AI returns."""

    def __init__(self, ai_call_lines: Set[int]) -> None:
        self._ai_call_lines = ai_call_lines
        self.calls: Dict[str, Set[str]] = {}       # function → set of callees
        self.returns_ai: Dict[str, bool] = {}       # function → has AI data
        self.defined_functions: Set[str] = set()
        self._current_function: Optional[str] = None
        # Track line ranges for each function to check AI call containment.
        self._function_ranges: Dict[str, Tuple[int, int]] = {}

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_func(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_func(node)

    def _visit_func(self, node) -> None:
        name = node.name
        self.defined_functions.add(name)
        self.calls.setdefault(name, set())

        # Determine line range for this function body.
        start = node.lineno
        end = node.end_lineno if hasattr(node, "end_lineno") and node.end_lineno else start
        self._function_ranges[name] = (start, end)

        # Check if any AI call lines fall within this function.
        has_direct_ai = any(start <= line <= end for line in self._ai_call_lines)
        self.returns_ai[name] = has_direct_ai

        prev = self._current_function
        self._current_function = name
        self.generic_visit(node)
        self._current_function = prev

    def visit_Call(self, node: ast.Call) -> None:
        if self._current_function is not None:
            callee = self._callee_name(node)
            if callee:
                self.calls[self._current_function].add(callee)
        self.generic_visit(node)

    @staticmethod
    def _callee_name(node: ast.Call) -> Optional[str]:
        """Extract simple function name from a Call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            return node.func.attr
        return None

    def resolve_transitive_ai(self) -> Set[str]:
        """Propagate AI returns through call graph until stable.

        Returns the set of function names that (transitively) return AI data.
        """
        changed = True
        while changed:
            changed = False
            for func, callees in self.calls.items():
                if self.returns_ai.get(func):
                    continue
                for callee in callees:
                    if callee in self.defined_functions and self.returns_ai.get(callee):
                        self.returns_ai[func] = True
                        changed = True
                        break
        return {f for f, v in self.returns_ai.items() if v}


class _FlowTracer(ast.NodeVisitor):
    """Trace where AI call results flow within function bodies."""

    def __init__(self, ai_calls: List[Dict],
                 ai_returning_functions: Optional[Set[str]] = None) -> None:
        # Map source_line → ai_call dict for quick lookup.
        self._ai_lines: Dict[int, Dict] = {c["source_line"]: c for c in ai_calls}
        # Map variable name → source_line of the AI call that produced it.
        self._var_origins: Dict[str, int] = {}
        # Functions that transitively return AI data (cross-function tracing).
        self._ai_returning_functions: Set[str] = ai_returning_functions or set()
        self.flows: List[Dict] = []  # Final output.
        # Intermediate: source_line → list of destination dicts.
        self._destinations: Dict[int, List[Dict]] = {
            line: [] for line in self._ai_lines
        }

    def analyse(self, tree: ast.Module) -> List[Dict]:
        """Run analysis and return the flow list."""
        self.visit(tree)
        for line, call in self._ai_lines.items():
            self.flows.append({
                "source": call["source"],
                "source_line": call["source_line"],
                "destinations": self._destinations.get(line, []),
            })
        return self.flows

    # -- assignments: link variable to AI origin --------------------------

    def visit_Assign(self, node: ast.Assign) -> None:
        self._check_assignment(node.targets, node.value, node.lineno)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value and node.target:
            self._check_assignment([node.target], node.value, node.lineno)
        self.generic_visit(node)

    def _check_assignment(self, targets, value, lineno: int) -> None:
        origin_line = self._value_origin(value)
        if origin_line is None:
            return
        for target in targets:
            if isinstance(target, ast.Name):
                self._var_origins[target.id] = origin_line
                self._add_dest(origin_line, "variable", lineno, _unparse_safe(target))
            elif isinstance(target, ast.Tuple):
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        self._var_origins[elt.id] = origin_line

    # -- return -----------------------------------------------------------

    def visit_Return(self, node: ast.Return) -> None:
        if node.value:
            origin = self._value_origin(node.value)
            if origin is not None:
                self._add_dest(origin, "return", node.lineno, _unparse_safe(node.value))
        self.generic_visit(node)

    # -- calls: logging, human review, API, display, persist ---------------

    def visit_Call(self, node: ast.Call) -> None:
        # Determine if any argument carries AI data.
        origins = set()
        for arg in list(node.args) + [kw.value for kw in node.keywords]:
            o = self._value_origin(arg)
            if o is not None:
                origins.add(o)

        if origins:
            dest_type = self._classify_call(node)
            for origin in origins:
                self._add_dest(origin, dest_type, node.lineno, _unparse_safe(node))

        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        origin = self._value_origin(node.test)
        if origin is not None:
            self._add_dest(origin, "automated_action", node.lineno, _unparse_safe(node.test))
        self.generic_visit(node)

    # -- helpers ----------------------------------------------------------

    def _value_origin(self, node: ast.AST) -> Optional[int]:
        """Return the AI-call source_line if this node traces back to one."""
        if isinstance(node, ast.Name):
            return self._var_origins.get(node.id)
        if isinstance(node, ast.Call):
            line = getattr(node, "lineno", None)
            if line in self._ai_lines:
                return line
            # Cross-function: call to a function that returns AI data.
            callee = self._call_func_name(node)
            if callee and callee in self._ai_returning_functions:
                # Create a synthetic AI origin for this call line so
                # downstream destinations are tracked.
                if line is not None and line not in self._ai_lines:
                    self._ai_lines[line] = {
                        "source": _unparse_safe(node),
                        "source_line": line,
                        "method": callee,
                    }
                    self._destinations[line] = []
                return line
        if isinstance(node, ast.Attribute):
            return self._value_origin(node.value)
        if isinstance(node, ast.Subscript):
            return self._value_origin(node.value)
        return None

    @staticmethod
    def _call_func_name(node: ast.Call) -> Optional[str]:
        """Extract the simple function name from a Call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            return node.func.attr
        return None

    def _classify_call(self, node: ast.Call) -> str:
        """Heuristically classify a function call that consumes AI data."""
        name = self._full_call_name(node).lower()

        # Logging
        parts = name.split(".")
        if any(p in LOGGING_CALL_NAMES for p in parts):
            return "log"
        if "log" in name or "audit" in name:
            return "log"

        # Human review
        if any(kw in name for kw in HUMAN_OVERSIGHT_KEYWORDS):
            return "human_review"

        # Display
        if any(p in name for p in ("print", "render", "display", "show", "st.write", "st.markdown")):
            return "display"

        # Persist
        if any(p in name for p in ("write", "save", "dump", "to_csv", "to_json",
                                     "to_parquet", "insert", "put", "store", "persist")):
            return "persisted"

        # API response
        if any(p in name for p in ("send", "respond", "jsonify", "json_response",
                                    "Response", "make_response", "post", "publish")):
            return "api_response"

        return "variable"

    @staticmethod
    def _full_call_name(node: ast.Call) -> str:
        return _unparse_safe(node.func)

    def _add_dest(self, origin_line: int, dest_type: str, line: int, detail: str) -> None:
        if origin_line in self._destinations:
            self._destinations[origin_line].append({
                "type": dest_type,
                "line": line,
                "detail": detail,
            })


def trace_ai_data_flow(content: str) -> List[Dict]:
    """Trace where AI operation results flow within a single file.

    For each AI operation (model.predict, llm.invoke, chat.completions.create,
    etc.), returns where the result goes:

        source          — the AI call expression
        source_line     — line number
        destinations    — list of dicts, each with:
            type    — "return", "variable", "log", "human_review",
                      "automated_action", "api_response", "display", "persisted"
            line    — line number
            detail  — code snippet

    Returns an empty list if the content cannot be parsed.
    """
    try:
        tree = ast.parse(content, mode="exec")
    except SyntaxError:
        return []

    analysis = parse_python_file(content)

    collector = _AICallCollector()
    collector.set_ai_imports(analysis["ai_imports"])
    collector.visit(tree)

    if not collector.ai_calls:
        return []

    # Build call graph for cross-function tracing.
    ai_call_lines = {c["source_line"] for c in collector.ai_calls}
    cg = _CallGraphBuilder(ai_call_lines)
    cg.visit(tree)
    ai_returning = cg.resolve_transitive_ai()

    tracer = _FlowTracer(collector.ai_calls, ai_returning_functions=ai_returning)
    return tracer.analyse(tree)


# =========================================================================
# Article 14 — Human Oversight Detection
# =========================================================================

class _OversightVisitor(ast.NodeVisitor):
    """Detect human oversight patterns and automated decision paths."""

    def __init__(self) -> None:
        self.oversight_patterns: List[Dict] = []
        self.automated_decisions: List[Dict] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_oversight_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_oversight_function(node)
        self.generic_visit(node)

    def _check_oversight_function(self, node) -> None:
        name_lower = node.name.lower()
        for kw in HUMAN_OVERSIGHT_KEYWORDS:
            if kw in name_lower:
                self.oversight_patterns.append({
                    "type": "oversight_function",
                    "name": node.name,
                    "line": node.lineno,
                    "detail": f"Function '{node.name}' suggests human oversight",
                })
                break

        # Check decorators for oversight hints.
        for dec in node.decorator_list:
            dec_str = _unparse_safe(dec).lower()
            for kw in HUMAN_OVERSIGHT_KEYWORDS:
                if kw in dec_str:
                    self.oversight_patterns.append({
                        "type": "oversight_decorator",
                        "name": _unparse_safe(dec),
                        "line": dec.lineno,
                        "detail": f"Decorator suggests human oversight: {_unparse_safe(dec)}",
                    })
                    break

    def visit_Call(self, node: ast.Call) -> None:
        name = _unparse_safe(node.func).lower()
        for kw in HUMAN_OVERSIGHT_KEYWORDS:
            if kw in name:
                self.oversight_patterns.append({
                    "type": "oversight_call",
                    "name": _unparse_safe(node.func),
                    "line": node.lineno,
                    "detail": f"Call suggests human oversight: {_unparse_safe(node.func)}",
                })
                break
        self.generic_visit(node)


def detect_human_oversight(content: str) -> dict:
    """Assess human oversight provisions per EU AI Act Article 14.

    Returns:
        has_oversight         — bool
        oversight_patterns    — list of evidence dicts
        automated_decisions   — list of places where AI output feeds directly
                                into automated action without human review
        oversight_score       — 0-100 (0 = fully automated, 100 = full human
                                oversight)
    """
    try:
        tree = ast.parse(content, mode="exec")
    except SyntaxError:
        return {
            "has_oversight": False,
            "oversight_patterns": [],
            "automated_decisions": [],
            "oversight_score": 0,
        }

    visitor = _OversightVisitor()
    visitor.visit(tree)

    # Also use data-flow analysis to find automated decisions.
    flows = trace_ai_data_flow(content)
    automated: List[Dict] = []
    for flow in flows:
        for dest in flow["destinations"]:
            if dest["type"] == "automated_action":
                automated.append({
                    "source": flow["source"],
                    "source_line": flow["source_line"],
                    "decision_line": dest["line"],
                    "detail": dest["detail"],
                })

    # Also flag returns / API responses with no human review step.
    unreviewed_outputs: List[Dict] = []
    for flow in flows:
        has_review = any(d["type"] == "human_review" for d in flow["destinations"])
        for dest in flow["destinations"]:
            if dest["type"] in ("api_response", "automated_action") and not has_review:
                unreviewed_outputs.append({
                    "source": flow["source"],
                    "source_line": flow["source_line"],
                    "output_line": dest["line"],
                    "output_type": dest["type"],
                    "detail": dest["detail"],
                })

    all_automated = automated + visitor.automated_decisions
    for item in unreviewed_outputs:
        all_automated.append({
            "source": item["source"],
            "source_line": item["source_line"],
            "decision_line": item.get("output_line", item["source_line"]),
            "detail": item["detail"],
        })

    # Score: base 50.  +points for oversight evidence, -points for
    # unreviewed automated paths.
    score = 50
    score += min(len(visitor.oversight_patterns) * 15, 40)
    score -= min(len(all_automated) * 10, 50)

    # If there are flows but zero oversight patterns, floor the score.
    if flows and not visitor.oversight_patterns:
        score = min(score, 20)

    # If no AI operations at all, score is neutral.
    if not flows:
        score = 50

    score = max(0, min(100, score))

    return {
        "has_oversight": len(visitor.oversight_patterns) > 0,
        "oversight_patterns": visitor.oversight_patterns,
        "automated_decisions": all_automated,
        "oversight_score": score,
    }


# =========================================================================
# Article 12 — Logging Practices Detection
# =========================================================================

class _LoggingVisitor(ast.NodeVisitor):
    """Detect logging calls and correlate them with AI operations."""

    def __init__(self) -> None:
        self.logging_patterns: List[Dict] = []
        # Lines of logging calls for proximity checks.
        self.logging_lines: List[int] = []

    def visit_Call(self, node: ast.Call) -> None:
        name = self._call_name(node)
        if name and self._is_logging_call(name):
            self.logging_patterns.append({
                "call": _unparse_safe(node),
                "line": node.lineno,
                "name": name,
            })
            self.logging_lines.append(node.lineno)
        self.generic_visit(node)

    @staticmethod
    def _call_name(node: ast.Call) -> Optional[str]:
        return _unparse_safe(node.func)

    @staticmethod
    def _is_logging_call(name: str) -> bool:
        parts = name.lower().split(".")
        # logging.info, logger.warning, self.logger.debug, etc.
        if any(p in LOGGING_CALL_NAMES for p in parts):
            return True
        if "logging" in parts or "logger" in parts:
            return True
        return False


def detect_logging_practices(content: str) -> dict:
    """Assess logging practices per EU AI Act Article 12.

    Returns:
        has_logging            — bool
        logging_patterns       — list of logging call dicts
        ai_operations_logged   — count of AI ops with nearby logging
        ai_operations_unlogged — count of AI ops without nearby logging
        logging_score          — 0-100
    """
    try:
        tree = ast.parse(content, mode="exec")
    except SyntaxError:
        return {
            "has_logging": False,
            "logging_patterns": [],
            "ai_operations_logged": 0,
            "ai_operations_unlogged": 0,
            "logging_score": 0,
        }

    log_visitor = _LoggingVisitor()
    log_visitor.visit(tree)

    flows = trace_ai_data_flow(content)
    logging_lines = set(log_visitor.logging_lines)

    logged = 0
    unlogged = 0

    for flow in flows:
        ai_line = flow["source_line"]
        # Check if any destination is a log, or if there is a logging call
        # within a proximity window (5 lines before/after the AI call).
        has_log_dest = any(d["type"] == "log" for d in flow["destinations"])
        has_nearby_log = any(
            abs(ll - ai_line) <= 5 for ll in logging_lines
        )
        if has_log_dest or has_nearby_log:
            logged += 1
        else:
            unlogged += 1

    total_ops = logged + unlogged

    # Score calculation.
    if total_ops == 0:
        # No AI operations: base score from general logging presence.
        if log_visitor.logging_patterns:
            logging_score = 60
        else:
            logging_score = 50  # Neutral — nothing to log.
    else:
        ratio = logged / total_ops
        logging_score = int(ratio * 80)
        # Bonus for having structured logging at all.
        if log_visitor.logging_patterns:
            logging_score += 10
        logging_score = min(100, logging_score)

    return {
        "has_logging": len(log_visitor.logging_patterns) > 0,
        "logging_patterns": log_visitor.logging_patterns,
        "ai_operations_logged": logged,
        "ai_operations_unlogged": unlogged,
        "logging_score": logging_score,
    }


# =========================================================================
# CLI Entry Point
# =========================================================================

def main() -> None:
    """CLI entry point. Accepts --file or --input and prints JSON analysis."""
    parser = argparse.ArgumentParser(
        description="AST-based Python code analysis for EU AI Act compliance.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--file", "-f",
        help="Path to a Python file to analyse.",
    )
    group.add_argument(
        "--input", "-i",
        help="Raw Python source code string to analyse.",
    )
    parser.add_argument(
        "--phase",
        choices=["all", "parse", "classify", "flow", "oversight", "logging"],
        default="all",
        help="Which analysis phase to run (default: all).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )

    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as fh:
                content = fh.read()
        except (OSError, IOError) as exc:
            print(json.dumps({"error": str(exc)}), file=sys.stderr)
            sys.exit(1)
    else:
        content = args.input

    results: Dict = {}

    if args.phase in ("all", "parse"):
        results["parse"] = parse_python_file(content)
    if args.phase in ("all", "classify"):
        results["context"] = classify_context(content)
    if args.phase in ("all", "flow"):
        results["data_flow"] = trace_ai_data_flow(content)
    if args.phase in ("all", "oversight"):
        results["human_oversight"] = detect_human_oversight(content)
    if args.phase in ("all", "logging"):
        results["logging"] = detect_logging_practices(content)

    indent = 2 if args.pretty else None
    print(json.dumps(results, indent=indent, default=str))


if __name__ == "__main__":
    main()
