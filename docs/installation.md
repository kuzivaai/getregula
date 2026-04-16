# Installing Regula

This page covers every supported install path, the errors you will hit if you pick the wrong one for your platform, and how to fix them.

**TL;DR:** use `pipx install regula-ai`. If you already use `uv`, use `uvx --from regula-ai regula`. Everything else is for people who know why they're doing it differently.

---

## Before you begin

You need **Python 3.10 or newer**. Check with:

```bash
python3 --version
```

If that prints `Python 3.10.x` or higher, you're set. If it prints an older version or `command not found`, install Python from [python.org/downloads](https://www.python.org/downloads/) or via your package manager (e.g. `brew install python@3.12`, `sudo apt install python3.12`).

---

## Recommended: pipx

`pipx` installs Regula into its own isolated virtualenv and puts the `regula` command on your PATH, without touching your system Python. This is the install that works on every platform and does not break on Debian/Ubuntu's externally-managed Python.

### Install pipx (one-time)

| Platform | Command |
|---|---|
| **macOS** | `brew install pipx && pipx ensurepath` |
| **Debian / Ubuntu** | `sudo apt install pipx && pipx ensurepath` |
| **Fedora** | `sudo dnf install pipx && pipx ensurepath` |
| **Arch** | `sudo pacman -S python-pipx && pipx ensurepath` |
| **openSUSE** | `sudo zypper install python3-pipx && pipx ensurepath` |
| **Windows (PowerShell)** | `python -m pip install --user pipx` then `python -m pipx ensurepath` |
| **Any Linux, no package available** | `python3 -m pip install --user pipx` then `python3 -m pipx ensurepath` |

After `pipx ensurepath` finishes, open a new terminal so the updated PATH is picked up.

### Install Regula

```bash
pipx install regula-ai
```

That's it. `regula --version` should now work from anywhere.

### Upgrading and uninstalling

```bash
pipx upgrade regula-ai
pipx uninstall regula-ai
```

---

## Alternative: uv / uvx

If you already use [uv](https://docs.astral.sh/uv/), it's faster than pipx and the install is one command.

### Run without installing

```bash
uvx --from regula-ai regula check .
```

`uvx` downloads, caches, and runs Regula in one step. The `--from regula-ai` flag is required because the PyPI package name (`regula-ai`) is different from the CLI command name (`regula`); plain `uvx regula-ai` will error with a hint.

### Install permanently

```bash
uv tool install regula-ai
```

Then `regula` is on your PATH the same way pipx would put it there.

---

## Fallback: plain pip (only inside a venv or with a flag)

Plain `pip install regula-ai` **will fail** on Ubuntu 22.04+, Debian 12+, Fedora, Arch, and macOS Homebrew Python with:

```
error: externally-managed-environment
× This environment is externally managed
```

This is PEP 668 at work — your OS doesn't want you `pip install`-ing packages into the Python it uses to run system tools. You have three options:

### Inside a virtualenv (safest)

```bash
python3 -m venv .venv
source .venv/bin/activate     # or .venv\Scripts\activate on Windows
pip install regula-ai
```

### Inside a conda env

```bash
conda create -n regula python=3.12
conda activate regula
pip install regula-ai
```

### `pip --user --break-system-packages` (only if you know what this means)

```bash
pip install --user --break-system-packages regula-ai
```

This installs into `~/.local/` and explicitly overrides PEP 668. Use it only if you accept that you may step on your distro's Python packaging later. For most people, pipx is what this flag wanted to be.

---

## Windows

Windows does not enforce PEP 668, so `pip install regula-ai` technically works — but pipx is still recommended for the same reasons (isolated, upgradeable, on PATH).

### PowerShell (recommended)

```powershell
python -m pip install --user pipx
python -m pipx ensurepath
# Close & reopen PowerShell so PATH updates, then:
pipx install regula-ai
regula --version
```

### cmd.exe

Identical to PowerShell — `python -m pipx ensurepath` writes the PATH update to your user environment regardless of shell. You will need to open a fresh cmd window for the change to take effect.

### PATH on Windows 11

If `regula` still isn't found after reopening your terminal, the pipx bin directory may not be on PATH. pipx installs binaries to `%USERPROFILE%\.local\bin` on modern Windows. Add it manually:

1. Start → "Edit environment variables for your account"
2. Select **Path** → Edit → New
3. Add `%USERPROFILE%\.local\bin`
4. OK through every dialog; open a new terminal.

---

## Verifying your install

Regardless of install method, verify with:

```bash
regula --version
```

You should see a line like `regula 1.6.x`.

To verify the scanner actually works, clone the repo and scan one of the fixtures:

```bash
git clone https://github.com/kuzivaai/getregula.git
cd getregula
regula check examples/cv-screening-app
```

You should see exactly one WARN finding flagging the high-risk employment pattern:

```
  HIGH-RISK INDICATORS:
    [WARN] [ 68] app.py — Employment and workers management
      Add human oversight before automated hiring/employment decisions
```

See [`examples/README.md`](../examples/README.md) for the other two fixtures (Article 50 limited-risk chatbot, minimal-risk code-completion tool).

---

## Troubleshooting

Error messages here are the literal strings you'll paste into a search engine. Match the one you're seeing and jump to the fix.

### `error: externally-managed-environment`

Your OS ships Python under PEP 668 protection. Use pipx:

```bash
# Linux
sudo apt install pipx || sudo dnf install pipx || sudo pacman -S python-pipx
pipx ensurepath
pipx install regula-ai

# macOS
brew install pipx
pipx ensurepath
pipx install regula-ai
```

See the pipx section above for the full table.

### `command not found: regula` (after install)

The install succeeded but your shell can't find the binary. pipx puts binaries in `~/.local/bin` (Linux/macOS) or `%USERPROFILE%\.local\bin` (Windows). These need to be on your PATH.

**Quick check:**

```bash
ls -l ~/.local/bin/regula     # should exist after pipx install
echo $PATH | tr ':' '\n' | grep '.local/bin'  # should print the path
```

**Fix per shell:**

- **bash:** add `export PATH="$HOME/.local/bin:$PATH"` to `~/.bashrc`, then `source ~/.bashrc`.
- **zsh (macOS default):** add the same line to `~/.zshrc`.
- **fish:** `fish_add_path ~/.local/bin` (persistent, no file editing).
- **PowerShell (Windows):** the `pipx ensurepath` command above handles this. If it didn't, add `%USERPROFILE%\.local\bin` manually as described in the Windows section.

Alternatively, run `pipx ensurepath` again and open a fresh terminal.

### `pip: command not found`

You don't have Python installed, or it was installed without pip. Install Python 3.10+ from [python.org/downloads](https://www.python.org/downloads/) or your package manager:

- macOS: `brew install python@3.12`
- Debian/Ubuntu: `sudo apt install python3 python3-pip`
- Fedora: `sudo dnf install python3 python3-pip`
- Windows: download the installer from python.org and tick "Add python.exe to PATH" during setup.

Then rerun the install.

### `ModuleNotFoundError: No module named 'yaml'` when running bias / pdf / ast features

Regula's core is stdlib-only, but three optional subsystems (YAML policy parsing, PDF export, deep AST parsing) pull in extras. Install with:

```bash
pipx install "regula-ai[yaml,ast,pdf]"
# or with pip inside a venv:
pip install "regula-ai[yaml,ast,pdf]"
```

### `regula check` shows `Files scanned: 0`

Two likely causes:

1. **You pointed at a directory with no code files matching Regula's extensions.** Regula scans `.py, .js, .ts, .jsx, .tsx, .java, .go, .rs, .c, .cpp, .mjs, .cjs, .ipynb`. The CLI now tells you this with `(no code files matched; check path and extensions)` rather than the old misleading `(test files excluded)` suffix.
2. **You're on an older release.** Versions before 1.6.1 had a telemetry bug where a clean scan could misreport 0 files scanned. Upgrade: `pipx upgrade regula-ai` (once 1.6.1+ is published — see the PyPI release-gap issue tracked separately).

### `regula: permission denied`

On macOS/Linux, check the binary is executable: `ls -l $(which regula)`. If the `x` bit is missing, `chmod +x` it. If pipx installed it, uninstall and reinstall: `pipx uninstall regula-ai && pipx install regula-ai`.

---

## Upgrading existing installs

```bash
pipx upgrade regula-ai        # pipx
uv tool upgrade regula-ai     # uv
pip install --upgrade regula-ai  # pip (inside venv)
```

---

## Uninstalling

```bash
pipx uninstall regula-ai      # pipx
uv tool uninstall regula-ai   # uv
pip uninstall regula-ai       # pip
```

All three remove only Regula. They do not remove the optional policy file at `~/.regula/regula-policy.yaml` or the audit log at `~/.regula/audit/` — delete those manually if you want a clean slate.
