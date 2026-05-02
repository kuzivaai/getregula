# Runtime Monitor — Design Spec

**Date:** 2026-04-23
**Status:** Draft
**Author:** Kuziva Muzondo + Claude

## Problem

Regula performs static analysis of codebases for EU AI Act risk patterns. It cannot produce evidence that a deployed AI system is being monitored at runtime — which Article 12 (record-keeping) and Article 14 (human oversight) require for high-risk systems.

AIR Blackbox (10.8K PyPI downloads, HMAC-SHA256 chains, 6-article mapping) already covers runtime monitoring via a Go reverse proxy. Regula's differentiator is not runtime monitoring alone — it is **static analysis + runtime monitoring in a single tool producing a single evidence pack.**

## Non-goals

- Replace AIR Blackbox or dedicated observability platforms (Langfuse, Datadog)
- Auto-patch third-party SDKs (monkey-patching is fragile)
- Capture full prompt/response content by default (PII risk)
- Require external dependencies for basic logging (must stay stdlib-only)
- Runtime proxy or sidecar process

## Design principles

1. **Capture automatically what you can. Ask the developer only what you must.**
2. **One tool, one evidence pack.** Static findings + runtime logs + signed manifest.
3. **Stdlib-only core.** No dependency on openai/anthropic/langchain internals.
4. **Honest about evidence strength.** Self-attesting logs, not independent observation. Document this limitation. Supplement with RFC 3161 timestamps where available.

## Regulatory grounding

Every field in the schema traces to a verified regulatory requirement:

| Requirement | Source | How satisfied |
|---|---|---|
| Automatic event recording over lifetime | Art. 12(1) | MonitorSession auto-logs every traced call |
| Period of use (start/end) | Art. 12(2)(a) (biometric ID systems only; good practice for all high-risk) | Session-level `started`/`ended` + per-event `timestamp` |
| Events relevant for identifying risk | Art. 12(1)(a) | `status`, `error`, `safety.*` fields flag anomalies |
| Post-market monitoring data | Art. 12(1)(b), Art. 72 | `latency_ms`, `error`, `status` enable trend analysis |
| 6-month minimum retention | Art. 12(3) | Monthly log rotation, configurable retention policy |
| Human oversight measures | Art. 14(3) | `human_oversight.*` fields per event |
| Ability to override/disregard output | Art. 14(4)(d) | `human_oversight.action: rejected`, `override_reason` |
| Risk management (continuous) | Art. 9(1) | `decision_context.*`, error tracking, session aggregation |
| Transparency to deployers | Art. 13(3) | `model`, `provider`, `transparency.*` |
| User informed of AI interaction | Art. 50(1) | `transparency.user_informed_ai` (applicable to specific system types only) |
| Tamper-evident logging | ISO 42001 A.6.10 (logging and monitoring) | SHA-256 hash chain (self-attesting; supplement with RFC 3161) |
| Model tracking in production | NIST AI RMF MEASURE 2.9 (model performance monitoring) | `model`, `model_version`, `system_version` |
| Prompt injection detection | OWASP LLM Top 10 LLM01:2025 | `safety.input_filtered` |
| Output validation | OWASP LLM Top 10 LLM05:2025 (insecure output handling) | `safety.output_validated` |
| Sensitive information disclosure | OWASP LLM Top 10 LLM02:2025 | `safety.pii_detected` |

**Limitation (documented honestly):** This is self-attesting evidence. The same developer who controls the application also controls the logs. For audit-grade independence, supplement with RFC 3161 external timestamps (already supported by `signing.py`) or forward logs to a SIEM. This limitation is inherent to any library-based approach (as opposed to an independent proxy like AIR Blackbox).

**Competitive honesty:** AIR Blackbox already provides regulation-mapped audit logging (6 Articles) with HMAC-SHA256 hash chains and produces evidence bundles. Regula's runtime monitor is not the first tool to do this. Regula's value is the combination of 389-pattern static analysis + runtime monitoring within a single CLI and evidence pack workflow — whether this combination is truly unique vs AIR Blackbox (which also has 26 static checks) has not been independently verified.

## Schema

### Tiered field model

Fields are split into three tiers based on who/when they are set:

**Tier 1 — Automatic (zero developer effort per call):**
Extracted from the LLM response object and timing context. Developer never touches these.

```
event_id          UUID4, auto-generated
timestamp         ISO 8601 with timezone, auto-generated
event_type        "inference" (auto) | "decision" | "override" | "error" | "feedback"
provider          Detected from response object via duck-typing
model             Extracted from response object
model_version     Extracted from response object (if available, else null)
input_tokens      Extracted from response usage (if available, else null)
output_tokens     Extracted from response usage (if available, else null)
latency_ms        Computed by trace context manager (end - start)
status            "success" | "error" | "timeout" | "filtered" (from response/exception)
error             Exception message if call failed, else null
previous_hash     SHA-256 of previous event in chain
current_hash      SHA-256 of this event
```

**Tier 2 — Declared once at session creation (system-level defaults):**
Set when creating `MonitorSession`. Apply to all events unless overridden per-event.

```
system_id           Developer-chosen name for their AI system
system_version      Application version string
environment         "production" | "staging" | "development" | custom
deployment_id       Optional, e.g., "eu-west-1" (jurisdiction tracking)
user_informed_ai    Default for Art. 50 (true/false)
consequential       Default — does this system make consequential decisions?
human_oversight_required  Default — is human review mandated for this system?
domain              Default risk domain, e.g., "customer-support", "medical", "hiring"
```

**Tier 3 — Per-event overrides (optional, for noteworthy moments):**
Used when something deviates from defaults — a human overrides output, a guardrail fires, a specific call is consequential even though the system default is non-consequential.

```
consequential           Override session default for this specific call
human_oversight:
    required            Override session default
    performed           Was oversight actually done? (bool)
    reviewer            Role label (not PII), e.g., "role:senior-analyst"
    action              "approved" | "modified" | "rejected" | "pending"
    override_reason     Free-text reason if rejected/modified
transparency:
    user_informed_ai    Override session default
    output_type         "text" | "image" | "audio" | "code" | "structured"
    confidence_score    Model confidence if available
safety:
    input_filtered      Was prompt injection filtering applied?
    output_validated    Was output sanitised before use?
    pii_detected        Was PII found in input or output?
    guardrail_triggered Name of guardrail that fired, if any
tags                    List of user-defined labels
metadata                Arbitrary key-value dict
```

### Response object duck-typing

The monitor must extract fields from response objects without importing provider SDKs. Detection strategy:

```python
def _extract_response(response) -> dict:
    """Duck-type across provider response formats.

    Handles three input types:
    - Provider SDK objects (OpenAI, Anthropic): use getattr()
    - Raw dicts (from HTTP clients): use dict access
    - Unknown objects: graceful fallback to nulls
    """
    data = {}

    if isinstance(response, dict):
        # Raw dict from requests/httpx/custom wrapper
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

    # SDK response objects: OpenAI, Anthropic, Google
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

    # Provider detection from module path
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
```

This uses only `getattr()`, `isinstance()`, `dict.get()`, and string inspection — no imports, stdlib-only.

### Providers supported at launch

| Provider | Response object | `model` | `input_tokens` | `output_tokens` | `provider` detection |
|---|---|---|---|---|---|
| OpenAI Chat Completions | `ChatCompletion` | `.model` | `.usage.prompt_tokens` | `.usage.completion_tokens` | `openai` in module |
| OpenAI Responses API | `Response` | `.model` | `.usage.input_tokens` | `.usage.output_tokens` | `openai` in module |
| Anthropic Messages | `Message` | `.model` | `.usage.input_tokens` | `.usage.output_tokens` | `anthropic` in module |
| Raw dict | `dict` | `["model"]` | `["usage"]["input_tokens"]` | `["usage"]["output_tokens"]` | `["provider"]` or `"unknown"` |
| Unknown | any object | `getattr` fallback | null | null | `"unknown"` |

Raw dicts are supported so developers using HTTP clients (requests, httpx) or custom wrappers can still use the monitor.

## Developer API

### Basic usage (common case)

```python
from monitor import MonitorSession  # bare import per Regula convention

# Create session — Tier 2 defaults declared once
session = MonitorSession(
    system_id="my-chatbot",
    system_version="2.1.0",
    environment="production",
    consequential=False,
    human_oversight_required=False,
    user_informed_ai=True,
    domain="customer-support",
)

# Trace an LLM call — Tier 1 fields captured automatically
with session.trace() as t:
    response = openai.chat.completions.create(
        model="gpt-4", messages=messages
    )
    t.record(response)

# Session end — writes session summary
session.close()
```

### Human override (Tier 3)

```python
with session.trace() as t:
    response = openai.chat.completions.create(
        model="gpt-4", messages=messages
    )
    t.record(response,
        consequential=True,
        human_oversight={"performed": True, "action": "modified",
                         "reviewer": "role:compliance-officer",
                         "override_reason": "Output referenced incorrect regulation article"},
    )
```

### Error handling

```python
with session.trace() as t:
    try:
        response = openai.chat.completions.create(
            model="gpt-4", messages=messages
        )
        t.record(response)
    except Exception as e:
        t.record_error(e)  # logs status="error", captures exception
```

### Safety annotations

```python
with session.trace() as t:
    response = client.messages.create(model="claude-sonnet-4-20250514", ...)
    t.record(response,
        safety={"input_filtered": True, "output_validated": True,
                "pii_detected": True, "guardrail_triggered": "pii-redactor"},
    )
```

### No context manager (minimal)

For developers who don't want `with` blocks:

```python
t = session.start_trace()
response = openai.chat.completions.create(model="gpt-4", messages=messages)
t.record(response)
t.end()
```

## Storage

### Log format

Append-only JSONL files, one line per event, stored at:
```
~/.regula/monitor/<system_id>/monitor_YYYY-MM.jsonl
```

Separate from the existing `~/.regula/audit/` directory (which stores Claude Code hook events). This keeps developer-application runtime logs distinct from development-tool audit logs.

### Session summary

When `session.close()` is called, a session summary record is appended:

```json
{
    "event_type": "session_summary",
    "system_id": "my-chatbot",
    "session_id": "uuid",
    "started": "ISO 8601",
    "ended": "ISO 8601",
    "total_inferences": 47,
    "total_errors": 2,
    "error_rate": 0.043,
    "human_overrides": 3,
    "models_used": ["gpt-4"],
    "avg_latency_ms": 720,
    "p95_latency_ms": 1340,
    "safety_events": {"pii_detected": 1, "guardrails_triggered": 0},
    "chain_valid": true
}
```

### Retention

Default: keep logs for 6 months (Art. 12(3) minimum). Configurable via:
```python
MonitorSession(..., retention_months=12)
```

Old log files are not auto-deleted (data destruction is the developer's responsibility) but `regula monitor prune` can clean up logs older than the retention period.

### Hash chain

Each event's `current_hash` is SHA-256 of the event data + `previous_hash`. Same algorithm as `log_event.py` (`compute_hash()`). Reuses the existing implementation — `monitor.py` imports `compute_hash` from `log_event`.

Chain verification: `regula monitor verify <system_id>` — walks the JSONL and checks every hash link. Same logic as `verify_chain()` in `log_event.py`.

## CLI commands

### `regula monitor status`

Show active monitor sessions, log file sizes, chain validity.

### `regula monitor report <system_id>`

Generate a compliance report from runtime logs:
- Total inferences, error rate, latency distribution
- Human oversight rate (what % of consequential calls were reviewed?)
- Safety event summary (PII detections, guardrail triggers)
- Anomaly detection (error rate spikes, latency degradation)
- Article-by-article readiness assessment based on the data

Output: text (default), json, html.

### `regula monitor verify <system_id>`

Verify hash chain integrity for a system's logs.

### `regula monitor prune <system_id>`

Delete logs older than retention period.

### `regula monitor export <system_id>`

Export logs as CSV (for spreadsheet analysis) or as an OTel-compatible JSON structure (future: for forwarding to Datadog/Langfuse).

## Evidence pack integration

The existing evidence pack generator (`evidence_pack.py`) already includes `05-audit-trail.json` from `log_event.py`. The runtime monitor adds a new section:

```
08-runtime-monitor.json
```

This section is included when `--runtime` flag is passed:
```bash
regula evidence-pack --sign --runtime my-chatbot .
```

It contains:
- Session summaries for the specified system
- Article-by-article assessment from runtime data
- Hash chain verification result
- Log statistics (event counts, error rates, oversight rates)

The value proposition: **one command produces a signed evidence pack containing static analysis findings, compliance gaps, remediation plan, AND runtime monitoring evidence.** (Whether this combination is unique vs competitors has not been independently verified — see competitive honesty note above.)

## File structure

```
scripts/
    monitor.py          MonitorSession, Trace, _extract_response, storage
    cli_monitor.py      CLI commands: status, report, verify, prune, export
```

Wire into `cli.py`:
- Import `cli_monitor` at the top with other cli_* imports
- Add `monitor` subparser with sub-subcommands in `_build_subparsers()`

Wire into `evidence_pack.py`:
- Import monitor log reader in the `08-runtime-monitor` section
- Gate behind `--runtime <system_id>` flag

## Testing

Tests in `tests/test_monitor.py`:

1. **MonitorSession creation** — verify Tier 2 defaults stored correctly
2. **Trace context manager** — verify timing captured (latency_ms > 0)
3. **Response extraction (OpenAI Chat Completions)** — mock response object with `.model`, `.usage.prompt_tokens`, `.usage.completion_tokens`
4. **Response extraction (OpenAI Responses API)** — mock with `.usage.input_tokens`
5. **Response extraction (Anthropic)** — mock with different module path
6. **Response extraction (raw dict)** — plain dict input
7. **Response extraction (unknown object)** — graceful fallback to nulls
8. **Hash chain** — write 10 events, verify chain, tamper one, verify fails
9. **Tier 3 overrides** — consequential override on non-consequential session
10. **Human oversight fields** — all four action types
11. **Error recording** — `trace.record_error(exception)` captures correctly
12. **Session summary** — close session, verify aggregate stats
13. **Log rotation** — events go to correct monthly file
14. **Retention** — prune deletes old files, keeps recent
15. **CLI report** — verify text output from log data
16. **CLI verify** — verify chain verification command
17. **Evidence pack integration** — `--runtime` flag includes section 08
18. **No external imports** — monitor.py only imports from stdlib + regula's own modules
19. **Thread safety** — concurrent traces in same session don't corrupt chain

## Future extensions (not in v1)

- **OTel export format** — export logs as OTel gen_ai spans for Datadog/Langfuse compatibility
- **Auto-instrumentation** — opt-in monkey-patching for openai/anthropic SDKs (after v1 proves the schema)
- **Streaming support** — capture token-by-token streaming responses
- **Framework adapters** — LangChain callback handler, CrewAI hook
- **Remote log forwarding** — push events to a SIEM or log aggregator
- **Anomaly alerting** — flag when error rate or latency exceeds thresholds
