# Regula — EU AI Act Compliance for VS Code

Scans your AI code for regulatory risk patterns. Shows findings inline as you type. Zero data transmission — your code stays on your machine.

## What it does

If your product uses AI and has EU users, the EU AI Act applies. Regula scans for 398 risk patterns across Python, JavaScript, TypeScript, Java, Go, Rust, C, and C++ and tells you which risk tier each finding falls into.

## Features

- Scan on save (configurable)
- Inline WARN/BLOCK decorations
- Quick-fix: `# regula-ignore` and `# regula-accept` annotations
- Workspace-wide scan command
- Status bar indicator

## Requirements

Install the Regula CLI: `pipx install regula-ai`

## Privacy

Regula runs entirely on your machine. No code is uploaded, no telemetry is sent, no account is needed.
