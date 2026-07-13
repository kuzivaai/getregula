# CLAIMS_REGISTER

Status: DRAFT (uncommitted). Public/technical claims audited in Phases 0–1.
All entries verified against commit `27731d811e89dd5ac3180ea47009ff46fd6594f9`
on 2026-07-13, Python 3.11.8, unless stated otherwise.

Classification: verified | reproduced | inferred | proposed | unknown | contradicted

---

```yaml
claim_id: C-001
statement: "Regula exposes 61 CLI commands."
classification: verified
evidence:
  files: [scripts/site_facts.py, data/site_facts.json]
  commands: ["python3 -m scripts.site_facts", "python3 scripts/claim_auditor.py --verify-facts"]
  external_sources: []
verified_against_commit: 27731d8
verified_at: 2026-07-13
limitations: "Count method = grep '^def cmd_' across topic modules; enforced by claim_auditor canonical set."
```

```yaml
claim_id: C-002
statement: "Regula maps 12 compliance frameworks."
classification: verified
evidence:
  files: [references/framework_crosswalk.yaml, data/site_facts.json]
  commands: ["python3 scripts/claim_auditor.py --verify-facts"]
verified_against_commit: 27731d8
verified_at: 2026-07-13
limitations: "12 have full crosswalk; 5 additional (Colorado SB-189, Canada AIDA, Singapore AI, OECD AI, South Korea AI) are partial-coverage filter keys per site_facts notes."
```

```yaml
claim_id: C-003
statement: "Regula scans 8 language families."
classification: verified
evidence:
  files: [scripts/ast_engine.py, data/site_facts.json]
  commands: ["python3 scripts/claim_auditor.py --verify-facts"]
verified_against_commit: 27731d8
verified_at: 2026-07-13
limitations: "Extension coverage != full analysis maturity; per-language maturity is a Phase 8 concern. README itself notes TypeScript findings are advisory (0% precision on current benchmark)."
```

```yaml
claim_id: C-004
statement: "Regula has 419 risk detection patterns (regexes)."
classification: verified
evidence:
  files: [scripts/risk_patterns.py, data/site_facts.json, scripts/claim_auditor.py]
  commands: ["python3 scripts/claim_auditor.py --verify-facts"]
verified_against_commit: 27731d8
verified_at: 2026-07-13
limitations: >
  Verified as ONE definition: site_facts counts.patterns.tier_regexes = 419.
  Same file records grand_total=722, marketing_409=467, historical_330_bucket=479.
  The GitHub repo 'About' description says 398 and AGENTS.md says 648 (web scanner) —
  both outside auditor scope. See DEF-003.
```

```yaml
claim_id: C-005
statement: "PyPI regula-ai 1.7.4 corresponds to the released version; HEAD is development ahead of it."
classification: verified
evidence:
  files: [pyproject.toml, scripts/constants.py]
  commands: ["git rev-list -n1 v1.7.4", "git rev-list --count v1.7.4..HEAD"]
  external_sources: ["https://pypi.org/pypi/regula-ai/json"]
verified_against_commit: 27731d8
verified_at: 2026-07-13
limitations: "1.7.4 uploaded 2026-07-06; tag v1.7.4 -> 2da9922; HEAD is 14 commits ahead. Wheel sha256 recorded in VERIFIED_BASELINE."
```

```yaml
claim_id: C-006
statement: "Regula has 2,543 tests passing (README), or 2,484 (PyPI), described as 'pytest --collect-only'."
classification: contradicted
evidence:
  files: [README.md, data/site_facts.json]
  commands: ["python3 -m pytest tests/ --collect-only -q", "python3 -m pytest tests/ -q"]
  external_sources: ["https://pypi.org/pypi/regula-ai/json"]
  test_results:
    - "collect-only @ 27731d8 = 2519"
    - "full run @ 27731d8 = 2488 passed + 32 skipped = 2520 collected"
    - "site_facts regenerated @ HEAD = 1574 test functions (committed json = 1565, stale)"
verified_against_commit: 27731d8
verified_at: 2026-07-13
limitations: >
  No published surface matches reality. README=2543, PyPI=2543, actual collect-only=2519.
  Number is not in the claim_auditor canonical set, so it drifts unaudited.
  User-selected canonical definition for remediation: pytest --collect-only total (= 2519 at HEAD).
  See DEFECT_REGISTER DEF-001.
```

```yaml
claim_id: C-007
statement: "Every public number is paired with a reproducible command (docs/TRUST.md positioning)."
classification: contradicted
evidence:
  files: [scripts/claim_auditor.py, README.md]
  commands: ["python3 scripts/claim_auditor.py --verify-facts"]
verified_against_commit: 27731d8
verified_at: 2026-07-13
limitations: "The tests count is published but not generated/enforced. Positioning claim is therefore not fully met for that number. See DEF-001."
```
