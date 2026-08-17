# Market sizing: TAM, SAM, SOM and earlyvangelists

**Date:** 2026-08-14
**Status:** evidence-tagged model. Every figure carries one of:
[VERIFIED-direct] checked by this session against the primary source on
2026-08-14; [VERIFIED-agent] extracted from the primary source by a research
agent on 2026-08-14 with the two most load-bearing figures re-checked
directly; [SECONDARY] not confirmed on a primary page; [REASONED] an
assumption with its overturning condition stated. Nothing here is a forecast
or a promise. `WILLINGNESS_TO_PAY: UNVALIDATED` stands and this document does
not change it.

**Honest headline before any number:** no authority counts the non-EU
population in EU AI Act scope. The European Commission's own impact
assessment says precise cost estimation is not possible, and no Commission,
Eurostat or EDPB count of extraterritorially-caught firms exists
[VERIFIED-agent: search exhausted, no such publication found]. Every non-EU
figure below is therefore scenario arithmetic on stated anchors, not a count.

## 1. Verified anchors (the numbers everything else is built from)

| # | Anchor | Value | Source, status |
|---|---|---|---|
| A1 | EU enterprises, business economy, 2024 | 33,462,377 total; 33,407,506 SMEs (99.84%) | Eurostat SBS API `sbs_sc_ovw`, updated 2026-03-10 [VERIFIED-agent] |
| A2 | EU enterprises with 10+ persons employed, 2024 | ~1,875,488 (small 10-49: 1,569,947; medium 50-249: 250,670; large 250+: 54,871) | same dataset [VERIFIED-agent] |
| A3 | EU enterprises (10+) using AI, 2025 | 20.0% (19.95% unrounded); small 17.00%, medium 30.36%, large 55.03%. Up from 13.5% in 2024 | Eurostat `isoc_eb_ai` + news release 11 Dec 2025 [VERIFIED-direct] |
| A4 | Commission high-risk share estimate | "only 5% to 15% of all AI applications are estimated to constitute a high risk" | SWD(2021) 84 final, pp. 68-69 [VERIFIED-agent, exact quotes extracted] |
| A5 | appliedAI risk-classification study (106 enterprise AI systems, March 2023) | 18% high-risk, 42% low-risk, 40% unclear; "ranges from 18% to 58%" | appliedAI white paper PDF [VERIFIED-agent]. Caveat: convenience sample of a public database, not representative |
| A6 | appliedAI startup survey (N=113 EU AI startups, Dec 2022) | 33% self-classified high-risk; report frames 33-50% including unclear | survey report PDF [VERIFIED-agent] |
| A7 | Article 2(1)(c) extraterritorial scope | applies to third-country providers and deployers "where the output produced by the AI system is used in the Union" | OJ text via AI Act explorer [VERIFIED-direct] |
| A8 | Article 99(4)(b) and 99(6) | rep-obligation fines up to €15m/3%, SMEs pay the LOWER of amount or percentage | OJ text [VERIFIED-direct] |
| A9 | US companies exporting goods to the EU, 2023 | 75,869 identified | US Census profile, released 29 May 2026 [VERIFIED-agent]. Goods only; no services/SaaS company count exists |
| A10 | GB businesses exporting services, 2024 | 220,300 (9.0% of business economy); no EU-destination split published | ONS ABS exporters dataset, 12 Jun 2026 [VERIFIED-agent] |
| A11 | Non-EU firms appointing a GDPR EU representative | 54% of surveyed non-EU respondents (2019); mostly internal appointments | McDermott/Ponemon press release [VERIFIED-agent]; N not stated in release |
| A12 | US firms actively certified under Privacy Shield at 2019 | "more than 5,000" | US DoC release [VERIFIED-agent]. DPF successor count ~2,800 circulates [SECONDARY] |
| A13 | GDPR Art 27 rep published prices, Aug 2026 | floor €19/mo (eurep.ie) to €440/mo (Prighter Large); crowded middle €490-1,000/yr; law-firm end $2,700+/yr (VeraSafe) | vendor pages [VERIFIED-agent]; Prighter re-checked [VERIFIED-direct] |
| A14 | AI Act authorised-rep published prices, Aug 2026 | only two published: Prighter GPAI rep from €420/yr annual (tiers to €4,752/yr); European Compliance Suite €2,400/yr per AI product. All others quote-gated | vendor pages [VERIFIED-agent]; Prighter [VERIFIED-direct] |
| A15 | Closest SME competitor | Legalithm: free-launch mode, launch prices €17/€47/€119 per month (these ARE the 40%-off prices; list is €29/€79/€199), CLI/MCP/GitHub Action. Its classification is declaration-driven, but see the correction below: it is NOT true that it does no code scanning. Commission's own Compliance Checker: free, official, beta, questionnaire-only, and distinct from FLI's similarly-named unaffiliated checker | prices re-fetched [VERIFIED-direct 14 Aug]; scanning behaviour read from shipped npm source [VERIFIED-agent] |
| A16 | Obligation timing | Art 5 since 2 Feb 2025; GPAI + Art 54 rep since 2 Aug 2025; Art 50 transparency since 2 Aug 2026 (marking grace to 2 Dec 2026); Annex III high-risk (and with it most Art 22 rep demand) 2 Dec 2027; Annex I 2 Aug 2028 | `scripts/omnibus.py`, repo single source of truth [VERIFIED-direct] |

Corrections this exercise makes to the 13 Aug research dossier: the GDPR Art 27
published range is wider than "€59-€200/month" (A13); EU Business Partners'
annual arithmetic is €996, and €997 does not appear on the current pricing
page; the 2024 AI-adoption figure (13.5%) is superseded by 2025 (20.0%); and
"a waitlist" is not an ungated demand test (personal data; privacy fields
unresolved).

## 2. TAM (total addressable market)

Definition used: SMEs, inside and outside the EU, that in principle need EU
AI Act scoping, documentation support, or representation at SME price points
in a given year. Enterprise platforms (Vanta/OneTrust class) excluded.

**Segment EU (derived from verified anchors):**
- Small (10-49) AI users: 1,569,947 x 17.00% = 266,891
- Medium (50-249) AI users: 250,670 x 30.36% = 76,103
- **EU SMEs (10-249) using AI, 2025: ~343,000** [derived from A2 x A3]
- Of these, the high-risk band is 17,000-51,000 on the Commission estimate
  (A4) or up to ~62,000-199,000 on the appliedAI range (A5, non-representative
  sample; treat as upper illustration). The 40%-unclear band (~137,000 as an
  illustration) is the scoping-need population where an
  `insufficient_information` answer is itself the product.
- Micro-enterprises (<10 employees): ~31.6M exist [A1-A2]; AI adoption is not
  measured by the survey. Unquantified upside, deliberately excluded from the
  model rather than guessed.

**Segment non-EU (scenario, [REASONED] throughout):**
- No count exists (see headline). Anchors A9-A12 bound the picture: 75,869 US
  goods exporters to the EU; 220,300 UK service exporters (all destinations);
  5,000+ US firms once actively certified for EU data-transfer compliance;
  54% of surveyed non-EU firms appointed GDPR reps.
- Illustrative UK-only arithmetic (each step flagged): if 40-60% of UK
  service exporters serve the EU (no split published; overturned by an ONS
  destination breakdown) that is ~88,000-132,000 firms; if AI adoption
  parallels the EU's 20% (proxy; overturned by a UK adoption statistic) that
  is ~18,000-26,000 UK firms with both EU service trade and AI use, before
  filtering to those whose AI output is used in the Union.
- Net scenario: the non-EU population facing the scoping question is
  plausibly in the **tens of thousands globally**; the representative-ELIGIBLE
  subset (GPAI providers now, high-risk providers as 2 Dec 2027 approaches)
  is plausibly in the **low thousands now, widening through 2027**. Overturned
  by: any published Commission/EDPB/market count, which does not exist today.

**TAM value scenario:** 150,000-250,000 firm-needs per year (EU unclear+high-risk
band plus non-EU tens of thousands) x €250-2,400/yr SME price points (A13-A15)
= **roughly €40M to €600M per year**. The spread is deliberate; the honest
statement is "low hundreds of millions of euros per year at SME price points,
on the stated assumptions", not a point estimate.

## 3. SAM (serviceable addressable)

Constraints applied: languages EN/DE/PT-BR; digital-only reach; segments with
a live or dated obligation; solo delivery capacity irrelevant at SAM level but
channel-reachability is not.

- Non-EU English-speaking AI/SaaS SMEs trading into the EU: ~10,000-30,000
  [REASONED from A9-A12 arithmetic above]
- DACH EU SMEs using AI reachable via German-language search/content: a
  minority share of the ~343,000 EU pool; Germany+Austria are ~a quarter of
  EU business economy, and medium-firm adoption is 30% [A3], so
  ~20,000-50,000 [REASONED]
- Privacy/AI-governance consultants (multiplier buyers): IAPP alone has
  90,000+ members [VERIFIED-agent]; the consultant-reachable subset serving
  SME clients is unknown; treated as channel, not counted twice.
- PT-BR: Brazil's PL 2338/2023 is not law [repo rule]; PT-BR SAM is future
  optionality, counted 0 today.

**SAM: ~30,000-80,000 firms; at €250-1,500 realistic first-year spend that is
~€8M-€120M/yr.** [REASONED; every input tagged above]

## 4. SOM (serviceable obtainable, 12 months from activation)

Bound by evidence and capacity, not by the market:
- Payment is NOT ACTIVE; SOM is zero until the P0 gate clears. From
  activation: one operator can credibly fulfil 1-3 scoping engagements per
  week alongside everything else; conversion evidence is nonexistent (zero
  third-party visibility recorded May 2026; assess analytics live only since
  10 Jul 2026).
- **SOM: 5-30 paid engagements in the first 12 months after activation
  (£1,250-£15,000 at the entry tier, up to ~£30,000 with mid-tier mixes), plus
  0-10 representative-style retainers ONLY if the EU-establishment and PI
  prerequisites are built (mostly a 2027 line per A16).** [REASONED]
- Plainly: this is a consultancy-with-a-wedge income in year one, not a
  product business. The product-business case (self-serve at Legalithm-like
  price points) requires volume evidence that does not exist yet, and a
  pricing fight against a free official checker and a free-launch competitor.

## 5. Earlyvangelist profiles (Blank criteria: has the problem, knows it,
is actively searching, has improvised a solution, has budget)

**E1. The already-paying non-EU founder (primary).** Founder/CTO of a non-EU
(US/UK/CA/AU) B2B SaaS, 5-100 staff, with a shipped AI feature and EU
customers. Already pays €420-6,000/yr for a GDPR Article 27 representative or
DPF certification [A13, A12]: budget and willingness to pay for exactly this
class of obligation are demonstrated, not hypothesised. Trigger events: an EU
customer's procurement questionnaire; a GDPR-rep vendor upselling AI Act rep
(Prighter already does, A14); reading that Article 50 went live on 2 Aug
2026. Improvised solution today: a law-firm blog post plus a generic LLM
chat. Searches: "does the EU AI Act apply to a US company". Disqualifier:
wants a certificate; must be referred out.

**E2. The consultant multiplier.** Fractional DPO / privacy consultant adding
AI Act scoping to an existing GDPR practice, serving 5-50 SME clients.
Already buys tools and templates; reachable through IAPP, Luiza's Newsletter
(99,000+ [VERIFIED-agent]), Enterprise AI Governance (8,500+), Privacy and
AI. The consultant-guide and engagement layer shipped in July 2026 serve
exactly this person. One converted consultant is worth many end-clients.

**E3. The 2027-deadline EU deployer (secondary, longer cycle).** DACH or
other EU SME (50-249 staff, the 30%-adoption band) deploying AI in an
Annex III-adjacent domain (hiring, credit, education), preparing for
2 Dec 2027. Pain is real but dated; free national-authority guidance
competes; converts to paid only where procurement or customers force
evidence earlier.

## 6. The SAM decision the owner asked for (objective recommendation)

Serve BOTH EU and non-EU SMEs with the same free scoping wedge; weight paid
effort to E1 then E2, and let E3 mature toward 2027. Reasons, with the
counterevidence attached:

For: (1) E1 is the only profile with demonstrated willingness to pay for the
obligation class (A13: a whole published-price market exists); (2) the live
obligations today (Art 54 GPAI since Aug 2025, Art 50 since Aug 2026) fall
on providers wherever established, and the extraterritorial question is the
one an EU-resident SME never has to ask, making non-EU pain sharper; (3) the
distribution channels Regula can actually use without paid spend (PyPI,
GitHub, dev newsletters, GEO content in English) skew non-EU/anglophone.

Against, stated with equal weight: (1) the EU pool is countable and larger
(343,000 vs tens of thousands); (2) the Commission's free official checker
and Legalithm's free launch tier both target the same scoping question, and
"free official" is a hard competitor for a paid scoping report; (3) the
recurring-revenue representative line mostly opens 2 Dec 2027 and requires
an EU entity plus professional indemnity cover that do not exist; (4)
willingness to pay remains UNVALIDATED for Regula specifically, whatever the
comparable market shows.

Net: the objectively best SAM is **"both, weighted non-EU-first for paid
conversion, EU-DACH-second, with the representative line built as the 2027
pipeline"**, and the fastest evidence test of that weighting is the
per-jurisdiction usage split the assessment already instruments.

## 7. What did I miss (recorded pass)

- Micro-enterprises are excluded for lack of data, and they are 94% of EU
  enterprises; if micro AI adoption is material, EU TAM is understated.
- No UK/US AI-adoption statistic was sourced; the EU 20% was used as proxy
  and flagged.
- The Art 27 provider list is not exhaustive (DPO Centre, Formiti, TechGDPR,
  DP-Dock seen in directories, not fetched).
- Luiza's Newsletter count could not be re-fetched directly (blocked); it
  carries agent-fetch status only.
- The appliedAI figures are 2022-2023 vintage, pre-Omnibus; risk-class
  shares may have shifted with Annex III deferral; no newer equivalent study
  was found this session.
- Legalithm's traction is unknown (no user counts published); its existence,
  not its success, is what is verified.
- Nothing here validates comprehension, trust or usability; those require
  the gated representative-user work.
