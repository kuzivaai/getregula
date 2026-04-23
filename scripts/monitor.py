#!/usr/bin/env python3
# regula-ignore
"""
Regula Runtime Monitor — Article 12 logging for AI applications.

Provides MonitorSession and Trace for developers to instrument LLM calls
in their own applications. Produces hash-chained JSONL audit logs that
map to EU AI Act Articles 9, 12, 13, 14, and 50.

Limitation: self-attesting evidence. The same developer who controls
the application controls the logs. Supplement with RFC 3161 external
timestamps for audit-grade independence.
"""

import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))

from log_event import compute_hash, _read_last_hash, _lock_file, _unlock_file


def _extract_response(response) -> dict:
    """Duck-type across provider response formats.

    Handles three input types:
    - Provider SDK objects (OpenAI, Anthropic): use getattr()
    - Raw dicts (from HTTP clients): use dict access
    - Unknown objects: graceful fallback to nulls
    """
    data: Dict[str, Any] = {}

    if isinstance(response, dict):
        data["model"] = response.get("model")
        usage = response.get("usage", {})
        data["input_tokens"] = (
            usage.get("input_tokens") or usage.get("prompt_tokens")
        )
        data["output_tokens"] = (
            usage.get("output_tokens") or usage.get("completion_tokens")
        )
        data["provider"] = response.get("provider", "unknown")
        return data

    data["model"] = getattr(response, "model", None)

    usage = getattr(response, "usage", None)
    if usage:
        data["input_tokens"] = (
            getattr(usage, "input_tokens", None)
            or getattr(usage, "prompt_tokens", None)
        )
        data["output_tokens"] = (
            getattr(usage, "output_tokens", None)
            or getattr(usage, "completion_tokens", None)
        )

    module = type(response).__module__ or ""
    if "openai" in module:
        data["provider"] = "openai"
    elif "anthropic" in module:
        data["provider"] = "anthropic"
    elif "google" in module:
        data["provider"] = "google"
    else:
        data["provider"] = getattr(response, "provider", "unknown")

    return data
