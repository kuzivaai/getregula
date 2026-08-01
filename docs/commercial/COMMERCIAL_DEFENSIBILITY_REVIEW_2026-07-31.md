# Commercial defensibility review — 2026-07-31

## Erratum — 2026-08-01: public release identity

**CONTRADICTED:** the review below described `regula-ai==1.7.4` as the current
public package. A no-cache PyPI JSON response retrieved 2026-08-01 at
09:16:26 UTC, `pip index versions regula-ai`, the downloaded
`regula_ai-1.9.0-py3-none-any.whl`, and local tag `v1.9.0` all identify 1.9.0
as current. The downloaded wheel SHA-256 is
`01cde674270adcf08acedf1b79e003c6f083c464944cf158582a14afde93cff3` and its
METADATA says `Version: 1.9.0`; tag `v1.9.0` resolves to
`96497430917cfdbe243cd942bb9e0f9448111607`.

The commercial_v1 public-package operational findings remain **VERSION_BOUND**
to the wheel actually tested, 1.7.4. commercial_v1 did not establish the
operational readiness of published 1.9.0. The 1.9.0 wheel still carries the
disputed classification, network, DPA, runtime, and auditor-completeness copy
quoted in the claim register. Frozen corpora, results, hashes, local 1.9.0
Candidate A/B results, and the STOP decision are unchanged.

## Executive decision

`OVERALL_DECISION: STOP`. No evaluated capability justifies a customer pilot.
The frozen local product missed 40/40 constructed Candidate A positives and
40/40 Candidate B positives, while transparent baselines found 40/40 in both.
Candidate C lacks human ground truth. Public claims materially exceed the
measured boundary. A future result can overturn this decision, but present
evidence cannot.

## Verdict fields

| Field | Verdict |
|---|---|
| TECHNICAL_EVIDENCE | **FAILED** |
| COMPARATIVE_ADVANTAGE | **NOT_DEMONSTRATED** |
| PUBLIC_CLAIM_INTEGRITY | **FAIL** |
| REGULATORY_CURRENCY | **PARTIAL** |
| OPERATIONAL_READINESS | **FAIL** |
| DEMAND_EVIDENCE | **UNVALIDATED** |
| OVERALL_DECISION | **STOP** |

These are internal decision labels, not legal or scientific standards.

## Scope and frozen identities

MEASURED against local product commit
`94efa9e6ad9173fb888822543c247195078b0220`, Regula 1.9.0, Python 3.12.3,
Linux 6.6.87.2-microsoft-standard-WSL2. Preregistration commit: `5bd2112`.
Protocol SHA-256:
`58c935903b5832eb7b8232116f6dc182b97708a89b5d3070f8b856ec9272d8c4`.
Public package: `regula-ai==1.7.4`, wheel SHA-256
`36e4a6b3b91dd2989a9163310fed1e35559e6fc0697c93a6bd042e6514ab3940`.
Local wheel: 1.9.0, SHA-256
`1282b69e64c863989346fbaf9e5c8c72fdcf5a0357f6e3b75b3bad8c02a36cd6`.

The 12 exact repository commits and acquisition hashes are in
`manifest.json` and the retained external `acquisition.json`. They comprise
microsoft/markitdown, open-webui/open-webui, browser-use/browser-use,
modelcontextprotocol/python-sdk, pallets/click, pallets/itsdangerous,
python-attrs/attrs, astral-sh/ruff, prettier/prettier, axios/axios,
sindresorhus/ky and vitest-dev/vitest. This is a purposive convenience frame,
not a representative sample.

## Deviations and integrity

Before results, `84e0118` fixed the verifier's conflation of the mutable
protocol tree with the detached product tree. After the frozen acquisition
failed on `sindresorhus/ky`'s lowercase root `license`, the before-fix exit 1
was retained and `056bcf2` added a class-wide case-insensitive runtime
acquirer outside the frozen input set. Frozen product rules, corpus, labels,
thresholds and `acquire.py` were not changed. The corrected acquisition found
12/12 repositories and 12/12 licence records.

## Results

The unit is one constructed observable decision. Labels are truth by
construction, not human judgements. Forty positives and forty negatives were
run per candidate and tool, twice from fresh output directories. Results were
identical after normalisation. Transformation families are correlated, so the
Wilson intervals below are descriptive and cannot establish external
accuracy.

| Tool/job | TP | FP | FN | TN | Precision (95% Wilson) | Recall (95% Wilson) |
|---|---:|---:|---:|---:|---|---|
| local 1.9.0 / A | 0 | 0 | 40 | 40 | undefined, 0/0 | 0/40 = 0.000 (0.000–0.0876) |
| naive imports / A | 40 | 4 | 0 | 36 | 40/44 = 0.909 (0.788–0.964) | 40/40 = 1.000 (0.912–1.000) |
| local 1.9.0 / B | 0 | 0 | 40 | 40 | undefined, 0/0 | 0/40 = 0.000 (0.000–0.0876) |
| naive markup / B | 40 | 0 | 0 | 40 | 40/40 = 1.000 (0.912–1.000) | 40/40 = 1.000 (0.912–1.000) |

Exact reproduction:

```bash
python3 benchmarks/commercial_v1/run.py --manifest benchmarks/commercial_v1/manifest.json --corpus benchmarks/commercial_v1/corpus.json --output OUT --tool naive
python3 benchmarks/commercial_v1/run.py --manifest benchmarks/commercial_v1/manifest.json --corpus benchmarks/commercial_v1/corpus.json --output OUT --tool local_head --executable python3
python3 benchmarks/commercial_v1/normalise.py --input OUT/results.json --output OUT/normalised.json
python3 benchmarks/commercial_v1/score.py --labels benchmarks/commercial_v1/labels.json --output SCORE --result OUT1/results.json --result OUT2/results.json --result OUT3/results.json --result OUT4/results.json
```

Raw-output root: `/tmp/regula-commercial-20260731.Inq4k2`; the score and
repository-operation records needed for the stated fractions are committed in
`benchmarks/commercial_v1/results/raw/`, with the compact result at
`benchmarks/commercial_v1/results/summary.json`. The full score output SHA-256 is
`bd8191a1ec9f19bfc408fc770fd40409da091b6a218308ae0014200a6df20a3e`.

Repository operational execution retained 12/12 outcomes per tool. Local
1.9.0 and public 1.7.4 each returned exit 0 for 9/12 and exit 1 for 3/12
(open-webui, python-sdk and prettier). Their second runs repeated every exit,
stdout hash and stderr hash for 12/12; wall time differed. compliance-agent
0.5.0 default and configured modes and AIR Blackbox 1.13.2 returned exit 0 for
12/12. This proves reachability only: no equivalent source-event adapter or
independent repository labels exist, so competitor accuracy is UNTESTABLE.
Complior's executable identity remained unresolved and was not replaced.

The documented journey on one active `openai` import/use fixture and one
negative arithmetic fixture returned empty data for both local and public
versions: observed positive findings 0/1 and negative false alerts 0/1.
Unicode/space paths exited 0 for both. Local 1.9.0 generated a nine-file
manifest and strict verification exited 0. Public 1.7.4 generated a legacy
manifest, non-strict verification exited 0, and strict verification exited 2
because the manifest did not declare `format=regula.evidence.v1`.

Network behaviour is UNVERIFIED. `unshare -n` failed with “Operation not
permitted”. The frozen Python socket-denial control replaced `socket.socket`
too early and caused `ssl` import to fail, so it did not execute the scanner.
Source inspection and ordinary offline success do not prove zero calls. Peak
memory is NOT_MEASURED because the available value is cumulative child RSS.

## Failure classes

After execution, the 80 local synthetic false negatives were classified as a
source-event adapter/product-output mismatch: the default `check` path emitted
no source-linked findings satisfying the frozen buyer-job definition. The
active OpenAI control reproduced the absence outside generated cases. Three
repository non-zero exits per Regula version are operational failures retained
in raw stderr. Candidate C is non-observable without declared context and
independent human annotation, not a measured classifier failure.

## Legal and regulatory boundary

PRIMARY-SOURCE VERIFIED on 2026-07-31: Regulation (EU) 2026/1744 entered into
force on 27 July 2026. Its transition moves relevant Annex III rules to
2 December 2027 and Annex I product-system rules to 2 August 2028; the legacy
Article 50(2) transition is 2 December 2026. Article 6 depends on intended
purpose and context. Article 50 source-code absence is not proof of violation.
Exact official sources and limitations are in the research register.

prEN 18228, prEN 18229-1 and prEN 18282 were observed in draft/enquiry stages;
EN 18286 was at formal vote in reviewed material. ISO/IEC 42005 and 42006 are
published international standards, but that does not create Article 40
presumption of conformity. No exact Official Journal citation for these
standards was established; any harmonisation claim remains UNVERIFIED.

## Commercial interpretation

The strongest proposed wedge was local AI inventory plus reproducible
evidence. Its strongest supporting fact is that 1.9.0 can generate and
strictly verify a local evidence manifest. The stronger contrary evidence is
that the same journey put zero observed findings into the pack and missed
40/40 constructed inventory positives; a small transparent import baseline
found 40/40. Evidence packaging without reliable evidence discovery is not a
defensible capability.

Demand is UNVALIDATED: no interviews, representative customer repositories,
design-partner commitments or payments were produced. Competitor availability
and regulatory workload are problem signals at most, not willingness to pay.
The maintenance burden includes regulatory currency, multilingual claims,
package/release divergence, comparator evolution and evidence-format support.

Economic reasoning is assumption-bound. At any price, a pilot that requires a
consultant to reconstruct missed inventory manually has negative product
leverage unless the tool saves more review time than it creates. No measured
customer time or cost exists, so no market price or ROI is claimed.

The decision would be falsified by a prospectively sampled, independently labelled
repository study in which a frozen Regula version clears the preregistered
lower bounds, beats the transparent baseline without a material regression,
reproduces its evidence packs, and has corrected public claims. The next
bounded unit is not a feature build: correct high-consequence public and PyPI
claims, publish no new accuracy claim, and design an owner-approved independent
annotation study before reconsidering a pilot.

## Successor prompt

> Work only on the bounded claim-integrity unit derived from commercial_v1.
> Recompute state; read the ledger and 2026-07-31 commercial review. Correct
> every active high-consequence README, TRUST, SECURITY, package-description
> and translated-site claim identified in the public claim register. Preserve
> the distinction between code-observable evidence and legal determination;
> remove zero-network, universal reproducibility and unqualified
> classification claims unless new mechanical evidence supports them. Do not
> change detector rules, benchmark labels or commercial_v1 results. Add
> exact-surface tests, run all repository gates, update the ledger, and stop
> before push, publication or deployment.

## Final adversarial review

An independent read-only reviewer received only the complete diff, protocol,
raw summary, test output, claim register and ledger. The reviewer found one
HIGH, two MEDIUM and two LOW defects. Reproduction confirmed all five. The
HIGH correction removes an invalid inference from A/B misses to the separate
legal-classification claim. One MEDIUM is closed by committing the raw score
and repository records and adding a summary-to-raw regression check. The other
MEDIUM remains a limitation: `gate.py` evaluates a supplied external-evidence
record and its conjunction test cannot prove those booleans were derived from
raw artefacts. No claim-ready verdict relies on that path here; both candidates
fail their measured recall gate. The LOW fixes rename hash equality accurately
and classify the observed >30-second runs as contradiction of the unqualified
bound. The open-alert wording now distinguishes alerts from confirmed
vulnerabilities. No arithmetic error, silent ledger closure, suppressed failed
run or hidden human-label substitution was found.

## Final verification state

MEASURED on the quiescent working tree after review disposition. The custom
runner exited 0: `1386 passed, 0 failed, 0 skipped (1071 test functions)`.
Full pytest exited 1 after 2,011.63 seconds: `6 failed, 2633 passed`; all six
failures independently report the same count-integrity condition, live
collection 2,639 versus public canonical 2,628. The session contract forbids
editing public website claims, so `site_facts.py` and
`cascade_count.py --apply` were not used to make those surfaces green. An
attempt to consolidate the 11 new checks into an existing test was fully
reverted because it would conceal the denominator change.

Fast gates: `site_integrity`, `build_recall_artefact --check`,
`build_gap_demo --check` and `check_selfref_sourcing --control-only` exited 0.
`claim_auditor --verify-facts` and `cascade_count --check` exited 1 on the same
2,628/2,639 count mismatch. The separately required merge blocker remained
exit 1. Commercial integrity exited 0 with 20 repository inputs verified.
Self-test exited 0 (6/6). Restricted doctor exited 1 solely because the sandbox
made `/home/mkuziva/.regula/audit` unwritable; the exact unrestricted control
exited 0 with 8 passed and 4 info. These are separate environment-specific
results, not one green run.

Because required gates are red, the results commit is evidence-complete but
not release-ready. Resolving the count mismatch requires an owner-authorised
public-claim cascade or a separately justified removal of tests; neither is
within this session's permitted scope.
