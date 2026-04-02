# regula-ignore
"""Domain types for Regula risk classification.

Defines the core RiskTier enum and Classification dataclass used throughout
the Regula engine and its consumers.
"""

import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional

__all__ = [
    "RiskTier", "Classification", "Finding",
    "compute_finding_tier",
]


class RiskTier(Enum):
    PROHIBITED = "prohibited"
    HIGH_RISK = "high_risk"
    LIMITED_RISK = "limited_risk"
    MINIMAL_RISK = "minimal_risk"
    NOT_AI = "not_ai"


def compute_finding_tier(tier_value: str, confidence_score: int) -> str:
    """Compute finding tier from risk tier and confidence score.

    Single source of truth for block/warn/info logic.
    Returns: 'block', 'warn', or 'info'
    """
    from policy_config import get_policy
    policy = get_policy()
    thresholds = policy.get("thresholds", {})
    block_above = int(thresholds.get("block_above", 80))
    warn_above = int(thresholds.get("warn_above", 50))

    if tier_value == "prohibited":
        return "block"

    if confidence_score >= block_above:
        return "block"
    elif confidence_score >= warn_above:
        return "warn"
    else:
        return "info"


@dataclass
class Classification:
    tier: RiskTier
    confidence: str
    indicators_matched: list = field(default_factory=list)
    applicable_articles: list = field(default_factory=list)
    category: Optional[str] = None
    description: Optional[str] = None
    action: str = "allow"
    message: Optional[str] = None
    exceptions: Optional[str] = None
    confidence_score: int = 0  # 0-100 numeric confidence

    def get_finding_tier(self) -> str:
        """Return finding tier based on confidence score and policy thresholds.

        Returns: 'block', 'warn', or 'info'
        """
        return compute_finding_tier(self.tier.value, self.confidence_score)

    def to_dict(self) -> dict:
        result = asdict(self)
        result["tier"] = self.tier.value
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class Finding:
    """A single scan finding with file location, risk tier, and confidence.

    Formalises the dict contract used throughout report.py and cli.py.
    Use Finding.to_dict() when passing to JSON serialisation or legacy code
    that expects plain dicts.
    """
    file: str
    line: int
    tier: str
    category: str
    description: str
    indicators: list = field(default_factory=list)
    articles: list = field(default_factory=list)
    confidence_score: int = 0
    suppressed: bool = False
    observations: list = field(default_factory=list)
    exceptions: Optional[str] = None
    remediation: Optional[str] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        # Omit None values to match existing dict convention
        return {k: v for k, v in d.items() if v is not None}

    @staticmethod
    def from_dict(d: dict) -> "Finding":
        """Create a Finding from a plain dict (backward compat)."""
        known = {f.name for f in Finding.__dataclass_fields__.values()}
        return Finding(**{k: v for k, v in d.items() if k in known})
