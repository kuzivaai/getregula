#!/usr/bin/env python3
# regula-ignore
"""Classify each claim at HEAD as present at a base commit, or introduced.

WHY THIS EXISTS
---------------
`claim_auditor.py --diff-base main` scans whole files. Any file the diff
touches is scanned in full, so a branch that edits one line of a document
inherits every unsourced claim already in it. The proposed remedy is an
"introduced-claim condition": fail only on claims present at HEAD and absent
at the merge base. Whether that condition is sufficient is a measurement, not
an opinion, and this module is that measurement.

It is committed rather than left in a scratchpad on purpose. The F25 exposure
figure of 22/46 is unanswerable today because the script that produced it was
never committed, and an independent attempt got 29/53 on the same corpus at
the same commit. A number whose apparatus is gone is not a measurement.

CLAIM IDENTITY
--------------
A claim is keyed on **(repo-relative path, normalised claim text)**.

Normalisation lowercases, collapses runs of whitespace, and strips a trailing
full stop. It deliberately does NOT normalise digits, so 42.0% and 51% are
different claims.

The consequence, stated plainly: a paragraph edited so that its claim TEXT
changes reads as newly introduced. That is intended. See
docs/adr/0001-claim-identity.md for the argument and the rejected alternative.

Identity is on the claim snippet, not the paragraph, so editing prose around a
claim does not re-flag it. Only editing the claim itself does, and editing a
claim is re-asserting it.

HOLDING THE INSTRUMENT CONSTANT
-------------------------------
Claim DETECTION changed between 6daacd2d and b310821: NUMERIC_CLAIM,
STRUCTURAL_REFS, is_exempt_number and strip_noise all differ. Running each
tree's own auditor would therefore change two variables at once, the content
and the detector, and measurement rule 2 forbids that. So this module runs ONE
detector, the one at HEAD, against BOTH content states.

That means copying HEAD's `claim_auditor.py` into the base worktree before
extracting. This is not the "measure with a copy" failure that rule 1 warns
about. That failure was REPO_ROOT resolving to a scratchpad, so repo-file
citations broke and sourced paragraphs counted as unsourced. Here REPO_ROOT
resolves to a complete, real checkout of the base commit, which is exactly the
tree being measured, and `_assert_repo_root` verifies it at runtime. Rule 1
says do not fork the instrument; holding one instrument against two specimens
is what rule 2 requires.

USAGE
  python3 scripts/claim_diff.py --base main
  python3 scripts/claim_diff.py --base main --json
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import claim_auditor as ca  # noqa: E402

REPO_ROOT = ca.REPO_ROOT

# Bucket predicate. Shared so that any figure of the form "N of M are the
# programme's own working documents" is produced here rather than by hand.
# `data/published_count_manifest.json` lists docs/improvement/ under
# excluded_by_design as "programme working documents"; .claude/ is agent
# configuration.
BUCKETS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("docs/improvement/", ("docs/improvement/",)),
    ("benchmarks/ + docs/benchmarks/", ("benchmarks/", "docs/benchmarks/")),
    (".claude/rules/", (".claude/rules/",)),
)

_WS = re.compile(r"\s+")


def normalise_claim(text: str) -> str:
    """Canonical form of a claim snippet for identity purposes.

    Digits are NOT normalised. Changing 42.0% to 51% must read as a different
    claim, because it is one.
    """
    return _WS.sub(" ", text.strip().lower()).rstrip(".")


def claim_key(path: str, snippet: str) -> tuple[str, str]:
    return (path, normalise_claim(snippet))


def bucket_of(path: str) -> str:
    for label, prefixes in BUCKETS:
        if path.startswith(prefixes):
            return label
    return "everything else"


def _git(*args: str, cwd: Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                          text=True, check=True).stdout


def _assert_repo_root(module, expected: Path) -> None:
    """Measurement rule 1. Fail loudly if the module resolved elsewhere."""
    if Path(module.REPO_ROOT).resolve() != expected.resolve():
        raise RuntimeError(
            f"{module.__name__}.REPO_ROOT is {module.REPO_ROOT}, expected "
            f"{expected}. Refusing to measure: every repo-file citation would "
            f"resolve against the wrong tree."
        )


def extract_claims(module, root: Path, paths: list[str]) -> set[tuple[str, str]]:
    """Every claim the detector finds in `paths` under `root`.

    Claims, not findings. The question this module answers is whether the same
    CLAIM existed at the base, regardless of whether it was sourced there.
    Sourcing is the gate's business; existence is identity's business.
    """
    _assert_repo_root(module, root)
    keys: set[tuple[str, str]] = set()
    for rel in paths:
        fp = root / rel
        if not fp.exists() or fp.suffix.lower() not in module.SCANNED_SUFFIXES:
            continue
        raw = fp.read_text(encoding="utf-8", errors="replace")
        cleaned = module.strip_noise(raw, fp.suffix.lower())
        for start, _end, para in module.split_paragraphs(cleaned):
            blocked: list[tuple[int, int]] = []
            for pat in module.STRUCTURAL_REFS:
                blocked += [(m.start(), m.end()) for m in pat.finditer(para)]
            tags = [(m.start(), m.end())
                    for m in module.HTML_TAG.finditer(para)]

            def blocked_at(pos: int) -> bool:
                return any(lo <= pos < hi for lo, hi in blocked)

            def in_tag(pos: int) -> bool:
                return any(lo <= pos < hi for lo, hi in tags)

            def add(kind: str, m) -> None:
                snip = m.group(0).strip()
                if kind == "numeric" and module.is_exempt_number(snip):
                    return
                if kind in ("numeric", "currency") and blocked_at(m.start()):
                    return
                if kind == "attributed" and in_tag(m.start()):
                    return
                keys.add(claim_key(rel, snip[:120]))

            for m in module.NUMERIC_CLAIM.finditer(para):
                add("numeric", m)
            for m in module.CURRENCY_CLAIM.finditer(para):
                add("currency", m)
            for m in module.SUPERLATIVE_CLAIM.finditer(para):
                add("superlative", m)
            for m in module.ATTRIBUTED_CLAIM.finditer(para):
                add("attributed", m)
    return keys


def classify_findings(findings: list[dict],
                      base_keys: set[tuple[str, str]]) -> list[dict]:
    """Mark each finding present-at-base or introduced, and bucket it.

    The whole decision of this module, in two lines, deliberately kept as a
    pure function of (findings, base_keys) so a test can drive it without a
    repository. Mutates in place and returns the same list for convenience.
    """
    for f in findings:
        f["bucket"] = bucket_of(f["file"])
        f["present_at_base"] = claim_key(f["file"], f["snippet"]) in base_keys
    return findings


def findings_at_head(base: str) -> list[dict]:
    """The findings `--diff-base <base>` reports, as records."""
    _assert_repo_root(ca, REPO_ROOT)
    allow = ca.load_allowlist()
    out: list[dict] = []
    for fp in ca.files_diff_base(base):
        rep = ca.scan_file(fp, allow)
        for f in rep.findings:
            out.append({
                "file": rep.path,
                "line": f.claim.line,
                "kind": f.claim.kind,
                "snippet": f.claim.snippet,
                "reason": f.reason,
            })
    return out


def base_worktree(base_sha: str, tmp: Path) -> Path:
    """A clean checkout of `base_sha`, carrying HEAD's detector."""
    wt = tmp / "base"
    subprocess.run(["git", "worktree", "add", "--detach", str(wt), base_sha],
                   cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    # One instrument, two specimens. See the module docstring.
    shutil.copy2(REPO_ROOT / "scripts" / "claim_auditor.py",
                 wt / "scripts" / "claim_auditor.py")
    return wt


def load_base_module(wt: Path):
    """Import the base worktree's auditor under a distinct module name.

    Registered in sys.modules BEFORE exec_module because @dataclass resolves
    its own module by name while the class body is being processed; without
    the registration it raises AttributeError on NoneType.
    """
    import importlib.util
    name = "claim_auditor_base"
    spec = importlib.util.spec_from_file_location(
        name, wt / "scripts" / "claim_auditor.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return mod


def classify(base: str) -> dict:
    base_sha = _git("merge-base", base, "HEAD", cwd=REPO_ROOT).strip()
    head_sha = _git("rev-parse", "HEAD", cwd=REPO_ROOT).strip()
    findings = findings_at_head(base)
    paths = sorted({f["file"] for f in findings})

    tmp = Path(tempfile.mkdtemp(prefix="claim-diff-"))
    try:
        wt = base_worktree(base_sha, tmp)
        base_mod = load_base_module(wt)
        base_keys = extract_claims(base_mod, wt, paths)
    finally:
        subprocess.run(["git", "worktree", "remove", "--force",
                        str(tmp / "base")], cwd=REPO_ROOT,
                       capture_output=True, text=True, check=False)
        shutil.rmtree(tmp, ignore_errors=True)

    classify_findings(findings, base_keys)

    return {
        "head": head_sha,
        "base": base,
        "base_sha": base_sha,
        "tree": str(REPO_ROOT),
        "total": len(findings),
        "present_at_base": sum(1 for f in findings if f["present_at_base"]),
        "introduced": sum(1 for f in findings if not f["present_at_base"]),
        "base_claim_keys": len(base_keys),
        "findings": findings,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default="main")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    r = classify(args.base)
    if args.json:
        print(json.dumps(r, indent=2))
        return 0

    print(f"HEAD {r['head'][:7]}  base {args.base} = {r['base_sha'][:7]}  "
          f"tree {r['tree']}")
    print(f"findings at HEAD          : {r['total']}")
    print(f"  present at merge base   : {r['present_at_base']}")
    print(f"  introduced by branch    : {r['introduced']}")
    print(f"distinct claim keys at base: {r['base_claim_keys']}")
    print()
    # Every count below comes from the predicate that built the set.
    labels = [lbl for lbl, _ in BUCKETS] + ["everything else"]
    width = max(len(x) for x in labels)
    print(f"  {'bucket'.ljust(width)}   total  at-base  introduced")
    for lbl in labels:
        rows = [f for f in r["findings"] if f["bucket"] == lbl]
        if not rows:
            continue
        at = sum(1 for f in rows if f["present_at_base"])
        print(f"  {lbl.ljust(width)}  {len(rows):6d}  {at:7d}  "
              f"{len(rows) - at:10d}")
    print(f"  {'TOTAL'.ljust(width)}  {r['total']:6d}  "
          f"{r['present_at_base']:7d}  {r['introduced']:10d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
