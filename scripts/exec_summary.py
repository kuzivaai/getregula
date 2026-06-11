# regula-ignore
"""Executive summary report generator.

Produces a print-optimised standalone HTML document suitable for
forwarding to counsel, attaching to a procurement questionnaire,
or presenting to a board. Zero external dependencies.

This document is an automated scan summary, NOT a conformity
assessment, legal determination, or compliance certificate.
"""

import sys
import socket
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from constants import VERSION


# Plain-English tier descriptions
TIER_DESCRIPTIONS = {
    "prohibited": (
        "This project contains indicators associated with AI practices "
        "not permitted under EU AI Act Article 5."
    ),
    "high_risk": (
        "This project contains indicators associated with HIGH-RISK AI "
        "systems under EU AI Act Annex III. Articles 9\u201315 obligations "
        "may apply (effective 2 December 2027, pending formal adoption of "
        "the Digital Omnibus)."
    ),
    "limited_risk": (
        "This project contains indicators associated with LIMITED-RISK AI "
        "systems under EU AI Act Article 50. Transparency obligations apply "
        "from 2 August 2026."
    ),
    "minimal_risk": (
        "This project contains indicators associated with MINIMAL-RISK AI "
        "systems. No specific EU AI Act obligations apply beyond voluntary "
        "codes of conduct."
    ),
}

TIER_ORDER = ["prohibited", "high_risk", "limited_risk", "minimal_risk",
              "ai_security", "agent_autonomy", "credential_exposure", "bias"]

DISCLAIMER = (
    "This scan detects code-level risk indicators. It cannot determine "
    "whether your system meets the \u2018significant risk\u2019 threshold "
    "under Article 6, whether Article 6(3) exemptions apply, or whether "
    "your intended use falls within a regulated category. These are "
    "contextual determinations requiring legal and domain expertise."
)


def _highest_tier(findings: list[dict]) -> str:
    """Return the highest-severity tier present in findings."""
    tiers = {f.get("tier", "minimal_risk") for f in findings}
    for t in TIER_ORDER:
        if t in tiers:
            return t
    return "minimal_risk"


def _plain_description(finding: dict) -> str:
    """Translate a finding into one sentence a non-technical person can read."""
    desc = finding.get("description", "")
    if desc:
        return desc
    cat = finding.get("category", finding.get("tier", ""))
    return f"Risk indicator detected: {cat}"


def generate_exec_summary(findings: list[dict], project_name: str) -> str:
    """Generate a standalone print-optimised HTML executive summary."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    hostname = socket.gethostname()
    tier = _highest_tier(findings)
    tier_desc = TIER_DESCRIPTIONS.get(tier, TIER_DESCRIPTIONS["minimal_risk"])

    # Top 5 findings by confidence, highest tier first
    sorted_findings = sorted(
        findings,
        key=lambda f: (TIER_ORDER.index(f.get("tier", "minimal_risk"))
                        if f.get("tier", "minimal_risk") in TIER_ORDER
                        else 99,
                        -(f.get("confidence_score", 0))),
    )
    top_findings = sorted_findings[:5]

    findings_rows = ""
    for f in top_findings:
        cat = f.get("category", f.get("tier", "unknown"))
        articles = f.get("applicable_articles", f.get("article", ""))
        if isinstance(articles, list):
            articles = ", ".join(str(a) for a in articles)
        file_line = f"{f.get('file', '?')}:{f.get('line', '?')}"
        desc = _plain_description(f)
        findings_rows += f"""
            <tr>
                <td>{cat}</td>
                <td>{articles}</td>
                <td><code>{file_line}</code></td>
                <td>{desc}</td>
            </tr>"""

    tier_upper = tier.replace("_", " ").upper()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Act Risk Indicator Summary \u2014 {project_name}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
    color: #1a1a2e; background: #ffffff; line-height: 1.6;
    max-width: 800px; margin: 0 auto; padding: 40px 32px;
  }}
  h1 {{ font-size: 1.5rem; color: #1a1a2e; margin-bottom: 4px; }}
  .subtitle {{ color: #6b7280; font-size: 0.95rem; margin-bottom: 24px; font-style: italic; }}
  .meta {{ font-size: 0.85rem; color: #6b7280; margin-bottom: 24px; }}
  .meta span {{ display: inline-block; margin-right: 16px; }}
  .tier-box {{
    background: #f8f9fa; border-left: 4px solid #3b82f6;
    padding: 16px 20px; margin: 24px 0; border-radius: 0 6px 6px 0;
  }}
  .tier-box .tier-label {{
    font-weight: 700; font-size: 1.1rem; color: #1a1a2e; margin-bottom: 4px;
  }}
  .tier-box .tier-desc {{ font-size: 0.9rem; color: #374151; }}
  h2 {{ font-size: 1.1rem; color: #1a1a2e; margin: 24px 0 8px; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; margin: 8px 0 16px; }}
  th {{ text-align: left; font-weight: 600; padding: 6px 8px; border-bottom: 2px solid #e5e7eb; color: #374151; }}
  td {{ padding: 6px 8px; border-bottom: 1px solid #f3f4f6; vertical-align: top; }}
  code {{ font-family: ui-monospace, 'Cascadia Code', monospace; font-size: 0.8rem; background: #f3f4f6; padding: 1px 4px; border-radius: 3px; }}
  .disclaimer {{
    background: #fffbeb; border-left: 4px solid #f59e0b;
    padding: 12px 16px; margin: 24px 0; border-radius: 0 6px 6px 0;
    font-size: 0.85rem; color: #92400e;
  }}
  .disclaimer strong {{ color: #78350f; }}
  .footer {{
    margin-top: 32px; padding-top: 16px; border-top: 1px solid #e5e7eb;
    font-size: 0.75rem; color: #9ca3af; line-height: 1.5;
  }}
  @media print {{
    body {{ padding: 20px; font-size: 11pt; }}
    .tier-box, .disclaimer {{ break-inside: avoid; }}
    .footer {{ position: fixed; bottom: 0; left: 0; right: 0; text-align: center; }}
  }}
</style>
</head>
<body>

<h1>AI Act Risk Indicator Summary</h1>
<p class="subtitle">Technical scan results for review \u2014 not a legal determination</p>

<div class="meta">
  <span><strong>Project:</strong> {project_name}</span>
  <span><strong>Scanned:</strong> {now}</span>
  <span><strong>Regula:</strong> v{VERSION}</span>
</div>

<div class="tier-box">
  <div class="tier-label">Risk tier: {tier_upper}</div>
  <div class="tier-desc">{tier_desc}</div>
</div>

<h2>Top findings</h2>
{"<p style='color:#6b7280;font-size:0.9rem;'>No findings detected.</p>" if not top_findings else f'''
<table>
  <thead>
    <tr><th>Category</th><th>Article</th><th>Location</th><th>Description</th></tr>
  </thead>
  <tbody>{findings_rows}
  </tbody>
</table>'''}

<div class="disclaimer">
  <strong>What this scan can and cannot determine</strong><br>
  {DISCLAIMER}
</div>

<h2>Data residency</h2>
<p style="font-size:0.9rem;">This scan ran locally on <code>{hostname}</code>. No code, findings, or metadata were transmitted.</p>

<h2>Methodology</h2>
<p style="font-size:0.9rem;">Regula v{VERSION}, {_pattern_count()} detection patterns across 8 language families. Benchmark: zero false positives at BLOCK/CI tier (measured on v1.7.0). Full methodology: <a href="https://github.com/kuzivaai/getregula/blob/main/docs/TRUST.md">TRUST.md</a></p>

<div class="footer">
  Generated by Regula (getregula.com). Open source, Apache 2.0.<br>
  This document is an automated scan summary, not a conformity assessment,
  legal determination, or compliance certificate.
</div>

</body>
</html>"""
    return html


def _pattern_count() -> int:
    """Get the canonical pattern count from site_facts."""
    try:
        import site_facts
        facts = site_facts.compute()
        return facts["counts"]["patterns"]["tier_regexes"]
    except Exception:
        return 398  # fallback
