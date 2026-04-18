"""Tests for compliance roadmap generation."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from roadmap import generate_roadmap, format_roadmap_text, ROADMAP_PHASES, ARTICLE_FIX_GUIDANCE


def test_roadmap_has_four_phases():
    assert len(ROADMAP_PHASES) == 4


def test_roadmap_with_no_gaps():
    """Project with all scores >= 90 should produce 0 tasks."""
    gap = {"articles": {"9": {"score": 95, "name": "Risk Management"}}}
    result = generate_roadmap(gap)
    assert result["total_tasks"] == 0


def test_roadmap_with_gaps():
    """Project with low scores should produce tasks."""
    gap = {
        "articles": {
            "9": {"score": 30, "name": "Risk Management", "gaps": ["Add hazard identification"]},
            "13": {"score": 10, "name": "Transparency", "gaps": ["Add AI disclosure"]},
        }
    }
    result = generate_roadmap(gap)
    assert result["total_tasks"] == 2
    assert result["weeks_remaining"] >= 1


def test_roadmap_quick_wins_first():
    """Quick wins (low effort, high criticality) should be in early weeks."""
    gap = {
        "articles": {
            "13": {"score": 10, "name": "Transparency", "gaps": ["Add AI disclosure"]},
            "9": {"score": 30, "name": "Risk Management", "gaps": ["Add hazard identification"]},
        }
    }
    result = generate_roadmap(gap)
    plan = result["weekly_plan"]
    if len(plan) >= 2:
        # Art 13 (transparency, low effort) should be scheduled before Art 9
        art13_week = next((p["week"] for p in plan if p["article"] == "13"), 999)
        art9_week = next((p["week"] for p in plan if p["article"] == "9"), 999)
        assert art13_week <= art9_week


def test_roadmap_target_date():
    gap = {"articles": {"13": {"score": 10, "name": "Transparency", "gaps": ["Add disclosure"]}}}
    result = generate_roadmap(gap, target_date="31 December 2027")
    assert "2027" in result["target_date"]


def test_roadmap_iso_date_format():
    gap = {"articles": {"13": {"score": 10, "name": "Transparency", "gaps": ["Add disclosure"]}}}
    result = generate_roadmap(gap, target_date="2027-12-31")
    assert result["weeks_remaining"] >= 1


def test_roadmap_has_omnibus_caveat():
    gap = {"articles": {"13": {"score": 10, "name": "Transparency", "gaps": ["Add disclosure"]}}}
    result = generate_roadmap(gap)
    assert "Omnibus" in result["omnibus_caveat"]


def test_format_roadmap_text():
    gap = {"articles": {"13": {"score": 10, "name": "Transparency", "gaps": ["Add disclosure"]}}}
    result = generate_roadmap(gap, project_name="my-project")
    text = format_roadmap_text(result)
    assert "my-project" in text
    assert "Week" in text


def test_roadmap_effort_disclaimer():
    gap = {"articles": {"13": {"score": 10, "name": "Transparency", "gaps": ["Add disclosure"]}}}
    result = generate_roadmap(gap)
    assert "heuristic" in result["effort_disclaimer"].lower()


def test_roadmap_tasks_have_next_command():
    """Each task should have a next_command for remediation."""
    gap = {
        "articles": {
            "13": {"score": 10, "name": "Transparency", "gaps": ["Add disclosure"]},
            "9": {"score": 30, "name": "Risk Management", "gaps": ["Add hazard identification"]},
        }
    }
    result = generate_roadmap(gap)
    for item in result["weekly_plan"]:
        assert "next_command" in item, f"Task for Art. {item['article']} missing next_command"
        assert item["next_command"].startswith("regula "), f"next_command should start with 'regula'"


def test_roadmap_tasks_have_fix_description():
    """Each task should have a fix_description."""
    gap = {"articles": {"13": {"score": 10, "name": "Transparency", "gaps": ["Add disclosure"]}}}
    result = generate_roadmap(gap)
    for item in result["weekly_plan"]:
        assert "fix_description" in item, f"Task for Art. {item['article']} missing fix_description"
        assert len(item["fix_description"]) > 0


def test_roadmap_fix_guidance_exists_for_all_articles():
    """ARTICLE_FIX_GUIDANCE should cover Articles 5, 9-15."""
    for art in ("5", "9", "10", "11", "12", "13", "14", "15"):
        assert art in ARTICLE_FIX_GUIDANCE, f"Missing fix guidance for Article {art}"
        assert "command" in ARTICLE_FIX_GUIDANCE[art]
        assert "description" in ARTICLE_FIX_GUIDANCE[art]


def test_roadmap_text_shows_commands_when_actionable():
    """Text output should include arrow commands when actionable=True."""
    gap = {"articles": {"13": {"score": 10, "name": "Transparency", "gaps": ["Add disclosure"]}}}
    result = generate_roadmap(gap)
    text = format_roadmap_text(result, actionable=True)
    assert "\u2192" in text
    assert "regula " in text


def test_roadmap_text_hides_commands_when_not_actionable():
    """Text output should not include arrow commands when actionable=False."""
    gap = {"articles": {"13": {"score": 10, "name": "Transparency", "gaps": ["Add disclosure"]}}}
    result = generate_roadmap(gap)
    text = format_roadmap_text(result, actionable=False)
    assert "\u2192" not in text


def test_roadmap_known_article_gets_specific_command():
    """Article 13 should map to 'regula disclose', not generic check."""
    gap = {"articles": {"13": {"score": 10, "name": "Transparency", "gaps": ["Add disclosure"]}}}
    result = generate_roadmap(gap)
    art13 = [item for item in result["weekly_plan"] if item["article"] == "13"]
    assert len(art13) == 1
    assert "disclose" in art13[0]["next_command"]


def test_roadmap_unknown_article_gets_fallback_command():
    """An article not in ARTICLE_FIX_GUIDANCE should get a fallback command."""
    gap = {"articles": {"99": {"score": 10, "name": "Unknown", "gaps": ["Something"]}}}
    result = generate_roadmap(gap)
    for item in result["weekly_plan"]:
        assert item["next_command"].startswith("regula ")
