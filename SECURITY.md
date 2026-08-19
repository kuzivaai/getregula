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

Security results are scoped by tool, dependency set and Git ref. A green result
for one scope is not described as a clean bill of health for another.

| Check | Last verified | Result and scope |
|---|---|---|
| `bandit -c pyproject.toml -r scripts/ hooks/` | 2026-08-19, working tree based on `edeeb32` | 0 findings after bounded URL/XML hardening; the pre-change run found 14 (3 low, 11 medium, 0 high) |
| `pip-audit -r <locked-all-extras-export>` | 2026-08-19, all optional extras | 1 advisory in WeasyPrint 68.1 with no fixed release; four `cryptography` 46.0.7 advisories were removed by locking 50.0.0 |
| Core dependency declaration | 2026-08-19 | No required third-party packages; this does not describe optional extras |
| Semgrep | 2026-08-19 | Not re-run in this audit; no current zero-finding claim is made |
| `regula self-test` | Release gate | Final branch result is recorded by CI before merge/release |
| Custom regression suite | Collection manifest | 3,112 pytest-collected tests; collection count is not a pass result |
| PyPI provenance attestation (PEP 740, Trusted Publishing) | Each release | Expected on wheel and sdist; verify the individual release rather than infer it |
| CodeQL static analysis | 2026-08-19 | PR 55 merge-ref analysis returned 0 results; default branch still exposes 43 open alerts from its last analysed commit |
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

At the 2026-08-19 snapshot, the default branch exposed **43 open alerts** from
analysis commit `65eb5b9421ab6ab75a13c47bbf6c3aee1e6209dc`. The exact PR 55
merge-ref analysis (`dbefebfaee3403145d6736c42b6c809c795f69d6`) returned zero
results. That is evidence about two different refs: the default-branch alerts
are not represented as closed until a post-merge default-branch analysis says
so. Use the [live code-scanning list](https://github.com/kuzivaai/getregula/security/code-scanning)
for current state and the dated [finding inventory](docs/security/SECURITY-FINDINGS-2026-08-19.md)
for the exact snapshot and dispositions.

**37 × `py/path-injection` (across 8 files).** A code scanner's job is to read
files from a folder the user points it at, so its file-reading paths are tainted
by design. Every scanning command routes through `walk_project_files()` /
`is_safe_to_scan()`, which reject named pipes, out-of-root symlinks and `.git`;
the optional REST API (`api_server.py`) additionally rejects any path outside the
current working directory (`Path.resolve().relative_to(cwd)`) and caps request
bodies at 1 MB. CodeQL does not model these containment checks as sanitisers, so
the taint path is reported even though the guard is present. `tests/test_hostile_sweep.py`
exercises this whole class against a deliberately hostile directory tree.

**6 × other rules, each reviewed individually:**

| Alert | Location | Assessment |
|---|---|---|
| `py/polynomial-redos` | `classify_risk.py` | Reachable only via *user-supplied* custom-rule patterns, which already pass `_compile_custom_pattern` (rejects nested quantifiers and patterns over 500 chars; unit-tested). Polynomial, not exponential; self-inflicted. Low risk, mitigated. |
| `py/bad-tag-filter` | `claim_auditor.py` | A genuine minor robustness gap in an internal docs-audit tool — **fixed**: the `<script>` / `<style>` blanking regex now tolerates whitespace and attributes in the closing tag. |
| `py/clear-text-logging-sensitive-data` | `tests/helpers.py` | Test helper that prints an assertion failure; the "secret" is a synthetic, char-code-constructed test credential. Test-only false positive. |
| `py/redos` | `tests/test_security_hardening.py` | A deliberately hostile regex used to exercise the scanner's ReDoS reporting. Test-only fixture, not an executed application regex. |
| `py/redos` | `tests/test_classification.py` | A regex inside the test that *asserts* ReDoS protection works. Test-only. |
| `py/incomplete-url-substring-sanitization` | `tests/test_build_regulations.py` | A test asserting rendered HTML contains a URL substring, not a security check. Test-only false positive. |

Regula's own PR scan also reports one high-risk biometrics *product indicator*
in `scripts/cli_scan.py`. It is not a CodeQL vulnerability and must not be
counted as one; it remains visible for separate product-governance review.

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
