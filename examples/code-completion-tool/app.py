"""Minimal code-completion reference app for Regula.

This example intentionally scans clean (minimal-risk) under the EU AI
Act. It exists so Regula users have a runnable fixture that shows what
a low-risk developer tool looks like under scan — not as production code.

What it does
------------
Accepts a partial Python line and returns the rest of a trivial
completion from a static lookup table. No ML model, no network calls,
no decision about a natural person.

Why it is minimal-risk under the EU AI Act
------------------------------------------
A developer-productivity utility that does not make decisions about
natural persons and does not fall under any Annex III category is
outside the scope of Articles 9-15 and Article 50 obligations.

See: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202401689
"""
from __future__ import annotations

_SNIPPETS: dict[str, str] = {
    "def ": "function_name(arg):\n    return arg",
    "class ": "ClassName:\n    def __init__(self):\n        pass",
    "for ": "item in iterable:\n    print(item)",
    "if ": "condition:\n    pass",
    "import ": "module",
}


def suggest(prefix: str) -> str | None:
    """Return the first snippet whose trigger the prefix ends with."""
    for trigger, body in _SNIPPETS.items():
        if prefix.endswith(trigger):
            return body
    return None


if __name__ == "__main__":
    print(suggest("def "))
    print(suggest("class "))
