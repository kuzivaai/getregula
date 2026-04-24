#!/usr/bin/env python3
"""
AST Context Module — Phase B Precision Gating

Builds a line-level context map for Python source files using ast.parse().
Used by report.py to filter/adjust findings based on code context:
  - Patterns inside docstrings/string literals → lower confidence
  - Patterns inside try blocks → skip no_error_handling findings
  - Patterns inside test assertions → reduce confidence
"""

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def build_context_map(content: str) -> dict:
    """Build a line-number to AST-context map for a Python file.

    Returns a dict: {line_number: set_of_context_flags}
    Context flags: 'string', 'try', 'except', 'test_assert', 'decorator'

    Returns empty dict if parsing fails (non-Python, syntax errors).
    Graceful degradation: if AST parsing fails, pattern matching
    proceeds without context (no precision improvement, no breakage).
    """
    try:
        tree = ast.parse(content)
    except (SyntaxError, ValueError):
        return {}

    context = {}  # line_number -> set of context strings

    _walk_node(tree, context, set())
    return context


def _walk_node(node, context, parent_contexts):
    """Recursively walk AST, tracking context for each line span."""
    # Handle Try nodes specially to mark body vs handlers
    if isinstance(node, ast.Try):
        for child in node.body:
            _mark_lines(child, context, parent_contexts | {'try'})
        for handler in node.handlers:
            _mark_lines(handler, context, parent_contexts | {'except'})
        for child in node.orelse:
            _mark_lines(child, context, parent_contexts)
        for child in node.finalbody:
            _mark_lines(child, context, parent_contexts)
        return

    # Python 3.11+ TryStar (try/except*)
    if hasattr(ast, 'TryStar') and isinstance(node, ast.TryStar):
        for child in node.body:
            _mark_lines(child, context, parent_contexts | {'try'})
        for handler in node.handlers:
            _mark_lines(handler, context, parent_contexts | {'except'})
        for child in node.orelse:
            _mark_lines(child, context, parent_contexts)
        for child in node.finalbody:
            _mark_lines(child, context, parent_contexts)
        return

    # Standalone string expression = docstring
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
        _mark_range(node.lineno, node.end_lineno or node.lineno, context, 'string')

    # Assert statements
    if isinstance(node, ast.Assert):
        _mark_range(node.lineno, node.end_lineno or node.lineno, context, 'test_assert')

    # self.assert* calls (unittest style)
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        func = node.value.func
        if isinstance(func, ast.Attribute) and func.attr.startswith('assert'):
            _mark_range(node.lineno, node.end_lineno or node.lineno, context, 'test_assert')

    # Decorator lines
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        for decorator in node.decorator_list:
            _mark_range(
                decorator.lineno,
                decorator.end_lineno or decorator.lineno,
                context,
                'decorator',
            )

    # Recursively visit children
    for child in ast.iter_child_nodes(node):
        _walk_node(child, context, parent_contexts)


def _mark_lines(node, context, ctx_set):
    """Mark all lines spanned by a node with the given context set."""
    start = getattr(node, 'lineno', None)
    end = getattr(node, 'end_lineno', None) or start
    if start:
        for line in range(start, end + 1):
            if line not in context:
                context[line] = set()
            context[line].update(ctx_set)
    for child in ast.iter_child_nodes(node):
        _mark_lines(child, context, ctx_set)


def _mark_range(start, end, context, flag):
    """Mark a range of lines with a single flag."""
    for line in range(start, end + 1):
        if line not in context:
            context[line] = set()
        context[line].add(flag)


def get_line_context(context_map: dict, line: int) -> set:
    """Get the context flags for a specific line. Returns empty set if no context."""
    return context_map.get(line, set())


def is_in_try(context_map: dict, line: int) -> bool:
    """Check if a line is inside a try block."""
    return 'try' in context_map.get(line, set())


def is_in_string(context_map: dict, line: int) -> bool:
    """Check if a line is a docstring/string expression."""
    return 'string' in context_map.get(line, set())


def is_in_test_assert(context_map: dict, line: int) -> bool:
    """Check if a line is inside a test assertion."""
    return 'test_assert' in context_map.get(line, set())
