"""The tool asks for facts, and now has somewhere to receive them (N149).

Before 2026-08-17: `regula check` reported `insufficient_information` and named
`is_ai_system` and `jurisdiction_in_scope`; `regula assess` asked questions that
answer exactly those two; nothing was written; running `check` again returned
the identical block. Enumerated across `scripts/cli.py` and
`scripts/decision_adapters.py`, no `--fact`, `declared_facts`, `facts_file` or
`sourced_facts` route existed.

These checks run the loop in both directions on a real project through the real
CLI, and pin the four properties that make the repair honest rather than merely
convenient:

* a declared fact is a PERSON'S declaration and says so in its provenance;
* `unknown` is an answer and is never read as `no`;
* a resolved fact may move `insufficient_information` to an `indication` and may
  never produce a tier, a score, a readiness percentage or an effort estimate;
* an unreadable or unknown declaration is refused, not silently dropped.

Module-level functions, not a TestCase: the custom runner binds by scanning
`dir(module)` and a class-based module exposes only class names (N134).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import fact_store as fs
from assess import ANSWER_NOT_MAPPED, ANSWER_TO_FACT, facts_from_answers
from decision_kernel import DecisionKernel
from errors import UsageError

FIXTURE = REPO / "examples" / "cv-screening-app"

# The two facts a bare EU check names when nothing is declared. Asserted rather
# than hardcoded blind: `test_the_bare_decision_still_names_exactly_these`
# re-derives them from the kernel so this pair cannot go stale silently.
BARE_FACTS = ("is_ai_system", "jurisdiction_in_scope")


def _project(tmp: str) -> Path:
    project = Path(tmp) / "proj"
    shutil.copytree(FIXTURE, project)
    return project


def _run(project: Path, *argv, cache: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONPATH=str(REPO), REGULA_CACHE_DIR=cache)
    return subprocess.run(
        [sys.executable, "-m", "scripts.cli", *argv],
        cwd=str(project), env=env, capture_output=True, text=True, timeout=600)


def _named_facts(text: str) -> set:
    """Fact ids the decision block lists as needed."""
    ids = set()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and ":" in stripped:
            candidate = stripped[2:].split(":", 1)[0].strip()
            if candidate and " " not in candidate:
                ids.add(candidate)
    return ids


# --------------------------------------------------------------------------
# The loop, run in both directions through the real CLI
# --------------------------------------------------------------------------

def test_the_loop_closes_end_to_end():
    """check -> the facts it names -> assess writes them -> check consumes them.

    The fail-before half is the first assertion pair and it is not hypothetical:
    it is the state this repository shipped in until this test existed.
    """
    with tempfile.TemporaryDirectory(prefix="regula-factloop-") as tmp:
        project = _project(tmp)
        cache = str(Path(tmp) / "cache")

        before = _run(project, "check", ".", cache=cache)
        named = _named_facts(before.stdout)
        assert set(BARE_FACTS) <= named, (named, before.stdout[:2000])
        assert not (project / ".regula" / "facts.json").exists(), (
            "nothing should be written by a plain check")

        saved = _run(project, "assess", "--answers", "yes,yes,no,yes,no",
                     "--save-facts", cache=cache)
        assert saved.returncode == 0, saved.stderr[-2000:]
        store = project / ".regula" / "facts.json"
        assert store.is_file(), saved.stdout[-2000:]

        after = _run(project, "check", ".", cache=cache)
        after_named = _named_facts(after.stdout)
        # The decision moved: neither fact the first run asked for is asked again.
        for fact_id in BARE_FACTS:
            assert fact_id not in after_named, (fact_id, after.stdout[:3000])
        # And the provenance of every answered fact is visible in the output.
        assert "Declared facts:" in after.stdout
        for fact_id in BARE_FACTS:
            assert fact_id in after.stdout
        assert "user_declaration" in after.stdout
        assert "cli:assess" in after.stdout
        assert "asked:" in after.stdout

        # Control, the other direction: remove the store and the two facts come
        # back. Without this, the assertion above could pass because the second
        # run failed for an unrelated reason.
        store.unlink()
        again = _run(project, "check", ".", cache=cache)
        assert set(BARE_FACTS) <= _named_facts(again.stdout), again.stdout[:2000]


def test_declared_facts_can_reach_an_indication():
    """The point of the loop: a resolved fact set changes the result type."""
    with tempfile.TemporaryDirectory(prefix="regula-factloop-") as tmp:
        project = _project(tmp)
        cache = str(Path(tmp) / "cache")
        result = _run(project, "check", ".", "--format", "json",
                      "--fact", "is_ai_system=yes",
                      "--fact", "jurisdiction_in_scope=yes",
                      "--fact", "eu_annex_iii_use=yes",
                      "--fact", "role_provider=yes",
                      "--fact", "eu_significant_risk=yes", cache=cache)
        payload = json.loads(result.stdout)["data"]
        assert payload["decision"]["result_type"] == "indication", payload["decision"]
        assert payload["declared_facts"], "declared facts absent from the payload"
        assert len(payload["declared_facts"]) == 5


def test_a_declared_fact_never_produces_a_tier_score_readiness_or_effort():
    """The prohibition that makes this repair a correction and not a broadening."""
    banned = ("compliance_score", "risk_tier", "highest_risk_tier", "readiness",
              "effort", "overall_score", "gap_score", "Verdict:")
    with tempfile.TemporaryDirectory(prefix="regula-factloop-") as tmp:
        project = _project(tmp)
        cache = str(Path(tmp) / "cache")
        result = _run(project, "check", ".", "--format", "json",
                      "--fact", "is_ai_system=yes",
                      "--fact", "jurisdiction_in_scope=yes",
                      "--fact", "eu_annex_iii_use=yes",
                      "--fact", "role_provider=yes",
                      "--fact", "eu_significant_risk=yes", cache=cache)
        present = [b for b in banned if b in result.stdout]
        assert present == [], present


def test_unknown_is_an_answer_and_is_never_read_as_no():
    with tempfile.TemporaryDirectory(prefix="regula-factloop-") as tmp:
        project = _project(tmp)
        cache = str(Path(tmp) / "cache")
        result = _run(project, "check", ".", "--format", "json",
                      "--fact", "is_ai_system=unknown", cache=cache)
        payload = json.loads(result.stdout)["data"]
        value = payload["declared_facts"]["is_ai_system"]["values"][0]
        assert value["state"] == "unknown", value
        assert payload["decision"]["result_type"] == "insufficient_information"


def test_contradictory_and_unknown_declarations_are_refused_with_exit_two():
    """N119's rule: refuse rather than report a success the tool did not achieve."""
    with tempfile.TemporaryDirectory(prefix="regula-factloop-") as tmp:
        project = _project(tmp)
        cache = str(Path(tmp) / "cache")
        for argv, needle in (
            (("--fact", "not_a_real_fact=yes"), "not defined by decision model"),
            (("--fact", "is_ai_system=maybe"), "is not a fact state"),
            (("--no-facts", "--fact", "is_ai_system=yes"), "contradicts"),
        ):
            result = _run(project, "check", ".", *argv, cache=cache)
            assert result.returncode == 2, (argv, result.returncode, result.stderr[-800:])
            assert needle in result.stderr, (argv, result.stderr[-800:])


def test_no_facts_ignores_the_store_it_would_otherwise_read():
    with tempfile.TemporaryDirectory(prefix="regula-factloop-") as tmp:
        project = _project(tmp)
        cache = str(Path(tmp) / "cache")
        _run(project, "assess", "--answers", "yes,yes,no,yes,no",
             "--save-facts", cache=cache)
        assert (project / ".regula" / "facts.json").is_file()
        ignored = _run(project, "check", ".", "--no-facts", cache=cache)
        assert set(BARE_FACTS) <= _named_facts(ignored.stdout), ignored.stdout[:2000]
        assert "Declared facts:" not in ignored.stdout


def test_the_bare_decision_still_names_exactly_these_two_facts():
    """Re-derived from the kernel, so BARE_FACTS above cannot go stale silently."""
    kernel = DecisionKernel()
    result = kernel.evaluate({"model_version": kernel.model_version,
                              "jurisdiction": "eu", "facts": {}})
    named = {item["fact_id"] for item in result["unresolved_predicates"]}
    assert named == set(BARE_FACTS), named


# --------------------------------------------------------------------------
# The store itself
# --------------------------------------------------------------------------

def test_every_stored_value_is_a_persons_declaration():
    """Regula establishes no fact. The data says so, not only the docstring."""
    facts, _ = facts_from_answers(
        {"uses_ai": "yes", "eu_users": "yes", "high_risk_domain": "no"})
    assert fs.source_types(facts) == {fs.SOURCE_USER_DECLARATION}, fs.source_types(facts)
    cli_facts = fs.collect_cli_facts(
        ["is_ai_system=yes"], "eu", DecisionKernel().model)
    assert fs.source_types(cli_facts) == {fs.SOURCE_USER_ATTESTATION}
    for source in (facts, cli_facts):
        for entry in source.values():
            for value in entry["values"]:
                assert "tool" not in value["provenance"]["source_type"]
                assert value["provenance"]["source_ref"].startswith("cli:")
                assert value["timestamp"].endswith("+00:00")


def test_the_assess_mapping_is_exact_and_says_what_it_will_not_map():
    """Three of six answers map. The other three are named with their reason.

    A questionnaire answer that silently goes nowhere is what N149 is about, so
    an unmapped answer must be reported rather than dropped.
    """
    answers = {"uses_ai": "yes", "eu_users": "yes", "prohibited": "no",
               "high_risk_domain": "yes", "non_eu_provider": "no"}
    facts, unmapped = facts_from_answers(answers)
    assert set(facts) == {"is_ai_system", "jurisdiction_in_scope", "eu_annex_iii_use"}
    assert set(unmapped) == {"prohibited", "non_eu_provider"}
    assert all(reason for reason in unmapped.values())
    # Every mapped id must exist in the model; a mapping to a fact the kernel
    # does not define would write a declaration nothing can read.
    known = fs.known_fact_ids(DecisionKernel().model)
    for fact_id, _question in ANSWER_TO_FACT.values():
        assert fact_id in known, fact_id
    assert not (set(ANSWER_TO_FACT) & set(ANSWER_NOT_MAPPED)), (
        "an answer cannot be both mapped and declared unmappable")


def test_the_stored_question_is_the_whole_question():
    """`high_risk_domain` means nothing without its nine bullets."""
    facts, _ = facts_from_answers({"high_risk_domain": "yes"})
    question = facts["eu_annex_iii_use"]["values"][0]["provenance"]["question"]
    assert "job candidates" in question, question
    assert "administration of justice" in question, question
    assert "\n" not in question


def test_the_store_fails_closed_on_anything_it_cannot_understand():
    model = DecisionKernel().model
    with tempfile.TemporaryDirectory(prefix="regula-factstore-") as tmp:
        path = Path(tmp) / "facts.json"

        path.write_text("{not json", encoding="utf-8")
        _refuses(path, model, "not valid JSON")

        path.write_text(json.dumps({"schema_version": "9.9", "facts": {}}), encoding="utf-8")
        _refuses(path, model, "schema_version")

        path.write_text(json.dumps({"schema_version": "1.0"}), encoding="utf-8")
        _refuses(path, model, "no `facts` object")

        path.write_text(json.dumps({
            "schema_version": "1.0",
            "facts": {"no_such_fact": {"values": [fs.build_value("yes", "eu", "cli:test")]}},
        }), encoding="utf-8")
        _refuses(path, model, "not defined by decision model")

        path.write_text(json.dumps({
            "schema_version": "1.0",
            "facts": {"is_ai_system": {"values": [{"state": "yes"}]}},
        }), encoding="utf-8")
        _refuses(path, model, "provenance")

        # And the other direction: a well-formed store loads.
        fs.save(path, {"is_ai_system": {"values": [fs.build_value("yes", "eu", "cli:test")]}},
                model["model_version"])
        loaded = fs.load(path, model)
        assert set(loaded["facts"]) == {"is_ai_system"}
        assert loaded["notices"] == []


def _refuses(path, model, needle):
    try:
        fs.load(path, model)
    except fs.FactStoreError as exc:
        assert needle in str(exc), (needle, str(exc))
        assert isinstance(exc, UsageError)
        assert exc.exit_code == 2
    else:
        raise AssertionError(f"a store that should be refused loaded: {needle}")


def test_a_store_from_a_different_model_is_reported_not_silently_applied():
    model = DecisionKernel().model
    with tempfile.TemporaryDirectory(prefix="regula-factstore-") as tmp:
        path = Path(tmp) / "facts.json"
        fs.save(path, {"is_ai_system": {"values": [fs.build_value("yes", "eu", "cli:test")]}},
                "1999-01-01.0")
        loaded = fs.load(path, model)
        assert loaded["facts"], "declarations must not be discarded"
        assert loaded["notices"], "a model-version difference must be reported"
        assert "1999-01-01.0" in loaded["notices"][0]
        assert model["model_version"] in loaded["notices"][0]


def test_merge_replaces_a_fact_rather_than_appending_a_second_answer():
    """Appending would manufacture a contradiction the user never made."""
    old = {"is_ai_system": {"values": [fs.build_value("no", "eu", "cli:old")]}}
    new = {"is_ai_system": {"values": [fs.build_value("yes", "eu", "cli:new")]}}
    merged = fs.merge(old, new)
    assert len(merged["is_ai_system"]["values"]) == 1
    assert merged["is_ai_system"]["values"][0]["state"] == "yes"
    assert merged["is_ai_system"]["values"][0]["provenance"]["source_ref"] == "cli:new"


def test_parse_fact_argument_accepts_every_state_and_refuses_the_rest():
    for state in ("yes", "no", "unknown", "not_applicable"):
        assert fs.parse_fact_argument(f"is_ai_system={state}") == ("is_ai_system", state)
    for bad in ("is_ai_system", "=yes", "is_ai_system=probably", ""):
        try:
            fs.parse_fact_argument(bad)
        except fs.FactStoreError:
            pass
        else:
            raise AssertionError(f"accepted a malformed --fact argument: {bad!r}")


def test_the_store_path_is_project_local():
    """Not `~/.regula`: a fact is about the system, not about the machine."""
    assert fs.STORE_RELATIVE_PATH == ".regula/facts.json"
    assert fs.store_path("/somewhere/else") == Path("/somewhere/else/.regula/facts.json")


def test_describe_shows_who_said_it_and_when():
    facts = {"is_ai_system": {"values": [
        fs.build_value("yes", "eu", "cli:check --fact", question="Is it?")]}}
    lines = "\n".join(fs.describe(facts))
    assert "is_ai_system = yes" in lines
    assert fs.SOURCE_USER_ATTESTATION in lines
    assert "cli:check --fact" in lines
    assert "asked: Is it?" in lines


if __name__ == "__main__":                                     # pragma: no cover
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as exc:                           # noqa: BLE001
                failures += 1
                print(f"FAIL {name}: {exc}")
    print(f"{failures} failure(s)")
    raise SystemExit(1 if failures else 0)
