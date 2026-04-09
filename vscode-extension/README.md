# Regula — VS Code Extension

**Status: work in progress (v0.1.0), not yet published to the Visual Studio Marketplace.**

This directory contains the in-development VS Code extension for Regula.
It is intentionally minimal (a single `src/extension.ts` file and a
package manifest) and exists in the public repo so that anyone who wants
to contribute editor integration can pick it up.

## What it will do (when shipped)

- Surface Regula findings inline in the VS Code diagnostics panel
- Block saves that introduce Article 5 prohibited-practice patterns
- Annotate AI-related code with the matching EU AI Act Article

## What it does NOT do today

- It is not installable from the Marketplace yet.
- It has no tests, no CI, and no release tag.
- The extension host integration is a skeleton — it shells out to the
  `regula` CLI, so you need Regula installed separately.

## Contributing

If you have VS Code extension experience and want to help land a v1.0,
open an issue tagged `vscode-extension` at
https://github.com/kuzivaai/getregula/issues — or just open a PR.

## When will it ship?

When the core Regula CLI (v1.6.x) stabilises and there is a clear
Marketplace publisher story. No fixed date. Follow the CHANGELOG for
updates.
