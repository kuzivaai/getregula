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

__all__ = ["extract_code", "extract_code_status", "is_notebook"]


def is_notebook(path: Union[str, Path]) -> bool:
    """Return True if path has the .ipynb extension."""
    return Path(path).suffix.lower() == ".ipynb"


def extract_code_status(path: Union[str, Path]) -> dict:
    """
    Extract code cells from a .ipynb and report a structured status so callers
    can distinguish four outcomes (review findings F3/F4):

      status:
        "ok"          — parsed as a notebook (may or may not contain code).
        "parse_error" — unreadable, not JSON, or not a notebook object.
      code:            joined code-cell source (may be "").
      has_code_cells:  True if at least one code cell was present.
      dropped_cells:   count of code cells whose `source` had an unusable type
                       (not str / not list-of-str) and were therefore NOT
                       scanned — a partial extraction the caller must surface.

    A caller building a compliance gate treats "parse_error" and
    "dropped_cells > 0" as a PARTIAL scan (fail closed), but a valid notebook
    with zero code cells (a markdown-only / freshly-created notebook) as a
    clean, complete scan — NOT a skip. Never raises.
    """
    p = Path(path)
    try:
        raw = p.read_text(encoding="utf-8", errors="ignore")
    except (OSError, PermissionError):
        return {"status": "parse_error", "code": "", "has_code_cells": False, "dropped_cells": 0}

    try:
        nb = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return {"status": "parse_error", "code": "", "has_code_cells": False, "dropped_cells": 0}

    if not isinstance(nb, dict):
        return {"status": "parse_error", "code": "", "has_code_cells": False, "dropped_cells": 0}

    cells = nb.get("cells")
    if not isinstance(cells, list):
        return {"status": "parse_error", "code": "", "has_code_cells": False, "dropped_cells": 0}

    chunks: list[str] = []
    has_code_cells = False
    dropped_cells = 0
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        if cell.get("cell_type") != "code":
            continue
        has_code_cells = True
        source = cell.get("source", "")
        # nbformat allows source to be either a list of strings or a single string.
        if isinstance(source, list):
            # A list with any non-str element is a partial extraction: some
            # source was dropped and will not be scanned.
            if any(not isinstance(s, str) for s in source):
                dropped_cells += 1
            text = "".join(s for s in source if isinstance(s, str))
        elif isinstance(source, str):
            text = source
        else:
            # Unusable source type (int/dict/None) — cell dropped, not scanned.
            dropped_cells += 1
            text = ""
        if text:
            chunks.append(text)

    # Join cells with a blank line so cell boundaries don't fuse identifiers.
    return {
        "status": "ok",
        "code": "\n\n".join(chunks),
        "has_code_cells": has_code_cells,
        "dropped_cells": dropped_cells,
    }


def extract_code(path: Union[str, Path]) -> str:
    """
    Extract code cells from a .ipynb file as a single newline-joined string.

    Returns an empty string if the file cannot be parsed as a notebook or
    contains no code cells. Never raises — corrupt notebooks are treated
    as empty so a single bad file does not abort a scan.

    Thin wrapper over extract_code_status() for the many callers that only
    want the code text. New callers that need to distinguish corrupt from
    empty should use extract_code_status().
    """
    return extract_code_status(path)["code"]
