# Regula claim-scope causality session

Date: 2026-08-05
Time: 195731
Repository: /home/mkuziva/getregula

Objectives:
1. Preserve the prior integrity-cycle evidence.
2. Isolate the causal effect of path-selection policy.
3. Implement only the smallest justified non-launderable gate.

PRODUCT_BUILD: STOP
VENTURE_DECISION: STOP
EXTERNAL_CONTACT: NOT_AUTHORISED
REAL_DATA_COLLECTION: DISABLED

## Authority and initial probe

Default sandbox Git probe: `git_dir_writable=no`, exit 73, read-only file system.

Already authorised unrestricted Git probe: `git_dir_writable=yes`, exit 0.

Initial HEAD: `55e9192d83cab8d5df13102c3f7dff3f1dc0a4c5`.

Initial tree: `1b2476e8e86a0776caef44697f81c513fea4ee05`.

Initial worktree change: untracked `docs/improvement/evidence-2026-08-05/` only.

## Prior evidence verification

The directory exists and its manifest is non-empty. The directory contains 38
files total: 37 files named in the manifest plus `SHA256SUMS.txt`. The manifest
contains 37 entries.

Mandated command:

```console
$ (cd docs/improvement/evidence-2026-08-05 && sha256sum -c SHA256SUMS.txt)
sha256sum: docs/improvement/evidence-2026-08-05/95caef4-claim-auditor.json: No such file or directory
...
sha256sum: WARNING: 37 listed files could not be read
[exit 1]
```

The failure applies to all 37 entries. Each manifest entry includes the
repository-root prefix `docs/improvement/evidence-2026-08-05/`, so evaluating
the manifest from inside that directory resolves a nonexistent nested path.

Read-only diagnostic from the repository root:

```console
$ sha256sum -c docs/improvement/evidence-2026-08-05/SHA256SUMS.txt
37 entries: OK
[exit 0]
```

Complete output: `/tmp/regula-claim-scope-root-hash-check.txt`.

Disposition: the bytes reconcile when the manifest is interpreted from the
repository root, but the exact verification contract in the prompt fails.
Under the explicit stop rule, the evidence directory was preserved unchanged,
nothing was committed, and no causal experiment or implementation began.

## Stop disposition

Authoritative in-repository handover:
`docs/improvement/HANDOVER-CLAIM-SCOPE-2026-08-05-195731.md`.

No file was staged. No commit, copy to Downloads, deletion, product change,
public action, contact, data collection, spend, push, release, or deployment
occurred. The Downloads copy was not attempted because the prompt requires the
handover to be committed before copying, while the evidence failure requires
that nothing be committed.
