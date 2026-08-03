Add a new CLI command to Regula named `$ARGUMENTS`.

## Steps

1. **Create the command function** in the `cli_*.py` module that matches its
   concern (`cli_scan.py`, `cli_analysis.py`, `cli_compliance.py`,
   `cli_evidence.py`, `cli_governance.py`, `cli_report.py`, `cli_admin.py`,
   `cli_infra.py`, `cli_monitor.py`, `cli_util.py`), NOT in `scripts/cli.py`.
   `cli.py` keeps `main()` and the subparser wiring only; command bodies were
   split out of it and this file used to say the opposite:
   ```python
   def cmd_$ARGUMENTS(args):
       """Short description."""
       # Implementation here
       if args.format == "json":
           json_output("$ARGUMENTS", result)
       sys.exit(0)
   ```

2. **Add the subparser** in the `main()` function of `scripts/cli.py`:
   ```python
   p = subparsers.add_parser("$ARGUMENTS", help="Short description")
   p.add_argument("--format", "-f", choices=["text", "json"], default="text")
   p.set_defaults(func=cmd_$ARGUMENTS)
   ```

3. **Add tests** to `tests/test_classification.py`:
   - Define the test function
   - Add it to the manual test list at the bottom of the file (inside `if __name__ == "__main__":`)

4. **Run verification**: `/verify`

## Conventions

- Function name: `cmd_$ARGUMENTS` (prefix with `cmd_`)
- Use `json_output("$ARGUMENTS", data)` for JSON output (standard envelope)
- Use `_validate_path()` for any path arguments
- Import dependencies inside the function (lazy loading)
- Exit codes: 0 = success, 1 = findings, 2 = tool error
