# UX / IA / JTBD Review — 27 July 2026

Scope honesty: every heuristic finding below was observed by actually
running the command this session on this repo (v1.9.0 tree). The site
journeys section defines the audit protocol but only the CLI journeys
were executed this session; the site pass is queued work, not done work.

## 1. Jobs to be done (JTBD)

Grounded in the shipped product surface (62 commands per
[`data/site_facts.json`](../data/site_facts.json), site, evidence packs)
and the business dossier's buyer analysis:

| # | Job | When I... | I want to... | So I can... | Primary surface |
|---|---|---|---|---|---|
| J1 | First risk look | inherit or build an AI-touching codebase | see in minutes whether anything looks prohibited/high-risk | decide if compliance work is needed | `regula` bare run, `regula check .` |
| J2 | CI gate | merge AI-related changes | fail the build on new BLOCK findings | stop risk arriving silently | GitHub Action, SARIF, exit codes |
| J3 | Evidence for a human | face a customer/auditor/lawyer question | hand over a signed, dated, source-linked pack | not assemble screenshots by hand | `regula evidence-pack`, `conform`, `docs` |
| J4 | Regulatory currency | a regulation changes (Omnibus, Korea decree, Colorado stay) | know what changed and whether my duties moved | not re-read law-firm alerts | delta-log (+ dataset), region pages, `regula timeline` |
| J5 | Consultant leverage (PK channel) | advise a client | run a defensible, current assessment under my own brand | anchor paid engagements | engagement layer, evidence packs |

Task-completion definition per job (see Section 4 for how these are
measured without telemetry): J1 = first meaningful verdict on a real
project; J2 = action merged and failing correctly on a seeded BLOCK;
J3 = pack generated and verified (`regula verify`); J4 = user can state
the applicable deadline for their tier post-Omnibus; J5 = engagement
output delivered to a client.

## 2. User journeys (current state, observed)

### J1 first-run journey (executed this session)
`pip install regula-ai` then bare `regula`:
1. Bare run scans cwd and prints a summary block, top findings, and
   numbered next steps. Observed 10-37 s on this repo (136 files).
2. `regula check .` gives the detail: verdict-first output, "Why" list
   with article citations, per-tier sections, suppression transparency,
   next steps.

**Verified strengths (keep, and say so in marketing honestly):**
- Verdict-first with article citations ("Art. 5(1)(d)") in the first
  screenful; a lawyer-adjacent reader sees the legal hook immediately.
- Suppression transparency ("1 high-risk finding(s) suppressed by domain
  gating" + how to activate) is a trust feature most scanners lack.
- Contextual next steps follow clig.dev guidance.

### Heuristic findings (Nielsen), observed this session

| ID | Heuristic | Finding | Severity | Status |
|---|---|---|---|---|
| H1 | Consistency / match with mental model | Bare-run summary showed "BLOCK findings: 4" beside "Compliance score: 100/100" and tier "not_ai" with no explanation of how both can be true (score = obligations for the classification; counts = raw pattern hits, here in test fixtures). Reads as a self-contradiction at the exact moment a new user is judging credibility. | P1 | **FIXED this session**: one-line explanation now prints whenever BLOCK findings coexist with not_ai/100 (`scripts/cli.py` bare-run summary); verified live. |
| H2 | Visibility of system status | Bare run prints nothing until the scan completes (observed 10-37 s on a 136-file repo). No "scanning N files" line. | P2 | Open. Candidate: a single stderr status line when file count > threshold; must not pollute piped stdout. |
| H3 | Aesthetic/minimalist | Next-steps block alignment drifts by one space on the longest command (`evidence-pack --project .`). | P3 | Open; cosmetic. |

The three findings above are the complete set for this pass: further CLI
heuristic claims would require journeys this session did not execute.
That is the honest boundary of this review.

### J2/J3 journeys
Not executed this session. Protocol for next pass: fresh venv + sample
AI repo; run the documented Action locally (act or a scratch repo);
generate + verify an evidence pack end-to-end; time each step; log every
moment of hesitation as a finding.

## 3. Information architecture

### CLI IA
The 62 commands counted in [`data/site_facts.json`](../data/site_facts.json)
are a lot of surface. The bare-run next-steps block is the
de-facto IA entry point and covers J1 to J3 well. Queued check (not
asserted): whether `regula --help` groups commands by job rather than
alphabetically; grouping by JTBD (Scan / Comply / Evidence / Watch)
would make the 62 legible. Do not restructure command names; grouping is
presentation only.

### Site IA
Current top-level: index, about, assess (interactive scanner), regions/
(6 jurisdiction trackers), blog/, docs links, pricing, locales (DE,
PT-BR). Queued audit protocol (playwright, per quality-standards rule):
landing-to-first-value click path for each JTBD persona, nav consistency
across locales, and whether region pages surface the delta-log (J4's
canonical asset) above the fold. The delta-log dataset
(`content/regulations/delta-log/dataset/`) should gain a linked mention
on the region pages once the site pass runs — queued, not done.

## 4. Task-completion metrics without telemetry

Hard constraint (product guarantee, non-negotiable): no data leaves the
machine; there is no usage telemetry to instrument. Metrics therefore
come from consent-based and public signals only:

| Metric | Job | Source (no telemetry) |
|---|---|---|
| Time-to-first-verdict | J1 | Scan time is already printed locally; docs invite users to self-report in a GitHub Discussion template. Published benchmarks re-measure it per release on the fixture corpus. |
| CI adoption proxy | J2 | Public GitHub code search for the Action's uses string, counted per release; recorded in the dossier with method + date. |
| Evidence-pack completion | J3 | Sales evidence only (packs sold/delivered); never inferred. |
| Currency awareness | J4 | Delta-log feed subscribers are not trackable by design; proxy = GSC queries for deadline-related terms once GSC is re-authed (owner). |
| Docs efficacy | J1-J3 | GitHub issues tagged `docs-gap`; the count and close rate are the metric. |

Anti-metric rule: never publish a number whose collection method is not
stated beside it (claim-auditor discipline applies to UX metrics too).

## 5. Fix log and queue

- FIXED (this session): H1 contradiction line (P1) — root-cause
  explanation, not a cosmetic reword; verified by re-running bare
  `regula`; self-test 6/6, doctor 8 passed after change.
- QUEUED P2: H2 progress line for large scans.
- QUEUED P3: H3 alignment nit.
- QUEUED: site playwright pass per Section 3 protocol; `--help` grouping
  check; region pages linking the machine-readable dataset.
