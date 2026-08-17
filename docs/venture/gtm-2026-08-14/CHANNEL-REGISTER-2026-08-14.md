# Channel register: distribution and amplification targets

**Date compiled:** 2026-08-14
**Status:** REGISTER ONLY. `EXTERNAL_CONTACT: NOT_AUTHORISED` stands. Nothing
in this file may be contacted, pitched or submitted until the owner signs a
dated authorisation (owner question set, field 14). Public, passive actions
(publishing on our own surfaces, submitting nothing, contacting no one) are
unaffected.

**Verification key:** [V-direct] fetched by the main session on 2026-08-14;
[V-agent] fetched by the research agent from the cited page on 2026-08-14;
[secondary] search-snippet or aggregator figure, not confirmed on a primary
page; [n/s] not publicly stated.

## Tier 1: on-format, low-cost, highest fit (submission or editorial)

| Channel | Audience | Why first |
|---|---|---|
| AI Governance Library (aigl.blog, Jakub Szarmach) | counts [n/s]; curates and reviews AI-governance resources and tools [V-agent] | Its entire format is reviewing artefacts like Regula; a curation submission is the single cheapest credible placement |
| Console.dev | "30k+ subscribers" [V-direct]; weekly devtool reviews, free review submission + paid /advertise | Reviews open-source devtools as its core job. **CORRECTED 14 Aug (second pass, all [V-direct] from console.dev/selection-criteria and /advertise):** the earlier note had the gating backwards. The weekly "Interesting tools" editorial review has NO version requirement; only the separate "Betas" listing is version-gated ("the release must be pre 1.0 ... Any GA or stable releases are not eligible"). Regula at v1.9.0 is therefore ineligible for Betas and fully eligible for the free editorial review, which is the route to take. Submission: "Email hello@console.dev". Sponsorship detail confirmed direct: "max 100 characters", "We don't do sponsored reviews", "68% of our readers have signed-up to a tool featured by Console" |
| Talk Python To Me / Python Bytes (talkpython.fm) | audience stats on request [V-agent]; public sponsorship offer | Exact stack match: Python CLI on PyPI; guest or news-item routes |
| Changelog News / podcasts (changelog.com/sponsor) | "reach 100,000 developers weekly"; 26,333 newsletter subscribers [V-agent] | OSS-native; a compliance CLI is unusual enough to be story-worthy |
| The EU AI Act Newsletter (Risto Uuk, FLI) | "over 50,000 subscribers" per FLI bio, internally inconsistent with "over 40,000" on same page [V-agent] | RECLASSIFIED 14 Aug (Sprint 1 dossier, accepted): treat as a COMPETITOR CHANNEL, not a partner; FLI ships the de facto community-standard free checker and the newsletter author owns it. Deprioritise; editorial coverage only if it arrives unsolicited |

## Tier 2: niche authority (editorial mention or guest slot)

| Channel | Audience | Notes |
|---|---|---|
| Luiza's Newsletter (Luiza Jarovsky) | "99,000+ subscribers" [V-agent; direct re-fetch failed, site likely blocks] | Highest single reach in the niche; sponsorship page indexed but 404 on access; editorial mention requires surviving scrutiny, which the honesty posture supports |
| Enterprise AI Governance (Oliver Patel) | "over 8,500 professionals" [V-agent] | Enterprise practitioners, cheat-sheet format adjacent to a scoping tool |
| Federico Marengo, Privacy and AI | [n/s] | DPO/consultant audience, matches the consultant-channel persona |
| RegInt podcast (Tea Mustac, Peter Hense) | [n/s] | Lawyer/consultant audience; founder-guest angle on scoping in code |
| Serious Privacy podcast | [n/s]; TrustArc-backed | Guest-slot target; vendor-adjacency may limit |
| Masters of Privacy (Sergio Maldonado) | [n/s] | Has run AI Act episodes; marketing-data/privacy intersection |
| IAPP (iapp.org) | "90,000+ Members" [V-agent] | Biggest consultant aggregation point; entry is contributed articles or tool trackers, not paid sponsorship |
| Montreal AI Ethics Brief | [n/s] on page; "21,000+" [secondary] | Mission-aligned with open source |
| Barry Scannell (William Fry, LinkedIn) | [n/s]; press-described leading AI commentator | Editorial amplifier for lawyers, no sponsorship route |
| Katharina Koerner | [n/s] | Privacy-engineering/AI governance bridge |

## Tier 3: founder reach (paid or newsworthy)

| Channel | Audience | Notes |
|---|---|---|
| TLDR AI | ~1.1M readers [secondary; advertise page blocked fetch] | Strongest raw dev reach; paid slots expensive; organic pickup of interesting repos happens |
| Ben's Bites | ~120K [secondary]; sponsor route public | "AI builders" and early founders; launch-angle fit |
| Sifted (EU startup press) | [n/s]; sustained AI Act coverage | Editorial pitch: the SME compliance-burden story; not sponsorship |
| Tech Policy Press | podcast 1k-10k monthly [secondary estimate] | Op-ed venue for a founder perspective |

## Deprioritised or excluded, with reasons

- Hacker News: prior submissions already made (project record); do not resubmit.
- Kai Zenner: insider validator, not a channel; outreach would be political.
- Rachel Adams, Johan Steyn: Global South / SA audiences, weak fit for EU AI
  Act SME distribution (relevant only if positioning changes).
- AI Policy Weekly (Center for AI Policy): operations paused per its own
  newsletter; skip.
- Holistic AI, Credo AI, trail, Legalithm blogs: competitor vendors, not
  neutral channels.
- No significant independent EU AI Act YouTube creator surfaced by the sweep;
  recorded as "searches did not surface one", not "none exists".

## Side-findings that affect strategy (moved into the market-sizing doc)

1. **Legalithm** (legalithm.com) is a direct competitor: AI-Act-native,
   self-serve, free-launch mode with no card [V-direct], published launch
   prices Starter €17/mo, Pro €47/mo, Business €119/mo [V-agent], and a free
   CLI/MCP/GitHub Action surface [V-agent]. This is the closest structural
   competitor found to date and must appear in every positioning decision.

   **CORRECTED 14 Aug (second pass, read from the shipped npm source, not the
   marketing page).** Two claims previously recorded here do not survive.

   - "Not code-pattern scanning" is **too strong and publicly refutable.** Its
     CLI does walk the repository: it reads dependency manifests for ten
     ecosystems in full, reads the **contents** of `.github/workflows/*.yml`,
     `Dockerfile*` and `docker-compose*.yml` against an AI-vendor token list,
     matches file **paths** against route patterns, and inspects environment
     variable **names**. What it does not do is read the body of a `.py`,
     `.ts` or `.js` source file. The defensible distinction for our copy is
     therefore **source-code pattern scanning** versus manifest, CI/IaC and
     path-level detection, never "scanning versus no scanning". Its final
     classification does remain declaration-driven: detection only seeds a
     fallback and never overrides an explicit user classification.
   - "Free until ~April 2028" is **refuted; no such date is published.** Two
     different dates appear on their site and neither is April 2028: the CLI,
     MCP server and Action are said to "stay free through the EU AI Act
     high-risk deadline (Dec 2027)", and the partner page signposts
     "monetization begins ~2028, no charges today". The honest statement is
     "free now; OSS surface promised free through Dec 2027; hosted
     monetisation undated, signposted ~2028".
   - The €17/€47/€119 figures ARE the 40%-off prices (list €29/€79/€199), and
     the founding discount is capped at 100 seats for year one only and is not
     yet active.
2. **The European Commission's own Compliance Checker** (AI Act Service Desk)
   is free, official and explicitly beta; questionnaire-only [V-agent].
3. **"Influencers/creator agencies trading in the EU" as a customer segment:**
   real and forming (Commission FAQ on Article 50; law-firm briefings aimed at
   advertisers; marketing-trade explainers) but with two honest caveats
   recorded by the sweep: Article 50(4) is narrower than "any genAI use"
   (deepfakes, synthetic media, public-interest text, with an
   editorial-control exemption), and creators' AI use lives in content tools,
   not codebases, so the fit with a code-scanning CLI is untested. Treat as a
   content-marketing angle (an Article 50 explainer page attracts that
   traffic), not a product pivot.

## Authorisation ledger

| Date | Action | Authorised by | Record |
|---|---|---|---|
| (empty; no outreach authorised) | | | |
