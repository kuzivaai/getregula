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
| 1.9.x | ✅ Receives security fixes |
| 1.7.x | ⚠️ Critical security fixes only; upgrade — 1.9.0 is a drop-in replacement (see `docs/VERSIONING.md`: the jump is a version realignment, not a breaking change) |
| < 1.7 | ❌ Unsupported — please upgrade |

The latest release is on PyPI at <https://pypi.org/project/regula-ai/>.

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
- The `hooks/` package (pre/post tool-use, stop hooks)
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

| Check | Last verified | Status |
|---|---|---|
| `bandit -c pyproject.toml -r scripts/ hooks/` | Each release | 0 low / 0 medium / 0 high |
| `semgrep --config p/security-audit --config p/python` | Each release | 0 findings on 200 rules / 129 files |
| `pip-audit` | Each release | 0 vulnerabilities (zero runtime deps) |
| `regula self-test` | Each commit | 6 / 6 |
| Custom regression suite | Each commit | 2,723 pytest-collected tests |
| PyPI provenance attestation (PEP 740, Trusted Publishing) | Each release | ✅ attached to wheel + sdist, Sigstore-backed |
| CodeQL static analysis | Each push | workflow green; open alerts triaged below, never suppressed |
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

## CodeQL static-analysis alerts (open, triaged, not suppressed)

CodeQL runs on every push. The dated snapshot recorded **42 open high-severity
alerts**; use the [live code-scanning list](https://github.com/kuzivaai/getregula/security/code-scanning) for current state.
They are listed here in full, with the reasoning for each, and left open in the
GitHub Security tab. We do not dismiss or suppress security alerts:
a compliance tool that clears its own dashboard by waving alerts away is not one
you should trust. The CodeQL *workflow* passes; these alerts do not gate it.

**37 × `py/path-injection` (across 8 files).** A code scanner's job is to read
files from a folder the user points it at, so its file-reading paths are tainted
by design. Every scanning command routes through `walk_project_files()` /
`is_safe_to_scan()`, which reject named pipes, out-of-root symlinks and `.git`;
the optional REST API (`api_server.py`) additionally rejects any path outside the
current working directory (`Path.resolve().relative_to(cwd)`) and caps request
bodies at 1 MB. CodeQL does not model these containment checks as sanitisers, so
the taint path is reported even though the guard is present. `tests/test_hostile_sweep.py`
exercises this whole class against a deliberately hostile directory tree.

**5 × other rules, each reviewed individually:**

| Alert | Location | Assessment |
|---|---|---|
| `py/polynomial-redos` | `classify_risk.py` | Reachable only via *user-supplied* custom-rule patterns, which already pass `_compile_custom_pattern` (rejects nested quantifiers and patterns over 500 chars; unit-tested). Polynomial, not exponential; self-inflicted. Low risk, mitigated. |
| `py/bad-tag-filter` | `claim_auditor.py` | A genuine minor robustness gap in an internal docs-audit tool — **fixed**: the `<script>` / `<style>` blanking regex now tolerates whitespace and attributes in the closing tag. |
| `py/clear-text-logging-sensitive-data` | `tests/helpers.py` | Test helper that prints an assertion failure; the "secret" is a synthetic, char-code-constructed test credential. Test-only false positive. |
| `py/redos` | `tests/test_classification.py` | A regex inside the test that *asserts* ReDoS protection works. Test-only. |
| `py/incomplete-url-substring-sanitization` | `tests/test_build_regulations.py` | A test asserting rendered HTML contains a URL substring, not a security check. Test-only false positive. |

If you are evaluating Regula: its own scanner is held to the same standard it
applies to your code. Every alert is visible, triaged in public, and either
explained or fixed — never silenced.

## How to verify a release independently

```bash
# Verify the wheel matches the published commit
git clone https://github.com/kuzivaai/getregula.git
cd getregula
git checkout v1.7.3
python3 -m build
sha256sum dist/regula_ai-1.7.3-py3-none-any.whl

# Compare against the wheel served by PyPI
pip download --no-deps -d /tmp/verify regula-ai==1.7.3
sha256sum /tmp/verify/regula_ai-1.7.3-py3-none-any.whl

# Verify PyPI provenance attestations (PEP 740, Sigstore-backed)
python3 -m pip install pypi-attestation-models
python3 -m pypi_attestations verify /tmp/verify/regula_ai-1.7.3-py3-none-any.whl
```

The two SHA-256 hashes should match. If they do not, **stop and report
to `support@getregula.com` immediately** — that would indicate either a
PyPI compromise or a non-reproducible build, both of which we want to
investigate.

## Acknowledgements

Researchers who have responsibly disclosed issues will be credited
here, with their consent. The list is currently empty — be the first.
