# Pinned external-corpus diagnostic — 26 August 2026

## Conclusion

Regula produced byte-stable result content across two clean repetitions of all
18 scan variants. The predeclared diagnostic assertions improved from 6/13 to
11/13 after error-led rule changes, while the frozen manifest stayed identical.
That is evidence of repeatable execution and useful regression discovery. It
is **not** an accuracy, legal-validity, or compliance result.

Two predeclared probes still fail and remain in the corpus:

- `private-gpt` emits no limited-risk/transparency indicator in the tested
  snapshot and default configuration;
- `proctoring-ai`, even with education declared, emits no high-risk indicator.

These are credible blind-spot hypotheses. Calling them false negatives would
require context-complete, independent annotation under the multi-annotator
protocol. The manifest was not edited to make the final result look better.

## What was tested

The purposive sample contains 13 public repositories at exact 40-character
commits and 18 configurations:

| Stratum | Exact project snapshots | Diagnostic purpose |
|---|---|---|
| Horizontal infrastructure controls | [OpenAI Python](https://github.com/openai/openai-python), [Ollama](https://github.com/ollama/ollama), [llama.cpp](https://github.com/ggml-org/llama.cpp), [Fairlearn](https://github.com/fairlearn/fairlearn) | Expose domain escalation caused by generic AI, evaluation, runtime or security vocabulary |
| General capability probes | [CrewAI](https://github.com/crewAIInc/crewAI), [private-gpt](https://github.com/zylon-ai/private-gpt), [OpenHands](https://github.com/OpenHands/OpenHands), [ComfyUI](https://github.com/Comfy-Org/ComfyUI) | Exercise autonomy and user-facing generated-content indicators without asserting legal scope |
| Documented decision-support probes | [AI Recruitment Agent](https://github.com/Ancastal/AI-Recruitment-Agent), [Credit Scoring](https://github.com/Machine-Learning-in-Credit-Scoring/Credit-Scoring), [Proctoring-AI](https://github.com/vardanagarwal/Proctoring-AI), [MedTriage Agentic AI](https://github.com/bharath2957s/MedTriage-Agentic-AI), [face-recognition attendance](https://github.com/amlanmohanty1/face-recognition-attendance-management-system-with-PowerBI-dashboard) | Compare undeclared purpose with an explicitly declared employment, finance, education, medical or biometric scan context |

The exact commits, recorded SPDX licence declarations, documented capability,
domains and expectations are in
[`benchmarks/external/manifest.v1.json`](../benchmarks/external/manifest.v1.json).
A recorded licence identifier permits transparent corpus review; it is not a
legal opinion about every file or use.

## Safety and repeatability controls

The runner:

1. validates the entire manifest before network access;
2. initialises an empty repository and fetches only the pinned commit;
3. verifies the checked-out `HEAD` and never imports, installs, builds or runs
   target code;
4. uses isolated scan cache and audit directories for each repetition;
5. stores paths and finding metadata, not third-party source excerpts;
6. records discovered, eligible, scanned and unsupported counts plus explicit
   `completed` or `completed_with_skips` status;
7. hashes the manifest, scan configuration, evaluator, codebook, protocol,
   ruleset and the complete scanner/reference source set.

This follows the verification/validation distinction in the [NIST AI RMF
Measure Playbook](https://airc.nist.gov/airmf-resources/playbook/measure/) and
the separation principle in [NIST AI Technology
Evaluation](https://pages.nist.gov/ai-technology-evaluation/). Those sources
inform the design; they do not validate Regula. The public corpus cannot be
sequestered from its developer, so an independent held-out study remains
necessary.

## Frozen before/after result

The manifest digest was identical in both runs:
`4f7f75f998c9edc679a31e60d36d51afee0465ad4d99c1140e50b1c90b9b3ac3`.

A final clean-acquisition rerun of the candidate tree at 16:47 UTC on
26 August reproduced the correction-run totals: 13 repositories, 18 variants,
36 repetitions, 18/18 byte-repeatable variants, 26 fully completed runs,
10 completed-with-skips runs, and 11/13 predeclared assertions. Its provenance
record covers 145 scanner/reference source files with digest
`6bc4984dc3f40b005ed8b0822c218f39f9834ea1b7a3db9c4b0f9db595fd21ed`;
the evaluator digest is
`6e982483c4b45017006186821015b2d247dc8f48e545ed7a65ffbbbfab3427ad`.
The record truthfully marks the tracked worktree dirty because it evaluated the
candidate before commit; these complete source digests, rather than the parent
commit alone, identify what ran.

| Observation | Baseline | Error-led correction run |
|---|---:|---:|
| Repositories / variants / clean runs | 13 / 18 / 36 | 13 / 18 / 36 |
| Byte-repeatable variants | 18/18 | 18/18 |
| Fully completed runs | 26/36 | 26/36 |
| Completed-with-skips runs | 10/36 | 10/36 |
| Predeclared assertions passed | 6/13 | 11/13 |
| Predeclared assertions failed | 7/13 | 2/13 |

The 11/13 fraction is **not** precision, recall, pass rate, or a product score.
The assertions are heterogeneous diagnostic probes over a purposive sample,
not exhaustive independently adjudicated labels.

### Changes supported by the frozen comparison

- A Go race-detector implementation in Ollama stopped producing a prohibited
  biometric inference indicator after the rule was restricted to biometric
  context.
- Cross-language command/tool execution in OpenHands began producing autonomy
  review indicators.
- Explicit employment, finance and biometric scan context began surfacing
  high-risk review indicators in the recruitment, credit and attendance
  probes.
- Broad face/speaker/identity vocabulary stopped escalating CrewAI,
  private-gpt, OpenHands and ComfyUI to high risk in the tested default paths.

These are corpus-specific observations. They support keeping the changes and
adding regressions; they do not establish improvement on an unseen target
population.

### What completion actually means

Across both result sets, 26 of 36 repetitions were fully completed and 10 were
`completed_with_skips`. The five affected variants each repeated twice. Large
unsupported-language populations are explicit rather than silently treated as
clean. For example, the CrewAI snapshot contained 26,856 discovered files,
only 919 eligible files and 25,537 unsupported files under the declared scan
population. llama.cpp had 3,212 discovered files, 1,125 eligible/scanned files,
1,885 unsupported files and three recorded skips.

Observed local wall times ranged from sub-second small-project scans to roughly
211 seconds per llama.cpp repetition. These are environment- and
snapshot-specific diagnostic timings, not performance guarantees.

## What this cannot establish

- No exhaustive independent labels exist, so precision, recall, F1, MCC,
  calibration and legal correctness are unavailable.
- Project README capability descriptions are selection evidence, not legal
  scope or finding-level ground truth.
- The sample is purposive, not random or representative of GitHub, a customer
  population, languages, sectors or repository sizes.
- Two repetitions establish deterministic content under the tested conditions,
  not cross-platform reproducibility or absence of nondeterministic defects.
- Static source observations cannot establish intended purpose, territorial
  scope, operator role, deployment impact, exceptions or operated controls.
- A passed negative control does not prove specificity; a passed capability
  probe does not prove that every emitted finding is correct.

## Defensible next validation

The next claim-bearing study must use exact licensed snapshots outside the
development corpus, project-held-out and chronological splits, context-complete
annotation units, independent blinded reviewers, a `not_assessable` outcome,
retained disagreements, inter-rater reliability with intervals, and integer
confusion counts before derived metrics. The preregistered method is
[`benchmarks/MULTI_ANNOTATOR_PROTOCOL.md`](../benchmarks/MULTI_ANNOTATOR_PROTOCOL.md).

Until that study exists, the defensible product claim is narrower: Regula is a
repeatable source-code indicator and evidence-scaffolding tool that exposed and
helped correct concrete rule failures on this pinned diagnostic sample.
