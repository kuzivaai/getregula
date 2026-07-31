"""Continuity checks for the programme's tracked handover."""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
HANDOVER = REPO_ROOT / "docs" / "improvement" / "HANDOVER.md"


def test_handover_names_current_record_before_historical_instructions():
    """A new session must see the current pointer before stale instructions."""
    text = HANDOVER.read_text(encoding="utf-8")
    current_marker = "## CURRENT RESUME POINT"
    historical_marker = "## HISTORICAL SESSION 4 HANDOVER"

    assert current_marker in text
    assert historical_marker in text
    assert text.index(current_marker) < text.index(historical_marker)

    current = text[text.index(current_marker):text.index(historical_marker)]
    assert "docs/improvement/LEDGER.md" in current
    assert "single durable record" in current
    assert "Do not use the historical Git state or verification figures below" in current
