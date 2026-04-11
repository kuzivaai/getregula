# Regula Assess — Web UI

A minimal web interface for the `regula assess` questionnaire. Non-technical users answer 5 yes/no questions and get their EU AI Act risk tier, applicable articles, and next steps.

## Quick start

```bash
# From the project root
pip install flask
cd web
python app.py
```

Then open http://localhost:5000.

## Install via optional dependency

```bash
pip install regula-ai[web]
```

## Docker

```bash
# From the project root (context needs access to scripts/)
docker build -f web/Dockerfile -t regula-assess-web .
docker run -p 5000:5000 regula-assess-web
```

## How it works

- Imports the question set and result formatting directly from `scripts/assess.py` — no duplication.
- Stateless: uses a Flask session cookie to track answers during a single assessment. No database, no accounts.
- The question flow and short-circuit logic (e.g. "not in scope" exits early) match the CLI exactly.

## Files

| File | Purpose |
|------|---------|
| `app.py` | Flask application |
| `templates/assess.html` | Single Jinja2 template (intro, question, result pages) |
| `Dockerfile` | Container deployment |
