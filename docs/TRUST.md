# Trust Pack — Regula

> The 2026 B2B buyer's playbook is "Evidence Pack first, pitch deck never."
> This document is Regula's Trust Pack: a single source of truth for the
> questions a sceptical buyer, auditor, or compliance officer asks before
> they will consider running it on their codebase.
>
> Every claim below is paired with the **exact shell command** anyone can
> run to verify it independently. If a claim is not verifiable, it is not
> in this document.

---

## Contents

1. [Who built it and what is it](#1-who-built-it-and-what-is-it)
2. [What Regula does (and does not) claim](#2-what-regula-does-and-does-not-claim)
3. [Reproducibility — verify every published number](#3-reproducibility)
4. [Tamper-evidence — verify the audit trail](#4-tamper-evidence)
5. [Transparency — verify every finding](#5-transparency)
6. [Independent verification — read the source](#6-independent-verification)
7. [Security posture — what is hardened, what is not](#7-security-posture)
8. [Privacy posture — what data Regula collects](#8-privacy-posture)
9. [Vendor evaluation answers](#9-vendor-evaluation-answers)
10. [Trust centre summary](#10-trust-centre-summary)

---

## 1. Who built it and what is it

Regula is an **open-source command-line tool** that scans source code for
EU AI Act compliance signals at the point of creation. It is licensed
under the Apache License 2.0. The full source is on GitHub at
[github.com/kuzivaai/getregula](https://github.com/kuzivaai/getregula).
PyPI package: [`regula-ai`](https://pypi.org/project/regula-ai/).

It is **not a SaaS, not a hosted service, not an API**. It runs entirely
on the developer's machine. No code, no findings, no telemetry leave the
machine unless the user explicitly opts in to anonymous crash reporting.

It is **not a legal opinion**, not a substitute for a Data Protection
Impact Assessment, not a guarantee of Article 6(3) exemption, and not a
vendor audit. Regula tells you what your code looks like under the EU
AI Act's published rules. The legal interpretation of those signals is
your lawyer's job, not Regula's.

---

## 2. What Regula does (and does not) claim

| Claim | Evidence |
|---|---|
| Detects 8 prohibited AI practices (Article 5 of Regulation (EU) 2024/1689) | `regula classify --text "predictive policing system"` |
| Detects 10 high-risk categories (Annex III + 2 Annex I categories cross-referenced by Article 6(1)) | `regula classify --text "classify_resume function"` |
| Maps every finding to specific articles of the EU AI Act | `regula classify --text "credit scoring model" --format json` |
| Maps every finding to ISO 42001, NIST AI RMF, NIST AI 600-1, NIST CSF 2.0, SOC 2 TSC, ISO 27001, OWASP LLM Top 10, MITRE ATLAS, CRA, ICO/DSIT, LGPD, Marco Legal IA | `cat references/framework_crosswalk.yaml` |
| Generates Annex IV conformity evidence packs | `regula conform .` |
| Generates Annex VIII registration packets | `regula register` |
| Cross-file Article 14 human-oversight detection (Python) | `regula oversight` |
| CycloneDX 1.7 ML-BOM with GPAI signatory annotations | `regula sbom --ai-bom` |
| SHA-256 hash-chained tamper-evident audit log | `regula audit verify` |
| 1,111 unique tests (1,232 pytest-collected), 6 self-tests, 0 known security findings | see [§3](#3-reproducibility) |

| Claim Regula does **NOT** make | Why |
|---|---|
| "Compliant with the EU AI Act" | Compliance is a legal determination. Regula cannot make it. |
| "100% precision" | Regula is intentionally tuned for recall on Annex III/Article 5. False positives at the INFO tier are documented and quantified — see [the precision/recall report](benchmarks/PRECISION_RECALL_2026_04.md). |
| "Audits your AI vendor" | Regula sees your code, not the vendor's. It surfaces vendor names and their published GPAI Code of Practice signatory status, nothing more. |
| "Replaces a DPIA / FRIA / HRIA" | These are organisational processes that involve people, policy, and stakeholder consultation. A static code scanner cannot perform them. |
| "Works on every language" | Python and JS/TS have full AST + cross-file flow. Java/Go/Rust/C/C++ are regex-only. This is documented in [`docs/architecture.md`](architecture.md). |

---

## 3. Reproducibility

> Every number Regula publishes can be reproduced by anyone with a checkout
> of the repo. The commands below run in under 30 seconds total on a laptop.

### 3.1 Internal test suite — 1,111 unique / 1,232 pytest-collected, all green

```bash
git clone https://github.com/kuzivaai/getregula.git
cd getregula
python3 -m pytest tests/ -q
# Expected: 1232 passed (~12 minutes on a laptop — verified 2026-04-25)
# 1,111 unique tests; 121 are duplicated via globals() import binding
# in test_classification.py and therefore collected twice by pytest.
```

Regula also ships a legacy auto-discovery runner for the classification
suite — run `python3 tests/test_classification.py` for its output
(`Results: 932 passed, 0 failed (495 test functions)`). It walks
`globals()` of `tests/test_classification.py`, finds every `test_*`
function, and executes it. The pytest total above covers this suite
plus all dedicated test files (signing, timestamping, evidence format
v1, dependency pinning, and others).

### 3.2 Self-tests — 6 / 6

```bash
python3 -m scripts.cli self-test
# Expected: 6/6 passed
```

Six round-trip assertions covering: prohibited practice detection,
high-risk classification, minimal-risk classification, credential
detection, framework mapping, limited-risk classification.

### 3.3 Doctor — environment health

```bash
python3 -m scripts.cli doctor
# Expected (inside a git repo): 9 passed, 2 info, 0 warn
# Expected (outside a git repo): 9 passed, 2 info, 1 warn
#   The 1 warn is ".gitignore not found" — Regula recommends
#   .gitignore-ing audit artefacts. Add a .gitignore to silence it.
```

Lists every optional dependency, hook installation status, audit
directory writability, and policy file presence. INFO entries for
optional features are not warnings — they are reminders that
`pipx install "regula-ai[yaml,ast]"` would unlock more features.

### 3.4 Synthetic precision + recall — 100 / 100

```bash
python3 benchmarks/synthetic/run.py
# Expected: precision 100% (5 TP, 0 FP), recall 100% (5 TP, 0 FN)
```

13 hand-crafted fixtures covering 5 Article 5 prohibited practices,
5 Annex III high-risk categories, and 3 negative cases. The
ground truth is the human-authored fixture set in
`benchmarks/synthetic/fixtures/`.

### 3.5 OSS precision benchmark — published, sliced, reproducible

The full report is at
[`docs/benchmarks/PRECISION_RECALL_2026_04.md`](benchmarks/PRECISION_RECALL_2026_04.md).

```bash
python3 benchmarks/label.py score
# Random corpus (blind-labelled, production code): 83.5% precision (N=115)
```

The headline precision is **83.5%** (N=115), measured on production code
from a random corpus of 50 Python AI repos selected via GitHub API
(pool of 276, random seed 42) and blind-labelled (labeller saw only
file path, code context, and finding description — no project name,
README, or purpose). This measures what users see with default
`--skip-tests` settings. Per-tier: `ai_security` (85%), `agent_autonomy`
(83%), `limited_risk` (88%), `minimal_risk` (100%). The `high_risk`
tier (33%) remains weakest — 6 subcategories now require `--domain`
declaration or import fingerprinting to fire (v1.7.0+).
Full methodology: `benchmarks/results/random_corpus/METHODOLOGY.json`.

### 3.6 Security posture — bandit, semgrep, pip-audit

```bash
# Bandit and pip-audit are lightweight:
pip install bandit pip-audit
bandit -c pyproject.toml -r scripts/ hooks/
# Expected: 0 low / 0 medium / 0 high
pip-audit
# Expected: 0 vulnerabilities (zero runtime deps)

# Semgrep is heavier (~150 MB) and optional. Skip if you only have
# capacity for the quick pass:
pip install semgrep
semgrep --config p/security-audit --config p/python scripts/ hooks/
# Expected: 0 findings (200 rules, 129 files)
```

Per the [comparative SAST research](https://semgrep.dev/blog/2021/python-static-analysis-comparison-bandit-semgrep/),
running both bandit and semgrep is the standard hardened-Python audit.
Regula passes both at the published version. Bandit's project config
is in `pyproject.toml [tool.bandit]` with every project-level skip
documented and rationalised.

Bandit project config in `pyproject.toml [tool.bandit]` documents every
project-level skip with rationale. Hard checks (B101 assert, B102 exec,
B301 pickle, B501–B507 ssl/tls, B601–B602 shell injection, B608 sql
injection) remain enabled.

---

## 4. Tamper-evidence

Regula maintains a SHA-256 hash-chained audit log of every scan it runs
on a developer's machine. This is the same construction used by
RFC 6962 Certificate Transparency.

```bash
regula audit show           # human-readable view
regula audit show --format json
regula audit verify         # walks the chain, recomputes every hash
# Expected: "Audit chain verified (N entries, no tampering detected)"
```

If a single byte of any past entry has been altered, `regula audit verify`
will report the exact entry where the chain breaks. The user can verify
this themselves by editing one character of `~/.regula/audit/*.jsonl` and
re-running the verify command.

### Optional: third-party RFC 3161 timestamping

```bash
regula audit anchor --tsa https://freetsa.org/tsr
```

This sends a SHA-256 of the current audit log head to a public RFC 3161
Time Stamp Authority and stores the signed timestamp token. Anyone with
the token can later prove the audit log existed in its current form at
that time. Regula does not require trust in any specific TSA — the user
sets `REGULA_TSA_URL` to the authority of their choice.

---

## 5. Transparency

Every Regula finding is paired with:

1. The article of the EU AI Act it maps to (e.g. Article 9, Article 14)
2. The ISO 42001 control it relates to (e.g. A.6.3, A.6.6)
3. The NIST AI RMF function (e.g. GOVERN, MAP, MEASURE, MANAGE)
4. The exact pattern in `scripts/risk_patterns.py` that fired
5. The exact `file:line` in the user's code

```bash
regula classify --text "classify_resume function" --format json
# Returns the full structured envelope with all five fields above
```

There are no opaque ML scores. There are no "trust the model" outputs.
Every finding is traceable to a specific regular expression in a
specific file in the open-source repo. A reviewer can read the pattern
and decide for themselves whether it is too broad or too narrow.

---

## 6. Independent verification

| Resource | Where |
|---|---|
| Source code | <https://github.com/kuzivaai/getregula> |
| PyPI package | <https://pypi.org/project/regula-ai/> |
| Direct contact | `support@getregula.com` |
| Issue tracker | <https://github.com/kuzivaai/getregula/issues> |
| Security disclosures | <https://github.com/kuzivaai/getregula/security/advisories/new> or `support@getregula.com` |
| Test suite | `tests/` (1,111 unique tests, 1,232 pytest-collected; 495 functions in the legacy `tests/test_classification.py` custom runner) |
| Pattern definitions | `scripts/risk_patterns.py` |
| Framework mapping | `references/framework_crosswalk.yaml` |
| Pre-commit hook source | `hooks/pre_tool_use.py` |
| MCP server source | `scripts/mcp_server.py` |
| Benchmark corpus | `benchmarks/labels.json` |
| Primary research citations | `references/FETCH.md` |
| Changelog | `CHANGELOG.md` |
| Known gaps and limitations | `TODO.md` |

The repository is intentionally legible. There are no compiled binaries,
no obfuscated bytecode, no generated code committed without the
generator. A reviewer can read every line of every file Regula will run
on their machine.

---

## 7. Security posture

### 7.1 What is hardened

- **Zero runtime dependencies.** Regula's core only uses Python's
  standard library. Optional features (YAML parsing, AST analysis, PDF
  export) are explicit opt-ins via `pipx install "regula-ai[yaml,ast,pdf]"`.
  Verify with `pip show regula-ai`.
- **Deterministic output.** Same input + same policy file produces
  byte-identical JSON output. Verify by running `regula check --format
  json` twice and `diff`-ing the results.
- **Schema-versioned JSON envelope.** Every JSON command output includes
  `format_version`, `regula_version`, `command`, `timestamp`, and
  `exit_code` so machine consumers can detect schema drift.
- **Hooks run in subprocess isolation.** The pre-commit hook is a
  separate Python script and cannot affect the parent process state.
- **No network calls in the core scanner.** `regula check` is fully
  offline. Network calls are scoped to opt-in commands: `regula feed`
  (governance news), `regula audit anchor` (RFC 3161 TSA), and
  `regula bias` (CrowS-Pairs dataset download, when network is available).
- **All `urllib.urlopen` call sites enforce `http(s)` only.** The
  `_require_http_url()` guard rejects `file://`, `ftp://`, `data://`
  schemes before any network call. Verified by semgrep
  `dynamic-urllib-use-detected` rule.
- **XML feed parsing prefers `defusedxml`** when available, falls back
  to `xml.etree` with a 10 MiB size cap to defuse XML-bomb vectors.
- **Credential detection has tested heuristics.** See `tests/`
  `test_classification.py::test_credentials_*` for the regression set.

### 7.2 What is NOT hardened

Honest list of things a buyer should ask about and what Regula's answer
currently is:

| Question | Answer |
|---|---|
| Do you have a SOC 2 Type II report? | No. Regula is an open-source CLI tool, not a hosted service. There is no Regula infrastructure to audit. The equivalent is the open-source code itself plus the bandit/semgrep/pip-audit clean state. |
| Have you had a third-party penetration test? | No. The attack surface is the user's local machine + opt-in network calls listed above. The code is open for review. |
| Do you have a CVE program? | Yes — [`SECURITY.md`](../SECURITY.md) defines the disclosure flow, supported versions, and target response times. Private disclosure via GitHub Security Advisory or `support@getregula.com`. The next public CVE we receive will also be the moment we register as a CNA. |
| Do you sign releases with Sigstore? | Not yet. Releases are reproducible from source via `python3 -m build`. |
| Do you have an SBOM for your own releases? | Yes — Regula generates one of itself: `regula sbom --ai-bom` from a checkout. |

### 7.3 Supply chain security

Regula's supply chain attack surface is intentionally minimal.

- **Zero runtime dependencies.** The core scanner uses only the Python
  standard library. Verify with `pip show regula-ai` — the `Requires`
  field is empty. This eliminates transitive dependency compromise as
  an attack vector.
- **Reproducible builds from source.** Anyone can rebuild the wheel from
  a tagged commit and compare the SHA-256 against the PyPI artefact.
  See [`SECURITY.md`](../SECURITY.md) "How to verify a release
  independently" for the exact steps.
- **No compiled binaries or obfuscated bytecode.** Every file in the
  repository is human-readable source. There is no `.so`, `.dll`,
  `.pyc`, or minified code committed.
- **Optional dependencies are explicit opt-ins.** `pyyaml`,
  `tree-sitter`, `weasyprint`, and `sentry-sdk` are declared as extras
  in `pyproject.toml` (e.g. `pipx install "regula-ai[yaml,ast,pdf]"`).
  They are never pulled in by a bare `pip install regula-ai`.
- **SBOM self-generation.** Regula can generate a CycloneDX 1.7 ML-BOM
  of itself from any checkout: `regula sbom --ai-bom`. This includes
  component hashes and dependency declarations.
- **OpenSSF Scorecard.** Adopting the OpenSSF Scorecard
  (<https://scorecard.dev>) for automated supply chain hygiene checks
  is on the roadmap. It is not yet run in CI — do not treat it as a
  current achievement.

### 7.4 Incident response

The formal vulnerability disclosure process is defined in
[`SECURITY.md`](../SECURITY.md). The key commitments are:

| Stage | Target |
|---|---|
| Acknowledgement of report | within 72 hours |
| Initial triage and severity confirmation | within 7 days |
| Fix or mitigation merged to `main` | within 30 days for high/critical |
| Coordinated disclosure | within 90 days from initial report |

If a fix takes longer than the target, the reporter will receive a
written explanation and an updated estimate. Reports are never
silently ignored.

The 90-day coordinated disclosure timeline is the default. Reporters
who require a different timeline (e.g. regulatory deadlines or
embargoed industry disclosure) should state this in the initial report.

Report privately via:
1. **GitHub Security Advisory** —
   <https://github.com/kuzivaai/getregula/security/advisories/new>
2. **Email** — `support@getregula.com` with subject `[SECURITY] <short
   description>`

### 7.5 Reported vulnerabilities

None as of the published version. Report security issues privately by
opening a GitHub Security Advisory at
<https://github.com/kuzivaai/getregula/security/advisories/new>.

---

## 8. Privacy posture

### 8.1 What Regula collects from a user's machine

**By default: nothing.** No telemetry, no usage stats, no error reports.

`regula doctor` will report `Telemetry — disabled` on a fresh install.

### 8.2 What Regula collects if telemetry is opted in

If the user runs `regula telemetry enable`, AND the operator has set
`_SENTRY_DSN` in `scripts/telemetry.py` to a Sentry endpoint of their
choice, anonymous Python crash reports (stack trace + Regula version +
OS string) will be sent to the configured DSN on uncaught exceptions.

The published PyPI build has `_SENTRY_DSN = ""` (empty). This means
**even if the user opts in, no data is sent unless they self-host a
Sentry DSN.** This is by design: Regula is a tool for compliance teams,
many of whom cannot legally exfiltrate any data to a third party.

Verify with:

```bash
grep -n "_SENTRY_DSN" $(pip show regula-ai | grep Location | cut -d: -f2)/scripts/telemetry.py
# Expected: _SENTRY_DSN = ""
```

### 8.3 What Regula sends over the network

Only when the user explicitly invokes the relevant command:

| Command | Endpoint | Data sent |
|---|---|---|
| `regula feed` | curated RSS/Atom feed URLs in `scripts/feed.py` (IAPP, EDPB, ICO, etc.) | HTTP GET only — no user data sent |
| `regula audit anchor` | user-configured RFC 3161 TSA (default `freetsa.org`) | A SHA-256 hash of the local audit log head. The hash itself reveals nothing about the user's code. |
| `regula bias` | `raw.githubusercontent.com/nyu-mll/crows-pairs/master/...` | HTTP GET only. Falls back to bundled 20-pair sample if network unavailable. |

`regula check`, `regula classify`, `regula gap`, `regula oversight`,
`regula sbom`, `regula register`, `regula conform`, `regula doctor`, and
the MCP server **make no network calls at all**. They run fully
offline.

---

## 9. Vendor evaluation answers

The questions a 2026 procurement team will ask, with copy-pasteable
answers.

**Q: What is the deployment model?**
A: Local-only command-line tool. Installs via `pipx install regula-ai`.
No accounts, no servers, no SaaS tier exists.

**Q: Where is data stored?**
A: All scan output, audit logs, and conformity packs are written to
the user's local filesystem under `~/.regula/` and the project
directory. Nothing is uploaded.

**Q: What is the licensing model?**
A: Apache License 2.0 (with EUPL-1.2 dual-licence option). Commercial
use, redistribution, and modification are permitted. There is no paid
tier. The maintainer accepts sponsorships but does not gate features
behind payment.

**Q: How do you handle GDPR / DPA / SCCs?**
A: Regula is a data processor only in the trivial sense that it
processes the user's own source code on the user's own machine. No
personal data leaves the user's environment. No DPA is required because
no controller-processor relationship is established.

**Q: What is the support model?**
A: Best-effort via `support@getregula.com` and GitHub Issues. Response
time is not contractually guaranteed. For enterprises that need a
paid SLA, email `support@getregula.com` to discuss a separate support
agreement.

**Q: How do we verify Regula's claims independently?**
A: Run the commands in section 3 above. Read the patterns in
`scripts/risk_patterns.py`. Read the framework mappings in
`references/framework_crosswalk.yaml`. Read the test suite. Read the
benchmark report. Cite the published methodology in your own internal
audit.

**Q: Who maintains the regulatory mapping?**
A: A single maintainer at present. Every regulatory claim is paired
with an article reference and a primary-source citation. The AICDI
2025 figures cited in `docs/landscape.md` are page-cited against the
published PDF (ISBN 978-92-3-100863-4, DOI 10.54678/YJWP8855); the
`references/FETCH.md` file records the SHA-256 of the canonical PDF.

**Q: What happens if you stop maintaining Regula?**
A: The repository is open source under Apache 2.0. Anyone can fork it. The
test suite is comprehensive enough that a competent maintainer can
verify a fork. The pattern definitions are flat data files that
anyone can update without touching the engine.

---

## Reading order for evaluators

If you have **15 minutes**, run the commands in [§3](#3-reproducibility)
and read [§2](#2-what-regula-does-and-does-not-claim).

If you have **1 hour**, also read
[`docs/landscape.md`](landscape.md) (the AICDI gap mapping) and
[`docs/benchmarks/PRECISION_RECALL_2026_04.md`](benchmarks/PRECISION_RECALL_2026_04.md)
(the precision/recall report).

If you have **half a day**, also read
[`scripts/risk_patterns.py`](../scripts/risk_patterns.py),
[`references/framework_crosswalk.yaml`](../references/framework_crosswalk.yaml),
and [`docs/architecture.md`](architecture.md).

If anything in this document is unclear, ambiguous, or unverifiable,
that is a bug. Open an issue.

---

## 10. Trust centre summary

Quick-reference table of all security and compliance evidence available
in this repository. Every row links to a verifiable artefact.

| Evidence | Location | What it covers |
|---|---|---|
| Vulnerability disclosure policy | [`SECURITY.md`](../SECURITY.md) | Supported versions, reporting channels, response timelines, scope |
| Trust pack (this document) | [`docs/TRUST.md`](TRUST.md) | Reproducibility, tamper-evidence, transparency, security and privacy posture, vendor evaluation Q&A |
| Licence | [`LICENSE.txt`](../LICENSE.txt) | Apache License 2.0 (with EUPL-1.2 dual-licence option) |
| Third-party notices | [`NOTICE`](../NOTICE) | Attribution for bundled data and referenced standards |
| Architecture overview | [`docs/architecture.md`](architecture.md) | Module map, data flow, scan pipeline, AST vs regex coverage |
| Scope and limitations | [`docs/what-regula-does-not-do.md`](what-regula-does-not-do.md) | Explicit list of what Regula is not and cannot do |
| Precision and recall benchmark | [`docs/benchmarks/PRECISION_RECALL_2026_04.md`](benchmarks/PRECISION_RECALL_2026_04.md) | Labelled corpus, methodology, per-tier and per-project breakdown |
| Framework crosswalk data | [`references/framework_crosswalk.yaml`](../references/framework_crosswalk.yaml) | EU AI Act ↔ ISO 42001 / NIST AI RMF / SOC 2 / etc. mappings |
| Pattern definitions | [`scripts/risk_patterns.py`](../scripts/risk_patterns.py) | All detection regexes, grouped by risk tier and category |
| Test suite | `tests/` | 1,111 unique tests (1,232 pytest-collected) |
| Self-test | `regula self-test` | 6 round-trip assertions |
| Environment health | `regula doctor` | 11 checks (9 pass + 2 info on a clean install) |
| SBOM | `regula sbom --ai-bom` | CycloneDX 1.7 ML-BOM from any checkout |
| Changelog | [`CHANGELOG.md`](../CHANGELOG.md) | Version history and breaking changes |

**Machine-readable security metadata.** A `security.txt` file
(per [RFC 9116](https://www.rfc-editor.org/rfc/rfc9116)) is on the
roadmap but not yet published. Until it is in place, the canonical
security contact is `support@getregula.com` and the disclosure process
is defined in [`SECURITY.md`](../SECURITY.md).
