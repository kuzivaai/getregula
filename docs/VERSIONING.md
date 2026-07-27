# Versioning and Deprecation Policy

> **Scheme:** Semantic Versioning 2.0.0, expressed within PEP 440.
> **Adopted:** 27 July 2026, with the 1.9.0 realignment release.
> **Enforced by:** `scripts/release_gate.py`, run by `release.yml` before
> every build; a release whose version bump understates its content does
> not publish.

## 1. Why this document exists

[`CHANGELOG.md`](../CHANGELOG.md) has claimed Semantic Versioning in its
header since 1.0.0, but the 1.7.x line shipped new functionality in
PATCH releases six times (its 1.7.2, 1.7.3, 1.7.5, 1.7.6, 1.7.8 and
1.7.10 sections all carry "Added" entries or feat content). SemVer 2.0.0 item 7 requires a MINOR increment for new
backward-compatible functionality, so those numbers understated what the
releases contained. Nothing checked the bump against the content, so the
drift went unnoticed until a user asked why the version was still 1.7.

SemVer's own remediation rule applies: released versions are immutable;
you correct a versioning mistake by releasing a new, correctly numbered
version, never by renaming or republishing old ones. **1.9.0 is that
corrective release.** Sections 5 and 6 record the decision in full.

## 2. The public API

SemVer item 1 requires a declared public API. Regula's public API, for
versioning purposes, is exactly this list:

| Surface | Covered |
|---|---|
| CLI commands and subcommands | Names and documented behaviour of every command in `regula --help-all` |
| Documented flags | Name, accepted values and documented semantics |
| Exit codes | The documented meanings (0 success, 1 findings/CI failure, 2 usage error) |
| JSON output envelope | The `json_output()` envelope structure (frozen) and documented field semantics |
| SARIF output | The structure consumed by GitHub code scanning |
| Evidence Format | `docs/spec/regula-evidence-format-v1.md` |
| Config file contracts | `regula-policy.yaml` / `regula-policy.json` and `regula-rules.yaml` accepted structure |
| Delta-log schema | `content/regulations/delta-log/schema.json` |

Explicitly **not** public API:

- Python import paths (`scripts/*`): Regula is a CLI, not a library.
  Importing its internals is unsupported and may break in any release.
- Detection pattern internals, tier regex counts and precision figures:
  these are quality characteristics, not interface contracts.
- The website, documentation prose and example artefacts.

## 3. Bump rules

| Change | Bump | Notes |
|---|---|---|
| Backward-incompatible change to any Section 2 surface | **MAJOR** | Includes removing or renaming a command or flag, renumbering exit codes, envelope changes, an incompatible Evidence Format revision |
| New command, flag, output field, framework mapping or jurisdiction | **MINOR** | New backward-compatible functionality |
| Deprecating any public API element | **MINOR** | SemVer item 7 makes deprecation a MINOR event |
| Bug fix, security fix with unchanged interface, pattern tuning, docs, site, CI | **PATCH** | |
| New detection patterns within existing commands | **MINOR** if they add a documented capability (a new category, tier or check), **PATCH** if they tune recall/precision of an existing one | Judgement call; the release gate takes the stricter of commit-type and changelog signals |

## 4. Deprecation policy

- A deprecation is announced in the CHANGELOG under `### Deprecated` and
  emits a runtime warning naming the replacement.
- Deprecated elements keep working for **at least one MINOR release and
  at least 90 days**, whichever is longer, before removal. The 90-day
  floor matches the common public-API norm (Kubernetes and Salesforce
  hold longer windows; 30 days is the minimum seen in major-vendor
  policies; 90 is a deliberate middle).
- Removal happens only in a **MAJOR** release.

## 5. The 1.7.x correction record

Releases whose numbers understated their content, from the CHANGELOG:

| Released as | Contained | SemVer-correct bump |
|---|---|---|
| 1.7.2 | Added | minor |
| 1.7.3 | Added | minor |
| 1.7.5 | Added (multiple) | minor |
| 1.7.6 | Added (DPV-AIAct export, a new command) | minor |
| 1.7.8 | Added | minor |
| 1.7.10 | feat commits (13th framework, MITRE ATLAS additions, enacted-Omnibus behaviour) | minor |

A strict reconstruction would place the project near 1.13.0, but that
number depends on judgement calls about each "Added" entry made months
later, so it is not recoverable with confidence. The realignment
therefore does not claim to compute the true number; it picks a clearly
documented reset point and enforces correctness from there.

## 6. Why 1.9.0, and why not the alternatives

- **Not 2.0.0:** SemVer reserves MAJOR for backward-incompatible
  changes. Nothing shipped or planned breaks the Section 2 API; a 2.0.0
  would tell users to expect breakage that does not exist.
- **Not 1.10.0 or higher:** PEP 440 orders release segments numerically,
  so 1.9.0 < 1.10.0 < 1.90.0; but humans routinely misread 1.10 as
  older than 1.9, and a compliance tool should not spend trust
  explaining its own version string. 1.9.0 is unambiguous.
- **Not 1.8.0:** equally legal, but the drift spans six releases, and
  the smallest possible bump reads as routine rather than corrective.
  1.9.0 marks the reset visibly while staying inside the 1.x line.
- **Not CalVer:** pip and black use calendar versioning because their
  releases are time-driven and compatibility signalling matters less.
  Regula's users pin it in CI and read the version as a compatibility
  promise; discarding SemVer's signal would remove exactly the
  information a compliance tool's version exists to carry.
- **Skipping 1.8.0 is precedented and legal:** SemVer only requires
  monotonic increase; React jumped 0.14 to 15 and PHP jumped 5 to 7,
  both with documented rationale. The rationale here is this document.

## 7. Enforcement

`scripts/release_gate.py` runs in `release.yml` before build and
publish. It derives the minimum required bump from two independent
signals: conventional-commit subjects since the previous release tag
(feat requires minor; `!` or BREAKING CHANGE requires major) and the
target version's CHANGELOG section (Added/Deprecated require minor;
Removed requires major). The actual bump must be at least the stricter
signal; over-bumping is always allowed, under-bumping fails the release
before anything is built. Unit tests in `tests/test_release_gate.py`
pin the logic, including a regression test proving the gate would have
failed the misnumbered v1.7.10.

## 8. Criteria for a future 2.0.0

A MAJOR release happens only when a Section 2 surface breaks:
an Evidence Format revision without backward compatibility, removal of
a deprecated command or flag after its Section 4 window, an envelope
change, or exit-code renumbering. Feature accumulation alone never
justifies a MAJOR bump.

## Sources

- [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html):
  items 1 and 6-8, and the FAQ remediation rule for misnumbered releases.
- [PEP 440 / Version specifiers](https://packaging.python.org/specifications/version-specifiers/):
  numeric per-segment ordering.
- [Python Packaging User Guide, Versioning discussion](https://packaging.python.org/en/latest/discussions/versioning/):
  scheme choice is the maintainer's; SemVer vs CalVer trade-offs.
- [React versioning policy](https://react.dev/community/versioning-policy) and the
  [0.14 to 15 jump](https://www.infoq.com/news/2016/02/react-version-bumped-to-15);
  [PHP's missing 6](https://ma.ttias.be/php6-missing-version-number/): version-jump precedents.
- [Conventional Commits](https://www.conventionalcommits.org/en/about/):
  the commit-type to bump-level mapping the gate implements.
- [Kubernetes deprecation policy](https://kubernetes.io/docs/reference/using-api/deprecation-policy/) and
  [Salesforce CLI deprecation policy](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_deprecation.html):
  deprecation-window norms behind Section 4.
