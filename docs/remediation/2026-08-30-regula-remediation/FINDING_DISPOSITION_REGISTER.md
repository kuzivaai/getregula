# Finding disposition register

Date: 30 August 2026

The controlling, machine-readable register is
`FINDING_DISPOSITION_REGISTER.csv` in this directory. It records every required
finding, its current disposition, reproduction evidence, changed paths,
regression control, remaining limitation and closure evidence.

## Summary

- BLOCKED: F-002, F-011.
- DEFERRED: F-008, F-009.
- PARTIALLY FIXED: F-007, F-024.
- FIXED IN TESTED OR SOURCE SCOPE: F-003, F-004, F-005, F-013, F-014,
  F-016 through F-023, F-025 through F-027, C-003 and PQA-001 through
  PQA-003.

The word fixed is always bounded by the evidence and remaining-limitation
columns in the CSV. It is not a claim of legal approval, representative
detector validity, production security, accessibility conformance or release
readiness.
