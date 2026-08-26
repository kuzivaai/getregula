# regula-ignore
"""No output and no key may assert a compliance state.

Project policy prohibits affirmative compliance-state claims. A prior audit
recorded three shipped paths that broke it, the worst being a pasteable Markdown badge that named the regulation
and asserted a compliance state in green for a directory whose only content
printed a greeting.

This module is the at-rest half. `scripts/determination_guard.py` carries the
predicate and its own `--control`; these tests pin the properties that make the
predicate trustworthy rather than merely quiet:

  - it can fail at all, on the real tree, on the real defect (measurement rule 4:
    a blank gate is not a green gate);
  - its corpus is non-empty and actually reaches the files that carried the
    defect, so an exclusion typo cannot make it pass by scanning nothing
    (N56's lesson, where an at-rest check trusted the tool that found the drift);
  - every way of making it QUIETER is exercised in the direction that would hide
    a real claim: the negator window, the technical-standard clearance, and the
    declared exemptions;
  - a declared exemption exempts an OCCURRENCE and never a file (N70's finding
    against broad path exclusions), and a stale one fails loudly (N123's rule);
  - it covers all three shipped languages, because N107's whole finding is that
    an English-only guard is blind to two thirds of the copy it polices.
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import determination_guard as dg  # noqa: E402

# The files that carried N125's three paths, plus the one found while fixing it.
# Named literally so a change to the corpus predicate that stopped reaching them
# fails here rather than passing silently.
FILES_THAT_CARRIED_THE_DEFECT = (
    "scripts/cli_report.py",
    "scripts/ai_code_governance.py",
    "scripts/cli_analysis.py",
    "scripts/assess.py",
    "site/blog/blog-does-ai-act-apply.html",
)


class TestTheGuardCanFail(unittest.TestCase):
    """Positive proof the predicate discriminates, in both directions."""

    def test_planted_determinations_are_all_detected(self):
        missed = []
        for name, text in (
            ("badge message", 'message = "compliant"'),
            ("printed state", "EU AI Act Transparency (Art 50/52): COMPLIANT"),
            ("json key", '"transparency_compliant": True,'),
            ("artefact claim", "generate compliant disclosure text"),
            ("regulation-qualified", "Generate Annex IV compliant documentation."),
            ("markup split", "is <strong>compliant</strong> with Article 50"),
            ("german inflected", "Ein EU-AI-Act-konformes Ergebnis."),
            ("portuguese copula", "O seu sistema est&aacute; em conformidade."),
        ):
            if not dg.determinations_in_text(text):
                missed.append(f"{name}: {text!r}")
        self.assertEqual([], missed, f"guard missed real determinations: {missed}")

    def test_legitimate_statements_do_not_fire(self):
        """Each of these is a way the guard is allowed to stay quiet.

        If any of them started firing, the fix would be the arm, not the copy:
        the last three are verbatim from the shipped German and Portuguese pages.
        """
        wrong = []
        for name, text in (
            ("negation", "A clean scan does not mean a system is compliant."),
            ("limitation", "Presence of a document is not compliance with Art 50."),
            ("technical standard", "Verify an RFC 3161-compliant TSA works."),
            ("de live negation", "Es bestimmt keine Konformit&auml;t."),
            ("de compound noun",
             "sollte nicht als endg&uuml;ltige Konformit&auml;tsbestimmung"),
            ("pt statement about the law",
             "N&atilde;o conformidade com requisitos acarreta multa"),
        ):
            hits = dg.determinations_in_text(text)
            if hits:
                wrong.append(f"{name}: {text!r} -> {hits}")
        self.assertEqual([], wrong, f"guard fired on legitimate copy: {wrong}")

    def test_the_module_control_passes(self):
        """`--control` is the shipped self-check; run it rather than trust it."""
        rc = dg.run(["--control"])
        self.assertEqual(0, rc, "determination_guard --control did not pass")


class TestTheCorpusIsRealAndReaches(unittest.TestCase):
    """An exclusion typo must not be able to make this gate pass."""

    def test_the_corpus_is_not_empty(self):
        scoped = [f for f in dg._tracked_files() if dg.in_scope(f)]
        self.assertGreater(
            len(scoped), 100,
            "corpus collapsed. A guard that scans almost nothing reports almost "
            "nothing, which is measurement rule 4's blank gate.")

    def test_the_corpus_reaches_every_file_that_carried_the_defect(self):
        scoped = {f for f in dg._tracked_files() if dg.in_scope(f)}
        missing = [f for f in FILES_THAT_CARRIED_THE_DEFECT if f not in scoped]
        self.assertEqual(
            [], missing,
            f"the guard no longer scans files that carried N125: {missing}")

    def test_the_only_self_exclusion_is_this_guard_and_the_test_tree(self):
        """The exclusion for its own source must not become a directory hatch.

        A guard cannot be its own corpus: its patterns and its planted controls
        are literal compliance-state assertions. That is structural, and it is
        bounded here rather than trusted. Anything else under scripts/ must
        remain in scope, and the exclusion must be exactly one file.
        """
        self.assertFalse(dg.in_scope("scripts/determination_guard.py"))
        for still_scanned in ("scripts/cli_report.py", "scripts/assess.py",
                              "scripts/ai_code_governance.py",
                              "scripts/discover_ai_systems.py"):
            self.assertTrue(dg.in_scope(still_scanned),
                            f"{still_scanned} fell out of scope")

    def test_text_bearing_vector_assets_are_in_scope(self):
        """`.svg` is scanned, and that is the point rather than an accident.

        A terminal-recorder SVG is entirely text: the whole transcript sits in
        `<text>` nodes. On 2026-08-17 `README.md` embedded one and three
        independent instruments could not read it: the delivery inventory
        classed it `non_claim_asset` because `.svg` was outside
        `public_surface_inventory.TEXT_SITE`, `claim_auditor.SCANNED_SUFFIXES`
        excluded it, and `verify_transcripts.py` filtered to `.md/.html/.txt`.
        This guard did not, and was the only instrument that could see it.

        The three recordings were removed the same day and the README embed
        replaced with a fenced transcript bound to a re-runnable command, so the
        path below no longer exists. The assertion is deliberately on the path
        SHAPE and not on a file: this guard's `.svg` scope must survive the
        recordings' removal, or the next one added would be unread again.
        """
        self.assertIn(".svg", dg.SCANNED_SUFFIXES)
        self.assertTrue(dg.in_scope("site/assets/demo/any-future-recording.svg"))
        self.assertTrue(dg.in_scope("vscode-extension/resources/regula-sidebar.svg"))


class TestQuietingMechanismsAreBounded(unittest.TestCase):
    """Every route to silence, exercised in the direction that would hide a claim."""

    def test_the_negator_window_does_not_reach_across_a_long_gap(self):
        """A negator far away must not clear a nearby affirmative claim."""
        filler = "x" * (dg.NEGATOR_WINDOW + 30)
        text = f"This tool does not certify anything. {filler} Your system is compliant."
        self.assertTrue(
            dg.determinations_in_text(text),
            "a negator beyond the window silenced a real claim, so the window "
            "is acting as a blanket exemption")

    def test_the_technical_clearance_does_not_cover_a_legal_claim(self):
        """RFC and CycloneDX are exempt; Annex IV and Article 50 are law."""
        self.assertTrue(dg.determinations_in_text(
            "Generate Annex IV compliant documentation."))
        self.assertTrue(dg.determinations_in_text(
            "The output is Article 50 compliant."))
        self.assertFalse(dg.determinations_in_text(
            "A CycloneDX 1.7 compliant BOM dictionary."))

    def test_every_shipped_language_has_at_least_one_arm(self):
        """N107's structural finding, applied to this guard.

        The site's shipped languages are enumerated from the pages themselves in
        `public_surface_inventory`; here the requirement is simply that this
        guard is not English-only, because that is the state N107 found and
        fixed elsewhere.
        """
        names = " ".join(dg.DETERMINATION_SHAPES)
        for language in ("German", "Portuguese"):
            self.assertIn(
                language, names,
                f"no {language} arm. An English-only determination guard is "
                f"blind to two thirds of the copy this project ships.")

    def test_non_english_negators_are_present(self):
        """Without these, the locale arms fire on correct negated copy.

        The shipped German and Portuguese pages say Regula does NOT establish
        conformity. If `keine` and `nao` were missing, the arms above would turn
        the guard red on exactly the sentences that get it right, and the
        tempting fix would be to delete the arms.
        """
        for negator in ("keine", "nicht", "nao", "nenhuma"):
            self.assertTrue(
                dg.NEGATORS.search(f"foo {negator} bar"),
                f"{negator!r} is not a recognised negator")


class TestDeclaredExemptions(unittest.TestCase):

    def test_no_declared_exemption_is_stale(self):
        """An exclusion must not outlive its premise. N123's rule."""
        stale = dg.audit_declared_exemptions(dg._tracked_files())
        self.assertEqual([], stale, f"stale exemptions: {stale}")

    def test_every_exemption_carries_a_reason(self):
        for rel, records in dg.DECLARED_NOT_A_DETERMINATION.items():
            for pattern, reason in records:
                self.assertTrue(
                    reason and len(reason) > 40,
                    f"{rel}: /{pattern}/ has no substantive reason recorded")

    def test_declaring_a_file_does_not_exempt_the_file(self):
        """N70's objection to broad path exclusions, asserted at the point of use.

        A determination planted on a DIFFERENT line of an exempted file must
        still be a finding, or the mechanism is a path exclusion wearing a
        reason.
        """
        exempted = "scripts/discover_ai_systems.py"
        self.assertIn(exempted, dg.DECLARED_NOT_A_DETERMINATION)
        planted = 'MESSAGE = "compliant"'
        self.assertIsNone(
            dg._exempt_line(exempted, planted),
            "an exempted file exempted a line its records do not name")
        self.assertTrue(dg.determinations_in_text(planted))


class TestTheShippedTreeIsClean(unittest.TestCase):

    def test_no_scanned_surface_asserts_a_compliance_state(self):
        rc = dg.run([])
        self.assertEqual(
            0, rc,
            "a scanned surface asserts a compliance state. Run "
            "`python3 scripts/determination_guard.py` for the itemisation.")

    def test_the_gate_is_reachable_as_a_subprocess(self):
        """CI runs the script, not the import, so run it the way CI does."""
        proc = subprocess.run(
            [sys.executable, "scripts/determination_guard.py", "--check"],
            cwd=str(REPO), capture_output=True, text=True, timeout=180,
        )
        self.assertEqual(0, proc.returncode,
                         f"gate failed as a subprocess:\n{proc.stdout}\n{proc.stderr}")
        self.assertIn("scanned", proc.stdout)


class TestTheBadgeSpecifically(unittest.TestCase):
    """The badge is the one output built to travel into a third party's README."""

    def test_the_badge_source_names_no_regulation_and_no_state(self):
        source = (REPO / "scripts" / "cli_report.py").read_text(encoding="utf-8")
        badge = source[source.index("def cmd_badge"):]
        badge = badge[:badge.index("def cmd_aibom")]
        self.assertNotIn("EU AI Act", badge,
                         "the badge label names the regulation again")
        self.assertNotIn("brightgreen", badge,
                         "a green badge beside a regulation reads as a pass")
        self.assertFalse(
            re.search(r'["\']compliant["\']', badge),
            "the badge message asserts a compliance state again")

    def test_the_badge_links_to_its_own_caveat(self):
        """The objection to a badge is that it detaches from every disclaimer.

        So the disclaimer is the link target. The document must be tracked, or
        the link 404s from inside someone else's README.
        """
        from cli_report import BADGE_CAVEAT_URL
        self.assertIn("what-regula-does-not-do", BADGE_CAVEAT_URL)
        tracked = subprocess.run(
            ["git", "ls-files", "docs/what-regula-does-not-do.md"],
            cwd=str(REPO), capture_output=True, text=True, check=True,
        ).stdout.strip()
        self.assertTrue(tracked, "the badge's caveat target is not tracked")


if __name__ == "__main__":
    unittest.main()
