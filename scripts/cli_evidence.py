"""Evidence pack and remediation commands for Regula CLI.

Covers: fix, attest, verify.

NOTE: Do NOT add 'from cli import ...' at module level.
cli.py imports this module (via cli_util) at module level, creating a
circular dependency. All imports from cli must stay inside function bodies.
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def cmd_fix(args) -> None:
    """Generate compliance fix scaffolds for findings."""
    from cli import json_output, _validate_path

    if args.project != ".":
        _validate_path(args.project)
    project_path = str(Path(args.project).resolve())

    from report import scan_files
    from remediation import get_remediation, remediate_observation

    print(f"Scanning {project_path}...", file=sys.stderr)
    findings = scan_files(project_path)

    # Filter to actionable findings across all significant tiers
    actionable_tiers = {"high_risk", "prohibited", "ai_security", "credential_exposure"}
    actionable = [
        f for f in findings
        if f.get("tier") in actionable_tiers and not f.get("suppressed")
    ]

    if not actionable:
        if args.format == "json":
            json_output("fix", {"fixes": [], "message": "No actionable findings."})
        else:
            print("No actionable findings to fix.")
        return

    fixes = []
    seen_obs_keys = set()  # deduplicate observation-based fixes per file
    for finding in actionable:
        rem = get_remediation(
            finding.get("tier", ""),
            finding.get("category", ""),
            finding.get("indicators", []),
            finding.get("file", ""),
            finding.get("description", ""),
        )
        fix_entry = {
            "file": finding.get("file", "?"),
            "line": finding.get("line", "?"),
            "tier": finding["tier"],
            "category": finding.get("category", "unknown"),
            "summary": rem.get("summary", ""),
            "article": rem.get("article", ""),
            "explanation": rem.get("explanation", ""),
            "fix_code": rem.get("fix_code", ""),
        }
        fixes.append(fix_entry)

        # Process governance observations attached to high-risk findings
        for obs in finding.get("observations", []):
            obs_text = obs.get("observation", "")
            obs_key = None
            if "no logging" in obs_text.lower() or "article 12" in obs_text.lower():
                obs_key = "no_logging"
            elif "fairness evaluation" in obs_text.lower():
                obs_key = "missing_fairness_evaluation"
            elif "automated decision" in obs_text.lower() or "article 13" in obs_text.lower():
                obs_key = "automated_decision"

            dedup = (finding.get("file", "?"), obs_key)
            if obs_key and dedup not in seen_obs_keys:
                seen_obs_keys.add(dedup)
                obs_rem = remediate_observation(obs_key)
                if obs_rem:
                    fixes.append({
                        "file": finding.get("file", "?"),
                        "line": finding.get("line", "?"),
                        "tier": "governance_observation",
                        "category": obs_key,
                        "summary": obs_rem["summary"],
                        "article": obs_rem["article"],
                        "explanation": obs_rem["explanation"],
                        "fix_code": obs_rem.get("fix_code", ""),
                    })

    if args.format == "json":
        json_output("fix", {"fixes": fixes, "total": len(fixes)})
    else:
        print(f"# Compliance Fixes \u2014 {len(fixes)} actionable findings\n")
        seen_categories = set()
        for fix in fixes:
            cat = fix["category"]
            if cat in seen_categories:
                continue
            seen_categories.add(cat)

            print(f"## {fix['file']}:{fix['line']} \u2014 {fix['tier'].upper().replace('_', '-')}")
            print(f"   Category: {fix['category']}")
            print(f"   Article: {fix['article']}")
            print(f"   {fix['summary']}")
            print(f"   {fix['explanation']}")
            if fix["fix_code"]:
                print("\n   Suggested code scaffold:")
                print(f"   {'─' * 40}")
                for code_line in fix["fix_code"].replace("\\n", "\n").split("\n"):
                    print(f"   {code_line}")
                print(f"   {'─' * 40}")
            print()

        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            lines = []
            for fix in fixes:
                cat = fix["category"]
                lines.append(f"# {fix['file']}:{fix['line']} \u2014 {fix['article']}")
                lines.append(f"# {fix['summary']}")
                if fix["fix_code"]:
                    lines.append(fix["fix_code"].replace("\\n", "\n"))
                lines.append("")
            out_path.write_text("\n".join(lines), encoding="utf-8")
            print(f"Fix scaffolds written to {out_path}", file=sys.stderr)


def cmd_attest(args) -> None:
    """Generate scan attestation (in-toto Statement v1)."""
    import hmac
    import subprocess
    from cli import _validate_path
    from constants import VERSION
    from report import scan_files
    from findings_view import partition_findings

    _validate_path(args.path)
    project = str(Path(args.path).resolve())
    findings = scan_files(project)

    view = partition_findings(findings)

    # Get git commit if available
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
            cwd=project,
        ).strip()
    except Exception:
        commit = "unknown"

    # Create scan result digest
    scan_json = json.dumps(findings, sort_keys=True, default=str)
    digest = hashlib.sha256(scan_json.encode()).hexdigest()

    statement = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [{
            "name": f"regula-scan-{args.path}",
            "digest": {"sha256": digest},
        }],
        "predicateType": "https://regula.dev/attestation/scan/v1",
        "predicate": {
            "scanner": {
                "name": "regula",
                "version": VERSION,
            },
            "invocation": {
                "parameters": ["check", args.path],
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            },
            "target": {
                "repository": args.path,
                "commit": commit,
            },
            "result": {
                "findings_count": len(findings),
                "prohibited_count": len(view["prohibited"]),
                "high_risk_count": len(view["high_risk"]),
                "digest": digest,
            },
        },
    }

    if args.sign_key:
        key = args.sign_key.encode()
        sig = hmac.new(
            key, json.dumps(statement, sort_keys=True).encode(), hashlib.sha256
        ).hexdigest()
        statement["signatures"] = [{
            "sig": sig,
            "keyid": hashlib.sha256(key).hexdigest()[:16],
        }]

    output = json.dumps(statement, indent=2)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"Attestation written to {args.output}")
    else:
        print(output)


def cmd_verify(args) -> None:
    """Verify the integrity of a Regula Evidence Pack.

    Implements the verification algorithm in `docs/spec/regula-evidence-format-v1.md`
    §7.1. Accepts a pack directory, a manifest.json file, or a .regula.zip archive.

    Exit codes:
      0 — all files verified, pack integrity confirmed
      1 — one or more files MISSING or MODIFIED; do not submit
      2 — manifest unreadable, pack path not found, or format strictly rejected
    """
    from cli import json_output

    pack_path = Path(args.pack_path).resolve()
    warnings: list[str] = []
    extracted_tmpdir = None  # keep reference so it isn't GC'd mid-function

    # --- Resolve input: directory, manifest file, or .zip bundle ---
    if pack_path.is_file() and pack_path.suffix == ".zip":
        # Bundle format per spec §3.2
        import tempfile
        import zipfile
        extracted_tmpdir = tempfile.TemporaryDirectory(prefix="regula-verify-")
        # Decompression-bomb guard: bundles come from third parties, and
        # a small .zip can declare gigabytes of expansion. Evidence packs
        # are megabytes; 500 MB is far above any legitimate pack.
        _MAX_EXTRACT_BYTES = 500 * 1024 * 1024
        _MAX_EXTRACT_MEMBERS = 10_000
        try:
            with zipfile.ZipFile(pack_path) as zf:
                infos = zf.infolist()
                if len(infos) > _MAX_EXTRACT_MEMBERS:
                    print(f"Refusing to extract {pack_path}: {len(infos)} members "
                          f"(limit {_MAX_EXTRACT_MEMBERS})")
                    sys.exit(2)
                declared = sum(zi.file_size for zi in infos)
                if declared > _MAX_EXTRACT_BYTES:
                    print(f"Refusing to extract {pack_path}: declares "
                          f"{declared / 1_048_576:.0f} MB uncompressed "
                          f"(limit {_MAX_EXTRACT_BYTES // 1_048_576} MB) — "
                          "possible decompression bomb")
                    sys.exit(2)
                zf.extractall(extracted_tmpdir.name)
        except zipfile.BadZipFile as exc:
            print(f"Cannot read zip bundle {pack_path}: {exc}")
            sys.exit(2)
        # Find the single top-level pack directory inside the zip
        entries = [p for p in Path(extracted_tmpdir.name).iterdir() if p.is_dir()]
        if len(entries) == 1 and (entries[0] / "manifest.json").exists():
            pack_dir = entries[0]
        else:
            # Zip may contain the pack at root (no wrapping dir)
            pack_dir = Path(extracted_tmpdir.name)
        manifest_path = pack_dir / "manifest.json"
    elif pack_path.is_file() and pack_path.name == "manifest.json":
        manifest_path = pack_path
        pack_dir = pack_path.parent
    elif pack_path.is_dir():
        manifest_path = pack_dir = pack_path
        for candidate in ["manifest.json", "00-assessment-summary.json"]:
            p = pack_path / candidate
            if p.exists():
                manifest_path = p
                break
        else:
            print(
                f"Error: No manifest.json or 00-assessment-summary.json "
                f"found in {pack_path}",
                file=sys.stderr,
            )
            print(
                "  This does not look like a Regula evidence pack. Pass the "
                "pack directory, its manifest.json, or a .regula.zip bundle.",
                file=sys.stderr,
            )
            sys.exit(2)
    else:
        print(f"Error: Path does not exist: {pack_path}", file=sys.stderr)
        print(
            "  Check the path is correct. `regula verify` accepts a pack "
            "directory, a manifest.json file, or a .regula.zip bundle.",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Cannot parse manifest {manifest_path}: {exc}")
        sys.exit(2)

    # --- Format declaration check (spec §7.1 step 2) ---
    pack_format = manifest_data.get("format", "unknown")
    pack_format_version = manifest_data.get("format_version", "unknown")
    pack_regula_version = manifest_data.get("regula_version", "unknown")

    strict = getattr(args, "strict", False)
    if pack_format != "regula.evidence.v1":
        msg = (
            f"Pack does not declare format=regula.evidence.v1 "
            f"(got {pack_format!r}). Proceeding under v0 best-effort semantics."
        )
        if strict:
            print(f"ERROR (strict mode): {msg}")
            sys.exit(2)
        warnings.append(msg)

    hash_algo = manifest_data.get("hash_algorithm", "sha256")
    if hash_algo != "sha256":
        print(f"Unsupported hash_algorithm: {hash_algo}. v1 requires sha256.")
        sys.exit(2)

    # --- Signature verification (spec §4.5 / §7.1 v1.1 addition) ---
    signature_status = None
    signature_detail = ""
    signing_block_present = bool(manifest_data.get("signing"))

    if signing_block_present:
        try:
            from signing import verify_manifest_signature, SigningUnavailable
            try:
                ok, detail = verify_manifest_signature(manifest_data)
                if ok:
                    signature_status = "VERIFIED"
                    signature_detail = detail
                else:
                    signature_status = "INVALID"
                    signature_detail = detail
                    print(f"ERROR: manifest signature did not verify: {detail}")
                    sys.exit(1)
            except Exception as exc:
                signature_status = "INVALID"
                signature_detail = f"{exc.__class__.__name__}: {exc}"
                print(f"ERROR: signature verification raised: {signature_detail}")
                sys.exit(1)
        except ImportError:
            signature_status = "UNVERIFIABLE"
            signature_detail = (
                "manifest carries a signature but the cryptography package "
                "is not installed (`pip install regula-ai[signing]` to verify)"
            )
            if strict:
                print(f"ERROR (strict mode): {signature_detail}")
                sys.exit(2)
            warnings.append(signature_detail)
    else:
        if strict:
            warnings.append(
                "manifest is unsigned (Regula Evidence Format v1.1 signing "
                "block is optional; no authenticated provenance claim)"
            )

    # --- Timestamp verification (spec §4.6 / §7.1 v1.1 addition) ---
    timestamp_status = None
    timestamp_detail = ""
    timestamp_block_present = bool(manifest_data.get("timestamp_authority"))

    if timestamp_block_present:
        try:
            from signing import canonicalize_manifest_for_signing
            from timestamp import verify_manifest_timestamp, TimestampUnavailable
            try:
                canonical = canonicalize_manifest_for_signing(manifest_data)
                ok, detail = verify_manifest_timestamp(manifest_data, canonical)
                if ok:
                    timestamp_status = "VERIFIED"
                    timestamp_detail = detail
                else:
                    timestamp_status = "INVALID"
                    timestamp_detail = detail
                    print(f"ERROR: manifest timestamp did not verify: {detail}")
                    sys.exit(1)
            except Exception as exc:
                timestamp_status = "INVALID"
                timestamp_detail = f"{exc.__class__.__name__}: {exc}"
                print(f"ERROR: timestamp verification raised: {timestamp_detail}")
                sys.exit(1)
        except ImportError:
            timestamp_status = "UNVERIFIABLE"
            timestamp_detail = (
                "manifest carries a timestamp but the asn1crypto package "
                "is not installed (`pip install regula-ai[signing]`)"
            )
            if strict:
                print(f"ERROR (strict mode): {timestamp_detail}")
                sys.exit(2)
            warnings.append(timestamp_detail)
    else:
        if strict:
            warnings.append(
                "manifest is not timestamped (Regula Evidence Format v1.1 "
                "timestamp block is optional; no external provenance claim)"
            )

    files = manifest_data.get("files", [])
    if not files:
        print("No files listed in manifest.")
        sys.exit(2)

    # --- File-by-file verification (spec §7.1 step 3) ---
    passed = 0
    failed = 0
    results = []

    resolved_pack_dir = pack_dir.resolve()
    for entry in files:
        filename = entry.get("filename", entry.get("name", entry.get("path", "")))
        expected_hash = entry.get("sha256", "")

        # Manifests come from third parties: an absolute or ../-crafted
        # filename must not escape the pack directory (arbitrary-file-read
        # oracle, or an indefinite hang hashing a special file).
        if Path(filename).is_absolute() or ".." in Path(filename).parts:
            results.append({"filename": filename, "status": "INVALID_PATH", "expected": expected_hash})
            failed += 1
            continue
        filepath = pack_dir / filename
        try:
            inside = filepath.resolve().is_relative_to(resolved_pack_dir)
        except OSError:
            inside = False
        if not inside or (filepath.exists() and not filepath.is_file()):
            results.append({"filename": filename, "status": "INVALID_PATH", "expected": expected_hash})
            failed += 1
            continue

        if not filepath.exists():
            results.append({"filename": filename, "status": "MISSING", "expected": expected_hash})
            failed += 1
            continue

        actual_hash = hashlib.sha256(filepath.read_bytes()).hexdigest()
        if actual_hash == expected_hash:
            results.append({"filename": filename, "status": "OK"})
            passed += 1
        else:
            results.append({
                "filename": filename, "status": "MODIFIED",
                "expected": expected_hash, "actual": actual_hash,
            })
            failed += 1

    # --- Emit report (spec §7.2) ---
    verify_report = {
        "format": "regula.verify.v1",
        "format_version": "1.0",
        "pack_path": str(pack_path),
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "verifier_version": _regula_version(),
        "pack_format": pack_format,
        "pack_format_version": pack_format_version,
        "pack_regula_version": pack_regula_version,
        "total": len(files),
        "passed": passed,
        "failed": failed,
        "results": results,
    }
    if signature_status is not None:
        verify_report["signature_status"] = signature_status
        verify_report["signature_detail"] = signature_detail
    if timestamp_status is not None:
        verify_report["timestamp_status"] = timestamp_status
        verify_report["timestamp_detail"] = timestamp_detail
    if warnings:
        verify_report["warnings"] = warnings

    if getattr(args, "report", None):
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(verify_report, indent=2), encoding="utf-8")

    if args.format == "json":
        json_output("verify", verify_report)
    else:
        print(f"\nVerifying: {pack_dir}")
        if pack_format != "unknown":
            print(f"  Format: {pack_format} v{pack_format_version} "
                  f"(generated by Regula {pack_regula_version})")
        if signature_status == "VERIFIED":
            print(f"  Signature: VERIFIED ({signature_detail})")
        elif signature_status == "UNVERIFIABLE":
            print(f"  Signature: UNVERIFIABLE ({signature_detail})")
        if timestamp_status == "VERIFIED":
            print(f"  Timestamp: VERIFIED ({timestamp_detail})")
        elif timestamp_status == "UNVERIFIABLE":
            print(f"  Timestamp: UNVERIFIABLE ({timestamp_detail})")
        for w in warnings:
            print(f"  \u26a0\ufe0f  {w}")
        print(f"{'=' * 60}")
        for r in results:
            icon = "\u2713" if r["status"] == "OK" else "\u2717"
            print(f"  {icon} {r['filename']} \u2014 {r['status']}")
        print(f"{'=' * 60}")
        print(f"  {passed}/{len(files)} files verified, {failed} issues")
        if failed > 0:
            print("  WARNING: Pack integrity compromised. Do not submit to auditor.")
            sys.exit(1)
        else:
            print("  All files match manifest. Pack integrity confirmed.")


def _regula_version() -> str:
    """Return the current Regula version string (for verifier_version field)."""
    try:
        from constants import VERSION
        return VERSION
    except ImportError:
        return "unknown"
