# regula-ignore
# Module 7: CI/CD Integration

## What You'll Learn

- Add Regula to GitHub Actions
- Configure SARIF output for the GitHub Security tab
- Set up diff-mode scanning for PRs

## GitHub Action

Add this to `.github/workflows/regula.yaml`:

```yaml
name: Regula AI Governance Scan
on: [push, pull_request]
permissions:
  security-events: write
  contents: read
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: kuzivaai/getregula@main
        with:
          path: '.'
          fail-on-prohibited: 'true'
          upload-sarif: 'true'
```

## SARIF Output

For any CI system, generate SARIF directly:

```bash
python3 scripts/cli.py check . --format sarif > results.sarif.json
```

The output is valid SARIF 2.1.0, compatible with GitHub Code Scanning, GitLab SAST, and Azure DevOps.

## Diff-Mode Scanning

Only scan files changed since a git ref:

```bash
python3 scripts/cli.py check . --diff HEAD~1
```

This is useful for PR checks — only report NEW findings from the PR's changes, not the entire project's backlog.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No BLOCK-tier findings |
| 1 | WARN-tier findings (with --strict) |
| 2 | BLOCK-tier findings (prohibited patterns or high-confidence issues) |

## Exercise

1. Generate SARIF: `python3 scripts/cli.py check . --format sarif | python3 -m json.tool | head -20`
2. Try diff mode: make a change to a file, then run `python3 scripts/cli.py check . --diff HEAD`

---

**Next:** [Module 8: Documentation Generation](08-documentation.md)
