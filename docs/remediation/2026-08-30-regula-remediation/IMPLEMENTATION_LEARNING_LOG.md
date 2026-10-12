# Implementation learning log

## 30 August 2026: passing semantic guard did not cover renderers

- Initial assumption: the existing determination guard and conformance suite
  would identify most legal-outcome wording in supported outputs.
- New evidence: both passed while HTML, PDF and model-card outputs still made
  dominant legal-tier and mandatory-duty statements.
- Changed conclusion: phrase scanning is a supporting control, not the primary
  product-boundary control.
- Effect on implementation: added a structured review schema and direct
  renderer assertions.
- New test: `tests/test_product_boundary_contract.py`.
- Other surfaces: browser output, examples, metadata and translated pages may
  have the same bypass and remain scheduled for the website phase.

## 30 August 2026: declared facts were treated as machine authority

- Initial assumption: separating code patterns from user-declared facts was
  sufficient to keep the product within an evidence-preparation role.
- New evidence: public adapters converted declared facts into obligations,
  legal-tier indications and outside-scope candidates.
- Changed conclusion: declared facts are review evidence, not authorisation for
  Regula to complete the legal decision.
- Effect on implementation: public schema 2.0 preserves declared, missing and
  contradictory context while setting `human_decision` to null.
- New test: the public context-evaluation contract rejects all internal outcome
  fields.
- Other surfaces: browser decision code and VS Code output may have the same
  defect and remain open.

## 30 August 2026: conformity layout and conformity authority are separable

- Initial assumption: preventing automated conformity would require removing
  the full article-organised pack.
- New evidence: the file layout is useful for review evidence, while the
  readiness, duty, deadline and decision fields are the unsafe authority.
- Changed conclusion: preserve the layout and integrity records, remove the
  legal outcome and leave human decisions empty.
- Effect on implementation: active pack content is now observation-centred and
  the declaration is an uncompleted review template.
- New test: a fully declared context cannot produce readiness, attached duties
  or a pre-filled conformity decision.
- Other surfaces: SME scaffolds and older generated examples require the same
  check.

## 30 August 2026: locked writes still need dirty-key merge semantics

- Initial assumption: re-reading the on-disk cache under an exclusive lock and
  merging the current in-memory mapping would prevent lost updates.
- New evidence: an instance loaded before another writer could retain stale
  values for keys it never changed, then overwrite the other writer while
  flushing its full snapshot.
- Changed conclusion: locking controls timing, but does not establish which
  values the current instance owns.
- Effect on implementation: each cache instance now records dirty keys and
  merges only those keys under the lock before atomic replacement.
- New test: two preloaded writers update different existing entries, plus two
  separate processes flush together and both updates survive.
- Other surfaces: other local JSON stores may have the same stale-snapshot
  pattern and should be assessed when their findings enter scope.

## 30 August 2026: a version prefix did not make sharing lossless

- Initial assumption: the existing version 3 share format and round-trip test
  indicated that answer-state preservation had already been implemented.
- New evidence: the test populated every answer. Production encoding mapped an
  absent answer and explicit uncertainty to the same character, then decoding
  padded all missing positions with that character.
- Changed conclusion: a complete-answer round trip did not test the evidence
  state whose preservation mattered.
- Effect on implementation: version 4 stores one explicit state per current
  question and rejects absent state fields rather than manufacturing answers.
- New test: partial, early-exit, explicit uncertainty, contradiction, malformed,
  unsupported, legacy and production-flow controls now supplement the complete
  case.
- Other surfaces: any compact or positional evidence format needs negative
  controls for omitted fields, not only fully populated examples.

## 30 August 2026: a denylist was not an MCP authority boundary

- Initial assumption: the existing MCP path rejection was an incomplete but
  usable base for a workspace restriction.
- New evidence: it rejected selected system roots but authorised every other
  readable path; a temporary project was also rejected merely because it sat
  below `/tmp`.
- Changed conclusion: the explicit workspace is the positive capability. A
  system-root list may reject dangerously broad roots, but cannot decide which
  child paths an MCP client may read.
- Effect on implementation: startup now requires one workspace root and every
  path tool applies lexical and resolved containment beneath it.
- New test: existing out-of-workspace targets, traversal-shaped paths,
  symlink escapes, secret-shaped targets and explicit temporary workspaces.
- Other surfaces: REST already had positive containment, but its root remains
  the launch directory rather than a separately named capability.

## 30 August 2026: model output safety required removing publication authority

- Initial assumption: stronger prompt wording and output filtering might be
  sufficient for the weekly digest.
- New evidence: the job held repository write permission and pushed the model
  text directly, so any prompt or validator defect retained branch authority.
- Changed conclusion: validation is defence in depth; the decisive control is
  that generated text cannot write to the branch.
- Effect on implementation: read-only permissions, no checkout credentials,
  an exact known-issue schema, inert Markdown rendering and a job-summary draft
  requiring human review.
- New test: planted sensitive values, untrusted instruction boundaries,
  unknown issue references, category mismatches, extra fields and workflow
  source assertions.
- Other surfaces: any future model workflow should be reviewed first for its
  downstream authority, before prompt quality.

## 30 August 2026: metadata can overrule qualified page copy

- Initial assumption: correcting visible headings and result copy would align
  the public product boundary.
- New evidence: social-image alternative text and structured descriptions
  still presented Regula as a compliance tool after visible copy was qualified.
- Changed conclusion: metadata is a determination-capable output surface.
- Effect on implementation: metadata, social previews and structured data were
  added to the semantic inventory and corrected across supported pages.
- New test: public-claim and determination controls include metadata forms.
- Other surfaces: live social-preview caches remain external and unverified.

## 30 August 2026: generated-page drift must be fixed at the source

- Initial assumption: the five mismatched region pages could be reconciled as
  isolated generated-output changes.
- New evidence: every mismatch traced to the shared template or its source
  record, so direct page edits would be overwritten.
- Changed conclusion: generator integrity is the controlling boundary.
- Effect on implementation: changed the template and source records, then
  regenerated all five pages.
- New test: site integrity requires byte-identical generator output.
- Other surfaces: two hand-maintained region exemptions remain explicit debt.

## 30 August 2026: a correct implementation can remain unreproducible in Git

- Initial assumption: session-created files could be staged explicitly after
  review without touching pre-existing dirty work.
- New evidence: `.git/index` is read-only for both sandboxed and approved
  escalated commands.
- Changed conclusion: the working-tree implementation can be tested, but the
  Git-based source inventory cannot include those files in this environment.
- Effect on implementation: retained the files untracked, recorded exact
  provenance and left the gate red.
- New test: the existing tracked-input contributor check exposes the condition.
- Other surfaces: generators and public inventories that enumerate only
  tracked files must be rerun after owner-controlled staging.

## 30 August 2026: current screenshots are evidence, not decoration

- Initial assumption: a file URL could provide visual verification when local
  serving was unavailable.
- New evidence: loopback binding failed with `PermissionError`, and the browser
  daemon could not create session state because its storage was read-only.
- Changed conclusion: source and DOM checks do not substitute for current
  rendered visual, keyboard or assistive-technology evidence.
- Effect on implementation: website status is limited to local source review;
  no accessibility-conformance or visual acceptance claim is made.
- New test: no substitute test was invented. Current browser capture remains a
  named external entry condition.
- Other surfaces: print and screen-reader behaviour remain unverified.
