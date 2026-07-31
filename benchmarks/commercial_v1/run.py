#!/usr/bin/env python3
"""Execute frozen commercial_v1 cases without reading expected labels."""

import argparse
import hashlib
import json
import os
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path


HERE = Path(__file__).parent
AI_NAMES = (
    "anthropic", "langchain", "llama_index", "ollama", "openai", "sklearn",
    "tensorflow", "torch", "transformers", "xgboost",
)
ARTICLE50_PHRASES = (
    "ai system", "ai-generated", "artificially generated",
    "emotion recognition", "biometric categorisation",
)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


class _VisibleEvidenceParser(HTMLParser):
    """Extract visible text and machine-readable AI marking evidence."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden_depth = 0
        self.text = []
        self.markers = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "template"):
            self.hidden_depth += 1
        pairs = dict(attrs)
        if tag == "meta" and pairs.get("name", "").lower() == "ai-generated":
            self.markers.append(pairs.get("content", ""))

    def handle_endtag(self, tag):
        if tag in ("script", "style", "template") and self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data):
        if not self.hidden_depth:
            self.text.append(data)


def _source_findings(payload, expected_file):
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)
            and Path(str(row.get("file", ""))).name == Path(expected_file).name
            and isinstance(row.get("line"), int) and row.get("indicators")]


def naive_prediction(case):
    content = case["content"].lower()
    if case["candidate"] == "A":
        active = [line.strip() for line in content.splitlines()
                  if not line.lstrip().startswith("#")]
        return any(
            line.startswith(f"import {name}") or
            line.startswith(f"from {name} import")
            for line in active for name in AI_NAMES
        )
    parser = _VisibleEvidenceParser()
    parser.feed(case["content"])
    visible = " ".join(parser.text).lower()
    if "does not use" in visible:
        return False
    return bool(parser.markers) or any(phrase in visible
                                       for phrase in ARTICLE50_PHRASES)


def _command(tool, case_dir, repo):
    if tool == "local_head":
        return [sys.executable, "-m", "scripts.cli", "check", str(case_dir),
                "--format", "json", "--deterministic", "--scope", "all",
                "--min-tier", "limited_risk"]
    raise ValueError(f"unknown executable tool: {tool}")


def _parse_prediction(case, stdout):
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return None, "malformed_json"
    findings = _source_findings(payload, case["relative_path"])
    if case["candidate"] == "A":
        return bool(findings), None
    return any(row.get("tier") == "limited_risk" for row in findings), None


def execute(tool, corpus, repo, output, timeout):
    cases_root = output / "cases"
    raw_root = output / "raw" / tool
    cases_root.mkdir(parents=True, exist_ok=False)
    raw_root.mkdir(parents=True, exist_ok=False)
    records = []
    for case in corpus:
        case_dir = cases_root / case["id"]
        target = case_dir / case["relative_path"]
        target.parent.mkdir(parents=True)
        target.write_text(case["content"])
        if hashlib.sha256(target.read_bytes()).hexdigest() != case["content_sha256"]:
            raise RuntimeError(f"materialised hash mismatch: {case['id']}")
        started = datetime.now(timezone.utc).isoformat()
        start_ns = time.monotonic_ns()
        before_rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        timed_out = False
        if tool == "naive":
            command = ["frozen-naive-baseline", case["candidate"]]
            stdout = json.dumps({"predicted": naive_prediction(case)})
            stderr = ""
            exit_code = 0
            predicted = naive_prediction(case)
            parse_error = None
        else:
            command = _command(tool, case_dir, repo)
            try:
                completed = subprocess.run(
                    command, cwd=repo, capture_output=True, text=True,
                    timeout=timeout, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                )
                stdout, stderr, exit_code = (
                    completed.stdout, completed.stderr, completed.returncode)
            except subprocess.TimeoutExpired as exc:
                stdout = exc.stdout or ""
                stderr = exc.stderr or ""
                exit_code = 124
                timed_out = True
            predicted, parse_error = _parse_prediction(case, stdout)
        finished = datetime.now(timezone.utc).isoformat()
        raw_out = raw_root / f"{case['id']}.stdout"
        raw_err = raw_root / f"{case['id']}.stderr"
        raw_out.write_text(stdout)
        raw_err.write_text(stderr)
        records.append({
            "decision_id": case["id"], "candidate": case["candidate"],
            "language": case["language"], "transform": case["transform"],
            "tool": tool, "command": command, "working_directory": str(repo),
            "started_at": started, "finished_at": finished,
            "duration_seconds": (time.monotonic_ns() - start_ns) / 1e9,
            "peak_memory_kb_delta": max(0, resource.getrusage(
                resource.RUSAGE_CHILDREN).ru_maxrss - before_rss),
            "exit_code": exit_code, "timed_out": timed_out,
            "parse_error": parse_error, "predicted": predicted,
            "input_sha256": case["content_sha256"],
            "stdout_sha256": sha256_bytes(stdout.encode()),
            "stderr_sha256": sha256_bytes(stderr.encode()),
            "raw_stdout": str(raw_out), "raw_stderr": str(raw_err),
        })
    return records


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tool", choices=("naive", "local_head"), required=True)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args(argv)
    if args.output.exists():
        raise SystemExit(f"refusing stale output directory: {args.output}")
    corpus_path = HERE / "corpus.json"
    corpus = json.loads(corpus_path.read_text())
    args.output.mkdir(parents=True)
    records = execute(args.tool, corpus, args.repo.resolve(), args.output,
                      args.timeout)
    payload = {
        "schema_version": "commercial_v1.raw.1",
        "regula_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=args.repo, check=True,
            capture_output=True, text=True).stdout.strip(),
        "corpus_sha256": hashlib.sha256(corpus_path.read_bytes()).hexdigest(),
        "tool": args.tool, "records": records,
    }
    (args.output / "results.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(f"{args.tool}: retained {len(records)} decisions in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
