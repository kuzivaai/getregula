# examples/ — runnable fixtures for Regula

Three minimal projects, one per EU AI Act risk tier, so new users can see what
Regula flags without needing their own codebase. Each directory has its own
README with the exact output of `regula check` verified against the current
release.

| Directory                    | EU AI Act tier             | Expected finding              |
| ---------------------------- | -------------------------- | ----------------------------- |
| `cv-screening-app/`          | High-risk (Annex III, 4)   | 1 WARN — employment pattern   |
| `customer-chatbot/`          | Limited-risk (Article 50)  | 1 INFO — chatbot transparency |
| `code-completion-tool/`      | Minimal-risk               | clean scan, 0 findings        |

## Quick start

```
pip install regula-ai
git clone https://github.com/kuzivaai/getregula.git
cd getregula

regula check examples/cv-screening-app       # high-risk → 1 WARN
regula check examples/customer-chatbot       # limited-risk → 1 INFO (use --verbose to see file:line)
regula check examples/code-completion-tool   # minimal-risk → clean
```

## Why three fixtures

The EU AI Act sorts AI systems into four risk tiers (prohibited, high-risk,
limited-risk, minimal-risk). Each tier has different obligations. Seeing
Regula's behaviour across tiers is the fastest way to understand what it will
flag on your own code.

`regula-rules.yaml` in this directory is a separate example showing how to
define custom organisation-specific patterns.
