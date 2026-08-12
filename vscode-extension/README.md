# Regula: EU AI Act Review for VS Code

Scans code for regulatory review patterns and shows them inline. The CLI decision kernel separately reports whether sourced facts support a determination. Your code stays on your machine.

## What it does

Regula scans for code patterns across Python, JavaScript, TypeScript, Java, Go, Rust, C, and C++. Pattern matches are detector observations, not legal classifications. Territorial scope, the legal AI-system definition, intended purpose, operator role, exclusions, and exceptions require sourced facts that code alone cannot establish.

## Features

- Scan on save (configurable)
- Inline detector-priority decorations
- Quick-fix: `# regula-ignore` and `# regula-accept` annotations
- Workspace-wide scan command
- Status bar indicator

## Requirements

Install the Regula CLI: `pipx install regula-ai`

## Privacy

Regula runs entirely on your machine. No code is uploaded, no telemetry is sent, and no account is needed.
