# EU AI Regulatory Sandbox Registry

Article 57 of Regulation (EU) 2024/1689 requires each Member State to
establish at least one AI regulatory sandbox by 2 August 2026. No
central registry tracks which Member States have done so, under what
entry criteria, and which companies are enrolled.

This repository is that registry.

## Status

**Seeded scaffold, needs completion.** The 27 EU Member States are
listed in `member-states/*.json`. Five seed entries are populated
from publicly-reported announcements (FR, ES, NL, FI, DE). The
remaining 22 are TODO placeholders. A central authority scraper is
planned but not yet written.

## Layout

```
content/regulations/sandbox-registry/
├── README.md
├── schema.json
├── index.json               ← auto-generated manifest
└── member-states/
    ├── AT.json ← TODO
    ├── BE.json ← TODO
    ├── BG.json ← TODO
    ├── CY.json ← TODO
    ├── CZ.json ← TODO
    ├── DE.json ← seeded
    ├── DK.json ← TODO
    ├── EE.json ← TODO
    ├── ES.json ← seeded
    ├── FI.json ← seeded
    ├── FR.json ← seeded
    ├── GR.json ← TODO
    ├── HR.json ← TODO
    ├── HU.json ← TODO
    ├── IE.json ← TODO
    ├── IT.json ← TODO
    ├── LT.json ← TODO
    ├── LU.json ← TODO
    ├── LV.json ← TODO
    ├── MT.json ← TODO
    ├── NL.json ← seeded
    ├── PL.json ← TODO
    ├── PT.json ← TODO
    ├── RO.json ← TODO
    ├── SE.json ← TODO
    ├── SI.json ← TODO
    └── SK.json ← TODO
```

## Fields

Each entry records:

- `country` — ISO 3166-1 alpha-2
- `competent_authority` — the body operating the sandbox
- `status` — `established` / `announced` / `planned` / `none` / `unknown`
- `established_date` — when the sandbox accepted its first entrants
- `entry_criteria_url` — primary source for the rules
- `enrolled_companies` — known participants (may be empty)
- `sectors` — sectors the sandbox covers
- `source_url` — primary source
- `verified_on` — date this record was last confirmed
- `confidence` — `verified-primary` / `verified-secondary` / `reported-unverified`

## Editorial rules

1. **Primary source or nothing.** Government website, press release,
   or official gazette.
2. **Mark your confidence.** Much of the reporting around Article 57
   is pre-launch promotional — flag it as such.
3. **27 entries only.** Not 28 (UK is not in the EU).
4. **British English.**

## Contributing

Open a PR that edits a single `member-states/XX.json` file. The
maintainer will verify against the primary source before merging.

## Licence

CC-BY-4.0.
