---
title: "EU AI Act Article 5 Is Already Live: Scanning Your Code for Prohibited AI Practices"
published: false
description: "Article 5 prohibited AI practices have been enforceable since 2 February 2025, with fines up to EUR 35 million or 7% of turnover. Here's how to scan your codebase for them."
tags: euaiact, compliance, ai, security
canonical_url: https://getregula.com/blog/blog-article-5-prohibited-practices.html
cover_image: https://getregula.com/assets/og-image.png
---

Eight categories of AI practice have been illegal in the EU since 2 February 2025. The fines are up to EUR 35 million or 7% of global annual turnover. Most developers have no idea. Here's what the prohibitions actually mean in code, how to scan for them, and what to do when something gets flagged.

## This is already law

I keep meeting developers who think the EU AI Act is a future problem. Something to deal with in 2027 or 2028, once the Omnibus delay sorts itself out.

For high-risk systems, that might be true. The Digital Omnibus on AI proposes pushing those deadlines to late 2027 or mid-2028, and trilogue negotiations are underway.

But Article 5 isn't part of that delay. Article 5 has been enforceable since **2 February 2025**. That was over a year ago. The prohibitions are in force right now, with the highest penalty tier in the entire regulation: up to EUR 35 million, or 7% of worldwide annual turnover, whichever is higher. For context, the high-risk non-compliance penalty is 3% of turnover. Article 5 violations are penalised at more than double that rate.

If your codebase contains one of the eight prohibited practices and you deploy it in the EU, you're already in breach. Not "will be in breach when the deadline hits." Are, today.

## The eight prohibited categories

Article 5 lists eight specific practices. Some are obvious. Others are narrower than you'd expect. Here's each one, and what it looks like when it shows up in code.

### Article 5(1)(a) — Subliminal manipulation

AI systems that deploy techniques operating beyond a person's consciousness to materially distort their behaviour, causing or likely to cause significant harm. Think dark patterns backed by AI that the user literally can't perceive. The key word is "beyond consciousness": if the user can see the nudge, it isn't subliminal in the legal sense.

In code, Regula looks for patterns like: `subliminal`, `beyond_consciousness`, `subconscious_influence`. Developers building these systems tend to name things what they are.

### Article 5(1)(b) — Exploiting vulnerabilities

AI systems that exploit the vulnerabilities of specific groups (due to age, disability, or socio-economic situation) to materially distort behaviour and cause significant harm. This is about targeting people because they are vulnerable, not about serving them.

Regula looks for `target_elderly`, `exploit_disabil`, `vulnerable_group_target`. The distinction matters. Building accessibility features for elderly users is fine. Building a system that targets elderly users because they're less likely to recognise a manipulative interface is not.

### Article 5(1)(c) — Social scoring

Evaluating or classifying people based on their social behaviour or personal traits, where this leads to detrimental treatment that is disproportionate to the context. The prohibition applies to scoring by public authorities or on their behalf.

Patterns: `social_score`, `social_credit`, `citizen_score`, `behaviour_scoring` (when combined with terms like `citizen`, `public`, `government`, or `trustworthy`). Social scoring shows up in a lot of different phrasings, so the category uses several matchers. But a gamification leaderboard is not social scoring. More on false positives below.

### Article 5(1)(d) — Individual criminal risk prediction

Predicting whether a person will commit a crime based solely on profiling or personality traits. The word "solely" is doing real work here. A system that uses multiple evidence sources (case facts, prior convictions with human review) may be lawful. One that predicts criminality from someone's profile alone is not.

Matched by: `crime_predict`, `criminal_risk_assess`, `predictive_policing`, `recidivism`. The `recidivism` pattern comes up most often in practice. If you're building a recidivism scoring model, look at this carefully.

### Article 5(1)(e) — Untargeted facial recognition scraping

Creating or expanding facial recognition databases by scraping facial images from the internet or CCTV in an untargeted way. This is the Clearview AI prohibition. If your system scrapes faces from public sources to build a recognition database, it's prohibited regardless of the purpose.

Patterns: `face_scrap`, `facial_database_untarget`, `mass_facial_collect`. Straightforward.

### Article 5(1)(f) — Emotion inference in workplaces and schools

Inferring emotions in workplace and educational settings. There's a narrow exception: medical or safety purposes, such as detecting driver fatigue or monitoring a patient's wellbeing in a clinical setting. But "let's see if our employees are happy" is prohibited.

Patterns: `emotion.*workplace`, `emotion.*school`, `sentiment.*employee`, `workplace.*emotion`, `employee.*emotion`. Regula matches these with a 40-character window between terms to catch common code structures like `detect_emotion(frame, context="workplace")`.

### Article 5(1)(g) — Biometric categorisation of sensitive attributes

Using biometric data to categorise people by race, political opinions, trade union membership, religious beliefs, sex life, or sexual orientation. There's a narrow exception for labelling lawfully acquired biometric datasets (photo sorting, for example) where no categorisation of individuals actually occurs.

Patterns: `race_detect` (with a negative lookahead to exclude `race_condition` and `thread` contexts), `ethnicity_infer`, `political_opinion_biometric`, `religion_detect`, `sexual_orientation_infer`. The race condition guard is there because `race_detect` in a concurrent programming context is an extremely common false positive.

### Article 5(1)(h) — Real-time biometric identification in public spaces

Real-time remote biometric identification in publicly accessible spaces for law enforcement. Narrow exceptions exist but require prior judicial authorisation: searching for victims of abduction or trafficking, preventing an imminent terrorist threat, or identifying suspects of serious criminal offences listed in Annex II.

Patterns: `real_time_facial_recogn`, `live_biometric_public`, `public_space_biometric`, `mass_surveillance_biometric`.

## What a scan actually looks like

Enough theory. Here's what happens when you run `regula check` against a project that contains prohibited patterns. This is Regula's actual output format.

Say you have a Python file called `hr_analytics.py` that analyses employee sentiment from webcam feeds, and a `scoring.py` that builds a social credit system for a government client:

```
$ regula check .

  Regula v1.7.0 -- EU AI Act compliance scanner
============================================================

  Verdict: PROHIBITED
  Your project contains AI practices prohibited under EU AI Act Article 5.
  These must be removed before deployment in the EU.

  Why:
    1. hr_analytics.py:42 -- Emotion inference in workplace or educational settings
       (Art. 5)
    2. scoring.py:17 -- Social scoring by public authorities or on their behalf
       (Art. 5)
    3. scoring.py:89 -- Social scoring by public authorities or on their behalf
       (Art. 5)

  Files scanned:       14
  Prohibited:          3
  Credentials:         0
  High-risk:           1
  Agent autonomy:      0
  Limited-risk:        2
  Suppressed:          0
  Block tier:          3
  Warn tier:           1
  Info tier:           2

  PROHIBITED INDICATORS:
    [BLOCK] [ 92] hr_analytics.py -- Emotion inference in workplace or educational settings [develop]
    [BLOCK] [ 88] scoring.py -- Social scoring by public authorities or on their behalf [develop]
    [BLOCK] [ 85] scoring.py -- Social scoring by public authorities or on their behalf [develop]

============================================================
  Confidence = pattern match + context analysis (0-100).
  Tiers: BLOCK (>=80 or prohibited), WARN (50-79), INFO (<50)
  Suppress findings: add '# regula-ignore' to file

  ────────────────────────────────────────────────────────
  Next steps:
    1. regula fix --project .         Remove prohibited practices
    2. regula gap --project .         See which articles you need to address
    3. regula roadmap --project .     Get a week-by-week compliance plan
    4. regula evidence-pack --project . --bundle   Generate auditor-ready evidence
```

Three things immediately: your verdict (prohibited), which files caused it, and what to do next. The confidence scores (92, 88, 85) reflect how closely the matched code resembles a real prohibited practice. A score of 92 on an emotion-in-workplace finding means the pattern matched `sentiment.*employee` or `emotion.*workplace` with strong surrounding context.

All prohibited findings are automatically BLOCK tier, regardless of confidence score. There's no scenario where a prohibited pattern gets downgraded to WARN or INFO. The Act doesn't have a "sort of prohibited" category.

## False positives are real, and that's fine

Regex-based scanning will produce false positives. That's a deliberate trade-off: I'd rather flag something that turns out to be fine than miss something that isn't.

Here are the most common ones I've seen across the prohibited categories:

**Emotion analysis for UX research.** Running sentiment analysis on product feedback to improve your interface isn't the same as inferring emotions in a workplace setting under Article 5(1)(f). The prohibition is specifically about workplace and educational contexts. A pattern like `sentiment_analysis(user_feedback)` won't trigger the prohibited patterns because the regex requires the `workplace`, `school`, or `employee` context term nearby. But `sentiment_analysis(employee_feedback)` will, because the word `employee` appears within the 40-character match window.

**Gamification scoring.** A leaderboard system that scores users on their activity in a game or app isn't social scoring under Article 5(1)(c). The prohibition requires evaluation by public authorities or on their behalf, and the scoring must lead to detrimental treatment disproportionate to the original context. If you have a variable called `social_score` in a gamification module, Regula will flag it. That's correct behaviour: document why it isn't a prohibited practice and move on.

**Race condition detection.** The biometric categorisation pattern under Article 5(1)(g) includes `race_detect`. In concurrent programming, `detect_race_condition` is extremely common. Regula's pattern has a negative lookahead excluding matches followed by `condition`, `thread`, or `concurrent`. Catches most of these, but not all. If you name your mutex debugging function `race_detector`, expect a flag.

**Recidivism in academic research.** If you're working on a paper about criminal justice outcomes and your code includes the word `recidivism`, Regula will flag it under Article 5(1)(d). The prohibition applies to systems that predict criminal risk based solely on profiling. Academic research analysing existing data isn't that. Document it and suppress.

## What to do when something gets flagged

Depends on whether the flag is accurate.

**If it's a true positive:** Remove or redesign the functionality before deploying in the EU. Run `regula fix --project .` for guided remediation. Article 5 doesn't have a grace period or a "comply or explain" mechanism. The practice is either prohibited or it isn't. If it is, it must not ship.

**If it's a false positive:** Add a `# regula-ignore` comment to the relevant line or file, with a rationale explaining why this isn't a prohibited practice. Regula tracks suppressed findings and will remind you if a suppression lacks a rationale. The suppression becomes part of your compliance evidence.

A suppression with rationale looks like this in your code:

```python
# regula-ignore: social_score is a gamification leaderboard,
# not public authority social scoring per Article 5(1)(c).
user_social_score = calculate_engagement_points(activity_log)
```

**If you're not sure:** Get legal review. Some of these categories have exceptions that require actual legal judgment, not just a regex match. The emotion inference prohibition has a medical/safety exception. The criminal prediction prohibition hinges on whether the system uses "solely" profiling. Regula can tell you a pattern matched. It can't tell you whether your specific use case falls within a narrow exception. A lawyer can.

## The Omnibus doesn't change this

I keep seeing this cause confusion, so I want to be direct. The Digital Omnibus on AI, currently in trilogue negotiations, proposes delaying the deadlines for **high-risk AI systems**. It doesn't touch Article 5.

The Article 5 prohibitions became enforceable on 2 February 2025. The Omnibus proposal doesn't modify that date. Neither the Council's general approach (13 March 2026) nor the Parliament's first-reading position (26 March 2026) proposed any change to the Article 5 application date. There's no version of the trilogue outcome that delays Article 5.

If someone on your team is saying "we can wait for the Omnibus," they're wrong about Article 5. They may be right about Annex III high-risk obligations. Not about this.

## The eight patterns in numbers

Regula defines 8 prohibited pattern categories containing 33 individual regex patterns. Every category has `confidence: high`, `likelihood: high`, `impact: high` in the pattern definitions. That's not a configurable risk weighting. It reflects the fact that Article 5 carries the highest penalty tier in the regulation.

The patterns aren't trying to be clever. They match the terms that developers actually use when building these systems: `social_credit`, `predictive_policing`, `face_scrap`, `emotion.*workplace`. Intentionally direct. Prohibited practice detection isn't the place for fuzzy matching or probabilistic classification. If the pattern matches, look at it. If it's a false positive, document it and suppress it. If it isn't, stop deploying it.

## Run the scan

Install Regula, point it at your project, and read the output. Takes about three seconds for a typical codebase. If everything comes back clean, you're done. If something gets flagged as prohibited, you now know about it before a regulator does.

```bash
pipx install regula-ai && regula check .
```

If you want only prohibited findings, filter with `regula check . --format json | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f['file'],f['description']) for f in d['data']['findings'] if f['tier']=='prohibited']"`. But honestly, just read the full output. It isn't long, and you should know your full risk profile.

Article 5 isn't coming. It's here. The scan takes seconds. The fines don't.

**Not legal advice.** Regula identifies regulatory risk indicators in code for developer review. It does not constitute legal advice, and its output should not be relied upon as a definitive compliance determination. Consult a qualified legal professional for legal questions. All regulatory dates and article references cited in this article are sourced from [Regulation (EU) 2024/1689](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689). Penalty amounts are specified in Article 99(3).

---

*Originally published at [getregula.com](https://getregula.com/blog/blog-article-5-prohibited-practices.html)*
