# examples/ — runnable fixtures for Regula

Three minimal projects, one per EU AI Act risk tier, so new users can see what
Regula flags without needing their own codebase. Each directory has its own
README with the exact output of `regula check` verified against the current
release.

| Directory                    | EU AI Act tier             | Expected finding (with `--scope all`)   |
| ---------------------------- | -------------------------- | --------------------------------------- |
| `cv-screening-app/`          | High-risk (Annex III, 4)   | HIGH-RISK verdict — employment pattern  |
| `customer-chatbot/`          | Limited-risk (Article 50)  | LIMITED-RISK verdict — chatbot transparency |
| `code-completion-tool/`      | Minimal-risk               | clean scan, 0 findings                  |

## Quick start

```
pipx install regula-ai   # 1.7.5 or newer
git clone https://github.com/kuzivaai/getregula.git
cd getregula

regula check examples/cv-screening-app --scope all    # high-risk verdict
regula check examples/customer-chatbot --scope all    # limited-risk verdict
regula check examples/code-completion-tool            # minimal-risk → clean
```

`--scope all` is needed because files under `examples/` carry example
provenance, and the default `--scope production` excludes their
non-minimal findings — a deliberate precision feature (your real scans
stay quiet about vendored demo code). The cv-screening project also
declares `system.domain: employment` in its `regula-policy.yaml`; since
v1.7.5 that declaration is what activates the domain-gated employment
patterns (verified 16 Jul 2026 against the released 1.7.5).

## Try Regula end-to-end in 10 minutes

[`cv-screening-app/README.md`](cv-screening-app/README.md) is a **complete
evaluation journey**: every Regula command (`check`, `plan`, `gap`,
`conform --zip`, `verify`, `handoff`, `bias`) against one realistic
high-risk fixture, with expected output for each step. End result is the
full 26-file Annex IV evidence pack + a portable `.regula.zip` bundle +
a verification report.

Use it when evaluating Regula before running against your own codebase.

## Why three fixtures

The EU AI Act sorts AI systems into four risk tiers (prohibited, high-risk,
limited-risk, minimal-risk). Each tier has different obligations. Seeing
Regula's behaviour across tiers is the fastest way to understand what it will
flag on your own code.

`regula-rules.yaml` in this directory is a separate example showing how to
define custom organisation-specific patterns.
