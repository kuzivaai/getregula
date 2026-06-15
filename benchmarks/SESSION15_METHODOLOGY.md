# Session 15: Labelling Methodology Note

## 1. What does inter-rater reliability require here?

Cohen's kappa measures the extent to which two raters agree on categorical assignments (here: tp/fp) beyond what chance alone would predict. Its diagnostic value — the reason we compute it — is that disagreements reveal genuine ambiguity in either the labelling criteria or the data. When raters disagree on a borderline case, that tells us something about the precision of the instrument.

**Independence requirements:**

- **Independence from each other during rating:** Non-negotiable. Each rater must label without seeing the other's decisions. This is a definitional property of kappa — without it, the statistic is meaningless. **Basis:** Cohen (1960), "A coefficient of agreement for nominal scales," *Educational and Psychological Measurement* 20(1), 37–46. The formula's chance-agreement correction assumes raters operate independently.

- **Independence from the instrument being evaluated:** Desirable but not strictly required by the kappa formula itself. Kappa measures reliability (consistency between raters), not validity (correctness of labels). In practice, published inter-rater reliability studies in software engineering routinely use raters who helped develop the coding scheme — but they require those raters to work from the codebook alone, not from memory of intent. **Basis:** Krippendorff (2018), *Content Analysis*, 4th ed., §11.1 — raters "must be instructable," i.e. work from explicit criteria, not tacit knowledge. Gwet (2014), *Handbook of Inter-Rater Reliability*, Ch. 1 — notes that reliability is a property of the rating process, not the raters' backgrounds, provided the process is followed.

- **What this means for Rater 1 (the founder):** The founder built the patterns and labelled the existing 446-entry corpus. Using the founder as Rater 1 is methodologically acceptable — published inter-rater reliability studies in software defect classification routinely use paper authors as raters with kappa measurement (e.g. Cristea et al., "Do I really need all this work to find vulnerabilities?", arXiv:2208.01595, where two researchers classify tool alerts as TP/FP with Cohen's kappa). The practice is widespread: study authors perform classification, compute kappa, discuss disagreements, and refine by consensus. **Note:** An earlier version of this document cited Herzig et al. (ICSE 2013) for this point; the paper is real but the full text was not accessed to verify it supports this specific claim. The citation was retracted and replaced with a verified reference. The conclusion is unchanged: Rater 1 (founder) is acceptable, but Rater 1's labels may carry confirmation bias toward the patterns' intent. This is WHY Rater 2 must be genuinely independent: the kappa measures whether an outsider reaches the same conclusions, not whether the author agrees with their own tool.

## 2. Can an LLM that worked on the patterns serve as a legitimate rater?

**The argument for:** An LLM can read code, apply the legal test in LABELLING_CRITERIA.md, and produce tp/fp judgements. It is reproducible. It does not have session-to-session memory in the way a human does. It can process findings faster than a human.

**The argument against:** The critical issue is not capability but independence from the instrument.

I (Claude) have participated in writing and refining risk_patterns.py across multiple sessions. This creates a specific form of non-independence: I share the pattern author's framing of what constitutes a risk. When I label a finding, I am not applying an independent reading of the legal text — I am applying the same interpretive lens that generated the pattern. This inflates agreement between my labels and the instrument's intent, which is exactly the bias kappa exists to detect and quantify.

**A concrete example of why this matters:** Suppose Regula flags `deepface/commons/weight_utils.py` (a utility that downloads model weights) as "Annex III, Category 1 — biometric identification." Is this a TP or FP? The legal test turns on whether the code "performs or enables biometric identification." A model weight downloader in a biometrics project *enables* biometric identification (it's infrastructure for the system), but it does not itself *perform* identification. A pattern-developer (including an LLM that helped develop patterns) might lean TP because the pattern was designed to flag the project. An independent rater might lean FP because the specific file is generic infrastructure. This disagreement is informative — it reveals the pattern's scope. But if both raters share the pattern-developer's framing, the disagreement is suppressed, and kappa overstates agreement.

**Reasoned position:** An LLM that co-developed the patterns is not a legitimate rater of record for kappa computation. **Confidence: HIGH.** This follows from the purpose of kappa (measuring independent agreement), not from convention or the prompt's prior assumption. The LABELLING_CRITERIA.md at line 135–136 states "Rater 2: must NOT be the founder or an LLM" — this was correct, though the document did not supply the reasoning. The reasoning is above.

**Where the prompt's framing was right and where it was incomplete:** The prompt hypothesised that Claude should not be a rater of record, and that hypothesis holds. However, the prompt slightly understated what a model CAN legitimately do. See §3.

## 3. Where can a model label legitimately sit?

**Excluded from kappa:** Yes. No model label may be counted as Rater 1 or Rater 2 in the kappa computation. A hostile reviewer must be unable to mistake a model label for an independent human rating.

**Legitimate as a disclosed decision-support signal:** Yes. A pre-label file headed with a clear provenance statement ("Model pre-label — not a rater of record, excluded from kappa") can serve the human rater by:

1. **Flagging ambiguous cases.** Cases where the model is uncertain are likely to be cases where human raters would also disagree. This helps the founder allocate attention to the hard cases rather than spending 2 minutes on each obvious TP.
2. **Providing a starting hypothesis.** The founder reads the model's call and reasoning, then accepts, overrides, or notes disagreement. The human label is the official one; the model label is a disclosed assist.
3. **Post-hoc consistency check.** After human labelling is complete, comparing human vs model labels can reveal systematic patterns (e.g. "the model consistently called infrastructure files TP while the human called them FP") that inform criteria refinement.

**Disclosure requirements:**
- Pre-label file must be in a SEPARATE file from any rater label file
- File header must state: model identity, that it is excluded from kappa, and that it is decision support only
- No pre-label value may be copied into a rater label file without the human making an independent decision
- If published alongside the benchmark, it must be in an appendix or supplementary table, not in the main reliability results

## 4. What genuinely requires a human, and why?

| Task | Human required? | Reasoning |
|------|----------------|-----------|
| **Rater 1 of record** | Yes | Labels must be attributed to a human who takes responsibility for them. The founder's domain knowledge and project context are relevant. |
| **Rater 2 (independent)** | Yes, a *different* human | Independence from both Rater 1 and the instrument is the entire point of the reliability measurement. |
| **Adjudicating disagreements** | Yes (both raters) | Adjudication is a discussion, not a computation. Both raters must understand why they disagreed. |
| **Reading code context** | No — model can assist | The model can parse code, identify imports, describe what a file does. This is decision-support, not rating. |
| **Applying the legal test per finding** | No — model can assist, but human must decide | The model can state whether code falls under an Annex III category and give reasoning. The human must make the final call, especially on borderline cases. |
| **Setting the label field in the official file** | Yes | The model pre-label is in a separate file. The human types their own label. |

**What this session showed can be done that was previously assumed human-only:** The model can produce a substantive per-finding pre-label with legal reasoning, flag genuinely ambiguous cases, and estimate likely difficulty — all of which reduces the human rater's clock time from ~2 min/finding to potentially ~30–60 sec/finding for clear cases. The previous estimate of 2.5 hours may be closer to 1–1.5 hours with model assist, because the obvious cases (deepface core files = TP, setup.py in a biometrics repo = FP) can be confirmed quickly when the model has already flagged them.
