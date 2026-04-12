#!/usr/bin/env python3
# regula-ignore
"""
Regula Unified Multi-Language AST Analysis Engine

Wraps ast_analysis.py (Python) and provides regex-based fallback for
JavaScript/TypeScript. Returns a unified analysis format for all supported
languages.

No external dependencies required. Tree-sitter is optional for JS/TS
(falls back to regex if unavailable).
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))
from degradation import check_optional

# Import existing Python AST analysis module
sys.path.insert(0, str(Path(__file__).parent))
from ast_analysis import (
    parse_python_file,
    classify_context,
    trace_ai_data_flow,
    detect_human_oversight,
    detect_logging_practices,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EXTENSION_MAP: Dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".h": "cpp",    # Could be C or C++, treat as C++ for AI detection
    ".hpp": "cpp",
}

JS_AI_LIBRARIES = {
    "openai", "@openai",
    "anthropic", "@anthropic-ai/sdk",
    "langchain", "@langchain",
    "tensorflow", "@tensorflow/tfjs",
    "brain.js",
    "transformers", "@xenova/transformers",
    "@huggingface/inference",
    "replicate",
    "ai",
    "@pinecone-database/pinecone",
    "chromadb",
    "@qdrant/js-client-rest",
    "weaviate-ts-client",
    "litellm",
    "llamaindex",
}

# Patterns for extracting JS/TS imports
_RE_IMPORT_FROM = re.compile(
    r"""(?:import\s+(?:.*?\s+from\s+)?['"]([^'"]+)['"]|require\s*\(\s*['"]([^'"]+)['"]\s*\))""",
    re.MULTILINE,
)

# Pattern for detecting function definitions in JS/TS
_RE_FUNCTION_DEF = re.compile(
    r"""(?:(?:export\s+)?(?:async\s+)?function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[a-zA-Z_]\w*)\s*=>)""",
    re.MULTILINE,
)

# Pattern for detecting class definitions in JS/TS
_RE_CLASS_DEF = re.compile(
    r"""(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?""",
    re.MULTILINE,
)

# Test file indicators for JS/TS
_JS_TEST_PATTERNS = re.compile(
    r"""(?:describe\s*\(|it\s*\(|test\s*\(|expect\s*\(|jest\.|vitest\.|\.spec\.|\.test\.)""",
    re.MULTILINE,
)


JAVA_AI_LIBRARIES = {
    "com.google.cloud.aiplatform", "dev.langchain4j", "ai.djl",
    "org.tensorflow", "org.deeplearning4j", "com.microsoft.semantickernel",
    "com.azure.ai.openai", "software.amazon.awssdk.services.bedrockruntime",
    "com.google.cloud.vertexai", "io.weaviate", "com.theokanning.openai",
    "com.aallam.openai", "org.apache.spark.ml",
}

GO_AI_LIBRARIES = {
    "github.com/sashabaranov/go-openai",
    "github.com/tmc/langchaingo",
    "github.com/replicate/replicate-go",
    "gorgonia.org/gorgonia",
    "github.com/nlpodyssey/spago",
    "cloud.google.com/go/aiplatform",
    "github.com/aws/aws-sdk-go-v2/service/bedrockruntime",
    "github.com/gomlx/gomlx",
    "github.com/cohere-ai/cohere-go",
}

RUST_AI_LIBRARIES = {
    "candle-core", "candle-nn", "candle-transformers",
    "burn", "burn-core", "burn-tensor",
    "burn-ndarray", "burn-candle", "burn-wgpu",
    "tch",  # Rust bindings for PyTorch
    "ort",  # ONNX Runtime
    "ort-sys",
    "rust-bert",
    "llm",  # llm crate for local inference
    "async-openai",
    "anthropic-rs",
    "misanthropic",  # Anthropic client
    "openai-api-rs",
    "langchain-rust",
    "llm-chain", "llm-connector", "rsllm",
    "mistralrs",
    "kalosm",
    "safetensors",
    "tokenizers",
    "rust-tokenizers",
    "hf-hub",  # Hugging Face Hub
    "ndarray",  # Numerical arrays (AI-adjacent)
    "linfa",  # ML toolkit
    "linfa-clustering", "linfa-linear", "linfa-logistic", "linfa-trees", "linfa-svm",
    "smartcore",  # ML algorithms
    "qdrant-client", "pinecone-sdk",
    "polars",  # DataFrame library (AI-adjacent)
}

CPP_AI_LIBRARIES = {
    "tensorflow", "tensorflow/c", "tensorflow/cc", "tensorflow/core",
    "tensorflow/lite", "tensorflow/cc",
    "torch", "torch/torch.h", "ATen",
    "torch/script.h", "torch/nn.h", "torch/jit.h",
    "onnxruntime", "onnxruntime_c_api.h",
    "onnxruntime_cxx_api.h",
    "llama.h", "llama-cpp",
    "opencv", "opencv2",
    "opencv2/dnn",
    "dlib",
    "dlib/dnn.h", "dlib/svm.h",
    "mlpack", "mlpack.hpp",
    "shark",  # Shogun ML
    "caffe", "caffe/caffe.hpp",
    "ncnn",
    "mxnet",
    "armnn",  # ARM NN inference engine
    "tensorrt", "NvInfer.h",  # TensorRT
    "openvino",
    "whisper.h",  # whisper.cpp
    "stable-diffusion.h",  # stable-diffusion.cpp
    "xgboost/c_api.h", "xgboost/learner.h",
    "LightGBM/c_api.h",
    "flashlight",
    "faiss/IndexFlat.h", "faiss/index_io.h",
    "ggml.h", "ggml-alloc.h",
}

# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

def detect_language(filename: str) -> Optional[str]:
    """Map a filename to a supported language string.

    Returns one of "python", "javascript", "typescript", "java", "go",
    "rust", "c", "cpp", or None.
    """
    ext = Path(filename).suffix.lower()
    return EXTENSION_MAP.get(ext)


# ---------------------------------------------------------------------------
# Tree-sitter (optional)
# ---------------------------------------------------------------------------

def _flatten_member_expr(node) -> str:
    """Flatten a tree-sitter member_expression into a dotted string.

    E.g. ``client.chat.completions.create`` from nested member_expression nodes.
    Works for identifier, property_identifier, and member_expression node types.
    """
    if node.type == "identifier":
        return node.text.decode("utf-8")
    if node.type == "property_identifier":
        return node.text.decode("utf-8")
    if node.type == "member_expression":
        obj = node.child_by_field_name("object")
        prop = node.child_by_field_name("property")
        obj_str = _flatten_member_expr(obj) if obj else ""
        prop_str = prop.text.decode("utf-8") if prop else ""
        return f"{obj_str}.{prop_str}" if obj_str else prop_str
    # fallback
    return node.text.decode("utf-8")


def _tree_sitter_parse(content: str, language: str, filename: str = "unknown.js") -> dict:
    """Parse JS/TS using tree-sitter if available.

    Raises ImportError if tree-sitter is not installed.

    Parameters
    ----------
    content : str
        Source code to parse.
    language : str
        "javascript" or "typescript".
    filename : str
        Original filename (used for test-file detection).

    Returns
    -------
    dict
        Unified analysis result matching the format of _analyse_python().
    """
    # --- import tree-sitter packages (raise ImportError if missing) -------
    if not check_optional("tree_sitter", "tree-sitter JS/TS parsing",
                          "pip install tree-sitter tree-sitter-javascript tree-sitter-typescript"):
        raise ImportError(
            "tree-sitter is not installed. Install it with: "
            "pip install tree-sitter tree-sitter-javascript tree-sitter-typescript"
        )
    import tree_sitter_javascript as tsjs  # noqa: F401
    import tree_sitter_typescript as tsts  # noqa: F401
    from tree_sitter import Language, Parser

    # --- build parser -----------------------------------------------------
    if language == "typescript":
        lang_obj = Language(tsts.language_typescript())
    else:
        lang_obj = Language(tsjs.language())

    parser = Parser(lang_obj)
    tree = parser.parse(bytes(content, "utf-8"))
    root = tree.root_node

    # ── helper: recursive walk ────────────────────────────────────────────
    def _walk(node):
        yield node
        for child in node.children:
            yield from _walk(child)

    # ── 1. Extract imports ────────────────────────────────────────────────
    imports: List[str] = []

    for node in _walk(root):
        # import … from 'pkg'
        if node.type == "import_statement":
            source = node.child_by_field_name("source")
            if source:
                # source is a string node; its first child with type
                # string_fragment carries the actual text
                for child in source.children:
                    if child.type == "string_fragment":
                        imports.append(child.text.decode("utf-8"))
                        break
                else:
                    # fallback: strip quotes from text
                    raw = source.text.decode("utf-8").strip("'\"")
                    if raw:
                        imports.append(raw)

        # require('pkg')
        if node.type == "call_expression":
            func = node.child_by_field_name("function")
            if func and func.type == "identifier" and func.text == b"require":
                args = node.child_by_field_name("arguments")
                if args:
                    for arg_child in args.children:
                        if arg_child.type == "string":
                            for sc in arg_child.children:
                                if sc.type == "string_fragment":
                                    imports.append(sc.text.decode("utf-8"))
                                    break
                            else:
                                raw = arg_child.text.decode("utf-8").strip("'\"")
                                if raw:
                                    imports.append(raw)

    # Deduplicate preserving order
    imports = list(dict.fromkeys(imports))

    # ── 2. Identify AI imports ────────────────────────────────────────────
    ai_imports: List[str] = []
    for imp in imports:
        if imp in JS_AI_LIBRARIES:
            ai_imports.append(imp)
            continue
        for lib in JS_AI_LIBRARIES:
            if imp.startswith(lib + "/"):
                ai_imports.append(imp)
                break
    ai_imports = list(dict.fromkeys(ai_imports))
    has_ai_code = len(ai_imports) > 0

    # ── 3. Extract functions, arrow functions, classes ────────────────────
    function_defs: List[dict] = []
    class_defs: List[dict] = []

    for node in _walk(root):
        # function declarations: function foo(…) { … }
        if node.type == "function_declaration":
            name_node = node.child_by_field_name("name")
            name = name_node.text.decode("utf-8") if name_node else "<anonymous>"
            params = node.child_by_field_name("parameters")
            args = []
            if params:
                for p in params.children:
                    if p.type in (
                        "identifier", "required_parameter",
                        "optional_parameter", "rest_pattern",
                    ):
                        args.append(p.text.decode("utf-8"))
            function_defs.append({
                "name": name,
                "args": args,
                "decorators": [],
                "is_test": name.startswith("test") or name.startswith("it_"),
                "line": node.start_point[0] + 1,
            })

        # arrow functions assigned to a variable: const foo = (…) => …
        if node.type == "variable_declarator":
            name_node = node.child_by_field_name("name")
            value_node = node.child_by_field_name("value")
            if value_node and value_node.type == "arrow_function" and name_node:
                name = name_node.text.decode("utf-8")
                params = value_node.child_by_field_name("parameters")
                args = []
                if params:
                    for p in params.children:
                        if p.type in (
                            "identifier", "required_parameter",
                            "optional_parameter", "rest_pattern",
                        ):
                            args.append(p.text.decode("utf-8"))
                function_defs.append({
                    "name": name,
                    "args": args,
                    "decorators": [],
                    "is_test": name.startswith("test") or name.startswith("it_"),
                    "line": node.start_point[0] + 1,
                })

        # method definitions inside classes
        if node.type == "method_definition":
            name_node = node.child_by_field_name("name")
            name = name_node.text.decode("utf-8") if name_node else "<anonymous>"
            # We attach methods to the most recent class below
            # For now, just record as a function def
            params = node.child_by_field_name("parameters")
            args = []
            if params:
                for p in params.children:
                    if p.type in (
                        "identifier", "required_parameter",
                        "optional_parameter", "rest_pattern",
                    ):
                        args.append(p.text.decode("utf-8"))
            function_defs.append({
                "name": name,
                "args": args,
                "decorators": [],
                "is_test": False,
                "line": node.start_point[0] + 1,
            })

        # class declarations
        if node.type == "class_declaration":
            name_node = node.child_by_field_name("name")
            name = name_node.text.decode("utf-8") if name_node else "<anonymous>"
            # heritage / extends
            bases = []
            for child in node.children:
                if child.type == "class_heritage":
                    # The extends clause text, strip 'extends '
                    heritage_text = child.text.decode("utf-8").strip()
                    if heritage_text.startswith("extends "):
                        bases.append(heritage_text[8:].strip())
            # Collect method names from class body
            methods: List[str] = []
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    if child.type == "method_definition":
                        mn = child.child_by_field_name("name")
                        if mn:
                            methods.append(mn.text.decode("utf-8"))
            class_defs.append({
                "name": name,
                "bases": bases,
                "methods": methods,
            })

    # ── 4. Test file detection ────────────────────────────────────────────
    is_test_file = False
    basename = Path(filename).stem.lower()
    if basename.endswith((".test", ".spec")) or basename.startswith("test_"):
        is_test_file = True
    # Also check for describe/it/test/expect calls in the AST
    if not is_test_file:
        test_call_names = {"describe", "it", "test", "expect"}
        for node in _walk(root):
            if node.type == "call_expression":
                func = node.child_by_field_name("function")
                if func and func.type == "identifier":
                    if func.text.decode("utf-8") in test_call_names:
                        is_test_file = True
                        break

    # ── 5. Context classification ─────────────────────────────────────────
    if is_test_file:
        context = "test"
    elif has_ai_code:
        context = "implementation"
    else:
        config_patterns = re.compile(
            r"""(?:model|endpoint|api_key|temperature|max_tokens|prompt)\s*[:=]""",
            re.IGNORECASE,
        )
        context = "configuration" if config_patterns.search(content) else "implementation"

    # ── 6. AI call detection & data-flow tracing ──────────────────────────
    # Known AI method names that indicate an AI operation
    _AI_METHODS = {
        "create", "complete", "generate", "chat", "embed", "invoke",
        "predict", "run", "send", "stream",
    }

    # Collect all call_expression nodes that look like AI calls
    ai_call_nodes: List[tuple] = []  # (node, flat_call_str, line)

    for node in _walk(root):
        if node.type != "call_expression":
            continue
        func = node.child_by_field_name("function")
        if func is None:
            continue
        flat = _flatten_member_expr(func)
        # Check if this call involves an AI library or known method
        parts = flat.split(".")
        is_ai_call = False
        # Method name match
        if parts[-1] in _AI_METHODS and len(parts) > 1:
            # Check if any part of the chain relates to AI
            for imp in ai_imports:
                imp_base = imp.split("/")[-1].replace("-", "").lower()
                for p in parts:
                    if imp_base in p.lower():
                        is_ai_call = True
                        break
                if is_ai_call:
                    break
            # Also match common client patterns
            if not is_ai_call:
                chain = flat.lower()
                ai_chain_keywords = {
                    "openai", "anthropic", "client.chat", "client.messages",
                    "completions", "embeddings", "chat.completions",
                    "messages.create",
                }
                for kw in ai_chain_keywords:
                    if kw in chain:
                        is_ai_call = True
                        break
        # new OpenAI() / new Anthropic() — constructor calls
        if not is_ai_call and node.parent and node.parent.type == "new_expression":
            if func.type == "identifier":
                name = func.text.decode("utf-8").lower()
                for imp in ai_imports:
                    if name in imp.lower() or imp.lower().endswith(name):
                        is_ai_call = True
                        break

        if is_ai_call:
            ai_call_nodes.append((node, flat, node.start_point[0] + 1))

    # Now trace data flows from AI call results
    data_flows: List[dict] = []
    # Map: variable name -> line of AI call assignment
    ai_vars: Dict[str, int] = {}

    for call_node, flat_call, call_line in ai_call_nodes:
        destinations: List[dict] = []

        # Walk up to find the assignment (variable_declarator wrapping an
        # await_expression wrapping a call_expression, or direct assignment)
        current = call_node
        assigned_var = None
        while current.parent:
            current = current.parent
            if current.type == "variable_declarator":
                name_node = current.child_by_field_name("name")
                if name_node:
                    assigned_var = name_node.text.decode("utf-8")
                    ai_vars[assigned_var] = call_line
                    destinations.append({
                        "type": "variable",
                        "name": assigned_var,
                        "line": current.start_point[0] + 1,
                    })
                break
            if current.type in (
                "expression_statement", "return_statement",
                "lexical_declaration", "variable_declaration",
            ):
                break

        data_flows.append({
            "source": flat_call,
            "source_line": call_line,
            "destinations": destinations,
        })

    # Second pass: find where AI-assigned variables are used
    if ai_vars:
        lines = content.split("\n")
        for node in _walk(root):
            if node.type == "identifier" and node.text.decode("utf-8") in ai_vars:
                var_name = node.text.decode("utf-8")
                # Skip the original assignment
                if node.start_point[0] + 1 == ai_vars[var_name]:
                    # Could be the assignment itself — check parent
                    parent = node.parent
                    if parent and parent.type == "variable_declarator":
                        name_n = parent.child_by_field_name("name")
                        if name_n and name_n.text.decode("utf-8") == var_name:
                            continue

                dest = _classify_destination(node, lines)
                if dest:
                    # Attach to the first flow that involves this variable
                    for flow in data_flows:
                        for d in flow["destinations"]:
                            if d.get("name") == var_name:
                                flow["destinations"].append(dest)
                                break
                        else:
                            continue
                        break

    # ── 7. Human oversight detection (Article 14) ─────────────────────────
    oversight_keywords_set = {
        "review", "approve", "approval", "confirm", "verify",
        "human", "manual", "override", "escalate", "moderator",
    }

    oversight_patterns: List[dict] = []
    oversight_functions: List[str] = []
    automated_decisions: List[dict] = []

    for fdef in function_defs:
        name_lower = fdef["name"].lower()
        for kw in oversight_keywords_set:
            if kw in name_lower:
                oversight_functions.append(fdef["name"])
                oversight_patterns.append({
                    "keyword": kw,
                    "function": fdef["name"],
                    "line": fdef.get("line", 0),
                })
                break

    # Also scan for oversight-related call expressions
    for node in _walk(root):
        if node.type == "call_expression":
            func = node.child_by_field_name("function")
            if func:
                flat = _flatten_member_expr(func).lower()
                for kw in oversight_keywords_set:
                    if kw in flat:
                        oversight_patterns.append({
                            "keyword": kw,
                            "call": _flatten_member_expr(func),
                            "line": node.start_point[0] + 1,
                        })
                        break

    # Detect automated decisions (if statements using AI vars without review)
    for node in _walk(root):
        if node.type == "if_statement":
            test_node = node.child_by_field_name("condition")
            if test_node:
                test_text = test_node.text.decode("utf-8")
                for var in ai_vars:
                    if var in test_text:
                        # Check if there's a review call inside the if body
                        has_review = False
                        for inner in _walk(node):
                            if inner.type == "call_expression":
                                inner_func = inner.child_by_field_name("function")
                                if inner_func:
                                    inner_flat = _flatten_member_expr(inner_func).lower()
                                    for kw in oversight_keywords_set:
                                        if kw in inner_flat:
                                            has_review = True
                                            break
                            if has_review:
                                break
                        if not has_review:
                            automated_decisions.append({
                                "line": node.start_point[0] + 1,
                                "variable": var,
                                "has_review": False,
                            })

    # Compute oversight score
    oversight_score = 50
    oversight_score += min(len(oversight_patterns) * 15, 40)
    oversight_score -= min(len(automated_decisions) * 10, 50)
    if has_ai_code and not oversight_patterns:
        oversight_score = min(oversight_score, 20)
    oversight_score = max(0, min(100, oversight_score))

    oversight = {
        "has_oversight": len(oversight_patterns) > 0,
        "oversight_patterns": oversight_patterns,
        "automated_decisions": automated_decisions,
        "oversight_score": oversight_score,
    }

    # ── 8. Logging detection (Article 12) ─────────────────────────────────
    _LOG_PATTERNS = {
        "console.log", "console.warn", "console.error", "console.info",
        "console.debug",
    }
    _LOG_PREFIXES = {"logger", "winston", "pino", "log"}
    _LOG_METHODS = {"info", "debug", "warn", "error", "log", "trace", "fatal"}

    logging_patterns_found: List[dict] = []
    logging_lines: set = set()

    for node in _walk(root):
        if node.type == "call_expression":
            func = node.child_by_field_name("function")
            if func is None:
                continue
            flat = _flatten_member_expr(func)
            is_log = False
            if flat in _LOG_PATTERNS:
                is_log = True
            else:
                parts = flat.split(".")
                if len(parts) >= 2:
                    if parts[0].lower() in _LOG_PREFIXES and parts[-1] in _LOG_METHODS:
                        is_log = True
                    elif parts[-1] in _LOG_METHODS and any(
                        p.lower() in _LOG_PREFIXES for p in parts
                    ):
                        is_log = True
            if is_log:
                line = node.start_point[0] + 1
                logging_patterns_found.append({
                    "call": flat,
                    "line": line,
                })
                logging_lines.add(line)

    # Count AI operations with nearby logging (within 5 lines)
    ai_ops_total = len(ai_call_nodes)
    ai_ops_logged = 0
    for _, _, call_line in ai_call_nodes:
        for ll in logging_lines:
            if abs(ll - call_line) <= 5:
                ai_ops_logged += 1
                break

    if ai_ops_total == 0:
        logging_score = 50
    else:
        logging_score = int((ai_ops_logged / ai_ops_total) * 80)
        if logging_patterns_found:
            logging_score += 10
    logging_score = max(0, min(100, logging_score))

    logging_info = {
        "has_logging": len(logging_patterns_found) > 0,
        "logging_patterns": logging_patterns_found,
        "ai_operations_logged": ai_ops_logged,
        "ai_operations_unlogged": ai_ops_total - ai_ops_logged,
        "logging_score": logging_score,
    }

    # ── Return unified dict ───────────────────────────────────────────────
    return {
        "language": language,
        "imports": imports,
        "ai_imports": ai_imports,
        "has_ai_code": has_ai_code,
        "context": context,
        "function_defs": function_defs,
        "class_defs": class_defs,
        "is_test_file": is_test_file,
        "data_flows": data_flows,
        "oversight": oversight,
        "logging": logging_info,
    }


def _classify_destination(id_node, lines: List[str]) -> Optional[dict]:
    """Classify how an AI-result variable is used at a given reference site.

    Returns a destination dict or None if not classifiable.
    """
    line = id_node.start_point[0] + 1
    parent = id_node.parent
    if parent is None:
        return None

    # Walk up through member expressions to find the call / statement
    current = parent
    while current and current.type == "member_expression":
        current = current.parent

    # return statement
    if current and current.type == "return_statement":
        return {"type": "return", "line": line}

    # Check the containing call_expression
    if current and current.type == "arguments":
        current = current.parent
    if current and current.type == "call_expression":
        func = current.child_by_field_name("function")
        if func:
            flat = _flatten_member_expr(func).lower()
            # Try to classify by the function being called
            # Log patterns
            log_indicators = {"console", "logger", "winston", "pino", "log"}
            log_methods = {"log", "info", "debug", "warn", "error", "trace", "fatal"}
            parts = flat.split(".")
            if any(p in log_indicators for p in parts) and parts[-1] in log_methods:
                return {"type": "log", "call": flat, "line": line}
            if flat in {"console.log", "console.warn", "console.error", "console.info"}:
                return {"type": "log", "call": flat, "line": line}

            # Human review
            review_kws = {"review", "approve", "confirm", "verify", "human", "manual", "escalate"}
            if any(kw in flat for kw in review_kws):
                return {"type": "human_review", "call": flat, "line": line}

            # API response
            api_kws = {"res.json", "res.send", "response", "reply"}
            if any(kw in flat for kw in api_kws):
                return {"type": "api_response", "call": flat, "line": line}

            # Display
            display_kws = {"render", "write", "display"}
            if any(kw in flat for kw in display_kws):
                return {"type": "display", "call": flat, "line": line}

            # Persisted
            persist_kws = {"save", "insert", "update", "writefile", "set"}
            if any(kw in flat for kw in persist_kws):
                return {"type": "persisted", "call": flat, "line": line}

    # If used in an if condition
    if parent and parent.type in ("binary_expression", "parenthesized_expression"):
        # Walk up to find if_statement
        cur = parent
        while cur:
            if cur.type == "if_statement":
                cond = cur.child_by_field_name("condition")
                if cond and id_node.start_point[0] == cond.start_point[0]:
                    return {"type": "automated_action", "line": line}
                break
            cur = cur.parent

    return None


# ---------------------------------------------------------------------------
# JS/TS regex fallback
# ---------------------------------------------------------------------------

def _analyse_js_ts_regex(content: str, filename: str) -> dict:
    """Analyse JavaScript/TypeScript using regex patterns.

    This is the default fallback when tree-sitter is not available.
    """
    # Extract imports
    imports = []
    for match in _RE_IMPORT_FROM.finditer(content):
        module = match.group(1) or match.group(2)
        if module:
            imports.append(module)

    # Identify AI imports
    ai_imports = []
    for imp in imports:
        # Check direct match or prefix match for scoped packages
        if imp in JS_AI_LIBRARIES:
            ai_imports.append(imp)
            continue
        # Check if the import starts with a known AI library prefix
        for lib in JS_AI_LIBRARIES:
            if imp == lib or imp.startswith(lib + "/"):
                ai_imports.append(imp)
                break

    # Deduplicate while preserving order
    ai_imports = list(dict.fromkeys(ai_imports))

    has_ai_code = len(ai_imports) > 0

    # Extract function definitions
    function_defs = []
    for match in _RE_FUNCTION_DEF.finditer(content):
        name = match.group(1) or match.group(2)
        if name:
            is_test = name.startswith("test") or name.startswith("it_")
            function_defs.append({
                "name": name,
                "args": [],
                "decorators": [],
                "is_test": is_test,
            })

    # Extract class definitions
    class_defs = []
    for match in _RE_CLASS_DEF.finditer(content):
        name = match.group(1)
        base = match.group(2)
        class_defs.append({
            "name": name,
            "bases": [base] if base else [],
            "methods": [],
        })

    # Determine if test file
    is_test_file = bool(_JS_TEST_PATTERNS.search(content))
    basename = Path(filename).stem.lower()
    if basename.endswith((".test", ".spec")) or basename.startswith("test_"):
        is_test_file = True

    # Classify context
    if is_test_file:
        context = "test"
    elif has_ai_code:
        context = "implementation"
    else:
        # Check for config-like patterns
        config_patterns = re.compile(
            r"""(?:model|endpoint|api_key|temperature|max_tokens|prompt)\s*[:=]""",
            re.IGNORECASE,
        )
        if config_patterns.search(content):
            context = "configuration"
        else:
            context = "implementation"

    # Basic data flow detection for JS/TS (simplified)
    data_flows = []
    if has_ai_code:
        # Look for common AI call patterns
        ai_call_re = re.compile(
            r"""(?:await\s+)?(\w+(?:\.\w+)*)\s*\.\s*(?:create|complete|generate|chat|embed|invoke|predict|run)\s*\(""",
            re.MULTILINE,
        )
        for match in ai_call_re.finditer(content):
            data_flows.append({
                "source": match.group(0).rstrip("(").strip(),
                "source_line": content[:match.start()].count("\n") + 1,
                "destinations": [],
            })

    # Basic oversight detection
    oversight_keywords = {
        "review", "approve", "approval", "confirm", "verify",
        "human", "manual", "override", "escalate", "moderator",
    }
    oversight_patterns = []
    for kw in oversight_keywords:
        if re.search(r"\b" + kw + r"\b", content, re.IGNORECASE):
            oversight_patterns.append({"keyword": kw})

    oversight = {
        "has_oversight": len(oversight_patterns) > 0,
        "oversight_patterns": oversight_patterns,
        "automated_decisions": [],
        "oversight_score": 50 + min(len(oversight_patterns) * 15, 40),
    }
    oversight["oversight_score"] = min(100, oversight["oversight_score"])

    # Basic logging detection
    logging_re = re.compile(
        r"""(?:console\.\w+|logger\.\w+|log\.\w+|winston\.\w+|pino\.\w+)\s*\(""",
        re.MULTILINE,
    )
    logging_patterns = []
    for match in logging_re.finditer(content):
        logging_patterns.append({
            "call": match.group(0).rstrip("(").strip(),
            "line": content[:match.start()].count("\n") + 1,
        })

    logging_info = {
        "has_logging": len(logging_patterns) > 0,
        "logging_patterns": logging_patterns,
        "ai_operations_logged": 0,
        "ai_operations_unlogged": len(data_flows),
        "logging_score": 60 if logging_patterns else 50,
    }

    return {
        "language": detect_language(filename) or "javascript",
        "imports": imports,
        "ai_imports": ai_imports,
        "has_ai_code": has_ai_code,
        "context": context,
        "function_defs": function_defs,
        "class_defs": class_defs,
        "is_test_file": is_test_file,
        "data_flows": data_flows,
        "oversight": oversight,
        "logging": logging_info,
    }


# ---------------------------------------------------------------------------
# Python analysis (delegates to ast_analysis.py)
# ---------------------------------------------------------------------------

def _analyse_python(content: str, filename: str) -> dict:
    """Analyse Python source by delegating to ast_analysis.py functions."""
    parsed = parse_python_file(content)
    context = classify_context(content)
    data_flows = trace_ai_data_flow(content)
    oversight = detect_human_oversight(content)
    logging_info = detect_logging_practices(content)

    # Map classify_context's "not_python" to unified "not_parseable"
    if context == "not_python":
        context = "not_parseable"

    return {
        "language": "python",
        "imports": parsed["imports"],
        "ai_imports": parsed["ai_imports"],
        "has_ai_code": parsed["has_ai_code"],
        "context": context,
        "function_defs": parsed["function_defs"],
        "class_defs": parsed["class_defs"],
        "is_test_file": parsed["is_test_file"],
        "data_flows": data_flows,
        "oversight": oversight,
        "logging": logging_info,
    }


# ---------------------------------------------------------------------------
# JS/TS analysis (tree-sitter with regex fallback)
# ---------------------------------------------------------------------------

def _analyse_js_ts(content: str, filename: str) -> dict:
    """Analyse JavaScript/TypeScript source.

    Tries tree-sitter first, falls back to regex.
    """
    try:
        return _tree_sitter_parse(content, detect_language(filename) or "javascript", filename=filename)
    except ImportError:
        return _analyse_js_ts_regex(content, filename)


# ---------------------------------------------------------------------------
# Java regex analysis
# ---------------------------------------------------------------------------

_RE_JAVA_IMPORT = re.compile(r'import\s+(static\s+)?([\w.]+)\s*;', re.MULTILINE)
_RE_JAVA_TEST_ANNOTATION = re.compile(r'@Test\b', re.MULTILINE)
_RE_JAVA_CLASS_DEF = re.compile(r'(?:public\s+|private\s+|protected\s+|abstract\s+|final\s+)*class\s+(\w+)', re.MULTILINE)
_RE_JAVA_METHOD_DEF = re.compile(r'(?:(?:public|private|protected|static|abstract|final|synchronized)\s+)*[\w<>\[\].]{1,80}\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{', re.MULTILINE)


def _analyse_java_regex(content: str) -> dict:
    """Analyse Java source using regex patterns."""
    # Extract imports
    imports = []
    for match in _RE_JAVA_IMPORT.finditer(content):
        pkg = match.group(2)
        if pkg:
            imports.append(pkg)

    # Identify AI imports (check if any prefix matches a known library)
    ai_imports = []
    for imp in imports:
        for lib in JAVA_AI_LIBRARIES:
            if imp == lib or imp.startswith(lib + "."):
                ai_imports.append(imp)
                break

    ai_imports = list(dict.fromkeys(ai_imports))
    has_ai_code = len(ai_imports) > 0

    # Extract class definitions
    class_defs = []
    for match in _RE_JAVA_CLASS_DEF.finditer(content):
        name = match.group(1)
        class_defs.append({"name": name, "bases": [], "methods": []})

    # Extract method definitions
    function_defs = []
    for match in _RE_JAVA_METHOD_DEF.finditer(content):
        name = match.group(1)
        if name not in {"if", "while", "for", "switch", "catch"}:
            function_defs.append({
                "name": name,
                "args": [],
                "decorators": [],
                "is_test": name.startswith("test"),
            })

    # Determine if test file based on class name or @Test annotations
    is_test_file = bool(_RE_JAVA_TEST_ANNOTATION.search(content))
    for cls in class_defs:
        if cls["name"].startswith("Test") or cls["name"].endswith("Test"):
            is_test_file = True
            break

    # Classify context
    if is_test_file:
        context = "test"
    elif has_ai_code:
        context = "implementation"
    else:
        config_patterns = re.compile(
            r"""(?:model|endpoint|apiKey|api_key|temperature|maxTokens|prompt)\s*[=:]""",
            re.IGNORECASE,
        )
        context = "configuration" if config_patterns.search(content) else "implementation"

    # Basic oversight detection
    oversight_keywords = {
        "review", "approve", "approval", "confirm", "verify",
        "human", "manual", "override", "escalate", "moderator",
    }
    oversight_patterns = []
    for kw in oversight_keywords:
        if re.search(r"\b" + kw + r"\b", content, re.IGNORECASE):
            oversight_patterns.append({"keyword": kw})

    oversight = {
        "has_oversight": len(oversight_patterns) > 0,
        "oversight_patterns": oversight_patterns,
        "automated_decisions": [],
        "oversight_score": min(100, 50 + min(len(oversight_patterns) * 15, 40)),
    }

    # Basic logging detection
    logging_re = re.compile(
        r"""(?:logger\.\w+|log\.\w+|Logger\.\w+|System\.out\.print)\s*\(""",
        re.MULTILINE,
    )
    logging_patterns = []
    for match in logging_re.finditer(content):
        logging_patterns.append({
            "call": match.group(0).rstrip("(").strip(),
            "line": content[:match.start()].count("\n") + 1,
        })

    logging_info = {
        "has_logging": len(logging_patterns) > 0,
        "logging_patterns": logging_patterns,
        "ai_operations_logged": 0,
        "ai_operations_unlogged": 0,
        "logging_score": 60 if logging_patterns else 50,
    }

    return {
        "language": "java",
        "imports": imports,
        "ai_imports": ai_imports,
        "has_ai_code": has_ai_code,
        "context": context,
        "function_defs": function_defs,
        "class_defs": class_defs,
        "is_test_file": is_test_file,
        "data_flows": [],
        "oversight": oversight,
        "logging": logging_info,
    }


# ---------------------------------------------------------------------------
# Go regex analysis
# ---------------------------------------------------------------------------

_RE_GO_IMPORT_BLOCK = re.compile(r'import\s*\(([^)]*)\)', re.MULTILINE | re.DOTALL)
_RE_GO_IMPORT_SINGLE = re.compile(r'^import\s+"([\w./\-]+)"', re.MULTILINE)
_RE_GO_QUOTED = re.compile(r'"([\w./\-]+)"')
_RE_GO_FUNC_DEF = re.compile(r'^func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(', re.MULTILINE)
_RE_GO_STRUCT_DEF = re.compile(r'^type\s+(\w+)\s+struct\b', re.MULTILINE)


def _analyse_go_regex(content: str) -> dict:
    """Analyse Go source using regex patterns."""
    # Extract imports from import blocks and standalone import statements
    imports = []
    for block_match in _RE_GO_IMPORT_BLOCK.finditer(content):
        block = block_match.group(1)
        for q_match in _RE_GO_QUOTED.finditer(block):
            imports.append(q_match.group(1))
    for match in _RE_GO_IMPORT_SINGLE.finditer(content):
        imports.append(match.group(1))

    imports = list(dict.fromkeys(imports))

    # Identify AI imports
    ai_imports = []
    for imp in imports:
        for lib in GO_AI_LIBRARIES:
            if imp == lib or imp.startswith(lib + "/"):
                ai_imports.append(imp)
                break

    ai_imports = list(dict.fromkeys(ai_imports))
    has_ai_code = len(ai_imports) > 0

    # Extract function definitions
    function_defs = []
    for match in _RE_GO_FUNC_DEF.finditer(content):
        name = match.group(1)
        function_defs.append({
            "name": name,
            "args": [],
            "decorators": [],
            "is_test": name.startswith("Test"),
        })

    # Extract struct definitions (analogous to class defs)
    class_defs = []
    for match in _RE_GO_STRUCT_DEF.finditer(content):
        name = match.group(1)
        class_defs.append({"name": name, "bases": [], "methods": []})

    # Determine if test file
    is_test_file = any(f["is_test"] for f in function_defs)

    # Classify context
    if is_test_file:
        context = "test"
    elif has_ai_code:
        context = "implementation"
    else:
        config_patterns = re.compile(
            r"""(?:model|endpoint|apiKey|api_key|temperature|maxTokens|prompt)\s*[=:]""",
            re.IGNORECASE,
        )
        context = "configuration" if config_patterns.search(content) else "implementation"

    # Basic oversight detection
    oversight_keywords = {
        "review", "approve", "approval", "confirm", "verify",
        "human", "manual", "override", "escalate", "moderator",
    }
    oversight_patterns = []
    for kw in oversight_keywords:
        if re.search(r"\b" + kw + r"\b", content, re.IGNORECASE):
            oversight_patterns.append({"keyword": kw})

    oversight = {
        "has_oversight": len(oversight_patterns) > 0,
        "oversight_patterns": oversight_patterns,
        "automated_decisions": [],
        "oversight_score": min(100, 50 + min(len(oversight_patterns) * 15, 40)),
    }

    # Basic logging detection
    logging_re = re.compile(
        r"""(?:log\.\w+|fmt\.Print|slog\.\w+|zap\.\w+|logrus\.\w+)\s*\(""",
        re.MULTILINE,
    )
    logging_patterns = []
    for match in logging_re.finditer(content):
        logging_patterns.append({
            "call": match.group(0).rstrip("(").strip(),
            "line": content[:match.start()].count("\n") + 1,
        })

    logging_info = {
        "has_logging": len(logging_patterns) > 0,
        "logging_patterns": logging_patterns,
        "ai_operations_logged": 0,
        "ai_operations_unlogged": 0,
        "logging_score": 60 if logging_patterns else 50,
    }

    return {
        "language": "go",
        "imports": imports,
        "ai_imports": ai_imports,
        "has_ai_code": has_ai_code,
        "context": context,
        "function_defs": function_defs,
        "class_defs": class_defs,
        "is_test_file": is_test_file,
        "data_flows": [],
        "oversight": oversight,
        "logging": logging_info,
    }


# ---------------------------------------------------------------------------
# Rust regex analysis
# ---------------------------------------------------------------------------

_RE_RUST_USE = re.compile(r'use\s+([\w:]+)', re.MULTILINE)
_RE_RUST_CARGO_DEP = re.compile(r'^([\w\-]+)\s*=', re.MULTILINE)
_RE_RUST_FN_DEF = re.compile(r'^(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*\(', re.MULTILINE)
_RE_RUST_STRUCT_DEF = re.compile(r'^(?:pub\s+)?struct\s+(\w+)\b', re.MULTILINE)


def _analyse_rust_regex(content: str) -> dict:
    """Analyse Rust source (or Cargo.toml) using regex patterns."""
    imports = []
    is_cargo_toml = "[dependencies]" in content or "[package]" in content

    if is_cargo_toml:
        # Parse Cargo.toml dependency names
        in_deps = False
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("[dependencies]") or stripped.startswith("[dev-dependencies]"):
                in_deps = True
                continue
            if stripped.startswith("[") and stripped.endswith("]"):
                in_deps = False
            if in_deps:
                m = _RE_RUST_CARGO_DEP.match(line)
                if m:
                    imports.append(m.group(1))
    else:
        # Parse `use` statements
        for match in _RE_RUST_USE.finditer(content):
            path = match.group(1)
            # The crate root is the first segment before '::'
            crate_root = path.split("::")[0]
            # Rust uses underscores in code but hyphens in Cargo.toml
            # Normalise underscores → hyphens for matching against RUST_AI_LIBRARIES
            imports.append(crate_root)

    imports = list(dict.fromkeys(imports))

    # Identify AI imports: normalise underscores → hyphens for comparison
    ai_imports = []
    for imp in imports:
        normalised = imp.replace("_", "-")
        if normalised in RUST_AI_LIBRARIES or imp in RUST_AI_LIBRARIES:
            ai_imports.append(imp)

    ai_imports = list(dict.fromkeys(ai_imports))
    has_ai_code = len(ai_imports) > 0

    # Extract function definitions
    function_defs = []
    for match in _RE_RUST_FN_DEF.finditer(content):
        name = match.group(1)
        function_defs.append({
            "name": name,
            "args": [],
            "decorators": [],
            "is_test": name.startswith("test_") or name == "test",
        })

    # Extract struct definitions (analogous to class defs)
    class_defs = []
    for match in _RE_RUST_STRUCT_DEF.finditer(content):
        name = match.group(1)
        class_defs.append({"name": name, "bases": [], "methods": []})

    # Determine if test file
    is_test_file = any(f["is_test"] for f in function_defs) or "#[cfg(test)]" in content

    # Classify context
    if is_test_file:
        context = "test"
    elif has_ai_code:
        context = "implementation"
    else:
        config_patterns = re.compile(
            r"""(?:model|endpoint|api_key|temperature|max_tokens|prompt)\s*[=:]""",
            re.IGNORECASE,
        )
        context = "configuration" if config_patterns.search(content) else "implementation"

    # Basic oversight detection
    oversight_keywords = {
        "review", "approve", "approval", "confirm", "verify",
        "human", "manual", "override", "escalate", "moderator",
    }
    oversight_patterns = []
    for kw in oversight_keywords:
        if re.search(r"\b" + kw + r"\b", content, re.IGNORECASE):
            oversight_patterns.append({"keyword": kw})

    oversight = {
        "has_oversight": len(oversight_patterns) > 0,
        "oversight_patterns": oversight_patterns,
        "automated_decisions": [],
        "oversight_score": min(100, 50 + min(len(oversight_patterns) * 15, 40)),
    }

    # Basic logging detection
    logging_re = re.compile(
        r"""(?:log::(?:info|debug|warn|error|trace)|println!|eprintln!|tracing::(?:info|debug|warn|error|trace))\s*[!(]""",
        re.MULTILINE,
    )
    logging_patterns = []
    for match in logging_re.finditer(content):
        logging_patterns.append({
            "call": match.group(0).rstrip("!(").strip(),
            "line": content[:match.start()].count("\n") + 1,
        })

    logging_info = {
        "has_logging": len(logging_patterns) > 0,
        "logging_patterns": logging_patterns,
        "ai_operations_logged": 0,
        "ai_operations_unlogged": 0,
        "logging_score": 60 if logging_patterns else 50,
    }

    return {
        "language": "rust",
        "imports": imports,
        "ai_imports": ai_imports,
        "has_ai_code": has_ai_code,
        "context": context,
        "function_defs": function_defs,
        "class_defs": class_defs,
        "is_test_file": is_test_file,
        "data_flows": [],
        "oversight": oversight,
        "logging": logging_info,
    }


# ---------------------------------------------------------------------------
# C/C++ regex analysis
# ---------------------------------------------------------------------------

_RE_CPP_INCLUDE = re.compile(r'#include\s*[<"]([\w/.\-]+)[>"]', re.MULTILINE)
_RE_CPP_FUNC_DEF = re.compile(
    r'^(?:[\w:*&<>\s]+)\s+(\w+)\s*\([^)]*\)\s*(?:const\s*)?\{',
    re.MULTILINE,
)
_RE_CPP_CLASS_DEF = re.compile(r'^(?:class|struct)\s+(\w+)\b', re.MULTILINE)


def _analyse_cpp_regex(content: str) -> dict:
    """Analyse C/C++ source using regex patterns."""
    # Extract #include directives
    imports = []
    for match in _RE_CPP_INCLUDE.finditer(content):
        imports.append(match.group(1))

    imports = list(dict.fromkeys(imports))

    # Identify AI imports by checking against CPP_AI_LIBRARIES
    ai_imports = []
    for inc in imports:
        # Direct match
        if inc in CPP_AI_LIBRARIES:
            ai_imports.append(inc)
            continue
        # Prefix match: e.g. "opencv2/core.hpp" matches "opencv2" prefix
        for lib in CPP_AI_LIBRARIES:
            if inc == lib or inc.startswith(lib + "/") or inc.startswith(lib + "."):
                ai_imports.append(inc)
                break

    # Also detect usage patterns like cv::Mat, torch::Tensor, tf::Tensor
    cpp_usage_patterns = re.compile(
        r'\b(?:cv|torch|tf|ort|dlib|caffe|ncnn|mxnet|armnn|trt|ov)::\w+',
        re.MULTILINE,
    )
    for match in cpp_usage_patterns.finditer(content):
        # Map namespace to a representative library if not already detected
        ns = match.group(0).split("::")[0]
        ns_to_lib = {
            "cv": "opencv", "torch": "torch", "tf": "tensorflow",
            "ort": "onnxruntime", "dlib": "dlib", "caffe": "caffe",
            "ncnn": "ncnn", "mxnet": "mxnet", "armnn": "armnn",
            "trt": "tensorrt", "ov": "openvino",
        }
        lib_name = ns_to_lib.get(ns)
        if lib_name and lib_name not in ai_imports:
            ai_imports.append(lib_name)

    ai_imports = list(dict.fromkeys(ai_imports))
    has_ai_code = len(ai_imports) > 0

    # Extract function definitions (simplified)
    function_defs = []
    for match in _RE_CPP_FUNC_DEF.finditer(content):
        name = match.group(1)
        if name not in {"if", "while", "for", "switch", "catch", "else"}:
            function_defs.append({
                "name": name,
                "args": [],
                "decorators": [],
                "is_test": name.startswith("test") or name.startswith("Test"),
            })

    # Extract class/struct definitions
    class_defs = []
    for match in _RE_CPP_CLASS_DEF.finditer(content):
        name = match.group(1)
        class_defs.append({"name": name, "bases": [], "methods": []})

    # Determine if test file
    is_test_file = any(f["is_test"] for f in function_defs)

    # Classify context
    if is_test_file:
        context = "test"
    elif has_ai_code:
        context = "implementation"
    else:
        config_patterns = re.compile(
            r"""(?:model|endpoint|api_key|temperature|max_tokens|prompt)\s*[=:]""",
            re.IGNORECASE,
        )
        context = "configuration" if config_patterns.search(content) else "implementation"

    # Basic oversight detection
    oversight_keywords = {
        "review", "approve", "approval", "confirm", "verify",
        "human", "manual", "override", "escalate", "moderator",
    }
    oversight_patterns = []
    for kw in oversight_keywords:
        if re.search(r"\b" + kw + r"\b", content, re.IGNORECASE):
            oversight_patterns.append({"keyword": kw})

    oversight = {
        "has_oversight": len(oversight_patterns) > 0,
        "oversight_patterns": oversight_patterns,
        "automated_decisions": [],
        "oversight_score": min(100, 50 + min(len(oversight_patterns) * 15, 40)),
    }

    # Basic logging detection
    logging_re = re.compile(
        r"""(?:std::cout|std::cerr|printf|fprintf|spdlog::\w+|LOG(?:_INFO|_DEBUG|_WARN|_ERROR)?)\s*[(<]""",
        re.MULTILINE,
    )
    logging_patterns = []
    for match in logging_re.finditer(content):
        logging_patterns.append({
            "call": match.group(0).rstrip("(<").strip(),
            "line": content[:match.start()].count("\n") + 1,
        })

    logging_info = {
        "has_logging": len(logging_patterns) > 0,
        "logging_patterns": logging_patterns,
        "ai_operations_logged": 0,
        "ai_operations_unlogged": 0,
        "logging_score": 60 if logging_patterns else 50,
    }

    return {
        "language": "cpp",
        "imports": imports,
        "ai_imports": ai_imports,
        "has_ai_code": has_ai_code,
        "context": context,
        "function_defs": function_defs,
        "class_defs": class_defs,
        "is_test_file": is_test_file,
        "data_flows": [],
        "oversight": oversight,
        "logging": logging_info,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyse_file(content: str, filename: str, language: Optional[str] = None) -> dict:
    """Analyse a source file and return a unified result dict.

    Parameters
    ----------
    content : str
        The source code to analyse.
    filename : str
        The filename (used for language detection if *language* is None).
    language : str, optional
        Force a specific language ("python", "javascript", "typescript").
        If None, detected from *filename*.

    Returns
    -------
    dict
        Unified analysis result with keys: language, imports, ai_imports,
        has_ai_code, context, function_defs, class_defs, is_test_file,
        data_flows, oversight, logging.
    """
    if language is None:
        language = detect_language(filename)

    if language is None:
        return {
            "language": "unknown",
            "imports": [],
            "ai_imports": [],
            "has_ai_code": False,
            "context": "not_parseable",
            "function_defs": [],
            "class_defs": [],
            "is_test_file": False,
            "data_flows": [],
            "oversight": {
                "has_oversight": False,
                "oversight_patterns": [],
                "automated_decisions": [],
                "oversight_score": 0,
            },
            "logging": {
                "has_logging": False,
                "logging_patterns": [],
                "ai_operations_logged": 0,
                "ai_operations_unlogged": 0,
                "logging_score": 0,
            },
        }

    if language == "python":
        return _analyse_python(content, filename)
    elif language in ("javascript", "typescript"):
        return _analyse_js_ts(content, filename)
    elif language == "java":
        return _analyse_java_regex(content)
    elif language == "go":
        return _analyse_go_regex(content)
    elif language == "rust":
        return _analyse_rust_regex(content)
    elif language in ("c", "cpp"):
        return _analyse_cpp_regex(content)
    else:
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
            "oversight": {
                "has_oversight": False,
                "oversight_patterns": [],
                "automated_decisions": [],
                "oversight_score": 0,
            },
            "logging": {
                "has_logging": False,
                "logging_patterns": [],
                "ai_operations_logged": 0,
                "ai_operations_unlogged": 0,
                "logging_score": 0,
            },
        }


def _build_cross_file_chains(results: List[dict]) -> List[dict]:
    """Identify cross-file AI call chains from per-file analysis results.

    After all files are analysed individually, this post-processing step links
    AI call sites to the functions that invoke them from other files, enabling
    traceability across module boundaries (Article 12).

    Only Python files are linked (full AST available). JS/TS and other languages
    contribute as AI call sources but are not traversed for caller relationships.

    Returns
    -------
    list[dict]
        Each entry describes one AI call chain::

            {
                "ai_file": "services/llm_client.py",
                "ai_call": "openai.chat.completions.create",
                "ai_call_line": 42,
                "propagated_to": [
                    {"file": "api/views.py", "function": "handle_request", "line": 18}
                ]
            }
    """
    # Step 1: build module-name → file path index (Python only, relative paths)
    # e.g. "services/llm_client.py" → module key "services.llm_client"
    module_to_file: Dict[str, str] = {}
    for r in results:
        if r.get("language") != "python":
            continue
        rel = r.get("file", "")
        # Convert path separators and strip .py → dotted module name
        mod = rel.replace("/", ".").replace("\\", ".")
        if mod.endswith(".py"):
            mod = mod[:-3]
        # Also register the bare filename stem for single-dir imports
        stem = Path(rel).stem
        module_to_file[mod] = rel
        module_to_file[stem] = rel

    # Step 2: build file → set of function names it defines
    file_functions: Dict[str, set] = {}
    for r in results:
        fpath = r.get("file", "")
        names = {f["name"] for f in r.get("function_defs", [])}
        file_functions[fpath] = names

    # Step 3: collect files that make direct AI calls (have non-empty data_flows
    # or have ai_imports used in function bodies)
    ai_call_files: Dict[str, List[dict]] = {}  # file → list of call dicts
    for r in results:
        fpath = r.get("file", "")
        flows = r.get("data_flows", [])
        if flows:
            ai_call_files[fpath] = [
                {"source": f["source"], "line": f.get("source_line", 0)}
                for f in flows
            ]
        elif r.get("ai_imports"):
            # File has AI imports but data_flows not available (non-Python / regex path)
            ai_call_files[fpath] = [
                {"source": imp, "line": 0} for imp in r["ai_imports"]
            ]

    if not ai_call_files:
        return []

    # Step 4: for each Python file, check its imports against ai_call_files.
    # If it imports a module that makes AI calls, record the calling functions.
    chains: List[dict] = []
    seen_chains: set = set()

    for r in results:
        if r.get("language") != "python":
            continue
        caller_file = r.get("file", "")
        imports = r.get("imports", [])
        function_defs = r.get("function_defs", [])

        for imp in imports:
            # Normalise import: "from services.llm_client import chat" → "services.llm_client"
            parts = imp.split(".")
            # Try progressively shorter prefixes to match module keys
            for length in range(len(parts), 0, -1):
                mod_key = ".".join(parts[:length])
                if mod_key in module_to_file:
                    target_file = module_to_file[mod_key]
                    if target_file in ai_call_files and target_file != caller_file:
                        for call in ai_call_files[target_file]:
                            chain_key = (caller_file, target_file, call["source"])
                            if chain_key in seen_chains:
                                continue
                            seen_chains.add(chain_key)

                            # Record which functions in the caller file are
                            # plausible entry points (all non-test functions,
                            # since we can't resolve which one calls the import
                            # without full call-graph analysis)
                            propagated = [
                                {
                                    "file": caller_file,
                                    "function": fn["name"],
                                    "line": fn.get("line", 0),
                                }
                                for fn in function_defs
                                if not fn.get("is_test", False)
                            ]

                            chains.append({
                                "ai_file": target_file,
                                "ai_call": call["source"],
                                "ai_call_line": call["line"],
                                "propagated_to": propagated,
                            })
                    break

    return chains


def analyse_project(project_path: str) -> List[dict]:
    """Walk a directory and analyse all supported source files.

    Parameters
    ----------
    project_path : str
        Path to the project root directory.

    Returns
    -------
    list[dict]
        List of analysis results, one per file. Each dict includes an extra
        "file" key with the relative file path. A top-level
        ``"call_chains"`` key is appended to the first result (index 0) so
        callers can retrieve cross-file chains without a separate return value.
    """
    results = []
    root = Path(project_path)

    # Directories to skip
    skip_dirs = {
        "node_modules", ".git", "__pycache__", ".venv", "venv",
        "env", ".env", "dist", "build", ".next", ".nuxt",
        "coverage", ".nyc_output", ".tox", ".mypy_cache",
        ".pytest_cache", ".ruff_cache",
    }

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skipped directories in-place
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]

        for fname in filenames:
            lang = detect_language(fname)
            if lang is None:
                continue

            filepath = Path(dirpath) / fname
            try:
                content = filepath.read_text(encoding="utf-8", errors="replace")
            except (OSError, PermissionError):
                continue  # unreadable file; skip

            result = analyse_file(content, fname, language=lang)
            result["file"] = str(filepath.relative_to(root))
            results.append(result)

    # Post-process: build cross-file call chains
    if results:
        chains = _build_cross_file_chains(results)
        results[0]["call_chains"] = chains

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _format_text(result: dict) -> str:
    """Format a single analysis result as human-readable text."""
    lines = []
    lines.append(f"Language: {result.get('language', 'unknown')}")
    if result.get("file"):
        lines.append(f"File: {result['file']}")
    lines.append(f"Context: {result.get('context', 'unknown')}")
    lines.append(f"Has AI code: {result.get('has_ai_code', False)}")
    lines.append(f"Is test file: {result.get('is_test_file', False)}")

    if result.get("imports"):
        lines.append(f"Imports ({len(result['imports'])}): {', '.join(result['imports'][:20])}")
    if result.get("ai_imports"):
        lines.append(f"AI imports: {', '.join(result['ai_imports'])}")
    if result.get("function_defs"):
        names = [f["name"] for f in result["function_defs"][:10]]
        lines.append(f"Functions ({len(result['function_defs'])}): {', '.join(names)}")
    if result.get("class_defs"):
        names = [c["name"] for c in result["class_defs"][:10]]
        lines.append(f"Classes ({len(result['class_defs'])}): {', '.join(names)}")
    if result.get("data_flows"):
        lines.append(f"Data flows: {len(result['data_flows'])} traced")
    if result.get("oversight"):
        o = result["oversight"]
        lines.append(f"Oversight score: {o.get('oversight_score', 0)}/100")
    if result.get("logging"):
        lg = result["logging"]
        lines.append(f"Logging score: {lg.get('logging_score', 0)}/100")

    return "\n".join(lines)


def main() -> None:
    """CLI entry point for the unified AST engine."""
    parser = argparse.ArgumentParser(
        description="Unified multi-language AST analysis for EU AI Act compliance.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Analyse a single file")
    group.add_argument("--project", help="Analyse all supported files in a directory")
    parser.add_argument(
        "--format", choices=["json", "text"], default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--language", choices=["python", "javascript", "typescript"],
        help="Force language (auto-detected from extension by default)",
    )

    args = parser.parse_args()

    if args.file:
        filepath = Path(args.file)
        if not filepath.is_file():
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        content = filepath.read_text(encoding="utf-8", errors="replace")
        result = analyse_file(content, filepath.name, language=args.language)
        result["file"] = str(filepath)

        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            print(_format_text(result))

    elif args.project:
        project_dir = Path(args.project)
        if not project_dir.is_dir():
            print(f"Error: directory not found: {args.project}", file=sys.stderr)
            sys.exit(1)
        results = analyse_project(str(project_dir))

        if args.format == "json":
            print(json.dumps(results, indent=2))
        else:
            for i, result in enumerate(results):
                if i > 0:
                    print("\n" + "=" * 50)
                print(_format_text(result))

            print(f"\n--- {len(results)} files analysed ---")
            ai_files = sum(1 for r in results if r.get("has_ai_code"))
            print(f"Files with AI code: {ai_files}")


if __name__ == "__main__":
    main()
