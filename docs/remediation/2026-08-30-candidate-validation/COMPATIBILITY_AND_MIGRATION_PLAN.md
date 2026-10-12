# Compatibility and migration plan

Date: 30 August 2026

## Compatibility boundary

Public review schema 2.0 is intentionally incompatible with consumers that treated detector output as an automated legal outcome. Compatibility is retained where it does not preserve misleading semantics.

## Machine-readable output

The stable outer JSON envelope remains unchanged:

`{format_version, regula_version, command, timestamp, exit_code, data}`

Inside `data`, supported decision-capable surfaces now use public review schema 2.0. Consumers must migrate away from:

- `result_type`
- `rule_resolution`
- `indications`
- `obligations`
- `outside_scope_basis`
- `decision_trace`

Use observations, declared context, missing context, contradictory context, potentially relevant references, reviewer questions, suggested review steps, limitations and an accountable human-decision field instead.

Do not create a compatibility layer that repopulates the former fields from code matches. That would recreate the defect.

The local discovery registry still persists `highest_risk`,
`previous_highest_risk`, `risk_classifications`, and `compliance_status` for
on-disk compatibility. Supported CLI JSON translates them to
`highest_detector_class`, `previous_detector_class`,
`detector_observations`, and `declared_workflow_status`, and leaves
`human_decision` empty.

Annex VIII output is now a schema 2.0 review scaffold. Migrate from
`registration_required`, `not_applicable`, or `no_registration_required` to
`registration_evidence_scaffold` or `unresolved_registration_scope`.
Candidate sections, targets and Article references are review inputs rather
than legal outcomes.

## Share links

Share payload schema 4 preserves absent, unanswered, explicitly unsure, yes, no, contradictory and not-applicable evidence where represented by the assessment.

Legacy links decode through an explicitly lossy recovery path. Unsupported or malformed payloads display a recovery state rather than manufacturing answers. Applications should retain the original link when reporting a migration problem.

## Cache

Cache schema v8 invalidates incompatible entries. Behaviour-changing rule, policy, threshold, domain, parser, feature, scanner and path-context inputs participate in identity. Old entries are not migrated into v8 results.

## CLI names

No command was removed in this candidate. This preserves scripts while public meaning changes.

- `check` remains the primary CORE workflow.
- `classify` and `compliance` are DEPRECATED but retained for compatibility.
- `comply`, `conform`, `exempt`, `assess`, `gap`, `governance`, `model-card` and related advanced commands are clarified as review-evidence or scaffold operations.
- Future renaming should use a compatibility alias, warning period and explicit machine-output versioning.

The complete disposition is in `COMMAND_AND_CAPABILITY_DISPOSITION.csv`.

## Integrations

- REST v1 remains EXPERIMENTAL, loopback-first and unauthenticated.
- MCP remains EXPERIMENTAL and now requires an explicit workspace root.
- SARIF remains ADVANCED; host severity rendering may visually overstate detector meaning.
- Weekly digest is workflow tooling under `tools/`, not an installed package module.
- Rating packets are evaluation tooling, not product output.

## Rollback

The candidate is isolated at a single commit and complete-history bundle. Rollback means continuing from the pre-candidate branch and snapshots, not rewriting history or deleting owner changes. Do not merge a partial subset of schema writers without their shared adapter and regression tests.

## Required downstream work

1. Inventory every external consumer of the six removed public fields.
2. Provide a schema 2.0 example and field mapping without synthesising legal outcomes.
3. Test old and new share links in a real browser.
4. Exercise MCP path containment on native Windows.
5. Confirm that extension and CI consumers render observation semantics consistently.
