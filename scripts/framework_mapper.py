# regula-ignore
#!/usr/bin/env python3
"""
Framework Mapper — Cross-framework compliance mapping for EU AI Act articles.

Maps EU AI Act articles (9-15) to equivalent controls in:
  - NIST AI RMF 1.0
  - ISO/IEC 42001:2023
  - NIST CSF 2.0
  - SOC 2 TSC (AICPA 2017)
  - ISO 27001:2022
  - OWASP LLM Top 10 (2025)
  - MITRE ATLAS
  - LGPD (Lei Geral de Proteção de Dados, Lei 13.709/2018 — Brasil)
  - Marco Legal da IA (PL 2338/2023 — Brasil, aprovado pelo Senado em dezembro/2024)

Uses references/framework_crosswalk.yaml as the data source.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from degradation import check_optional

# Cache for loaded crosswalk data
_crosswalk_cache: dict | None = None

# Path to the crosswalk file (relative to repo root)
_CROSSWALK_PATH = Path(__file__).parent.parent / "references" / "framework_crosswalk.yaml"

# Mapping from article number to crosswalk key
_ARTICLE_KEY_MAP = {
    "9": "article_9",
    "10": "article_10",
    "11": "article_11",
    "12": "article_12",
    "13": "article_13",
    "14": "article_14",
    "15": "article_15",
}

# Supported framework filter names
_FRAMEWORK_KEYS = {
    "eu-ai-act": "eu_ai_act",
    "nist-ai-rmf": "nist_ai_rmf",
    "iso-42001": "iso_42001",
    "nist-csf": "nist_csf",
    "soc2": "soc2",
    "iso-27001": "iso_27001",
    "owasp-llm-top10": "owasp_llm_top10",
    "mitre-atlas": "mitre_atlas",
    "lgpd": "lgpd",
    "marco-legal-ia": "marco_legal_ia",
}


def _load_crosswalk() -> dict:
    """
    Load references/framework_crosswalk.yaml.

    Tries pyyaml first; falls back to _parse_yaml_fallback from classify_risk.
    Result is cached after first load.
    """
    global _crosswalk_cache
    if _crosswalk_cache is not None:
        return _crosswalk_cache

    content = _CROSSWALK_PATH.read_text(encoding="utf-8")

    if check_optional("yaml", "using fallback YAML parser", "pip install pyyaml"):
        import yaml
        data = yaml.safe_load(content) or {}
    else:
        from classify_risk import _parse_yaml_fallback
        data = _parse_yaml_fallback(content)

    _crosswalk_cache = data
    return _crosswalk_cache


def map_to_frameworks(
    articles: list,
    frameworks: list = None,
) -> dict:
    """
    Map EU AI Act article numbers to cross-framework controls.

    Parameters
    ----------
    articles : list[str]
        Article numbers to map, e.g. ["9", "14"].
    frameworks : list[str] | None
        Framework filter. Accepts "eu-ai-act", "nist-ai-rmf", "iso-42001",
        "owasp-llm-top10", or "all". None or ["all"] returns all frameworks.

    Returns
    -------
    dict
        Keys are article numbers; values are dicts with framework sub-dicts.

    Example
    -------
    {
        "9": {
            "eu_ai_act": {"article": "9", "title": "...", "requirement": "..."},
            "nist_ai_rmf": {"functions": [...], "subcategories": [...]},
            "iso_42001": {"controls": [...]},
        }
    }
    """
    crosswalk = _load_crosswalk()
    mappings = crosswalk.get("mappings", {})

    # Determine which framework keys to include
    if frameworks is None or frameworks == ["all"] or "all" in (frameworks or []):
        include = list(_FRAMEWORK_KEYS.values())  # all three
    else:
        include = []
        for f in frameworks:
            key = _FRAMEWORK_KEYS.get(f)
            if key:
                include.append(key)
            else:
                # Accept internal keys directly (e.g. "nist_ai_rmf")
                if f in _FRAMEWORK_KEYS.values():
                    include.append(f)

    result = {}
    for article in articles:
        article = str(article)
        crosswalk_key = _ARTICLE_KEY_MAP.get(article)
        if crosswalk_key is None:
            result[article] = {}
            continue

        article_data = mappings.get(crosswalk_key, {})
        mapped = {}
        for fw_key in include:
            if fw_key in article_data:
                mapped[fw_key] = article_data[fw_key]
        result[article] = mapped

    return result


def format_mapping_text(mapping: dict) -> str:
    """Return a human-readable string showing each article's cross-framework mapping."""
    lines = []
    for article, frameworks in sorted(mapping.items(), key=lambda x: int(x[0])):
        lines.append(f"Article {article}")
        lines.append("=" * 40)

        eu = frameworks.get("eu_ai_act", {})
        if eu:
            lines.append(f"  EU AI Act — {eu.get('title', '')}")
            lines.append(f"    Requirement: {eu.get('requirement', '')}")

        nist = frameworks.get("nist_ai_rmf", {})
        if nist:
            functions = ", ".join(nist.get("functions", []))
            lines.append(f"  NIST AI RMF — Functions: {functions}")
            for sub in nist.get("subcategories", []):
                lines.append(f"    • {sub}")

        iso = frameworks.get("iso_42001", {})
        if iso:
            lines.append("  ISO/IEC 42001")
            for ctrl in iso.get("controls", []):
                lines.append(f"    • {ctrl}")

        lgpd = frameworks.get("lgpd", {})
        if lgpd:
            lines.append("  LGPD (Lei 13.709/2018 — Brasil)")
            for art in lgpd.get("articles", []):
                lines.append(f"    • {art}")
            if lgpd.get("notes"):
                lines.append(f"    Nota: {lgpd['notes']}")

        marco = frameworks.get("marco_legal_ia", {})
        if marco:
            status = marco.get("status", "")
            lines.append(f"  Marco Legal da IA — {status}" if status else "  Marco Legal da IA (PL 2338/2023 — Brasil)")
            for art in marco.get("articles", []):
                lines.append(f"    • {art}")
            if marco.get("notes"):
                lines.append(f"    Nota: {marco['notes']}")

        lines.append("")

    return "\n".join(lines)


def format_mapping_json(mapping: dict) -> str:
    """Return the mapping as a formatted JSON string."""
    return json.dumps(mapping, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Map EU AI Act articles to NIST AI RMF and ISO 42001 controls."
    )
    parser.add_argument(
        "--articles",
        required=True,
        help="Comma-separated article numbers, e.g. 9,12,14",
    )
    parser.add_argument(
        "--framework",
        default="all",
        help="Framework filter: eu-ai-act | nist-ai-rmf | iso-42001 | all (default: all)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    article_list = [a.strip() for a in args.articles.split(",") if a.strip()]
    framework_list = [f.strip() for f in args.framework.split(",") if f.strip()]

    mapping = map_to_frameworks(articles=article_list, frameworks=framework_list)

    if args.format == "json":
        print(format_mapping_json(mapping))
    else:
        print(format_mapping_text(mapping))


if __name__ == "__main__":
    main()
