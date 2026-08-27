# Regula quick start

Regula helps a developer or governance reviewer find **code-observable AI-governance indicators**, record deployment facts that source code cannot establish, and prepare evidence for human review. It does not determine legal classification, compliance, or which duties apply to a real system.

## 1. Install the current public source

PyPI distribution is currently unavailable. Until a new package release is published, install the public `main` branch with Python 3.10 or later:

```bash
pipx install git+https://github.com/kuzivaai/getregula.git@main
regula --version
regula self-test
```

This is a moving source reference, not an immutable release. For a reproducible evaluation, replace `main` with the exact public commit you reviewed. See [Installing Regula](installation.md) for `uv`, virtual-environment, upgrade, and uninstall instructions.

## 2. Record the facts code cannot show

Start with the guided assessment:

```bash
regula assess
regula assess --save-facts
```

The assessment asks about intended purpose, jurisdiction, operator role, and deployment context. Saved answers are declarations from the operator, not facts inferred or verified by Regula. `unknown` remains unknown; it is never treated as `no`.

You can inspect or provide facts explicitly:

```bash
regula check . --list-facts
regula check . --fact is_ai_system=yes \
               --fact jurisdiction_in_scope=yes
```

## 3. Scan the code

```bash
regula check .
regula check . --explain
```

The result separates:

- **detector observations** — patterns seen in the files that were scanned;
- **declared facts** — contextual answers supplied by a person; and
- **decision state** — often `insufficient_information` until required facts are resolved.

A prohibited-practice, Annex III, or transparency indicator is a prompt for contextual review. It is not a finding that the law applies. Likewise, no elevated indicator is not proof of low risk or compliance.

For the three executable jurisdiction reference sets:

```bash
regula check . --jurisdictions eu,korea,colorado
```

Regula also maps selected findings to additional governance and security framework references. Those cross-references are review aids, not independent implementations of each framework.

## 4. Review coverage and unresolved work

```bash
regula gap .
regula gap . --framework nist-ai-rmf,iso-42001
regula plan .
```

`gap` examines code-observable signals against an Articles 9–15 review scaffold. Its output cannot verify organisational controls, real-world performance, data provenance, contracts, or deployment behaviour. Framework options include `nist-ai-rmf`, `iso-42001`, `nist-csf`, `soc2`, `iso-27001`, `owasp-llm-top10`, and `mitre-atlas`.

`plan` prioritises follow-up items derived from the available observations and facts. Its priorities are workflow aids, not legal advice, audit conclusions, or effort guarantees.

## 5. Prepare reviewer-completable evidence

```bash
regula docs . --all
regula evidence-pack . --bundle
```

Generated documentation and evidence packs are scaffolds. Complete their contextual fields, verify every claim against source evidence, and have the result reviewed by an appropriately qualified person before relying on it.

## Try a known fixture

The examples are in the repository rather than the installed package:

```bash
git clone https://github.com/kuzivaai/getregula.git
cd getregula
regula check examples/cv-screening-app --scope all
```

The fixture deliberately contains employment-related indicators. The result demonstrates detection and fact handling; it does not demonstrate that an actual product is legally high-risk.

## What Regula cannot establish

Regula cannot establish from source code alone:

- whether a system meets a legal definition of AI;
- territorial scope, operator role, intended purpose, or actual deployment context;
- whether an exception or exemption applies;
- whether policies and controls work in practice;
- real-world accuracy, bias, robustness, accessibility, or human oversight quality; or
- legal compliance, certification, or readiness.

It is also not a general vulnerability scanner. Use appropriate security, dependency, privacy, accessibility, model-evaluation, and operational-monitoring tools alongside it.

## Interpret results conservatively

The detector is deterministic and covered by regression tests, but repeatability is not validity. Current benchmark evidence shows both false-negative risk and dependence on declared domain context. Review [the trust evidence](TRUST.md), [the current validity audit](VALIDITY_UX_ENGINEERING_AUDIT_2026-08-26.md), and [the current self-scan](self-scan-results.md) before deciding whether Regula is suitable for a workflow.
