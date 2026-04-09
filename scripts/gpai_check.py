# regula-ignore
#!/usr/bin/env python3
"""
Regula GPAI Code of Practice Check

Static-analysis check that maps a GPAI (General-Purpose AI) provider codebase
to the three chapters of the EU AI Act GPAI Code of Practice (final version
published 10 July 2025, endorsed by the Commission and AI Board 1 August 2025,
obligations in force since 2 August 2025, enforcement actions from 2 August 2026).

Chapters:
    1. Transparency             — all GPAI providers (Article 53)
    2. Copyright                — all GPAI providers (Article 53(1)(c))
    3. Safety and Security      — systemic-risk only (>= 10^25 FLOPs, Art 55)

This module emits a per-obligation PASS / WARN / FAIL / N/A verdict with
article anchors. It is a code-level indicator, not a legal determination.
The Code of Practice provides a rebuttable presumption of conformity —
adherence is evidenced by the concrete practices in each chapter.

Pattern surface is intentionally conservative: every obligation checks for
a concrete filesystem or source-code signal documented in
references/gpai_code_of_practice.yaml. Absence of a signal is recorded as
WARN or FAIL, never PASS.

Stdlib only. PyYAML is optional — if absent, the reference metadata fields
(code_status, enforcement dates) default to "unknown" but the checks still run.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Signal patterns — compiled once
# ---------------------------------------------------------------------------
# Each entry: (regex, short_label). Labels are stable identifiers used in
# reports and tests — do not rename without updating test_gpai_check.py.

_TRAINING_SIGNAL_SOURCES = [
    (r'\bloss\.backward\(\)', 'pytorch_backward'),
    (r'\boptimizer\.step\(\)', 'pytorch_optimizer_step'),
    (r'from\s+transformers\s+import[^\n]*Trainer\b', 'hf_trainer_import'),
    (r'\btransformers\.Trainer\b', 'hf_trainer_ref'),
    (r'\bTrainingArguments\b', 'hf_training_args'),
    (r'\b(?:pl|lightning|L)\.LightningModule\b', 'lightning_module_alias'),
    (r'\bLightningModule\b', 'lightning_module'),
    (r'\.push_to_hub\(', 'hf_push_to_hub'),
    (r'\.save_pretrained\(', 'hf_save_pretrained'),
    (r'\bimport\s+optax\b', 'jax_optax'),
    (r'\bfrom\s+optax\b', 'jax_optax_from'),
    (r'\bimport\s+flax\b', 'jax_flax'),
    (r'\bfrom\s+flax\b', 'jax_flax_from'),
    (r'\bfrom\s+accelerate\s+import', 'accelerate_import'),
    (r'\baccelerate\.Accelerator\b', 'accelerate_ref'),
    (r'\bimport\s+deepspeed\b', 'deepspeed_import'),
    (r'\bLoraConfig\b|\bget_peft_model\b', 'peft_finetune'),
]
_TRAINING_DISTRIBUTION_LABELS = {'hf_push_to_hub', 'hf_save_pretrained'}

_CRAWLER_SIGNAL_SOURCES = [
    (r'\bfrom\s+scrapy\b|\bimport\s+scrapy\b', 'scrapy'),
    (r'\bBeautifulSoup\s*\(', 'beautifulsoup'),
    (r'\bfrom\s+playwright\b|\bimport\s+playwright\b', 'playwright'),
    (r'\bselenium\.webdriver\b', 'selenium'),
    (r'\brequests\.get\(', 'requests_get'),
    (r'\bhttpx\.get\(|\bhttpx\.AsyncClient\b', 'httpx'),
    (r'\burllib\.request\.urlopen\b|\burllib\.request\.Request\b', 'urllib_request'),
    (r'\bcommon_crawl\b|\bc4_dataset\b', 'common_crawl'),
    (r'\bload_dataset\s*\(\s*["\']c4', 'hf_c4'),
]

_ROBOTS_COMPLIANCE_SOURCES = [
    (r'\burllib\.robotparser\b', 'urllib_robotparser'),
    (r'\bRobotFileParser\b', 'robot_file_parser'),
    (r'\bfrom\s+reppy\b', 'reppy'),
    (r'[\'"]robots\.txt[\'"]', 'robots_txt_literal'),
    (r'\bTDMRep\b|\btdmrep\b', 'tdmrep'),
]

_ROBOTS_BYPASS_SOURCES = [
    (r'\bROBOTSTXT_OBEY\s*=\s*False\b', 'scrapy_robots_disabled'),
    (r'--ignore-robots-txt|ignore_robots_txt', 'ignore_robots_flag'),
]

# Compile once
_TRAINING_SIGNALS = [(re.compile(p), label) for p, label in _TRAINING_SIGNAL_SOURCES]
_CRAWLER_SIGNALS = [(re.compile(p), label) for p, label in _CRAWLER_SIGNAL_SOURCES]
_ROBOTS_COMPLIANCE_SIGNALS = [(re.compile(p), label) for p, label in _ROBOTS_COMPLIANCE_SOURCES]
_ROBOTS_BYPASS_SIGNALS = [(re.compile(p), label) for p, label in _ROBOTS_BYPASS_SOURCES]

# Directories to skip during walk
_SKIP_DIRS = {
    '.venv', 'venv', 'env', '.env', '__pycache__', '.git', '.mypy_cache',
    '.pytest_cache', '.ruff_cache', 'node_modules', 'dist', 'build',
    '.tox', '.nox', 'site-packages',
}

# Directories considered test/fixture code — their training signals do
# not create GPAI provider obligations (they are self-contained examples).
_TEST_DIR_NAMES = {'tests', 'test', '__tests__', 'testdata', 'fixtures'}


# ---------------------------------------------------------------------------
# Filesystem walk
# ---------------------------------------------------------------------------

def _iter_python_files(project_path: Path, max_files: int = 2000):
    """Yield (relative_path, content) for each .py file under project_path.

    Skips common noise directories, files marked with ``# regula-ignore``
    in their first 10 lines (matches the project-wide suppression convention
    used by scripts/risk_patterns.py et al.), and caps at max_files to keep
    the scan bounded on large monorepos.
    """
    count = 0
    for p in project_path.rglob('*.py'):
        parts = set(p.parts)
        if parts & _SKIP_DIRS:
            continue
        if parts & _TEST_DIR_NAMES:
            continue
        try:
            content = p.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        # Honour the project's `# regula-ignore` file-level suppression marker.
        head = content[:512]
        if 'regula-ignore' in head and 'regula-ignore:' not in head.split('regula-ignore', 1)[1][:1]:
            # bare "regula-ignore" (not "regula-ignore:rule") near the top
            # → skip this file entirely
            continue
        try:
            rel = p.relative_to(project_path)
        except ValueError:
            continue
        yield str(rel), content
        count += 1
        if count >= max_files:
            return


# ---------------------------------------------------------------------------
# Signal detection
# ---------------------------------------------------------------------------

def detect_gpai_signals(project_path: str | Path) -> dict:
    """Scan project_path for GPAI provider / training / crawler signals.

    Returns a dict with boolean summaries and per-label match lists.
    Callers use the match lists to attach file:line evidence to obligations.
    """
    project_path = Path(project_path).resolve()
    signals: dict[str, Any] = {
        'is_training_code': False,
        'has_distribution_code': False,
        'is_crawler_code': False,
        'training_matches': [],
        'crawler_matches': [],
        'robots_compliance_matches': [],
        'robots_bypass_matches': [],
        'files_scanned': 0,
    }

    if not project_path.is_dir():
        return signals

    for rel, content in _iter_python_files(project_path):
        signals['files_scanned'] += 1
        for rgx, label in _TRAINING_SIGNALS:
            if rgx.search(content):
                signals['training_matches'].append((rel, label))
        for rgx, label in _CRAWLER_SIGNALS:
            if rgx.search(content):
                signals['crawler_matches'].append((rel, label))
        for rgx, label in _ROBOTS_COMPLIANCE_SIGNALS:
            if rgx.search(content):
                signals['robots_compliance_matches'].append((rel, label))
        for rgx, label in _ROBOTS_BYPASS_SIGNALS:
            if rgx.search(content):
                signals['robots_bypass_matches'].append((rel, label))

    signals['is_training_code'] = any(
        label not in _TRAINING_DISTRIBUTION_LABELS
        for _, label in signals['training_matches']
    )
    signals['has_distribution_code'] = any(
        label in _TRAINING_DISTRIBUTION_LABELS
        for _, label in signals['training_matches']
    )
    # Require >= 2 distinct crawler labels to avoid flagging a single
    # incidental requests.get() as a crawler.
    distinct_crawler_labels = {label for _, label in signals['crawler_matches']}
    signals['is_crawler_code'] = len(distinct_crawler_labels) >= 2

    return signals


# ---------------------------------------------------------------------------
# Documentation discovery
# ---------------------------------------------------------------------------

_DOC_SEARCH_ROOTS = ['', 'docs', 'doc', 'documentation']


def _find_doc_file(project_path: Path, candidates: list[str]) -> str | None:
    """Return the first candidate doc file that exists, or None.

    Searches at project root and in docs/, doc/, documentation/ subdirs.
    Accepts a directory candidate (trailing '/') and returns its name if
    the directory exists and is non-empty.
    """
    for name in candidates:
        if name.endswith('/'):
            d = project_path / name.rstrip('/')
            if d.is_dir():
                try:
                    if any(d.iterdir()):
                        return name
                except OSError:
                    continue
        else:
            for root in _DOC_SEARCH_ROOTS:
                p = (project_path / root / name) if root else (project_path / name)
                if p.is_file():
                    try:
                        rel = p.relative_to(project_path)
                        return str(rel)
                    except ValueError:
                        return str(p.name)
    return None


def _find_readme_section(project_path: Path, keywords: list[str]) -> str | None:
    """Return the README filename if a heading contains any keyword."""
    for readme in ['README.md', 'README.MD', 'readme.md', 'README.rst', 'README']:
        p = project_path / readme
        if not p.is_file():
            continue
        try:
            content = p.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        for line in content.splitlines():
            s = line.strip().lower()
            if s.startswith('#'):
                for kw in keywords:
                    if kw in s:
                        return readme
    return None


# ---------------------------------------------------------------------------
# Code of Practice metadata loader
# ---------------------------------------------------------------------------

def _load_cop_metadata() -> dict:
    """Load references/gpai_code_of_practice.yaml metadata, best-effort.

    Returns an empty dict if PyYAML is missing or the file is absent.
    """
    try:
        ref_path = Path(__file__).resolve().parent.parent / 'references' / 'gpai_code_of_practice.yaml'
        if not ref_path.is_file():
            return {}
        try:
            import yaml
        except ImportError:
            return {}
        return yaml.safe_load(ref_path.read_text(encoding='utf-8')) or {}
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Obligation evaluators
# ---------------------------------------------------------------------------

def _obligation(chapter: str, oid: str, article: str, summary: str,
                verdict: str, evidence: str) -> dict:
    return {
        'chapter': chapter,
        'obligation_id': oid,
        'article': article,
        'summary': summary,
        'verdict': verdict,
        'evidence': evidence,
    }


def evaluate_transparency(project_path: Path, signals: dict) -> list[dict]:
    """Evaluate the three Transparency chapter obligations."""
    results = []

    # 1. model-documentation
    model_card = _find_doc_file(project_path, [
        'MODEL_CARD.md', 'MODEL_CARD.MD', 'model_card.md',
        'model-card.md', 'ModelCard.md',
        'model_card.yaml', 'model_card.yml',
    ])
    readme_hit = _find_readme_section(project_path, ['model card', 'model details'])
    if model_card:
        verdict, evidence = 'PASS', f'Found {model_card}'
    elif readme_hit:
        verdict = 'WARN'
        evidence = (f'README contains a model-card section but no dedicated '
                    f'MODEL_CARD.md. Extract into a separate file to strengthen the '
                    f'Article 53(1)(a) evidence trail.')
    else:
        verdict = 'FAIL'
        evidence = ('No MODEL_CARD.md or equivalent found at project root or '
                    'docs/. Article 53(1)(a) requires current technical '
                    'documentation of the GPAI model.')
    results.append(_obligation(
        'transparency', 'model-documentation', '53(1)(a)',
        'Maintain current technical documentation of the GPAI model',
        verdict, evidence,
    ))

    # 2. downstream-provider-information (only meaningful if distribution present)
    if signals['has_distribution_code']:
        dl_doc = _find_doc_file(project_path, [
            'DOWNSTREAM.md', 'downstream.md',
            'DOCS.md', 'docs.md', 'docs/index.md',
        ])
        if dl_doc or model_card:
            verdict = 'PASS'
            evidence = f'Distribution code present and documentation at {dl_doc or model_card}.'
        else:
            verdict = 'FAIL'
            evidence = ('Distribution code (push_to_hub / save_pretrained) '
                        'detected but no downstream-facing documentation found. '
                        'Article 53(1)(b) requires information for downstream providers.')
    else:
        verdict = 'N/A'
        evidence = ('No model-distribution code detected. Obligation applies '
                    'at distribution time.')
    results.append(_obligation(
        'transparency', 'downstream-provider-information', '53(1)(b)',
        'Make model information and documentation available to downstream providers',
        verdict, evidence,
    ))

    # 3. training-content-summary
    if signals['is_training_code']:
        data_summary = _find_doc_file(project_path, [
            'TRAINING_DATA_SUMMARY.md', 'training_data_summary.md',
            'DATA_CARD.md', 'data_card.md',
            'DATASHEET.md', 'datasheet.md',
        ])
        readme_data_hit = _find_readme_section(project_path, [
            'training data', 'dataset', 'data sources',
        ])
        if data_summary:
            verdict, evidence = 'PASS', f'Found {data_summary}'
        elif readme_data_hit:
            verdict = 'WARN'
            evidence = ('README mentions training data but no dedicated '
                        'TRAINING_DATA_SUMMARY.md. Article 53(1)(d) requires a '
                        'sufficiently detailed summary using the Commission template.')
        else:
            verdict = 'FAIL'
            evidence = ('Training code detected but no TRAINING_DATA_SUMMARY.md '
                        'or DATA_CARD.md found. Article 53(1)(d) applies.')
    else:
        verdict = 'N/A'
        evidence = ('No training code detected. Obligation applies to GPAI '
                    'model providers only.')
    results.append(_obligation(
        'transparency', 'training-content-summary', '53(1)(d)',
        'Publish a sufficiently detailed summary of content used for training',
        verdict, evidence,
    ))

    return results


def evaluate_copyright(project_path: Path, signals: dict) -> list[dict]:
    """Evaluate the Copyright chapter obligations."""
    results = []

    # 1. written-copyright-policy
    cpol = _find_doc_file(project_path, [
        'COPYRIGHT_POLICY.md', 'copyright_policy.md',
        'COPYRIGHT.md', 'copyright.md',
        'LICENSING.md', 'licensing.md',
    ])
    readme_hit = _find_readme_section(project_path, ['copyright', 'licensing'])
    if cpol:
        verdict, evidence = 'PASS', f'Found {cpol}'
    elif readme_hit:
        verdict = 'WARN'
        evidence = ('README contains a copyright/licensing section but no '
                    'dedicated COPYRIGHT_POLICY.md.')
    else:
        verdict = 'FAIL'
        evidence = ('No written copyright policy found. Article 53(1)(c) '
                    'requires all GPAI providers to maintain a policy to '
                    'comply with Union copyright law.')
    results.append(_obligation(
        'copyright', 'written-copyright-policy', '53(1)(c)',
        'Maintain a written copyright policy published by the provider',
        verdict, evidence,
    ))

    # 2. tdm-optout-compliance
    if signals['is_crawler_code']:
        if signals['robots_bypass_matches']:
            files = sorted({f for f, _ in signals['robots_bypass_matches']})
            verdict = 'FAIL'
            evidence = (f'Crawler code explicitly bypasses robots.txt in: '
                        f'{", ".join(files[:3])}. This conflicts with Article '
                        f'53(1)(c) and the Directive (EU) 2019/790 Art 4 TDM '
                        f'opt-out mechanism.')
        elif signals['robots_compliance_matches']:
            files = sorted({f for f, _ in signals['robots_compliance_matches']})
            verdict = 'PASS'
            evidence = (f'Crawler code with robots.txt / TDMRep handling in: '
                        f'{", ".join(files[:3])}')
        else:
            verdict = 'WARN'
            evidence = ('Data-ingestion/crawler code detected but no robots.txt '
                        'parsing or TDMRep handling found. Add a RobotFileParser '
                        'check before ingesting URLs.')
    else:
        verdict = 'N/A'
        evidence = ('No data-ingestion/crawler code detected. Obligation applies '
                    'at data-collection time.')
    results.append(_obligation(
        'copyright', 'tdm-optout-compliance', '53(1)(c) + 2019/790 Art 4',
        'Honour text-and-data mining opt-outs expressed in a machine-readable manner',
        verdict, evidence,
    ))

    return results


def evaluate_safety_security(project_path: Path, signals: dict,
                             systemic_risk: bool) -> list[dict]:
    """Evaluate the Safety & Security chapter. Only runs when systemic_risk=True."""
    if not systemic_risk:
        return [_obligation(
            'safety_and_security', 'applicability', '55',
            'Safety & Security chapter applies only to systemic-risk GPAI '
            '(cumulative training compute >= 10^25 FLOPs, Article 51)',
            'N/A',
            'Run with --systemic-risk if this provider trains or makes significant '
            'modifications to a model at or above the 10^25 FLOP threshold.',
        )]

    results = []

    # 1. model-evaluation
    eval_hit = _find_doc_file(project_path, [
        'EVAL_REPORT.md', 'eval_report.md',
        'EVALUATION.md', 'evaluation.md',
        'evals/', 'evaluation/', 'benchmarks/',
    ])
    if eval_hit:
        verdict, evidence = 'PASS', f'Evaluation artefact present: {eval_hit}'
    else:
        verdict = 'FAIL'
        evidence = ('No evaluation artefacts (EVAL_REPORT.md, evals/, '
                    'benchmarks/) found. Article 55(1)(a) requires state-of-the-art '
                    'model evaluation including standardised adversarial testing.')
    results.append(_obligation(
        'safety_and_security', 'model-evaluation', '55(1)(a)',
        'Perform state-of-the-art model evaluation including adversarial testing',
        verdict, evidence,
    ))

    # 2. serious-incident-reporting
    incident = _find_doc_file(project_path, [
        'INCIDENT_RESPONSE.md', 'incident_response.md',
        'SECURITY.md', 'security.md',
    ])
    if incident:
        verdict, evidence = 'PASS', f'Found {incident}'
    else:
        verdict = 'FAIL'
        evidence = ('No INCIDENT_RESPONSE.md or SECURITY.md found. Article '
                    '55(1)(c) requires tracking, documenting, and reporting '
                    'serious incidents to the AI Office.')
    results.append(_obligation(
        'safety_and_security', 'serious-incident-reporting', '55(1)(c)',
        'Track, document, and report serious incidents to the AI Office',
        verdict, evidence,
    ))

    # 3. cybersecurity-protection
    sbom_present = any(
        (project_path / name).is_file() for name in
        ('sbom.json', 'bom.json', 'cyclonedx.json', 'SBOM.json', 'cyclonedx.xml')
    )
    signing_detected = False
    # Cheap scan — only look at the first 100 Python files for signing markers
    checked = 0
    for _, content in _iter_python_files(project_path):
        if re.search(r'\bcosign\b|\bsigstore\b|gpg\s+--(sign|verify)', content):
            signing_detected = True
            break
        checked += 1
        if checked >= 100:
            break
    if sbom_present or signing_detected:
        verdict = 'PASS'
        evidence = (f'SBOM present: {sbom_present}, weight-signing markers '
                    f'detected: {signing_detected}.')
    else:
        verdict = 'WARN'
        evidence = ('No SBOM (sbom.json / bom.json / cyclonedx.json) or '
                    'cosign/sigstore/gpg signing markers detected. Article '
                    '55(1)(d) requires adequate cybersecurity protection for '
                    'the model and its infrastructure.')
    results.append(_obligation(
        'safety_and_security', 'cybersecurity-protection', '55(1)(d)',
        'Ensure adequate cybersecurity protection for the model and infrastructure',
        verdict, evidence,
    ))

    return results


# ---------------------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------------------

def run_gpai_check(project_path: str | Path, systemic_risk: bool = False) -> dict:
    """Run the full GPAI Code of Practice check and return a structured result.

    Parameters
    ----------
    project_path : str | Path
        Project root to scan. Only .py files are inspected for training and
        crawler signals; documentation files are discovered by filename.
    systemic_risk : bool
        If True, run Chapter 3 (Safety & Security) checks. These only apply
        to systemic-risk GPAI providers (cumulative training compute >= 10^25
        FLOPs, EU AI Act Article 51).

    Returns
    -------
    dict
        Keys: project_path, is_training_code, is_crawler_code,
        has_distribution_code, systemic_risk_evaluated, cop_status,
        cop_in_force_date, cop_enforcement_begins, obligations, summary,
        overall_verdict, files_scanned.
    """
    pp = Path(project_path).resolve()
    signals = detect_gpai_signals(pp)
    cop = _load_cop_metadata()

    obligations = []
    obligations.extend(evaluate_transparency(pp, signals))
    obligations.extend(evaluate_copyright(pp, signals))
    obligations.extend(evaluate_safety_security(pp, signals, systemic_risk))

    counts = {'PASS': 0, 'WARN': 0, 'FAIL': 0, 'N/A': 0}  # nosec B105 — verdict counters, not credentials
    for o in obligations:
        counts[o['verdict']] = counts.get(o['verdict'], 0) + 1

    if counts['FAIL'] > 0:
        overall = 'FAIL'
    elif counts['WARN'] > 0:
        overall = 'WARN'
    else:
        overall = 'PASS'

    return {
        'project_path': str(pp),
        'is_training_code': signals['is_training_code'],
        'has_distribution_code': signals['has_distribution_code'],
        'is_crawler_code': signals['is_crawler_code'],
        'systemic_risk_evaluated': systemic_risk,
        'files_scanned': signals['files_scanned'],
        'cop_status': cop.get('code_status', 'unknown'),
        'cop_published_date': cop.get('code_published_date', 'unknown'),
        'cop_in_force_date': cop.get('obligations_in_force_date', 'unknown'),
        'cop_enforcement_begins': cop.get('enforcement_actions_begin_date', 'unknown'),
        'obligations': obligations,
        'summary': counts,
        'overall_verdict': overall,
        'disclaimer': (
            'Regula performs pattern-based indication, not a legal determination. '
            'The GPAI Code of Practice provides a rebuttable presumption of '
            'conformity with Articles 53 and 55 — adherence is evidenced by the '
            'concrete practices listed in each chapter, not by this tool alone.'
        ),
    }


# ---------------------------------------------------------------------------
# Text formatter
# ---------------------------------------------------------------------------

_VERDICT_TAG = {  # nosec B105 — display tags for console output, not credentials
    'PASS': '[PASS]',
    'WARN': '[WARN]',
    'FAIL': '[FAIL]',
    'N/A': '[ -- ]',
}

_CHAPTER_TITLES = [
    ('transparency',
     'Chapter 1 - Transparency (all GPAI providers, Art 53)'),
    ('copyright',
     'Chapter 2 - Copyright (all GPAI providers, Art 53(1)(c))'),
    ('safety_and_security',
     'Chapter 3 - Safety & Security (systemic-risk only, Art 55)'),
]


def _wrap(text: str, width: int = 58, indent: str = '           ') -> list[str]:
    """Word-wrap a single string into indent-prefixed lines."""
    out = []
    while text:
        chunk = text[:width]
        if len(text) > width:
            space = chunk.rfind(' ')
            if space > width // 2:
                chunk = text[:space]
        out.append(f'{indent}{chunk.rstrip()}')
        text = text[len(chunk):].strip()
    return out


def format_gpai_check_text(result: dict) -> str:
    """Human-readable report for terminal output."""
    lines = []
    lines.append('')
    lines.append('=' * 64)
    lines.append('  Regula - GPAI Code of Practice Check')
    lines.append('=' * 64)
    lines.append('')
    lines.append(f"  Code of Practice status:      {result['cop_status']}")
    lines.append(f"  Code published:               {result['cop_published_date']}")
    lines.append(f"  Obligations in force:         {result['cop_in_force_date']}")
    lines.append(f"  Enforcement actions begin:    {result['cop_enforcement_begins']}")
    lines.append('')
    lines.append(f"  Project path:                 {result['project_path']}")
    lines.append(f"  Python files scanned:         {result['files_scanned']}")
    lines.append(f"  Training code detected:       {'yes' if result['is_training_code'] else 'no'}")
    lines.append(f"  Distribution code detected:   {'yes' if result['has_distribution_code'] else 'no'}")
    lines.append(f"  Crawler/data ingest detected: {'yes' if result['is_crawler_code'] else 'no'}")
    if result['systemic_risk_evaluated']:
        lines.append("  Systemic-risk evaluated:      yes")
    else:
        lines.append("  Systemic-risk evaluated:      no (pass --systemic-risk for Chapter 3)")
    lines.append('')

    for ch_id, ch_title in _CHAPTER_TITLES:
        chs = [o for o in result['obligations'] if o['chapter'] == ch_id]
        if not chs:
            continue
        lines.append(f"  {ch_title}")
        lines.append('  ' + '-' * 60)
        for o in chs:
            tag = _VERDICT_TAG.get(o['verdict'], f"[{o['verdict']}]")
            lines.append(f"    {tag}  Art {o['article']} - {o['summary']}")
            lines.extend(_wrap(o['evidence']))
        lines.append('')

    s = result['summary']
    lines.append(
        f"  Summary: {s.get('PASS', 0)} pass, {s.get('WARN', 0)} warn, "
        f"{s.get('FAIL', 0)} fail, {s.get('N/A', 0)} not applicable"
    )
    lines.append(f"  Overall verdict: {result['overall_verdict']}")
    lines.append('')
    lines.append('  ' + '-' * 60)
    for line in _wrap(result['disclaimer'], width=60, indent='  '):
        lines.append(line)
    lines.append('')
    return '\n'.join(lines)
