#!/usr/bin/env python3
"""Version consistency check between cli.py and pyproject.toml.

Called by Claude Code Stop hook to warn about version drift.
"""
import re
import sys
from pathlib import Path

root = Path(__file__).parent.parent

cli_path = root / "scripts" / "cli.py"
toml_path = root / "pyproject.toml"

cli_version = None
toml_version = None

if cli_path.exists():
    m = re.search(r'VERSION\s*=\s*"([^"]+)"', cli_path.read_text(encoding="utf-8"))
    if m:
        cli_version = m.group(1)

if toml_path.exists():
    m = re.search(r'version\s*=\s*"([^"]+)"', toml_path.read_text(encoding="utf-8"))
    if m:
        toml_version = m.group(1)

if cli_version and toml_version and cli_version != toml_version:
    print(
        f"WARNING: Version mismatch — cli.py={cli_version} vs pyproject.toml={toml_version}",
        file=sys.stderr,
    )
