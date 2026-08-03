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

Regula is an **open-source command-line tool** that combines code scanning
with governance questionnaires for EU AI Act compliance at the point of
creation. It is licensed
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
| Machine-readable risk indication as JSON-LD, *aligned to* (not certified against) the DPVCG EU-AIAct vocabulary — a W3C Community Group report, **not a ratified W3C Standard** | `regula dpv .` |
| SHA-256 hash-chained tamper-evident audit log | `regula audit verify` |
| 2,681 unique tests (2,681 pytest-collected), 6 self-tests; versioned open-alert inventory retained | see [§3](#3-reproducibility) and [SECURITY.md](../SECURITY.md) |

| Claim Regula does **NOT** make | Why |
|---|---|
| "Compliant with the EU AI Act" | Compliance is a legal determination. Regula cannot make it. |
| "100% precision" | Regula is intentionally tuned for recall on Annex III/Article 5. False positives at the INFO tier are documented and quantified — see [the precision/recall report](benchmarks/PRECISION_RECALL_2026_04.md). |
| "Audits your AI vendor" | Regula sees your code, not the vendor's. It surfaces vendor names and their published GPAI Code of Practice signatory status, nothing more. |
| "Replaces a DPIA / FRIA / HRIA" | These are organisational processes that involve people, policy, and stakeholder consultation. `regula conform --organisational` provides a structured self-assessment questionnaire for Articles 9/17/27/72, but the output is a self-reported evidence document, not a compliance certificate. A qualified assessor must verify the answers. |
| "Works on every language" | Python and JS/TS have full AST + cross-file flow. Java/Go/Rust/C/C++ are regex-only. This is documented in [`docs/architecture.md`](architecture.md). |

---

## 3. Reproducibility

> This document provides reproduction commands for selected, version-bounded
> facts. Runtime is environment-dependent, and known exceptions are retained.
>
> **One documented exception, stated here rather than discovered later.** The
> landing page's `regula gap` / `regula comply` demo panel (9% overall,
> Article 11 at 25%) does NOT currently reproduce from a clean checkout: it
> was generated on a machine whose copy of the scanned fixture held a
> gitignored `.regula/` directory, which the Article 11 checker credits. A
> clean clone yields 6% and 0%. The generator now refuses to build from
> untracked inputs, so this cannot recur; correcting the published figures
> is pending and tracked as ledger row N43 in
> [`docs/improvement/LEDGER.md`](improvement/LEDGER.md).

### 3.1 Internal test suite — 2,681 [unique](../tests/) / 2,681 pytest-collected, all green

```bash
git clone https://github.com/kuzivaai/getregula.git
cd getregula
python3 -m pytest tests/ -q
# Expected: 2681 passed. Wall-clock is machine-dependent and is NOT a claim;
# it has varied by a factor of two on one laptop in a single day. Quote the
# count, never the duration.
# 2,681 unique tests (sort -u of test IDs equals collected count).
```

Regula also ships a legacy auto-discovery runner for the classification
suite — run `python3 tests/test_classification.py` for its current output.
The runner currently discovers 1,082 functions, a count machine-checked by
`tests/test_published_count_manifest.py`). **Read that line carefully:
`1386 passed` is not a count of tests.** The runner's counter is incremented by
the `assert_true` / `assert_eq` / `assert_false` helpers in `tests/helpers.py`,
so it counts helper assertions, and a test written with a bare `assert`
contributes nothing to it. The figure was **also 1386 when the runner executed
978, 1010, 1011, 1015, 1023, 1033, 1043, 1051, 1056, 1059 and 1060 functions**: 82 functions were added across those
runs and not one of them uses the helpers. **The number to read is the function count
in brackets.** It walks `globals()` of `tests/test_classification.py`,
finds every `test_*` function, and executes it; 437 of those functions
are defined in the file itself, the rest are aliased in from other test
modules. The pytest total above covers this suite
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
# Expected on a fresh install (inside a git repo): 8 passed, 4 info, 0 warn
# Expected on a fresh install (outside a git repo): 8 passed, 4 info, 1 warn
#   The 4 info messages cover: no hooks installed, no ai_officer in policy,
#   telemetry not configured, and no domain declared. The 1 warn (outside
#   git) is ".gitignore not found". Telemetry moves from INFO to PASS only
#   if you both opt in and set REGULA_SENTRY_DSN; 12 checks run either way.
```

Lists every optional dependency, hook installation status, audit
directory writability, and policy file presence. INFO entries for
optional features are not warnings — they are reminders that
`pipx install "regula-ai[yaml,ast]"` would unlock more features.

### 3.4 Synthetic precision and recall: classifier path, all domains declared, prohibited 5/5, high-risk 16/30

```bash
python3 benchmarks/synthetic/run.py
# Expected (corpus v2.0, measured 2026-07-28):
#   prohibited   tp=5   fp=0  fn=0
#   high_risk    tp=16  fp=0  fn=14
# The command prints these as percentages. Prohibited recall is 5/5.
# High-risk recall is 16 of 30 on the classifier path.
```

**38 hand-crafted fixtures** covering 5 Article 5 prohibited practices,
**30** Annex III high-risk categories, and 3 negative cases. Ground truth
is the human-authored fixture set in `benchmarks/synthetic/fixtures/`.

> **This section previously claimed "100 / 100" against a 13-fixture
> corpus (5 high-risk).** The high-risk set was expanded to 30 on
> 28 July 2026 and recall fell to **16 of 30**. The old figure was not a
> misstatement at the time; it was **underpowered** — 5 fixtures happened
> to sample categories that pass. Corrected here rather than left
> unreproducible.
>
> **Gate conditions change this number more than anything else does.** The
> 53% above is the **classifier** path (`report.scan_files`, what `run.py`
> measures) with all eight opt-in domains declared. The **scanner** path
> (`regula check`, what a user actually runs) with **no flags** gives
> **10 of 30** on the same corpus, because opt-in domain suppression and an
> AI-library-indicator requirement gate findings the classifier assigns.
>
> Every figure below is reproducible from `benchmarks/synthetic/RECALL.json`,
> which `scripts/build_recall_artefact.py` produces from an actual run:
> **scanner path, default scan 10/30**; **scanner path, all domains declared
> 16/30**; **scanner path, domains declared with an AI import injected
> 23/30**; **classifier path, all domains declared 16/30**. Prohibited
> recall is **5/5** on every one of them.
>
> **No recall figure may be quoted without naming its path and its gate
> condition** — `claim_auditor --verify-facts` now rejects one that is not.
> The earlier "14/30 domain-declared" and "19/30 with both gates" figures
> are WITHDRAWN as NOT REPRODUCIBLE: the conditions behind them were never
> committed. Full decomposition, including the 17-vs-3
> gates-vs-patterns split, is in
> `benchmarks/headtohead/RESULTS-synthetic-v2-2026-07-28.md`.
>
> **Finding F8 (scanner and classifier disagree) is not supported by the
> artefact.** Under the same gate condition the two paths miss the
> identical 14 fixtures. The divergence previously recorded compared two
> different gate conditions as well as two paths.

### 3.5 OSS precision benchmark — published, sliced, reproducible

The full report is at
[`docs/benchmarks/PRECISION_RECALL_2026_04.md`](benchmarks/PRECISION_RECALL_2026_04.md).

```bash
# Headline precision (blind-labelled random corpus, production code only):
python3 benchmarks/label.py score --corpus random
# Expected: 83.5% precision (N=115)
# Labelled by a single reviewer; no inter-rater agreement measurement
# exists. See benchmarks/README.md.

# Full development corpus (library + application projects, all code):
python3 benchmarks/label.py score
# Expected: 36.8% precision (N=446)
```

**Two corpora, two numbers — both honest, different scopes.** The
headline precision is **83.5%** (N=115, **measured on Regula v1.7.0**,
labelled by a **single reviewer** with no inter-rater agreement
measurement, see [`benchmarks/README.md`](../benchmarks/README.md)),
on production code from a random corpus of 50 Python AI repos selected
via GitHub API (pool of 276, random seed 42) and blind-labelled
(labeller saw only file path, code context, and finding description —
no project name, README, or purpose). This measures what users see
with default `--skip-tests` and domain-gating settings.

> **Version note:** Precision figures are re-measured per release where
> the corpus permits. Pattern additions in v1.7.1+ (including Article
> 5(1)(i) NCII/CSAM detection) are not yet reflected in benchmark
> numbers. Figures cite the Regula version they were measured on. Per-tier:
`ai_security` (85%), `agent_autonomy` (83%), `limited_risk` (88%),
`minimal_risk` (100%). The `high_risk` tier (33%, N=6) remains weakest and is
**statistically unmeasurable** at this sample size — corpus expansion
to N>=30 is required before any meaningful conclusion about high_risk
precision. Six subcategories now require `--domain` declaration or
import fingerprinting to fire. All per-tier figures in this note are the
rounded values from the N=115 published benchmark recorded in
[`benchmarks/README.md`](../benchmarks/README.md).

The development corpus (`python3 benchmarks/label.py score`, no flags)
scores **36.8%** on 446 entries across 5 AI library projects and 12
application projects. The library subset (scikit-learn, langchain,
pydantic-ai, instructor, openai-python) alone is 15.2% — AI framework
infrastructure code is the hardest corpus, analogous to running an SQL
injection scanner on psycopg2 itself. Discovering this 36.8% figure is
not a contradiction of the 83.5% headline (N=115, single reviewer, see
[`benchmarks/README.md`](../benchmarks/README.md)) — it is a different corpus
measuring a different thing.

**Development corpus per-tier precision (v1.7.3, `benchmarks/label.py score --breakdown`):**

| Tier | TP | FP | Precision |
|------|-----|-----|-----------|
| ai_security | 33 | 11 | 75.0% |
| agent_autonomy | 47 | 20 | 70.1% |
| limited_risk | 5 | 3 | 62.5% |
| high_risk | 38 | 38 | 50.0% |
| credential_exposure | 2 | 5 | 28.6% |
| minimal_risk | 39 | 205 | 16.0% |
Source: `benchmarks/results/random_corpus/METHODOLOGY.json`, regenerated by `benchmarks/label.py score --breakdown` on the 446-entry development corpus.

**By corpus type:** application code 66.1% (125 TP, 64 FP); library source code 15.2% (39 TP, 218 FP). Source: [`benchmarks/results/random_corpus/METHODOLOGY.json`](../benchmarks/results/random_corpus/METHODOLOGY.json).

**By language:** Python 36.7% (160 TP, 276 FP); TypeScript 0.0% (0 TP, 6 FP); Jupyter/YAML/PKL 100% (3 TP, 0 FP; N too small for significance). Source: `benchmarks/results/random_corpus/METHODOLOGY.json`.

Full methodology: `benchmarks/results/random_corpus/METHODOLOGY.json`.

### 3.5 Known limitations

- **TypeScript precision is 0% on the current benchmark** (0 TP, 6 FP). All six TypeScript false positives are domain-keyword matches in code where no AI inference occurs. Regula has no TypeScript-specific AST gating, so TypeScript findings should be treated as advisory. Source: [`benchmarks/results/random_corpus/METHODOLOGY.json`](../benchmarks/results/random_corpus/METHODOLOGY.json).
- **Library source code** has 15.2% precision on the measured library corpus, compared with 66.1% for measured application code. AI frameworks implement APIs that the patterns flag, so use `--scope production` and `--skip-tests` to focus on application code. Source: [`benchmarks/results/random_corpus/METHODOLOGY.json`](../benchmarks/results/random_corpus/METHODOLOGY.json).

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

### Project scoping

Audit events are attributed to the project they were recorded in and
stored in per-project chains (`~/.regula/audit/projects/<slug>/`).
Deliverables — evidence packs, conformity packs, HTML reports — embed
only the scanned project's own chain, never events from other projects
on the same machine. `regula audit verify --project <path>` verifies a
single project's chain; without `--project` it verifies the machine
store and every project chain.

Two honesty notes. First, log files rotate monthly, and versions before
v1.7.5 started each new monthly file from the genesis hash instead of
continuing the chain. Verification therefore reports a genesis seed at
the start of a file as a "legacy restart" rather than failing; the
consequence is that truncating a *legacy* store exactly at a month
boundary is not detectable by the chain alone. Chains written by
current versions are continuous across files, so this forgiveness does
not extend to new data. Second, events recorded by versions without
project scoping live unattributed in the machine-wide store; they are
excluded from deliverables and each deliverable's audit section says so.

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

### Regulatory currency

Deadline and status copy is not hand-maintained per page: it derives
from a single source (`scripts/omnibus.py`) consumed by every CLI
output, registration packet, and report, and a test
(`tests/test_source_of_truth.py`) fails the build if any consumer
drifts. This mechanism exists because the manual approach failed us:
when the Digital Omnibus changed the EU AI Act's status in June 2026,
the correction had to be hand-edited into six files and two were
missed. The prose now lives in one constant, and the next status
change (Official Journal publication) is a one-line flip that the
test suite propagates and checks. Changes to the regulatory record
are tracked in a public delta log (`content/regulations/delta-log/`).

---

## 6. Independent verification

| Resource | Where |
|---|---|
| Source code | <https://github.com/kuzivaai/getregula> |
| PyPI package | <https://pypi.org/project/regula-ai/> |
| Direct contact | `support@getregula.com` |
| Issue tracker | <https://github.com/kuzivaai/getregula/issues> |
| Security disclosures | <https://github.com/kuzivaai/getregula/security/advisories/new> or `support@getregula.com` |
| Test suite | `tests/` (2,681 unique tests, 2,681 pytest-collected; the legacy `tests/test_classification.py` runner executes 1,082 functions, 437 defined in-file) |
| Pattern definitions | `scripts/risk_patterns.py` |
| Framework mapping | `references/framework_crosswalk.yaml` |
| Pre-commit hook source | `hooks/pre_tool_use.py` |
| MCP server source | `scripts/mcp_server.py` |
| Benchmark corpus | `benchmarks/labels.json` |
| Self-scan (Regula run on its own repo) | [`docs/self-scan-results.md`](self-scan-results.md) |
| Primary research citations | `references/FETCH.md` |
| Changelog | `CHANGELOG.md` |
| Known gaps and limitations | `docs/what-regula-does-not-do.md` |

The repository is intentionally legible. There are no compiled binaries,
no obfuscated bytecode, no generated code committed without the
generator. A reviewer can read every line of every file Regula will run
on their machine.

### 6.1 Verify an evidence pack without installing Regula

A Regula evidence pack is designed so that the party *receiving* it — a
client's auditor, counsel, or security team — can verify it without
trusting or installing Regula. Two independent tiers, both specified in
[Evidence Format v1](spec/regula-evidence-format-v1.md):

**Tier 1 — file integrity (Python standard library only).** Every pack
file's SHA-256 is recorded in `manifest.json`:

```python
import hashlib, json, sys
from pathlib import Path

pack = Path(sys.argv[1])
manifest = json.loads((pack / "manifest.json").read_text(encoding="utf-8"))
for entry in manifest["files"]:
    digest = hashlib.sha256((pack / entry["filename"]).read_bytes()).hexdigest()
    assert digest == entry["sha256"], f"TAMPERED: {entry['filename']}"
print(f"{len(manifest['files'])} file hashes match the manifest")
```

**Tier 2 — signature (needs only `pip install cryptography`).** Signed
packs embed an Ed25519 signature over the canonical manifest
(spec §4.5), with the public key in the pack:

```python
import base64, json
from cryptography.hazmat.primitives.serialization import load_pem_public_key

sig = manifest["signing"]
stripped = {k: v for k, v in manifest.items()
            if k not in ("signing", "timestamp_authority")}
canonical = json.dumps(stripped, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False).encode("utf-8")
pub = load_pem_public_key(base64.b64decode(sig["public_key"]))
pub.verify(base64.b64decode(sig["signature"]), canonical)  # raises if invalid
print("Ed25519 signature VERIFIED")
```

Both walkthroughs were executed against a pack generated by the
released `regula-ai` 1.7.5 on 16 July 2026: 9/9 hashes matched, the
signature verified, and a deliberately flipped byte in one pack file
was caught by tier 1 (then restored).

Why this design matters: Ed25519 is an asymmetric scheme, so the
verifying party never holds signing capability — anyone with the pack
can check it, and nobody who can check it can forge it. A symmetric
scheme (e.g. an HMAC chain) cannot offer that separation: verification
requires the same secret that creates the records, so any party able
to verify is also able to forge, and third-party verification without
key disclosure is impossible. The distribution pipeline carries the
same property end-to-end — the PyPI release is published via OIDC
trusted publishing with PEP 740 attestations, so the package itself
is provenance-verifiable before you run it.

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

Crash reporting requires **both** of the following. Neither is the default:

1. the user runs `regula telemetry enable`, and
2. a Sentry endpoint is configured, via the `REGULA_SENTRY_DSN`
   environment variable.

The published PyPI build ships `_SENTRY_DSN = ""` (empty) and reads the
endpoint from the environment, so **even if the user opts in, nothing is
sent unless they point Regula at a Sentry instance themselves.** This is
by design: Regula is a tool for compliance teams, many of whom cannot
legally exfiltrate any data to a third party.

Verify with:

```bash
grep -n "^_SENTRY_DSN" $(pip show regula-ai | grep Location | cut -d: -f2)/scripts/telemetry.py
# Expected: _SENTRY_DSN = ""
```

When an endpoint *is* configured and consent given, an uncaught exception
sends: the exception type and message, a stack trace through Regula's own
code, and the Regula, OS and Python versions. Stack-frame local variables
are explicitly disabled (`include_local_variables=False`) because Regula's
scan frames hold whole scanned files in memory, and the auto-detected
hostname is replaced with `redacted`. One residual caveat, stated because
it cannot be fully prevented: an exception *message* can itself contain a
file path (for example a permission error naming the file).

Sending is suppressed regardless of stored consent when any of
`DO_NOT_TRACK`, `REGULA_NO_TELEMETRY`, or `CI` is set to a value other
than `0`/`false`/`no`. `DO_NOT_TRACK` follows the cross-tool CLI
convention (<https://consoledonottrack.com>).

> **Correction (21 Jul 2026).** Between commit `2c9829d` (10 Apr 2026) and
> this change, `_SENTRY_DSN` was hardcoded to a live endpoint while this
> section continued to state it was empty — so the claim above was false
> for releases in that window, including v1.7.7 on PyPI. Reaching the
> endpoint still required the optional `sentry-sdk` extra to be installed
> *and* explicit opt-in, so the default-install posture was unaffected.
> The DSN is now read from the environment and defaults to empty, which
> restores the documented behaviour.

### 8.3 What Regula sends over the network

Only when the user explicitly invokes the relevant command:

| Command | Endpoint | Data sent |
|---|---|---|
| `regula feed` | curated RSS/Atom feed URLs in `scripts/feed.py` (IAPP, EDPB, ICO, etc.) | HTTP GET only — no user data sent |
| `regula audit anchor` | user-configured RFC 3161 TSA (default `freetsa.org`) | A SHA-256 hash of the local audit log head. The hash itself reveals nothing about the user's code. |
| `regula bias` | `raw.githubusercontent.com/nyu-mll/crows-pairs/master/...` | HTTP GET only. Falls back to bundled 20-pair sample if network unavailable. |

Core scan paths are designed for local execution. This repository has not
completed operating-system-level network observation for every command and
environment. Optional timestamping, configured telemetry, update/feed paths,
and other explicitly network-enabled features are excluded from any local-only
statement.

---

## 9. Vendor evaluation answers

The questions a 2026 procurement team will ask, with copy-pasteable
answers.

**Q: What is the deployment model?**
A: Local-only command-line tool. Installs via `pipx install regula-ai`.
No accounts, no servers, no SaaS tier exists.

**Q: Where is data stored?**
A: Core scan output, audit logs, and generated scaffolds are written to
the user's local filesystem under `~/.regula/` and the project directory.
Optional network-enabled features have separate boundaries and must be assessed.

**Q: What is the licensing model?**
A: Apache License 2.0 (with EUPL-1.2 dual-licence option). Commercial
use, redistribution, and modification are permitted. There is no paid
tier. The maintainer accepts sponsorships but does not gate features
behind payment.

**Q: How do you handle GDPR / DPA / SCCs?**
A: Core scan paths are designed to process source locally. Whether a controller-
processor relationship, DPA, SCCs, or other privacy measure is required depends
on the actual deployment, data, roles, and optional features; Regula does not
make that legal determination.

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
2025 figures are page-cited against the
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
[`docs/benchmarks/PRECISION_RECALL_2026_04.md`](benchmarks/PRECISION_RECALL_2026_04.md)
(the precision/recall report) and
[`docs/what-regula-does-not-do.md`](what-regula-does-not-do.md)
(the scope statement).

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
| Test suite | `tests/` | 2,681 unique tests (2,681 pytest-collected) |
| Self-test | `regula self-test` | 6 round-trip assertions |
| Environment health | `regula doctor` | 12 checks (pass/info split varies by environment) |
| SBOM | `regula sbom --ai-bom` | CycloneDX 1.7 ML-BOM from any checkout |
| Changelog | [`CHANGELOG.md`](../CHANGELOG.md) | Version history and breaking changes |

**Machine-readable security metadata.** A `security.txt` file
(per [RFC 9116](https://www.rfc-editor.org/rfc/rfc9116)) is on the
roadmap but not yet published. Until it is in place, the canonical
security contact is `support@getregula.com` and the disclosure process
is defined in [`SECURITY.md`](../SECURITY.md).
