# cv-screening-app — high-risk fixture (Annex III, Category 4)

A minimal reference project that triggers an EU AI Act high-risk classification
when scanned with Regula. Use it to see what Regula flags on employment /
recruitment code without needing your own fixture.

## Run the scan

```
regula check examples/cv-screening-app
```

Expected output (verified by running against Regula v1.6.1 on 2026-04-16):

```
Regula Scan: /home/mkuziva/getregula/examples/cv-screening-app
============================================================
  Files scanned:      1
  Prohibited:         0
  Credentials:        0
  High-risk:          1
  Agent autonomy:     0
  Limited-risk:       0
  Suppressed:         0
  BLOCK tier:         0
  WARN tier:          1
  INFO tier:          0

  HIGH-RISK INDICATORS:
    [WARN] [ 68] app.py — Employment and workers management
      Add human oversight before automated hiring/employment decisions
============================================================
```

## Why Regula flags this

Annex III (4)(a) lists *"AI systems intended to be used for recruitment or
selection of natural persons, in particular to place targeted job
advertisements, to analyse and filter job applications, and to evaluate
candidates"* as a high-risk use case. If deployed for real hiring, Articles 9–15
apply: risk management, data governance, documentation, logging, transparency,
human oversight, accuracy.

## What the fixture does

`app.py` trains a toy logistic-regression model on in-memory job applicants and
ranks new candidates by predicted hire probability. No network calls, no
persistence, no real PII.

## What Regula does NOT tell you

Whether this code, in your context, is actually in scope of Annex III. That
depends on Article 6 (significant risk of harm) and the Article 6(3) exemption
for narrow procedural tasks. Regula surfaces the risk indicators; the
applicability decision is yours.
