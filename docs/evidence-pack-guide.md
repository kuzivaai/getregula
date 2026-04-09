# Evidence pack guide — what auditors actually get

Regula has two commands that produce audit-ready output:

- `regula evidence-pack .` — the developer-friendly bundle
- `regula conform .` — the Article 43 conformity assessment evidence pack

This page documents what each one produces, the format, and how an
external auditor can verify it came from Regula without trusting the
Regula project.

## `regula conform .`

Produces an **Article 43 conformity assessment evidence pack**: a
directory containing 26 files mapped to Articles 9–15 (and related
annexes), each with a per-article readiness score and a SHA-256
integrity hash.

This command backs the "26 files mapped to Articles 9-15, per-article
readiness scores, SHA-256 integrity hashes" claim on the Regula
landing page. The claim is asserted by the
`conform: end-to-end pack structure verified` test in
`tests/test_classification.py`, which is run on every CI build and
on every `python3 -m scripts.cli self-test`.

### Directory layout

```
conform-pack-YYYY-MM-DD/
├── manifest.json                       ← per-file SHA-256 + article map
├── 01-risk-management.md               ← Art. 9 readiness
├── 02-data-governance.md               ← Art. 10 readiness
├── 03-technical-documentation.md       ← Art. 11 readiness (scaffold)
├── 04-record-keeping.md                ← Art. 12 readiness
├── 05-transparency.md                  ← Art. 13 readiness
├── 06-human-oversight.md               ← Art. 14 readiness
├── 07-accuracy-robustness.md           ← Art. 15 readiness
├── 08-annex-iv-section-1.md            ← general description
├── 09-annex-iv-section-2.md            ← system architecture
├── 10-annex-iv-section-3.md            ← monitoring, functioning, control
├── 11-annex-iv-section-4.md            ← performance metrics
├── 12-annex-iv-section-5.md            ← risk management
├── 13-annex-iv-section-6.md            ← changes to the system
├── 14-annex-iv-section-7.md            ← harmonised standards list
├── 15-annex-iv-section-8.md            ← EU declaration of conformity
├── 16-annex-iv-section-9.md            ← post-market monitoring plan
├── 17-findings-summary.json            ← all scan findings, de-duplicated
├── 18-ai-bom.cdx.json                  ← CycloneDX 1.7 AI-BOM
├── 19-dependency-graph.json            ← third-party dependencies
├── 20-human-oversight-trace.json       ← cross-file Art. 14 trace
├── 21-scan-manifest.json               ← tool version, pattern version
├── 22-framework-crosswalk.json         ← NIST / ISO / OWASP mappings
├── 23-gap-assessment.json              ← Art. 9-15 readiness scores
├── 24-prioritised-remediation.json     ← `regula plan` output
├── 25-policy-snapshot.yaml             ← regula-policy.yaml at scan time
└── 26-changelog.md                     ← scan history since last pack
```

Every file is SHA-256 hashed in `manifest.json`. The manifest is itself
hashed and the hash is stamped into the JSON envelope of the CLI
output, so downstream auditors can detect post-hoc tampering.

### How an auditor verifies a pack

```bash
# Re-compute every file's SHA-256 and compare against manifest.json
cd conform-pack-YYYY-MM-DD
python3 -c "
import hashlib, json, sys
manifest = json.load(open('manifest.json'))
failures = []
for entry in manifest['files']:
    with open(entry['path'], 'rb') as f:
        got = hashlib.sha256(f.read()).hexdigest()
    if got != entry['sha256']:
        failures.append(entry['path'])
sys.exit(1 if failures else 0)
print('OK' if not failures else 'TAMPER:', *failures)
"
```

This verification runs without installing Regula. Auditors only need
Python stdlib.

## `regula evidence-pack .`

A lighter-weight bundle intended for developer review and pull-request
evidence. Uses the same `json_output` envelope format (`format_version`,
`regula_version`, `command`, `timestamp`, `exit_code`, `data`) and is
suitable for attachment to code review artefacts. It is **not** a
substitute for the Article 43 conformity pack when a notified body is
involved.

## What the pack is NOT

Consistent with `docs/what-regula-does-not-do.md`:

- **It is not a conformity certificate.** Only a notified body (for
  Annex VII routes) or a properly-completed internal control process
  (for Annex VI routes) can result in conformity. The pack is the
  evidence that feeds those processes.
- **It is not a legal opinion.** The scaffolded Annex IV sections are
  starting points. A human must fill in the organisational details
  that a scanner cannot know.
- **It does not replace post-market monitoring.** The pack is a
  snapshot. Article 72 monitoring is a continuous process.

## Reproducibility

Every pack includes `21-scan-manifest.json` which records:

- `regula_version` — the version of the CLI that produced the pack
- `pattern_version` — the pattern ruleset version from `regula-policy.yaml`
- `timestamp` — ISO 8601, UTC
- `git_sha` — the git commit of the scanned project (if under git)
- `delta_log_latest_entry` — the most recent EU AI Act change Regula
  was aware of at scan time

Two auditors who run `regula conform .` on the same git commit with
the same `regula_version` and `pattern_version` will get byte-identical
packs. This is the "evidence workflow" gap competitor SaaS platforms
usually close with a hosted control library — Regula closes it with
reproducibility plus the delta log.
