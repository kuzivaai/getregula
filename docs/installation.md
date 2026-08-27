# Installing Regula

Regula requires Python 3.10 or later. The core has no required third-party runtime dependencies.

## Current distribution status

As verified on 27 August 2026, `https://pypi.org/pypi/regula-ai/json` returns HTTP 404 and the public GitHub repository has no GitHub Release for version 2.0.0. Do not use the bare registry commands `pip install regula-ai` or `pipx install regula-ai`: they do not currently resolve to a public package.

The supported temporary path is installation from the public GitHub source:

```bash
pipx install git+https://github.com/kuzivaai/getregula.git@main
```

`main` is a moving source reference. It is convenient for evaluation, but it is not an immutable or signed release artefact. For reproducible use, pin the exact public commit you reviewed:

```bash
pipx install git+https://github.com/kuzivaai/getregula.git@COMMIT_SHA
```

Replace `COMMIT_SHA` with a full commit hash from the repository. Verify the commit and the project’s published security evidence before relying on it.

## Before you begin

Check Python:

```bash
python3 --version
```

If it is older than 3.10, install a current Python from [python.org](https://www.python.org/downloads/) or your operating-system package manager.

## Recommended temporary path: pipx

`pipx` keeps Regula isolated from the system Python and puts `regula` on the command path.

| Platform | Install pipx once |
|---|---|
| macOS | `brew install pipx && pipx ensurepath` |
| Debian / Ubuntu | `sudo apt install pipx && pipx ensurepath` |
| Fedora | `sudo dnf install pipx && pipx ensurepath` |
| Arch | `sudo pacman -S python-pipx && pipx ensurepath` |
| openSUSE | `sudo zypper install python3-pipx && pipx ensurepath` |
| Windows | `python -m pip install --user pipx` then `python -m pipx ensurepath` |

Open a new terminal after `pipx ensurepath`, then install and verify:

```bash
pipx install git+https://github.com/kuzivaai/getregula.git@main
regula --version
regula self-test
regula doctor
```

To refresh a source installation after reviewing the new commit:

```bash
pipx uninstall regula-ai
pipx install git+https://github.com/kuzivaai/getregula.git@main
```

To remove it:

```bash
pipx uninstall regula-ai
```

## Alternative: uv

Run without a persistent installation:

```bash
uvx --from git+https://github.com/kuzivaai/getregula.git@main regula check .
```

Or install it as a tool:

```bash
uv tool install git+https://github.com/kuzivaai/getregula.git@main
regula --version
```

Use a full commit hash instead of `main` when reproducibility matters.

## Alternative: a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install git+https://github.com/kuzivaai/getregula.git@main
regula self-test
```

Avoid installing into an operating system’s managed Python. If you see `error: externally-managed-environment`, use pipx or a virtual environment; do not disable the operating system’s protection.

## Install from a reviewed local checkout

This is the clearest path for contributors and for organisations that archive the exact source they evaluated:

```bash
git clone https://github.com/kuzivaai/getregula.git
cd getregula
git checkout COMMIT_SHA
pipx install .
regula self-test
```

Run directly from the checkout without installing:

```bash
python3 -m scripts.cli --version
python3 -m scripts.cli self-test
```

## Optional features

The core scan is standard-library only. Optional features add dependencies and may add network access. From a reviewed checkout, install only the extras you need:

```bash
pip install '.[yaml]'     # YAML policy support
pip install '.[ast]'      # syntax-aware JavaScript/TypeScript analysis
pip install '.[pdf]'      # PDF output
pip install '.[signing]'  # Ed25519 signing and RFC 3161 verification
pip install '.[all]'      # all user-facing optional features
```

Review [`pyproject.toml`](../pyproject.toml) for the exact dependency boundaries. Telemetry remains opt-in; timestamping and configured remote integrations can make network requests.

## Verify the installation

```bash
regula --version
regula self-test
regula doctor
```

To exercise a tracked fixture, use a repository checkout because examples are not included in the installed package:

```bash
regula check examples/cv-screening-app --scope all
```

The fixture should produce an employment-related code indicator. It does not prove the legal classification of a real product.

## Troubleshooting

### `command not found: regula`

Open a new terminal after `pipx ensurepath`. If the problem remains, run `pipx ensurepath` again and inspect `pipx environment` rather than guessing the binary location.

### `error: externally-managed-environment`

Use pipx or create a virtual environment. Do not use `--break-system-packages` merely to install this CLI.

### `git` is not installed

The temporary source-install path requires Git. Install Git from [git-scm.com](https://git-scm.com/downloads) or your package manager, then repeat the command.

### Optional feature reports a missing module

Install the matching extra from a reviewed checkout. `regula doctor` reports available and missing optional capabilities.

### `regula check` reports zero scanned files

Confirm the path contains a supported source-code extension and inspect the command’s skipped-file summary. Default production scope deliberately excludes test, benchmark, example, dependency, generated, and other non-production directories. Use `--scope all` only when you intentionally want those paths included.

## Distribution limitation

Source installation is a stopgap, not a substitute for a release process. A future public release should provide an immutable tag, build provenance, signed or attested artefacts, checksums, an installation test from the public registry, and rollback instructions. Until then, treat the exact commit hash as part of your evidence.
