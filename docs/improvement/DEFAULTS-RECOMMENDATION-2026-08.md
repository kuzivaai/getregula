# What `regula check` should do by default

**A decision for the owner. Written 2026-08-17.** Measured at
`ae59cd5d60e230b475fd5fc5f460cfd99337b9fc`, tree
`2c8b99b736079a19e6910b576108f0974250f104`.

**No default was changed in this session.** Section 7 says why.

---

## 0. The recommendation, first

1. **Do not change the domain default.** It buys 6/30 on the synthetic corpus and
   **nothing at all** on three real repositories. Changing it would improve a
   score and change no user's output.
2. **Change the AI-indicator default, but not by removing the gate.** Removing it
   buys 4/30 alone and 13/30 combined on synthetic, and costs 11 extra findings
   across 10,600 real files of which roughly four are clearly real, three
   arguable and four clearly noise. The honest form is not "remove the gate" but
   "when a file matches a high-risk pattern and the AI-indicator gate is what
   suppressed it, say so", the way domain gating already does.
3. **The largest suppressor on real code is neither gate, and nobody was
   measuring it.** `SKIP_DIRS` hides 11 of 14 high-risk findings on the one
   corpus repository where the tool's core competence applies. **That is the
   default that is demonstrably wrong**, and it is the one this document
   recommends changing.

---

## 1. What was asked, and one premise that did not survive

The brief states: default high-risk recall is 10/30, 16/30 with domains declared,
23/30 with domains plus an AI import.

All three figures reproduce. **The third does not mean what the sentence implies.**

`benchmarks/synthetic/RECALL.json` records its own method for that condition:

> Fixtures copied and given `import torch  # injected by build_recall_artefact.py`
> so the AI-indicator gate is satisfied for every file. **The corpus is modified;
> the number is not comparable to a scan of the corpus as committed.**

So 23/30 was obtained by **changing the corpus**, not by **changing the default**.
It is an upper bound on what the gate costs, not a measurement of what turning it
off would give. That distinction is the reason section 3 measures the gate
directly.

**A second premise, also checked rather than assumed.** N2's split of the 20
default misses into 6 / 7 / 7 was derived by subtracting fractions, which is only
valid if the missed sets are nested. They are:

```
missed(domains)   subset of missed(default)? True
missed(both)      subset of missed(domains)? True
fixtures missed WITH domains but hit by default : 0 []
fixtures missed WITH ai-import but hit w/ domains: 0 []
```

---

## 2. The 20 default misses, decomposed by set difference

Produced by predicate over the committed artefact, never by subtraction.

```
A. recovered by declaring domains        : 6
     highrisk_employment.py          highrisk_traffic_control.py
     highrisk_judicial_support.py    highrisk_visa_triage.py
     highrisk_promotion_ranking.py   highrisk_water_supply.py

B. recovered only by adding an AI import : 7
     highrisk_admissions.py          highrisk_task_allocation_shift.py
     highrisk_medical_triage.py      highrisk_voice_verify.py
     highrisk_polygraph_screen.py    highrisk_worker_monitoring.py
     highrisk_student_assessment.py

C. never recovered (pattern-side)        : 7
     highrisk_benefits_eligibility.py  highrisk_energy_grid.py
     highrisk_border_screening.py      highrisk_exam_proctor.py
     highrisk_crime_forecast.py        highrisk_recidivism.py
     highrisk_voter_targeting.py

itemisation: 6 + 7 + 7 = 20
default misses as published            = 20
RECONCILED

gate behaviour (A+B) : 13 of 20
pattern absence (C)  : 7 of 20
RECONCILED: 13 + 7 = 20
```

**13 of 20 are gate behaviour and 7 are genuine pattern absence.** The brief's
alternative hypothesis, that the gap is pattern absence rather than gating, is
therefore **partly true**: a third of the misses are patterns the tool does not
have, and no default change reaches them.

### Where the two gates sit in the code

- **AI-indicator gate**: `scripts/classify_risk.py:733`.
  `if not is_ai_related(text, ...): return Classification(tier=RiskTier.NOT_AI, ...)`.
  `check_high_risk()` is never reached when it fires. `check_prohibited()` runs
  **before** it, which is why prohibited recall is 5/5 in every configuration.
- **Domain gate**: `scripts/report.py:1156-1172`. A `high_risk` finding all of
  whose indicators are in `OPT_IN_CATEGORIES` is suppressed unless the user
  declared a matching `--domain` or the project's imports fingerprinted one.

---

## 3. Every candidate default, measured on the synthetic corpus

Four configurations through the **real CLI**, with the `REGULA_POLICY` pin
`build_recall_artefact._run_cli` uses, so all four are comparable to each other and
to the committed artefact. One variable moves between rows.

D2 and D3 toggle the gate by rebinding `classify_risk.is_ai_related` in a driver
that then calls the real `scripts.cli.main`. **Control, run first:** with the gate
left ON the driver's output is identical to the shipped CLI's apart from the
timestamp, so the driver is not itself a variable.

```
corpus: 38 fixtures = 30 high_risk + 5 prohibited + 3 negative   RECONCILED

configuration                   high-risk recall  prohibited  FP on 3 negs  findings a user sees
D0  current default                    10/30           5/5            0/3                     21
D1  domains declared                   16/30           5/5            0/3                     27
D2  AI-indicator gate off              14/30           5/5            0/3                     25
D3  both gates off                     23/30           5/5            0/3                     34

RECONCILIATION: hits + missed == 30 for every row: True

D1: +6  -0
D2: +4  -0
D3: +13 -0     (no configuration loses a finding the current default makes)
```

**D3 reaches 23/30 by changing the tool, and the artefact reached 23/30 by
changing the corpus.** Two different methods, the same figure. That is the
strongest evidence in this document that the AI-indicator gate is exactly what
separates the two conditions.

### What precision means here, and why the 0/3 column is nearly worthless

The corpus holds **three** negative fixtures. A precision figure over three
negatives cannot bound the false-positive cost of a default, and the `0/3` column
should not be read as "no false positives". It should be read as "this corpus
cannot answer that question". Section 4 is where the answer comes from.

---

## 4. The same four defaults on real repositories

Three third-party repositories, pinned by the commit cloned, chosen before
anything was run and not screened for a flattering result:

**Every hash in this table names an object in the third-party repository beside
it, never in this one.** `docs/improvement/LEDGER.md` carries a guard asserting
that a backticked hash resolves in this repository, which is why the same commits
appear there without backticks (N39c).

| repository | commit | shape |
|---|---|---|
| `ageitgey/face_recognition` | `9f3061aaeed9a8756d2c970f5dfe066617a8281d` | 106 files, 30 Python |
| `open-webui/open-webui` | `01f4282f1ffe0d6212f58d3afbeae21fffd0c4be` | 5,031 files, 256 Python, 740 TS/JS/Svelte |
| `vercel/ai` | `86892f3f6b4de52ee7f41d73c9c477b839596468` | 7,988 files, 5,556 TS |

These have no ground-truth labels, so what is reported is **what a user would
see**: the number of findings. An increase is a cost whether or not each new
finding is correct, because the user reads all of them.

```
repository               D0     D1     D2     D3     D3-D0
face_recognition          2      2      3      3        +1
open-webui               18     18     20     20        +2
vercel-ai                30     30     38     38        +8
```

### 4a. The disagreement, and it is the decision-relevant one

**On the synthetic corpus, declaring domains is the single largest recall win:
+6 of 30. On all three real repositories it adds exactly nothing.**

```
face_recognition   D1 adds files: []
open-webui         D1 adds files: []
vercel-ai          D1 adds files: []
```

`D3 == D2` on every real repository, by file set as well as by count. The domain
gate contributes nothing observable on real code.

**Why, and it is not a mystery.** The domain gate opens when the project's imports
fingerprint a domain. A real repository that does face recognition imports face
recognition libraries; a real chat application imports LLM SDKs. **The synthetic
fixtures are single files with no dependency surface**, so the fingerprint never
fires for them and only an explicit `--domain` can open the gate. The corpus is
constructed in exactly the shape that makes the domain gate look expensive.

**So the 16/30 figure is real, reproducible, and a poor guide to what a user
would get.** That is the finding this section exists to produce.

### 4b. What the AI-indicator change actually adds, itemised

All 11 findings D2 adds over D0, with their own categories:

```
face_recognition
  high_risk    p88  face_recognition/face_recognition_cli.py
                    Annex III, Category 1: Biometric identification and categorisation

open-webui
  limited_risk p53  backend/open_webui/routers/users.py           Synthetic content generation
  limited_risk p53  src/lib/constants/permissions.ts              Synthetic content generation

vercel-ai
  limited_risk p53  packages/ai/src/generate-image/index.ts       Synthetic content generation
  limited_risk p68  packages/ai/src/generate-text/index.ts        Synthetic content generation
  limited_risk p53  packages/ai/src/generate-text/generated-file.test-d.ts   Synthetic content generation
  limited_risk p73  packages/assemblyai/src/assemblyai-api-types.ts          Emotion recognition systems
  limited_risk p68  packages/assemblyai/src/assemblyai-transcription-model-options.ts  Emotion recognition systems
  limited_risk p68  packages/deepgram/src/deepgram-transcription-options.ts  Chatbots and conversational AI
  limited_risk p53  packages/codemod/src/codemods/v5/move-image-model-maxImagesPerCall.ts  Synthetic content generation
  limited_risk p53  packages/xai/src/responses/xai-responses-api.ts          Synthetic content generation
```

**My reading of those 11, labelled as judgement and not as measurement**, because
nothing here is labelled ground truth:

- **Clearly real, 4.** `face_recognition_cli.py` is the library's own
  face-identification CLI and is the second core module in the package;
  `generate-image/index.ts` and `generate-text/index.ts` are the AI SDK's image and
  text generation entry points, which is what Article 50 is about;
  `xai-responses-api.ts` is an LLM response API.
- **Arguable, 3.** The two AssemblyAI files are option and type definitions for a
  transcription service that does offer sentiment features, so "emotion
  recognition" is defensible on the vocabulary and thin on the substance.
  `deepgram-transcription-options.ts` is labelled "Chatbots and conversational AI",
  which is a mislabel of a transcription options file.
- **Clearly noise, 4.** `move-image-model-maxImagesPerCall.ts` is a **codemod**, a
  script that rewrites other people's source; `generated-file.test-d.ts` is a
  **type test**, and its `.test-d.ts` suffix is not recognised by the test-file
  exclusion; `permissions.ts` and `routers/users.py` are a constants file and a
  user router labelled "synthetic content generation".

So the cost of the AI-indicator change on ~10,600 real files is **11 findings, of
which I judge 4 clearly worth reading and 4 clearly not.** That is a genuinely
modest cost, and it is not zero.

### 4c. The suppressor nobody was measuring, and it is the largest

Neither gate is what hides most of the findings on real code.

On `face_recognition`, per directory, same command, `--scope all`:

```
target               py_on_disk   files_scanned   high_risk
.                        30             6             3
face_recognition          4             4             2
examples                 22            23            11
tests                     2             0             0
docs                      1             1             1
docker                    0             0             0
```

**`regula check .` reports 3 high-risk findings. The same tool reports 14 across
the same tree when pointed at each subdirectory.** The difference is
`constants.SKIP_DIRS`, which contains `examples`, `example`, `demos` and `demo`,
and 23 of the repository's files live under `examples/`.

**11 of 14 findings, 79%, are invisible at the default invocation, and no line of
the output says a directory was skipped.** The only scope line the run prints is
`Scope: 1 non-production finding(s) excluded`, which refers to a provenance
deduction on `docs/conf.py` and not to the 23 unread files.

For comparison, on the same repository the two gates in the brief are worth +0
(domains) and +1 (AI indicator). **The directory skip is worth 11.**

`SKIP_DIRS` is byte-identical between PyPI 1.9.0 and this tree, so this is
current behaviour and not a historical note.

**The counter-argument, which is in the code and is serious.** The comment above
that set reads: "Example/demo directories are not production code, scanning them
inflates false positives by 23% (benchmarked on 5 OSS projects)." That is a real
design decision with a stated measurement behind it. It is also, on this
repository, the reason a face-identification library's 23 face-identification
examples are unread. Both are true. Note also that the figure in that comment is
an unsourced numeric claim living in a code comment, where no claim instrument
reaches it.

---

## 5. The recommendation, stated as a decision

### 5a. Do not change the domain default

**Cost of changing it:** on the synthetic corpus, +6 recall. On real code, nothing.

**Risk of changing it:** the fingerprint route exists precisely so that a real
project gets its domains opened automatically. Declaring all eight by default
removes the distinction between "this project handles biometrics" and "this
project mentions a word", and the only corpus on which that looks like a win is
the one whose fixtures have no imports.

**Strongest case against this recommendation:** a project can be genuinely
in-domain without importing a fingerprinted library, for example a hiring system
written against a bare database with no ML dependency. On such a project the
domain gate is a silent false negative and the synthetic corpus is the honest
model, not the misleading one. **That case is real and this measurement cannot
rule on it, because all three corpus repositories import their domain's
libraries.** What would settle it is a real repository that is in-domain and
imports nothing fingerprinted.

### 5b. Change what the AI-indicator gate does when it fires, not whether it fires

Removing it is defensible on the numbers: +13 synthetic recall, no regressions,
11 extra findings on 10,600 real files. But four of those 11 are noise on files
that are not AI systems at all, and the gate is what keeps the tool from
reporting on every file in a repository.

**The better change is the one the domain gate already makes.** When domain gating
suppresses a finding, the scan says so:

```
  INFO: 1 high-risk finding(s) suppressed by domain gating
        Categories: justice
        To activate, use: regula check --domain <domain>
```

**The AI-indicator gate says nothing at all.** A file that matches a high-risk
pattern and is dropped because it imports no AI library is invisible. Making it
visible costs the user nothing, tells the truth about what the scan did, and
leaves the finding count where it is.

### 5c. Change the default that is demonstrably wrong: disclose the directory skip

`Files scanned: 6` on a 30-file repository is true and incomplete. The class fix
is the one this project already ruled on for a different instrument: **N138
established that when an instrument cannot read part of its population, the gap is
declared and printed at the point of use rather than left silent.** The same
remedy applies here.

**This does not require changing what is scanned.** It requires the scan to report
what it skipped. Whether to also change `SKIP_DIRS` is a separate ruling, and the
23% false-positive figure in that comment should be re-derived before it is taken
as decisive, because it is undated, unsourced, and names a corpus of five
unidentified projects.

---

## 6. The strongest case against everything above

**The synthetic corpus is 38 files and 3 of them are negatives.** Every recall
figure in section 3 rests on 30 hand-written fixtures whose own manifest says they
were written as a developer in that domain would plausibly write the code. That is
the right method and it is still 30 files.

**The three real repositories have no labels.** Section 4's "cost" column counts
findings, not errors. My classification of the 11 into 4 real, 3 arguable and 4
noise is judgement, and a hostile reader should treat it as such.

**And the real-repository sample is three.** The domain-gate conclusion in 5a
rests entirely on the observation that all three fingerprint their domains, which
is a property of the three, not of repositories.

**What would overturn 5a:** any real repository, in an Annex III domain, that
imports nothing the fingerprint recognises. If such repositories are common, the
domain gate is a false-negative engine and the synthetic corpus was right.

**What would overturn 5b and 5c:** a measurement showing the disclosure lines are
read as noise by an actual user. No comprehension test has ever been run on this
project, so that is untested rather than assumed away.

---

## 7. Why no default was changed here

The brief permits changing a default whose current setting is demonstrably wrong,
and says not to change one unless the measurement is unambiguous.

**It is unambiguous for one of the three**, section 5c, and that is a disclosure
change rather than a scope change: it alters no finding.

**It is not unambiguous for the other two.** 5a recommends *not* changing a
default, and 5b recommends changing what a gate reports rather than whether it
fires, which is a product behaviour change under `PRODUCT_BUILD STOP` with a
counter-argument I cannot close from three repositories.

`PRODUCT_BUILD` remains STOP. The standing product, venture, contact,
data-collection and pilot verdicts are unchanged by this document.
