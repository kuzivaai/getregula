#!/usr/bin/env python3
"""Derive Regula's public delivery surfaces from the mechanisms that ship them."""
from __future__ import annotations

import argparse
import email.parser
import hashlib
import html
import importlib
import json
import re
import subprocess
import sys
import tarfile
import unicodedata
import zipfile
from collections import Counter, deque
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10: only the project readme key is needed.
    tomllib = None

sys.path.insert(0, str(Path(__file__).parent))

REPO = Path(__file__).resolve().parent.parent
OUTPUT = REPO / "data/public_claim_surfaces.json"
REPORT = REPO / "docs/improvement/PUBLIC-SURFACE-DISCOVERY.md"
POLICY = REPO / "data/public_surface_policy.json"
TEXT_SITE = {".html", ".htm", ".txt", ".xml", ".json"}
LINK_RE = re.compile(r"(?<!!)\[[^]]*\]\(([^)#?]+)(?:#[^)]*)?\)")
TAG_RE = re.compile(r"<[^>]+>")

# Languages the site actually ships. Derived at test time from the lang
# attribute of every tracked page (see tests/test_public_claim_integrity.py);
# repeated here as the authoring contract for PROHIBITED_CLAIMS, which must
# carry one arm per shipped language or the guard is blind to that locale.
CLAIM_LANGUAGES = ("en", "de", "pt")


def fold_for_claim_match(text: str) -> str:
    """Reduce copy to the form the prohibited-claim patterns are written against.

    Three defects made the previous raw-text match unsound, each demonstrated
    against shipped pages before this was written:

    1. Inline markup split a phrase, so `zero <strong>network</strong> calls`
       evaded the English pattern that exists precisely to catch it.
    2. Accented copy is written with HTML entities, so `c&oacute;digo` never
       matched a pattern containing `codigo`, let alone `código`.
    3. Accents alone defeated matching even after decoding.

    So: decode entities, fold to ASCII-compatible letters, casefold, and
    collapse whitespace. Patterns are therefore authored lowercase and
    unaccented; `test_claim_patterns_are_written_in_folded_form` enforces that.
    """
    decoded = html.unescape(text)
    decomposed = unicodedata.normalize("NFKD", decoded)
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", stripped.casefold())


def claim_match_variants(text: str) -> tuple[str, ...]:
    """Both readings of a source: markup kept, and markup replaced by space.

    Matching only the tag-stripped form would lose claims that live in
    attribute values (`aria-label`, `alt`, `content`), which the raw match used
    to cover. Matching only the raw form is what let markup-split phrases
    through. Each pattern is tried against both and the results unioned, so
    coverage is a strict superset of the previous behaviour and no join
    artefact can invent a match that neither reading contains.
    """
    return (fold_for_claim_match(text),
            fold_for_claim_match(TAG_RE.sub(" ", html.unescape(text))))


# claim class -> language -> pattern, matched against folded text.
# Non-English arms are translations of the English claim, not quotations of
# shipped copy; each is proved live by a planted negative control per
# (class, language) pair in tests/test_public_claim_integrity.py. A hedged
# statement must not match: the German and Portuguese homepages say the local
# core does not upload scanned files, which is a bounded claim and stays green.
PROHIBITED_CLAIMS = {
    "legal classification": {
        "en": re.compile(
            r"(?:(?:regula|scanner|tool|command)\s+(?:automatically\s+)?"
            r"classif(?:y|ies)\b.{0,120}(?:system|snippet).{0,80}risk tier|"
            r"classifies your system\b)",
            re.I,
        ),
        "de": re.compile(
            r"(?:(?:regula|scanner|tool|werkzeug)\s+(?:automatisch\s+)?"
            r"(?:klassifiziert|stuft)\b.{0,120}(?:system|code).{0,80}"
            r"risiko(?:stufe|klasse|kategorie)|"
            r"klassifiziert ihr system\b|bestimmt die risiko(?:stufe|klasse))",
            re.I,
        ),
        "pt": re.compile(
            r"(?:(?:regula|scanner|ferramenta)\s+(?:automaticamente\s+)?"
            r"classifica\b.{0,120}sistema.{0,80}(?:nivel|categoria|grau) de risco|"
            r"classifica o seu sistema\b|determina o nivel de risco)",
            re.I,
        ),
    },
    "compliance scan": {
        "en": re.compile(r"(?:compliance scanner|compliance issues|assess compliance gaps)", re.I),
        "de": re.compile(
            r"(?:compliance.scanner|konformitatsscanner|compliance.probleme|"
            r"konformitatsprobleme|compliance.lucken bewerten)",
            re.I,
        ),
        "pt": re.compile(
            r"(?:scanner de conformidade|verificador de conformidade|"
            r"problemas de conformidade|avalia(?:r)? lacunas de conformidade)",
            re.I,
        ),
    },
    "obligation determination": {
        "en": re.compile(r"tells? you which obligations apply", re.I),
        "de": re.compile(r"sagt ihnen,? welche pflichten (?:gelten|zutreffen|anwendbar sind)", re.I),
        "pt": re.compile(r"diz(?: a voce)?,? quais obrigacoes se aplicam", re.I),
    },
    "universal network": {
        "en": re.compile(
            r"(?:zero network calls|no API calls|no data leaves|"
            r"zero data transmission|never leaves your machine|"
            r"your code never leaves|nothing leaves your machine)",
            re.I,
        ),
        "de": re.compile(
            r"(?:(?:null|keine) netzwerk(?:aufrufe|verbindungen|anfragen)|"
            r"keine daten verlassen|"
            r"verlasst (?:niemals|nie) (?:ihren|deinen|den) (?:rechner|computer)|"
            r"ihr code verlasst (?:niemals|nie))",
            re.I,
        ),
        "pt": re.compile(
            r"(?:(?:zero|sem|nenhuma) chamadas? de rede|nenhum dado sai|"
            r"nunca sa(?:i|em) d(?:a|o) (?:sua|seu) (?:maquina|computador)|"
            r"seu codigo nunca sai)",
            re.I,
        ),
    },
    "DPA determination": {
        "en": re.compile(r"no DPA (?:is )?required", re.I),
        "de": re.compile(r"(?:kein avv|keine auftragsverarbeitung|kein auftragsverarbeitungsvertrag) (?:ist )?erforderlich", re.I),
        "pt": re.compile(r"(?:nenhum|sem) (?:dpa|contrato de tratamento de dados)(?: e)? (?:necessario|exigido)", re.I),
    },
    "auditor completeness": {
        "en": re.compile(r"auditor.ready|audit.ready", re.I),
        "de": re.compile(r"(?:auditbereit|auditsicher|prufungsbereit|pruferfertig)", re.I),
        "pt": re.compile(r"pront[oa]s? para auditoria", re.I),
    },
    # Bounded, not `.*`. Folding collapses newlines, so an unbounded run would
    # span a whole document and pair an "every number" in the intro with a
    # "reproducible" thousands of characters later. 200 characters is about two
    # sentences, which is the range over which the two halves form one claim.
    "universal reproducibility": {
        "en": re.compile(r"every (?:metric|number).{0,200}?(?:reproduc|CI.enforced)", re.I),
        "de": re.compile(r"jede (?:kennzahl|zahl|metrik).{0,200}?(?:reproduzierbar|ci.erzwungen)", re.I),
        "pt": re.compile(r"(?:cada|toda) (?:metrica|numero).{0,200}?(?:reproduzivel|garantid[oa] (?:por|no) ci)", re.I),
    },
    "unbounded runtime": {
        "en": re.compile(r"(?:in|under|takes?) (?:10|30) seconds", re.I),
        "de": re.compile(r"(?:in|unter|dauert) (?:10|30) sekunden", re.I),
        "pt": re.compile(r"(?:em|menos de|leva) (?:10|30) segundos", re.I),
    },
    "zero security findings": {
        "en": re.compile(r"zero known security findings|0 known security findings", re.I),
        "de": re.compile(r"(?:null|keine|0) bekannten? sicherheits(?:befunde|probleme)", re.I),
        "pt": re.compile(
            r"(?:zero|nenhum[a]?|0) (?:vulnerabilidades|falhas|problemas) de seguranca conhecid[oa]s",
            re.I,
        ),
    },
}


def claim_violations(text: str) -> list[tuple[str, str]]:
    """Every (claim class, language) prohibited claim present in ``text``."""
    variants = claim_match_variants(text)
    return [(name, language)
            for name, arms in PROHIBITED_CLAIMS.items()
            for language, pattern in sorted(arms.items())
            if any(pattern.search(variant) for variant in variants)]


class DiscoveryError(RuntimeError):
    """Discovery failed closed."""


def _git(root: Path, *args: str) -> list[str]:
    try:
        run = subprocess.run(["git", *args], cwd=root, text=True,
                             capture_output=True, check=False)
    except OSError as exc:
        raise DiscoveryError(f"git unavailable: {exc}") from exc
    if run.returncode:
        raise DiscoveryError(f"git {' '.join(args)} failed: {run.stderr.strip()}")
    return [line for line in run.stdout.splitlines() if line]


def tracked(root: Path) -> set[str]:
    return set(_git(root, "ls-files"))


def _stable(channel: str, source: str, destination: str, kind: str) -> str:
    key = "\0".join((channel, source, destination, kind)).encode()
    return f"{channel}:{hashlib.sha256(key).hexdigest()[:16]}"


def record(channel: str, source: str, destination: str, basis: str,
           kind: str, claim_capable: bool, classification: str,
           reason: str) -> dict[str, Any]:
    return {
        "stable_id": _stable(channel, source, destination, kind),
        "channel": channel, "source": source, "destination": destination,
        "discovery_basis": basis, "content_kind": kind,
        "claim_capable": claim_capable, "classification": classification,
        "reason": reason,
    }


def website_records(root: Path, files: set[str]) -> list[dict[str, Any]]:
    workflows = [p for p in (".github/workflows/ci.yaml", ".github/workflows/pages.yml") if p in files]
    bodies = "\n".join((root / p).read_text(encoding="utf-8") for p in workflows)
    if not re.search(r"upload-pages-artifact@[\s\S]*?path:\s*['\"]?\.?/?site['\"]?", bodies):
        raise DiscoveryError("GitHub Pages publish root could not be derived")
    rows = []
    for rel in sorted(p for p in files if p.startswith("site/")):
        suffix = Path(rel).suffix.lower()
        claim = suffix in TEXT_SITE
        kind = "web-page" if suffix in {".html", ".htm"} else (
            "machine-readable" if suffix in {".txt", ".xml", ".json"} else "asset")
        dest = "/" + rel.removeprefix("site/")
        if dest.endswith("/index.html"):
            dest = dest[:-10]
        elif dest == "/index.html":
            dest = "/"
        rows.append(record("website", rel, dest,
                           "GitHub Pages workflow uploads tracked site/ as artifact root",
                           kind, claim, "active_product" if claim else "non_claim_asset",
                           "deployed reader or machine-readable content" if claim else "deployed non-claim asset"))
    return rows


def _project_fields(pyproject: str) -> tuple[str, Any]:
    if tomllib is not None:
        project = tomllib.loads(pyproject)["project"]
    else:
        project_match = re.search(r"(?ms)^\[project\]\s*$\n(.*?)(?=^\[|\Z)", pyproject)
        project_body = project_match.group(1) if project_match else ""
        readme_match = re.search(
            r'''(?m)^\s*readme\s*=\s*(?:["']([^"']+)["']|\{[^}\n]*\bfile\s*=\s*["']([^"']+)["'][^}\n]*\})\s*(?:#.*)?$''',
            project_body,
        )
        description_match = re.search(r'''(?m)^\s*description\s*=\s*["']([^"']*)["']\s*(?:#.*)?$''', project_body)
        project = {
            "description": description_match.group(1) if description_match else None,
            "readme": next((value for value in readme_match.groups() if value), None) if readme_match else None,
        }
    return project.get("description"), project.get("readme")


def package_records(root: Path, files: set[str]) -> list[dict[str, Any]]:
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    _, readme = _project_fields(pyproject)
    if isinstance(readme, dict):
        readme = readme.get("file")
    if not isinstance(readme, str) or readme not in files:
        raise DiscoveryError("pyproject project.readme is missing or untracked")
    return [
        record("package", "pyproject.toml#project.description", "wheel:METADATA:Summary;sdist:PKG-INFO:Summary",
               "PyPA core metadata generated from pyproject [project]", "package-summary", True,
               "active_product", "published package summary"),
        record("package", readme, "wheel:METADATA:Description;sdist:PKG-INFO:Description",
               "pyproject project.readme long-description source", "package-long-description", True,
               "active_product", "published wheel and sdist long description"),
    ]


def _markdown_reachable(root: Path, files: set[str]) -> set[str]:
    queue = deque(["README.md"])
    seen: set[str] = set()
    while queue:
        rel = queue.popleft()
        if rel in seen or rel not in files or Path(rel).suffix.lower() != ".md":
            continue
        seen.add(rel)
        body = (root / rel).read_text(encoding="utf-8", errors="strict")
        for raw in LINK_RE.findall(body):
            target = (Path(rel).parent / raw).as_posix()
            target = str(Path(target))
            if target in files and target.endswith(".md"):
                queue.append(target)
    return seen


def docs_records(root: Path, files: set[str]) -> list[dict[str, Any]]:
    rows = []
    for rel in sorted(_markdown_reachable(root, files)):
        needs_policy = rel == "CHANGELOG.md" or rel.startswith("docs/improvement/")
        rows.append(record("repository_docs", rel,
                           f"https://github.com/kuzivaai/getregula/blob/main/{rel}",
                           "repository-relative Markdown link reachability from README.md",
                           "repository-document", True, "needs_policy" if needs_policy else "active_product",
                           "delivery-reachable record requires explicit current/historical/internal disposition" if needs_policy
                           else "README-reachable public documentation"))
    return rows


def _yaml_descriptors(path: Path) -> list[tuple[str, str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    section = "metadata"
    current = "action"
    rows: list[tuple[str, str, str]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        top = re.match(r"^(inputs|outputs):\s*$", line)
        if top:
            section = top.group(1); current = ""; i += 1; continue
        item = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)
        if section in {"inputs", "outputs"} and item:
            current = item.group(1); i += 1; continue
        desc = re.match(r"^(\s*)(name|description):\s*(.*)$", line)
        if desc and (len(desc.group(1)) == 0 or section in {"inputs", "outputs"}):
            key, value = desc.group(2), desc.group(3).strip().strip("'\"")
            if value in {">-", "|", "|-", ">"}:
                indent = len(desc.group(1)); parts = []; i += 1
                while i < len(lines) and (not lines[i].strip() or len(lines[i]) - len(lines[i].lstrip()) > indent):
                    if lines[i].strip(): parts.append(lines[i].strip())
                    i += 1
                value = " ".join(parts); i -= 1
            rows.append((section, current if section != "metadata" else "action", key + ": " + value))
        i += 1
    if not rows:
        raise DiscoveryError("action.yml descriptors could not be parsed")
    return rows


def action_records(root: Path, files: set[str]) -> list[dict[str, Any]]:
    if "action.yml" not in files:
        return []
    return [record("action", f"action.yml#{section}.{name}.{index}", "GitHub Marketplace/action runtime",
                   "tracked action.yml user-facing metadata", f"action-{section}-descriptor", True,
                   "active_product", value)
            for index, (section, name, value) in enumerate(_yaml_descriptors(root / "action.yml"))]


class _ParserCaptured(Exception):
    def __init__(self, parser: argparse.ArgumentParser): self.parser = parser


def _real_parser(root: Path) -> argparse.ArgumentParser:
    sys.path.insert(0, str(root / "scripts"))
    cli = importlib.import_module("cli")
    original = argparse.ArgumentParser.parse_args
    def capture(parser: argparse.ArgumentParser, args=None, namespace=None):
        raise _ParserCaptured(parser)
    argparse.ArgumentParser.parse_args = capture
    try:
        cli.main([])
    except _ParserCaptured as caught:
        return caught.parser
    except Exception as exc:
        raise DiscoveryError(f"CLI parser construction failed: {exc}") from exc
    finally:
        argparse.ArgumentParser.parse_args = original
    raise DiscoveryError("CLI parser was not constructed")


def cli_records(root: Path, files: set[str]) -> list[dict[str, Any]]:
    parser = _real_parser(root)
    rows = []
    queue = deque([("regula", parser)])
    while queue:
        path, current = queue.popleft()
        source = "scripts/cli.py#" + path
        rows.append(record("cli", source, path, "registered argparse parser tree",
                           "cli-parser", True, "active_product",
                           "registered parser description/help/epilogue and exit semantics"))
        for action in current._actions:
            if isinstance(action, argparse._SubParsersAction):
                for name, child in sorted(action.choices.items()): queue.append((f"{path} {name}", child))
            else:
                for option in action.option_strings:
                    rows.append(record("cli", source + ":" + option, f"{path} {option}",
                                       "registered argparse option", "cli-option", True,
                                       "active_product", action.help or "registered option semantics"))
    return rows


def mcp_records(root: Path, files: set[str]) -> list[dict[str, Any]]:
    sys.path.insert(0, str(root / "scripts"))
    try:
        tools = importlib.import_module("mcp_server").TOOLS
    except Exception as exc:
        raise DiscoveryError(f"MCP registry import failed: {exc}") from exc
    names = [tool["name"] for tool in tools]
    if names != sorted(names) or len(names) != len(set(names)):
        raise DiscoveryError("MCP tools/list registry must have unique deterministic name order")
    return [record("mcp", f"scripts/mcp_server.py#TOOLS.{tool['name']}", f"tools/list:{tool['name']}",
                   "actual MCP tools/list registry", "mcp-tool-descriptor", True,
                   "active_product", json.dumps({"description": tool.get("description"),
                                                  "inputSchema": tool.get("inputSchema")}, sort_keys=True))
            for tool in tools]


def apply_policy(root: Path, rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    payload = json.loads((root / "data/public_surface_policy.json").read_text(encoding="utf-8"))
    by_source = {row["source"]: row for row in rows}
    exclusions = []
    seen = set()
    for entry in payload.get("dispositions", []):
        source = entry["source"]
        if source in seen: raise DiscoveryError(f"duplicate policy source: {source}")
        seen.add(source)
        if source not in by_source: raise DiscoveryError(f"stale policy entry: {source}")
        if entry["classification"] not in {"historical_record", "internal_record", "non_claim_asset"}:
            raise DiscoveryError(f"invalid narrow policy disposition: {source}")
        row = by_source[source]
        row["classification"] = entry["classification"]
        row["claim_capable"] = bool(entry.get("claim_capable", row["claim_capable"]))
        row["reason"] = entry["reason"]
        exclusions.append(row.copy())
    missing = sorted(row["source"] for row in rows if row["classification"] == "needs_policy")
    if missing: raise DiscoveryError(f"missing policy disposition: {', '.join(missing)}")
    return rows, exclusions


def verify_package_artifacts(root: Path, dist: Path) -> None:
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    expected_summary, readme = _project_fields(pyproject)
    if not isinstance(expected_summary, str):
        raise DiscoveryError("pyproject project.description is missing or unsupported")
    if isinstance(readme, dict):
        readme = readme.get("file")
    if not isinstance(readme, str):
        raise DiscoveryError("pyproject project.readme is missing or unsupported")
    expected_body = (root / readme).read_text(encoding="utf-8").strip()
    wheels = sorted(dist.glob("*.whl")); sdists = sorted(dist.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise DiscoveryError("package verification requires exactly one wheel and one sdist")
    with zipfile.ZipFile(wheels[0]) as archive:
        names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        if len(names) != 1: raise DiscoveryError("wheel METADATA missing or ambiguous")
        wheel_meta = archive.read(names[0]).decode("utf-8")
    with tarfile.open(sdists[0], "r:gz") as archive:
        members = [m for m in archive.getmembers() if m.name.count("/") == 1 and m.name.endswith("/PKG-INFO")]
        if len(members) != 1: raise DiscoveryError("sdist PKG-INFO missing or ambiguous")
        stream = archive.extractfile(members[0])
        if stream is None: raise DiscoveryError("sdist PKG-INFO unreadable")
        sdist_meta = stream.read().decode("utf-8")
    for label, raw in (("wheel METADATA", wheel_meta), ("sdist PKG-INFO", sdist_meta)):
        message = email.parser.Parser().parsestr(raw)
        if message.get("Summary") != expected_summary:
            raise DiscoveryError(f"{label} summary differs from pyproject.toml")
        if message.get_payload().strip() != expected_body:
            raise DiscoveryError(f"{label} long description differs from {readme}")


def discover(root: Path = REPO) -> dict[str, Any]:
    files = tracked(root)
    rows = (website_records(root, files) + package_records(root, files) +
            docs_records(root, files) + action_records(root, files) +
            cli_records(root, files) + mcp_records(root, files))
    rows, exclusions = apply_policy(root, rows)
    rows.sort(key=lambda row: (row["channel"], row["destination"], row["source"]))
    ids = [row["stable_id"] for row in rows]
    if len(ids) != len(set(ids)): raise DiscoveryError("duplicate stable ID")
    claim_files = sorted({r["source"].split("#", 1)[0] for r in rows
                          if r["classification"] == "active_product" and r["claim_capable"]})
    residual = []
    for rel in claim_files:
        path = root / rel
        if not path.is_file(): continue
        body = path.read_text(encoding="utf-8", errors="replace")
        residual.extend({"source": rel, "claim_class": name, "language": language}
                        for name, language in claim_violations(body))
    return {"schema_version": 2, "authority": "repository-derived delivery mechanisms",
            "records": rows,
            "totals": {"channel": dict(sorted(Counter(r["channel"] for r in rows).items())),
                       "classification": dict(sorted(Counter(r["classification"] for r in rows).items()))},
            "exclusions": exclusions,
            "active_not_claim_enforced": [r["stable_id"] for r in rows
                                           if r["classification"] == "active_product" and not r["claim_capable"]],
            "residual_overclaims": residual}


def render_report(payload: dict[str, Any], old_sources: set[str]) -> str:
    sources = {r["source"].split("#", 1)[0] for r in payload["records"]}
    omitted = sorted(sources - old_sources)
    stale = sorted(old_sources - sources)
    lines = ["# Repository-derived public surface discovery", "",
             "Generated by `python3 scripts/public_surface_inventory.py --write`.", "",
             "## Totals", "",
             f"- Records: {len(payload['records'])}",
             f"- Channels: `{json.dumps(payload['totals']['channel'], sort_keys=True)}`",
             f"- Classifications: `{json.dumps(payload['totals']['classification'], sort_keys=True)}`", "",
             "## Old contract versus derived population", "",
             f"- Old path entries: {len(old_sources)}", f"- Derived source files: {len(sources)}",
             f"- Previously omitted source files: {len(omitted)}", f"- Old entries no longer derived: {len(stale)}", ""]
    lines += [f"- `{p}`" for p in omitted] or ["- None"]
    lines += ["", "## Exclusions", ""]
    lines += [f"- `{r['source']}` — {r['classification']}: {r['reason']}" for r in payload["exclusions"]] or ["- None"]
    lines += ["", "## Active surfaces not covered by claim enforcement", ""]
    lines += [f"- `{sid}`" for sid in payload["active_not_claim_enforced"]] or ["- None"]
    lines += ["", "## Residual overclaims", ""]
    lines += [f"- `{r['source']}` — {r['claim_class']}" for r in payload["residual_overclaims"]] or ["- None"]
    lines += ["", "This inventory is the active-surface enforcement authority. The independent merge blocker remains controlling.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--verify-dist", type=Path)
    args = parser.parse_args(argv)
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    old_sources = set(policy["legacy_contract_sources"])
    payload = discover()
    encoded = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    report = render_report(payload, old_sources)
    if args.write:
        OUTPUT.write_text(encoded, encoding="utf-8")
        REPORT.write_text(report, encoding="utf-8")
    if args.check:
        if OUTPUT.read_text(encoding="utf-8") != encoded or REPORT.read_text(encoding="utf-8") != report:
            raise DiscoveryError("generated public-surface inventory/report is stale")
    if args.verify_dist:
        verify_package_artifacts(REPO, args.verify_dist)
    if not args.write and not args.check and not args.verify_dist: print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
