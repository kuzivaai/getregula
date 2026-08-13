"""Python side of the frozen cross-runtime decision corpus."""

import hashlib
import json
import sys
import types
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from build_decision_conformance import render
from decision_kernel import DecisionInputError, DecisionKernel
from mcp_server import handle_request
from cli_analysis import cmd_questionnaire
from test_api_server import _dispatch_request


ROOT = Path(__file__).parent.parent
CORPUS_PATH = ROOT / "references" / "decision_conformance.v1.json"
MODEL_PATH = ROOT / "references" / "decision_model.v1.json"


def _corpus():
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def test_decision_conformance_corpus_is_current_and_reconciled():
    corpus = _corpus()
    assert CORPUS_PATH.read_text(encoding="utf-8") == render()
    assert corpus["model_sha256"] == hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest()
    assert corpus["counts"]["total"] == len(corpus["vectors"])
    assert corpus["counts"]["reconciled_by_category"] is True
    assert corpus["counts"]["reconciled_by_jurisdiction"] is True


def test_python_matches_every_decision_conformance_vector():
    kernel = DecisionKernel()
    for vector in _corpus()["vectors"]:
        if "error" in vector["expected"]:
            try:
                kernel.evaluate(vector["request"])
            except DecisionInputError as exc:
                assert type(exc).__name__ == vector["expected"]["error"]
            else:
                raise AssertionError(f"{vector['id']} did not reject invalid input")
        else:
            assert kernel.evaluate(vector["request"]) == vector["expected"]["result"], (
                vector["id"]
            )


def test_rest_matches_every_decision_conformance_vector():
    for vector in _corpus()["vectors"]:
        status, body = _dispatch_request(
            "POST",
            "/v1/questionnaire/evaluate",
            json_body={"answers": {}, "decision_request": vector["request"]},
        )
        if "error" in vector["expected"]:
            assert status == 400, vector["id"]
            assert body["error"], vector["id"]
        else:
            assert status == 200, vector["id"]
            assert body["data"] == vector["expected"]["result"], vector["id"]


def test_mcp_matches_every_decision_conformance_vector():
    for index, vector in enumerate(_corpus()["vectors"]):
        response = handle_request({
            "jsonrpc": "2.0",
            "id": index,
            "method": "tools/call",
            "params": {
                "name": "regula_classify",
                "arguments": {
                    "input": "conformance detector input",
                    "decision_request": vector["request"],
                },
            },
        })
        if "error" in vector["expected"]:
            assert response["error"]["code"] == -32602, vector["id"]
            assert response["error"]["message"], vector["id"]
        else:
            actual = response["result"]["structuredContent"]["decision"]
            assert actual == vector["expected"]["result"], vector["id"]


def test_cli_matches_every_decision_conformance_vector():
    for vector in _corpus()["vectors"]:
        captured = []
        fake_cli = types.ModuleType("cli")
        fake_cli.json_output = lambda command, data: captured.append((command, data))
        args = Namespace(
            evaluate=json.dumps(vector["request"]),
            format="json",
        )
        if "error" in vector["expected"]:
            try:
                with patch.dict("sys.modules", {"cli": fake_cli}):
                    cmd_questionnaire(args)
            except DecisionInputError as exc:
                assert type(exc).__name__ == vector["expected"]["error"], vector["id"]
            else:
                raise AssertionError(f"{vector['id']} did not reject invalid input")
        else:
            with patch.dict("sys.modules", {"cli": fake_cli}):
                cmd_questionnaire(args)
            assert captured == [
                ("questionnaire", vector["expected"]["result"])
            ], vector["id"]
