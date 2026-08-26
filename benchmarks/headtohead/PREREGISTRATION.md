# Head-to-head benchmark pre-registration (LOCKED BEFORE ANY TOOL RUNS)

Written 27 July 2026. This document must be committed, with corpus
selection rules frozen, BEFORE any comparative tool run happens. Changing
the corpus or metric after seeing any tool's results invalidates the
study; if a change is ever genuinely required, the change and its reason
are published alongside the results.

## Commitments

1. **Publish regardless of outcome.** If Regula loses on detection, the
   results are published anyway, scoped honestly. Claims about dimensions
   Regula wins are made ONLY if those dimensions were measured.
2. **Prior-run disclosure.** Any earlier exploratory run is listed with the
   result. The confirmatory corpus and metrics remain frozen before the first
   confirmatory run.
3. **Fairness.** Each tool runs per its own documentation, latest stable
   release at run time, versions and invocation commands pinned in the
   results. Tools are not configured beyond documented defaults plus
   whatever their docs recommend for the scan scenario. Where a tool's
   scope differs (runtime vs static), the difference is stated, not
   scored against it.
4. **Metric.** The FP-penalising score in `scoring.py`, explicitly
   described as ADAPTED from the CASTLE Score (Dubniczky et al.,
   arXiv:2503.09433, Section 3.3), plus plain precision/recall per tier.
   Both reported; neither cherry-picked.
5. **Corpus.** Selected BEFORE any tool runs, by rule, not by hand:
   the random-corpus repositories (seeded selection, documented in
   benchmarks/results/random_corpus/METHODOLOGY.json) plus the synthetic
   fixture set (benchmarks/synthetic/). No repository may be added or
   removed after the first comparative run.
6. **Ground truth.** The multi-annotator corpus (MULTI_ANNOTATOR_PROTOCOL.md).
   The head-to-head is GATED on that corpus reaching >= 2 independent
   raters on the scored subset: scoring against single-rater labels would
   import exactly the weakness the upgrade exists to fix.

## Tools in scope (verified to exist, 27 Jul 2026)

| Tool | Distribution | Invocation to pin at run time |
|---|---|---|
| Regula | PyPI `regula-ai` | `regula check <path> --format json` |
| AIR Blackbox | PyPI `air-blackbox` | per its README at run time |
| Systima Comply | npm + GitHub Action | per its README at run time |
| ark-forge mcp-eu-ai-act | GitHub (MIT), CLI/MCP | per its README at run time |

Each competitor's exact package version, invocation, and output-mapping
adapter is recorded in the results file. Output mapping (their finding
categories to comparable tiers) is documented per tool and reviewed for
fairness before scoring.

## What blocks the run today

1. Ground-truth gate: the required independent labels do not yet exist.
2. Adapter implementation for the three competitor tools (mapping tables
   must be written against their CURRENT output formats at run time, not
   guessed in advance).

## Status

Harness (scoring + Regula adapter + this pre-registration): ready.
Comparative runs: NOT started, by design, per the gate above.
