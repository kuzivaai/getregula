# code-completion-tool — minimal-risk fixture (clean scan)

A minimal reference project that scans clean under Regula. Use it to confirm
that Regula does not raise false positives on ordinary developer tooling, and
to see what a "clean" scan looks like.

## Run the scan

```
regula check examples/code-completion-tool
```

Expected output (verified against Regula v1.7.0 on 2026-04-16):

```
Regula Scan: /home/mkuziva/getregula/examples/code-completion-tool
============================================================
  Files scanned:      1
  Prohibited:         0
  Credentials:        0
  High-risk:          0
  Agent autonomy:     0
  Limited-risk:       0
  Suppressed:         0
  BLOCK tier:         0
  WARN tier:          0
  INFO tier:          0
============================================================
```

## Why Regula does not flag this

A developer-productivity utility that does not make decisions about natural
persons, does not fall under any Annex III category, and does not interact
directly with end users is outside the scope of Articles 9-15 and Article 50.
Regula matches patterns for those categories and finds none here.

## What the fixture does

`app.py` returns a code snippet from a static lookup table based on the
prefix you pass it. No ML, no network, no decisions about people.
