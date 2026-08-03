# regula-ignore
"""Every set/multiset comparison in the claim apparatus, classified.

WHY THIS EXISTS
---------------
N37 was a comparison whose KEY was coarser than the UNIT it resolved to. A
finding key with the line dropped was differenced to pick out one occurrence
among several, and it produced a correct total of 70 with a wrong
attribution: the difference resolved to line 213 while the finding actually
revealed was at line 210. It was fixed where the join guard fired.

Nothing then checked whether any OTHER comparison had the same shape. That
audit ran on 2026-07-30 and found one more, in
`claim_diff.classify_findings`, which compared a SET of claim keys across two
commits and so lost multiplicity rather than position. Same root cause, a key
too coarse for the question, different symptom.

An audit is a snapshot. This file is what stops it going stale: it re-runs the
enumeration by AST on every test run and fails if a comparison site appears
that nobody has classified. Adding a new set difference to the apparatus is
then a deliberate act with a written reason, not something that lands
unnoticed.

WHY AN AST WALK AND NOT GREP
----------------------------
`.claude/rules/measurement.md` rule 4c: a completeness claim is a measurement
and must be produced by enumeration. A grep misses an operator inside a
comprehension or a nested call and cannot tell `a - b` on two sets from `a - b`
on two integers. The walk below finds both and the inventory records which is
which.

WHY THE INVENTORY IS KEYED ON (file, function, kind) AND NOT ON LINE NUMBERS
---------------------------------------------------------------------------
Line numbers drift on every edit, and an inventory that has to be renumbered
is an inventory that gets renumbered carelessly. The enclosing function is
stable under edits that do not change what the code does, which is exactly the
property wanted.

WHAT "IN SCOPE" MEANS HERE
--------------------------
A site is IN SCOPE for the N37 class if it compares collections whose elements
stand for FINDINGS, CLAIMS or QUARANTINE ENTRIES across two states: two
instrument states over one tree, or two commits. Regex flag unions, type
annotation unions, display arithmetic on lengths, and sets of file paths are
all recorded and marked out of scope, with the reason, because "we looked at
it and it is fine" is only useful if it says why.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# The apparatus, enumerated by predicate in test_the_apparatus_set_is_derived
# below rather than trusted as a hand-written list.
APPARATUS_MODULES = {
    "claim_auditor", "gate_probe", "claim_diff", "merge_blockers",
    "f25_exposure", "quarantine_liveness",
}

SET_OPS = {ast.Sub: "-", ast.BitAnd: "&", ast.BitOr: "|", ast.BitXor: "^"}
SET_METHODS = {
    "difference", "intersection", "union", "symmetric_difference",
    "most_common", "subtract", "elements", "issubset", "issuperset",
}
# A bare `a - b` is arithmetic far more often than it is a set difference, so
# Sub is kept only where the line mentions something set-shaped. The inventory
# then records what each survivor actually is.
SUB_HINTS = ("set(", "Counter", "sig", "key", "fired", "finding", "rows",
             "keys")
MEMBERSHIP_HINTS = ("sig", "_key", "fired", "seen", "keys")

CROSS_STATE = "CROSS-STATE"
OUT_OF_SCOPE = "out-of-scope"

# (file, function, kind) -> (verdict, reason)
#
# CROSS-STATE entries are the N37 class. Each states which key it uses, whether
# that key can collide within one file, and what kind of comparison it makes.
INVENTORY: dict[tuple[str, str, str], tuple[str, str]] = {
    ("scripts/merge_blockers.py", "active_claim_surface_paths", "setcomp"): (
        OUT_OF_SCOPE,
        "SAFE. Single-state derivation from the generated delivery inventory. "
        "The repository-relative source path is the key; repeated records for "
        "one source intentionally collapse because publication is a file-level "
        "predicate. It compares neither commits nor finding populations."),
    ("scripts/claim_auditor.py", "delivery_surface_paths", "setcomp"): (
        OUT_OF_SCOPE,
        "SAFE. This is a single-state derivation of active source paths from "
        "one generated inventory. The key is the repository-relative source "
        "path; duplicates intentionally collapse because a source file is "
        "scanned once even when it supplies multiple destinations. It does "
        "not compare states, totals, findings, or commits."),
    # ---- CROSS-STATE: the class N37 belongs to -------------------------
    ("scripts/gate_probe.py", "arm_delta", "setcomp"): (
        CROSS_STATE,
        "SAFE. Key is finding_key = (file, LINE, kind, snippet, occurrence). "
        "Cannot collide within one file because the line is in the key. "
        "Same-tree comparison of two instrument states, arm on against arm "
        "off, over one unchanged tree, so lines are stable and a line-bearing "
        "key is the correct one. This is the N37 fix."),
    ("scripts/gate_probe.py", "arm_delta", "BinOp -"): (
        CROSS_STATE,
        "SAFE. Set difference on finding_key, a same-tree comparison. The key "
        "cannot collide within one file because it carries both the line and "
        "the occurrence ordinal, so the difference resolves to an exact "
        "occurrence. Reverting the key to a line-free form reintroduces N37 "
        "and is pinned against in tests/test_gate_probe.py."),
    ("scripts/claim_diff.py", "blocker_delta", "BinOp |"): (
        CROSS_STATE,
        "SAFE. A union of the KEY SETS of two Counters, purely to enumerate "
        "every signature present on either side. The key is "
        "content_signature and CAN collide within one file, which costs "
        "nothing here because no attribution is taken from this union; the "
        "counts on the next line do that, and they preserve multiplicity."),
    ("scripts/claim_diff.py", "blocker_delta", "BinOp -"): (
        CROSS_STATE,
        "SAFE, and deliberately coarse. Key is content_signature = (file, "
        "kind, snippet) with NO coordinates, because lines move between "
        "commits and a line-keyed diff reports every finding below an "
        "insertion as removed and re-added. It CAN collide within one file, "
        "which is the point: it is a MULTISET difference, so a collision "
        "changes a count rather than losing an occurrence. Where a signature "
        "existed on both sides the row carries ambiguous=True and lists every "
        "line, rather than picking one and looking certain."),
    ("scripts/claim_diff.py", "classify_findings", "BinOp -"): (
        CROSS_STATE,
        "WAS DEFECTIVE, FIXED 2026-07-30. Key is claim_key = (file, snippet), "
        "no line and no ordinal, so it CAN collide within one file. It "
        "compared a SET across two commits, so a base holding a claim once "
        "marked a head holding it twice as entirely inherited and the "
        "introduced occurrence vanished. Now a multiset comparison; the "
        "surplus is introduced, the tie-break is declared and every finding "
        "in an ambiguous group carries present_at_base_ambiguous. Measured "
        "under-count on the real tree at 509c997 was 0, so the defect was "
        "latent rather than active."),
    ("scripts/quarantine_liveness.py", "cause_of", "in/not-in"): (
        CROSS_STATE,
        "SAFE, and checked rather than inherited. Compares FIRED SETS across "
        "four instrument passes, keyed (file, normalised claim). The key CAN "
        "collide within one file, and it does not matter: a quarantine ENTRY "
        "is keyed identically, so the key granularity equals the unit being "
        "classified. There is no occurrence to attribute to, so there is "
        "nothing to misattribute. Multiplicity is kept separately in "
        "scan_pass's `occurrences` list."),
    ("scripts/quarantine_liveness.py", "also_blocked_by", "in/not-in"): (
        CROSS_STATE,
        "SAFE. Fired-set membership across instrument passes, stated in full "
        "rather than deferring to cause_of, because a reason that says 'as "
        "above' rots when the above changes. The key is (file, normalised "
        "claim) and CAN collide within one file; it does not matter, because "
        "a quarantine entry is keyed identically, so the key is the unit "
        "rather than a lossy identifier for something finer."),

    # ---- out of scope, with the reason --------------------------------
    ("scripts/claim_auditor.py", "<module>", "BinOp |"): (
        OUT_OF_SCOPE, "re.IGNORECASE | re.VERBOSE flags, and a type union."),
    ("scripts/claim_auditor.py", "strip_noise", "BinOp |"): (
        OUT_OF_SCOPE, "re.DOTALL | re.IGNORECASE flags."),
    ("scripts/claim_auditor.py", "_is_self_url", "BinOp |"): (
        OUT_OF_SCOPE, "PageIdentity | None type annotation."),
    ("scripts/claim_auditor.py", "_is_self_file_ref", "BinOp |"): (
        OUT_OF_SCOPE, "PageIdentity | None type annotation."),
    ("scripts/claim_auditor.py", "paragraph_has_source", "BinOp |"): (
        OUT_OF_SCOPE, "PageIdentity | None type annotation."),
    ("scripts/claim_auditor.py", "stale_number_verdict", "BinOp |"): (
        OUT_OF_SCOPE, "dict | None type annotation."),
    ("scripts/claim_auditor.py", "main", "BinOp |"): (
        OUT_OF_SCOPE, "list[str] | None type annotation."),
    ("scripts/claim_auditor.py", "human_report", "BinOp -"): (
        OUT_OF_SCOPE,
        "len(findings) - 20 for a truncated display line. Arithmetic on one "
        "length in one state."),
    ("scripts/claim_auditor.py", "check_precision_claims", "BinOp &"): (
        OUT_OF_SCOPE,
        "Intersects candidate roundings of ONE published percentage with the "
        "known values from ONE artefact. Both sides are the same state, so "
        "there is no cross-state attribution to get wrong."),
    ("scripts/claim_auditor.py", "check_recall_claims", "setcomp"): (
        OUT_OF_SCOPE,
        "Denominators of the known fractions in one artefact. One state."),
    ("scripts/claim_diff.py", "classify", "setcomp"): (
        OUT_OF_SCOPE,
        "sorted({f['file'] ...}): FILE PATHS, to pick the paths to scan. A "
        "path occurs once, so there is no multiplicity to lose."),
    ("scripts/claim_diff.py", "main", "BinOp -"): (
        OUT_OF_SCOPE, "len(rows) - at, a display column."),
    ("scripts/f25_exposure.py", "_manifest_surfaces", "BinOp -"): (
        OUT_OF_SCOPE,
        "set(paths) - set(kept) on FILE PATHS from a manifest, to name the "
        "surface the auditor cannot scan. No multiplicity, no occurrence."),
    ("scripts/f25_exposure.py", "totals", "setcomp"): (
        OUT_OF_SCOPE, "Distinct file names, for a per-file report."),
    ("scripts/f25_exposure.py", "report_shape", "setcomp"): (
        OUT_OF_SCOPE, "Distinct file names, for a per-file report."),
    ("scripts/gate_probe.py", "citation_word_rows", "setcomp"): (
        OUT_OF_SCOPE,
        "Distinct citation WORDS in one paragraph in one state."),
    ("scripts/gate_probe.py", "paragraph_shape", "setcomp"): (
        OUT_OF_SCOPE, "Distinct citation words in one state."),
    ("scripts/gate_probe.py", "enumerate_revealed", "BinOp -"): (
        OUT_OF_SCOPE,
        "findings_with_arm_off - findings_now, two INDEPENDENTLY counted "
        "totals reconciled against the enumeration. It is the check on the "
        "set difference, not a set difference."),
    ("scripts/merge_blockers.py", "main_only_findings", "setcomp"): (
        OUT_OF_SCOPE, "Distinct file names, for a per-file breakdown."),
    ("scripts/quarantine_liveness.py", "named_pages", "setcomp"): (
        OUT_OF_SCOPE, "Distinct file names named by the quarantine."),
    ("scripts/quarantine_liveness.py", "measure", "BinOp |"): (
        OUT_OF_SCOPE, "dict | None type annotation."),
    ("scripts/untracked_source_audit.py", "main", "setcomp"): (
        OUT_OF_SCOPE, "Distinct file and ref names, for display counts."),
}


def apparatus_scripts() -> list[str]:
    """Scripts that touch the claim apparatus, by import, not by memory."""
    listed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "scripts"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    out = []
    for rel in listed:
        if not rel.endswith(".py"):
            continue
        try:
            tree = ast.parse((REPO_ROOT / rel).read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        if (imported & APPARATUS_MODULES) or Path(rel).stem in APPARATUS_MODULES:
            out.append(rel)
    return sorted(out)


def _enclosing_functions(tree: ast.AST) -> dict[int, str]:
    """Line -> innermost enclosing function name, or '<module>'."""
    mapping: dict[int, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.walk(node):
                if hasattr(child, "lineno"):
                    mapping.setdefault(child.lineno, node.name)
    return mapping


def enumerate_sites() -> list[tuple[str, str, str, int, str]]:
    """Every set/multiset operation site, as (file, function, kind, line, src)."""
    sites: list[tuple[str, str, str, int, str]] = []
    for rel in apparatus_scripts():
        source = (REPO_ROOT / rel).read_text(encoding="utf-8")
        lines = source.splitlines()
        tree = ast.parse(source)
        scope = _enclosing_functions(tree)

        def text(node) -> str:
            index = node.lineno - 1
            return lines[index].strip() if 0 <= index < len(lines) else ""

        def record(node, kind: str) -> None:
            sites.append((rel, scope.get(node.lineno, "<module>"), kind,
                          node.lineno, text(node)))

        class Walker(ast.NodeVisitor):
            def visit_BinOp(self, node):
                for op_type, symbol in SET_OPS.items():
                    if isinstance(node.op, op_type):
                        if op_type is ast.Sub and not any(
                                h in text(node) for h in SUB_HINTS):
                            continue
                        record(node, f"BinOp {symbol}")
                self.generic_visit(node)

            def visit_Call(self, node):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr in SET_METHODS:
                    record(node, f".{func.attr}()")
                self.generic_visit(node)

            def visit_SetComp(self, node):
                record(node, "setcomp")
                self.generic_visit(node)

            def visit_Compare(self, node):
                for op in node.ops:
                    if isinstance(op, (ast.In, ast.NotIn)) and any(
                            h in text(node) for h in MEMBERSHIP_HINTS):
                        record(node, "in/not-in")
                        break
                self.generic_visit(node)

        Walker().visit(tree)
    return sites


def test_the_apparatus_set_is_derived_not_remembered():
    """git ls-files plus an import check, never a hand-written list."""
    scripts = apparatus_scripts()
    assert scripts, "the enumeration returned nothing, so this gate is blank"
    for rel in scripts:
        assert (REPO_ROOT / rel).is_file(), rel
    # The six apparatus modules must all be in their own enumeration.
    for module in APPARATUS_MODULES:
        assert f"scripts/{module}.py" in scripts, module
    print(f"✓ {len(scripts)} apparatus scripts, enumerated by import")


def test_every_comparison_site_is_classified():
    """A new set difference cannot land in the apparatus unclassified."""
    sites = enumerate_sites()
    assert sites, "the AST walk found nothing, so this gate is blank"

    unclassified = sorted({
        (rel, func, kind) for rel, func, kind, _line, _src in sites
        if (rel, func, kind) not in INVENTORY
    })
    assert not unclassified, (
        "set/multiset comparison sites with no entry in INVENTORY.\n"
        "Classify each one: state which key it uses, whether that key can "
        "collide within one file, and what kind of comparison it performs.\n"
        + "\n".join(f"  - {r}::{f} [{k}]" for r, f, k in unclassified))
    print(f"✓ all {len(sites)} sites map to a classified inventory entry")


def test_the_inventory_has_no_entries_for_sites_that_are_gone():
    """A stale entry is a claim about code that no longer exists."""
    present = {(rel, func, kind) for rel, func, kind, _l, _s
               in enumerate_sites()}
    stale = sorted(set(INVENTORY) - present)
    assert not stale, (
        "INVENTORY entries whose site no longer exists; delete them:\n"
        + "\n".join(f"  - {r}::{f} [{k}]" for r, f, k in stale))
    print(f"✓ every one of the {len(INVENTORY)} entries names a live site")


def test_the_audit_reconciles_against_its_own_enumeration():
    """The headline figures are computed here, never typed into prose."""
    sites = enumerate_sites()
    keys = {(rel, func, kind) for rel, func, kind, _l, _s in sites}
    cross = {k for k in keys if INVENTORY[k][0] == CROSS_STATE}
    out = {k for k in keys if INVENTORY[k][0] == OUT_OF_SCOPE}

    assert len(cross) + len(out) == len(keys), "a verdict is neither value"
    assert len(keys) == len(INVENTORY), (
        f"{len(keys)} distinct sites against {len(INVENTORY)} entries")

    defective = {k for k in cross if "WAS DEFECTIVE" in INVENTORY[k][1]}
    assert len(cross) == 7, sorted(cross)
    assert len(defective) == 1, sorted(defective)
    assert ("scripts/claim_diff.py", "classify_findings", "BinOp -") \
        in defective
    print(f"✓ {len(sites)} sites, {len(keys)} distinct, {len(cross)} "
          f"cross-state, {len(defective)} found defective")


def test_every_cross_state_entry_states_key_collision_and_comparison():
    """A verdict with no reasoning is the thing this audit was written against."""
    for key, (verdict, reason) in INVENTORY.items():
        if verdict != CROSS_STATE:
            continue
        assert "ey is" in reason or "key" in reason.lower(), key
        assert ("collide" in reason.lower() or "collision" in reason.lower()), (
            f"{key} does not say whether its key can collide within one file")
        assert any(w in reason.lower() for w in
                   ("same-tree", "cross-commit", "two commits", "passes",
                    "multiset", "membership", "union")), (
            f"{key} does not say what kind of comparison it performs")
    print("✓ every cross-state entry states key, collision and comparison")


def test_the_control_a_new_unclassified_site_is_caught():
    """Rule 4: prove the check fires. An absent signal is not a passing one."""
    sites = enumerate_sites()
    keys = {(rel, func, kind) for rel, func, kind, _l, _s in sites}
    planted = keys | {("scripts/newly_added.py", "compare_them", "BinOp -")}
    unclassified = sorted(k for k in planted if k not in INVENTORY)
    assert unclassified == [
        ("scripts/newly_added.py", "compare_them", "BinOp -")], unclassified
    print("✓ an unclassified site is detected, so the check is not inert")


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
