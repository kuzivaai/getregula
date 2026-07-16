# regula-ignore
"""Engagement metadata for consultant-prepared deliverables.

A governance consultant running Regula inside a client engagement needs
client-facing deliverables (executive summary, evidence pack) to carry
the engagement context: who the deliverable is for, who prepared it,
and the engagement reference.

Single source of truth for that metadata. Every deliverable generator
reads it through load_engagement() so the fields, precedence rules, and
validation live in exactly one place (no parallel-path drift).

Sources, in precedence order (highest wins):
  1. CLI flags (--client, --prepared-by, --engagement-ref)
  2. The `engagement:` section of regula-policy.yaml:

       engagement:
         client: "Client Legal Name"
         prepared_by: "Consultant / Firm Name"
         reference: "ENG-2026-014"

All fields are optional. When nothing is configured, load_engagement()
returns an empty dict and deliverables render exactly as before —
output for non-consultant users is byte-identical.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Field order is presentation order in deliverables.
ENGAGEMENT_FIELDS = ("client", "prepared_by", "reference")

# Hard cap per field: engagement metadata is display text, not a
# document store. Prevents pathological policy files from bloating
# manifests and HTML headers.
_MAX_FIELD_LEN = 200


def _clean(value) -> str:
    """Normalise a field value to a bounded, single-line string."""
    if value is None:
        return ""
    text = " ".join(str(value).split())  # collapse whitespace/newlines
    return text[:_MAX_FIELD_LEN]


def load_engagement(policy: dict = None, overrides: dict = None,
                    project_path: str = None) -> dict:
    """Return engagement metadata, or {} when none is configured.

    Args:
        policy: A parsed policy dict. When None, the policy is resolved
            from project_path (if given) and then the standard cached
            locations.
        overrides: Field values from CLI flags. Keys outside
            ENGAGEMENT_FIELDS are ignored. Empty/None values do not
            override policy values.
        project_path: The scanned project directory. Consultants run
            `regula report --project /path/to/client` from outside the
            client directory, so the client project's own policy file
            must win over the CWD one.
    """
    if policy is None:
        from policy_config import get_policy
        policy = None
        if project_path:
            base = Path(project_path)
            for candidate in (base / "regula-policy.yaml",
                              base / "regula-policy.json"):
                if candidate.exists():
                    policy = get_policy(path=str(candidate))
                    break
        if policy is None:
            policy = get_policy()

    section = policy.get("engagement", {}) if isinstance(policy, dict) else {}
    if not isinstance(section, dict):
        section = {}

    result = {}
    for field in ENGAGEMENT_FIELDS:
        value = _clean(section.get(field))
        override = _clean((overrides or {}).get(field))
        if override:
            value = override
        if value:
            result[field] = value
    return result


def engagement_from_args(args) -> dict:
    """Build the CLI-override dict from argparse args (missing attrs OK)."""
    return {
        "client": getattr(args, "client", None),
        "prepared_by": getattr(args, "prepared_by", None),
        "reference": getattr(args, "engagement_ref", None),
    }
