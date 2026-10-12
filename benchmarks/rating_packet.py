#!/usr/bin/env python3
"""Versioned rating-packet loader shared by agreement utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
ITEM_ID_SCHEME = "corpus-project-file-line-v1"
LABELS = {"tp", "fp"}


class RatingPacketError(ValueError):
    """The packet cannot be interpreted without inventing evaluation data."""


def canonical_item_id(entry: dict[str, Any], corpus: str) -> str:
    """Return the stable evaluation-item identifier for one packet entry."""
    explicit = str(entry.get("item_id") or entry.get("id") or "").strip()
    if explicit:
        return explicit

    file_path = str(entry.get("file") or "").strip().replace("\\", "/")
    line = entry.get("line")
    if not corpus or not file_path or line in (None, ""):
        raise RatingPacketError(
            "each rating item requires corpus, file and line, or an explicit item_id"
        )
    project = str(entry.get("project") or "_unattributed").strip()
    return f"{corpus}::{project}::{file_path}::{line}"


def load_packet(path: Path) -> dict[str, Any]:
    """Load and validate a packet while preserving unrated items as missing."""
    packet_path = Path(path)
    with packet_path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise RatingPacketError("rating packet must be a JSON object")
    version = data.get("schema_version")
    if version != SCHEMA_VERSION:
        raise RatingPacketError(
            f"unsupported rating packet schema {version!r}; expected {SCHEMA_VERSION!r}"
        )
    if data.get("item_id_scheme") != ITEM_ID_SCHEME:
        raise RatingPacketError(
            f"unsupported item_id_scheme {data.get('item_id_scheme')!r}"
        )
    corpus = str(data.get("corpus") or "").strip()
    entries = data.get("labels")
    if not isinstance(entries, list):
        raise RatingPacketError("rating packet requires a labels list")

    item_ids: list[str] = []
    labels: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise RatingPacketError("every labels entry must be an object")
        item_id = canonical_item_id(entry, corpus)
        if item_id in item_ids:
            raise RatingPacketError(f"duplicate rating item_id: {item_id}")
        item_ids.append(item_id)
        label = str(entry.get("label") or "").strip().lower()
        if label in LABELS:
            labels[item_id] = label
        elif label:
            raise RatingPacketError(
                f"unsupported label {label!r} for item {item_id}"
            )

    return {
        "schema_version": version,
        "item_id_scheme": ITEM_ID_SCHEME,
        "corpus": corpus,
        "item_ids": item_ids,
        "labels": labels,
        "rated_count": len(labels),
        "unrated_count": len(item_ids) - len(labels),
    }


def load_labels(path: Path) -> dict[str, str]:
    """Compatibility helper returning only completed labels."""
    return load_packet(path)["labels"]
