# Brain feed

The five lines below are read mechanically by `~/kuziva-brain`
(`scripts/sync-projects.sh`, daily). Keep them current before ending a session in
which anything material changed. Contract and rationale:
`~/kuziva-brain/state/projects/FEED-CONTRACT.md`.

Write prose, not metrics. Any number here must carry its source in the same
line, because this file is a tracked markdown surface and the claim auditor
scans it like any other.

<!-- BRAIN:BEGIN -->
state: Development-time AI governance risk-indication CLI, published and deployed. The claim gates are green on main and the commercial gates are not.
blocker: The controlling commercial verdicts (STOP, PRODUCT_PILOT_STATUS NOT_APPROVED, TECHNICAL_EVIDENCE FAILED) stand until new evidence clears each gate on its own terms; no engineering increment moves them.
next: Owner decisions before engineering, per the priority action plan in the 13 August end-to-end dossier: name the seller and consultant, define the service scope, take qualified advice on terms, refunds, privacy and tax. Separately, review two committed workstreams on feat/engagement-fixes (PR #55 is still open, nothing is on main): the browser-assessment rework, where the questionnaire flow is now one shared module instead of three inline copies and the German and Brazilian Portuguese intros no longer claim the tool determines a legal classification; and a claim-integrity pass that verifies quoted regulatory passages against cached primary corpora, and rebuilds the prohibited-claim guard so it reads accented and marked-up copy in all three shipped languages rather than English only.
gates: Claim freeze holds for external use. No precision figures, no test count, no pattern count, no version number, no cross-map count anywhere outside this repo. Never present a scan as a compliance determination, or "not flagged" as "compliant". Payment and booking stay disabled until every P0 control is complete.
updated: 2026-08-14
<!-- BRAIN:END -->

## Context the block cannot carry

The claim quarantine (`.claim-quarantine.json`) is the thing most easily
misread from outside. The published-surface gate passing does not mean the
published claims are reconciled: the quarantine holds pre-existing claims that
its own status field records as unverified and not endorsed, so that the gate
can pass for new claims while that backlog burns down. Anyone quoting this
project's numbers should read the quarantine before deciding a green gate means
what they want it to mean.
