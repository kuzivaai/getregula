#!/usr/bin/env python3
"""Reproduce the frozen deterministic repository selection."""

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).parent


def main():
    population = json.loads((HERE / "repository_candidates.json").read_text())
    seed = population["selection_seed_material"]
    selected = sorted(row["id"] for row in population["candidates"]
                      if row["eligible"])
    manifest = json.loads((HERE / "manifest.json").read_text())
    frozen = [row["id"] for row in manifest["layers"]["public_repositories"]]
    if selected != sorted(frozen) or len(selected) != 12:
        raise SystemExit(
            f"selection mismatch: calculated={selected}, manifest={frozen}")
    print(json.dumps({"seed_sha256": hashlib.sha256(seed.encode()).hexdigest(),
                      "selected": selected}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
