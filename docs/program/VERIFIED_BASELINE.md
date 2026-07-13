# VERIFIED_BASELINE

Status: DRAFT (uncommitted). Produced by the Evidence-Driven Product Improvement
Program, Phases 0–1. All facts below were reproduced locally against the exact
commit unless a weaker classification is stated.

## Baseline identity

| Field | Value | Evidence |
|---|---|---|
| Repo root | `/Users/kmuzondo/getregula` (fresh clone) | runtime |
| Remote | `https://github.com/kuzivaai/getregula.git` | `git clone` |
| Branch | `main` (= `origin/main` = `origin/HEAD`) | `git status` |
| HEAD commit | `cf170c663422277c6d0f7e6e1d53d299736daa45` | `git rev-parse HEAD` |
| HEAD author/date | `github-actions[bot]`, 2026-07-13 11:06:54 +0000, "chore: weekly metrics [skip ci]" | `git log` |
| Last human commit | `6ffd5757…` Kuziva Muzondo, 2026-07-10 | `git log` |
| Working tree | clean | `git status --porcelain` (empty) |
| Package version | `1.7.4` (pyproject.toml:7 and scripts/constants.py:15 agree) | source |
| `git describe` | `v1-9-g27731d8` | `git describe --tags` |

## Release provenance

| Field | Value | Evidence |
|---|---|---|
| Latest PyPI release | `regula-ai 1.7.4`, uploaded 2026-07-06 09:21:07 UTC | pypi.org/pypi/regula-ai/json |
| 1.7.4 wheel sha256 | `36e4a6b3b91dd2989a9163310fed1e35559e6fc0697c93a6bd042e6514ab3940` | PyPI JSON |
| PyPI owner | `kmvm14` | PyPI JSON |
| Tag `v1.7.4` → commit | `47cbfb0f120bcbf7d949ea003f09c498cf629dcc` | `git rev-list -n1 v1.7.4` |
| Floating `v1` → commit | `b4b41bee28a5db475f9b3858875b02402b66a1ca` | `git rev-list -n1 v1` |
| HEAD ahead of `v1.7.4` | 14 commits | `git rev-list --count v1.7.4..HEAD` |
| Release trigger | `v[0-9]+.[0-9]+.[0-9]+*` (NOT `v*`; avoids `v1` alias re-publish, documented 2026-07-08 incident) | .github/workflows/release.yml |

## Runtime / environment

| Field | Value | Evidence |
|---|---|---|
| Local Python | 3.11.8 | `python3 --version` |
| CI Python matrix | 3.10, 3.11, 3.12, 3.13 | .github/workflows/ci.yaml |
| Core dependencies | 0 required (stdlib-only); optional extras: yaml, ast, test, pdf, sentry/telemetry, web, signing | pyproject.toml |
| Tracked files | 538 | `find` |
| `scripts/*.py` | 110 | `find` |
| `tests/test_*.py` files | 60 | `find` |
| CI workflows | 9 (ci, benchmark, pages, regula-scan, release, test-action, triage, weekly-digest, weekly-metrics) | .github/workflows |

## Verification suite result (at cf170c6, Python 3.11.8) — reproduced

| Command | Exit | Result |
|---|---|---|
| `python3 tests/test_classification.py` | 0 | 1362 passed, 0 failed, 8 skipped (888 test functions) |
| `pytest tests/ -q` | 0 | 2488 passed, 32 skipped (2520 collected), 454s |
| `python3 -m scripts.cli self-test` | 0 | 6/6 passed |
| `python3 -m scripts.cli doctor` | 0 | 6 passed, 6 info |
| `python3 -m scripts.cli security-self-check` | 0 | 0 unexpected findings (18 total, 18 acceptable) |

## Generated-facts mechanism

- Generator: `scripts/site_facts.py` → writes `data/site_facts.json`.
- Enforcer: `scripts/claim_auditor.py --verify-facts` (CI job `claim-audit` in ci.yaml).
- Enforced canonical numbers: **only** `419` (tier_regexes), `61` (commands),
  `12` (frameworks), `8` (languages) — `scripts/claim_auditor.py:682-687`.
- NOT enforced: the published "tests passing" number (see DEFECT_REGISTER DEF-001).

## Local-only tooling (gitignored; referenced by AGENTS.md but not in repo)

`CLAUDE.md`, `.claude/`, `hooks/` — excluded via `.gitignore`. `site/assess/uae.html`
appears relocated to `site/regions/uae.html` (per ci.yaml deploy comment). These
are documentation-accuracy notes, not defects.

## Limitations of this baseline

- Verification executed on Python 3.11.8 only; 3.10/3.12/3.13 and Windows/macOS-CI/Linux-CI not locally reproduced.
- No CLI runtime behaviour beyond self-test/doctor/security-self-check was exercised.
- Benchmark suite not executed.
- Single-agent investigation; no independent review performed or claimed.
