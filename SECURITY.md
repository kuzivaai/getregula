# Security Policy

> Regula is an open-source CLI tool that combines code scanning with
> governance questionnaires, running entirely on the user's local
> machine. It has zero runtime dependencies and makes no network calls
> in its core operations. The attack surface is therefore narrow, but it
> is not nil — see this document for the full posture and how to
> report issues.

## Supported versions

| Version | Supported |
|---|---|
| 2.0.x | ✅ Receives security fixes |
| 1.9.x | ⚠️ Critical security fixes only; 2.0.0 has breaking output/config changes documented in `CHANGELOG.md` |
| < 1.9 | ❌ Unsupported — please upgrade |

There is currently no public PyPI package or GitHub Release for 2.0.0. The
temporary source-install path and its reproducibility limitation are documented
in [`docs/installation.md`](docs/installation.md).

## Reporting a vulnerability

**Please report vulnerabilities privately, not via public GitHub issues.**

Two channels:

1. **GitHub Security Advisory (preferred)** —
   <https://github.com/kuzivaai/getregula/security/advisories/new>
2. **Email** — `support@getregula.com` with the subject line
   `[SECURITY] <short description>`

Include in your report:

- A clear description of the issue
- Steps to reproduce (a minimal repro is ideal)
- The Regula version and Python version you tested against
- Your suggested severity (critical / high / medium / low)
- Whether you intend to publish your own write-up after disclosure

## What to expect

| Stage | Target |
|---|---|
| Acknowledgement | within 72 hours |
| Initial triage and severity confirmation | within 7 days |
| Fix or mitigation in `main` | within 30 days for high/critical |
| Coordinated disclosure | within 90 days from initial report |

If a fix takes longer, you will be told why and given an updated
estimate. The maintainer will not silently ignore a reported issue.

We follow a 90-day coordinated disclosure timeline by default — if you
need a different timeline (regulatory deadlines, embargoed industry
disclosure, etc.), include that in your initial report.

## What is in scope

- The `regula` CLI commands and the `scripts/` package
- The `references/` data files when consumed by the scanner
- The benchmark runner (`benchmarks/label.py`, `benchmarks/synthetic/run.py`)
- The MCP server (`scripts/mcp_server.py`)

## What is out of scope

- Issues in third-party tools that integrate with Regula (Claude Code,
  Cursor, Windsurf, IDE plugins) — please report those upstream
- Issues in optional dependencies (`pyyaml`, `tree-sitter`,
  `weasyprint`, `sentry-sdk`) — please report those to the upstream
  package maintainers
- The landing page (`index.html`, `uae.html`, `de.html`,
  `pt-br.html`) is hosted statically and has no server-side code; web
  vulnerabilities there are out of scope
- Attacks that require an attacker to already control the user's
  shell, filesystem, or Python interpreter — Regula cannot defend
  against a compromised host

## Current security posture

Security results are scoped by tool, dependency set and Git ref. A green result
for one scope is not described as a clean bill of health for another.

| Check | Last verified | Result and scope |
|---|---|---|
| `bandit -c pyproject.toml -r scripts/` | 2026-08-27, current working tree | 0 findings across 44,228 lines; 16 specifically disabled findings remain visible in Bandit's metrics |
| `pip-audit -r <locked-all-extras-export>` | 2026-08-19, all optional extras | 1 advisory in WeasyPrint 68.1 with no fixed release; four `cryptography` 46.0.7 advisories were removed by locking 50.0.0 |
| Core dependency declaration | 2026-08-19 | No required third-party packages; this does not describe optional extras |
| Semgrep | 2026-08-19 | Not re-run in this audit; no current zero-finding claim is made |
| `regula self-test` | Release gate | Final branch result is recorded by CI before merge/release |
| Custom regression suite | Collection manifest | 2,922 pytest-collected tests; collection count is not a pass result |
| Release provenance | 2026-08-27 | No current public release artefact exists; provenance and registry-install gates therefore remain outstanding |
| CodeQL static analysis | 2026-08-20 analysis; dispositions verified 2026-08-22 | Analysis `1646686319` at main commit `fe1f5e7` produced 41 results. All 41 were reviewed and individually dispositioned; the current main-branch CodeQL open count is 0. This is a reviewed static-analysis result, not proof of no vulnerabilities. |
Source: reproducible commands and evidence are documented in [`docs/TRUST.md`](docs/TRUST.md); live workflow state is available in [GitHub Actions](https://github.com/kuzivaai/getregula/actions).

The full posture is in [`docs/TRUST.md`](docs/TRUST.md), Section 7.

## Known unhardened areas

Honest list, also recorded in `docs/TRUST.md`:

- **No SOC 2 Type II.** Regula is a local CLI, not a hosted service —
  there is no infrastructure to audit. The equivalent is the open-source
  code itself.
- **No third-party penetration test.** The attack surface is the user's
  local machine + opt-in network calls. Open for review at
  <https://github.com/kuzivaai/getregula>.
- **No formal CVE program (yet).** The next public CVE we receive will
  also be the moment we register as a CNA. Until then, GitHub Security
  Advisory + email.

## CodeQL static-analysis results (individually dispositioned)

Default-branch CodeQL analysis `1646686319` completed at commit
`fe1f5e72702339bcea550ff17b813bb0a8bc5aac` with **41 results**. On
2026-08-22 every result was reviewed and dispositioned on its own alert; no
query, path or rule was disabled. The current open CodeQL count for main is
**0**. The earlier PR 55 zero was baseline-relative and did **not** establish
this inventory result. Use the [live code-scanning list](https://github.com/kuzivaai/getregula/security/code-scanning)
for current state and the dated [finding inventory](docs/security/SECURITY-FINDINGS-2026-08-19.md)
for IDs, controls and residual risks.

**36 × `py/path-injection` (across 8 files, enumerated in the
[dated finding inventory](docs/security/SECURITY-FINDINGS-2026-08-19.md)).**
These results trace the caller-selected scan root and the guard operations themselves. Content reads
reject escaping symlinks, named pipes, non-regular files and oversized files;
POSIX main walkers pin parent directories with `os.fwalk`; and REST targets
must pass lexical and resolved containment within the server launch directory
before handler probes. CodeQL does not model these project-specific boundaries
as sanitisers. Each alert was therefore dismissed as a false positive with an
alert-specific evidence comment.

That disposition is not an assertion of perfect path safety. Windows lacks the
POSIX `O_NOFOLLOW`/`fwalk` controls, and `compliance_check.py` reopens a by-name
read after its 64 MiB content-cache budget is exhausted. Those ancestor-race
residuals require an attacker able to mutate the selected tree concurrently and
remain documented rather than erased.

**5 × other results, each reviewed individually:**

| Result | Location | Disposition |
|---|---|---|
| `py/polynomial-redos` | `classify_risk.py` | False positive after mitigation: custom regexes require explicit `--rules` opt-in and the accepted subset rejects unbounded repeats, multiple variable repeats, quantified groups, lookarounds and backreferences; pattern and input sizes are capped. This is bounded risk, not a general proof about arbitrary regexes. |
| `py/clear-text-logging-sensitive-data` | `tests/helpers.py` | Used in tests: assertion helper for synthetic credential fixtures, with no production secret source. |
| `py/redos` | `tests/test_security_hardening.py` | Used in tests: deliberately catastrophic expression executed under a CPU-time meter to prove the detector observes the failure mode. |
| `py/redos` | `tests/test_classification.py` | Used in tests: hostile expression used to assert custom-pattern rejection. |
| `py/incomplete-url-substring-sanitization` | `tests/test_build_regulations.py` | Used in tests: checks rendered output contains a URL; it is not a URL sanitizer. |

The prior `py/bad-tag-filter` result and three superseded API path flows are
absent from the terminal main analysis after their fixes. Absence from this
analysis is narrower evidence than a penetration test.

Regula's own PR scan also reports one high-risk biometrics *product indicator*
in `scripts/cli_scan.py`. It is not a CodeQL vulnerability and must not be
counted as one; it remains visible for separate product-governance review.

## How to verify the current source independently

```bash
git clone https://github.com/kuzivaai/getregula.git
cd getregula
git checkout COMMIT_SHA
git rev-parse HEAD
python3 tests/test_classification.py
python3 -m pytest tests/ -q
python3 -m scripts.cli self-test
python3 -m scripts.cli doctor

# Optional local build inspection; requires the `build` package
python3 -m build
sha256sum dist/*
```

Replace `COMMIT_SHA` with the full public commit you intend to evaluate. A
locally built hash identifies that build; it cannot be compared with a trusted
current registry artefact because none exists. Do not treat source installation
as release attestation. A restored release process must add an immutable public
tag, checksums, provenance attestations, registry installation tests, and
rollback instructions before this limitation can be closed.

## Acknowledgements

Researchers who have responsibly disclosed issues will be credited
here, with their consent. The list is currently empty — be the first.
