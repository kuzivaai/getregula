# Changelog

All notable changes to Regula are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Security
- **Closed the ancestor-directory race in `regula gap` / `conform`
  (compliance scoring), the last module holding it (#33).** The eight Article
  checkers read files by name after the walk, so an ancestor directory could
  be swapped for a symlink between the walk and the read, which `O_NOFOLLOW`
  cannot stop. Content is now read once during the walk through the `os.fwalk`
  descriptor into a per-scan, memory-bounded (64 MiB) cache the checkers
  consume. Scoring is byte-identical, verified by diffing full assessments on
  real projects before and after. Past the budget, reads fall back to the
  by-name guard, so a pathological multi-gigabyte tree bounds memory instead
  of holding it all. This closes the scan-safety class across every scanning
  command.
- **Closed three loopback SSRF bypasses in the timestamp URL guard.**
  `ipaddress.ip_address` accepts only canonical IPv4, so the guard refused
  `127.0.0.1` but accepted `2130706433`, `127.1` and `0x7f000001`, all of
  which `urlopen` resolves to loopback. The guard now parses the legacy forms
  with `socket.inet_aton`, the way the resolver does. Operator-set input only,
  so defence in depth, but a real bypass and now closed.
- **`regula inventory` reads through the shared guarded walk.** It used
  `rglob` plus a by-name read, leaving the ancestor race open; it now uses
  `walk_project_files`, which reads through the walk descriptor and enforces
  containment. No behaviour change (verified against the example projects).

## [1.7.8] - 2026-07-21

### Security
- **`regula handoff` hung indefinitely on a named pipe, read files outside
  the scan root, and walked into `.git`.** Four defects in one command, each
  reproduced before and after the fix. It used `rglob` — which follows
  symlinks, unlike `os.walk(followlinks=False)` — with a bare `read_text()`,
  and carried a private skip list holding 7 entries against the shared
  `SKIP_DIRS`' 28, omitting `.git` and `.env` among 21 others. A symlinked
  `.py` escaping the root was read and reported in the output. A fourth
  defect masked the other three: paths were reported relative to Regula's
  own installation directory rather than the scanned project, so every
  invocation naming a project outside the Regula checkout raised
  `ValueError` and exited before reaching the pipe. The command was missed
  by the previous sweep of "all 28 commands that accept a project path"
  because its path is its *second* positional (`handoff <tool> <project>`).
  All four are closed by reading through `scan_safety.walk_project_files`.
- **Ancestor-directory race closed in `cross_file_flow`,
  `ai_code_governance` and `guardrail_scanner`.** These collected paths
  during the walk and reopened them by name afterwards; between the two
  resolutions an ancestor directory can be swapped for a symlink, which
  `O_NOFOLLOW` cannot prevent because it guards only the final component.
  Content is now read inside the walk, through a descriptor held on the
  parent directory. `compliance_check` is deliberately excluded: its file
  index is consumed by eight Article checker functions across ten iteration
  sites, so reading content into it would hold the entire scanned project
  in memory (ceiling 578 files x 10.5 MB = 6.1 GB on this repository alone),
  trading a race the attacker must win for a memory exhaustion any large
  repository triggers. Closing it properly requires inverting control so a
  single walk feeds all eight checkers; tracked in #33.
- **Added a hostile-fixture sweep to the test suite**
  (`tests/test_hostile_sweep.py`). Runs every path-taking command as a
  subprocess against a tree containing a named pipe, a symlink escaping the
  scan root, a symlinked directory and a `.git` holding bait, asserting that
  no command hangs, crashes, reads out-of-root content, or walks a skipped
  directory. The command list is derived from the argument parser rather
  than hardcoded — a hardcoded list would have missed `handoff`, the one
  command carrying a real defect.
- **Dependency manifests were read from outside the scanned project
  (issue #32).** `scan_dependencies()` loaded all nine manifest types
  (`requirements.txt`, `pyproject.toml`, `package.json`, `Pipfile`,
  `Cargo.toml`, `CMakeLists.txt`, `vcpkg.json`, `go.mod`, `build.gradle`)
  with a bare `read_text()`, so a symlinked manifest pointing outside the
  scan root was followed and its packages reported in the output.
  Reproduced against both `regula deps` and `regula sbom` — the latter
  reaches the same function via `sbom.py`, so guarding sbom's own four
  walkers did not protect it, which is exactly the trap of applying a guard
  per-walker rather than at the read. All nine now read through
  `scan_safety.read_bytes_if_safe`. Verified by sweeping all 28 commands
  that accept a project path against an escaping-symlink fixture: no
  command leaks out-of-root content.
- **TOCTOU race between the path guard and the file read (issue #31).**
  `is_safe_to_scan` validated a *name*, and every caller then re-opened that
  name. An attacker with write access to a scanned tree could replace the
  approved file with a symlink between the two resolutions and have the
  scanner read a file the guard had rejected — defeating the symlink-escape
  protection entirely. New `scan_safety.open_if_safe` / `read_bytes_if_safe`
  resolve once and derive every decision from the descriptor: `O_NOFOLLOW`
  makes the kernel refuse the swapped symlink outright, `fstat` measures the
  file actually held so the size capped is the size read, and `S_ISREG`
  rejects non-regular files. `report.py` and `sbom.py`'s content-reading
  walkers now read through it. Residual gaps are documented in the module
  docstring rather than implied away: hardlink swaps are not prevented (they
  confer no privilege), and Windows lacks `O_NOFOLLOW` so it degrades to the
  name check plus `fstat`.
- **Denial of service via a named pipe in a scanned repository.** Found while
  testing the above: `open(fifo, O_RDONLY)` blocks until a writer appears,
  and the `S_ISREG` check runs only after `open()` returns. A single FIFO
  committed to a repository would hang a scan indefinitely. `O_NONBLOCK` is
  now set so the open returns and the file is rejected.
- **Audit store was world-readable.** `mkdir()` and `open(..., "a")` created
  the store 0755/0644 under a default umask. It records full tool inputs and
  responses — under the Claude Code hook that includes command output and
  file contents from the user's project — so every other local account could
  read it, on any shared workstation, build agent, or multi-tenant CI runner.
  Now created 0700/0600 atomically at creation (not by a later `chmod`, which
  would leave an exposure window), and stores created before this change are
  tightened on next use, including per-project chains under `projects/<slug>/`.
- **`regula doctor` asserted a check it never performed.** Its Security check
  reported "no world-readable policy files" while never inspecting a file
  mode. It now actually inspects the audit store and warns, naming the
  exposed paths.
- **Crash-reporting endpoint no longer shipped in published builds.** From
  `2c9829d` (10 Apr 2026) through v1.7.7, `scripts/telemetry.py` hardcoded a
  live Sentry DSN while `docs/TRUST.md` §8.2 stated published builds ship an
  empty one — verified by downloading `regula-ai==1.7.7` from PyPI and
  inspecting the shipped file. The DSN is now read from the
  `REGULA_SENTRY_DSN` environment variable and defaults to empty, restoring
  the documented behaviour. Reaching the endpoint always required the
  optional `sentry-sdk` extra **and** explicit opt-in, so default installs
  were never affected.
- **Stack-frame locals excluded from crash reports**
  (`include_local_variables=False`). sentry-sdk defaults this to `True`, and
  Regula's scan frames hold an entire scanned file in `content`, so an
  opted-in user's crash could have transmitted their source. The
  auto-detected hostname is now reported as `redacted`.
- **`REGULA_NO_TELEMETRY` now suppresses sending, not just the first-run
  prompt.** It was previously checked only when prompting, so a user who had
  consented once and later set the variable kept transmitting.
- **`DO_NOT_TRACK` is now honoured** (<https://consoledonottrack.com>),
  alongside `REGULA_NO_TELEMETRY` and `CI`. Values of `0`/`false`/`no`/empty
  are correctly treated as unset.
- **Path-safety guard extended to the AI-BOM walkers.** `scan_safety.py`
  centralises the symlink-escape and file-size checks that previously lived
  only in `report.py`; `sbom.py`'s four walkers now apply them, so a symlink
  inside a scanned repository can no longer pull an out-of-repo file's name,
  contents, or JSON keys into a generated BOM.

### Added
- **RFC 3161 TimeStampToken signature verification.** `regula verify` now
  verifies the PKCS#7 SignedData signature (RFC 5652 §5.4) over a
  timestamp token, checks that the signed attributes bind it to that exact
  TSTInfo, and requires the critical `id-kp-timeStamping` EKU (RFC 3161
  §2.3). Reports the strongest status actually proven — `HASH_MATCHED`,
  `SIGNATURE_VERIFIED`, or `CHAIN_VERIFIED` — and never a bare `VERIFIED`.
- **`--tsa-trust-anchor`** chains the signer certificate to a caller-supplied
  anchor, yielding `CHAIN_VERIFIED`. Documented as a LIMITED check: no
  revocation (CRL/OCSP), no name constraints, no intermediate chain
  building.

### Fixed
- **Unimplemented signature algorithms are no longer reported as tampering.**
  Algorithm-dispatch failures and genuine verification failures shared one
  error channel, so both surfaced as `INVALID`. A conforming TSA using
  Ed25519 (or any algorithm not implemented here) would have hard-failed a
  valid pack. Such tokens now degrade to `UNSUPPORTED` and retain the
  hash-only verdict, as `docs/spec/regula-evidence-format-v1.md` §4.6.3
  already required. Provably-bad signatures still return `INVALID`.
- **`regula doctor` telemetry check** now recognises an endpoint configured
  via `REGULA_SENTRY_DSN`, and its guidance points at the environment
  variable rather than editing `scripts/telemetry.py`.
- Removed dead code in `claim_auditor.py` that could raise `ValueError` on a
  genuine count mismatch, turning an actionable audit failure into a
  traceback. Removed an orphaned helper in `ast_analysis.py`.
- Corrected stale figures in `docs/TRUST.md`: the legacy runner's result
  (was `1373 passed, 4 skipped, 888 functions`; measured
  `1381 passed, 0 skipped, 942 functions`) and `regula doctor`'s expected
  split (was `9 passed, 3 info`; actual `8 passed, 4 info`). `README.md`
  also documented `regula telemetry --enable`, which is not a valid command.

### Changed
- German and Brazilian Portuguese pages gained the jurisdiction-scope notice
  and pattern-match caveat that the English pages already carried, and their
  navigation now links to the localised assessor rather than the English
  one. Translations reviewed and signed off by the maintainer.

## [1.7.7] - 2026-07-20

### Fixed
- **`regula dpv` failed on `pip install` (packaging).** The DPV vocabulary
  snapshot lived at repo-root `data/`, which is not included in the wheel, so
  `regula dpv` raised `FileNotFoundError` for every installed user (the 1.7.6
  release CI smoke-tested `self-test`/`demo` but not `dpv`). The snapshot moved
  to `scripts/dpv_data/dpv_aiact_terms.json` (packaged like `scripts/bias_data`)
  and is now declared in `[tool.setuptools.package-data]`. Verified by building
  the wheel, confirming the file is inside it, and running `regula dpv` in a
  clean-room install. The release workflow now also smoke-tests `regula dpv`.

## [1.7.6] - 2026-07-20

### Added
- **DPV-AIAct machine-readable export** (`regula dpv`, and
  `regula evidence-pack --dpv`). Emits the risk indication as JSON-LD tagged
  with concept IRIs from the **DPVCG EU-AIAct vocabulary** (the W3C Data
  Privacy Vocabularies and Controls Community Group's "EU-AIAct" extension,
  namespace `https://w3id.org/dpv/legal/eu/aiact#`), so RDF/GRC tooling can
  ingest a scan result without Regula. Risk tiers map to `RiskLevel*`
  concepts, Article 5 practices to `ProhibitedAISystem-A5-1-*`, and Annex III
  categories to `HighRiskAISystem-AnnexIII-*` / `-A6-1`. Honesty is enforced
  in code: the vocabulary is a W3C **Community Group report, not a ratified
  Standard** (the output says "aligned to", never "standard"); every emitted
  IRI is validated at load against a checked-in vocabulary snapshot
  (`scripts/dpv_data/dpv_aiact_terms.json`, 170 terms) so a fabricated IRI cannot ship;
  and genuine gaps are stated, not invented — Article 5(1)(i) (the Digital
  Omnibus CSAM/NCII prohibition, absent from the vocabulary) and non-EU
  findings (Korea AI Basic Act, Colorado SB 26-189) are reported as
  out-of-scope rather than forced into an EU concept. The evidence-pack
  artefact (`09-dpv-aiact.jsonld`) is off by default, keeping the manifest
  byte-identical to prior releases. Anti-drift tests pin the mapping to both
  the vocabulary snapshot and `scripts/risk_patterns.py`. Refresh the snapshot
  with `scripts/refresh_dpv_vocab.py`. This is risk indication, not
  classification.

### Changed
- **Homepage cognitive-load reduction (all locales):** the dense
  market-comparison section (3-card grid + 10-row table) is now progressive
  disclosure — a native `<details>` collapsed by default, reusing the existing
  translated heading as its summary (zero new prose; content stays in the DOM,
  SEO-safe; language-neutral `+`/`−` affordance). Grounded in the July 2026
  UX/IA research (NN/g cognitive load + scanning; move dense, non-decision
  content off the main scroll). Verified in-browser across EN/DE/PT-BR.
- **Documentation index (`docs/README.md`):** the tracked user-facing docs are
  now signposted by the four Diátaxis types (tutorials / how-to / reference /
  explanation), linked from the top-level README.
- **Accessibility (WCAG 2.2 AA):** `scroll-padding-top` on `html` so the sticky
  nav no longer obscures keyboard-focused or anchor-linked content
  (SC 2.4.11 Focus Not Obscured).
- Version is single-sourced from `scripts/constants.py` (R1): pyproject
  declares `dynamic = ["version"]` and reads the same attribute at
  build time; the release workflow's tag assertion reads it too. The
  two-place bump that produced a mis-versioned rehearsal wheel on
  16 July 2026 is no longer possible, and the source-of-truth test now
  fails if a literal version reappears in pyproject.
- Site metadata pass (18 Jul 2026): every page title ≤65 and meta
  description ≤165 rendered characters (trims on 3 region sources,
  4 guides, 2 blog posts, both PT-BR pages); pricing and sample-report
  gained Open Graph/Twitter cards and WebPage+Breadcrumb JSON-LD they
  lacked.
- Homepage motion choreography (shared CSS, all locales): revealed
  sections stagger their children's entrance and the hero plays a
  one-time load sequence. No copy changes; noscript/JS-failure
  behaviour unchanged (children are only animated after the existing
  reveal fires) and prefers-reduced-motion disables all of it.

### Governance
- Every `# regula-ignore` suppression in the codebase (27) now carries a
  same-line rationale; `regula check --audit-suppressions` reports zero
  "NO RATIONALE" rows on the repo itself (was 19). The self-scan
  transparency document is updated accordingly.

### Fixed
- `regula plan` task and footer deadline lines carry the adopted-Omnibus
  context again ("2 August 2026 (Omnibus: 2 December 2027 for Annex III,
  …; pending OJ publication)") instead of the bare baseline date. 1.7.5
  rendered the bare date because the contextual constant had no
  production consumer; both now derive from
  `omnibus.annex_iii_deadline_line()` and flip automatically at OJ
  publication.
- The `cv-screening-app` reference project declares
  `system.domain: employment` in its own `regula-policy.yaml`, so the
  documented evaluation journey reproduces under the v1.7.5 domain
  gating (with `--scope all` to include example-provenance findings).

### Security
- All GitHub Actions are pinned to full commit SHAs (with version
  comments); Dependabot maintains the pins. CodeQL analysis added for
  the Python source.

### Changed
- Dependency ranges refreshed: setuptools <84, cryptography <50,
  asn1crypto >=1.5.1, flask ~=3.1, weasyprint <70 (from the
  corresponding Dependabot proposals, applied together).

## [1.7.5] - 2026-07-16

Deep-audit remediation (8 July 2026), extended by the 10 July follow-up
audit. Full findings and evidence in the maintainer's audit report;
every fix below was verified by test.

### Fixed (16 July, morning)

- **Deliverables no longer embed the machine-wide audit trail**
  (client-confidentiality defect). Evidence packs, conformity packs,
  and HTML reports with `--include-audit` embedded every audit event
  on the machine — including tool inputs/outputs and secret-detection
  events from unrelated projects and other clients. All four surfaces
  now read exclusively from the scanned project's own audit chain via
  a single scoped collector (`log_event.collect_audit_trail`). Events
  are attributed to a project at write time (hooks use the session's
  working directory; CLI commands pass the project path) and stored in
  per-project chains under `~/.regula/audit/projects/<slug>/`.
  Machine-wide events recorded by earlier versions stay on the machine
  and are never embedded in deliverables. `05-audit-trail.json` gains
  `scope`, `project`, `project_slug`, `limit_reached`, and `scope_note`
  fields alongside the existing keys (additive).
  **Action for existing users**: any evidence pack, conformity pack, or
  `--include-audit` report generated with v1.7.4 or earlier may contain
  audit events from other projects on the machine that generated it
  (including tool inputs/outputs). Regenerate such artefacts with the
  fixed version before sharing them, and review anything already shared
  from a machine used for more than one project.
- **Audit-chain verification no longer fails structurally at month
  boundaries.** The writer seeded each new monthly log file with the
  genesis hash while `verify_chain` required cross-file continuity, so
  `chain_valid` was false on any store spanning two or more months —
  in both the audit trail and the runtime monitor. New events now
  continue the chain across monthly rotation; verification tolerates
  and *reports* pre-fix genesis seeds at file boundaries as "legacy
  restarts" instead of failing, and still fails on tampering or any
  non-genesis mismatch.
- **Reading an absent audit chain no longer creates store directories.**
  `get_audit_dir` unconditionally created directories, so every query or
  verification against a project with no chain left an empty
  `projects/<slug>/` directory in the operator's real store (27 were
  found there after the first scoped test runs). Read paths now pass
  `create=False`; an absent chain reads as an empty valid chain. A new
  suite-wide `tests/conftest.py` fixture also isolates
  `REGULA_AUDIT_DIR` for every test, so the test suite can no longer
  write to (or read from) the operator's real store. The custom runner
  (`tests/test_classification.py`, which pytest fixtures cannot cover)
  gets the same guarantee via process-level isolation in its `__main__`
  block, and `test_audit_hash_chain` now restores the prior
  `REGULA_AUDIT_DIR` instead of popping it (the pop silently disabled
  isolation for every test that ran after it). Verified live: a full
  custom-runner pass leaves the real store byte-identical.
- **Secret values are redacted from audit payloads before they are
  persisted.** The pre-tool hook only blocks HIGH-confidence secret
  findings; medium/low-confidence values executed and were logged
  verbatim into `tool_input`/`tool_response` — and the audit trail is
  embedded in client-facing deliverables. New
  `credential_check.redact_secrets()` replaces every known secret
  pattern with `[REDACTED:<pattern>]`; hooks redact before truncating
  (truncation could split a value so the pattern no longer matches
  while most of the secret survives).

### Added (16 July, morning)

- **`--project` on `regula audit query/export/verify`** — scope the
  audit CLI to one project's chain. Default remains the whole machine
  (machine store plus every project chain, merged by timestamp).
- **Walking conformance guard for the audit-scoping class**
  (`tests/test_audit_surface_conformance.py`) — discovers every
  `query_events`/`log_event` call site and every pack-writing module by
  walking `scripts/` and `hooks/` (never a hardcoded file list), and
  fails if a deliverable surface bypasses `collect_audit_trail`, a hook
  drops project attribution, a read path creates store directories, or
  a secret value survives into a logged payload. Verified to fail on a
  re-injection of the original defect (3 targeted failures) and pass on
  the fixed tree.

### Fixed (16 July, morning — walkthrough P2–P6 + deadline single-sourcing)

- **`system.domain` in regula-policy.yaml now actually activates
  domain-gated patterns** — doctor and the consultant guide documented
  the syntax, but only the `--domain` flag activated anything (the
  policy declaration fed the confidence-boost path only). Activation
  now happens inside `scan_files` itself, reading the TARGET project's
  policy file, so check, report, gap, evidence packs, conformity packs,
  and init all agree on what is active for a given project — including
  when scanning a directory other than the CWD.
- **`regula init` no longer writes hooks without consent (P4)**:
  non-interactive runs print the manual `regula install <platform>`
  command instead of silently writing `.claude/settings.local.json`;
  an unanswerable prompt (piped stdin, CI) counts as a decline, not a
  yes.
- **`regula init`'s scan can no longer contradict `regula check`
  (P5)**: the quick scan uses the same domain activation, reports
  domain-gated potential findings explicitly, and its "AI files" label
  (which read as an authoritative zero) is now "Files with findings".
- **Verdict copy is indication-framed (P2)**: `regula check` no longer
  prints "is classified as high-risk … you must comply" — findings are
  indicators; Article 6 classification depends on context. New copy:
  "shows indicators of high-risk AI … If confirmed high-risk
  (Article 6), Articles 9-15 obligations apply."
- **Fresh unsigned evidence packs verify cleanly (P6)**: unsigned
  manifests now carry the Evidence Format v1 declaration the spec lists
  as REQUIRED (plus `project_directory`), so `regula verify` no longer
  hedges "v0 best-effort semantics" on packs Regula itself just
  generated. Versioned via the `format_version` field; the v0 path
  remains for packs from older releases.
- **Every deadline-copy consumer now derives from `omnibus.py` (P3,
  closes audit finding H8)**: remediation plan, exec summary, assess,
  explain, explain-articles, register packets, and the roadmap default
  all single-source the binding deadline, so the OJ flip is one line
  plus the enumerated site sweep. `test_omnibus_status.py` asserts the
  wiring pre- and post-flip and guards against new hardcoded
  binding-deadline literals in scripts/. Stale "provisional agreement /
  may defer / if Omnibus passes" phrasing corrected to the adopted
  state (EP 16 Jun, Council 29 Jun 2026; pending OJ publication) in
  assess, explain, explain-articles, registration packet status
  values, and references data.
- **Homepage version badge said v1.7.3 in all three locales** (stale
  since the 1.7.4 release); corrected, and `site_integrity.py` gains a
  `version` check comparing the badges against
  `scripts/constants.py::VERSION` so the badge can never silently lag
  a release again.

### Fixed (16 July, morning — site)

- **Residual Brazil legal error**: the page tracker's "Entry into
  force" row still asserted "1 year after publication per Art. 45" —
  the 16 July vacatio correction fixed the body, FAQ, and gaps
  sections but missed this row. Now states the verified 730/180-day
  phasing (Senado Notícias, 10 Dec 2024).
- **Brazil and South Africa pages converted to generator sources
  (DQ-7)**: `content/regulations/{brazil,south-africa}.py` now drive
  the pages through the builder and drift guard; content carried
  verbatim (parser-verified) apart from the tracker fix above, stale
  "Last updated" dates refreshed to 16 July, two stray "Guides" link
  artifacts removed per page, and SA card headings h4→h3 (WCAG
  heading hierarchy). `uae.html` formally exempted: it is a conversion
  landing page, not a tracker — forcing it through the tracker schema
  would destroy it. Builder gains optional per-page extension fields
  (head_extra, tracker_html, jsonld_article_override, body_end_html,
  structured-data-only FAQ entries); shared region-page component
  styles promoted from per-page `<style>` blocks into site.css (also
  fixes previously unstyled `<pre>` blocks on the Colorado/Korea/UK
  pages).
- **False licence claim on region pages**: the region-page template's
  footer said "MIT licence"; the project is Apache 2.0 / EUPL 1.2
  (pyproject.toml). Template corrected; Colorado and UK pages
  regenerated. The template also gained the current site chrome
  (mobile nav, Assess/Guides/About links, Plausible analytics — which
  Colorado and UK pages previously lacked entirely) and the site-wide
  disclaimer wording.
- **Korea page reconciled with its generator source (DQ-6)**: shipped
  content ported into `content/regulations/south-korea.py` and the
  page rebuilt through the pipeline — zero visible-content change,
  drift-guard KNOWN_DRIFT entry removed. The page's meta description
  now matches the verified on-page claims (the old one referenced
  "PIPC enforcement", which the page never substantiated).

### Added (16 July)

- **Consultant engagement metadata** — client-facing deliverables can
  now carry engagement context (client, preparer, engagement
  reference). Configure once per client project via the `engagement:`
  section of `regula-policy.yaml`, or per run with `--client`,
  `--prepared-by`, `--engagement-ref` on `regula report` and
  `regula evidence-pack`. The executive summary renders the fields in
  its header; the evidence-pack manifest records them inside the
  signed content (optional block, spec §4.3 — unsigned manifests stay
  byte-compatible when unconfigured). New `scripts/engagement.py` is
  the single source of truth; 18 tests in `tests/test_engagement.py`.
- **Consultant workflow guide** (`docs/consultant-guide.md`) —
  engagement methodology from scoping through signed evidence pack,
  including honest-positioning guidance and jurisdiction selection.
- **Jurisdiction aliases `kr`/`co`** on `regula check --jurisdictions`
  and `regula assess --jurisdiction`, matching the web assess tool's
  `?j=kr`/`?j=co` codes so both surfaces share one vocabulary.
- **Multi-jurisdiction card on the homepage** (EN/DE/PT-BR) — the
  Korea + Colorado coverage shipped earlier was absent from the main
  marketing surface.

### Fixed (16 July)

- **Colorado SB 26-189 characterisation corrected across every surface** —
  "disclosure-only" overstated the law's narrowness: the signed act also
  grants consumers correction and meaningful human-review rights
  (§ 6-1-1705) and imposes 3-year record retention on developers and
  deployers (§§ 6-1-1702(4), 6-1-1703). Reworded to "disclosure-focused"
  with the rights named, in README, homepage cards (EN/DE/PT-BR),
  llms.txt, consultant guide, regulations index, framework crosswalk,
  CLI/framework-mapper fallback strings, and the regenerated Colorado
  region page. Verified against the signed act text
  (leg.colorado.gov/bill_files/116489/download).
- **Region-page builder wrote to the repo root** — `build_regulations.py`
  was never updated for the site/ IA restructure: output landed at the
  repo root and generated canonicals/og:url/JSON-LD pointed at
  pre-restructure URLs, so the shipped Colorado page had drifted from its
  generator source (which still described repealed SB 24-205 duties as
  live law). Builder now writes to `site/regions/`, emits `/regions/`
  URLs, and `content/regulations/colorado.py` was rewritten for the
  SB 26-189 world with §-level citations and the xAI v. Weiser
  litigation watch note.
- Colorado jurisdiction YAML precision: AG-rulemaking citation now points
  at the mandatory-rules provisions (§ 6-1-1705(3)) rather than the
  discretionary § 6-1-1706(5) power alone; the $20,000 penalty is
  attributed to the CCPA (C.R.S. § 6-1-112); record retention cites both
  § 6-1-1702(4) (developer) and § 6-1-1703 (deployer).
- Homepage hero sub-line (EN/DE/PT-BR) no longer implies EU-only
  coverage — it names the South Korea and Colorado mappings the scan
  already performs.
- `site/llms.txt` taught `--jurisdictions kr` before `kr` existed as an
  alias; now documents the canonical names and aliases.
- Removed dead `--jurisdictions` options `canada`, `singapore`, `oecd`:
  they carried no crosswalk or domain data and produced a misleading
  "has article-level crosswalk mapping" note. Canada's AIDA (Bill
  C-27) died on prorogation on 6 January 2025 (verified against
  LEGISinfo) with no successor bill.
- Executive summary now HTML-escapes project names, finding fields,
  and engagement values (scanned repositories are third-party input).

### Added (10 July)

- **Positional project path on 20 more subcommands** — `regula conform
  --sign .`, `regula oversight .`, `regula discover .`, `regula
  guardrails .`, `regula sbom --ai-bom .`, `regula report . -f html`
  and every other `--project` subcommand now accept the natural
  positional form the docs and site teach (the 8 July fix covered six
  commands; this closes the whole class — `install` and `baseline`
  keep their existing positional arguments).

### Fixed (10 July)

- **`regula report --domain` / `--scope`** — `report` on a domain-gated
  project silently produced zero findings because there was no way to
  declare the domain; both flags now work exactly like `regula check`'s.
  `--scope` defaults to `all` (reports are a full inventory), so
  existing report output is unchanged.
- **Evidence/conformity pack files are byte-stable on Windows** — pack
  writers now pin `newline="\n"`, so the SHA-256 hashes recorded in the
  manifest match the on-disk bytes on every platform. Previously
  `regula verify` reported every file MODIFIED for packs generated on
  Windows.
- **`regula evidence-pack --sign --timestamp`** prints an actionable
  error (exit 2) when the TSA is unreachable or the key is invalid,
  matching `regula conform`, instead of a raw traceback.
- **Atomic AI-system registry writes** — parallel `regula discover
  --register` runs can no longer corrupt the registry JSON
  (temp file + `os.replace`).

### Added

- **`regula evidence-pack --sign` / `--signing-key` / `--timestamp` /
  `--tsa-url`** — the natural form taught by earlier docs now works,
  with the same semantics as `regula conform` (both flags imply
  `--sign`; `--timestamp` adds an RFC 3161 token). A signed evidence
  pack declares Evidence Format v1.1 (`format`, `format_version`,
  `schema_uri`, `hash_algorithm`) so `regula verify` accepts it and
  verifies the Ed25519 signature; the legacy `schema_version` field is
  kept, and the UNSIGNED manifest encoding is byte-compatible with
  previous releases. The sign→timestamp sequence is now a single shared
  implementation (`signing.apply_manifest_security`) used by both
  `conform` and `evidence-pack`.

### Site

- **Sample-report bridge page** (`/sample-report.html`): real, verbatim
  output from scanning the bundled CV-screening example — terminal
  verdict, full HTML report, and executive summary — so non-CLI
  visitors can see the product before installing (UX-audit High
  finding: the non-developer journey previously dead-ended at a CLI
  referral). Provenance and reproduction command stated on the page;
  one hostname scrubbed, everything else verbatim.
- **LCP**: `fetchpriority="high"` on the font preloads sitewide
  (web.dev-recommended dual preload + priority for text-LCP pages;
  supported by all major browsers).
- **CSS pipeline**: pages now load `site.min.css`/`fonts.min.css`
  (~30% smaller), generated by `scripts/minify_css.py` from the
  readable sources; an enforcement test fails CI if the minified files
  drift from `minify(source)`.
- **Assess funnel instrumented** (5 events, EN/DE/PT-BR): jurisdiction
  selection, per-question progress, result exports (print/share/JSON),
  and click-to-copy on the CLI commands shown in results. NOTE:
  matching goals must be created in the Plausible dashboard before the
  events appear.

### Fixed (scan cache)

- **Scan-cache entries are now context-safe.** Three defects fixed in
  one schema bump (v3→v4, old entries invalidated): `--min-tier` scans
  wrote incomplete per-file entries that later full scans consumed
  (silent under-reporting); domain-gated files were never cached (the
  gated finding is now stored ungated and re-gated at read time, so a
  later `--domain` scan finds it on a cache hit); and entries embedded
  the AI-library self-scan confidence cap under a context-free key
  (keys now carry an app/lib context token).

### Security

- **GitHub Actions script injection fixed** in the issue-triage workflow:
  issue title/body now reach the script only via environment variables. A
  crafted issue title could previously execute shell in a step holding
  repository secrets.
- **`regula verify` path traversal fixed**: manifest filenames that are
  absolute or contain `..` are rejected (`INVALID_PATH`) instead of being
  read from outside the pack directory; symlink escapes are also blocked
  and special files are refused. The bundled standalone verifier now
  rejects absolute paths too.
- **Zip decompression-bomb guard** on `regula verify <pack>.zip`:
  bundles declaring more than 500 MB uncompressed or 10,000 members are
  refused before extraction (limits defined in `scripts/cli_evidence.py`,
  `_MAX_EXTRACT_BYTES` / `_MAX_EXTRACT_MEMBERS`).
- **Ed25519 signing key hardening**: the private key file is now created
  `0600` atomically (`O_CREAT|O_EXCL`); a permissions failure aborts key
  generation instead of warning and continuing; the key directory is
  created `0700`.
- **BREAKING: API server no longer sends `Access-Control-Allow-Origin: *`.**
  The server has no authentication, so wildcard CORS let any website a
  developer visited read local scan results via requests to localhost.
  Browser access is now opt-in: set `REGULA_API_ALLOW_ORIGIN` to an
  explicit origin (a literal `*` is refused). Non-browser clients (curl,
  CI) are unaffected.
- Least-privilege `permissions: contents: read` added to the CI,
  benchmark, release, and test-action workflows.

### Fixed

- **`fail-on-prohibited` in the GitHub Action now actually works.**
  `regula check --format sarif --output FILE` previously never wrote the
  file (only HTML honoured `--output`), so the action's fallback
  overwrote real results with an empty, schema-invalid SARIF stub —
  the gate always counted zero findings, and the invalid stub broke
  SARIF upload. `--output` now writes SARIF, the fallback no longer
  destroys real output, and the last-resort stub is valid SARIF 2.1.0.
- **`regula-ignore` / `regula-accept` now work in all scanned languages.**
  The annotation parser only recognised `#` comments, so suppressions
  were silently dead in JS/TS/Java/Go/Rust/C/C++ — 7 of the 8 languages
  Regula scans. `//`, `/*` and `*` comment leaders are now recognised.
- **`regula gap|plan|roadmap|docs|evidence-pack|disclose` accept a
  positional path** (`regula gap .`), matching `regula check` and every
  published quickstart — these commands previously exited 2 on the
  documented form.
- **`regula docs` default output** now resolves against the project
  directory, not the current working directory, so invocations from
  another directory no longer drop generated files into it.
- `regula gap` no longer counts Regula-generated draft scaffolds or
  hidden tool directories as compliance evidence, and its output states
  that the score measures documentation presence, not code risk.
- **Remaining "zero false positives at BLOCK tier" claims removed**
  (site index EN/DE/PT-BR, UAE page, model card, governance doc, and the
  `regula exec-summary` template). The 8 July audit removed one instance;
  these parallel copies survived. The underlying figure was a 0-findings
  cell presented as 100% precision; a correction note now scopes it in
  the April 2026 benchmark report.
- **robots.txt no longer blocks the legacy redirect stubs** — a
  robots.txt Disallow stopped crawlers from ever seeing the stubs'
  noindex/canonical signals, stranding the old URLs in search indexes
  instead of consolidating them.
- **schema.org `softwareVersion` corrected to the released version** on
  the site index, UAE page, and both locale pages (still 1.7.3 after the
  1.7.4 release); an enforcement test now pins every site
  `softwareVersion` to `scripts/constants.py` VERSION.
- **`regula evidence-pack --sign` was taught but never existed** — the
  `--sign` flag belongs to `regula conform`. The homepage copy-pill
  (EN/DE/PT-BR), the pricing page, llms-full.txt, and the CLI's own
  evidence-pack hint all taught the broken form; every instance now
  shows `regula conform --sign .` (verified end-to-end: Ed25519
  signature embedded and `regula verify` passes).
- **Evidence-pack pricing page is now linked and indexable**
  (`/pricing.html`): noindex removed, added to the sitemap, linked from
  the homepage evidence-pack card and the EN/DE/PT-BR footers. Copy
  unchanged and explicit that paid tiers are not yet purchasable.
- **Claim auditor now verifies precision figures** (`--verify-facts`):
  every "N% … precision" claim in published copy must be derivable from
  the benchmark artifacts (`benchmarks/results/*/PRECISION.json`,
  `benchmarks/labels.json`) — fabricated or drifted precision numbers
  fail CI.

### Changed

- Digital Omnibus enactment status now derives from a single module
  (`scripts/omnibus.py`) across every command that prints deadline copy;
  a regression test simulates OJ publication and verifies all consumers
  flip. Scanner skip-directory lists and the JSON output envelope were
  likewise consolidated to single sources of truth with enforcement
  tests.
- **BREAKING: `regula assess --format json` now emits the standard JSON
  envelope** (`format_version`, `regula_version`, `command`, `timestamp`,
  `exit_code`, `data`) used by every other `--format json` command. It
  previously printed a bare `{tier, non_eu_provider, answers}` object with
  no version marker. Consumers should read the old fields under `data`;
  the presence of `format_version` distinguishes new output from old.

## [1.7.4] — 2026-07-06

Regulatory-status correction and release-pipeline hardening. Updates the
Digital Omnibus adoption status in CLI output and jurisdiction metadata to
reflect the Council's approval on 29 June 2026, and ships the first release
published via PyPI trusted publishing (OIDC) rather than a manual token
upload.

### Changed

- **Digital Omnibus status copy** in `regula assess` and `regula timeline`
  output, and in the EU AI Act jurisdiction metadata
  (`references/jurisdictions/eu_ai_act.yaml`), now states that the Council
  approved the Omnibus on 29 June 2026 (previously "pending Council
  adoption"). Deadlines are unchanged — Annex III remains 2 December 2027,
  Annex I remains 2 August 2028; only the adoption-status wording is
  updated. `OMNIBUS_OJ_DATE` stays unset pending Official Journal
  publication, so the original 2 August 2026 deadline remains the legally
  binding baseline until then.

### Release process

- First release published through GitHub Actions with PyPI **trusted
  publishing** (OIDC, no stored API token). Distributions carry PEP 740
  provenance attestations.

## [1.7.3] — 2026-07-02

Multi-jurisdiction expansion, security hardening, and demo fix. Adds
South Korea and Colorado alongside the EU AI Act. Fixes `regula register`
crash, eliminates ReDoS vulnerabilities, redacts secrets from output,
hardens the MCP server against SSRF, and fixes `regula demo` so it
correctly shows HIGH-RISK for the bundled hiring-system example.

### Added

- **Multi-jurisdiction support** — pattern-based risk indication now covers
  3 jurisdictions: EU AI Act (Regulation (EU) 2024/1689), South Korea AI
  Basic Act (Act No. 20676, in force 22 January 2026), and Colorado
  SB 26-189 (disclosure-only, effective 1 January 2027).
- **`scripts/regulation_map.py`** — new module mapping jurisdictions to
  their regulation configs, risk patterns, and questionnaire flows.
- **3 jurisdiction YAML configs** (`references/jurisdictions/eu_ai_act.yaml`,
  `south_korea.yaml`, `colorado.yaml`) — each defines the jurisdiction's
  risk tiers, article references, and obligation mappings.
- **`--jurisdictions` flag on `regula check`** — comma-separated list
  (e.g. `--jurisdictions eu,korea,colorado`) applies all relevant
  framework mappings simultaneously.
- **`--jurisdiction` flag on `regula assess`** — selects the jurisdiction
  questionnaire (`eu`, `korea`, or `colorado`).
- **Domain detection** (`detect_domains` in `classify_risk.py`) — identifies
  housing, transportation, and other domain contexts for jurisdiction-
  specific risk mapping.
- **Web assess jurisdiction selector** — Korea (9 questions) and Colorado
  (8 questions) questionnaires available via the web tool at
  `https://getregula.com/assess/?j=kr` and `?j=co`.
- **New housing and transportation detection patterns** — Housing
  (Colorado SB 26-189) and Transportation (Korea AI Basic Act Art 33)
  risk categories added to `risk_patterns.py`.
- **Emotion inference pattern split** — separated for correct domain
  mapping across jurisdictions (EU workplace restriction vs Korea/Colorado
  broader scope).
- **33 new multi-jurisdiction tests** covering jurisdiction loading,
  domain detection, regulation mapping, questionnaire flows, and
  path traversal protection.

### Fixed

- **`regula demo` verdict** — the bundled cv-screening-app was showing
  "NO AI DETECTED" because employment patterns are domain-gated and the
  examples/ directory was excluded by `--scope production`. Demo now
  declares `--domain employment` and `--scope all` so the HIGH-RISK
  verdict appears correctly. Normal scans are unaffected.
- **YAML fallback parser** enhanced for flow mappings (`{key: value}`)
  used in jurisdiction config files.
- **Path traversal protection** on jurisdiction loading — prevents
  loading configs from outside `references/jurisdictions/`.
- **Packaging: `regula register` crash on pip-install** — `references/annex_viii_sections.json`
  was missing from package-data; added `*.json` glob to `pyproject.toml`.
- **ReDoS in `rag_poisoning` and `no_grounding` patterns** — negative lookahead inside
  quantified groups caused catastrophic backtracking; rewritten to bounded lookaheads.
- **Secret values leaked in finding descriptions** — `scan_config_files()` embedded
  first 40 chars of matched secrets in output; now redacted to type + char count.
- **`strip_comments()` escape handling** — backslash-escaped quotes (`\"`, `\'`) were
  mishandled, causing false negatives and false positives in Python classification.
- **Malformed policy file silently ignored** — `_load_policy()` now surfaces a clear
  WARNING to stderr and exposes the error via `get_policy_parse_error()`.
- **MCP path denylist bypass** — exact-match check replaced with prefix blocking via
  `Path.is_relative_to()`; `/proc`, `/sys`, `/dev`, `/boot` added to blocklist.
- **SSRF via `REGULA_TSA_URL`** — `_require_http_url()` now rejects private/internal IPs
  (loopback, RFC 1918, link-local, AWS metadata).
- **SSRF via `--repos` git clone** — `_validate_clone_url()` rejects non-https schemes.

### Changed

- **WCAG accessibility fixes** — contrast improvements, `focus-visible`
  rules, and `aria-pressed` attributes on jurisdiction selector buttons
  in the web assess tool.

## [1.7.2] — 2026-06-15

Precision engineering release. Regex bug fixes, AST context gating,
and smarter filtering reduce false positives on application code.
Documentation audit brings all counts and claims up to date.
MCP Registry namespace tag updated for official registry compatibility.

### Added

- **Runtime monitoring SDK** (`scripts/monitor.py`): `MonitorSession`
  and `Trace` for Article 12 runtime logging of LLM calls.
  Hash-chained JSONL storage, tiered schema (auto/session/per-event),
  duck-typed response extraction for OpenAI, Anthropic, and raw dicts.
- **CLI: `regula monitor status|report|verify|prune|export`**
  subcommands (`scripts/cli_monitor.py`).
- **Evidence pack: `--runtime <system_id>`** flag includes runtime
  logs in section 08 (`08-runtime-monitor.json`).
- **24 new tests** for monitor module (`tests/test_monitor.py`).
- **AST context gating** (`scripts/ast_context.py`). Builds a
  line-level context map (try/except, docstrings, test assertions) to
  suppress findings in non-production code paths.
- **Application-code benchmark** (`benchmarks/results/app_*.json`).
  13-project benchmark measuring precision on real AI applications
  (not library source code).
- **Import-based AIBOM fallback.** When no manifest (requirements.txt)
  is found, scans source imports to build the AI bill of materials.

### Fixed

- **9 regex precision bugs**: broken lookahead, pickle word boundary,
  torch exclusion, temperature range overmatch, path indicator
  conflation, AI term conflation with non-AI usage, `performance_scor`
  partial match, `rag_poisoning` overreach, `no_grounding` false
  positives.
- **`resume` → `resumes?`** in employment patterns: requires plural or
  compound form (`classify_resume`, `score_resumes`) to avoid collision
  with ML "resume training".
- **`response.content`** no longer triggers AI output detection (too
  generic — matches HTTP responses). Now requires LLM-specific
  structures.
- **`send_message`** removed from agent communication pattern (collides
  with LLM client methods).
- **Multi-segment SDK chains** (`client.chat.completions.create`) now
  detected correctly.
- **CI directories** (`.github`, `.gitlab`, `.circleci`) added to
  SKIP_DIRS.
- **`docs/conf.py`** classified as documentation, not production code.
- **Generic minimal_risk findings** suppressed (reduces noise without
  losing signal).
- **Library infrastructure penalty** reduces score for patterns found
  in library internals.

### Changed

- Landing page precision disclosure rewritten: leads with "0 false
  positives at BLOCK tier", contextualises INFO-tier 15.2% as measured
  on AI library source code (hardest corpus).
- README, site_facts counts updated (55→60 commands, 1055→1223 tests).
- Documentation audit: architecture.md, cli-reference.md,
  evidence-pack-guide.md, CONTRIBUTING.md all reconciled with current
  codebase state.
- **MCP Registry namespace**: `<!-- mcp-name: regula -->` →
  `<!-- mcp-name: io.github.kuzivaai/regula -->` for Official MCP
  Registry compatibility (PyPI ownership verification).
- **File-path exclusion layer** (`classify_provenance` +
  `_should_exclude_for_production_scope`): `--scope production` is now
  the default for `regula check`. Excludes test files, type stubs,
  utility plumbing, and examples from non-minimal tiers.

## [1.7.1] — 2026-05-02

Market readiness release. Landing page rewritten with questionnaire
framing, competitive comparison table, and auditor persona card. Blog
content: 5 articles published (Article 5 prohibited practices, Omnibus
decision framework, Omnibus delay, Omnibus trilogue failure, 5 AI
frameworks scanned). Regulatory accuracy: Omnibus trilogue failure
tracked, pattern count consolidated to 389 (later 398 in v1.7.2).
VS Code extension prepared. Pre-commit hook added. IndexNow support.
REST API, web dashboard, and Trust Center added. Precision confirmed
at 83.5% on random corpus. Domain gating for opt-in high-risk
categories. 55 commits.

## [1.7.0] — 2026-04-16

Evidence Format **v1.1** — tamper-evident conformity packs. Optional
`regula[signing]` extra adds Ed25519 manifest signing and RFC 3161
trusted timestamping; `regula verify` validates both. Plus regulatory
accuracy fixes (EP Omnibus vote date corrected), packaging fixes
(`regula[all]` now actually bundles signing support — 1.6.2 silently
dropped it), supply-chain-security improvements (dependency pinning
score raised), and the CLI UX polish and doc rewrite that makes pipx
install the first-class path.

### Added — Evidence Format v1.1

- **Ed25519 manifest signing.** `regula conform --sign` produces an
  `evidence.json.sig` alongside the canonical manifest, using
  PKCS8-serialised private keys at `~/.regula/signing.key` (chmod 600
  on POSIX). Canonical form documented in
  `docs/spec/regula-evidence-format-v1.md` §4.5. Key export via
  `regula verify --export-public-key`.
- **RFC 3161 trusted timestamping.** `regula conform --timestamp`
  requests a TSA token (default: FreeTSA.org) over the canonical
  manifest digest and embeds the token in the pack. `regula verify`
  validates the token's `messageImprint` against the pack's canonical
  digest.
- **`regula verify` extended.** Produces a signer-verified and
  timestamp-verified exit status. Signer-chain validation for the TSA
  is deliberately out of scope in v1.1 — documented in spec §4.6.4.
  Consumers with higher trust bars can run the raw token through
  `openssl ts -verify`.
- **Optional `[signing]` extra**: `pipx install "regula-ai[signing]"`
  adds `cryptography` and `asn1crypto`. Zero-dep core unchanged.
- **Specification bundled** at `docs/spec/regula-evidence-format-v1.md`
  + JSON schema at `docs/spec/regula.manifest.v1.schema.json`.
- **Tests**: round-trip and tamper-detection suites in
  `tests/test_signing.py` and `tests/test_manifest_timestamp.py`.

### Added — other

- **EUPL-1.2 dual-licence** alongside MIT. The EUPL route is aimed at
  European public-sector procurement, where EUPL-1.2 is the preferred
  open-source licence for Commission, national-government, and EU-agency
  procurement.
- **CSP-readiness comments** on inline `onload` handlers in
  `site/index.html` and locales, documenting inline-script dependencies
  for future Content Security Policy hardening.

### Changed

- **`regula[all]` now bundles `[signing]`.** In 1.6.2, the `[all]`
  extra silently omitted Ed25519 / RFC 3161 support. Users running
  `pipx install "regula-ai[all]"` did not actually get the signing
  features. Fixed in `pyproject.toml`.
- **User-facing docs use `regula` (not `python3 scripts/cli.py`).**
  Pipx users don't have a `scripts/` directory, so doc instructions
  showing `python3 scripts/cli.py …` literally failed on copy-paste.
  README, examples, CLI help, first-run wizard, quickstart, and
  `docs/cli-reference.md` now use the installed `regula` command.
  Maintainer-only docs (`.claude/skills/regula/SKILL.md`) retain the
  dev-time invocation.
- **Dependency-scan classifier** distinguishes bounded-range from
  unbounded-range pins. Optional-dependency pinning score raised from
  61/100 to 79/100. See `scripts/dependency_scan.py`.
- **CLI help, error messages, and first-run onboarding** polished.
  Copy tested against pipx + uvx + plain-pip install flows.
- **`examples/cv-screening-app/`** expanded into a 10-minute evaluation
  walkthrough that covers v1.1 signing + timestamping end-to-end.

### Fixed

- **Claim-auditor false positive on markdown section-number headings.**
  `### 4.2 File record schema` was misread as a "4.2 files" numeric
  claim, blocking CI on clean commits. Section-number prefixes now
  exempted via the existing structural-reference mechanism.
- **EP plenary vote date** on the EU Digital Omnibus: **23 March →
  26 March 2026**. Tally added: **569-45-23** (missing the 23
  abstentions). Trilogue launched 26 March; Cypriot Presidency
  political-agreement target 28 April 2026 (may slip).
- **Competitor facts**: AIR Blackbox **39 → 48 checks**; Microsoft
  Agent Governance Toolkit release date corrected.
- **Numeric-claim reconciliation**. Every numeric claim in user-facing
  docs and landing pages reconciled to `scripts/site_facts.py` output.
  Test counts to canonical 1,000 (`pytest --collect-only`); framework
  counts to canonical 17 (`references/framework_crosswalk.yaml`).
- **Exception handling**: narrower `except` clauses, removed unreachable
  branches, removed unused imports. Addresses code-review items
  H1-H6, M2, M3, L2, N2.
- **South Africa AI tracker 404** on `sa-tracker.json`.
- **Landing-page cold-load FOUC** (white flash) fix applied site-wide.
- **`test_env_regula_strict`** no longer relies on a self-scan false
  positive.

### Accessibility

- **WCAG 2.2 AA.** 14 pages (English, German, Portuguese, region
  trackers, blog posts, spec pages) pass axe-core automated audit.
  Screen-reader audit pending manual NVDA / VoiceOver / TalkBack
  testing.

### Security

- Signing keys written with `chmod 600` on POSIX
  (`~/.regula/signing.key`). Key rotation is not yet supported in v1.1.
  Documentation warns users to back up and not commit the key — see
  `docs/spec/regula-evidence-format-v1.md` §4.5.4 and
  `examples/cv-screening-app/README.md` step 5.

## [1.6.2] — 2026-04-16

First PyPI release since 1.6.0 (9 April 2026). 1.6.1 was tagged locally
but never published to PyPI, so users installing via `pipx install
regula-ai` were stuck on 1.6.0 through 122 subsequent commits. This
release bundles everything merged since: the distribution-readiness
work (two new CLI commands — `handoff` and `regwatch`, open regulatory
data assets, integrity tooling), plus the subsequent fixes — repo IA
restructure (`site/`, `docs/`, `configs/`), runnable examples directory,
installation path rewrite to pipx-primary, LIMITED-RISK rendering fix,
Python 3.10/3.11 f-string compatibility, and the landing-page cold-load
FOUC fix. Command count is now **53** (verified via `regula --help-all`;
`regula -h` shows 6 primary commands via progressive disclosure). No
breaking changes for existing `regula check` / `regula plan` / `regula gap`
users. All 941 tests still pass.

### Added — runnable examples and CI plumbing

- **`examples/`** — three runnable fixtures, one per EU AI Act risk tier,
  each with a README documenting verified `regula check` output:
  - `examples/cv-screening-app/` — high-risk employment pattern (Annex III
    Category 5); expect one WARN finding flagging automated hiring.
  - `examples/customer-chatbot/` — Article 50 limited-risk AI chatbot
    interaction; expect one LIMITED-RISK finding after the rendering fix.
  - `examples/code-completion-tool/` — minimal-risk code completion;
    expect zero findings.
- **GitHub workflow-command annotations in `--ci` mode**: `regula check
  --ci` now emits `::error` / `::warning` / `::notice` lines when
  `GITHUB_ACTIONS=true`, so findings surface inline on the PR "Files
  changed" tab without SARIF setup.
- **Installation guide** at `docs/installation.md` — per-error
  troubleshooting table keyed to the literal error strings users paste
  into search engines. Covers pipx, uv/uvx, plain pip fallbacks, Windows
  PATH recovery, `externally-managed-environment`, `command not found`,
  and `ModuleNotFoundError` for optional extras.

### Changed — information architecture and install path

- **Repository IA restructured** (`site/`, `docs/`, `configs/`): all
  landing-page HTML + assets moved under `site/`, long-form governance
  docs under `docs/`, tool configs under `configs/`. 12 redirect stubs
  preserve every previous root-level URL for SEO continuity. Root is now
  limited to build metadata and repo hygiene files. GitHub Pages
  workflow updated to deploy `./site` as the artifact root.
- **`regula check` LIMITED-RISK section now prints finding rows**: an
  Article 50 chatbot scan previously printed only a bare `LIMITED-RISK:`
  header with no row underneath, so the finding wasn't visible without
  `--verbose`. Section header relabelled `LIMITED-RISK (Article 50)`
  for clarity. Matches how HIGH-RISK / PROHIBITED / credentials render.
- **Honest "test files excluded" suffix**: the trailing
  `(test files excluded)` annotation on a clean scan now only appears
  when test files were actually skipped, and the skipped count is
  surfaced in the telemetry payload. Previously appeared even when zero
  tests were skipped, which was misleading on directories with no tests.
- **Install documentation leads with pipx**: primary install command is
  now `pipx install regula-ai`, with `uvx --from regula-ai regula` as
  the faster alternative for uv users. Plain `pip install` is now the
  fallback section with explicit venv / conda / `--break-system-packages`
  guidance. Reason: plain `pip install regula-ai` fails with PEP 668
  `externally-managed-environment` on Ubuntu 22.04+, Debian 12+, Fedora,
  macOS Homebrew Python, and Arch. Affected files: `README.md`,
  `site/index.html` (pills and CTAs), `site/locales/de.html`,
  `site/locales/pt-br.html`, `action.yml`, `examples/*/README.md`.

### Fixed — landing page, CLI output, Python compatibility

- **Landing-page white flash on cold load**: `site/index.html` rendered
  a solid white viewport for ~600ms on slow connections before snapping
  to the dark theme. Root cause was render-blocking CSS on a dark-theme
  page — the browser had no stylesheet to paint against until
  `/assets/site.css` arrived. The hero terminal sits at the top of the
  fold so the white→dark snap read as "the demo flashing". Fix: inline
  critical CSS in `<head>` (including `color-scheme: dark`) establishes
  the brand background immediately; `/assets/fonts.css` and
  `/assets/site.css` now load via `media="print" onload` so they don't
  block first paint. `<noscript>` fallback preserves styling for
  JS-disabled clients. Measured live first-paint on simulated 3G:
  **624ms → 472ms (~24% faster)**. Qualitative result depends on OS
  preference: for users on dark-mode OS the pre-paint canvas is also
  dark (via `color-scheme`) and the flash is **eliminated**; for
  light-mode OS users the pre-paint canvas is still white but the
  flash duration shortens to ~300ms and the paint itself is dark.
  A previous attempt (commit 93a833b) targeted panel opacity and
  font preload but misdiagnosed the cause.
- **`regula docs` and `regula handoff garak` no longer pollute the
  working tree**: generator commands previously wrote artefacts into
  the Regula repo checkout rather than the user's current directory,
  dirtying version control. Output now lands in `cwd` as intended.
- **Python 3.10 / 3.11 f-string syntax compatibility**: the compliance
  CLI used f-string features only available in Python 3.12+ and raised
  `SyntaxError` on 3.10 / 3.11 despite both being listed as supported
  in `requires-python`. All nested f-strings now parse cleanly across
  3.10 / 3.11 / 3.12 / 3.13.
- **Terminal demo accessibility scaffolding** (`site/index.html`): hero
  terminal now carries `role="region"`, `aria-label`, per-tab
  `aria-selected` / `aria-controls`, `role="tablist"` and `role="tab"` /
  `role="tabpanel"`. JS swap keeps `aria-selected` in sync with the
  active tab. Decorative traffic-light bar marked `aria-hidden`.

### Added — new CLI commands

- **`regula handoff {garak,giskard,promptfoo}`** — detects LLM
  entrypoints in a project and emits a scoped red-team config for the
  target tool. Positions Regula as complementary to runtime behaviour
  testing, not competitive with it. Detected 14 entrypoints in the
  Regula repo itself on first smoke test.
- **`regula regwatch`** — reads the regulatory delta log, compares
  against `regula-policy.yaml → regulatory_basis.last_reviewed`, and
  warns when the installed ruleset is older than the most recent
  regulatory change. Ignores future-dated placeholder entries.

### Added — open data assets

- **[`content/regulations/delta-log/`](content/regulations/delta-log/)**
  — primary-source-linked regulatory changelog for the EU AI Act.
  Schema + 5 seed entries (Regulation adoption 12 Jul 2024; Digital
  Omnibus proposal 19 Nov 2025; Council general approach 13 Mar 2026;
  Parliament plenary position 26 Mar 2026; trilogue target 28 Apr 2026).
  Builder `scripts/build_delta_log.py` emits `index.json`, RSS
  `feed.xml`, and `SUMMARY.md`. CC-BY-4.0.
- **[`content/regulations/enforcement-tracker/`](content/regulations/enforcement-tracker/)**
  — schema + empty index for the first EU AI Act enforcement tracker.
  Pre-populated skeleton so the first fine can be published within
  hours, not weeks. CC-BY-4.0.
- **[`content/regulations/sandbox-registry/`](content/regulations/sandbox-registry/)**
  — 27-Member-State Article 57 sandbox registry. 5 entries seeded
  (DE, ES, FI, FR, NL) from primary sources; 22 TODO. CC-BY-4.0.
- **[`data/patterns/`](data/patterns/)** — 34 risk pattern groups
  extracted from `scripts/risk_patterns.py` as CC-BY-4.0 YAML.
  Regenerate with `python3 scripts/extract_patterns.py`.
- **[`data/site_facts.json`](data/site_facts.json)** + `site_facts.md`
  — canonical source of truth for every numeric claim on landing
  pages. Computes `historical_330_bucket` (279 + 38 + 9 + 4 = 330
  exact) and `grand_total` (502, inclusive). Regenerate with
  `python3 scripts/site_facts.py`.

### Added — integrity tooling

- **[`scripts/claim_auditor.py`](scripts/claim_auditor.py)** — stdlib-only
  scanner that blocks commits introducing unverified factual claims in
  Markdown or HTML. Recognises URLs, markdown links, HTML anchors,
  in-repo file references, bracketed verification labels, and explicit
  citation words. Exempts structural regulatory references (Article /
  Annex / Recital / Category / Chapter) and short UX time durations.
  Backtest against the last 10 commits: 54 total unsourced findings
  surfaced (noise floor ~2–4 per small commit).
- **[`scripts/ci_heal.py`](scripts/ci_heal.py)** + `.github/workflows/self-heal.yaml`
  — self-healing CI agent that classifies failing GitHub Actions
  logs (pytest / type / lint / build / import / syntax), applies a
  minimal fix via Claude Code, runs the full verify sequence locally,
  and pushes with a `Ci-Heal-Attempt: N` commit trailer. Capped at 3
  attempts per branch. Backtest: 10/10 historical failing CI runs
  classified as auto-healable. Posts PR summary comments.
- **[`.pre-commit-config.yaml`](.pre-commit-config.yaml)** — local
  pre-commit hook running the claim auditor on staged files.
- **`.github/PULL_REQUEST_TEMPLATE.md`** — with explicit verify
  checklist, honesty gate checklist, scope rules, and locale-parity
  reminder.
- **`.github/dependabot.yml`** — weekly pip + github-actions updates.

### Added — documentation

- **[`docs/what-regula-does-not-do.md`](docs/what-regula-does-not-do.md)**
  — explicit scope statement. Lists articles Regula addresses
  partially / fully (Art. 5, 10, 11, 12, 13, 14, 15, 49, 51-55, 99)
  vs cannot address (Art. 9, 17, 26, 27, 29, 43, 63, 72/73, 74).
  Positions Regula as the "code layer of an AI governance programme,
  not the whole programme".
- **[`docs/evidence-pack-guide.md`](docs/evidence-pack-guide.md)** —
  auditor-facing documentation of `regula conform` output (26-file
  Article 43 pack, SHA-256 verification steps, reproducibility
  guarantees).
- Internal planning and research documents were produced during this
  development cycle. They served their purpose and were removed from the
  public tree — the fixes they recommended are all applied. Available in
  git history if needed.

### Changed

- `pyproject.toml`: Python 3.13 classifier added, CI matrix now tests
  3.10 / 3.11 / 3.12 / 3.13. Added `Documentation`, `Changelog`,
  `Trust pack`, and `Delta log` URLs. Homepage switched to
  `https://getregula.com`.
- `CLAUDE.md`: new `## Honesty & Verification`, `## Workflow`, and
  `## Project Conventions` sections. Identity line now explicitly says
  "Positioned as the code layer of an AI governance programme, not
  the whole programme". Command count reconciled 39 → 43.
- `README.md`: test count reconciled from the stale "525 tests" to
  "688 test functions (935 passing assertions)" with inline citations
  to `scripts/site_facts.py` and `benchmarks/labels.json`.
- `index.html`, `de.html`, `pt-br.html`: "Where Regula fits" section
  now names AIR Blackbox, Systima Comply, and ark-forge as OSS peers
  (honest competitive acknowledgement). Command count 38/39 → 43.
  CycloneDX 1.6 → 1.7 (matches sbom test assertion). Framework count
  13 → 12 (removed duplicate NIST AI 600-1 from visible list).
- `de.html` and `pt-br.html`: German "Sie-form" and Brazilian Portuguese
  translations of the "Where Regula fits" section added.
- `regula-policy.yaml`: `governance.ai_officer` populated for the
  Regula project itself (maintainer accountable under Article 4);
  `last_reviewed` bumped to 2026-04-09.
- `scripts/doctor.py`: support both `governance.ai_officer` and
  `governance.contacts.ai_officer` schema paths. Result: 9 pass /
  2 info (was 8 pass / 3 info).
- `.github/workflows/ci.yaml`: new `regula security-self-check` step,
  new `html-wellformed` job, new `claim-audit` job.
- `.gitignore`: re-include `.claude/agents/**` and `.claude/skills/**`
  so agent definitions and skills are tracked while local config stays
  ignored; add `.ci-heal/` scratch dir.

### Removed

- `docs/marketing/uae_outreach_v1.md` — internal sales template not
  suitable for public repo. (Was referenced in the 1.6.1 Added section;
  that reference is now plain-text, not a markdown link.)

### Renamed

- `docs/QUICKSTART_VIBE_CODERS.md` → `docs/QUICKSTART.md` (the
  informal name was flagged by the repo audit as ageing poorly).

### Fixed

- `scripts/make_og_uae.py` was missing the `# regula-ignore` marker
  and tripped Regula's own security self-check on the first run.
  Caught by the test suite (`test_security_self_check_passes`), not
  by a human. Fixed.
- During the research-eval pass, a documentation edit about Article
  5(1)(f) triggered Regula's own `pre_tool_use.py` hook. The sentence
  was rephrased to convey the same regulatory fact without matching
  the `emotion_inference_restricted` detector. The tool worked as
  designed, live, on its own maintainer.

### Honesty note — the "330 risk patterns" claim

The "330 risk patterns" figure cited on all landing pages is not a
fabrication and not drift. It is the exact sum of the tiered risk
regexes (279) plus architecture detectors (38) plus credential
detectors (9) plus oversight detectors (4) = **330**. This bucketing
is now transparently documented in `data/site_facts.md` via the
`historical_330_bucket` computation. The grand-total figure (502) is
higher and is also published in the same file. Any auditor can
reproduce both numbers by running `python3 scripts/site_facts.py`.

## [1.6.1] — 2026-04-09

The "trust foundation" point release. Adds the buyer-facing Trust Pack,
publishes a reproducible precision/recall benchmark, kills the
`yaml not installed` nag, sharpens the doctor `.gitignore` check, and
adds standard OSS meta-files (SECURITY.md, CITATION.cff, CODE_OF_CONDUCT.md).
No breaking changes; all 935 tests still pass.

### Added

- **[`docs/TRUST.md`](docs/TRUST.md)** — Trust Pack with 9 sections.
  Every claim is paired with the exact shell command that verifies it.
- **[`docs/benchmarks/PRECISION_RECALL_2026_04.md`](docs/benchmarks/PRECISION_RECALL_2026_04.md)**
  — published precision/recall benchmark with reproducible methodology.
  Headline: 100% on the synthetic Annex III/Article 5 corpus; **0
  false positives at the BLOCK CI tier across 257 labelled findings on
  5 mature OSS projects**. Sliced by tier, project, and indicator
  category. CORE-Bench-style explicit limitations.
- **[`SECURITY.md`](SECURITY.md)** — vulnerability disclosure policy
  with supported versions, target response times, and a 90-day
  coordinated disclosure default.
- **[`CITATION.cff`](CITATION.cff)** — Citation File Format metadata.
- **[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)** — short, technical, direct.
- **[`site/regions/uae.html`](site/regions/uae.html)** — landing page
  for DIFC, ADGM, Hub71, Dubai Internet City, and NEOM portfolio teams.
  Cites Article 2(1)(c) extraterritoriality, Article 16 provider
  obligations, Article 99 fines (€35M / 7%), and Article 113 enforcement
  timing — all against Regulation (EU) 2024/1689 primary text.
  (The file lived at `uae.html` at the repo root in 1.6.1; moved to
  `site/regions/` in the 1.6.2 IA restructure.)
- `docs/marketing/uae_outreach_v1.md` — 50-message distribution test
  templates with targeting checklist, per-sector message bodies, and
  stop conditions. (Removed in 1.6.2 as an internal sales template
  not suitable for public repo; see the 1.6.2 "Removed" section below.)
- **[`demos/regula-cli.cast`](demos/regula-cli.cast)** + `regula-cli.txt`
  — asciinema v2 cast and plain-text fallback of the value-first
  user journey. 11 seconds.
- **`support@getregula.com`** — direct contact channel surfaced on
  both landing pages, in `README.md`, in `SECURITY.md`, and in the
  Trust Pack vendor evaluation answers.

### Changed

- **`regula doctor` `.gitignore` check is now context-aware.** It
  only WARNs about a missing `.gitignore` when the cwd is actually
  inside a git repository (walks up looking for `.git/`). Outside a
  git repo it shows INFO instead of WARN.
- **`yaml not installed` nag is silent by default.** The fallback
  parser works; users were seeing the same notice on every CLI
  invocation. The full optional-dependency picture is still in
  `regula doctor`. Set `REGULA_VERBOSE=1` to opt back in.
- **Landing page CTA reordered.** Primary button now installs
  ("Try free in 30 seconds"); `regula assess` is the secondary
  "no codebase needed" option.
- **Landing page footer expanded** with Trust Pack, Benchmarks,
  SECURITY.md, UAE page, and `support@getregula.com`.
- **`README.md`** — new "Trust, security, and how to verify" and
  "Contact" sections.
- **Test count: 925 → 935.**
- Removed 24 stale `docs/tmp*_annex_iv.md` files left over from
  prior conformity-pack test runs.

### Verified

- 935/935 custom test runner
- 6/6 self-test
- doctor: 8 pass / 3 info / 0 warn (in a git repo)
- bandit `-c pyproject.toml`: 0 / 0 / 0
- semgrep `p/security-audit + p/python`: 0 findings on 200 rules / 129 files
- pip-audit: 0 vulnerabilities
- regula self-scan: 0 findings

---

## [1.6.0] — 2026-04-09

The "live-path reliability" release. Bundles the v1.6 feature work that
shipped over March–April 2026 with five P0/P1 fixes uncovered by the
April 2026 reliability audit and a `/research-eval` pass against primary
EU and UNESCO sources.

### Added

- **`regula conform --sme`** — SME-simplified Annex IV under Article 11(1)
  second subparagraph (interim format pending Commission template).
- **`regula exempt`** — Article 6(3) high-risk exemption decision tree
  with the Commission's missed 2 February 2026 Article 6(5) guideline-deadline
  disclosure baked in. Interactive or `--answers yes,no,...` for CI use.
- **`regula register`** — Annex VIII Section A/B/C registration packet
  generator (Article 49). Branches by provider/deployer role and Annex III
  area, including Article 49(4) non-public routing for biometrics / law
  enforcement / migration and Article 49(5) national-level routing for
  critical infrastructure. Auto-fills from existing scan artefacts and
  dual-annotates 2026-08-02 vs Omnibus-proposed 2027-12-02 deadlines.
- **`regula gpai-check`** — maps GPAI provider code to the three chapters
  of the GPAI Code of Practice (Transparency / Copyright / Safety &
  Security) with Article 53 + Article 55 scope rules.
- **OWASP LLM01:2025 prompt-injection detection (expanded)** — direct
  user-input concatenation, indirect (RAG / web-fetch / file-read flowing
  into prompt), and tool-output (plugin/function results passed back).
- **Tier-3 regional landing pages** — Colorado AI Act (SB 24-205 +
  SB 25B-004 delay to 30 June 2026), South Korea AI Basic Act, United
  Kingdom (DSIT-led approach), South Africa April 2026 draft policy.
- **Harmonised-standards plumbing** — `references/harmonised_standards.yaml`
  ready to load CEN-CENELEC standards once published Q4 2026 (currently a
  documented stub).
- **`regula assess --answers`** — non-interactive `regula assess` for CI /
  piped use. Previously errored "requires an interactive terminal" with
  no escape hatch.
- **JS/TS tree-sitter data-flow tracing** with destination classification
  (log / api_response / human_review / persisted / display /
  automated_action / return) — already shipped, README finally documents it
  honestly.
- **Recall expansion** for Annex III pattern lists in `risk_patterns.py`:
  - `employment` — classify_resume / score_resume / hire-reject / job-applicant
    phrasings + prompt-string templates.
  - `education` — grade_essay / predict_dropout / admissions ranking /
    placement scoring + prompt-string templates.
  - `essential_services` — approve_loan / mortgage / health insurance pricing
    / welfare eligibility / claim assessment.
  - `law_enforcement` — parole / bail / threat-scoring (lawful Annex III
    uses, distinct from the Article 5(1)(d) profiling prohibition handled
    by `PROHIBITED_PATTERNS`).
- **Regression tests** for every recall expansion and bug fix:
  - `test_recall_realistic_employment_code`
  - `test_recall_realistic_education_code`
  - `test_recall_realistic_essential_services_code`
  - `test_recall_realistic_law_enforcement_code`
  - `test_assess_run_from_answers_non_interactive`
  - `test_scan_files_exposes_files_scanned_count`

### Fixed

- **Scan cache silent staleness on upgrade.** `ScanCache` now keys
  entries on `{path}:v2:{regula_version}:{patterns_fingerprint}:{sha256}`.
  Previously only `{path}:{sha256}`, so users who upgraded Regula kept
  seeing stale "no findings" results until they edited each file. The
  most subtle reported bug.
- **`Files scanned: 0` lying.** `scan_files` now exposes the real
  scanned-file count via `scan_files.last_stats`, and `cmd_check` uses it
  instead of misreporting `len(unique files with findings)`. Empty scans
  now print an honest "no code files matched" message.
- **`regula assess` non-TTY crash** — see Added.
- **Recall gap on realistic AI code** — see Added (recall expansion).
- **README v1.3 roadmap line** — corrected: JS/TS tree-sitter data-flow
  already ships in `scripts/ast_engine.py`. AVID and typosquat moved to
  explicit backlog.
- **Five factual errors** identified by `/research-eval`:
  1. Commission Omnibus proposal date — was "December 2025", actually
     **COM(2025) 836 adopted 19 November 2025**
     ([EP Legislative Train](https://www.europarl.europa.eu/legislative-train/package-digital-package/file-digital-omnibus-on-ai)).
  2. "10 Annex III categories" — Annex III has **8 areas** (points 1–8).
     Regula has 10 high-risk pattern categories because it includes 2
     Annex I (Article 6(1) harmonised legislation) categories: medical
     devices and machinery safety components. README, ROADMAP, and
     the documentation now makes the split honest. Detection logic was
     correct; only the labelling was wrong.
     ([Regulation (EU) 2024/1689 Annex III](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
  3. Trilogue timing — was "first trilogue completed in late March 2026,
     second scheduled for 28 April 2026". Parliament adopted its
     plenary mandate on **26 March 2026** (after the **Council's 13 March
     mandate**); trilogue negotiations launched the same day. The 28 April
     date is the **Cypriot Council Presidency's target for political
     agreement**, not a scheduled meeting.
     ([EP press release dated 26 March 2026](https://www.europarl.europa.eu/news/en/press-room/20260323IPR38829/),
      [Council 13 March 2026](https://www.consilium.europa.eu/en/press/press-releases/2026/03/13/council-agrees-position-to-streamline-rules-on-artificial-intelligence/))
  4. EP plenary vote — recorded as "569–45" on "23 March". Corrected to
     **569 in favour, 45 against, 23 abstentions on 26 March 2026**
     (the EP press release URL slug `20260323IPR38829` led to the date
     error — the press release is dated 26 March 2026 per its own header).
     ([howtheyvote.eu/votes/189384](https://howtheyvote.eu/votes/189384))
  5. AICDI gap framings — "closes the 2.7% gap" / "closes the 12% gap"
     inverted the direction. The 2.7% / 12% are the share of companies
     that **have** the safeguard, so the gap is 97.3% / 88%. Reworded.
     ([dig.watch coverage of UNESCO/TRF report](https://dig.watch/updates/unesco-responsible-ai-practice-report))

### Verified

- 889/889 custom runner tests
- 734/734 pytest tests
- `regula self-test` 6/6
- `regula doctor` 8 PASS / 2 INFO / 1 WARN (Sentry DSN unset, unrelated)
- Clean-venv install of `dist/regula_ai-1.6.0-py3-none-any.whl` runs every
  advertised v1.6 command end-to-end (`conform --sme`, `exempt --answers`,
  `gpai-check`, `assess --answers`, `register`, `disclose`)
- `twine check` PASSED on `dist/regula_ai-1.6.0-py3-none-any.whl` and
  `dist/regula-ai-1.6.0.tar.gz`

### Known issues

See [TODO.md](TODO.md) for the prioritised gap backlog.

## [1.5.0] — 2026-04-03

### Added
- EU Cyber Resilience Act (2024/2847) as 11th compliance framework mapped to Articles 9-15
- 2 vibe-coding architecture antipatterns: no_error_handling_ai_call, exposed_api_key_env
- Vibe coder quickstart guide (docs/QUICKSTART_VIBE_CODERS.md)
- `Finding` dataclass — formalises the scan finding contract (12 fields, backward-compatible)
- `compute_finding_tier()` — single source of truth for block/warn/info logic
- `get_policy(path=)` override for testability
- `__all__` on 6 key public API modules (constants, risk_types, classify_risk, report, log_event, policy_config)
- 5 new risk patterns: driverless, automated driving, vehicle control system, dialogue system, conversational model
- 28 orphaned tests added to manual runner (324 total, 748 assertions)

### Changed
- Landing page: light cream theme with hexagonal tile pattern, research-validated copy targeting both vibe coders and production developers
- VERSION moved to constants.py — breaks circular import chain (evidence_pack/gen_docs/sbom no longer import cli.py)
- report.py refactored: extracted _scan_agent_autonomy(), _scan_credentials(), _scan_ai_security(), _parse_suppression_rules()
- Removed unverifiable competitive claims ("unique", "The only") from all landing pages and docs
- Competitor landscape updated with verified data: Systima Comply, ArkForge, EuConform, ClawGuard, VerifyWise
- Risk pattern count: 130 (was 123). Command count corrected: 33 (was 34).
- _compile_custom_pattern() now catches re.error
- strip_comments() docstring corrected to match actual behaviour

### Fixed
- CRA crosswalk misattributions: Art. 13(15) → Annex II, Annex VII → Art. 13(8)

---

## [1.3.0] — 2026-03-28

### Fixed
- Credit scorer false negative — `train_credit_model` and similar underscore-prefixed identifiers now correctly match `essential_services` high-risk patterns. Root cause: `\b` word-boundary anchor fails when the keyword is preceded by `_` (a word character). Fixed `credit.?model`, `credit.?risk`, `credit.?predict` in `risk_patterns.py`. Adds regression test `test_fn_fix_credit_scorer_function_names`.
- Advisory directory resolution — `_load_advisories()` in `dependency_scan.py` returned empty when Python loaded the module from `__pycache__` (`.pyc`), causing `here.parent` to resolve to `scripts/__pycache__` instead of `scripts/`. Fix: step up an extra level when `here.name == "__pycache__"`, with `Path.cwd() / "references" / "advisories"` as a final fallback. Adds regression test `test_advisory_load_fallback_pyc_path`.
- `skip_dirs` absolute path bug in `code_analysis.py` and `generate_documentation.py` — both used `filepath.parts` (absolute path) to check skip directories, causing any project nested inside a directory named `tests/`, `build/`, `venv/`, etc. to have all files silently skipped. Fixed to use `filepath.relative_to(project).parts`. Adds regression test `test_docs_nested_in_tests_dir_not_blank`.
- Version string in generated documentation was `v1.1.0` in 6 places; corrected to `v1.2.0`.

### Added
- AST analysis wired into Annex IV documentation generator (`generate_documentation.py`). Section 2.1 now lists detected AI frameworks and function signatures. Section 3.3 now includes an AST-derived oversight score (0-100), specific oversight patterns with line numbers, and unreviewed automated decision paths. Section 3.4 now includes a logging coverage score (0-100), counts of logged vs unlogged AI operations, and an Article 12 gap warning when AI operations have no nearby logging. For non-Python projects the generator falls back to regex-based detection. Adds 4 new regression tests.
- `ast_analyse_project()` helper in `generate_documentation.py` — aggregates `parse_python_file`, `detect_human_oversight`, and `detect_logging_practices` across all Python source files in a project, returning AI imports, function signatures, oversight score/evidence, and logging coverage metrics.

- `parse_go_mod()` in `dependency_scan.py` — parses Go module dependencies from `go.mod` files. Handles block `require(...)` and single-line `require` statements. All go.mod versions treated as exact (Go modules have no range specifiers). 67 known AI Go modules registered including `github.com/tmc/langchaingo`, `github.com/sashabaranov/go-openai`, `github.com/ollama/ollama`, `github.com/anthropics/anthropic-sdk-go`.
- `parse_build_gradle()` in `dependency_scan.py` — parses Java/Kotlin dependencies from `build.gradle` (Groovy DSL) and `build.gradle.kts` (Kotlin DSL). Handles string-style (`'group:artifact:version'`) and named-arg style (`group: 'g', name: 'a', version: 'v'`). 40+ known AI Java/Kotlin artifacts registered including `dev.langchain4j:langchain4j`, `ai.djl:api`, `org.deeplearning4j:deeplearning4j-core`, `org.tensorflow:tensorflow-core-platform`. Both parsers wired into `scan_dependencies()`.

### Tests
- 435 tests, 1,044 assertions (was 348 at v1.2.0 release)

---

## [1.2.0] — 2026-03-28

### Added
- `regula status --show <name>` — detailed view of one registered system with libraries, findings, risk trend
- `regula status --format csv` — CSV export of registry for spreadsheet analysis
- `regula status --format json` — structured JSON export of registry
- `regula discover --sync` — re-scan all previously registered projects, update timestamps and risk levels
- `regula docs --format model-card` — generates HuggingFace-compatible model card with auto-detected architecture, data sources, and EU AI Act compliance section
- Auto-populated Annex IV sections: model architecture (from imports), data sources (CSV/DB/API/S3), human oversight patterns, logging infrastructure, risk register with OWASP mappings
- `scripts/code_analysis.py` — detection helpers for architecture (12 frameworks), data sources (10 types), oversight (4 categories), logging (4 types)
- `tests/test_documentation.py` — 10 test functions / 22 assertions for documentation generation
- MCP server permission analysis — parses `mcpServers` config, assesses risk per server against OWASP Agentic Top 10
- MCP credential detection in both env vars (MEDIUM) and hardcoded args (HIGH)
- Known MCP server risk profiles (filesystem, postgres, github, slack, puppeteer, fetch, everything)
- Autonomous action detection — flags AI output flowing to subprocess/HTTP/database without human gate
- OWASP Agentic Top 10 mapping (#1 Excessive Agency, #2 Uncontrolled Tool Use, #5 Identity Gaps, #6 Unmonitored Actions, #7 Data Exfiltration, #8 Supply Chain)
- `tests/test_agent_governance.py` — 10 test functions / 13 assertions for agent governance
- `tests/test_reliability.py` — 12 test functions / 17 assertions for edge cases (unicode, null bytes, binary files, concurrent writes, nested JSON, network timeout)
- Narrowed 16 `except Exception` blocks across 8 files to specific exception types (OSError, ValueError, SyntaxError, subprocess.SubprocessError). 3 intentional catch-alls remain with comments explaining why.
- Risk trend tracking — `previous_highest_risk` stored when risk tier changes between scans
- `tests/test_registry.py` — 8 test functions / 21 assertions for registry features
- `--ci` flag for check command — implies `--strict`, exits 1 on any WARN or BLOCK finding
- Generic exception handler in CLI — non-RegulaError exceptions produce a clean message with bug report link instead of raw tracebacks
- Smoke tests for CLI subcommands (previously only 5 were tested)
- Tests for `--ci` flag behaviour (5 tests: compliant, warn-tier, error, global position, info-tier)
- Tests for generic exception handler and `--framework` removal
- 3 hook resilience tests: empty stdin, large payload (500KB), binary content edge cases
- `scripts/__main__.py` — enables `python -m scripts` invocation
- `INFO` status level in `regula doctor` for setup-specific items (not problems)
- Pytest compatibility — tests run via both `python3 tests/test_*.py` and `pytest tests/`
- 2 new test fixtures: `sample_prohibited` (Article 5), `sample_mixed_tier` (employment + chatbot)
- Benchmark manifest at `tests/fixtures/benchmark_manifest.json`

- `--skip-tests` flag for `check` — excludes test files entirely from scan results (removes ~27% noise on typical AI codebases)
- `--min-tier` flag for `check` — filters output to a minimum risk tier (`prohibited`, `high_risk`, `limited_risk`, `minimal_risk`); combined with `--skip-tests` reduces LangChain's 2,108 raw findings to 19 actionable ones
- Agent autonomy detection wired into `check` — `detect_autonomous_actions()` now runs on all code files, not just via `agent` subcommand
- Contextual agent path detection — files in `agent/`, `tool/`, `middleware/`, `plugin/`, `executor/`, `sandbox/` paths are flagged for subprocess/exec even without AI imports (OWASP Agentic ASI02/ASI04)
- `agent_autonomy` tier in SARIF output and text report
- `_is_test_file()` extended to catch suffix patterns (`standard-tests/`, `langchain_tests/`)
- `test_security_hardening.py` — security hardening assertions (no eval/exec in source, no os.system, self-scan clean)

### Changed
- Refactored 5 CLI commands (report, audit, install, docs, discover) from sys.argv manipulation to direct function calls
- Split classify_risk.py (844 lines) into 4 focused modules:
  - `risk_types.py` (63 lines) — RiskTier enum and Classification dataclass
  - `risk_patterns.py` (321 lines) — all EU AI Act pattern definitions
  - `policy_config.py` (132 lines) — policy loading, caching, and accessors
  - `classify_risk.py` (377 lines) — classification logic, security checks, CLI
- All existing imports (`from classify_risk import X`) continue to work via re-exports
- `datetime.utcnow()` replaced with `datetime.now(timezone.utc)` — removes Python 3.12+ deprecation warnings
- Doctor output distinguishes INFO (setup needed) from WARN (potential issue)
- Doctor .gitignore check recognises `.regula/` as covering audit subdirectory
- Removed false "world-readable policy file" warning from doctor (policy contains no secrets)
- README: removed stale `--framework` CLI examples, added `--ci` flag documentation
- `sample_warn_tier` fixture docstring corrected to document test-path deprioritisation

### Removed
- Unused `--framework` global flag (was declared but never consumed by any command)

### Fixed
- `--ci` flag now works after subcommand (`regula check --ci`) not just before it
- `regula audit query` now correctly passes `--after` and `--before` date filters (were silently dropped)
- `regula docs` now correctly supports `--format json` output (was silently defaulting to markdown)
- `regula discover` now correctly supports `--format json` in all code paths
- False positive regex patterns tightened with word boundaries:
  - `predictive.?polic` → `predictive.?policing`
  - `face.?scrap` → `\bface.?scrap`
  - `race.?detect` → `\brace.?detect(?!.*(?:condition|thread|concurrent))`
  - `face.?recogn` → `\bface.?recogn`
  - `voice.?recogn` → `\bvoice.?recogn`
  - `support.?bot` → `support.?bot\b`
  - `age.?estimat` → `\bage.?estimat`

## [1.0.0] - 2026-03-11

### Added
- Initial release
- EU AI Act Article 5 prohibited practice detection (8 categories, 24 patterns)
- Annex III high-risk classification (10 categories)
- Limited-risk and minimal-risk classification
- Confidence scoring (0-100 with BLOCK/WARN/INFO tiers)
- Credential detection (API keys, private keys, connection strings)
- SARIF output for CI/CD integration
- HTML report generation
- Audit trail with hash-chain verification
- AI system discovery and registry
- Compliance status management with workflow transitions
- Gap assessment (Articles 9-15)
- Questionnaire-based risk assessment
- Session-level risk aggregation
- Baseline save/compare for incremental compliance
- Documentation scaffolding (Annex IV, QMS)
- EU AI Act enforcement timeline
- Hook system (pre_tool_use, post_tool_use, stop_hook)
- Installation for Claude Code, Copilot CLI, Windsurf, pre-commit, git-hooks
- Custom exception hierarchy (RegulaError, PathError, ConfigError, ParseError, DependencyError)
- Exit code convention (0=success, 1=findings, 2=error, 130=interrupt)
- AI security patterns (LLM05 unsafe deserialization, prompt injection, eval-on-output)
- SBOM generation (CycloneDX 1.6 format)
- Agentic AI governance monitoring (`agent` subcommand)
- Dependency supply chain analysis (`deps` subcommand)
- Multi-framework compliance mapping (8 frameworks)
- Policy thresholds configuration (block_above, warn_above)
- Diff scanning mode (`check --diff REF`)
- Remediation engine with inline fix suggestions
- Article 6(3) exemption assessment
- Model card validation
- Tree-sitter JS/TS AST analysis
- Rust, C, C++, Java, Go language support in AST engine
