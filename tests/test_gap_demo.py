# regula-ignore
"""Class 1 - the landing page's terminal demo must be real output.

The landing page previously presented detector-derived tiers, duties,
readiness percentages, deadlines, and effort estimates behind `$` prompts.
The four current panels must instead match real unresolved decision output.

`data/gap_demo.json` is produced by `scripts/build_gap_demo.py` from real
runs against the committed fixture `tests/fixtures/sample_high_risk`. This
file binds the site to it on both sides:

- the artefact must match a fresh run, so it cannot be hand-edited
- every decision field the artefact records must appear in each locale's panel
- no readiness percentage may appear while applicability is unresolved

All three locales carry the same block because command output is English
in all three.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTEFACT = REPO_ROOT / "data/gap_demo.json"
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import build_gap_demo as builder

LOCALE_PAGES = [
    "site/index.html",
    "site/locales/de.html",
    "site/locales/pt-br.html",
]

GAP_PANEL = re.compile(
    r'<pre tabindex="0"><span class="t-p">\$</span> '
    r'<span class="t-c">regula gap [^<]*</span>.*?</pre>', re.DOTALL)
COMPLY_PANEL = re.compile(
    r'<pre tabindex="0"><span class="t-p">\$</span> '
    r'<span class="t-c">regula comply [^<]*</span>.*?</pre>', re.DOTALL)
PERCENT = re.compile(r"(\d{1,3})%")
CHECK_PANEL = re.compile(
    r'<pre tabindex="0"><span class="t-p">\$</span> '
    r'<span class="t-c">regula check [^<]*</span>.*?</pre>', re.DOTALL)
PLAN_PANEL = re.compile(
    r'<pre tabindex="0"><span class="t-p">\$</span> '
    r'<span class="t-c">regula plan [^<]*</span>.*?</pre>', re.DOTALL)
PANELS = {
    "check": CHECK_PANEL,
    "plan": PLAN_PANEL,
    "gap": GAP_PANEL,
    "comply": COMPLY_PANEL,
}


def _artefact() -> dict:
    return json.loads(ARTEFACT.read_text(encoding="utf-8"))


def _panel(page: str, pattern: re.Pattern[str]) -> str:
    text = (REPO_ROOT / page).read_text(encoding="utf-8")
    m = pattern.search(text)
    if not m:
        raise AssertionError(f"{page}: terminal panel not found")
    return m.group(0)


class TestArtefactIsProducedNotWritten(unittest.TestCase):
    def test_artefact_matches_a_fresh_run(self):
        proc = subprocess.run(
            [sys.executable, "scripts/build_gap_demo.py", "--check"],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=1800)
        self.assertEqual(
            proc.returncode, 0,
            f"data/gap_demo.json disagrees with a fresh run.\n"
            f"stdout: {proc.stdout}\nstderr: {proc.stderr}")

    def test_the_fixture_is_committed(self):
        """An untracked fixture would make the published output
        unreproducible from a clone. Measurement rule 4b."""
        fixture = _artefact()["fixture"]
        out = subprocess.run(["git", "ls-files", fixture], cwd=str(REPO_ROOT),
                             capture_output=True, text=True).stdout.strip()
        self.assertTrue(
            out, f"{fixture} is not tracked, so no clone reproduces the "
                 f"numbers this page publishes")

    def test_unresolved_output_carries_resolvable_facts(self):
        gap = _artefact()["gap"]
        self.assertEqual(gap["result_type"], "insufficient_information")
        self.assertEqual(gap["article_observations_emitted"], 0)
        self.assertGreater(gap["article_observations_held"], 0)
        self.assertEqual(gap["unresolved_count"], len(gap["unresolved_fact_ids"]))


def test_untracked_or_ignored_content_is_not_an_input():
    """A local file inside the fixture must never enter the snapshot."""
    stray = REPO_ROOT / builder.FIXTURE / ".mutation-untracked-input"
    assert not stray.exists(), f"mutation path already exists: {stray}"
    try:
        stray.write_text("must not be scanned\n", encoding="utf-8")
        with builder._tracked_fixture_snapshot() as snapshot:
            assert not (snapshot / stray.name).exists()
    finally:
        stray.unlink(missing_ok=True)


def test_git_failure_is_fatal():
    failed = subprocess.CompletedProcess(
        args=["git"], returncode=128, stdout=b"", stderr=b"git unavailable"
    )
    with mock.patch.object(builder.subprocess, "run", return_value=failed):
        try:
            with builder._tracked_fixture_snapshot():
                pass
        except RuntimeError as exc:
            assert "Git could not derive" in str(exc)
        else:
            raise AssertionError("Git failure was swallowed")


class TestEveryLocalePanelMatchesTheArtefact(unittest.TestCase):
    def test_gap_panel_contains_no_unresolved_readiness_percentage(self):
        for page in LOCALE_PAGES:
            found = sorted(int(p) for p in PERCENT.findall(_panel(page, GAP_PANEL)))
            self.assertEqual(found, [], f"{page}: unresolved gap panel has percentages {found}")

    def test_comply_panel_contains_no_unresolved_readiness_percentage(self):
        for page in LOCALE_PAGES:
            found = sorted(int(p) for p in PERCENT.findall(
                _panel(page, COMPLY_PANEL)))
            self.assertEqual(found, [], f"{page}: unresolved comply panel has percentages {found}")

    def test_every_decision_field_is_present_in_every_locale(self):
        artefact = _artefact()
        for command, pattern in PANELS.items():
            art = artefact[command]
            for page in LOCALE_PAGES:
                panel = _panel(page, pattern)
                self.assertIn(art["result_type"], panel)
                self.assertIn(art["model_version"], panel)
                self.assertIn(art["rule_resolution"], panel)
                for fact_id in art["unresolved_fact_ids"]:
                    self.assertIn(fact_id, panel)

    def test_check_and_plan_panels_do_not_emit_unresolved_claims(self):
        forbidden = ("Classification: HIGH-RISK", "OBLIGATIONS:", "Effort:", "Deadline:")
        for page in LOCALE_PAGES:
            for pattern in (CHECK_PANEL, PLAN_PANEL):
                panel = _panel(page, pattern)
                for phrase in forbidden:
                    self.assertNotIn(phrase, panel)

    def test_the_panel_names_the_fixture_it_scanned(self):
        """A `$` prompt with no target is what made the old block read as a
        scan of the visitor's own project."""
        fixture = _artefact()["fixture"]
        for page in LOCALE_PAGES:
            self.assertIn(fixture, _panel(page, GAP_PANEL),
                          f"{page}: the gap panel does not say what it scanned")

    def test_comply_panel_shows_the_all_flag(self):
        """Without --all the command prints no article table for this
        fixture. A panel showing rows without the flag depicts output the
        command does not produce."""
        for page in LOCALE_PAGES:
            self.assertIn("--all", _panel(page, COMPLY_PANEL),
                          f"{page}: comply panel omits the --all flag")


class TestTheInventedNumbersAreGone(unittest.TestCase):
    """Control. The repair is only real if the old figures cannot return."""

    INVENTED = ["42/100", "1/7 obligations"]

    def test_no_locale_still_carries_the_invented_headline(self):
        for page in LOCALE_PAGES:
            text = (REPO_ROOT / page).read_text(encoding="utf-8")
            for phrase in self.INVENTED:
                self.assertNotIn(
                    phrase, text,
                    f"{page} still carries {phrase!r} from the mock-up")

    def test_the_old_progress_bar_glyphs_are_gone_from_the_panels(self):
        for page in LOCALE_PAGES:
            for pattern in (GAP_PANEL, COMPLY_PANEL):
                panel = _panel(page, pattern)
                self.assertNotIn(
                    "&#9608;", panel,
                    f"{page}: a progress-bar glyph survives in a panel that "
                    f"is meant to be verbatim command output")


if __name__ == "__main__":
    unittest.main()
