# Article 50 static-signal regression corpus

This corpus measures only whether `scripts/article50_evidence.py` recognises the
implementation vocabulary it claims to recognise. It does **not** measure legal
applicability, compliance, production behaviour, or real-world accuracy.

The cases are synthetic paraphrases derived from the European Commission's
final Article 50 guidelines (20 July 2026), especially sections 3.1–3.2,
4.1–4.3, 5.1, 6.1–6.2 and 7. They are labelled by the project maintainer and
are neither independently annotated nor representative of production code.
Accordingly, a perfect result is a regression result, not an accuracy claim.

Run:

```bash
python3 benchmarks/article50/evaluate.py
python3 benchmarks/article50/evaluate.py --write
```

The evaluator reports trigger and control precision/recall separately and
lists every false positive and false negative. The checked-in `results.json`
must exactly match the current scanner and corpus.

Primary sources:

- Regulation (EU) 2024/1689, Article 50 and Article 96(1)(d):
  https://eur-lex.europa.eu/eli/reg/2024/1689/oj
- Regulation (EU) 2026/1744, Article 111(4):
  https://eur-lex.europa.eu/eli/reg/2026/1744/oj
- Commission final Article 50 guidelines:
  https://digital-strategy.ec.europa.eu/en/library/guidelines-obligations-ai-act-art50
