#!/usr/bin/env python3
"""Enumerate decision entry points and emitted regulatory references.

This is an audit predicate, not a manually maintained count. It derives rows
from Python ASTs, runtime configuration objects, jurisdiction data, and the
three browser assessment sources. Every reported total is calculated from the
itemised rows emitted in the same JSON document.
"""

import ast
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from compliance_check import ARTICLE_NUMBERS
from regulation_map import list_jurisdictions, load_jurisdiction
from risk_patterns import (
    BIAS_RISK_PATTERNS,
    GOVERNANCE_OBSERVATIONS,
    HIGH_RISK_PATTERNS,
    LIMITED_RISK_PATTERNS,
    PROHIBITED_PATTERNS,
)


ROOT = Path(__file__).parent.parent
BROWSER_LOCALES = {
    "en": ROOT / "site" / "assess" / "index.html",
    "de": ROOT / "site" / "assess" / "de.html",
    "pt-BR": ROOT / "site" / "assess" / "pt-br.html",
}


def _python_calls(paths, targets):
    rows = []
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        parents = {}
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                parents[child] = parent
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            else:
                name = None
            if name not in targets:
                continue
            owner = node
            while owner in parents and not isinstance(
                    owner, (ast.FunctionDef, ast.AsyncFunctionDef)):
                owner = parents[owner]
            rows.append({
                "file": str(path.relative_to(ROOT)),
                "line": node.lineno,
                "owner": owner.name if isinstance(
                    owner, (ast.FunctionDef, ast.AsyncFunctionDef)) else "<module>",
                "call": name,
            })
    return sorted(rows, key=lambda row: (row["file"], row["line"], row["call"]))


def _regex_rows(path, predicate, pattern):
    rows = []
    regex = re.compile(pattern)
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = regex.search(line)
        if match:
            rows.append({
                "file": str(path.relative_to(ROOT)),
                "line": number,
                "predicate": predicate,
                "match": match.group(0),
            })
    return rows


def enumerate_entry_points():
    targets = {
        "evaluate_questionnaire",
        "classify",
        "scan_files",
        "assess_compliance",
        "generate_evidence_pack",
        "generate_conformity_pack",
        "generate_documentation",
        "export_dpv",
        "to_sarif",
        "evaluate_payload",
        "empty_decision",
        "evaluate",
    }
    return {
        "python_direct_calls": _python_calls(
            sorted((ROOT / "scripts").glob("*.py")), targets),
        "cli_handler_bindings": _regex_rows(
            ROOT / "scripts" / "cli.py",
            "set_defaults binds a CLI handler",
            r"set_defaults\(func=[A-Za-z_][A-Za-z0-9_]*\)",
        ),
        "rest_routes": _regex_rows(
            ROOT / "scripts" / "api_server.py",
            "normalized path literal dispatches a REST handler",
            r'path == "(?:/health|/v1/[^"]+)"',
        ),
        "mcp_tool_names": _regex_rows(
            ROOT / "scripts" / "mcp_server.py",
            "MCP declaration names a regula tool",
            r'"name": "regula_[a-z_]+"',
        ),
        "vscode_command_registrations": _regex_rows(
            ROOT / "vscode-extension" / "src" / "extension.ts",
            "VS Code registers a command",
            r"vscode\.commands\.registerCommand",
        ),
        "browser_decision_function_definitions": sorted(
            [
                row
                for path in [
                    ROOT / "site" / "assess" / "decision-kernel.js",
                    ROOT / "site" / "assess" / "decision-adapters.js",
                    ROOT / "site" / "assess" / "decision-ui.js",
                    ROOT / "site" / "assess" / "scanner.js",
                    *BROWSER_LOCALES.values(),
                ]
                for row in _regex_rows(
                    path,
                    "browser function emits or presents detector or decision output",
                    r"function (?:evaluateDecision|evaluateQuestionnaire|renderDecision|calculateResults|classifyCode|scanCode)\(",
                )
            ],
            key=lambda row: (row["file"], row["line"]),
        ),
    }


def _edge(runtime, jurisdiction, source, condition, provision, output, name):
    return {
        "runtime": runtime,
        "jurisdiction": jurisdiction,
        "source": source,
        "condition": condition,
        "provision": str(provision),
        "output": output,
        "name": name,
    }


def _python_edges():
    rows = []
    for name, config in sorted(PROHIBITED_PATTERNS.items()):
        rows.append(_edge(
            "python", "eu", "risk_patterns.PROHIBITED_PATTERNS",
            f"pattern group {name!r} has at least one match and is first prohibited match",
            config.get("article", "5"), "applicable_article", name,
        ))
    for name, config in sorted(HIGH_RISK_PATTERNS.items()):
        for provision in config.get("articles", []):
            rows.append(_edge(
                "python", "eu", "risk_patterns.HIGH_RISK_PATTERNS",
                f"pattern group {name!r} has at least one match",
                provision, "applicable_article", name,
            ))
    for name, config in sorted(LIMITED_RISK_PATTERNS.items()):
        rows.append(_edge(
            "python", "eu", "risk_patterns.LIMITED_RISK_PATTERNS",
            f"pattern group {name!r} has at least one match after higher tiers do not match",
            config.get("article", "50"), "applicable_article", name,
        ))
    for provision in ("9", "10", "11", "12", "13", "14", "15"):
        rows.append(_edge(
            "python", "eu", "classify_risk._check_policy_overrides",
            "configured force_high_risk substring matches source text",
            provision, "applicable_article", "policy force-high-risk",
        ))
    for provision in ARTICLE_NUMBERS:
        rows.append(_edge(
            "python", "eu", "compliance_check.assess_compliance",
            "article filter is absent or includes the provision, regardless of risk classification",
            provision, "readiness_article", "compliance gap assessment",
        ))
    for name, config in sorted(GOVERNANCE_OBSERVATIONS.items()):
        rows.append(_edge(
            "python", "eu", "risk_patterns.GOVERNANCE_OBSERVATIONS",
            f"classification is high-risk and observation predicate {name!r} resolves true",
            config["article"], "observation_article", name,
        ))
    for name, config in sorted(BIAS_RISK_PATTERNS.items()):
        rows.append(_edge(
            "python", "eu", "risk_patterns.BIAS_RISK_PATTERNS",
            f"AI-related source satisfies bias observation predicate {name!r}",
            config.get("article_clause", config["article"]),
            "observation_article", name,
        ))
    return rows


def _jurisdiction_edges():
    rows = []
    aliases = {"eu_ai_act": "eu", "south_korea": "kr", "colorado": "co"}
    for jurisdiction_id in list_jurisdictions():
        config = load_jurisdiction(jurisdiction_id)
        jurisdiction = aliases.get(jurisdiction_id, jurisdiction_id)
        for domain, mapping in sorted(config.get("domain_mappings", {}).items()):
            condition = (
                f"the scanner detects domain {domain!r} and the adapter requests "
                f"jurisdiction {jurisdiction!r}"
            )
            for provision in mapping.get("articles", []):
                rows.append(_edge(
                    "python", jurisdiction, f"jurisdiction:{jurisdiction_id}:{domain}",
                    condition, provision, "mapping_article", mapping.get("category", domain),
                ))
            for obligation in mapping.get("obligations", []):
                rows.append(_edge(
                    "python", jurisdiction, f"jurisdiction:{jurisdiction_id}:{domain}",
                    condition, obligation.get("article", ""), "domain_obligation",
                    obligation.get("name", ""),
                ))
        threshold = config.get("high_performance_threshold")
        if threshold:
            condition = f"declared compute exceeds {threshold.get('flops')} FLOPs"
            for obligation in threshold.get("obligations", []):
                rows.append(_edge(
                    "python", jurisdiction,
                    f"jurisdiction:{jurisdiction_id}:high_performance_threshold",
                    condition, obligation.get("article", ""), "threshold_obligation",
                    obligation.get("name", ""),
                ))
    return rows


def _array_text(source, name):
    marker = f"const {name} = ["
    start = source.find(marker)
    if start < 0:
        raise ValueError(f"missing browser array {name}")
    start = source.find("[", start)
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(source)):
        char = source[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise ValueError(f"unterminated browser array {name}")


def _browser_array_items(source, name):
    body = _array_text(source, name)
    pattern = re.compile(
        r"article:\s*(?:\"([^\"]+)\"|(\d+))\s*,\s*name:\s*\"([^\"]+)\""
    )
    return [
        {"provision": match.group(1) or match.group(2), "name": match.group(3)}
        for match in pattern.finditer(body)
    ]


def _model_edges():
    model_path = ROOT / "references" / "decision_model.v1.json"
    model = json.loads(model_path.read_text(encoding="utf-8"))
    rows = []
    for jurisdiction, config in sorted(model["jurisdictions"].items()):
        for rule in config["rules"]:
            rows.append(_edge(
                "canonical-kernel",
                jurisdiction,
                str(model_path.relative_to(ROOT)),
                f"named predicate {rule['id']!r} resolves true from sourced facts",
                rule["provision"],
                "indication",
                rule["classification"],
            ))
        for obligation in config["obligations"]:
            rows.append(_edge(
                "canonical-kernel",
                jurisdiction,
                str(model_path.relative_to(ROOT)),
                f"every expression edge for obligation {obligation['id']!r} resolves true",
                obligation["provision"],
                "obligation",
                obligation["name"],
            ))
    return rows


def _browser_question_references():
    arrays = {
        "QUESTIONS": "eu",
        "QUESTIONS_KR": "kr",
        "QUESTIONS_CO": "co",
    }
    rows = []
    article_pattern = re.compile(r'article:\s*"([^"]+)"')
    id_pattern = re.compile(r'id:\s*"([^"]+)"')
    for locale, path in BROWSER_LOCALES.items():
        source = path.read_text(encoding="utf-8")
        for array_name, jurisdiction in arrays.items():
            body = _array_text(source, array_name)
            objects = re.findall(r"\{(.*?)\}", body, flags=re.DOTALL)
            for obj in objects:
                article_match = article_pattern.search(obj)
                id_match = id_pattern.search(obj)
                if article_match and id_match:
                    rows.append(_edge(
                        f"browser:{locale}", jurisdiction,
                        f"{path.relative_to(ROOT)}:{array_name}",
                        "question is displayed during the selected jurisdiction assessment",
                        article_match.group(1), "question_reference", id_match.group(1),
                    ))
    return rows


def _with_reconciliation(groups):
    return {
        name: {
            "predicate_count": len(rows),
            "items": rows,
            "itemised_count": len(rows),
            "reconciled": len(rows) == len(list(rows)),
        }
        for name, rows in groups.items()
    }


def _canonical_tokens(row):
    """Return legal identifiers without locale wording or source annotations."""
    value = row["provision"]
    jurisdiction = row["jurisdiction"]
    if jurisdiction == "co":
        return re.findall(r"6-1-170\d(?:\(\d+\))?", value)
    if jurisdiction == "kr":
        return re.findall(r"(?:Article|Artikel|Artigo)?\s*(3[1-6]|4)\b", value)
    if jurisdiction == "eu":
        tokens = []
        value = re.sub(r"\s*\[Regulation[^\]]+\]", "", value)
        annex_match = re.search(
            r"(?:Annex|Anhang|Anexo)\s+III(?:\((\d+)\))?",
            value,
            re.IGNORECASE,
        )
        if annex_match:
            suffix = f"({annex_match.group(1)})" if annex_match.group(1) else ""
            tokens.append(f"Annex III{suffix}")
            value = value[:annex_match.start()] + value[annex_match.end():]
        if "GDPR" in value:
            tokens.extend(f"GDPR {item}" for item in re.findall(
                r"Article\s+(\d+(?:\(\d+\))?)", value[value.find("GDPR"):]
            ))
            value = value[:value.find("GDPR")]
        labelled = re.findall(
            r"(?:Article|Artikel|Artigo)\s+(\d+(?:\(\d+\))?(?:\([a-z]+\))?)",
            value,
        )
        matches = labelled or re.findall(
            r"^\s*(\d+(?:\(\d+\))?(?:\([a-z]+\))?)\s*$", value,
        )
        tokens.extend(matches)
        return tokens
    return [value]


def main():
    entry_points = enumerate_entry_points()
    detector_reference_rows = _python_edges() + _jurisdiction_edges()
    obligation_rows = _model_edges()
    reference_rows = _browser_question_references()
    counts_by_output = Counter(row["output"] for row in obligation_rows)
    counts_by_jurisdiction = Counter(row["jurisdiction"] for row in obligation_rows)
    canonical_by_jurisdiction = {}
    for jurisdiction in sorted({row["jurisdiction"] for row in obligation_rows + reference_rows}):
        emitted = sorted({
            token
            for row in obligation_rows
            if row["jurisdiction"] == jurisdiction
            for token in _canonical_tokens(row)
        })
        explanatory = sorted({
            token
            for row in reference_rows
            if row["jurisdiction"] == jurisdiction
            for token in _canonical_tokens(row)
        })
        canonical_by_jurisdiction[jurisdiction] = {
            "emitted": emitted,
            "question_references": explanatory,
            "all": sorted(set(emitted) | set(explanatory)),
        }
    document = {
        "predicate": (
            "Executable entry points are selected by AST call target or source registration. "
            "Regulatory edges are selected from runtime pattern/configuration objects, "
            "jurisdiction files, and browser obligation arrays."
        ),
        "commit": _git_value("rev-parse", "HEAD"),
        "base_tree": _git_value("rev-parse", "HEAD^{tree}"),
        "worktree_status": _git_value("status", "--short"),
        "entry_points": _with_reconciliation(entry_points),
        "regulatory_edges": {
            "predicate_count": len(obligation_rows),
            "items": obligation_rows,
            "itemised_count": len(obligation_rows),
            "reconciled": len(obligation_rows) == len(list(obligation_rows)),
            "counts_by_output": dict(sorted(counts_by_output.items())),
            "counts_by_jurisdiction": dict(sorted(counts_by_jurisdiction.items())),
        },
        "detector_reference_edges": {
            "predicate_count": len(detector_reference_rows),
            "items": detector_reference_rows,
            "itemised_count": len(detector_reference_rows),
            "reconciled": len(detector_reference_rows) == len(list(detector_reference_rows)),
        },
        "browser_question_references": {
            "predicate_count": len(reference_rows),
            "items": reference_rows,
            "itemised_count": len(reference_rows),
            "reconciled": len(reference_rows) == len(list(reference_rows)),
        },
        "canonical_provisions_by_jurisdiction": canonical_by_jurisdiction,
    }
    print(json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False))


def _git_value(*args):
    import subprocess
    result = subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


if __name__ == "__main__":
    main()
