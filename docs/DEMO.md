# A demonstration you can run live

**Written 2026-08-17; last reviewed 2026-08-25.** Every command below was executed in the order shown, from
a clean environment, against a public repository pinned to a commit, using a
wheel built from this tree and installed from the file. Every timing is measured
rather than estimated, and the command that reproduces each one is beside it.

This is not a script that flatters the tool. It runs on a repository selected
before the result was known, shows what the scan declined to read, and states
what the tool does not know. A defect belongs in the issue tracker with a
reproduction, not in a rewrite of the evidence.

---

## What this demonstration is for

The argument is one sentence: **Regula tells you what it cannot determine, and
then lets you determine it.** Everything else on this page exists to show that
sentence happening.

A tool that prints a compliance score from a code scan is guessing, because
applicability under the EU AI Act depends on intended purpose, operator role and
territorial scope, none of which is in the code. Regula reports
`insufficient_information` and names the facts it needs. You supply them. The
decision moves, and the output records that **you** supplied them.

---

## Before you start

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install regula-ai
regula --version
```

Measured on the built artefact: `regula --version` returns in **0.1s**.

The corpus for this demonstration is a public repository, pinned:

```bash
git clone https://github.com/ageitgey/face_recognition
cd face_recognition
git checkout 9f3061aaeed9a8756d2c970f5dfe066617a8281d
```

That SHA names a commit in **that** repository, not in Regula's. It is pinned
because an unpinned clone measures whatever the default branch happens to be
today and would make the demonstration irreproducible.

Face recognition is chosen deliberately. Biometric identification is the least
ambiguous Annex III category there is, so if the tool says nothing useful here
that is the most damaging result available to it.

---

## Step 1. Ask, and be told what is not known

```bash
regula check . --scope all
```

Measured: **0.3s**, exit 0, on 6 scanned files.

```
Decision: insufficient_information
Model: 2026-08-19.1
Jurisdiction: eu
Rule resolution: unresolved
Facts needed to resolve the next decision: 2
  - is_ai_system: Does the subject meet the governing law's definition of an AI system or regulated automated technology?  [answering this advances 1 provision]
  - jurisdiction_in_scope: Does this jurisdiction's territorial and operator scope apply?  [answering this advances 1 provision]
  Declare one with: regula check . --fact is_ai_system=yes|no|unknown|not_applicable

Detector observations (not legal facts):
  Files scanned:      6
  High-risk:          3

  INFO: 23 code file(s) in 1 skipped director(ies) were not scanned
        examples
        These directory names are excluded by default (examples, tests caches, vendored code).
        To scan one, pass it as the path: regula check <dir>
```

**Three things to point at, in this order.**

1. **No verdict.** There is no risk tier, no compliance score and no percentage,
   because two facts required to reach one are unresolved and nothing in the code
   supplies them.
2. **The scan says what it did not read.** Six files read, twenty-three code
   files in `examples/` not read, named. The counts above are drawn from the six.
   A tool that printed "Files scanned: 6" and stopped would let a reader hear
   "this repository has three high-risk indicators" when the honest statement is
   "the six files I read have three".
3. **The list is ordered by leverage, and says so.** `[answering this advances 1
   provision]` is the decision model's own figure, not a heuristic.

Without `--scope all` the same command excludes non-production files and reports
zero findings in production scope, under an explicit line saying so:
`This is not evidence that the project contains no AI.` Show that too if you
have time; it is the honest form of a clean result.

---

## Step 2. Supply what the tool cannot see

The vocabulary is not documentation, it is the model:

```bash
regula check . --list-facts
```

Measured: **0.1s**. Prints every fact id the running decision model defines, with
its question. At model `2026-08-19.1` that is **73** ids across three
jurisdictions.

Two routes answer them. The questionnaire:

```bash
regula assess --answers yes,yes,no,yes,no --save-facts
```

Measured: **0.1s**, exit 0.

```
Declared facts written to .regula/facts.json
3 of your answers map to a fact the decision model uses; 3 fact(s) now in the store:
  - eu_annex_iii_use = yes
  - is_ai_system = yes
  - jurisdiction_in_scope = yes
2 answer(s) were NOT written, and why:
  - non_eu_provider: the model has no fact for where the provider is established;
    jurisdiction_in_scope and role_provider are different questions
  - prohibited: one yes/no over seven separate Article 5 practices; the model has
    a distinct fact for each and a single yes does not say which
These are your declarations. Regula establishes none of them.
Next: regula check .   (it now reads them)
```

**Point at the refusal, not the acceptance.** Three of five answers were written
and two were not, with the reason. A questionnaire that mapped `prohibited=yes`
onto one Article 5 fact would be inventing a fact on your behalf.

Or declare a fact directly, for one run:

```bash
regula check . --scope all --fact role_provider=yes --fact eu_significant_risk=yes
```

`unknown` is one of the four states and is never read as `no`. A fact you have
not answered is absent, which is a different thing again, and the model treats
all three differently.

---

## Step 3. Watch the decision move

```bash
regula check . --scope all
```

Measured: **0.1s**. The two facts from step 1 are gone from the list, and the
declarations are printed with their provenance:

```
Declared facts: 3 (asserted by a person, not established by Regula)
  - eu_annex_iii_use = yes  [user_declaration via cli:assess at 2026-08-17T...]
      asked: Does your product do any of the following? a) Screen, rank, or filter
             job candidates or CVs b) ... i) Used in administration of justice ...
```

With the two facts the questionnaire does not ask, the decision resolves:

```bash
regula check . --scope all --fact role_provider=yes --fact eu_significant_risk=yes
```

Measured: **0.1s**.

```
Decision: indication
Rule resolution: partial
  - high_risk_candidate: Regulation (EU) 2024/1689, Article 6(2)-(3) and Annex III

Declared facts: 5 (asserted by a person, not established by Regula)
```

**This is the moment the demonstration exists for.** `indication`, not
`determination`; `high_risk_candidate`, not `high-risk`; and five facts, each
recorded with who declared it, through which command, in answer to which
question, and when.

**Say the limit out loud.** `assess` asks six questions, three of which map to a
fact. The model needs five facts to reach this indication, so the questionnaire
alone cannot get there and `--fact` supplied `role_provider` and
`eu_significant_risk`. That is a gap in the questionnaire, it is recorded, and it
is better said by you than found by them.

---

## Step 4. The artefact they keep

```bash
regula evidence-pack --project .
```

Measured: **0.8s**. Nine files with SHA-256 integrity hashes. `00-summary.md`
opens with:

```
## Decision status
**Kernel result:** `insufficient_information`
...
No legal classification, article duty, readiness percentage, or effort estimate
is emitted because the generator received no sourced decision facts.

## Scan coverage
**Files read:** 8
**Not read:** 23 code file(s) in 1 excluded director(ies): examples.
... **Observations below are drawn only from the files read.**
```

The reliance gate is first and the coverage statement is before any count. This
is the one artefact that gets forwarded to somebody who never saw the tool run,
so the order it is written in is the whole of what that reader gets.

SARIF, for a pipeline rather than a person:

```bash
regula check . --scope all --format sarif --output findings.sarif
```

Measured: **0.1s**. Valid SARIF 2.1.0 with full paths and partial fingerprints;
it drops into GitHub code scanning unmodified.

---

## How to describe accuracy honestly

Regula has regression evidence, not a validated current accuracy claim.

- The synthetic fixtures are regression tests. They help detect rule and
  runtime-parity regressions, but they are not an independent evaluation and do
  not represent the prevalence, ambiguity or context of real repositories.
- No independently annotated, representative, project-held-out real-world
  evaluation has been completed. Regula therefore has no current real-world
  precision, recall or accuracy estimate.
- A clean scan is not evidence of compliance. Applicability depends on legal and
  operational facts that source code may not contain, so Regula can abstain and
  request those facts instead of manufacturing a verdict.
- The preregistered path to publishable evidence is
  [`benchmarks/MULTI_ANNOTATOR_PROTOCOL.md`](../benchmarks/MULTI_ANNOTATOR_PROTOCOL.md).
  It requires independent annotation, preserved disagreements, project-held-out
  evaluation, uncertainty intervals and explicit missingness before any result
  is described as real-world performance.

Do not present fixture pass counts as real-world accuracy, or interpret a
detector score as a legal-compliance probability.

---

## Reproducing every number on this page

| Claim | Command that re-derives it |
|---|---|
| Timings | Run the commands in order from a clean `HOME` and a fresh `REGULA_CACHE_DIR`. |
| Fact ids the model defines | `regula check . --list-facts` |
| Files read and not read | the `Files scanned` and `INFO: ... not scanned` lines of step 1 |
| Synthetic regression evidence | `python3 scripts/build_recall_artefact.py --check`, then `benchmarks/synthetic/RECALL.json` |
| Accuracy-evidence boundary | `benchmarks/MULTI_ANNOTATOR_PROTOCOL.md` and `docs/RESEARCH_BASIS_2026-08-25.md` |
| That every command and flag above exists | `python3 -m pytest tests/test_demo_doc.py` |

**What no guard on this page can cover.** The timings and the third-party output
depend on a clone this repository does not contain, so `tests/test_demo_doc.py`
binds what it can: every `regula` command and every flag used above is checked
against the real argparse registry on every test run, so a renamed flag fails
verification before someone relies on the page. Nothing checks that the timings
still hold; re-run them.

**Second machine, second load.** Every timing here is one run, on one machine, at
one load. The ratios matter more than the absolutes: step 1 is a cold scan and
steps 2 to 5 are warm.
