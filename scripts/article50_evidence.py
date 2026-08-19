#!/usr/bin/env python3
# regula-ignore — this module intentionally detects Article 50 transparency vocabulary
"""Static Article 50 observations that do not pretend to decide applicability.

The decision kernel needs facts about role, intended purpose, jurisdiction and
exceptions. Source-code strings cannot establish those facts. This scanner
therefore reports two narrower things for each Article 50 path:

* trigger-like implementation signals; and
* control-like implementation signals.

It never emits a compliance score or a legal conclusion. A missing match is
not evidence that a system lacks a feature, and a match is not evidence that a
runtime control is shown at the right time or works as intended.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from constants import CODE_EXTENSIONS, SKIP_DIRS
from decision_kernel import load_model
from scan_safety import walk_project_files


SCANNABLE_EXTENSIONS = set(CODE_EXTENSIONS) | {
    ".css", ".html", ".htm", ".json", ".md", ".rst", ".toml", ".txt",
    ".xml", ".yaml", ".yml",
}
# A README that quotes an obligation is useful context, but it is not an
# implemented notice. Control observations are therefore limited to formats
# that can participate in runtime behaviour or a rendered interface. This is
# still only a heuristic: the limitations remain load-bearing.
CONTROL_EXTENSIONS = set(CODE_EXTENSIONS) | {
    ".css", ".html", ".htm", ".json", ".svelte", ".vue", ".xml",
    ".yaml", ".yml",
}
MAX_OBSERVATIONS_PER_SET = 20


def _patterns(*items: tuple[str, str]) -> tuple[tuple[str, re.Pattern], ...]:
    return tuple((label, re.compile(pattern, re.IGNORECASE))
                 for label, pattern in items)


BRANCHES = {
    "50(1)": {
        "title": "Direct interaction with an AI system",
        "actor": "provider",
        "provision": "Regulation (EU) 2024/1689, Article 50(1)",
        "triggers": _patterns(
            # No leading word boundary: identifiers commonly use
            # `CustomerChatbot`, where the CamelCase transition is not a
            # regex word boundary. The trailing boundary still rejects
            # longer words beginning with chatbot.
            ("chatbot", r"chat[ -]?bot\b"),
            ("virtual assistant", r"\bvirtual assistant\b"),
            ("conversational agent", r"\bconversational (?:ai|agent|system)\b"),
            ("AI assistant", r"\bai assistant\b"),
            ("chat-completion interface", r"\bchat[._ -]?completions?\b"),
        ),
        "controls": _patterns(
            ("AI interaction notice", r"\binteract(?:ing|ion)? with (?:an? )?ai\b"),
            ("AI identity notice", r"\b(?:this is|you are (?:talking|chatting) (?:to|with)) an? ai\b"),
            ("AI assistant identity", r"\b(?:i am|i'm|we are)\b.{0,40}\ban? ai assistant\b"),
            ("AI-powered notice", r"\bpowered by (?:an? )?ai\b"),
            ("bot disclosure identifier", r"\b(?:ai|bot)[_ -]?disclos(?:ure|e|ing)\b"),
        ),
        "unresolved": (
            "role_provider", "eu_direct_interaction", "eu_interaction_obvious",
            "eu_50_1_criminal_law_exception",
            "eu_50_1_public_crime_reporting",
        ),
    },
    "50(2)": {
        "title": "Synthetic content generation or manipulation",
        "actor": "provider",
        "provision": "Regulation (EU) 2024/1689, Article 50(2)",
        "triggers": _patterns(
            ("text generation", r"\btext[ _-]?(?:generation|generator|to[ _-]text)\b"),
            ("image generation", r"\b(?:image[ _-]?(?:generation|generator)|text[ _-]to[ _-]image)\b"),
            ("audio generation", r"\b(?:audio|speech|voice)[ _-]?(?:generation|generator|synthesis)\b"),
            ("video generation", r"\b(?:video[ _-]?(?:generation|generator)|text[ _-]to[ _-]video)\b"),
            ("diffusion model", r"\b(?:stable[ _-]?diffusion|diffusion[ _-]?(?:model|pipeline))\b"),
            ("voice cloning", r"\bvoice[ _-]?clon(?:e|ing)\b"),
        ),
        "controls": _patterns(
            ("C2PA", r"\bc2pa\b"),
            ("Content Credentials", r"\bcontent credentials?\b"),
            ("machine-readable mark", r"\bmachine[ -]?readable (?:mark|label|format)\b"),
            ("watermark", r"\bwatermark(?:ed|ing)?\b"),
            ("content provenance", r"\b(?:content|media)[ _-]?provenance\b"),
            ("digital source type", r"\bdigitalSourceType\b"),
        ),
        "unresolved": (
            "role_provider", "eu_generates_synthetic_content",
            "eu_standard_editing_assistance_only",
            "eu_50_2_criminal_law_exception",
        ),
    },
    "50(3)": {
        "title": "Emotion recognition or biometric categorisation",
        "actor": "deployer",
        "provision": "Regulation (EU) 2024/1689, Article 50(3)",
        "triggers": _patterns(
            ("emotion recognition", r"\bemotion[ _-]?(?:recognition|detection|classifier)\b"),
            ("affect recognition", r"\baffect(?:ive)?[ _-]?(?:recognition|detection|computing)\b"),
            ("facial emotion analysis", r"\bfacial[ _-]?(?:emotion|expression)[ _-]?(?:analysis|recognition|detection)\b"),
            ("voice emotion analysis", r"\bvoice[ _-]?emotion[ _-]?(?:analysis|recognition|detection)\b"),
            ("biometric categorisation", r"\bbiometric[ _-]?categori[sz](?:ation|e|ing)\b"),
        ),
        "controls": _patterns(
            ("emotion-system notice", r"\b(?:emotion|affect(?:ive)?).{0,50}\b(?:notice|inform|disclos(?:ure|e|ing))\b"),
            ("biometric-system notice", r"\bbiometric.{0,50}\b(?:notice|inform|disclos(?:ure|e|ing))\b"),
            ("notice before exposure", r"\b(?:notice|inform).{0,50}\b(?:emotion recognition|biometric categori[sz]ation)\b"),
        ),
        "unresolved": (
            "role_deployer", "eu_emotion_recognition",
            "eu_biometric_categorisation", "eu_50_3_persons_exposed",
            "eu_50_3_criminal_law_exception",
        ),
    },
    "50(4)": {
        "title": "Deep-fake or public-interest synthetic content",
        "actor": "deployer",
        "provision": "Regulation (EU) 2024/1689, Article 50(4)",
        "triggers": _patterns(
            ("deep fake", r"deep[ _-]?fake\b"),
            ("face swap", r"\bface[ _-]?swap(?:ping)?\b"),
            ("voice cloning", r"\bvoice[ _-]?clon(?:e|ing)\b"),
            ("synthetic media", r"\bsynthetic[ _-]?media\b"),
            ("public-interest synthetic text", r"public[ _-]?interest.{0,40}(?:synthetic|generated|manipulated)[ _-]?text\b"),
        ),
        "controls": _patterns(
            ("AI-generated label", r"\b(?:ai|artificially)[ -]generated\b"),
            ("synthetic-media label", r"\bsynthetic (?:content|media).{0,40}\b(?:label|notice|disclos(?:ure|e|ing))\b"),
            ("deep-fake disclosure", r"\bdeep[ _-]?fake.{0,40}\b(?:label|notice|disclos(?:ure|e|ing))\b"),
            ("manipulated-content disclosure", r"\b(?:label|notice|disclos(?:ure|e|ing)).{0,40}\b(?:generated|manipulated)\b"),
        ),
        "unresolved": (
            "role_deployer", "eu_deepfake_content", "eu_public_interest_text",
            "eu_human_review_or_editorial_control",
            "eu_50_4_criminal_law_exception",
        ),
    },
}


RUNTIME_REVIEW_QUESTIONS = {
    "article50_5_first_interaction_or_exposure": (
        "Is the required information presented no later than the first "
        "interaction or exposure?"
    ),
    "article50_5_clear_and_distinguishable": (
        "Is the required information clear and distinguishable to the people "
        "concerned?"
    ),
    "article50_5_accessibility": (
        "Does the required information meet applicable accessibility requirements?"
    ),
    "article50_4_artistic_manner": (
        "For an evidently artistic, creative, satirical, fictional or analogous "
        "work, is the disclosure made in an appropriate manner that does not "
        "hamper display or enjoyment?"
    ),
}


def _find(content: str, relative_path: str, patterns) -> list[dict]:
    observations = []
    seen = set()
    lines = content.splitlines()
    for label, pattern in patterns:
        for line_number, line in enumerate(lines, 1):
            match = pattern.search(line)
            if not match:
                continue
            key = (label, line_number, match.group(0).lower())
            if key in seen:
                continue
            seen.add(key)
            observations.append({
                "file": relative_path,
                "line": line_number,
                "signal": label,
                "matched_text": match.group(0)[:120],
                "snippet": line.strip()[:240],
            })
            if len(observations) >= MAX_OBSERVATIONS_PER_SET:
                return observations
    return observations


def _state(triggers: list[dict], controls: list[dict]) -> str:
    if not triggers:
        return "trigger_not_observed"
    if controls:
        return "trigger_and_control_signals_observed"
    return "trigger_signal_observed_control_not_observed"


def scan_article50(
    project_path: str | Path,
    resolved_fact_ids: set[str] | None = None,
) -> dict:
    """Return traceable Article 50 technical observations for one project.

    ``resolved_fact_ids`` is presentation context supplied by a caller that has
    already evaluated human-declared facts.  The scanner still establishes no
    fact; the option only prevents the combined output from calling a fact
    "unresolved" after the decision kernel has resolved it.
    """
    project = Path(project_path).resolve()
    if not project.is_dir():
        raise ValueError(f"Project path is not a directory: {project}")

    findings = {
        key: {"triggers": [], "controls": []}
        for key in BRANCHES
    }
    scanned_file_count = 0
    for path, raw in walk_project_files(
        project, extensions=SCANNABLE_EXTENSIONS, skip_dirs=SKIP_DIRS
    ):
        scanned_file_count += 1
        content = raw.decode("utf-8", errors="ignore")
        relative = str(path.relative_to(project))
        for key, branch in BRANCHES.items():
            remaining_triggers = MAX_OBSERVATIONS_PER_SET - len(findings[key]["triggers"])
            if remaining_triggers > 0:
                found = _find(content, relative, branch["triggers"])
                findings[key]["triggers"].extend(found[:remaining_triggers])
            remaining_controls = MAX_OBSERVATIONS_PER_SET - len(findings[key]["controls"])
            if remaining_controls > 0 and path.suffix.lower() in CONTROL_EXTENSIONS:
                found = _find(content, relative, branch["controls"])
                findings[key]["controls"].extend(found[:remaining_controls])

    branches = {}
    model = load_model()
    fact_definitions = model["fact_definitions"]
    unresolved_ids = {"jurisdiction_in_scope", "is_ai_system"}
    any_trigger = False
    for key, branch in BRANCHES.items():
        triggers = findings[key]["triggers"]
        controls = findings[key]["controls"]
        any_trigger = any_trigger or bool(triggers)
        if triggers:
            unresolved_ids.update(branch["unresolved"])
        branches[key] = {
            "title": branch["title"],
            "actor_to_resolve": branch["actor"],
            "provision": branch["provision"],
            "observation_state": _state(triggers, controls),
            "trigger_observations": triggers,
            "control_observations": controls,
        }

    # Article 50(5) concerns presentation and timing of the information in
    # paragraphs 1-4. Static text cannot establish those runtime properties.
    branches["50(5)"] = {
        "title": "Timing, clarity, distinguishability and accessibility",
        "actor_to_resolve": "provider or deployer, following the applicable path",
        "provision": "Regulation (EU) 2024/1689, Article 50(5)",
        "observation_state": (
            "runtime_review_required" if any_trigger else "upstream_trigger_not_observed"
        ),
        "trigger_observations": [],
        "control_observations": [],
    }
    unknown_fact_ids = sorted(unresolved_ids - set(fact_definitions))
    if unknown_fact_ids:
        raise RuntimeError(
            "Article 50 scanner emitted non-canonical fact ids: "
            + ", ".join(unknown_fact_ids)
        )
    already_resolved = resolved_fact_ids or set()
    unresolved = [
        {"fact_id": fact_id, "question": fact_definitions[fact_id]["question"]}
        for fact_id in fact_definitions
        if fact_id in unresolved_ids and fact_id not in already_resolved
    ]
    runtime_review_ids = []
    if any_trigger:
        runtime_review_ids.extend([
            "article50_5_first_interaction_or_exposure",
            "article50_5_clear_and_distinguishable",
            "article50_5_accessibility",
        ])
    if findings["50(4)"]["triggers"]:
        runtime_review_ids.append("article50_4_artistic_manner")
    runtime_review_questions = [
        {"review_id": review_id,
         "question": RUNTIME_REVIEW_QUESTIONS[review_id]}
        for review_id in runtime_review_ids
    ]
    return {
        "result_type": "technical_observations",
        "project_path": str(project),
        "scanned_file_count": scanned_file_count,
        "branches": branches,
        "unresolved_facts": unresolved,
        "runtime_review_questions": runtime_review_questions,
        "limitations": [
            "A source-code match is a review lead, not proof that Article 50 applies.",
            "A control string does not prove that a notice or marking is visible, timely, accessible, machine-readable, robust or effective at runtime.",
            "No match is not proof that a trigger or control is absent; behaviour may be configured, generated, hosted or implemented outside the scanned tree.",
            "Provider/deployer role, territorial scope, intended purpose, statutory definitions and exceptions require declared facts and legal review.",
            "This output is not a compliance determination and contains no compliance score.",
        ],
    }


def format_article50_text(result: dict) -> str:
    """Render Article 50 observations without upgrading them to conclusions."""
    lines = [
        "Article 50 technical observations (not a legal determination):",
        f"Scanned files: {result['scanned_file_count']}",
    ]
    for key, branch in result["branches"].items():
        lines.append(f"  {key} {branch['title']}: {branch['observation_state']}")
        lines.append(
            "    trigger signals: "
            f"{len(branch['trigger_observations'])}; control signals: "
            f"{len(branch['control_observations'])}"
        )
    lines.append(f"Unresolved facts: {len(result['unresolved_facts'])}")
    for item in result["unresolved_facts"]:
        lines.append(f"  - {item['fact_id']}: {item['question']}")
    lines.append(
        f"Runtime review questions: {len(result['runtime_review_questions'])}"
    )
    for item in result["runtime_review_questions"]:
        lines.append(f"  - {item['review_id']}: {item['question']}")
    lines.append("Limitations:")
    for limitation in result["limitations"]:
        lines.append(f"  - {limitation}")
    return "\n".join(lines)
