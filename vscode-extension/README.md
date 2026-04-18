# Regula -- EU AI Act Compliance for VS Code

Scans your code for EU AI Act risk patterns directly in the editor.

## Requirements

- [Regula CLI](https://pypi.org/project/regula-ai/) installed: `pip install regula-ai`
- Python 3.10+

## Features

- Inline diagnostics (squiggly underlines) for risk patterns
- Severity mapped from tier: Prohibited = Error, High-Risk = Warning, Limited = Info
- Lifecycle phase shown in diagnostic messages
- Quick-fix actions: `# regula-ignore` and `# regula-accept`
- Scan on save (configurable)
- Workspace scan command

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `regula.scanOnSave` | `true` | Scan files on save |
| `regula.minTier` | `limited_risk` | Minimum tier to display |
| `regula.scope` | `all` | `production` excludes test/example files |
| `regula.executablePath` | `regula` | Path to regula CLI |

## Commands

- `Regula: Scan Current File` -- scan the active file
- `Regula: Scan Workspace` -- scan the entire workspace
