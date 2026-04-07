# regula-ignore
"""
Jupyter notebook (.ipynb) source extraction.

Extracts code cells from a .ipynb file and returns them as a single string
that can be fed through Regula's existing classification pipeline.

Limitations (v1):
- Line numbers in findings refer to the position in the joined source,
  not to the original notebook cell. A cell-aware mapping is a future
  enhancement.
- Markdown and raw cells are skipped.
- Magics (%matplotlib, !pip install) are kept as-is — the classifier
  treats them as comments / shell, which is acceptable for risk scanning.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union

__all__ = ["extract_code", "is_notebook"]


def is_notebook(path: Union[str, Path]) -> bool:
    """Return True if path has the .ipynb extension."""
    return Path(path).suffix.lower() == ".ipynb"


def extract_code(path: Union[str, Path]) -> str:
    """
    Extract code cells from a .ipynb file as a single newline-joined string.

    Returns an empty string if the file cannot be parsed as a notebook or
    contains no code cells. Never raises — corrupt notebooks are treated
    as empty so a single bad file does not abort a scan.
    """
    p = Path(path)
    try:
        raw = p.read_text(encoding="utf-8", errors="ignore")
    except (OSError, PermissionError):
        return ""

    try:
        nb = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return ""

    if not isinstance(nb, dict):
        return ""

    cells = nb.get("cells")
    if not isinstance(cells, list):
        return ""

    chunks: list[str] = []
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        if cell.get("cell_type") != "code":
            continue
        source = cell.get("source", "")
        # nbformat allows source to be either a list of strings or a single string
        if isinstance(source, list):
            text = "".join(s for s in source if isinstance(s, str))
        elif isinstance(source, str):
            text = source
        else:
            continue
        if text:
            chunks.append(text)

    # Join cells with a blank line so cell boundaries don't fuse identifiers
    return "\n\n".join(chunks)
