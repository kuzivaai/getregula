# Security Policy

> Regula is an open-source CLI tool that runs on the user's local
> machine. It has zero runtime dependencies and makes no network calls
> in its core scanner. The attack surface is therefore narrow, but it
> is not nil — see this document for the full posture and how to
> report issues.

## Supported versions

| Version | Supported |
|---|---|
| 1.6.x | ✅ Receives security fixes |
| 1.5.x | ⚠️ Critical security fixes only |
| < 1.5 | ❌ Unsupported — please upgrade |

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
| Custom regression suite | Each commit | 926 / 926 |

The full posture is in [`docs/TRUST.md`](docs/TRUST.md), Section 7.

## Known unhardened areas

Honest list, also recorded in `docs/TRUST.md`:

- **No SOC 2 Type II.** Regula is a local CLI, not a hosted service —
  there is no infrastructure to audit. The equivalent is the open-source
  code itself.
- **No third-party penetration test.** The attack surface is the user's
  local machine + opt-in network calls. Open for review at
  <https://github.com/kuzivaai/getregula>.
- **Sigstore release signing — on the roadmap, not yet shipped.**
  Current method: reproducible builds from `python3 -m build` against
  the published commit hash. v1.7.0 will add Sigstore-keyless signing
  via PyPI's trusted publishing flow.
- **No formal CVE program (yet).** The next public CVE we receive will
  also be the moment we register as a CNA. Until then, GitHub Security
  Advisory + email.

## How to verify a release independently

```bash
# Verify the wheel matches the published commit
git clone https://github.com/kuzivaai/getregula.git
cd getregula
git checkout v1.6.1
python3 -m build
sha256sum dist/regula_ai-1.6.1-py3-none-any.whl

# Compare against the wheel served by PyPI
pip download --no-deps -d /tmp/verify regula-ai==1.6.1
sha256sum /tmp/verify/regula_ai-1.6.1-py3-none-any.whl
```

The two SHA-256 hashes should match. If they do not, **stop and report
to `support@getregula.com` immediately** — that would indicate either a
PyPI compromise or a non-reproducible build, both of which we want to
investigate.

## Acknowledgements

Researchers who have responsibly disclosed issues will be credited
here, with their consent. The list is currently empty — be the first.
