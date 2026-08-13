# CI self-scan root-cause record

**Date:** 2026-08-13

**Pull request:** `50`

## Symptom

The `Regula AI Governance Scan` workflow failed with two prohibited-practice
findings after the decision-kernel branch was published. The findings pointed
to `site/assess/decision-adapters.js` and
`site/assess/decision-model.js`.

## Direct cause

The self-scan matched the literal Article 5 descriptions carried by the
browser's regulatory decision data. Those files describe rules and map
questionnaire facts; they do not implement the practices described by the
rules. The generated model and adapter did not yet carry the reasoned
`regula-ignore` annotation already used by other rule, template, and test-data
files in this repository.

The workflow behaved correctly for its inputs: `fail-on-prohibited` was true,
the scan completed, SARIF was uploaded, and the final gate returned exit 2.
The defect was in self-scan classification scope, not the failure threshold.

## Correction

- The decision-model generator emits a file-level, reasoned suppression for
  generated regulatory rule descriptions.
- The questionnaire adapter carries an equivalent reasoned suppression for its
  regulatory mapping data.
- The browser contract test asserts that both markers exist, so regeneration or
  editing cannot silently remove the rationale.
- The workflow threshold remains unchanged. No rule text, finding, assertion,
  or Article 5 gate was deleted or weakened.

## Verification

The JavaScript browser contract reported 64 of 64 assertions passing. The
related Python set reported 32 passes. A clean tracked-file snapshot, equivalent
to a fresh Actions checkout rather than the developer tree's ignored VS Code
test download, completed with return code 0: prohibited 0, high risk 0,
suppressed 22, skipped 0, completion status `completed`.

The ordinary developer tree self-scan also exposed why a clean checkout is the
right comparison: an ignored `.vscode-test` download contributed oversized
files, three agent-autonomy observations, and one high-risk observation. Those
third-party, ignored runtime files do not exist in GitHub's fresh checkout and
must not be confused with the tracked-tree regression.

## Residual risk and falsifier

The correction would be falsified if the rerun workflow still reports either
generated browser data file as active, if either rationale disappears after
regeneration, or if a genuine implementation in another file becomes
suppressed. Generated-data suppressions must remain narrow, reasoned, visible
to the audit-suppression command, and covered by the clean-snapshot self-scan.
