# Decision log

## D-001: Product boundary

- Evidence: OBSERVED in `docs/ENGINEERING_ROADMAP.md` and explicitly supplied
  by the owner for this session.
- Decision: Regula is a local code-observation and evidence-preparation tool.
- Consequence: code matches cannot populate legal applicability, legal tier,
  duties, compliance, conformity, certification, safety or legal
  non-applicability decisions. Those fields remain unresolved until an
  accountable reviewer completes them.

## D-002: Dirty-tree compatibility

- Evidence: OBSERVED material dirty state with direct overlap in website files.
- Decision: preserve all pre-existing content and implement compatible
  incremental changes only after reading the relevant diff.
- Consequence: no cleanup, reset, stash, attribution or broad regeneration is
  permitted.

## D-003: No release or external mutation

- Evidence: owner authority boundary and current no-push remote.
- Decision: no commit, push, deployment, publication, external GitHub change,
  package operation or communication.

## D-004: Legal and language review boundary

- Evidence: legislation skill is UK-specific; EU legal and fluent locale
  approval are outside this implementation authority.
- Decision: use current official EU sources for engineering wording checks,
  preserve explicit uncertainty, and mark qualified legal and fluent-language
  review as external assurance.

## D-005: Public review schema replaces machine legal outcomes

- Evidence: REPRODUCED public adapters exposed internal predicate-engine
  `indications`, `obligations` and outside-scope candidates.
- Decision: keep the predicate engine internal and expose versioned reviewable
  context with candidate references and `human_decision: null`.
- Consequence: public schema 2.0 is intentionally incompatible with consumers
  of the old decision object. A later owner-approved major release must manage
  that compatibility boundary.

## D-006: Preserve conformity evidence layout, remove authority

- Evidence: the legacy article-organised pack generated readiness,
  classification, deadline, duty and conformity fields after declared facts.
- Decision: retain useful evidence directories and integrity records, but
  convert their contents to observations, unresolved reviewer questions and
  blank human-decision fields.
- Consequence: no declared context can unlock an automated conformity result.

## D-007: Preserve the compatible pre-existing website redesign

- Evidence: the starting manifest records 63 website and generated-page
  changes that existed before remediation.
- Decision: retain that work and apply boundary, journey, accessibility and
  integrity fixes incrementally.
- Consequence: visual authorship cannot be attributed to this session, and
  current visual acceptance remains unverified.

## D-008: Version sharing rather than reinterpret old links

- Evidence: version 3 merged missing and explicit uncertainty, then padded
  absent positions.
- Decision: version 4 preserves explicit states; legacy links decode only as
  visibly `legacy_lossy` evidence.
- Consequence: compatibility is preserved without pretending that lost state
  can be reconstructed.

## D-009: Controlling CI consumes the repository lock

- Evidence: the lockfile existed, but controlling Linux lanes installed ranged
  extras directly.
- Decision: pin the package-manager bootstrap and use locked synchronisation in
  those lanes.
- Consequence: remote CI execution is still external, but its repository-local
  dependency input is deterministic.

## D-010: Local-review status only

- Evidence: publication controls are blocked, browser review did not execute,
  the second rating is absent and the Git index is read-only.
- Decision: classify the current tree as ready for local code review only.
- Consequence: it is not production-ready, not ready for representative
  evaluation and not approved for publication.
