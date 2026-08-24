"""Mechanical privacy and drift guards for the anonymous funnel contract.

These tests establish which event names and properties can leave the browser.
They do not establish that Plausible receives an event, that a visitor is
unique, or that the funnel causes a commercial outcome.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "data" / "analytics_event_spec.json"
MODULE_PATH = ROOT / "site" / "assets" / "analytics.js"


def _spec() -> dict:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def _node(source: str) -> dict:
    completed = subprocess.run(
        ["node", "-e", source],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def test_every_event_has_the_directive_required_fields():
    required = {
        "purpose",
        "trigger",
        "properties",
        "prohibited_properties",
        "denominator",
        "privacy_classification",
        "implementation",
        "test",
        "dashboard_or_report",
    }
    spec = _spec()
    assert spec["format_version"] == 1
    assert spec["events"]
    for name, event in spec["events"].items():
        assert set(event) == required, name
        assert event["denominator"], name
        assert event["test"] == "tests/test_analytics_contract.py", name


def test_global_prohibited_properties_cover_the_owner_directive():
    prohibited = set(_spec()["privacy_boundary"]["prohibited_properties"])
    assert {
        "question_answers",
        "source_code",
        "repository_url",
        "organisation_name",
        "email",
        "ip_derived_profile",
        "free_text",
        "regulatory_result",
        "tracking_identifier",
        "personal_identifier",
    } <= prohibited


def test_browser_module_and_machine_spec_have_the_same_events_and_campaigns():
    source = """
global.location={search:'',pathname:'/',href:'https://getregula.com/'};
global.sessionStorage={getItem:()=>null,setItem:()=>{}};
const a=require('./site/assets/analytics.js');
console.log(JSON.stringify({events:Object.keys(a.eventProperties).sort(),campaigns:a.campaignAllowlists}));
"""
    actual = _node(source)
    spec = _spec()
    assert actual["events"] == sorted(spec["events"])
    assert actual["campaigns"] == spec["campaign_allowlists"]


def test_browser_module_drops_unknown_names_properties_and_campaign_text():
    source = """
let stored={};
global.location={search:'?utm_source=alice@example.com&utm_medium=email&utm_campaign=release-2-0',pathname:'/',href:'https://getregula.com/'};
global.sessionStorage={getItem:k=>stored[k]||null,setItem:(k,v)=>{stored[k]=v}};
global.plausible=()=>{};
const a=require('./site/assets/analytics.js');
console.log(JSON.stringify({
  unknown:a.sanitise('Made Up Event',{email:'alice@example.com'}),
  safe:a.sanitise('Contact Intent',{route:'consultant',email:'alice@example.com',free_text:'secret'})
}));
"""
    actual = _node(source)
    assert actual["unknown"] is None
    assert actual["safe"] == {
        "campaign_medium": "email",
        "campaign_name": "release-2-0",
        "route": "consultant",
    }


def test_browser_module_suppresses_duplicate_logical_events():
    source = """
let calls=[];
global.location={search:'',pathname:'/',href:'https://getregula.com/'};
global.sessionStorage={getItem:()=>null,setItem:()=>{}};
global.plausible=(name,options)=>calls.push({name,options});
const a=require('./site/assets/analytics.js');
const first=a.track('Qualifier Start');
const duplicate=a.track('Qualifier Start');
console.log(JSON.stringify({first,duplicate,calls}));
"""
    actual = _node(source)
    assert actual["first"] is True
    assert actual["duplicate"] is False
    assert [call["name"] for call in actual["calls"]] == ["Qualifier Start"]


def test_site_has_no_uncontracted_literal_plausible_events():
    offenders = []
    literal_call = re.compile(r"(?:window\.)?plausible\(\s*['\"]([^'\"]+)")
    for path in (ROOT / "site").rglob("*"):
        if path.suffix not in {".html", ".js"} or path == MODULE_PATH:
            continue
        text = path.read_text(encoding="utf-8")
        for match in literal_call.finditer(text):
            offenders.append((str(path.relative_to(ROOT)), match.group(1)))
    assert not offenders, offenders


def test_funnel_surfaces_load_the_guard_before_their_event_calls():
    pages = (
        "site/index.html",
        "site/locales/de.html",
        "site/locales/pt-br.html",
        "site/assess/index.html",
        "site/assess/de.html",
        "site/assess/pt-br.html",
        "site/pricing.html",
        "site/sample-report.html",
    )
    for relative in pages:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count('src="/assets/analytics.js"') == 1, relative


def test_reserved_events_do_not_fire_before_the_corresponding_feature_exists():
    corpus = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "site").rglob("*")
        if path.suffix in {".html", ".js"} and path != MODULE_PATH
    )
    assert "Enquiry Prepared" not in corpus
    assert "Documentation Search" not in corpus


def test_assessment_and_scanner_events_do_not_carry_result_properties():
    corpus = "\n".join(
        (ROOT / relative).read_text(encoding="utf-8")
        for relative in (
            "site/assess/assess-flow.js",
            "site/assess/index.html",
            "site/assess/de.html",
            "site/assess/pt-br.html",
        )
    )
    event_lines = "\n".join(
        line for line in corpus.splitlines() if "RegulaAnalytics" in line
    )
    for prohibited in ("result_type", "detector_class", "answered", "jurisdiction", "language"):
        assert prohibited not in event_lines
