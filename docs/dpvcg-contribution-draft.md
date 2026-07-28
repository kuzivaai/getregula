# DPVCG contribution draft (owner posts; do NOT post autonomously)

Target: https://github.com/w3c/dpv/issues/229 ("Update EU-AIAct extension
with practical concepts", open, asks for "representing more of AIAct
itself"). Secondary fit: #199 (GPAI Code of Practice concepts, help-wanted).

Both issues verified open on 27 Jul 2026. Post as a comment on #229 first;
reference #199 only if the maintainers ask about scope.

---

Suggested comment text (plain, no em dashes, honest):

Hello, I maintain Regula (getregula.com), an open-source EU AI Act risk
scanner that exports scan results tagged with EU-AIAct concept IRIs
(validated against the 2.3 term set at build time, so it never emits a
concept the vocabulary does not define).

Two things that may be useful for this issue:

1. Amendment/change concepts. The Digital Omnibus on AI (Regulation (EU)
2026/1744, OJ 24 July 2026, in force 27 July 2026) changed the AI Act's
application dates and added Article 5 points (ba)/(bb). We maintain a
machine-readable delta-log of AI Act changes (JSON-LD, ELI-based act
relations, primary-source links and dated verification grades):
https://github.com/kuzivaai/getregula/tree/main/content/regulations/delta-log
Representing regulatory change events is currently outside EU-AIAct's
concept set. If the group is open to it, we would like to propose a small
set of change-event concepts (for example ApplicationDateDeferred,
ProvisionAdded, ProvisionAmended, with dct:date and ELI act references)
and contribute the Omnibus delta (2024/1689 to 2026/1744) as the first
worked example. If this is out of scope for the extension, we are happy to
keep it in our own namespace and simply align identifiers.

2. Omnibus-introduced concepts. The Omnibus adds definitions the extension
may want to carry once stable, for example SME/SMC references (Article 3
points (14a)/(14b), the SMC by reference to Recommendation (EU) 2025/1099)
and the simplified technical documentation route in amended Article 11(1).
We can draft these as a PR against the 2.4 milestone if useful.

No expectation either way; the delta-log stays published regardless, and we
already state clearly in our exports that DPV is a W3C Community Group
report rather than a ratified W3C Standard.

---

Fallback (if DPVCG declines or stalls): publish the dataset with a Zenodo
DOI (owner account needed). The dataset file is already citable in-repo;
CITATION.cff exists at repo root and can gain a dataset section.
