# cv-screening-app — Try Regula in 10 minutes

A minimal high-risk reference project (Annex III, Category 4 — Employment)
designed as a **complete evaluation journey**. Run every Regula workflow
against a single realistic fixture, watch every artefact Regula produces,
verify the whole thing without touching your own codebase.

Intended for: maintainers evaluating Regula, auditors reviewing the output
format, contributors learning the command surface, or anyone who wants to
see what a full Article 43 evidence pack looks like before running Regula
on their own project.

Allow around ten minutes end-to-end. No cloud services, no API keys,
no registrations — every command below runs locally.

---

## Step 0 — install

```bash
pipx install regula-ai    # or: uvx --from regula-ai regula
regula --version           # expect regula 1.6.2 or newer
```

Clone the repo to get this example:

```bash
git clone https://github.com/kuzivaai/getregula.git
cd getregula
```

---

## Step 1 — scan (`regula check`) — 30 seconds

```bash
regula check examples/cv-screening-app
```

Expected output (verified against Regula v1.6.2 on 2026-04-16):

```
Regula Scan: /home/you/getregula/examples/cv-screening-app
============================================================
  Files scanned:      1
  Prohibited:         0
  Credentials:        0
  High-risk:          1
  Agent autonomy:     0
  Limited-risk:       0
  Suppressed:         0
  BLOCK tier:         0
  WARN tier:          1
  INFO tier:          0

  HIGH-RISK INDICATORS:
    [WARN] [ 68] app.py — Employment and workers management
      Add human oversight before automated hiring/employment decisions
============================================================
```

**What to notice:** Regula matched the employment vocabulary in `app.py`
(`hire_probability`, `applicants`, `job`) and classified the project as
**high-risk, Annex III Category 4**. That is an indication, not a legal
determination — Article 6 + Article 6(3) still govern the applicability
decision for your real system.

---

## Step 2 — remediation plan (`regula plan`) — 10 seconds

```bash
regula plan --project examples/cv-screening-app
```

Expected output (abbreviated — full plan is 8 tasks):

```
# Remediation Plan — cv-screening-app
Generated: 2026-04-16T…
Tasks: 8

## Priority: HIGH

TASK-001 [HIGH] Article 12 — Record-Keeping
  Action: Address compliance gaps for Article 12:
    - No logging framework detected in code files
    - No structured or auditable logging format detected
  Effort: ~5-11h
  Deadline: 2 August 2026

TASK-002 [HIGH] Article 13 — Transparency
  …

TASK-003 [HIGH] Article 14 — Human Oversight
  Action: No evidence that AI outputs are reviewed by humans before action
  Effort: ~4-8h
…
```

**What to notice:** Regula converted the scan findings into a prioritised
remediation list mapped to EU AI Act Articles 9 through 15. Use this to
populate your own JIRA / Linear backlog.

---

## Step 3 — gap assessment (`regula gap`) — 15 seconds

```bash
regula gap
```

(Yes — `gap` has no path argument. It reads the policy file and
cross-references framework mappings.)

Expected output (excerpt):

```
GAP REPORT — 6 of 7 articles have strong evidence. 1 have moderate.

Article 9   Risk management           [OK ] …
Article 10  Data governance           [OK ] …
Article 11  Technical documentation   [WARN] …
Article 12  Record-keeping            [OK ] …
Article 13  Transparency              [WARN] …
Article 14  Human oversight           [OK ] …
Article 15  Accuracy/robustness       [OK ] …
```

**What to notice:** the cross-framework mapping (ISO 42001, NIST AI RMF,
SOC 2, GDPR, DORA, NIS2) is in the full text output — see
`docs/cli-reference.md` for the column key.

---

## Step 4 — full evidence pack (`regula conform --zip`) — 30 seconds

```bash
rm -rf /tmp/regula-demo
regula conform \
  --project examples/cv-screening-app \
  --output /tmp/regula-demo \
  --name cv-screening-app \
  --zip
```

Expected terminal output:

```
Generating conformity assessment evidence pack for examples/cv-screening-app...
Conformity evidence pack written to: /tmp/regula-demo/conformity-evidence-cv-screening-app-2026-04-16
Contains 26 files with SHA-256 integrity hashes.
Overall readiness: 21%
Bundle written to:      /tmp/regula-demo/conformity-evidence-cv-screening-app-2026-04-16.regula.zip
Verify bundle with:     regula verify /tmp/regula-demo/conformity-evidence-cv-screening-app-2026-04-16.regula.zip
Start with: /tmp/regula-demo/conformity-evidence-cv-screening-app-2026-04-16/00-assessment-summary.json
```

**What was generated:**

```
conformity-evidence-cv-screening-app-2026-04-16/
├── 00-assessment-summary.json          ← start here
├── README.md
├── manifest.json                       ← SHA-256 integrity, declares regula.evidence.v1
├── 01-risk-classification/
│   ├── findings.json
│   └── coverage.json
├── 02-risk-management-art9/
│   ├── evidence.json
│   └── coverage.json
├── 03-data-governance-art10/
├── 04-technical-documentation-art11/
│   ├── annex-iv-draft.md               ← the Annex IV doc your auditor expects
│   ├── evidence.json
│   └── coverage.json
├── 05-record-keeping-art12/
│   ├── audit-trail.json
│   └── …
├── 06-transparency-art13/
├── 07-human-oversight-art14/
│   └── oversight-analysis.json         ← cross-file human-in-the-loop analysis
├── 08-accuracy-robustness-art15/
│   ├── sbom.json                       ← CycloneDX AI-BOM
│   └── …
├── 09-supply-chain/
│   ├── dependency-report.json
│   └── sbom.json
├── 10-declaration-of-conformity/
│   └── declaration-template.md         ← Article 47 DoC scaffold
└── 11-remediation/
    └── remediation-plan.md

+ conformity-evidence-cv-screening-app-2026-04-16.regula.zip    ← portable bundle
```

Open `00-assessment-summary.json` for the top-level readiness score and
article-by-article breakdown. Open `04-technical-documentation-art11/annex-iv-draft.md`
for the Annex IV draft a notified body would review.

**What Regula did NOT produce** (see each `coverage.json`): the
organisational parts of the compliance evidence. Risk Management System
documentation (Article 9 process records), Quality Management System
(Article 17), Post-Market Monitoring (Article 72), and Fundamental Rights
Impact Assessment (Article 29a) are out of scope for a code scanner.
`regula conform --organisational` produces a questionnaire for those.

The format produced above is the
[Regula Evidence Format v1](../../docs/spec/regula-evidence-format-v1.md) —
a versioned, schema-validated, portable spec that any third-party tool
can read without re-running Regula.

---

## Step 5 — verify the pack (`regula verify`) — 5 seconds

The manifest binds every file to a SHA-256 hash. Anyone can verify the
pack has not been tampered with, **without re-running Regula**:

```bash
regula verify /tmp/regula-demo/conformity-evidence-cv-screening-app-2026-04-16
```

Expected output:

```
Verifying: /tmp/regula-demo/conformity-evidence-cv-screening-app-2026-04-16
  Format: regula.evidence.v1 v1.0 (generated by Regula 1.6.2)
============================================================
  ✓ 01-risk-classification/findings.json — OK
  ✓ 01-risk-classification/coverage.json — OK
  …
  ✓ README.md — OK
============================================================
  26/26 files verified, 0 issues
  All files match manifest. Pack integrity confirmed.
```

Verify the `.regula.zip` bundle directly (useful for transporting evidence
to a reviewer):

```bash
regula verify /tmp/regula-demo/conformity-evidence-cv-screening-app-2026-04-16.regula.zip
```

Write a machine-readable verification report (for audit trails):

```bash
regula verify \
  /tmp/regula-demo/conformity-evidence-cv-screening-app-2026-04-16 \
  --strict \
  --format json \
  --report /tmp/regula-demo/verify-report.json
```

`--strict` fails if the pack does not declare `format=regula.evidence.v1`
(useful in CI to reject legacy packs).

### Optional — tamper-evident signing + timestamping (v1.1)

For audit-relevant provenance, sign the manifest with an Ed25519 key
and witness its existence with an RFC 3161 timestamp. Signing binds
*who*, timestamping binds *when* — together they close the "motivated
attacker" gap that the SHA-256 manifest alone does not protect against.

Install the optional crypto extra once:

```bash
pipx install "regula-ai[signing]"
# or:  pip install "regula-ai[signing]"
```

Regenerate the pack with both signatures:

```bash
regula conform \
  --project examples/cv-screening-app \
  --output /tmp/regula-demo-signed \
  --name cv-screening-app \
  --zip \
  --sign \
  --timestamp
```

First `--sign` generates an Ed25519 keypair at `~/.regula/signing.key`
(override with `--signing-key <path>` or the `REGULA_SIGNING_KEY` env
var). `--timestamp` contacts `https://freetsa.org/tsr` by default;
override with `--tsa-url <url>` for a different TSA.

Expected output additions:

```
Format: regula.evidence.v1 (format_version 1.1)
…
Signed: Ed25519 signature embedded (verify with `regula verify …`).
Timestamped: RFC 3161 token from https://freetsa.org/tsr at 2026-04-16T16:02:28+00:00.
```

Verify the signed + timestamped pack:

```bash
regula verify /tmp/regula-demo-signed/conformity-evidence-cv-screening-app-*
```

Expected new lines:

```
Format: regula.evidence.v1 v1.1 (generated by Regula 1.6.2)
Signature: VERIFIED (ed25519 signature verified)
Timestamp: VERIFIED (timestamp hash matches manifest; gen_time=… (signer-chain NOT independently verified))
============================================================
  26/26 files verified, 0 issues
  All files match manifest. Pack integrity confirmed.
```

Any post-signing edit — changing a finding's hash, touching a file,
re-ordering keys — invalidates the signature and `regula verify` exits 1.
See [`docs/spec/regula-evidence-format-v1.md`](../../docs/spec/regula-evidence-format-v1.md),
§4.5 (signing) and §4.6 (timestamp), for the canonical form and the
trust boundaries (in particular, v1.1 does not independently validate
the TSA signer-cert chain — consumers with a higher trust bar should
run the raw token through `openssl ts -verify`).

---

## Step 6 — red-team hand-off (`regula handoff`) — 10 seconds

Regula detects LLM entrypoints and emits a scoped config for a
behavioural-testing tool (Giskard / garak / promptfoo). Regula covers the
static layer; this command hands off to the dynamic layer.

```bash
regula handoff giskard examples/cv-screening-app --output /tmp/giskard.yaml
cat /tmp/giskard.yaml
```

Expected config (abbreviated):

```yaml
# Giskard scan config — generated by `regula handoff giskard`
model:
  name: REPLACE_ME
  model_type: text_generation
  feature_names:
    - "prompt"
scan:
  scans:
    - "robustness"
    - "performance"
    - "hallucination"
    - "harmful_content"
    - "stereotypes"
    - "information_disclosure"
  threshold: 0.2
regula_handoff:
  version: 1
  generated_at: "2026-04-16T…"
  entrypoint_count: 0
```

Terminal also prints OWASP LLM Top 10 coverage (5/10 for Giskard on this
fixture; `regula handoff garak` covers 7/10 with different emphasis). No
entrypoints were detected here because the fixture is a classical ML
model, not an LLM — run the same command on a real LLM project to see
entrypoint detection in action.

---

## Step 7 — (optional) bias evaluation — 1 minute

If you have [Ollama](https://ollama.ai) installed with a supported model:

```bash
ollama pull llama3.2
regula bias --project examples/cv-screening-app --model llama3.2
```

Two benchmarks run (CrowS-Pairs + BBQ) with Wilson and bootstrap
confidence intervals. Aggregated scores only — no individual stereotype
pairs are displayed. See the
[bias methodology + ethics statement](../../README.md#bias-evaluation--methodology-and-ethics)
in the main README.

---

## What you now have

Every Regula artefact, end to end, against one project:

| Artefact | Path |
|---|---|
| Scan finding | (terminal, Step 1) |
| Remediation plan | (terminal, Step 2) |
| Gap report | (terminal, Step 3) |
| Evidence pack — 26 files mapped to Articles 9–15 + supply chain + DoC | `/tmp/regula-demo/conformity-evidence-…/` |
| Annex IV draft | `…/04-technical-documentation-art11/annex-iv-draft.md` |
| Declaration of Conformity scaffold | `…/10-declaration-of-conformity/declaration-template.md` |
| AI-BOM (CycloneDX) | `…/08-accuracy-robustness-art15/sbom.json` |
| Integrity manifest | `…/manifest.json` (regula.evidence.v1) |
| Portable bundle | `….regula.zip` |
| Verification report | `/tmp/regula-demo/verify-report.json` |
| Ed25519-signed manifest (v1.1, optional) | `/tmp/regula-demo-signed/…/manifest.json` |
| RFC 3161 timestamp token (v1.1, optional) | embedded in the signed manifest |
| Red-team config | `/tmp/giskard.yaml` |

This is the evidence package you show an auditor, a buyer's procurement
team, or a regulator who asks "can you prove what your AI system does?"

---

## Why Regula flags this project

Annex III (4)(a) lists *"AI systems intended to be used for recruitment
or selection of natural persons, in particular to place targeted job
advertisements, to analyse and filter job applications, and to evaluate
candidates"* as high-risk. If deployed for real hiring, Articles 9–15
apply: risk management, data governance, documentation, logging,
transparency, human oversight, accuracy.

## What Regula does NOT tell you

Whether this code, in your context, is actually in scope of Annex III.
That depends on Article 6 (significant risk of harm) and the Article 6(3)
exemption for narrow procedural or preparatory tasks. Regula surfaces the
risk indicators; the applicability decision — and the legal advice that
accompanies it — is yours.

See [`docs/what-regula-does-not-do.md`](../../docs/what-regula-does-not-do.md)
for the full scope statement.

---

## What the fixture does (for contributors)

`app.py` trains a toy logistic-regression model on in-memory job
applicants and ranks new candidates by predicted hire probability.
No network calls, no persistence, no real PII. Output is deterministic
given the hardcoded training data. The vocabulary (`JobApplicant`,
`hire_probability`, `rank_candidates`) triggers Regula's employment
patterns — see `data/patterns/high_risk__employment.yaml`.

Two other reference projects in this directory demonstrate the other
risk tiers:

- [`examples/customer-chatbot`](../customer-chatbot) — Article 50
  limited-risk chatbot transparency obligation
- [`examples/code-completion-tool`](../code-completion-tool) — minimal-risk
  dev-time assistant (clean scan)
