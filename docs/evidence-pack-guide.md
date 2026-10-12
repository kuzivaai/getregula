# Evidence packs for contextual review

Regula generates source-code observations and documentation drafts for a human
reviewer. A pack is not a compliance decision, legal opinion or conformity
certificate. Its hashes check file consistency, not whether its contents are
true or sufficient for an applicable obligation.

The layouts below were checked against generated version 2.0.0 output on
16 September 2026. Optional sections depend on the requested features and the
available input. The manifest lists the files actually included.

## Choose the handoff

- `regula evidence-pack . --bundle` creates a review folder and a portable ZIP
  with a standalone hash verifier.
- `regula conform . --zip` creates a contextual review handoff. With no sourced
  decision facts, it keeps applicability unresolved and does not attach article
  duties or emit a readiness score.

Read `00-summary.md` or `00-assessment-summary.json` first, resolve the listed
questions with the accountable owner, and verify each observation against its
source. The current CLI commands start from an empty decision fact set. A saved
assessment does not automatically turn either pack into a resolved decision.

## `regula evidence-pack .`

The implemented generator is [`scripts/evidence_pack.py`](../scripts/evidence_pack.py).
A default run with the optional local evidence available produces:

```text
evidence-pack-PROJECT-DATE/
  00-summary.md
  01-scan-results.json
  02-gap-assessment.json
  03-annex-iv-draft.md
  04-dependency-report.json
  05-audit-trail.json
  06-resolvable-facts.md
  07-risk-decisions.json
  README.md
  manifest.json
```

The summary describes scan coverage and reliance limits. The documentation is
an unverified draft. The audit trail is project-scoped; it does not establish
that every relevant action was recorded. Optional dependency and audit sections
can be absent if their inputs cannot be read.

For a consultant-prepared handoff, the CLI accepts `--client`, `--prepared-by`
and `--engagement-ref`. These fields identify the engagement; they do not
establish the preparer's qualifications or approval.

## `regula conform .`

The implemented generator is [`scripts/conform.py`](../scripts/conform.py).
The default unresolved handoff contains:

```text
conformity-evidence-PROJECT-DATE/
  00-assessment-summary.json
  01-detector-observations/findings.json
  02-unassigned-evidence/evidence.json
  02-unassigned-evidence/audit-trail.json
  03-documentation-draft/annex-iv-draft.md
  04-resolvable-facts.md
  README.md
  manifest.json
```

The name of this command does not establish conformity under Article 43 of
Regulation (EU) 2024/1689. Applicable duties and assessment routes require
contextual legal review, including the current status of any Omnibus amendments.
The pack is a snapshot and does not establish an ongoing Article 72 monitoring
process.

## Verify file consistency

After generation, pass the returned pack path to the verifier:

```bash
regula verify ./PACK_DIRECTORY --strict
regula verify ./PACK_DIRECTORY --strict --format json
```

Exit 0 means the requested integrity checks passed; 1 reports an integrity or
signer failure; 2 reports an invalid input or a strict verification rejection.
The JSON envelope's `exit_code` matches the process exit code. Strict mode does
not require an optional signature or timestamp.

`regula evidence-pack . --bundle` includes a standalone `verify.py`. Extract
the ZIP, enter its pack directory, and run `python3 verify.py` to compare file
hashes without installing Regula. Review the script before executing code
received from another party. Its hash check does not authenticate a signer.

An unsigned pack can be edited together with its manifest. Matching SHA-256
hashes therefore establish internal consistency, not authenticated provenance.
For signer continuity, use `--expect-public-key` with a public key obtained
through a separate trusted channel.

## Repeatability and provenance

Manifests record the tool version, generation time, project name and hashes of
the included files. Generation timestamps and audit history can change between
runs, even when the source tree is unchanged. Complete packs are not promised
to be byte-identical.

Archive the exact reviewed source revision, configuration and rule version
alongside the handoff when repeatability matters. The default evidence pack
manifest alone does not record all those inputs. A reproducible run is still
not validation of a detector finding or legal conclusion.

## Optional runtime evidence

`regula evidence-pack . --runtime my-system` can add `08-runtime-monitor.json`
from application events recorded through Regula's instrumentation. It includes
counts, chain status and session summaries. The application owner controls what
is instrumented, so this is self-attested evidence input relevant to Article 12,
not independent monitoring or proof of complete event capture.

`regula monitor report my-system` reports the share of consequential inference
events marked as human-reviewed. Ordinary reviewed calls do not increase that
share. With no consequential events, the rate is unknown. The metric depends on
truthful instrumentation and does not measure review quality.

## Optional signing and timestamping

`regula conform . --sign` or `regula evidence-pack . --sign` adds an Ed25519
manifest signature. Install the optional signing dependencies from the reviewed
source as described in [installation.md](installation.md). A valid signature
alone does not identify a trusted reviewer or establish professional approval.

`--signing-key PATH` selects a key. Without it, signing uses the configured
`REGULA_SIGNING_KEY` location or creates a local key at `~/.regula/signing.key`.
Keep the private key private and share only the public key for verification.

`--timestamp` implies signing and requests an RFC 3161 timestamp from a remote
Time Stamping Authority. The default endpoint is `https://freetsa.org/tsr`;
`--tsa-url URL` overrides it. This option requires network access.

The verifier distinguishes these timestamp results:

| Status | Meaning |
|---|---|
| `HASH_MATCHED` | The imprint matches; the timestamp signature was not evaluated. |
| `SIGNATURE_VERIFIED` | The signature verifies against the embedded certificate; signer identity is not independently anchored. |
| `CHAIN_VERIFIED` | The signature also chains to the supplied direct issuer anchor and both certificates were valid at the recorded time. |
| `INVALID` | Verification failed. |
| `UNVERIFIABLE` | Required verification dependencies are absent. |

Use `--tsa-trust-anchor PATH` to supply the direct issuer certificate. Regula
performs no revocation checks, intermediate chain building, name-constraint or
policy validation. A timestamp establishes neither the truth of the evidence
nor legal conformity. Use dedicated validation against a maintained trust store
where fuller certificate validation is required.
