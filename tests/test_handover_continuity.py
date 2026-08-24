"""Continuity checks for the programme's tracked handover."""
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
HANDOVER = REPO_ROOT / "docs" / "improvement" / "HANDOVER.md"
STATE = REPO_ROOT / "docs" / "improvement" / "STATE.md"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import current_state  # noqa: E402


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


def test_current_state_is_generated_from_live_instruments():
    assert STATE.read_text(encoding="utf-8") == current_state.render()


def test_current_state_does_not_confuse_local_source_with_deployment():
    text = STATE.read_text(encoding="utf-8")
    assert "Deployment currency is not derivable from this repository" in text
    assert "A local or committed HTML change is not a deployment" in text
    assert "Scanner parity is not scanner validity" in text


def test_executed_analytics_gate_is_not_reported_as_future_work():
    text = STATE.read_text(encoding="utf-8")
    assert "Anonymous funnel contract: EXECUTED" in text
    assert "Execute the first tailored editorial submissions" in text
    assert "Complete the anonymous funnel contract's full gate" not in text
