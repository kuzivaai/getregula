"""Analysis and assessment commands for Regula CLI.

Covers: deps, bias, owasp-agentic, ai-codegen, docs, questionnaire,
explain-article.

NOTE: Do NOT add 'from cli import ...' at module level.
cli.py imports this module (via cli_util) at module level, creating a
circular dependency. All imports from cli must stay inside function bodies.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def cmd_explain_article(args) -> None:
    """Explain an EU AI Act article in plain language."""
    from cli import json_output
    from explain_articles import ARTICLES

    article_num = args.article.lstrip("article").lstrip("art").lstrip(".").lstrip(" ")

    if article_num not in ARTICLES:
        available = ", ".join(sorted(ARTICLES.keys(), key=lambda x: int(x)))
        print(f"Article {article_num} not found. Available: {available}")
        return

    a = ARTICLES[article_num]

    if args.format == "json":
        json_output("explain-article", {"article": article_num, **a})
        return

    print(f"\n  Article {article_num} \u2014 {a['title']}")
    print(f"  {'=' * (len(a['title']) + len(article_num) + 14)}\n")
    print(f"  {a['summary']}\n")
    print(f"  Who:   {a['who']}")
    print(f"  When:  {a['when']}\n")
    print("  What Regula checks:")
    print(f"  {a['what_regula_checks']}\n")


def cmd_deps(args) -> None:
    """Dependency supply chain analysis."""
    from cli import json_output, _validate_path

    if args.project != ".":
        _validate_path(args.project)
    from dependency_scan import scan_dependencies, format_dep_text
    results = scan_dependencies(args.project)
    # Compute the verdict exit code ONCE so json and text modes agree
    # (DEF-008 class: json_output("deps", ...) previously always hardcoded
    # envelope exit_code=0, contradicting the real process exit code when
    # compromised dependencies are found — unconditionally, not even
    # gated behind --strict — or when --strict + low pinning_score applies).
    _deps_exit = 0
    if results.get("compromised_count", 0) > 0:
        _deps_exit = 1
    elif args.strict and results.get("pinning_score", 100) < 50:
        _deps_exit = 1
    if args.format == "json":
        json_output("deps", results, exit_code=_deps_exit)
    else:
        print(format_dep_text(results))
    if _deps_exit:
        sys.exit(_deps_exit)


def cmd_bias(args) -> None:
    """Evaluate model stereotype bias using multiple benchmarks."""
    # Pre-flight: check Ollama is available.
    # --endpoint is an unvalidated CLI string, so the scheme is checked before
    # it reaches urlopen, exactly as bias_eval and bias_bbq already do. Without
    # this, file://, gopher:// and cloud metadata addresses reached urlopen.
    import urllib.request
    from bias_stats import require_http_url
    try:
        require_http_url(args.endpoint)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(2)
    try:
        urllib.request.urlopen(f"{args.endpoint}/api/tags", timeout=5)  # nosec B310  # nosemgrep: dynamic-urllib-use-detected — scheme validated by require_http_url above
    except Exception:
        print("Error: Cannot connect to Ollama at " + args.endpoint, file=sys.stderr)
        print("", file=sys.stderr)
        print("The bias command requires a local Ollama instance with a model loaded.", file=sys.stderr)
        print("Setup steps:", file=sys.stderr)
        print("  1. Install Ollama: https://ollama.ai/download", file=sys.stderr)
        print("  2. Pull a model: ollama pull llama3", file=sys.stderr)
        print("  3. Start Ollama: ollama serve", file=sys.stderr)
        print("  4. Run: regula bias --model llama3", file=sys.stderr)
        sys.exit(2)

    from cli import json_output
    from bias_eval import load_crowspairs_sample, evaluate_with_ollama
    from bias_bbq import load_bbq_sample, evaluate_bbq_full
    from bias_report import format_text_report, format_json_report, format_annex_iv

    benchmark = getattr(args, "benchmark", "all")
    method = getattr(args, "method", "auto")
    method_arg = None if method == "auto" else method
    seed = getattr(args, "seed", None)
    confidence_n = getattr(args, "confidence", 1000)
    fmt = getattr(args, "format", "text")

    crowspairs_result = None
    bbq_result = None

    if benchmark in ("all", "crowspairs"):
        pairs = load_crowspairs_sample(csv_path=getattr(args, "csv", None), max_pairs=args.sample)
        print(f"CrowS-Pairs: loaded {len(pairs)} pairs. Evaluating with {args.model}...", file=sys.stderr)
        crowspairs_result = evaluate_with_ollama(
            pairs, model=args.model, endpoint=args.endpoint,
            method=method_arg, seed=seed, bootstrap_resamples=confidence_n,
        )

    if benchmark in ("all", "bbq"):
        items = load_bbq_sample(max_items=args.sample)
        print(f"BBQ: loaded {len(items)} items. Evaluating with {args.model}...", file=sys.stderr)
        bbq_result = evaluate_bbq_full(items, model=args.model, endpoint=args.endpoint)

    all_error = True
    if crowspairs_result and crowspairs_result.get("status") == "ok":
        all_error = False
    if bbq_result and bbq_result.get("status") == "ok":
        all_error = False

    if all_error:
        msg = "All benchmarks failed"
        if crowspairs_result:
            msg += f" \u2014 CrowS-Pairs: {crowspairs_result.get('message', 'unknown error')}"
        if bbq_result:
            msg += f" \u2014 BBQ: {bbq_result.get('message', 'unknown error')}"
        if fmt == "json":
            json_output("bias", {"status": "error", "message": msg}, exit_code=1)
        else:
            print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    if fmt == "json":
        report = format_json_report(crowspairs_result, bbq_result, args.model, args.endpoint, seed)
        json_output("bias", report)
    elif fmt == "annex-iv":
        print(format_annex_iv(crowspairs_result, bbq_result, args.model, args.endpoint))
    else:
        print(format_text_report(crowspairs_result, bbq_result, args.model, args.endpoint))


def cmd_questionnaire(args) -> None:
    """Context-driven risk assessment questionnaire."""
    from cli import json_output
    from questionnaire import (
        evaluate_questionnaire,
        format_decision_result_cli,
        format_questionnaire_cli,
        generate_questionnaire,
    )
    if args.evaluate:
        try:
            candidate = args.evaluate.lstrip()
            if candidate.startswith(("{", "[")):
                answers = json.loads(args.evaluate)
            else:
                answers = json.loads(Path(args.evaluate).read_text())
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        if (
            isinstance(answers, dict)
            and {"jurisdiction", "facts"}.issubset(answers)
        ):
            from decision_adapters import evaluate_payload
            result = evaluate_payload(answers)
        else:
            result = evaluate_questionnaire(answers)
        if args.format == "json":
            json_output("questionnaire", result)
            return
        print(format_decision_result_cli(result))
    else:
        q = generate_questionnaire()
        if args.format == "json":
            json_output("questionnaire", q)
        else:
            print(format_questionnaire_cli(q))


def cmd_docs(args) -> None:
    """Generate documentation scaffolds."""
    from generate_documentation import scan_project, generate_annex_iv, generate_qms_scaffold, generate_model_card
    from classify_risk import RiskTier
    from decision_adapters import (
        empty_decision,
        format_decision_text,
        unresolved_documentation_draft,
    )

    project_path = str(Path(args.project).resolve())
    project_name = args.name or Path(project_path).name

    print(f"Scanning {project_path}...")
    findings = scan_project(project_path)

    ai_count = len(findings["ai_files"])
    model_count = len(findings["model_files"])
    highest = findings["highest_risk"]
    if isinstance(highest, RiskTier):
        highest = highest.value
    decision = empty_decision("eu", "cli:docs")
    print(format_decision_text(decision))
    print(
        f"Detector observations: {ai_count} AI-related files, "
        f"{model_count} model files; detector class "
        f"{highest.upper().replace('_', '-')}"
    )

    # "docs" is the argparse default sentinel, not a user choice. Resolve it
    # against the PROJECT, not the CWD — otherwise running the docs command
    # (or any test that exercises it) from the Regula repo root writes
    # <cwd>/docs/<project>_annex_iv.md into this repo. 56 junk
    # docs/tmp*_annex_iv.md files accumulated exactly this way, and the
    # pdf branch below already resolves the sentinel per-project.
    if getattr(args, "output", None) and args.output != "docs":
        output_dir = Path(args.output)
    else:
        output_dir = Path(project_path) / "docs"
    output_dir.mkdir(parents=True, exist_ok=True)

    fmt = getattr(args, "format", "markdown")

    if fmt == "pdf":
        from pdf_export import generate_annex_iv_html, render_to_pdf
        html = generate_annex_iv_html(project_path, system_name=project_name)
        gate = unresolved_documentation_draft("", project_path=project_path)
        html = html.replace("<body>", f"<body><pre>{gate}</pre>", 1)
        pdf_bytes = render_to_pdf(html, fallback_to_html=True)
        out_path = Path(args.output) if getattr(args, "output", None) and args.output != "docs" else Path(project_path) / "annex_iv.pdf"
        if pdf_bytes[:4] == b'%PDF':
            out_path.write_bytes(pdf_bytes)
            print(f"PDF written to: {out_path}")
        else:
            html_path = out_path.with_suffix(".html")
            html_path.write_text(html, encoding="utf-8")
            print(f"weasyprint not installed. HTML written to: {html_path}")
            print("Open in browser \u2192 File \u2192 Print \u2192 Save as PDF")
    elif fmt == "conformity-declaration":
        from generate_documentation import generate_conformity_declaration
        doc = generate_conformity_declaration(project_path, system_name=project_name)
        doc = unresolved_documentation_draft(doc, project_path=project_path)
        out_path = Path(project_path) / "declaration_of_conformity.md"
        out_path.write_text(doc, encoding="utf-8")
        print(f"Declaration of Conformity scaffold written to: {out_path}")
        print("IMPORTANT: This document requires legal review and authorised signature before use.")
    elif fmt == "model-card":
        card = generate_model_card(findings, project_name, project_path)
        card = unresolved_documentation_draft(card, project_path=project_path)
        card_file = output_dir / f"{project_name}_model_card.md"
        card_file.write_text(card, encoding="utf-8")
        print(f"Model card written to {card_file}")
    else:
        # Annex IV
        output_file = output_dir / f"{project_name}_annex_iv.md"
        doc = generate_annex_iv(findings, project_name, project_path)
        doc = unresolved_documentation_draft(doc, project_path=project_path)
        output_file.write_text(doc, encoding="utf-8")
        print(f"Annex IV documentation written to {output_file}")

        # Completion report
        if getattr(args, "completion", False):
            from generate_documentation import generate_completion_report
            print()
            print(generate_completion_report(project_name))

        # QMS scaffold
        if args.qms or getattr(args, "all", False):
            qms_file = output_dir / f"{project_name}_qms.md"
            qms_doc = generate_qms_scaffold(findings, project_name, project_path)
            qms_doc = unresolved_documentation_draft(
                qms_doc, project_path=project_path
            )
            qms_file.write_text(qms_doc, encoding="utf-8")
            print(f"QMS scaffold written to {qms_file}")

    try:
        from log_event import log_event as _log
        _log("documentation_generated", {
            "project": project_name, "highest_risk": highest,
            "ai_files": ai_count, "model_files": model_count,
            "types": ["annex_iv"] + (["qms"] if args.qms or getattr(args, "all", False) else []),
        }, project_path=project_path)
    except (OSError,):
        pass  # audit log write failed; non-critical


def cmd_owasp_agentic(args) -> None:
    """OWASP Top 10 for Agentic Applications assessment."""
    from cli import json_output, _validate_path
    from agent_monitor import assess_owasp_agentic, format_owasp_agentic_text

    if args.project != ".":
        _validate_path(args.project)
    result = assess_owasp_agentic(args.project)
    fmt = getattr(args, "format", "text")
    # Compute the verdict exit code ONCE so json and text modes agree
    # (DEF-008 class: json_output("owasp-agentic", ...) previously always
    # hardcoded envelope exit_code=0, contradicting the real process exit
    # code under --strict/--ci with an at_risk finding).
    _owasp_exit = 0
    if getattr(args, "strict", False) or getattr(args, "ci", False):
        at_risk = [r for r in result.get("risks", []) if r.get("status") == "at_risk"]
        if at_risk:
            _owasp_exit = 1
    if fmt == "json":
        json_output("owasp-agentic", result, exit_code=_owasp_exit)
    else:
        print(format_owasp_agentic_text(result))
    if _owasp_exit:
        sys.exit(_owasp_exit)


def cmd_ai_codegen(args) -> None:
    """AI-generated code governance scanner."""
    from cli import json_output, _validate_path
    from ai_code_governance import scan_ai_generated_code, format_ai_codegen_text

    if args.project != ".":
        _validate_path(args.project)
    result = scan_ai_generated_code(
        args.project,
        include_git=not getattr(args, "no_git", False),
    )
    fmt = getattr(args, "format", "text")
    # Compute the verdict exit code ONCE so json and text modes agree
    # (DEF-008 class: json_output("ai-codegen", ...) previously always
    # hardcoded envelope exit_code=0, contradicting the real process exit
    # code under --strict/--ci when transparency_compliant is False).
    #  named scripts/cli.py:1646 (the help text) as the place --strict
    # turned a determination into a CI failure. This is the line that actually
    # does it, and it was not in that enumeration. The flag keeps its behaviour,
    # which is a legitimate gate: "fail the build if a required document is
    # missing" is a real, code-observable condition. Only the key it reads
    # changes, so what the exit code MEANS is now what it can support.
    _codegen_exit = 0
    if getattr(args, "strict", False) or getattr(args, "ci", False):
        if not result.get("summary", {}).get("transparency_documents_present", False):
            _codegen_exit = 1
    if fmt == "json":
        json_output("ai-codegen", result, exit_code=_codegen_exit)
    else:
        print(format_ai_codegen_text(result))
    if _codegen_exit:
        sys.exit(_codegen_exit)
