# regula-ignore
"""Domain types for Regula risk classification.

Defines the core RiskTier enum and Classification dataclass used throughout
the Regula engine and its consumers.
"""

import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional


class RiskTier(Enum):
    PROHIBITED = "prohibited"
    HIGH_RISK = "high_risk"
    LIMITED_RISK = "limited_risk"
    MINIMAL_RISK = "minimal_risk"
    NOT_AI = "not_ai"


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
        from policy_config import get_policy
        policy = get_policy()
        thresholds = policy.get("thresholds", {})
        block_above = int(thresholds.get("block_above", 80))
        warn_above = int(thresholds.get("warn_above", 50))

        # Prohibited always blocks regardless of confidence
        if self.tier == RiskTier.PROHIBITED:
            return "block"

        if self.confidence_score >= block_above:
            return "block"
        elif self.confidence_score >= warn_above:
            return "warn"
        else:
            return "info"

    def to_dict(self) -> dict:
        result = asdict(self)
        result["tier"] = self.tier.value
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
