# regula-ignore
"""Multi-jurisdiction regulation mapping.

Maps detected domain concepts to jurisdiction-specific obligations.
Patterns detect domains. This module maps domains to articles and obligations.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    import yaml
except ImportError:
    from policy_config import _parse_yaml_fallback
    yaml = None

JURISDICTIONS_DIR = Path(__file__).parent.parent / "references" / "jurisdictions"

# Cache loaded jurisdictions to avoid repeated file I/O
_JURISDICTION_CACHE = {}


def _load_yaml(path):
    """Load YAML file using PyYAML if available, fallback otherwise."""
    text = path.read_text(encoding="utf-8")
    if yaml:
        return yaml.safe_load(text)
    return _parse_yaml_fallback(text)


def load_jurisdiction(jurisdiction_id):
    """Load a jurisdiction config from YAML.

    Args:
        jurisdiction_id: Short ID matching filename in references/jurisdictions/
            (e.g. 'eu_ai_act', 'south_korea', 'colorado')

    Returns:
        dict: Parsed jurisdiction configuration.

    Raises:
        ValueError: If jurisdiction_id doesn't match any YAML file.
    """
    if jurisdiction_id in _JURISDICTION_CACHE:
        return _JURISDICTION_CACHE[jurisdiction_id]

    path = JURISDICTIONS_DIR / f"{jurisdiction_id}.yaml"
    # Path traversal containment: resolved path must stay within JURISDICTIONS_DIR
    try:
        resolved = path.resolve()
        base = JURISDICTIONS_DIR.resolve()
        if not resolved.is_relative_to(base):
            raise ValueError(f"Invalid jurisdiction_id: {jurisdiction_id!r}")
    except (OSError, ValueError):
        raise ValueError(f"Invalid jurisdiction_id: {jurisdiction_id!r}")

    if not path.exists():
        available = [p.stem for p in JURISDICTIONS_DIR.glob("*.yaml")]
        raise ValueError(
            f"Unknown jurisdiction: {jurisdiction_id}. "
            f"Available: {', '.join(sorted(available))}"
        )

    try:
        config = _load_yaml(path)
    except Exception as e:
        raise ValueError(
            f"Failed to parse jurisdiction file {path.name}: {e}"
        ) from e
    _JURISDICTION_CACHE[jurisdiction_id] = config
    return config


def list_jurisdictions():
    """Return list of available jurisdiction IDs."""
    return sorted(p.stem for p in JURISDICTIONS_DIR.glob("*.yaml"))


def map_domains_to_obligations(domains, jurisdiction_id):
    """Map a set of detected domains to jurisdiction-specific obligations.

    Args:
        domains: iterable of domain strings (e.g. {"employment", "credit"})
        jurisdiction_id: jurisdiction to map against

    Returns:
        list of dicts, one per covered domain, each containing:
            domain, risk_level, category, articles, obligations
        Empty list if no domains are covered.
    """
    config = load_jurisdiction(jurisdiction_id)
    domain_map = config.get("domain_mappings", {})
    results = []

    for domain in sorted(domains):
        if domain not in domain_map:
            continue
        mapping = domain_map[domain]
        results.append({
            "domain": domain,
            "covered": True,
            "risk_level": mapping.get("risk_level", "unknown"),
            "category": mapping.get("category", ""),
            "articles": mapping.get("articles", []),
            "obligations": mapping.get("obligations", []),
        })

    return results


def get_jurisdiction_summary(jurisdiction_id):
    """Return human-readable summary of a jurisdiction.

    Returns:
        dict with name, law, effective_date, status, penalty_range, deadlines
    """
    config = load_jurisdiction(jurisdiction_id)
    return {
        "id": config["jurisdiction_id"],
        "name": config["name"],
        "law": config["law_reference"],
        "effective_date": config.get("effective_date", ""),
        "status": config.get("status", ""),
        "penalty_range": config.get("penalties", {}).get("range", ""),
        "risk_tiers": config.get("risk_tiers", []),
        "deadlines": config.get("deadlines", {}),
    }
