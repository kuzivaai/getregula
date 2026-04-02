# regula-ignore
"""Custom exception hierarchy for Regula CLI.

Exit code convention (research-validated, scanner industry standard):
  0 = success, no actionable findings
  1 = findings detected (BLOCK/WARN/prohibited)
  2 = tool error (bad config, missing path, parse failure)
"""


class RegulaError(Exception):
    """Base for all Regula errors. CLI catches this and prints cleanly."""
    exit_code = 1


class PathError(RegulaError):
    """Target path doesn't exist or isn't accessible."""
    exit_code = 2


class ConfigError(RegulaError):
    """Bad or missing configuration file."""
    exit_code = 2


class ParseError(RegulaError):
    """File couldn't be parsed (bad JSON, YAML, syntax)."""
    exit_code = 2


class DependencyError(RegulaError):
    """Optional dependency missing and needed for requested operation."""
    exit_code = 2
