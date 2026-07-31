#!/usr/bin/env python3
"""Deterministic normalisation for commercial_v1 tool records."""

import json
from pathlib import Path


VOLATILE_FIELDS = {
    "duration", "duration_seconds", "finished_at", "peak_memory_kb",
    "peak_memory_kb_delta", "raw_stderr", "raw_stdout", "started_at",
    "timestamp", "working_directory",
}


def _clean(value):
    if isinstance(value, dict):
        return {key: _clean(item) for key, item in sorted(value.items())
                if key not in VOLATILE_FIELDS}
    if isinstance(value, list):
        return [_clean(item) for item in value]
    return value


def _normalise_command(command):
    normalised = []
    for token in command:
        text = str(token)
        if "/cases/" in text:
            normalised.append("<CASE_DIR>")
        elif text.startswith("/") and ("python" in Path(text).name):
            normalised.append("<PYTHON>")
        else:
            normalised.append(text)
    return normalised


def normalise(records):
    """Drop declared volatile fields and sort records by canonical JSON."""
    cleaned = []
    for record in records:
        item = _clean(record)
        if isinstance(item, dict) and isinstance(item.get("command"), list):
            item["command"] = _normalise_command(item["command"])
        cleaned.append(item)
    return sorted(cleaned, key=lambda row: json.dumps(
        row, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def main(argv=None):
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    payload = json.loads(args.input.read_text())
    records = payload.get("records", payload) if isinstance(payload, dict) else payload
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(normalise(records), indent=2,
                                      ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
