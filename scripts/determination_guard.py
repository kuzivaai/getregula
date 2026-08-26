#!/usr/bin/env python3
"""Refuse any output or key that asserts a compliance state.

Project policy prohibits presenting a scan result as a compliance
determination or presenting "not flagged" as "compliant". A prior audit found
three shipped paths doing that, the worst being `regula badge`, which emitted a pasteable
Markdown badge reading "EU AI Act: compliant" in brightgreen for a directory
whose only content was `print('hello')`.

WHY NOTHING CAUGHT IT, corrected. N125 recorded that the guard for this class is
`verify_transcripts.RETIRED_MARKERS`, and that widening it would flag legitimate
negated prose. That named the wrong guard. The guard for this class is
`public_surface_inventory.PROHIBITED_CLAIMS`, which has arms for "legal
classification", "compliance scan", "obligation determination" and "universal
network", and had no arm for the STRONGEST form of the claim: asserting that a
compliance state holds. N107 built that machinery, in three languages, with a
planted control per (class, language) pair. It simply had nothing to say about
the word `compliant`.

WHY THIS IS A SEPARATE MODULE AND NOT A FIFTH ARM THERE. PROHIBITED_CLAIMS is
applied to PUBLISHED SURFACES, selected from the delivery-derived inventory by
suffix (`TEXT_SITE`). Two of N125's three paths were not on a published surface
at all: they were string literals and a dict key in `scripts/`, which only become
output when a command runs. A guard that reads published copy cannot see
`message = "compliant"` in a Python source file. So this module scans SOURCE and
the strings it emits, and the published-copy half stays with PROHIBITED_CLAIMS,
which gains its missing arm in the same commit.

WHAT MAKES THIS A CLAIM-SHAPE RULE RATHER THAN A SUBSTRING. N125's objection to
widening a substring list is correct and is honoured here. `compliant` appears
141 times in 55 tracked files, and the overwhelming majority are legitimate:
negations ("a clean scan does not mean a system is compliant"), prohibitions
("never as standards-compliant"), and technical-format conformance ("RFC
3161-compliant TSA"). Only an AFFIRMATIVE assertion that a LEGAL compliance state
holds is a finding. Three mechanisms separate them:

  1. The patterns match affirmative shapes only (`: COMPLIANT`, `is compliant`,
     `compliant <artefact>`, `<regulation>-compliant`, a `*compliant*` JSON key).
  2. A negator inside NEGATOR_WINDOW characters before the match clears it, so
     "is not compliance" and "does not certify compliance" stay green.
  3. TECHNICAL_STANDARDS clears conformance to a named machine format, because
     "RFC 3161-compliant" is a checkable statement about a wire protocol and not
     a statement about anybody's legal position.

Every one of those three is a way to make the guard quieter, so each is paired
with a control proving it still fires on a real legal claim. A guard that can be
talked out of every finding is measurement rule 4's blank gate.

EXEMPTIONS ARE DATA, NOT CODE, AND THEY GO STALE LOUDLY. One legitimate
occurrence remains: the self-recorded `compliance_status` state machine in
`scripts/discover_ai_systems.py`, whose terminal value is `compliant`. Regula
never sets it; `discover` always writes `not_started` and `register_system`
preserves an existing value, so the assertion belongs to the person who typed it.
The owner ruled on 2026-08-17 to keep the stored values, because renaming them
migrates registry files on users' machines. Following N123's discipline, that
disposition is a DECLARED RECORD keyed on the hit's own line, and a record that
matches nothing FAILS as stale, so an exemption cannot outlive its premise.

SUFFIX SCOPE, and the carrier this closes. `.svg` is scanned. A terminal-recorder
SVG is entirely text: it carries a whole transcript in `<text>` nodes. When this
module was written on 2026-08-17 the delivery inventory classified
`site/assets/demo/regula-check.svg` as `content_kind: asset,
claim_capable: False` purely because `.svg` was not in `TEXT_SITE`, and
`claim_auditor.SCANNED_SUFFIXES` and `verify_transcripts.py` both filtered it
out as well, while `README.md:32` embedded it as the first visual on the
project's front page. This module was the only instrument that could read it.

Later the same day the three recordings were removed, the README embed was
replaced by a fenced transcript bound to a re-runnable command, `svg_text` gave
the other instruments a way to read the carrier, and the inventory started
deciding `.svg` by content rather than by suffix. `.svg` stays in scope here
regardless: the scope must outlive the files that motivated it, or the next
recording added would be unread again.

Usage:
    python3 scripts/determination_guard.py            # report, rc=1 on findings
    python3 scripts/determination_guard.py --check    # same, for CI
    python3 scripts/determination_guard.py --control  # prove the guard can fail
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from public_surface_inventory import claim_match_variants  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent

# Suffixes scanned. `.svg` is deliberate; see the module docstring.
SCANNED_SUFFIXES = {
    ".py", ".js", ".ts", ".html", ".htm", ".md", ".txt", ".json", ".yaml",
    ".yml", ".svg",
}

# Paths whose whole purpose is to record what was once true, or to test this
# guard. Excluding a directory is the move N70 found hides live defects, so this
# list is deliberately short and every entry is a verbatim historical record.
EXCLUDED_PREFIXES = (
    "CHANGELOG.md",           # records what shipped, verbatim
    "benchmarks/results/",    # captured scanner output, byte-identical by rule
    "content/regulations/delta-log/",  # dated regulatory captures
)

# Affirmative shapes. Authored against folded text: entities decoded, accents
# stripped, casefolded, whitespace collapsed. See fold_for_claim_match.
DETERMINATION_SHAPES = {
    "state asserted after a colon":
        re.compile(r":\s*compliant\b"),
    "state asserted as a copula":
        re.compile(r"\b(?:is|are|was|were|becomes?|remains?|now)\s+"
                   r"(?:fully\s+|now\s+)?compliant\b"),
    "artefact asserted compliant":
        re.compile(r"\bcompliant\s+(?:disclosure|documentation|document|text|"
                   r"output|artefacts?|artifacts?|report|pack|scaffold|code)\b"),
    # Adjective-after-noun, which English does not use and German and Brazilian
    # Portuguese do. The FIRST run of _control missed
    # "gera texto de divulgacao compliant" because every other shape here was
    # authored in English word order. That is N107's finding, a guard blind to a
    # shipped language, recurring inside the guard written to answer it. The
    # noun list is deliberately narrow: a bare `\w+ compliant` would match
    # "is compliant" and "not compliant" and turn the negator window into the
    # only thing standing between this guard and constant false positives.
    "artefact asserted compliant, adjective after noun":
        re.compile(r"\b(?:text[eo]?|texto|documento|documenta\w+|divulga\w+|"
                   r"relatorio|saida|codigo|dokument\w*|bericht|ausgabe|"
                   r"offenlegung\w*)\s+(?:\w+\s+){0,3}compliant\b"),
    "certification asserted":
        re.compile(r"\bcertif(?:ies|ied|ication)\s+(?:of\s+|as\s+)?complian\w*"),
    "regulation-qualified compliance":
        re.compile(r"\b(?:annex\s+[ivx]+|article\s+\d+[a-z]?|eu ai act|ai act|"
                   r"gdpr|lgpd)[\s-]*compliant\b"),
    "compliance state as a literal value":
        re.compile(r"[=:]\s*[\"']compliant[\"']"),
    "key name asserting a compliance state":
        re.compile(r"[\"'][a-z_]*compliant[\"']\s*:"),
    # --- German ---------------------------------------------------------------
    # The site ships in three languages and the whole of N107 is the finding that
    # a guard written only in English is blind to two thirds of the copy it
    # polices. Deliberately NOT matching `konformitatsbestimmung` or a bare
    # `konformitat`: the shipped German pages use both correctly, in sentences
    # saying Regula does NOT establish conformity.
    # `konform\w*` not `konform\b`: German inflects the adjective, so
    # `konformes`, `konforme` and `konformer` all evade a word boundary placed
    # straight after the stem. The FIRST run of the multilingual control missed
    # "Ein EU-AI-Act-konformes Ergebnis" for exactly that reason. English has no
    # equivalent, which is why authoring in one language and translating the
    # words is not the same as covering the language.
    "German: conformity asserted":
        re.compile(r"\b(?:ist|sind|war|waren|wird|werden)\s+"
                   r"(?:vollstandig\s+|nun\s+)?konform\w*\b"),
    "German: conformity asserted as achieved":
        re.compile(r"\bkonformitat\s+(?:ist\s+)?"
                   r"(?:nachgewiesen|bestatigt|gegeben|erreicht|hergestellt)\b"),
    "German: regulation-qualified conformity":
        re.compile(r"\b(?:eu[\s-]*)?(?:ai[\s-]*act|ki[\s-]*verordnung|dsgvo)"
                   r"[\s-]*konform\w*\b"),
    "German: conformity asserted after a colon":
        re.compile(r":\s*konform\b"),
    # --- Brazilian Portuguese -------------------------------------------------
    # Deliberately NOT matching a bare `conformidade com`, which is legitimate
    # and live: the comparison table's own aria-label reads "ferramentas e
    # servicos de conformidade com o Regulamento de IA da UE", and a page
    # explains that `nao conformidade` with information requirements incurs a
    # fine. Both are statements about the law, not about a user's position.
    "Portuguese: conformity asserted":
        re.compile(r"\b(?:esta|estao|e|sao|fica|ficam)\s+"
                   r"(?:totalmente\s+|plenamente\s+)?em conformidade\b"),
    "Portuguese: conformity asserted as achieved":
        re.compile(r"\bconformidade\s+(?:foi\s+)?"
                   r"(?:comprovada|confirmada|atingida|garantida)\b"),
    "Portuguese: conformity asserted after a colon":
        re.compile(r":\s*em conformidade\b"),
}

# A negator this close before a match clears it. 70 characters covers the real
# phrasings on this repo's surfaces ("a clean scan does not mean a system is
# compliant") without reaching across a sentence boundary into unrelated prose.
NEGATOR_WINDOW = 70
# German and Portuguese negators are NOT optional decoration. Every affirmative
# arm below has a locale sibling, and the shipped German and Portuguese copy is
# correctly negated throughout ("Es bestimmt keine Konformitaet", "O Regula nao
# determina ... conformidade"). Without `keine` and `nao` in this list, adding
# those arms would turn the guard red on the very sentences that get it right,
# and the obvious next step would be to delete the arms rather than the
# blindness. That is how a locale-aware guard becomes a monolingual one again.
NEGATORS = re.compile(
    r"\b(?:not|never|no|nor|nothing|cannot|can't|doesn't|does not|isn't|is not|"
    r"aren't|are not|without|neither|refuse[sd]?|forbid(?:s|den)?|prohibit(?:s|ed)?|"
    r"must not|do not|don't|rather than|instead of|"
    # German
    r"kein|keine|keinen|keiner|nicht|weder|noch|nie|niemals|ohne|statt|"
    # Portuguese, folded (accents already stripped)
    r"nao|nem|nenhum|nenhuma|sem|nunca|jamais|em vez de)\b"
)

# Conformance to a named machine format is not a legal claim. Each entry is a
# wire protocol or serialisation whose conformance is checkable by a machine.
# NOT exempt, deliberately: "Annex IV", "Article 50", "EU AI Act", which are law.
TECHNICAL_STANDARDS = re.compile(
    r"\b(?:rfc\s*\d+|cyclonedx|json-?ld|sarif|spdx|in-toto|schema\.org|"
    r"iso\s*8601|pkcs\s*#?\d+|oauth|posix|utf-?8)\b"
)
TECHNICAL_WINDOW = 40


class StaleExemption(Exception):
    """A declared exemption matched nothing. Its premise is gone."""


# path -> tuple of (line_regex, reason). Matched against the HIT's own line, per
# N123: a character window either side lets one declared constant vouch for a
# claim two lines below, which the fixtures for that mechanism killed at once.
DECLARED_NOT_A_DETERMINATION = {
    "scripts/discover_ai_systems.py": (
        (r'^COMPLIANCE_STATUSES\s*=',
         "The user's own status vocabulary for their own registry. Regula never "
         "assigns the terminal value. Owner ruling 2026-08-17: keep the stored "
         "values, because renaming migrates ~/.regula/registry.json on users' "
         "machines. Framing corrected at every point Regula prints them."),
        (r'^\s*"(?:implementing|compliant|review_due)":',
         "Transition table for the same user-declared vocabulary."),
    ),
    "scripts/dpv_data/dpv_aiact_terms.json": (
        (r'"AIAct(?:Compliant|NonCompliant)"\s*:',
         "Third-party vocabulary, not a Regula claim. These are class names in "
         "the W3C DPVCG Data Privacy Vocabulary AI Act extension, each carrying "
         "its own w3id.org IRI. Regula maps to the vocabulary; it does not "
         "assert the class of anything. Renaming a term would break the mapping "
         "and misquote an external standard, which is the rule that keeps "
         "captured artefacts byte-identical."),
        (r'"label"\s*:\s*"AI Act (?:Compliant|Non-compliant)"',
         "The human label of the same external DPVCG class."),
    ),
    "site/blog/blog-startups-ignoring-ai-act.html": (
        (r'GDPR compliant.{0,40}badges started appearing',
         "A MENTION, not a use: the sentence describes other companies' GDPR "
         "badges appearing before enforcement, in quotation marks and in a "
         "critical register. Regula asserts nothing about anyone's compliance "
         "here, and the passage is an argument against exactly the behaviour "
         "the badge defect exhibited."),
    ),
}


def _tracked_files() -> list[str]:
    """Enumerate by git, never by glob (measurement rule 4b, 4c).

    Fails closed: an unreadable index raises rather than returning an empty
    corpus, because an empty corpus is a guard that passes for the wrong reason.
    """
    out = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    )
    return [p for p in out.stdout.split("\0") if p]


def _own_path() -> str:
    """This module's own repo-relative path, derived rather than written down.

    A guard cannot be its own corpus. Every pattern in DETERMINATION_SHAPES and
    every case in `_control` IS a literal compliance-state assertion, because
    that is what a pattern and a planted control are. Staging this file made it
    tracked and the guard immediately reported 26 findings, all of them its own
    source, which is the self-reference the ledger records for the count guard at
    N109 and N111.

    This is a structural exclusion and NOT a suppression, for a reason that can
    be checked: this module emits no user-facing product output. It prints
    findings to a maintainer and exits. Nothing here can reach a README, a badge
    or a page. The exclusion is computed from `__file__` rather than listed, so
    it covers exactly one file and cannot be widened into a directory escape
    hatch, which is the failure N70 found in broad path exclusions.
    """
    return str(Path(__file__).resolve().relative_to(REPO_ROOT))


def in_scope(rel: str) -> bool:
    if rel.startswith(EXCLUDED_PREFIXES):
        return False
    if rel.startswith("tests/"):
        # The guard's own controls plant real determinations on purpose.
        return False
    if rel == _own_path():
        return False
    return Path(rel).suffix.lower() in SCANNED_SUFFIXES


# Directory names inside an installed package that are build residue rather
# than shipped content.
_ARTEFACT_SKIP_DIRS = {"__pycache__"}


DIST_NAME = "regula_ai"


def artefact_files(root: Path) -> list[str]:
    """Every file THIS distribution installed under `root`, from its own RECORD.

    `_tracked_files` cannot serve here and substituting it would be measurement
    rule 1: an installed artefact is not a git checkout, so there is no index to
    ask. A bare walk cannot serve either, and that was measured rather than
    assumed: walking a real virtual environment's site-packages returned a
    finding inside `pip/_vendor/distlib/metadata.py`, which is not this
    project's artefact at all. The population is what the wheel installed, and
    the wheel says so in `*.dist-info/RECORD`.

    Fails closed on a missing or empty RECORD, because an empty corpus is a
    guard that passes for the wrong reason (measurement rule 4).
    """
    root = Path(root)
    if not root.is_dir():
        raise RuntimeError(f"{root}: not a directory, so there is no artefact to scan")

    records = sorted(root.glob(f"{DIST_NAME}-*.dist-info/RECORD"))
    if len(records) != 1:
        raise RuntimeError(
            f"{root}: expected exactly one {DIST_NAME}-*.dist-info/RECORD, found "
            f"{len(records)}. Without the distribution's own manifest this scan "
            f"would be a walk over whatever else is installed beside it.")

    files = []
    for line in records[0].read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rel = line.split(",")[0]
        if not rel or rel.endswith("/"):
            continue
        if _ARTEFACT_SKIP_DIRS & set(Path(rel).parts):
            continue
        if any(part.endswith((".dist-info", ".egg-info")) for part in Path(rel).parts):
            continue
        if not (root / rel).is_file():
            raise RuntimeError(f"{rel}: named in RECORD but absent from {root}")
        files.append(rel)
    if not files:
        raise RuntimeError(f"{root}: RECORD lists no files, so this scan would prove nothing")
    return sorted(files)


def artefact_in_scope(rel: str) -> bool:
    """Scope inside an installed artefact.

    Deliberately NOT `in_scope`. `EXCLUDED_PREFIXES` names repository paths that
    do not exist in a wheel, and applying them would silently do nothing while
    looking like coverage. The one exclusion that must survive is this module's
    own source, which ships inside the package and IS a corpus of literal
    compliance-state assertions by construction — the same self-reference
    `_own_path` handles for the tree.
    """
    if Path(rel).name == Path(__file__).name and Path(rel).parts[:1] == ("scripts",):
        return False
    return Path(rel).suffix.lower() in SCANNED_SUFFIXES


def _cleared_by_negator(folded: str, start: int) -> bool:
    window = folded[max(0, start - NEGATOR_WINDOW):start]
    return bool(NEGATORS.search(window))


def _cleared_by_technical_standard(folded: str, start: int, end: int) -> bool:
    lo = max(0, start - TECHNICAL_WINDOW)
    hi = min(len(folded), end + TECHNICAL_WINDOW)
    return bool(TECHNICAL_STANDARDS.search(folded[lo:hi]))


def determinations_in_text(text: str) -> list[tuple[str, str]]:
    """Every affirmative compliance-state assertion in one blob of text.

    Returns (shape name, the folded fragment) pairs. Both readings of the source
    are searched, markup kept and markup replaced by space, and results are
    unioned, so a phrase split by an inline tag cannot evade the pattern and a
    claim living in an attribute value stays covered. That is N107's finding.
    """
    found = {}
    for folded in claim_match_variants(text):
        for shape, pattern in DETERMINATION_SHAPES.items():
            for m in pattern.finditer(folded):
                if _cleared_by_negator(folded, m.start()):
                    continue
                if _cleared_by_technical_standard(folded, m.start(), m.end()):
                    continue
                lo = max(0, m.start() - 60)
                hi = min(len(folded), m.end() + 60)
                found.setdefault((shape, folded[lo:hi].strip()), None)
    return sorted(found)


def _exempt_line(rel: str, line: str) -> str | None:
    for pattern, reason in DECLARED_NOT_A_DETERMINATION.get(rel, ()):
        if re.search(pattern, line):
            return reason
    return None


def scan_file(rel: str, root: Path | None = None) -> list[dict]:
    """Findings in one file, line by line so exemptions can be exact.

    `root` defaults to the repository. It is a parameter so the same predicate
    can read an installed package; forking it would be measurement rule 1.
    """
    path = Path(root or REPO_ROOT) / rel
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:                                    # pragma: no cover
        raise RuntimeError(f"{rel}: unreadable ({exc})") from exc

    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        hits = determinations_in_text(line)
        if not hits:
            continue
        if _exempt_line(rel, line):
            continue
        for shape, fragment in hits:
            findings.append({"file": rel, "line": number,
                             "shape": shape, "fragment": fragment})
    return findings


def audit_declared_exemptions(files: list[str]) -> list[str]:
    """A declared exemption that matches nothing is a defect, not a saving.

    N123's rule, and the quarantine's before it: an exclusion must not outlive
    its premise. Returns human-readable staleness complaints.
    """
    stale = []
    for rel, records in DECLARED_NOT_A_DETERMINATION.items():
        if rel not in files:
            stale.append(f"{rel}: declared exempt but git does not track it")
            continue
        text = (REPO_ROOT / rel).read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        for pattern, _reason in records:
            if not any(re.search(pattern, ln) for ln in lines):
                stale.append(f"{rel}: exemption /{pattern}/ matches no line")
    return stale


def run(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="CI mode (same behaviour; kept for gate symmetry)")
    parser.add_argument("--control", action="store_true",
                        help="Prove the guard can fail: run it against planted "
                             "determinations and a planted negation")
    parser.add_argument("--root", metavar="PATH",
                        help="Scan an INSTALLED package root (site-packages) by "
                             "walk instead of this repository by git index. "
                             "N144: the tree is not what anyone installs.")
    args = parser.parse_args(argv)

    if args.control:
        return _control()

    if args.root:
        return _run_artefact(Path(args.root))

    files = _tracked_files()
    scoped = [f for f in files if in_scope(f)]
    if not scoped:
        print("determination-guard: REFUSING, corpus is empty. A guard with no "
              "corpus passes for the wrong reason.", file=sys.stderr)
        return 2

    stale = audit_declared_exemptions(files)
    findings = []
    for rel in scoped:
        findings.extend(scan_file(rel))

    print(f"determination-guard: scanned {len(scoped)} tracked file(s) of "
          f"{len(files)}, {len(findings)} finding(s)")
    for f in findings:
        print(f"  {f['file']}:{f['line']}: {f['shape']}: {f['fragment']}")
    for s in stale:
        print(f"  STALE EXEMPTION {s}")

    if findings or stale:
        print("\nAn affirmative compliance-state assertion is the one claim this "
              "project forbids outright. Re-express it "
              "as an indicator, or record why it is not a determination in "
              "DECLARED_NOT_A_DETERMINATION with a reason.")
        return 1
    print("  no compliance-state assertion on any scanned surface — OK")
    return 0


def _run_artefact(root: Path) -> int:
    """The same guard, over an installed artefact rather than over the tree.

    DECLARED_NOT_A_DETERMINATION is deliberately NOT consulted here. Every entry
    in it is keyed on a repository-relative path, and honouring those keys inside
    a wheel would exempt lines by coincidence of name. An artefact scan is
    therefore stricter than a tree scan, which is the correct direction: what
    ships has no context to plead.
    """
    files = artefact_files(root)
    scoped = [f for f in files if artefact_in_scope(f)]
    if not scoped:
        print("determination-guard: REFUSING, artefact corpus is empty. A guard "
              "with no corpus passes for the wrong reason.", file=sys.stderr)
        return 2

    findings = []
    for rel in scoped:
        findings.extend(scan_file(rel, root=root))

    print(f"determination-guard: scanned {len(scoped)} installed file(s) of "
          f"{len(files)} under {root}, {len(findings)} finding(s)")
    for f in findings:
        print(f"  {f['file']}:{f['line']}: {f['shape']}: {f['fragment']}")
    if findings:
        print("\nThese are in the artefact a user installs, not only in the tree. "
              "N144 is the entry that exists because nothing checked this.")
        return 1
    print("  no compliance-state assertion in the installed artefact — OK")
    return 0


def _control() -> int:
    """Positive proof the predicate discriminates, in both directions."""
    must_fire = [
        ("badge message", 'message = "compliant"'),
        ("printed state", "EU AI Act Transparency (Art 50/52): COMPLIANT"),
        ("json key", '"transparency_compliant": True,'),
        ("artefact claim", "generate compliant disclosure text"),
        ("regulation-qualified", "Generate Annex IV compliant documentation."),
        ("copula", "Your project is compliant with the EU AI Act."),
        ("markup split", "is <strong>compliant</strong> with Article 50"),
        ("entity accented", "gera texto de divulga&ccedil;&atilde;o compliant"),
        ("de copula", "Ihr System ist konform."),
        ("de achieved", "Die Konformit&auml;t ist nachgewiesen."),
        ("de regulation-qualified", "Ein EU-AI-Act-konformes Ergebnis."),
        ("de colon", "EU AI Act Transparenz: KONFORM"),
        ("pt copula", "O seu sistema est&aacute; em conformidade."),
        ("pt achieved", "A conformidade foi comprovada."),
        ("pt colon", "Transpar&ecirc;ncia do Regulamento de IA: em conformidade"),
    ]
    must_stay_silent = [
        ("negation", "A clean scan does not mean a system is compliant."),
        ("prohibition", 'never as "the AI Act standard" or "standards-compliant".'),
        ("limitation", "Presence of a document is not compliance with Article 50."),
        ("technical rfc", "Verify an RFC 3161-compliant TSA works."),
        ("technical cyclonedx", "A CycloneDX 1.7 compliant BOM dictionary."),
        ("technical jsonld", "any conformant JSON-LD processor can expand the"),
        ("refusal", "Regula refuses to say your system is compliant."),
        # Verbatim from the shipped locale pages. If any arm above fires on one
        # of these, the arm is wrong, not the copy.
        ("de live negation",
         "Es stellt keine Konformit&auml;t fest. Ein qualifizierter Rechtsanwalt"),
        ("de live negation 2",
         "Risikoindikatoren zur &Uuml;berpr&uuml;fung. Es bestimmt keine "
         "Konformit&auml;t."),
        ("de live compound noun",
         "seine Ausgabe sollte nicht als endg&uuml;ltige "
         "Konformit&auml;tsbestimmung herangezogen werden"),
        ("pt live negation",
         "O Regula n&atilde;o determina classifica&ccedil;&atilde;o "
         "jur&iacute;dica nem conformidade."),
        ("pt live statement about the law",
         "N&atilde;o conformidade com requisitos de informa&ccedil;&atilde;o "
         "acarreta multa"),
        ("pt live aria-label",
         "Compara&#231;&#227;o de ferramentas e servi&#231;os de conformidade "
         "com o Regulamento de IA da UE"),
    ]
    failures = []
    for name, text in must_fire:
        if not determinations_in_text(text):
            failures.append(f"MISSED a real determination [{name}]: {text!r}")
    for name, text in must_stay_silent:
        hits = determinations_in_text(text)
        if hits:
            failures.append(f"FALSE POSITIVE [{name}]: {text!r} -> {hits}")

    for line in failures:
        print(f"  {line}")
    if failures:
        print(f"\ncontrol: {len(failures)} of "
              f"{len(must_fire) + len(must_stay_silent)} cases wrong")
        return 1
    print(f"control: {len(must_fire)} planted determinations all detected, "
          f"{len(must_stay_silent)} legitimate statements all silent")
    return 0


if __name__ == "__main__":
    sys.exit(run())
