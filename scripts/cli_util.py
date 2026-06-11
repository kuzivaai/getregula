"""Utility commands for Regula CLI — re-export shim.

Split in May 2026 from a 1116-line monolith into focused modules:
  - cli_infra.py     — doctor, self-test, config, install, quickstart, init,
                       telemetry, metrics, security-self-check
  - cli_evidence.py  — fix, attest, verify
  - cli_analysis.py  — deps, bias, owasp-agentic, ai-codegen, docs,
                       questionnaire, explain-article
  - cli_admin.py     — status, audit, session, timeline, regwatch, feed,
                       api-server, mcp-server

This file re-exports every cmd_* so that cli.py's single import statement
continues to work without changes.

NOTE: Do NOT add 'from cli import ...' at module level.
cli.py imports this module at module level, creating a circular dependency.
All imports from cli must stay inside function bodies.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Infrastructure & setup
from cli_infra import (  # noqa: F401
    cmd_doctor, cmd_self_test, cmd_config, cmd_install,
    cmd_quickstart, cmd_init, cmd_telemetry, cmd_metrics,
    cmd_security_self_check,
)

# Evidence pack & remediation
from cli_evidence import (  # noqa: F401
    cmd_fix, cmd_attest, cmd_verify,
)

# Analysis & assessment
from cli_analysis import (  # noqa: F401
    cmd_explain_article, cmd_deps, cmd_bias,
    cmd_questionnaire, cmd_docs,
    cmd_owasp_agentic, cmd_ai_codegen,
)

# Admin, registry & operations
from cli_admin import (  # noqa: F401
    cmd_timeline, cmd_regwatch, cmd_feed,
    cmd_status, cmd_audit, cmd_session,
    cmd_api_server, cmd_mcp_server,
)
