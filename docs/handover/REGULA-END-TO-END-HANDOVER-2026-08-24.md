# Regula: end-to-end Codex and Claude Code handover

**Continuity date:** 24 August 2026, 20:30 Europe/London

**Repository:** `kuzivaai/getregula`

**Public product:** [getregula.com](https://getregula.com/)

**Python distribution:** `regula-ai`

**Primary readers:** the owner, Codex, Claude Code, and any engineer resuming after the laptop reset

## 1. Read this first

Regula is an open-source, local-first AI-governance risk-indication tool. It
scans source code for code-observable patterns, records deployment facts that
code cannot establish, and produces reviewable evidence scaffolds. Its public
scope currently includes the EU AI Act, South Korea's AI Basic Act and Colorado
SB 26-189. It is not legal advice, a compliance determination, a certification,
or evidence that an organisation's controls operate in practice.

The most important continuity facts are:

1. The founder-first product, version 2.0.0 release, security closeout,
   distribution measurement system and production analytics privacy hotfix are
   implemented and on `main`. Sources: merge commits `2ab71d8`, `1be502f`,
   `ef5309a`, `ef98360` and `15b559e` in `git log --merges`.
2. PR #63 merged to `main` as
   `1e0a4f7001fa8ca40d205d2434e10b371861cf48` at 19:45:34Z on 24 August.
   Its final source head was
   `f8124af2a2c65abbea1dbb83ac0f8164eda0984b`. Source: the GitHub PR record
   and `git log` after fetching `origin/main`.
3. GitHub allowed `gh pr merge --auto --merge` to merge PR #63 immediately
   rather than waiting for every in-progress check. At the last pre-merge
   query, 16 named checks had passed and 8 were still running, with no reported
   failure. The new default-branch CI, CodeQL and Regula workflows are running;
   the Action workflow passed. This is not a final deployment verdict. Verify
   runs `32770006248`, `32770006256` and `32770006275` before claiming the
   merged state is terminally green or deployed.
4. The exact local acceptance command passed on the closeout tree before this
   handover was written: 1,464 legacy assertions passed across 1,427 runner
   functions; 3,135 pytest cases passed; self-test passed 6/6; doctor reported
   8 pass and 4 informational notices. Sources: terminal run ending 24 August
   2026 and `data/site_facts.json`. Adding this documentation does not alter the
   test collection.
5. The public website was genuinely updated. Production was checked after PR
   #62 deployed. A browser journey with an injected
   `utm_content=secret-company-name` emitted exactly Pageview, Qualifier Start
   and Qualifier Complete; every transmitted URL was
   `https://getregula.com/`, the injected value was absent, only allowlisted
   campaign properties were present, no automatic form-submission event fired,
   and the console had no errors or warnings. Source:
   `data/distribution_execution_policy.json`, action
   `anonymous-funnel-contract-2026-08-24`.
6. Public distribution has not yet produced demand evidence. Four editorial
   routes are prepared but not sent. Three are email-only, and the available
   Google credential returned HTTP 403 on a read-only Gmail API capability
   probe. Changelog requires an authenticated attributed account. Do not call
   these submissions executed. Source: `docs/distribution/SUBMISSIONS.md` and
   the 24 August browser/capability checks.
7. Two untracked directories are present: `marketing/` and `output/`. Together
   they contained 59 files at the continuity timestamp; approximate local sizes
   were 16 KiB and 4.1 MiB respectively. They are not in Git and will not be
   restored by cloning the repository. Back them up separately before resetting
   the PC. Source: `git status --short`, `find ... -type f | wc -l` and `du -sh`.

## 2. What is safely recoverable after the reset

The following work is already remote and recoverable from GitHub:

- `main` through PR #63 merge commit
  `1e0a4f7001fa8ca40d205d2434e10b371861cf48`;
- the merged PR #63 source branch through
  `f8124af2a2c65abbea1dbb83ac0f8164eda0984b`;
- release tags `v2.0.0` and floating `v2`; floating `v1` was deliberately left
  unchanged;
- published PyPI package `regula-ai` 2.0.0 and its GitHub Release assets.

Sources: `git branch -vv`, `git tag --list`,
`data/distribution_execution_policy.json` and
`docs/distribution/SUBMISSIONS.md`.

This handover and its pointer updates are visible on merged `main` through PR
#63. A final status correction follows on branch
`docs/pc-reset-handover-final`; use the verified Downloads copy if that branch
has not yet merged when the PC resets.

The following local data is not protected by the repository:

- `marketing/`, including `marketing/.handover.md` and
  `marketing/blog-what-a-scanner-cannot-see.md`;
- `output/`, including browser screenshots and Playwright evidence;
- browser sessions, terminal scrollback, temporary files and locally cached
  authentication state;
- any unpublished Plausible export or platform login state that exists outside
  the repository.

A non-destructive recovery archive was created at
`/mnt/c/Users/mkuzi/Downloads/REGULA-UNTRACKED-WORK-BACKUP-2026-08-24.tar.gz`.
It contains both directories, 59 files and 67 total archive entries including
directories. Its SHA-256 is
`1e83e0ff6b70546b094e43b2d39193b3d6117c5877c5c2890594da08fa20fc7e`.
Source: `find marketing output -type f`, `tar -tzf`, `wc -l` and `sha256sum`
run on 24 August 2026. This is a continuity backup, not a decision to commit or
publish those files.

Do not add `marketing/` or `output/` to a commit without first asking the owner
what belongs there. They pre-dated the closeout work and were deliberately left
untouched.

## 3. Product purpose and target users

The primary landing-page user is a non-technical founder or operator trying to
answer a practical question: could AI regulation reach this business, and what
should the team do next? The secondary user is a developer who needs local code
evidence and CI integration. A third user is a technical, governance or legal
reviewer who needs traceable scaffolds without machine-made legal conclusions.

The intended task sequence is:

1. record scope and deployment context;
2. scan code for candidate indicators and engineering evidence;
3. keep unresolved legal or organisational facts unresolved;
4. route the result to the right technical and legal owners;
5. generate artefacts that humans can complete and review.

The public interface must remain founder-first. Developer commands and detailed
product breadth belong after the plain-language task and limitations, not ahead
of them. Automated checks establish mechanical evidence only. Representative
founder comprehension, confidence and task completion have not been measured,
so nobody should call the interface human-validated or fully user-ready.

## 4. Non-negotiable truth boundaries

The following are hard product and communications rules:

- Never turn a code observation into a legal applicability, risk-tier,
  compliance or conformity determination.
- Never present absence of a finding as compliance, safety or legal clearance.
- Keep detector observations separate from the decision kernel and from facts
  declared by a human.
- Keep obligations unresolved until the decision kernel has enough sourced
  applicability facts.
- Treat generated Annex IV documents, evidence packs and governance outputs as
  scaffolds requiring human completion.
- Do not offer legal advice or compliance certification.
- Do not accept customer source uploads.
- Keep payment, consultant booking and personal-data transmitting forms
  disabled until their independent P0 gates are complete.
- Do not use unsupported urgency, vanity metrics, synthetic benchmark results
  as real-world accuracy, or conversion language unsupported by a defined
  denominator.

The owner directive is encoded in
`data/distribution_execution_policy.json`. Its effective states include safe
local implementation, tests, commits, pushes, PR updates, policy-gated merge,
policy-gated deployment, release, anonymous analytics and controlled
distribution. It expressly keeps payment, booking, personal-data web forms,
legal advice, certification and customer source upload inactive.

## 5. Current Git, release and deployment state

### 5.1 Git

- Local branch after the final status correction began:
  `docs/pc-reset-handover-final`.
- Merged PR #63 source head:
  `f8124af2a2c65abbea1dbb83ac0f8164eda0984b`.
- Local and remote `main` after the last fetch:
  `1e0a4f7001fa8ca40d205d2434e10b371861cf48`.
- PR #63 is merged; its default-branch workflows require terminal
  verification.
- The only pre-handover working-tree entries were untracked `marketing/` and
  `output/`.

These values are observations, not permanent facts. Run the commands in section
18 immediately after recovery.

### 5.2 Completed merge sequence

- PR #55: founder-first website and associated correctness work, merged as
  `2ab71d8`.
- PR #57: version 2.0.0 release preparation, merged as `1be502f`.
- PR #58: security closeout, merged as `ef5309a`.
- PR #61: analytics, measurement and distribution operating system, merged as
  `ef98360`.
- PR #62: analytics privacy hotfix, merged as `15b559e`.
- PR #63: production-evidence closeout, current-state correction and recovery
  handover, merged as `1e0a4f7`.

Source: `git log --merges --oneline` and GitHub PR records.

### 5.3 Package release

`regula-ai` 2.0.0 was published on 24 August 2026. The release workflow built,
published and verified the package. Independently downloaded wheel and sdist
assets matched `SHA256SUMS`; a clean wheel install reported 2.0.0 and passed the
six self-tests. PyPI Integrity records bind both artefacts to
`kuzivaai/getregula`, `.github/workflows/release.yml` and the `pypi`
environment. Exact hashes and the immutable release commit are recorded in
`docs/distribution/SUBMISSIONS.md` and
`docs/venture/gtm-2026-08-14/GTM-SPRINT-PLAN-2026-08-14.md`.

Do not describe provenance as proof of security. It proves how an artefact was
published, not that the code is correct or safe.

### 5.4 Production website

The production site is GitHub Pages at `https://getregula.com/`. PR #62's main
deployment completed successfully before the production browser verification.
The founder-first page, qualifier, browser assessment/scanner, pricing truth
page, privacy pages and locale surfaces are live.

GitHub Pages response headers still lack a repository-controlled Content
Security Policy, HSTS, `X-Content-Type-Options`, `Referrer-Policy` and
`Permissions-Policy` at the last audit. That is an honest hosting/security gap.
Do not claim the site has those protections merely because equivalent meta tags
or local configuration exist.

## 6. What changed in the founder-first product

The old landing page led with the CLI and exposed a long sequence of technical
features, terminal transcripts, regulatory content and market positioning. The
new experience leads with a five-question, plain-language qualifier for
founders and operators, including explicit "not sure" choices. It routes to:

- a free local route;
- a written-assessment concept with honest availability limits;
- an unbooked consultant-conversation route without a booking control.

The detailed developer and product content was moved behind clearer information
architecture rather than deleted indiscriminately. English, German and
Brazilian Portuguese surfaces were kept in sync. The shared qualifier generator
and locale structures are guarded by tests.

Mechanical browser verification covered representative desktop and mobile
viewports, 640 px, 390 px and 320 px widths, keyboard use, no-JavaScript state,
success, error, reset, scanner recovery, locale pages and the 404 route. Pricing
and privacy pages were checked for mobile reflow. This is not representative
human usability research.

## 7. Analytics and the production privacy incident

PR #61 introduced an anonymous event contract in
`data/analytics_event_spec.json`, implementation in
`site/assets/analytics.js`, a funnel processor in
`scripts/distribution_funnel.py`, and a stale-labelled retained baseline in
`data/metrics/distribution_funnel_baseline_2026-08-14.json`.

The first real production network inspection found two defects that the custom
event allowlist did not cover:

1. Plausible received the full landing URL, including arbitrary query-string
   content.
2. Plausible's automatic form tracking emitted an unregistered
   `Form: Submission` event.

External distribution was stopped. PR #62 then changed every shipped tracker
carrier and the generator template to:

- strip the complete query string from every Plausible request;
- disable automatic form-submission tracking;
- preserve only finite allowlisted campaign properties.

The post-deployment production capture described in section 1 passed. The
correct conclusion is that the captured journey respected the contract. It is
not a guarantee against a future implementation or vendor change.

The retained Plausible export ends before the new contract became effective.
It cannot establish the new funnel baseline. A fresh exact-window aggregate
export is still required, and no current Plausible credential was available in
this environment at the continuity timestamp.

## 8. Scanner parity, detector evidence and accuracy limits

The browser scanner in `site/assess/scanner.js` is a client-side port of the
Python detection rules. The parity suite now executes all 38 canonical
synthetic fixtures, including all 30 high-risk fixtures, rather than the former
13-fixture subset. The JavaScript suite currently emits 130 assertions. Source:
`node tests/test_scanner_js.js` and `docs/improvement/STATE.md`.

Parity means the two implementations make the same runtime decision on that
corpus. It does not prove that either decision is correct.

The canonical current-state generator reports synthetic high-risk label
fidelity of 18/30 and negative fidelity of 3/3 for the browser/Python parity
path. The separate default CLI condition recalls 10/30 high-risk fixtures.
Source: `docs/improvement/STATE.md`, generated by
`scripts/current_state.py` from the manifest, parity output and `RECALL.json`.

The corpus is maintainer-authored and synthetic. Those fractions do not
establish real-world precision, recall, legal accuracy, fairness or absence of
bias. There are 12 named high-risk label disagreements in the full parity
corpus. Investigate them as individual hypotheses; do not tune solely to make a
small synthetic benchmark green.

The previously published precision result is also narrow: Python only, one
reviewer, no inter-rater agreement measurement, and a historical product
version. Read the benchmark methodology before quoting it. Never generalise it
to other languages, corpora or legal decisions.

## 9. Ledger and review bot

The programme contains two distinct populations:

- machine-state ledger: 119 entries, currently 25 OPEN, 27 PARTIAL and 67
  CLOSED;
- historical table: 72 rows, including 32 `REVIEW_REQUIRED` rows.

Source: `docs/improvement/STATE.md`, generated from
`scripts/ledger_status.py` and `scripts/ledger_review.py`.

The review bot in `scripts/ledger_review.py` was built specifically to prevent
automatic laundering of ambiguous historical prose into a definitive state.
It:

- exposes the source evidence for every queued row;
- requires two genuinely independent evidenced reviews;
- preserves revisions;
- does not infer a state itself;
- does not carry a decision across changed source evidence;
- leaves disagreements for adjudication outside the bot.

Use `python3 scripts/ledger_review.py summary` before reviewing. Do not collapse
the 32-row queue into OPEN, PARTIAL or CLOSED merely to reduce a backlog count.

## 10. Security and dependency truth

The packaged core remains standard-library-only. Optional features and the
development environment have dependencies, so "zero dependencies" must never
be used as an unqualified repository-wide or feature-wide security claim.

The release closeout included dependency audits, Bandit, CodeQL and individual
review of the terminal default-branch CodeQL results. The recorded outcome was
no open CodeQL alerts after 41 results were individually dispositioned, plus a
separate Regula product indicator that remained open at the time. The optional
dependency audit recorded one advisory affecting WeasyPrint 68.1. Source:
`data/distribution_execution_policy.json` and
`docs/security/SECURITY-FINDINGS-2026-08-19.md`.

These are dated findings, not permanent guarantees. Re-run the relevant audits
after dependency or code changes. Do not describe "0 unexpected security
findings" as "secure", and do not present a scanner's own clean run as an
independent security certification.

## 11. Architecture and important source locations

### Runtime and packaging

- `scripts/cli.py`: CLI entry point and command registration. Do not refactor
  the monolith unless explicitly asked.
- `scripts/constants.py`: package version source of truth.
- `pyproject.toml`: dynamic version configuration; it must not gain a literal
  version.
- `scripts/errors.py`: error hierarchy and exit-code semantics.
- `scripts/decision_kernel.py`, `scripts/fact_store.py` and decision adapters:
  applicability and declared-fact flow.
- `scripts/risk_patterns.py`: primary risk-pattern definitions.
- `scripts/ast_engine.py` and analysis modules: language parsing and fallback
  analysis.
- `scripts/evidence_pack.py`, documentation and conformity modules: generated
  review scaffolds.
- `server.json`, `mcp-server.json`, `scripts/mcp_server.py`: MCP distribution.
- `action.yml`: GitHub Action distribution.
- `vscode-extension/`: editor integration, still outside the main Python CI
  scope unless separately exercised.

Every `scripts/*.py` module uses the repository's bare sibling-import pattern.
Keep imports such as `from errors import RegulaError`; do not convert them to
`from scripts.errors` or relative imports.

### Website

- `site/index.html`: English homepage.
- `site/locales/de.html` and `site/locales/pt-br.html`: homepage locales.
- `site/assess/`: browser assessment and scanner in three languages.
- `site/assess/scanner.js`: generated/shared scanner port.
- `site/assets/analytics.js`: anonymous analytics boundary.
- `site/assets/qualifier.js`: founder qualifier behaviour.
- `site/privacy.html` plus locale privacy pages: current disclosure.
- `site/pricing.html`: truthful service boundary; no payment or booking.
- `scripts/build_qualifier.py`: generated qualifier surfaces.
- `scripts/update_sitemap.py`: reconciles canonical URLs and git-derived dates.

Any English content change must be evaluated for German and Brazilian
Portuguese parity. Any scoring-logic change in assess must be applied to all
three locale engines. Browser inspection is required after site changes.

### Governance, evidence and distribution

- `data/distribution_execution_policy.json`: canonical authorization and
  execution decisions.
- `data/analytics_event_spec.json`: permitted analytics events and properties.
- `data/distribution_experiments.json`: experiment questions and decision
  rules.
- `docs/distribution/SUBMISSIONS.md`: listing and submission truth register.
- `docs/venture/gtm-2026-08-14/GTM-SPRINT-PLAN-2026-08-14.md`: current
  distribution and commercial operating plan.
- `docs/improvement/STATE.md`: generated current resume state. Never hand-edit.
- `docs/improvement/LEDGER.md`: detailed chronological programme record.
- `scripts/current_state.py`: generator for the current resume state.
- `scripts/ledger_status.py`: machine ledger measurement.
- `scripts/ledger_review.py`: independent review queue workflow.
- `scripts/distribution_funnel.py`: exact-window Plausible aggregate report.

### Tests and truth gates

- `tests/test_classification.py`: custom runner plus manual list. Do not delete
  the manual list.
- `tests/test_*.py`: pytest collection.
- `tests/test_scanner_js.js`: full canonical browser/Python fixture parity.
- `scripts/site_facts.py`: generates canonical public facts.
- `scripts/cascade_count.py`: propagates public count changes.
- `scripts/claim_auditor.py`: public claim and fact verification.
- `scripts/public_surface_inventory.py`: delivered-surface inventory.
- `scripts/site_integrity.py`: generated pages and link integrity.
- `tests/test_source_of_truth.py`: version-declaration enforcement.

When a test is added or removed, first regenerate `data/site_facts.json` with
`python3 scripts/site_facts.py`, then run
`python3 scripts/cascade_count.py --apply`, and finally run both tools in check
mode plus the claim auditor. This prevents a real test change from turning the
public test count into a false claim.

## 12. Distribution and commercial validation state

### Completed

- PyPI 2.0.0 is published and independently install-verified.
- GitHub Release assets and checksums exist.
- Floating major tag `v2` exists; `v1` was preserved.
- The GitHub repository description was corrected live to remove an absolute
  data-transmission claim.
- The existing GitHub Marketplace listing is live, although its accessible
  public page did not expose a version proving that the recommendation moved
  from 1.9.0 to 2.0.0.
- Anonymous campaign attribution and funnel events are implemented under a
  finite privacy contract.
- The production privacy gate passed for the tested journey.

### Prepared but not executed

The first editorial set is prepared for:

- Console.dev;
- AI Governance Library;
- Python Bytes;
- Changelog News.

Do not send generic mass outreach. Each channel requires tailored copy, a
campaign URL whose source is in the finite allowlist, one recorded submission,
and its own follow-up/stop state.

At the continuity timestamp:

- Console.dev, AI Governance Library and Python Bytes were email-only routes;
- no usable outbound email capability was available through the authenticated
  Google credential;
- Changelog's form was disabled until sign-in and states that the profile is
  used for attribution and notification;
- no submission was sent.

The next owner action is to provide or authenticate an approved sender,
preferably the existing `support@getregula.com` identity, and separately choose
whether to create or connect an attributed Changelog account. Do not send from
the owner's personal Gmail address or accept new platform terms by assumption.

### Corporate B2B outreach

The directive authorises controlled corporate outreach only under the
compliance policy. It is not ready to execute because the repository does not
contain a verified private recipient register, lawful-basis/legitimate-interest
record, suppression workflow and eligible official business addresses. Do not
scrape personal addresses, buy a list, or infer permission from the broad owner
directive.

### User research

Representative founder testing is necessary, but moderated research remains
behind its separate privacy gate. Before collecting personal data, define the
controller, notice, consent or other lawful basis as appropriate, storage,
access, retention, withdrawal and deletion route. Product analytics consent is
not a substitute for research consent.

### Paid human service

The product may truthfully describe a possible fixed-scope human review route,
but payment and booking remain unavailable. Seller identity, tax, contract,
privacy, refund/cancellation, fulfilment, professional-boundary and validated
price facts remain incomplete. Keep visible controls non-actionable or absent.
Do not call the service available.

## 13. External blockers requiring a human or credential

1. **Official MCP Registry 2.0.0:** `server.json` validates, but the official
   registry still reports 1.9.0. The stored JWT expired. Human action:
   `mcp-publisher login github`, complete the device flow as `kuzivaai`, then
   publish and verify the official API. Registry metadata is immutable per
   version, so check the exact manifest before publication.
2. **PR #63 post-merge verification:** GitHub merged before all in-progress
   checks reached a terminal state. Verify the named default-branch workflows
   and the Pages deployment before describing the merge as fully green and
   deployed.
3. **Editorial email:** configure an approved outbound sender. The current
   Google credential lacks Gmail API access.
4. **Changelog:** owner-authenticated attributed account required.
5. **Plausible:** provide an authorised current export or API credential, then
   build an exact-window report. Do not reuse the pre-contract baseline as if
   it measured current events.
6. **Google Search Console:** no credential/property was available for a fresh
   index baseline.
7. **Human research:** privacy/research protocol and responsible owner missing.
8. **Payment and booking:** P0 commercial and privacy facts missing; hard stop.

## 14. Objective outstanding priorities

The priority order is based on blocked value, falsifiability and user risk, not
on feature breadth.

### P0: preserve and reconcile current work

1. Back up untracked `marketing/` and `output/` before the PC reset.
2. Ensure the final handover-correction branch is pushed.
3. Verify the PR #63 default-branch workflows to terminal state.
4. Verify the resulting `main` deployment rather than assuming the completed
   merge equals a deployment.

### P1: execute measurable distribution without crossing identity gates

1. Authenticate an approved editorial sender.
2. Send one tailored submission per approved channel and record the exact
   timestamp, route, copy, campaign URL and state.
3. Do not duplicate the historical Hacker News submissions.
4. After a defined observation window, obtain a fresh Plausible aggregate
   export and report exact denominators. With the current low traffic, treat
   results as operational signals, not causal conversion evidence.
5. Update the official MCP Registry after owner device authentication.

### P2: validate comprehension and detection quality

1. Run representative founder comprehension/usability sessions after the
   research privacy gate.
2. Review the 12 named synthetic high-risk label disagreements without tuning
   only to the benchmark.
3. Build independent real-world labelled evidence with more than one reviewer
   before broad accuracy claims.
4. Complete two independent evidenced reviews for each of the 32 historical
   `REVIEW_REQUIRED` rows.

### P3: security and operational debt

1. Decide whether to move the public site to hosting that can set the missing
   security response headers, or document the accepted GitHub Pages limitation.
2. Re-verify the VS Code Marketplace package and bring it into a maintained CI
   path if it remains a supported distribution.
3. Re-run optional dependency audits and disposition the recorded WeasyPrint
   advisory against current upstream state.
4. Keep package-versus-source behavioural checks in the release gate so the
   public package cannot silently lag the repository product.

## 15. Known limitations and counterevidence

- A large test suite is not external validation.
- Full scanner parity is not real-world accuracy.
- A clean CodeQL or Bandit run is not proof of security.
- A provenance attestation is not proof of safe behaviour.
- Browser automation and axe do not establish human usability.
- Founder-first design is a reasoned design response, not a measured conversion
  improvement.
- The current analytics baseline predates the new event contract.
- The official MCP Registry is stale at 1.9.0 until independently verified
  otherwise.
- Marketplace existence does not prove its selected release identity.
- A public price description does not prove willingness to pay.
- A generated evidence pack does not prove legal sufficiency or organisational
  operation.
- Regulatory mappings still need qualified legal review.

## 16. Project-specific engineering rules

1. Read `AGENTS.md`, `CLAUDE.md`, this handover and
   `docs/improvement/STATE.md` before changing anything.
2. Use British English for new prose and avoid em dashes except in verbatim
   records.
3. Preserve bare imports in `scripts/*.py`.
4. Keep the packaged core standard-library-only.
5. Do not change the JSON envelope:
   `{format_version, regula_version, command, timestamp, exit_code, data}`.
6. Do not refactor `scripts/cli.py` unless explicitly requested.
7. Do not delete the custom runner's manual test list.
8. Synchronise English, German and Brazilian Portuguese site changes.
9. Verify regulatory claims against current primary sources and cite article
   numbers. Preserve the enacted Omnibus caveat for EU deadlines.
10. Do not place credentials in fixtures. The pre-tool hook scans for them;
    construct credential-like test strings from character codes.
11. Use `apply_patch` for edits and preserve unrelated dirty work.
12. Before staging, inspect `git status`; do not stage `marketing/` or `output/`
    by accident.
13. After site changes, inspect the rendered result in a real browser at
    representative mobile and desktop sizes, including failure paths.
14. Do not claim deployment from local or committed files. Check the remote
    branch, deployment job and live production response.

## 17. Internet and research rules after recovery

Before any online research, read
`/home/mkuziva/.claude/skills/agent-reach/SKILL.md` and run
`agent-reach doctor`. Use its current routing table. Install Agent Reach from
its GitHub project only, never the unrelated PyPI package. Do not connect real
Twitter, Reddit, Instagram, Facebook or XiaoHongShu accounts; the project notes
the restriction/ban risk.

For regulatory, security or technical claims, prefer primary legislation,
official registries, official documentation and original research. Record the
date checked and distinguish direct evidence, inference and unavailable data.

The Windows Downloads folder is `/mnt/c/Users/mkuzi/Downloads`, not
`/home/mkuziva/Downloads`. Verify every requested deliverable there is present,
non-empty and readable before reporting success.

## 18. Recovery and resume runbook

### 18.1 Clone and orient

```bash
git clone https://github.com/kuzivaai/getregula.git
cd getregula
git fetch --all --tags --prune
git status --short --branch
git log -8 --oneline --decorate
gh pr view 63 --json url,state,headRefOid,mergeable,mergeStateStatus,statusCheckRollup
```

PR #63 is merged, so update `main` and inspect its workflow runs:

```bash
git switch main
git pull --ff-only
git log -5 --oneline --decorate
gh pr view 63 --json state,mergedAt,mergeCommit,headRefOid
gh run view 32770006248
gh run view 32770006256
gh run view 32770006275
```

### 18.2 Reproduce current state

```bash
python3 scripts/ledger_status.py
python3 scripts/ledger_review.py summary
node tests/test_scanner_js.js
python3 scripts/current_state.py --check
python3 scripts/cascade_count.py --check
python3 scripts/claim_auditor.py --verify-facts
```

### 18.3 Complete acceptance gate

```bash
python3 tests/test_classification.py && python3 -m pytest tests/ -q && python3 -m scripts.cli self-test && python3 -m scripts.cli doctor
```

Do not paraphrase this as green unless all four commands actually exit zero.
Informational doctor notices are not failures, but report them.

### 18.4 Post-merge and production verification

```bash
git fetch origin main
git rev-parse origin/main
gh pr view 63 --json state,mergedAt,mergeCommit,headRefOid
gh run list --branch main --limit 12
```

Wait for the default-branch workflow and Pages deployment to reach a terminal
success state. Then verify live HTML and the affected browser path. The PR
mainly updates evidence, generated state, the recovery handover and synchronized
public test counts; it does not redesign the founder journey.

### 18.5 MCP Registry

```bash
mcp-publisher validate server.json
mcp-publisher login github
mcp-publisher publish server.json
```

The login step needs the owner to complete the device flow. After publication,
query the official Registry API and verify that 2.0.0 is active/latest before
changing any status record.

## 19. Suggested first prompt for Codex

> Read `AGENTS.md`, `CLAUDE.md`,
> `docs/handover/REGULA-END-TO-END-HANDOVER-2026-08-24.md`,
> `docs/improvement/STATE.md` and
> `data/distribution_execution_policy.json` completely. Reverify Git, merged PR #63,
> `main`, production, PyPI and the official MCP Registry before stating their
> status. Preserve untracked `marketing/` and `output/`. Complete any still-open
> PR #63 default-branch checks and production deployment first. Then continue only the safe,
> independently executable distribution work. Keep payment, booking,
> personal-data forms, customer source upload, legal advice and certification
> disabled. Report evidence, counterevidence and blockers without inflating
> synthetic tests into user or market validation.

## 20. Suggested first prompt for Claude Code

> Start by reading `CLAUDE.md`, `AGENTS.md`,
> `docs/handover/REGULA-END-TO-END-HANDOVER-2026-08-24.md`,
> `.handover.md`, `docs/improvement/STATE.md` and
> `data/distribution_execution_policy.json`. Treat the dated handover as a
> pointer, not live truth: run its recovery commands and update your view from
> GitHub and production. Do not touch untracked `marketing/` or `output/` unless
> the owner separately authorises them. Reconcile merged PR #63 and the production
> deployment before starting new development. Preserve the risk-indication,
> privacy, locale, accessibility and commercial hard-stop rules.

## 21. Handover acceptance checklist

- [ ] This file is committed and pushed to a recoverable remote branch.
- [ ] `.handover.md`, `AGENTS.md`, `CLAUDE.md` and `BRAIN-FEED.md` point to it.
- [ ] A non-empty readable copy exists in
  `/mnt/c/Users/mkuzi/Downloads`.
- [x] `marketing/` and `output/` are backed up separately in the verified
  Downloads archive named in section 2.
- [x] PR #63's source head and merge commit are recorded; terminal
  default-branch workflow and deployment verification remain outstanding.
- [ ] No credentials, access tokens, browser cookies or private recipient data
  are included.
- [ ] Pending actions remain labelled pending or blocked.

## 22. Final objective assessment

Regula is materially more honest and operationally disciplined than it was at
the start of this work. The website is genuinely founder-first in production,
the released package identity is current, the complete synthetic browser parity
corpus runs, the stale narrative state is generated, the historical review
queue has a non-inferential bot, and the analytics privacy defect was found in
production and fixed rather than concealed.

It is not commercially validated, legally validated, independently
accuracy-validated or human-usability-validated. Distribution has an operating
system but has not yet produced channel evidence. The official MCP listing is
stale, the current analytics baseline is stale for the new contract, and the
paid-service prerequisites remain incomplete. The correct next move is not more
feature breadth. It is safe recovery, PR reconciliation, authenticated narrow
distribution, fresh measurement, representative comprehension research and
independent detector review.
