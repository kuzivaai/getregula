#!/usr/bin/env python3
"""Digital Omnibus enactment status — THE single source of truth.

WHEN THE OMNIBUS IS PUBLISHED IN THE OFFICIAL JOURNAL, EDIT ONE LINE:
set ``OMNIBUS_OJ_DATE`` below to the publication date ("YYYY-MM-DD").
Every consumer (report, remediation_plan, evidence_pack, exec_summary,
assess, timeline, roadmap, api_server) derives its deadline copy from
this module, so the flip is a one-line change verified by
tests/test_omnibus_status.py.

Before July 2026 the status prose was hand-copied across six scripts;
the 29 June Council approval had to be manually edited into each one and
two were missed. Do not add a new hardcoded Omnibus status string
anywhere — import from here.

Legislative history: provisional agreement 7 May 2026; European
Parliament approved 16 June 2026 (423/57/174); Council approved
29 June 2026. Entry into force is 3 days after OJ publication.
"""

# ---------------------------------------------------------------------------
# THE flip switch
# ---------------------------------------------------------------------------
OMNIBUS_OJ_DATE = None  # Set to "YYYY-MM-DD" when published in the OJ

OMNIBUS_ENACTED = OMNIBUS_OJ_DATE is not None

# Entry into force is 3 days after OJ publication (see the module docstring /
# legislative history). "In force" copy must key off this DERIVED date, not the
# OJ date itself — otherwise the tool asserts the amendment is legally in force
# up to 3 days early, which is a legal-status overstatement in a compliance
# tool. If the flip date is malformed this raises at import (a loud failure the
# maintainer catches immediately, better than silently wrong deadline copy).
_ENTRY_INTO_FORCE_DELAY_DAYS = 3
if OMNIBUS_OJ_DATE is not None:
    from datetime import datetime as _dt, timedelta as _td
    OMNIBUS_IN_FORCE_DATE = (
        _dt.strptime(OMNIBUS_OJ_DATE, "%Y-%m-%d")
        + _td(days=_ENTRY_INTO_FORCE_DELAY_DAYS)
    ).strftime("%Y-%m-%d")
else:
    OMNIBUS_IN_FORCE_DATE = None

# ---------------------------------------------------------------------------
# Canonical deadline dates (ISO) — machine-readable
# ---------------------------------------------------------------------------
DEADLINE_PROHIBITED        = "2025-02-02"  # Article 5 — not affected by Omnibus
DEADLINE_CURRENT_LAW       = "2026-08-02"  # General high-risk / current law
DEADLINE_OMNIBUS_ANNEX_III = "2027-12-02"  # Omnibus extension for Annex III
DEADLINE_OMNIBUS_ANNEX_I   = "2028-08-02"  # Omnibus extension for Annex I / sectoral
DEADLINE_OMNIBUS_LIMITED   = "2026-12-02"  # Omnibus extension for limited-risk watermarking

# ---------------------------------------------------------------------------
# Canonical prose fragments — human-readable
# ---------------------------------------------------------------------------
ANNEX_III_PROSE = "2 December 2027"
ANNEX_I_PROSE   = "2 August 2028"
LIMITED_PROSE   = "2 December 2026"
ORIGINAL_PROSE  = "2 August 2026"

# Adoption history in the abbreviated form used in CLI output.
ADOPTION_HISTORY = "agreed 7 May 2026, EP approved 16 Jun 2026, Council approved 29 Jun 2026"

OMNIBUS_STATUS = (
    f"Published in OJ {OMNIBUS_OJ_DATE}; in force from {OMNIBUS_IN_FORCE_DATE}"
    if OMNIBUS_ENACTED
    else "EP approved 16 Jun 2026, Council approved 29 Jun 2026; pending OJ publication"
)

# One-line qualifier for deadline copy: what is legally binding right now.
BINDING_NOTE = (
    f"Published in OJ {OMNIBUS_OJ_DATE}; in force from {OMNIBUS_IN_FORCE_DATE} "
    "(3 days after publication)."
    if OMNIBUS_ENACTED
    else "Until publication in the Official Journal, original deadlines remain legally binding."
)


def status_parenthetical() -> str:
    """Short parenthetical for deadline lines, e.g.
    '(Omnibus agreed 7 May 2026, EP approved 16 Jun 2026, Council approved
    29 Jun 2026; pending OJ publication)'."""
    if OMNIBUS_ENACTED:
        return (
            f"(Omnibus {ADOPTION_HISTORY}; published in OJ {OMNIBUS_OJ_DATE}, "
            f"in force from {OMNIBUS_IN_FORCE_DATE})"
        )
    return f"(Omnibus {ADOPTION_HISTORY}; pending OJ publication)"


def annex_iii_deadline_line() -> str:
    """Primary-deadline sentence fragment for Annex III systems."""
    if OMNIBUS_ENACTED:
        return (
            f"{ANNEX_III_PROSE} for Annex III (Omnibus published in OJ "
            f"{OMNIBUS_OJ_DATE}, in force from {OMNIBUS_IN_FORCE_DATE})"
        )
    return (
        f"{ORIGINAL_PROSE} (Omnibus: {ANNEX_III_PROSE} for Annex III, "
        "EP approved 16 Jun 2026, Council approved 29 Jun 2026; pending OJ publication)"
    )
