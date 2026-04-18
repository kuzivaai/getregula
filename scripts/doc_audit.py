"""Document quality scoring engine for EU AI Act compliance docs.

Scores compliance documents 0-100 based on coverage, depth, and structure
per EU AI Act article (Articles 9-15).

Honest limitation: scores structural completeness, not semantic adequacy.
"""

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


# ---------------------------------------------------------------------------
# Article checklists — keyed by article number
# ---------------------------------------------------------------------------

ARTICLE_CHECKLISTS = {
    "9": {
        "name": "Risk Management (Article 9)",
        "doc_patterns": ["risk_management", "risk-management"],
        "sections": [
            ("hazard identification", 10),
            ("residual risk", 10),
            ("testing", 10),
            ("mitigation", 10),
        ],
        "depth_terms": [
            "risk assessment", "risk register", "likelihood", "severity",
            "risk treatment", "continuous", "lifecycle",
        ],
    },
    "10": {
        "name": "Data Governance (Article 10)",
        "doc_patterns": ["data_governance", "data-governance"],
        "sections": [
            ("training data", 10),
            ("data quality", 10),
            ("bias", 10),
            ("representat", 10),
        ],
        "depth_terms": [
            "dataset", "annotation", "labelling", "validation set",
            "demographic", "preprocessing",
        ],
    },
    "11": {
        "name": "Technical Documentation (Article 11)",
        "doc_patterns": ["technical_documentation", "technical-documentation", "tech_doc"],
        "sections": [
            ("system description", 10),
            ("design specification", 10),
            ("development process", 10),
            ("intended purpose", 10),
        ],
        "depth_terms": [
            "architecture", "algorithm", "training", "validation",
            "performance", "hardware", "software version",
        ],
    },
    "12": {
        "name": "Record-Keeping (Article 12)",
        "doc_patterns": ["record_keeping", "record-keeping", "recordkeeping"],
        "sections": [
            ("logging", 10),
            ("retention", 10),
            ("audit trail", 10),
            ("traceability", 10),
        ],
        "depth_terms": [
            "event log", "timestamp", "duration", "tamper",
            "integrity", "storage", "deletion",
        ],
    },
    "13": {
        "name": "Transparency (Article 13)",
        "doc_patterns": ["transparency"],
        "sections": [
            ("user instruction", 10),
            ("capability", 10),
            ("limitation", 10),
            ("human oversight", 10),
        ],
        "depth_terms": [
            "disclosure", "inform", "understand", "accuracy",
            "error rate", "foreseeable misuse",
        ],
    },
    "14": {
        "name": "Human Oversight (Article 14)",
        "doc_patterns": ["human_oversight", "human-oversight"],
        "sections": [
            ("oversight measure", 10),
            ("human-machine interface", 10),
            ("intervention", 10),
            ("override", 10),
        ],
        "depth_terms": [
            "review", "approve", "reject", "escalat",
            "monitor", "stop", "disable",
        ],
    },
    "15": {
        "name": "Accuracy/Robustness/Cybersecurity (Article 15)",
        "doc_patterns": [
            "accuracy", "robustness", "cybersecurity",
            "accuracy_robustness", "accuracy-robustness",
        ],
        "sections": [
            ("accuracy", 10),
            ("error", 10),
            ("robustness", 10),
            ("cybersecurity", 10),
        ],
        "depth_terms": [
            "metric", "benchmark", "adversarial", "resilience",
            "redundancy", "fallback", "encryption", "vulnerability",
        ],
    },
}


# ---------------------------------------------------------------------------
# Filename-to-article mapping
# ---------------------------------------------------------------------------

_DOC_ARTICLE_MAP = {
    pat: art_num
    for art_num, checklist in ARTICLE_CHECKLISTS.items()
    for pat in checklist["doc_patterns"]
}


def _match_article(filename):
    """Return article number for a filename, or None."""
    lower = filename.lower()
    # Strip extension for matching
    stem = Path(lower).stem
    for pattern, article in _DOC_ARTICLE_MAP.items():
        if pattern in stem:
            return article
    return None


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_document(content: str, article: str) -> dict:
    """Score a document against an article checklist.

    Returns dict with coverage, depth, structure, total, article,
    article_name, and gaps.
    """
    checklist = ARTICLE_CHECKLISTS.get(str(article))
    if not checklist:
        return {
            "coverage": 0, "depth": 0, "structure": 0, "total": 0,
            "article": str(article), "article_name": f"Article {article}",
            "gaps": [f"No checklist for Article {article}"],
        }

    content_lower = content.lower()
    gaps = []

    # --- Coverage (0-40): section keywords found --------------------------
    coverage = 0
    for keyword, weight in checklist["sections"]:
        if keyword.lower() in content_lower:
            coverage += weight
        else:
            gaps.append(f"Missing section: {keyword}")

    # --- Depth (0-40): word count (0-20) + depth terms (0-20) -------------
    words = content.split()
    word_count = len(words)

    # Word count scoring: 0 at 0 words, 20 at 2000+ words, linear between
    wc_score = min(20, int(20 * word_count / 2000)) if word_count > 0 else 0

    # Depth terms ratio
    depth_terms = checklist["depth_terms"]
    terms_found = sum(1 for t in depth_terms if t.lower() in content_lower)
    dt_score = int(20 * terms_found / len(depth_terms)) if depth_terms else 0

    depth = wc_score + dt_score

    # --- Structure (0-20): headings + version/date + author/owner ---------
    # Markdown headings (0-8)
    headings = re.findall(r"^#{1,6}\s+.+", content, re.MULTILINE)
    heading_score = min(8, len(headings) * 2)

    # Version or date present (0-6)
    has_version = bool(re.search(r"(?:version|v\d)", content_lower))
    has_date = bool(re.search(r"\d{4}-\d{2}-\d{2}", content))
    version_date_score = 0
    if has_version:
        version_date_score += 3
    if has_date:
        version_date_score += 3

    # Author or owner (0-6)
    has_author = bool(re.search(r"(?:author|owner|prepared by|maintained by)", content_lower))
    author_score = 6 if has_author else 0

    structure = heading_score + version_date_score + author_score

    total = coverage + depth + structure

    return {
        "coverage": coverage,
        "depth": depth,
        "structure": structure,
        "total": total,
        "article": str(article),
        "article_name": checklist["name"],
        "gaps": gaps,
    }


# ---------------------------------------------------------------------------
# Project auditor
# ---------------------------------------------------------------------------

def audit_project(project_path: str) -> list:
    """Scan project root and docs/ for compliance documents.

    Returns list of scored results, one per matched document.
    """
    results = []
    search_dirs = [project_path]

    docs_dir = os.path.join(project_path, "docs")
    if os.path.isdir(docs_dir):
        search_dirs.append(docs_dir)

    seen = set()
    for search_dir in search_dirs:
        try:
            entries = os.listdir(search_dir)
        except OSError:
            continue

        for entry in sorted(entries):
            filepath = os.path.join(search_dir, entry)
            if not os.path.isfile(filepath):
                continue
            if not entry.lower().endswith(".md"):
                continue

            article = _match_article(entry)
            if article is None:
                continue

            # Avoid scoring the same file twice (e.g. if docs/ is a
            # symlink back to root)
            real = os.path.realpath(filepath)
            if real in seen:
                continue
            seen.add(real)

            try:
                content = Path(filepath).read_text(encoding="utf-8")
            except OSError:
                continue

            result = score_document(content, article)
            result["filename"] = entry
            result["path"] = filepath
            results.append(result)

    return results
