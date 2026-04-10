# McKinsey AI Transformation Manifesto (April 2026) — relevance to Regula

Reference: Singla, A., Sukharevsky, A., Lamarre, E., Smaje, K., &
Levin, R. (April 2026). *The AI transformation manifesto: Twelve
themes separate companies that are truly rewired for AI from their
peers.* McKinsey & Company / QuantumBlack.

Excerpted from *Rewired: How Leading Companies Win with Technology and
AI* (2nd edition), Wiley, 2026. Copyright McKinsey & Company.

---

## Why this document matters for Regula

The manifesto synthesises McKinsey's work on "hundreds of large-scale
tech and AI transformations" into 12 themes. Three of them directly
validate Regula's positioning and feature set. Regula does NOT claim
McKinsey endorsement — the alignment is between industry research
findings and the product's design choices.

---

## Theme 10 — "No trust, no right to deploy AI"

> "Digital trust grows when stakeholders have confidence that your
> organization protects consumer data, enacts effective cybersecurity,
> offers trustworthy AI-powered products and services, and provides
> transparency around AI and data usage."

> "The challenges are only increasing with the expansion of agentic
> technologies, requiring much more time for testing agentic systems
> and automating risk controls."

> "The excitement for agentic AI may be getting ahead of companies'
> ability to manage the more complex risks associated with the
> technology."

**Relevance to Regula:** This is the business case for Regula's
existence. The tool provides:

- **Transparency detection** — Article 13 patterns, disclosure
  templates (`regula disclose`)
- **Automated risk controls** — pre-commit hooks, CI/CD gates, the
  claim auditor, the self-healing CI agent
- **Agentic-system testing bridge** — `regula handoff garak/giskard/promptfoo`
  emits scoped runtime-testing configs from static code analysis
- **Trust evidence** — `regula conform` produces Article 43 evidence
  packs with SHA-256 integrity hashes

The manifesto's "automating risk controls" language directly describes
what `scripts/claim_auditor.py` and `.github/workflows/self-heal.yaml`
do — they are AI-governance risk controls that run without human
intervention.

---

## Theme 9 — "Design for adoption and build for scale"

> "Adoption often fails because adjacent upstream and downstream
> processes are left unchanged. An AI solution may predict equipment
> failures days in advance, but if maintenance still follows
> calendar-based scheduling, nothing happens."

**Relevance to Regula:** This validates the `regula conform
--organisational` questionnaire and the scope boundary documented in
`docs/what-regula-does-not-do.md`. Code scanning alone does not create
compliance if the organisation's risk management system, quality
management system, post-market monitoring, and fundamental-rights
impact assessment are not in place. Regula explicitly positions itself
as "the code layer of a governance programme, not the whole programme"
— which is exactly the "adjacent process" point McKinsey makes.

---

## Theme 11 — "Agentic engineering becomes the next capability to master"

> "Foundation models are now capable of sustained, autonomous work over
> long periods, making it possible to build complex agentic workflows."

**Relevance to Regula:** Regula detects `agent_autonomy` patterns in
code — flagging systems where AI agents operate without human oversight
gates. The `regula handoff` command then bridges from static detection
to runtime testing by emitting scoped configs for Garak, Giskard, and
Promptfoo. The self-healing CI agent (`scripts/ci_heal.py`) is itself
an agentic workflow governed by Regula's own risk-control patterns —
dogfooding the manifesto's guidance.

---

## Themes NOT used (honest exclusions)

| Theme | Why not used |
|---|---|
| #3: "20% EBITDA uplift, $3 per $1 invested" | Applies to AI transformation broadly, not to compliance tools specifically. Using it for Regula would misrepresent the scope of the research. |
| #4: "Senior business leaders in the driver's seat" | Organisational advice. Regula is a developer tool, not a leadership programme. |
| #5: "70% in-house talent" | Workforce composition. Not relevant to a CLI tool. |
| #6: "Speed is the defining advantage" | Regula IS fast (scan in seconds, not weeks with a consultant) but claiming this is supported by McKinsey's Theme 6 would be a stretch — McKinsey is talking about organisational metabolic rate, not tool performance. |
| #8: David Baker / Nobel Prize on data quality | Relevant to AI broadly but not specifically to Regula's code-scanning function. |
| #12: "(Re)learn" | The delta log RSS feed supports continuous learning about AI Act changes, but claiming McKinsey endorsement of that feature would overstate the alignment. |

---

## How to cite

When referencing this material on the landing page, in docs, or in
articles, cite McKinsey directly:

> Per McKinsey's April 2026 *AI Transformation Manifesto*: "No trust,
> no right to deploy AI." (Singla, Sukharevsky, Lamarre, Smaje, &
> Levin, 2026)

Do NOT write "McKinsey recommends Regula" or "as endorsed by McKinsey"
or any phrasing that implies a relationship. McKinsey published general
industry research. Regula happens to align with three of their twelve
themes. That is all.

---

*Last reviewed: 2026-04-10. Added to the Regula reference library for
the maintainer's strategic planning, not as user-facing marketing
material.*
