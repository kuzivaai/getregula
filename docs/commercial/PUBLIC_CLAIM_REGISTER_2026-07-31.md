# Public claim register — 2026-07-31

## Erratum — 2026-08-01: published package

The register's references to PyPI 1.7.4 as the current release are
**CONTRADICTED**. Primary package-registry evidence retrieved 2026-08-01 and
downloaded wheel metadata identify `regula-ai==1.9.0` as current; wheel
SHA-256 `01cde674270adcf08acedf1b79e003c6f083c464944cf158582a14afde93cff3`.
The 1.7.4 findings remain VERSION_BOUND to 1.7.4, while 1.9.0 operational
readiness is UNTESTED by commercial_v1. The published 1.9.0 METADATA contains
the same disputed high-consequence claim classes. Frozen benchmark data and
the local 1.9.0 Candidate A/B results are not altered by this correction.

This register is version-aware. The sentence originally recorded that no public
wording was edited in the 2026-07-31 benchmark session; the separate 2026-08-01
claim-correction session did edit local public-source wording but did not release
or deploy it.

| Exact claim | Active surfaces/version | Disposition and evidence | Exact proposed replacement | Consequence |
|---|---|---|---|---|
| “classifies your system into one of the Act's four risk tiers, and tells you which obligations apply” | README and PyPI 1.7.4 description; related site copy | **LEGAL_REVIEW_REQUIRED and UNTESTED.** Article 6 requires intended purpose/context. Candidate C, the only commercial_v1 job addressing contextual high-risk review, has no independent human labels and was not executed as an accuracy study. Candidate A/B misses do not test this claim. | “Reports code-observable risk indicators and links them to provisions for human review; it does not determine legal classification or which obligations apply.” | release- and pilot-blocking |
| “No external dependencies, no API calls, no data leaves your machine” and “zero network calls during scanning — no DPA required” | README/PyPI 1.7.4; TRUST | **UNTESTABLE and legally overbroad.** Namespace denial unavailable; socket probe invalid. Optional extras exist in wheel metadata. A tool cannot decide whether a DPA is required. | “The stdlib core is designed to scan local files. Network behaviour has not yet been mechanically verified across every command and environment. Optional features add dependencies and may use network services.” | release- and pilot-blocking |
| “Auditor-ready evidence package” | README, CLI help, guides | **VERSION_BOUND / CONTRADICTED in broad form.** Local 1.9.0 strict verification passed, but the tested pack contained 0 observed scan findings; public 1.7.4 strict verification failed. | “Hash-manifested evidence scaffold for reviewer completion; output completeness and legal sufficiency require independent review. Strict v1 verification is available in 1.9.0.” | pilot-blocking |
| “Every metric is CI-enforced and generated from source … independently verified” | README consultant paragraph | **CONTRADICTED.** Merge blocker exits 1; N43 records timing disclaimer gaps; public release counts are stale. | “Selected generated facts have repository checks. Review the versioned evidence register and known failing gates before relying on a number.” | release-blocking |
| “under 30 seconds” / “30 seconds” | README and TRUST | **CONTRADICTED as an unqualified universal bound.** The frozen local `ruff` repository runs took 68.885 and 122.778 seconds; three Regula repository runs also returned non-zero. No frozen hardware, repository-size or command boundary accompanies the public wording. | “Runtime depends on repository size, language mix and environment; no universal runtime bound is claimed.” | material |
| “0 known security findings” | TRUST | **CONTRADICTED as an inventory statement, not proof of vulnerabilities.** SECURITY discloses 42 open high-severity CodeQL alerts, says they are triaged and explains why many are believed false positives. An alert is not automatically a confirmed vulnerability, but the zero wording hides the disclosed open-alert inventory. | “See SECURITY.md for the current, versioned open-alert inventory and disposition; open alerts are not equivalent to confirmed vulnerabilities.” | release-blocking |
| “100% recall” residue and derived precision/recall claims | TRUST, benchmark/history surfaces | **STALE / VERSION_BOUND.** Historical fixture results do not establish current buyer-job performance; commercial_v1 local recall was 0/40 for A and 0/40 for B. | “Historical fixture result; not a current external accuracy estimate. commercial_v1 results are reported separately with corpus, fractions and intervals.” | pilot-blocking |
| current test, pattern and command counts (including a stale PyPI passing-count badge) | README, badges, PyPI 1.7.4, site/generated facts | **STALE / VERSION_BOUND.** Initial HEAD collected 2,628 pytest cases; the custom runner reported 1,060 functions and 1,386 cases. Counts changed again with this harness. | “Version-specific counts only, generated from the named release artefact and command; do not reuse local-HEAD counts for 1.7.4.” | material |
| “independently verifiable” evidence signing/timestamping | TRUST and evidence guide | **VERSION_BOUND.** Local unsigned hash-manifest strict verification passed; no signed or timestamped commercial_v1 pack was tested. | “Unsigned manifest integrity was reproduced for 1.9.0. Signature identity and timestamp trust require the documented keys, dependencies and trust-anchor checks and were not tested here.” | material |
| draft standards are “published” or provide harmonised-standard presumption | standards/blog surfaces | **CONTRADICTED / UNVERIFIED.** Draft/enquiry/formal-vote stages are not OJ citation; no OJ citation was established. | “Draft or voting-stage work item; no Article 40 presumption of conformity is claimed unless and until the exact standard is cited in the Official Journal.” | release-blocking |
| Article 50 and high-risk application dates stated without 2026/1744 transition | README/docs/site/blog and translations where present | **STALE where old dates remain.** PRIMARY-SOURCE VERIFIED transition dates are in the research register. | “Dates reflect Regulation (EU) 2026/1744: identify the exact provision and transition; include the Digital Omnibus caveat and retrieval date.” | release-blocking |

“Not found in reviewed official material” never means a competitor feature or
standard does not exist. Main, local HEAD, PyPI 1.7.4, current README, TRUST,
SECURITY, MODEL_CARD, site source, regional pages, translated pages, generated
facts, badges, CLI help and wheel metadata were in scope. Exact exhaustive
line-by-line disposition remains a successor claim-correction unit; this
register identifies every high-consequence class found in the bounded session.
