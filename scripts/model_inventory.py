#!/usr/bin/env python3
"""
Regula Model Inventory

Scans a project's source code and config files for references to specific
AI model identifiers (e.g. "gpt-4o", "claude-3-5-sonnet-20241022",
"llama-3.1-8b") and annotates each with EU AI Act GPAI tier notes.

Detection is heuristic static analysis. It does not know whether a model
is actually deployed — only that the identifier appears in the codebase.
This is shift-left model discovery, not a live organisational registry.

EU AI Act notes are informational flags for human review, not legal
conclusions. Article 53 obligations have been in force since 2 August 2025.
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Known-models catalogue
# ---------------------------------------------------------------------------
# Each entry: (provider, model_id, gpai_tier, eu_note)
# gpai_tier: "frontier" | "open_weight" | "unknown"

_MODEL_CATALOGUE = [
    # OpenAI — frontier
    ("OpenAI", "gpt-4o", "frontier",
     "GPAI obligations under Art 53. Systemic risk assessment required (Art 51 — 10²⁵ FLOPs presumption)."),
    ("OpenAI", "gpt-4o-mini", "frontier",
     "GPAI obligations under Art 53. Verify systemic risk threshold (Art 51)."),
    ("OpenAI", "gpt-4-turbo", "frontier",
     "GPAI obligations under Art 53. Systemic risk assessment required (Art 51 — 10²⁵ FLOPs presumption)."),
    ("OpenAI", "gpt-4", "frontier",
     "GPAI obligations under Art 53. Systemic risk assessment required (Art 51)."),
    ("OpenAI", "gpt-3.5-turbo", "frontier",
     "GPAI obligations under Art 53. Likely below systemic risk threshold — verify."),
    ("OpenAI", "o1", "frontier",
     "GPAI obligations under Art 53. Systemic risk assessment required (Art 51)."),
    ("OpenAI", "o1-mini", "frontier",
     "GPAI obligations under Art 53. Verify systemic risk threshold (Art 51)."),
    ("OpenAI", "o3", "frontier",
     "GPAI obligations under Art 53. Systemic risk assessment required (Art 51)."),
    ("OpenAI", "o3-mini", "frontier",
     "GPAI obligations under Art 53. Verify systemic risk threshold (Art 51)."),
    # Anthropic — frontier
    ("Anthropic", "claude-3-5-sonnet", "frontier",
     "GPAI obligations under Art 53. Systemic risk assessment required (Art 51)."),
    ("Anthropic", "claude-3-5-haiku", "frontier",
     "GPAI obligations under Art 53. Verify systemic risk threshold (Art 51)."),
    ("Anthropic", "claude-3-opus", "frontier",
     "GPAI obligations under Art 53. Systemic risk assessment required (Art 51)."),
    ("Anthropic", "claude-3-sonnet", "frontier",
     "GPAI obligations under Art 53. Verify systemic risk threshold (Art 51)."),
    ("Anthropic", "claude-3-haiku", "frontier",
     "GPAI obligations under Art 53. Verify systemic risk threshold (Art 51)."),
    # Google — frontier
    ("Google", "gemini-1.5-pro", "frontier",
     "GPAI obligations under Art 53. Systemic risk assessment required (Art 51)."),
    ("Google", "gemini-2.0-flash", "frontier",
     "GPAI obligations under Art 53. Verify systemic risk threshold (Art 51)."),
    ("Google", "gemini-1.5-flash", "frontier",
     "GPAI obligations under Art 53. Verify systemic risk threshold (Art 51)."),
    ("Google", "gemini-pro", "frontier",
     "GPAI obligations under Art 53. Verify systemic risk threshold (Art 51)."),
    # Mistral — frontier
    ("Mistral AI", "mistral-large", "frontier",
     "GPAI obligations under Art 53. Verify systemic risk threshold (Art 51)."),
    ("Mistral AI", "mistral-medium", "frontier",
     "GPAI obligations under Art 53. Verify systemic risk threshold (Art 51)."),
    ("Mistral AI", "mixtral-8x22b", "frontier",
     "GPAI obligations under Art 53. Verify systemic risk threshold (Art 51)."),
    # Cohere — frontier
    ("Cohere", "command-r-plus", "frontier",
     "GPAI obligations under Art 53. Verify systemic risk threshold (Art 51)."),
    ("Cohere", "command-r", "frontier",
     "GPAI obligations under Art 53. Verify systemic risk threshold (Art 51)."),
    # Meta — open-weight
    ("Meta", "llama-3.1-405b", "open_weight",
     "Art 53(1)(a)+(b) may be exempt if freely available open-source (Art 53(2)). Copyright policy + training data summary still required under Art 53(1)(c)+(d)."),
    ("Meta", "llama-3.1-70b", "open_weight",
     "Art 53(1)(a)+(b) may be exempt if freely available open-source (Art 53(2)). Copyright policy + training data summary still required under Art 53(1)(c)+(d)."),
    ("Meta", "llama-3.1-8b", "open_weight",
     "Art 53(1)(a)+(b) may be exempt if freely available open-source (Art 53(2)). Copyright policy + training data summary still required under Art 53(1)(c)+(d)."),
    ("Meta", "llama-3-70b", "open_weight",
     "Art 53(1)(a)+(b) may be exempt if freely available open-source (Art 53(2)). Copyright policy + training data summary still required."),
    ("Meta", "llama-3-8b", "open_weight",
     "Art 53(1)(a)+(b) may be exempt if freely available open-source (Art 53(2)). Copyright policy + training data summary still required."),
    ("Meta", "llama-2-70b", "open_weight",
     "Art 53(1)(a)+(b) may be exempt if freely available open-source (Art 53(2)). Copyright policy + training data summary still required."),
    # Mistral — open-weight
    ("Mistral AI", "mistral-7b", "open_weight",
     "Art 53(1)(a)+(b) may be exempt if freely available open-source (Art 53(2)). Copyright policy + training data summary still required."),
    ("Mistral AI", "mixtral-8x7b", "open_weight",
     "Art 53(1)(a)+(b) may be exempt if freely available open-source (Art 53(2)). Copyright policy + training data summary still required."),
    # Microsoft — open-weight
    ("Microsoft", "phi-3", "open_weight",
     "Art 53(1)(a)+(b) may be exempt if freely available open-source (Art 53(2)). Copyright policy + training data summary still required."),
    ("Microsoft", "phi-4", "open_weight",
     "Art 53(1)(a)+(b) may be exempt if freely available open-source (Art 53(2)). Copyright policy + training data summary still required."),
    # Google — open-weight
    ("Google", "gemma-2", "open_weight",
     "Art 53(1)(a)+(b) may be exempt if freely available open-source (Art 53(2)). Copyright policy + training data summary still required."),
    ("Google", "gemma-7b", "open_weight",
     "Art 53(1)(a)+(b) may be exempt if freely available open-source (Art 53(2)). Copyright policy + training data summary still required."),
    # Alibaba — open-weight
    ("Alibaba", "qwen-2.5", "open_weight",
     "Art 53(1)(a)+(b) may be exempt if freely available open-source (Art 53(2)). Copyright policy + training data summary still required."),
    # DeepSeek — open-weight
    ("DeepSeek", "deepseek-r1", "open_weight",
     "Art 53(1)(a)+(b) may be exempt if freely available open-source (Art 53(2)). Copyright policy + training data summary still required."),
    # TII — open-weight
    ("TII", "falcon-40b", "open_weight",
     "Art 53(1)(a)+(b) may be exempt if freely available open-source (Art 53(2)). Copyright policy + training data summary still required."),
]

# Scannable extensions
_SCAN_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
    ".yaml", ".yml", ".json", ".toml", ".env", ".cfg", ".ini",
}
_SKIP_DIRS = {".git", "node_modules", "__pycache__", "venv", ".venv", "dist", "build"}


def scan_for_models(project_path: str) -> dict:
    """Scan a project directory for AI model identifier references.

    Returns:
        {
            "models": [
                {
                    "provider": str,
                    "model_id": str,
                    "gpai_tier": "frontier" | "open_weight" | "unknown",
                    "eu_note": str,
                    "occurrences": [{"file": str, "line": int}]
                }
            ],
            "summary": {"total": int, "frontier": int, "open_weight": int, "unknown": int}
        }
    """
    project = Path(project_path).resolve()
    # Map model_id -> {"entry": catalogue tuple, "occurrences": list}
    found: dict[str, dict] = {}

    for filepath in _walk_project(project):
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(filepath.relative_to(project))
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            for provider, model_id, gpai_tier, eu_note in _MODEL_CATALOGUE:
                # Match model_id as a quoted string or from_pretrained argument
                pattern = r'["\']' + re.escape(model_id) + r'["\']'
                if re.search(pattern, line, re.IGNORECASE):
                    if model_id not in found:
                        found[model_id] = {
                            "provider": provider,
                            "model_id": model_id,
                            "gpai_tier": gpai_tier,
                            "eu_note": eu_note,
                            "occurrences": [],
                        }
                    # Avoid duplicate file:line entries
                    occ = {"file": rel, "line": i}
                    if occ not in found[model_id]["occurrences"]:
                        found[model_id]["occurrences"].append(occ)

    models = list(found.values())
    summary = {
        "total": len(models),
        "frontier": sum(1 for m in models if m["gpai_tier"] == "frontier"),
        "open_weight": sum(1 for m in models if m["gpai_tier"] == "open_weight"),
        "unknown": sum(1 for m in models if m["gpai_tier"] == "unknown"),
    }
    return {"models": models, "summary": summary}


def _walk_project(project: Path):
    """Yield scannable files, skipping common non-source directories."""
    for filepath in project.rglob("*"):
        if not filepath.is_file():
            continue
        if any(part in _SKIP_DIRS for part in filepath.parts):
            continue
        if filepath.suffix.lower() in _SCAN_EXTENSIONS:
            yield filepath


def format_table(result: dict) -> str:
    """Format model inventory as a human-readable table."""
    models = result["models"]
    summary = result["summary"]
    if not models:
        return "No AI model identifiers detected in this project."
    lines = [
        f"{'Provider':<15} {'Model':<35} {'GPAI Tier':<12} {'Files':<5}",
        f"{'-'*15} {'-'*35} {'-'*12} {'-'*5}",
    ]
    for m in sorted(models, key=lambda x: (x["gpai_tier"], x["provider"], x["model_id"])):
        files_count = len(set(o["file"] for o in m["occurrences"]))
        tier_label = m["gpai_tier"].replace("_", "-")
        lines.append(f"{m['provider']:<15} {m['model_id']:<35} {tier_label:<12} {files_count:<5}")
    lines.append("")
    lines.append(f"Total: {summary['total']} model(s) — {summary['frontier']} frontier, {summary['open_weight']} open-weight, {summary['unknown']} unknown")
    lines.append("Notes are flags for human review, not legal conclusions. Art 53 obligations in force 2 August 2025.")
    return "\n".join(lines)


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="Regula model inventory — scan codebase for AI model references")
    parser.add_argument("path", nargs="?", default=".", help="Path to scan (default: .)")
    parser.add_argument("--format", "-f", choices=["table", "json"], default="table")
    args = parser.parse_args(argv)

    result = scan_for_models(args.path)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_table(result))


if __name__ == "__main__":
    main()
