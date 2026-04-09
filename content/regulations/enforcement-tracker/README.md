# EU AI Act Enforcement Tracker

A structured, primary-source-linked record of every enforcement action
under Regulation (EU) 2024/1689. Parallel in intent to the
CMS GDPR Enforcement Tracker.

## Status

**Pre-populated skeleton, zero entries.** Article 99 penalties apply
from 2 August 2026 (or later if the Digital Omnibus is adopted). This
repository exists ahead of the first fine so that:

1. When the first enforcement action lands, the entry can be published
   within hours, not weeks.
2. The schema is stable from day one — every downstream consumer
   (compliance vendors, journalists, researchers) can build against a
   known shape.
3. The domain, URL structure, and citation pattern become the default
   reference before any commercial alternative fills the gap.

## Layout

```
content/regulations/enforcement-tracker/
├── README.md              ← you are here
├── schema.json            ← JSON Schema for every entry
├── index.json             ← auto-generated manifest (empty until first entry)
└── actions/
    └── YYYY-MM-DD-slug.json
```

## Editorial rules

Same as the delta log:

1. **Primary source or nothing.** Aggregator press is not a primary
   source. Cite the authority's own publication, the official journal,
   or the court ruling directly.
2. **Structured, not narrative.** Every entry fills the schema. Prose
   commentary belongs in the `summary` field, not in loose blog posts.
3. **Confidence labelled.** `verified-primary` only when the authority
   has published the decision itself. Press coverage is
   `verified-secondary`. Pre-announcement leaks are `reported-unverified`.
4. **No fabrication.** An empty tracker is better than a speculative
   one.
5. **British English.**

## Fields

See `schema.json` for the full specification. Summary:

- `id` — `YYYY-MM-DD-slug`
- `authority` — National Competent Authority, Market Surveillance
  Authority, notified body, European AI Office, or court
- `respondent` — the entity subject to the action
- `country` — ISO 3166-1 alpha-2
- `article_cited` — which articles are invoked
- `action_type` — one of eight enumerated action types
- `fine_amount_eur` / `turnover_percentage` — where applicable
- `source_url` — primary source
- `confidence` — labelled on every entry
- `appeal_status` — tracks whether the decision has been challenged

## Reading the tracker programmatically

```bash
# Regula CLI (planned) — fetch the tracker and surface actions that
# match any pattern the local scan flagged.
regula enforcement --format json

# RSS feed (auto-generated when the first entry lands)
curl https://getregula.com/content/regulations/enforcement-tracker/feed.xml
```

## Why this exists, bluntly

No existing publication covers EU AI Act enforcement as a structured
dataset. The CMS GDPR Enforcement Tracker is a proven precedent for the
GDPR regime. This tracker replicates that precedent for the AI Act.
Being first with a clean schema and a maintained feed is the entire
moat.

## Licence

CC-BY-4.0. Cite as: *Regula EU AI Act Enforcement Tracker,
getregula.com, accessed YYYY-MM-DD.*
