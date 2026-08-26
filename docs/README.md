# Regula documentation

Organised by the four [Diátaxis](https://diataxis.fr/) documentation types, so
you can find docs by what you're trying to do — learn, solve a task, look
something up, or understand *why*.

New to Regula? Start with the [Quickstart](QUICKSTART.md), then the
[course](course/README.md). Evaluating without installing anything? Use the
browser [assessment flow](https://getregula.com/assess/).

> Regula is **risk indication, not legal classification**. Findings are flags
> for human review; false positives and negatives occur. See
> [What Regula does not do](what-regula-does-not-do.md).

## Tutorials — learning by doing

Start here if you're new. Guided, step-by-step, first-success paths.

- [Quickstart](QUICKSTART.md) — install and get your first risk indication in one command.
- [Course](course/README.md) — a 10-part path from setup to custom patterns:
  [setup](course/01-setup.md) ·
  [risk classification](course/02-risk-classification.md) ·
  [scanning real code](course/03-scanning-real-code.md) ·
  [compliance gaps](course/04-compliance-gaps.md) ·
  [dependency security](course/05-dependency-security.md) ·
  [AI security patterns](course/06-ai-security-patterns.md) ·
  [CI/CD integration](course/07-cicd-integration.md) ·
  [documentation](course/08-documentation.md) ·
  [framework mapping](course/09-framework-mapping.md) ·
  [custom patterns](course/10-custom-patterns.md).

## How-to guides — solving a specific task

You know what you want to do; these give you the steps.

- [Installation](installation.md) — pipx, uv, and pip; platform notes.
- [Evidence-pack guide](evidence-pack-guide.md) — produce a review-ready evidence bundle for an auditor or assessor.
- [DPV-AIAct export](dpv-aiact-export.md) — emit the risk indication as machine-readable JSON-LD for RDF/GRC tooling.

## Reference — accurate, complete, look-it-up

Dry, factual descriptions. No interpretation.

- [CLI reference](cli-reference.md) — every command and flag.
- [Model card](MODEL_CARD.md) — the detection engine's scope, metrics, and limits.
- [Precision/recall benchmark](benchmarks/PRECISION_RECALL_2026_04.md) — measured precision and recall.
- [Detection Rule Licence](LICENSE.Detection.Rules.md) — the DRL 1.1 terms for the pattern set.
- [Evidence Format v1 spec](spec/regula-evidence-format-v1.md) — the evidence-pack + manifest format.

## Explanation — understanding why

Background, context, and trade-offs.

- [Architecture](architecture.md) — how the scanner and precision layers work.
- [What Regula does not do](what-regula-does-not-do.md) — the honest limits (read this).
- [AI governance context](AI_GOVERNANCE.md) — how Regula fits the wider governance picture.
- [Accessibility](accessibility/README.md) — the site/docs accessibility posture.
- [Trust](TRUST.md) — what's verified, reproducibility, security and privacy posture.
- [Governance](../GOVERNANCE.md) — maintainership, access controls and bus-factor limits.
- [Engineering roadmap](ENGINEERING_ROADMAP.md) — current technical priorities, evidence gates and known unknowns.
- [Evidence review and engineering basis](RESEARCH_BASIS_2026-08-25.md) — source appraisal and research-led implementation order as of 25 August 2026.
- [Versioning and deprecation policy](VERSIONING.md) — what version numbers promise, the public API they cover, and the 1.9.0 realignment record.

---

*Internal review, research, and planning notes are kept outside this
user-facing docs tree and are not part of the published repository.*
