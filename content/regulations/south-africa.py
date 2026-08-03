# regula-ignore — sourced regulatory prose for the SA page quotes the draft policy's own risk vocabulary
"""South Africa — draft National AI Policy coverage page.

Data file consumed by scripts/build_regulations.py to generate
south-africa-ai-policy.html. Converted from the hand-maintained
page on 16 July 2026 (DQ-7); content carried verbatim from the
reviewed 16 Jul state except: cta-card headings h4->h3 (site
heading-hierarchy rule); two stray Guides link artifacts removed;
the visible last-updated date refreshed to 16 July 2026 (the page
was edited 16 Jul in 09d4750 but still displayed 13 June 2026).

The live tracker is JS-driven from /sa-tracker.json with the
static rows below as SEO/no-JS fallback — keep both in sync
(source of truth: content/regulations/sa-tracker.json, copied to
site/sa-tracker.json).

Key verified facts: draft gazetted 10 Apr 2026 (No. 54477, Notice
3880 — gov.za); withdrawn ~26 Apr 2026 (SAnews); revised draft
'reported' Jan 2027 (secondary, marked as such)."""

import json

REGION = {
    "slug": "south-africa-ai-policy",
    "flag": "🇿🇦",
    "nav_label": "South Africa",
    "lang": "en-ZA",
    "og_locale": "en_ZA",
    "hreflang_self": "en",
    "geo_region": "ZA",
    "geo_placename": "South Africa",
    "status_cls": "",
    "status_text": "Withdrawn &mdash; draft pulled ~26 April 2026",
    "title_tag": "South Africa Draft AI Policy 2026 &mdash; Regula",
    "title_html": "South Africa's <span class=\"hl\">draft National AI Policy</span>: gazetted, then withdrawn",
    "meta_description": "South Africa AI policy tracker. Cabinet-approved draft National AI Policy, data protection under POPIA, and readiness for global AI regulation.",
    "meta_keywords": "South Africa AI Policy, National AI Policy South Africa, DCDT AI Policy, South Africa AI Act, POPIA AI compliance, South Africa AI regulation 2026, Khumbudzo Ntshavheni AI, AI governance South Africa, AI policy framework South Africa, sector-specific AI regulation South Africa",
    "og_title": "South Africa Draft AI Policy 2026 — Regula",
    "og_description": "South Africa's draft National AI Policy was gazetted 10 April 2026 then withdrawn ~26 April 2026 after AI-hallucinated citations were discovered. Revised draft expected 2027. POPIA and King V baseline remains.",
    "twitter_title": "South Africa Draft AI Policy 2026 — Regula",
    "twitter_description": "Sector-specific multi-regulator model, timeline, POPIA & King V implications. Live tracker updated as the gazette publishes.",
    "last_updated": "16 July 2026",
    "published_time": "2026-04-07T00:00:00+02:00",
    "modified_time": "2026-07-16T00:00:00+02:00",
    "lede": "On 25 March 2026, Cabinet approved South Africa's draft National Artificial Intelligence Policy. It was gazetted on 10 April 2026 (Government Gazette No. 54477, Notice 3880) with a 60-day comment window. On ~26 April 2026, Communications Minister Solly Malatsi <strong>withdrew the draft</strong> after at least 6 of 67 academic citations were found to be AI-generated hallucinations. No timeline for a revised draft has been announced; reports suggest 2027. The POPIA and King V baseline analysis below remains relevant regardless of the policy's status.",
    # Bespoke tracker (verbatim from the reviewed page) — used instead
    # of builder-rendered tracker_rows.
    "tracker_html": """
<div class="tracker" id="sa-tracker" data-src="/sa-tracker.json">
            <h2>Live tracker <span id="tracker-ts" class="tracker-ts"></span></h2>
            <div id="tracker-rows">
                <div class="tracker-row">
                    <div class="lbl">Cabinet approval</div>
                    <div class="val">2 April 2026 — draft approved for public comment by Minister in the Presidency Khumbudzo Ntshavheni at a post-Cabinet briefing &nbsp;<span class="ok">CONFIRMED</span></div>
                </div>
                <div class="tracker-row">
                    <div class="lbl">Gazette publication</div>
                    <div class="val">Gazetted 10 April 2026 (No. 54477, Notice 3880); draft withdrawn 26 April 2026 &nbsp;<span class="pend">WITHDRAWN</span></div>
                </div>
                <div class="tracker-row">
                    <div class="lbl">Public comment window</div>
                    <div class="val">60 days from gazette date (expected April–June 2026)</div>
                </div>
                <div class="tracker-row">
                    <div class="lbl">Regulatory model</div>
                    <div class="val">Sector-specific, multi-regulator (financial services, health, education, telecoms) — <em>per Michalsons reporting; confirm on gazette</em> &nbsp;<span class="pend">SECONDARY</span></div>
                </div>
                <div class="tracker-row">
                    <div class="lbl">Final policy</div>
                    <div class="val">2026/2027 financial year (target)</div>
                </div>
                <div class="tracker-row">
                    <div class="lbl">Sector regulations</div>
                    <div class="val">2027/2028 financial year (target)</div>
                </div>
                <div class="tracker-row">
                    <div class="lbl">Background</div>
                    <div class="val">October 2024 DCDT Policy Framework published as the precursor document</div>
                </div>
            </div>
        </div>
""",
    "tracker_rows": [],
    "sections_html": [
        {
            "id": "what-cabinet-approved",
            "heading": "What Cabinet approved (announced 2 April 2026)",
            "body": """\
            <p>At a post-Cabinet media briefing in Pretoria, Minister in the Presidency Khumbudzo Ntshavheni announced (<a href="https://www.sanews.gov.za/south-africa/minister-announces-withdrawal-draft-ai-policy">SAnews, gov.za</a>) that Cabinet had approved publication of the draft National Artificial Intelligence Policy for public comment. The draft reportedly cleared the Socio-Economic Impact Assessment System and achieved concurrence across all Director-General clusters in a 24 February 2026 DCDT briefing to Parliament.</p>

            <p>The gazette has not yet published the text, so the policy's exact wording is not in the public domain. What the draft is <strong>reported</strong> to contain — pending gazette confirmation — is the following:</p>

            <ul>
                <li><strong>A sector-specific, multi-regulator governance model.</strong> Rather than creating a single dedicated AI regulator, AI governance will be embedded within existing supervisory frameworks — the FSCA for financial services, the Information Regulator for data protection, the Council for Medical Schemes for health, ICASA for telecommunications, the Department of Higher Education and Training for education, and so on. Pragmatic, but creates a patchwork that is harder to navigate for smaller businesses operating across sectors.</li>
                <li><strong>Six core pillars</strong> organised around capacity and talent development, AI for inclusive growth and job creation, responsible governance, ethical and inclusive AI, cultural preservation and international integration, and human-centred deployment.</li>
                <li><strong>A 60-day public comment window</strong> that opens on the gazette publication date (expected April 2026).</li>
                <li><strong>Final policy</strong> targeted for the 2026/2027 financial year.</li>
                <li><strong>Sector-specific regulations and guidelines</strong> targeted for the 2027/2028 financial year.</li>
            </ul>

            <p class="note-inline">All six-pillar and multi-regulator claims above are sourced from <a href="https://www.michalsons.com" target="_blank" rel="noopener">Michalsons' 3 April 2026 analysis</a> and will be verified against the gazetted text the moment it publishes. We will update this page within seven days of publication.</p>

            <p><strong>The question everyone is asking.</strong> How will the DCDT coordinate across that many sector regulators so South African organisations don't end up complying with six different, conflicting AI rulebooks? That is the single most important question to raise during the public comment window.</p>
""",
        },
        {
            "id": "legal-baseline",
            "heading": "The South African legal baseline for AI today",
            "body": """\
            <p>South Africa does not have an AI Act yet, and the draft policy Cabinet approved is not itself an Act either — it is a policy that will later be translated into sector-specific regulations. But South African organisations deploying AI are already bound by a substantial body of existing law. None of these require waiting for the gazette.</p>

            <ul>
                <li><strong>POPIA (Protection of Personal Information Act, 2013)</strong> — applies to any AI system that processes personal information. <strong>Section 71</strong> specifically addresses automated decision-making and profiling: a data subject is entitled not to be subject to a decision based solely on automated processing unless specific exceptions apply. This obligation already binds South African organisations regardless of when the AI Policy is gazetted.</li>
                <li><strong>Copyright Act, 1978</strong> (and the unsigned Copyright Amendment Bill) — relevant to training-data provenance and to AI-generated outputs.</li>
                <li><strong>Competition Act, 1998</strong> — relevant to algorithmic pricing, market concentration in AI infrastructure, and data-driven anti-competitive conduct.</li>
                <li><strong>Patents Act, 1978</strong> — relevant to AI-generated inventions; the <em>Thaler</em> line of decisions has been tested in South African courts.</li>
                <li><strong>King IV / King V Codes on Corporate Governance</strong> — non-statutory but widely adopted. <strong>King V was adopted by the Institute of Directors in South Africa (IoDSA) on 31 October 2025 and is in force for financial years commencing on or after January 2026.</strong> It consolidates King IV's 17 principles into 13 and introduces explicit AI governance principles alongside enhanced cyber risk provisions — governing bodies are now expected to oversee AI use and AI-related risk as a board-level matter under King V's "apply and explain" regime.</li>
            </ul>
""",
        },
        {
            "id": "what-to-do",
            "heading": "What South African organisations should do now",
            "body": """\
            <p>While the draft policy works through the gazette and the 60-day comment window, five things are worth doing today. None of them require waiting for the final text.</p>
            <ol>
                <li><strong>Inventory your AI systems.</strong> A list of what you have deployed, in which products, by which teams, with which third-party providers, and against which categories of personal data. POPIA already requires you to know this, and King V now makes it a board-level oversight obligation.</li>
                <li><strong>Document your data flows.</strong> Where training data came from, what consent or contractual basis covers it, where inference data lives, and who has access.</li>
                <li><strong>Document human oversight.</strong> For each high-stakes deployment (hiring, credit scoring, healthcare triage, content moderation), name the human function that reviews or can override the system. Human oversight is central to every modern AI governance regime and will be a focal point of the draft policy's "human-centred deployment" pillar.</li>
                <li><strong>Map your existing obligations.</strong> POPIA Section 71 (automated decision-making), Competition Act, Copyright Act, and sector regulator guidance from the Information Regulator, the FSCA, the Council for Medical Schemes, ICASA and the Department of Higher Education and Training as applicable. Those are the regulators most likely to own AI rule-making in a sector-specific model.</li>
                <li><strong>Submit comments during the 60-day public comment window.</strong> Industry voices will dominate the consultation if civil society, individual technologists and smaller businesses do not participate. Early feedback is the best chance to shape how sector-specific rules are eventually written.</li>
            </ol>
""",
        },
        {
            "id": "regula",
            "heading": "Where Regula fits",
            "body": """\
            <p>Regula is an <strong>open-source compliance CLI</strong> that combines code scanning with governance questionnaires for AI Act-shaped risk assessment. It was built primarily against the EU AI Act (Regulation (EU) 2024/1689), but the risk categories it detects — employment, biometrics, education, law enforcement, migration, critical infrastructure, credit scoring, medical devices — are exactly the areas every modern AI governance regime treats as high-risk, including the sectors South Africa's draft policy will route to sector-specific regulators. If you need to know whether a deployment touches a high-risk category today, Regula will tell you.</p>

            <p>For a South African team, the practically useful starting commands are:</p>

<pre><code><span class="term-comment"># Install</span>
<span class="term-cmd">pipx install regula-ai</span>

<span class="term-comment"># Inventory what you have</span>
<span class="term-cmd">regula discover .</span>                    <span class="term-comment"># AI systems present in the project</span>
<span class="term-cmd">regula inventory</span>                     <span class="term-comment"># AI library / model references with GPAI annotations</span>

<span class="term-comment"># Risk indicators against the same categories the Framework names</span>
<span class="term-cmd">regula check .</span>                       <span class="term-comment"># Scan for risk indicators</span>
<span class="term-cmd">regula classify --input "..."</span>        <span class="term-comment"># Classify a code snippet</span>
<span class="term-cmd">regula check --explain path/to/file</span>   <span class="term-comment"># Explain why something was classified</span>

<span class="term-comment"># Generate compliance evidence</span>
<span class="term-cmd">regula gap</span>                           <span class="term-comment"># Articles 9–15-style gap assessment</span>
<span class="term-cmd">regula oversight</span>                     <span class="term-comment"># Cross-file Article 14-style oversight detection</span>
<span class="term-cmd">regula conform</span>                       <span class="term-comment"># Annex IV-style conformity evidence pack</span>
<span class="term-cmd">regula register .</span>                    <span class="term-comment"># Annex VIII-shaped registration packet</span>

<span class="term-comment"># Health and reproducibility</span>
<span class="term-cmd">regula self-test</span>
<span class="term-cmd">regula doctor</span></code></pre>

            <p>The <code>register</code> command produces an Annex VIII-shaped local artifact even though South Africa does not have an EU-style central AI database. The fields it captures — provider identity, intended purpose, data inputs, system status, conformity references, fundamental rights impact assessment, data protection impact assessment — are the exact fields any sector-specific South African regulator will eventually ask for. Treat the artifact as a structured record-keeping baseline, not as a legal filing.</p>

            <p>Regula is open source, written in Python with <strong>zero production dependencies</strong>, and the entire detection ruleset is in the repository. South African teams can fork it, add SA-specific patterns (POPIA Section 71 markers, FSCA conduct standards, CMS clinical AI requirements) and contribute them back.</p>

            <div class="cta-row">
                <div class="cta-card">
                    <h3>Install Regula</h3>
                    <p>Open source, zero dependencies, runs locally.</p>
                    <a href="https://github.com/kuzivaai/getregula" target="_blank" rel="noopener">github.com/kuzivaai/getregula →</a>
                </div>
                <div class="cta-card">
                    <h3>Contribute SA patterns</h3>
                    <p>POPIA, FSCA, CMS markers welcome.</p>
                    <a href="https://github.com/kuzivaai/getregula/issues" target="_blank" rel="noopener">Open an issue →</a>
                </div>
            </div>
""",
        },
        {
            "id": "faq",
            "heading": "Frequently asked questions",
            "body": """\
            <div class="faq">
                <details>
                    <summary>What did Cabinet approve on 2 April 2026?</summary>
                    <p>Cabinet approved the publication of South Africa's draft National Artificial Intelligence Policy for public comment. Minister in the Presidency Khumbudzo Ntshavheni announced the decision at a post-Cabinet media briefing in Pretoria. The draft had previously cleared the Socio-Economic Impact Assessment System and achieved Director-General cluster concurrence at a 24 February 2026 DCDT briefing to Parliament. The gazette has not yet published the text.</p>
                </details>
                <details>
                    <summary>Has South Africa's draft AI policy been gazetted?</summary>
                    <p>It was gazetted on 10 April 2026 (No. 54477, Notice 3880) and then withdrawn later that month after fabricated citations were found in the draft. No replacement consultation date is treated here as authoritative until the responsible department publishes it.</p>
                </details>
                <details>
                    <summary>Does South Africa have an AI Act?</summary>
                    <p>No. The policy Cabinet approved is a policy, not an Act. Sector-specific regulations based on the policy are targeted for the 2027/2028 financial year. Until then, AI systems are governed by existing law: POPIA Section 71 (automated decision-making), the Copyright Act, the Competition Act, the Patents Act, and the King IV / King V Codes on Corporate Governance.</p>
                </details>
                <details>
                    <summary>Will South Africa have a single AI regulator?</summary>
                    <p>Reporting on the draft policy indicates government has chosen a sector-specific, multi-regulator model rather than creating a single dedicated AI regulator. AI governance will be embedded within existing supervisory frameworks — financial services (FSCA), data protection (Information Regulator), health (Council for Medical Schemes), telecoms (ICASA), education (DHET), and others. Pragmatic, but creates a patchwork for organisations operating across sectors. This claim will be verified against the gazetted text when it publishes.</p>
                </details>
                <details>
                    <summary>When does the public comment window open and close?</summary>
                    <p>The comment window opened with the 10 April 2026 gazette and was due to close on 10 June 2026, but withdrawal of the draft superseded it. Check the responsible department for any replacement consultation.</p>
                </details>
                <details>
                    <summary>How does POPIA apply to AI systems?</summary>
                    <p>POPIA Section 71 governs decisions based solely on automated processing of personal information, including profiling. A data subject is entitled not to be subject to such a decision unless specific exceptions apply — contract conclusion/execution, protective measures, or a law or code of conduct that safeguards their interests. Any AI system deployed in South Africa that processes personal data already falls under POPIA, regardless of whether the draft AI policy has been gazetted.</p>
                </details>
                <details>
                    <summary>What does King V require for AI governance?</summary>
                    <p>King V was adopted by the Institute of Directors in South Africa on 31 October 2025 and is in force for financial years commencing on or after January 2026. It consolidates King IV's 17 principles into 13 and introduces explicit AI governance principles alongside enhanced cyber risk provisions. Governing bodies are now expected to oversee AI use and AI-related risk as a board-level matter under King V's "apply and explain" regime.</p>
                </details>
                <details>
                    <summary>What should South African organisations do now?</summary>
                    <p>Inventory AI systems in production. Document data flows and consent bases. Identify each high-stakes deployment (hiring, credit scoring, healthcare triage, content moderation) and name the human function that reviews or can override the system. Map existing POPIA, Competition Act, Copyright Act, and sector regulator obligations. Submit comments during the 60-day public comment window once the draft policy gazettes — industry voices will dominate if civil society, technologists and smaller businesses do not participate.</p>
                </details>
            </div>
""",
        },
        {
            "id": "honest-gaps",
            "heading": "What we are tracking and what we still need to verify",
            "body": """\
            <p>We would rather publish what we know and flag what we don't than wait for certainty and let others dominate the conversation. Here is the gap list as of 16 July 2026:</p>
            <div class="gaps-box">
                <h3>To verify on gazette publication</h3>
                <ol>
                    <li><strong>Exact number and naming of pillars.</strong> Current reporting says six; the gazetted text may show a different count or structure.</li>
                    <li><strong>The sector-specific multi-regulator model.</strong> Whether the final text confirms this approach or hedges it, and which specific regulators are named.</li>
                    <li><strong>Coordination mechanism across regulators.</strong> How DCDT proposes to prevent conflicting sector rules — this is the single most important practical question for businesses operating across industries.</li>
                    <li><strong>High-risk category definitions.</strong> Whether the draft policy carries an explicit Annex III-style list and how it compares to the EU AI Act's categories.</li>
                    <li><strong>Public sector obligations.</strong> The extent to which state use of AI (welfare, policing, border control) is treated differently from private sector deployment.</li>
                    <li><strong>Alignment with the AU Continental AI Strategy and SADC digital frameworks.</strong> Not addressable until the text is in the public domain.</li>
                </ol>
            </div>
            <p>The moment the gazette publishes, we update the tracker above, update this list, and publish a focused breakdown of what changed between the Cabinet-approved draft and the gazetted text. If you want to be nudged when that happens, <a href="https://github.com/kuzivaai/getregula" target="_blank" rel="noopener">watch the repository</a>.</p>
""",
        },
        {
            "id": "sources",
            "heading": "Sources",
            "body": """\
            <div class="sources">
                <ul>
                    <li><strong>Post-Cabinet media briefing (2 April 2026)</strong> — Minister in the Presidency Khumbudzo Ntshavheni, Pretoria. Announcement of Cabinet approval of the draft National AI Policy for public comment. Confirmed via live broadcast coverage on <a href="https://www.sowetan.co.za" target="_blank" rel="noopener">Sowetan</a> and <a href="https://www.businessday.co.za" target="_blank" rel="noopener">Business Day</a>.</li>
                    <li><strong>Michalsons — Nathan-Ross Adams (3 April 2026)</strong>, "South Africa's draft national AI policy open for public comment." Source for the six-pillar structure, sector-specific multi-regulator model, 60-day comment window, 24 February 2026 parliamentary briefing, SEIAS clearance and DG cluster concurrence, and the 2026/2027 and 2027/2028 targets. To be verified against the gazetted text.</li>
                    <li><strong>Department of Communications and Digital Technologies</strong> — the lead department. Web: <a href="https://www.dcdt.gov.za" target="_blank" rel="noopener">www.dcdt.gov.za</a>. Tel: +27 12 427 8000.</li>
                    <li><strong>POPIA (Protection of Personal Information Act 4 of 2013)</strong> — Republic of South Africa. Section 71 governs automated decision-making and profiling.</li>
                    <li><strong>King V Code of Corporate Governance (October 2025)</strong> — Institute of Directors in South Africa. Adopted 31 October 2025, in force for financial years commencing on or after January 2026.</li>
                    <li><strong>October 2024 DCDT National AI Policy Framework</strong> — the precursor document published for public comment (closed 29 November 2024). Useful historical context; superseded in focus by the April 2026 draft policy.</li>
                </ul>
            </div>
            <p style="margin-top: 24px; font-size: 14px; color: var(--text-dim);">If you spot an error on this page, open an issue on <a href="https://github.com/kuzivaai/getregula/issues" target="_blank" rel="noopener">github.com/kuzivaai/getregula</a> or email a correction. We would rather be told than be wrong.</p>
""",
        },
    ],
    "faq": [
        # Structured-data-only entries: the visible FAQ lives in
        # sections_html (bespoke markup carried verbatim from the
        # hand-maintained page, incl. PT-BR pairs for search).
        {
            "q": "What did Cabinet approve on 2 April 2026?",
            "a": "Cabinet approved the publication of South Africa's draft National Artificial Intelligence Policy for public comment on 25 March 2026. It was gazetted on 10 April 2026 (No. 54477, Notice 3880). However, Communications Minister Solly Malatsi withdrew the draft on approximately 26 April 2026 after at least 6 of 67 academic citations were found to be AI-generated hallucinations. A revised draft is reported to be targeted for January 2027 after review by a national AI expert panel (reported May 2026).",
            "jsonld_only": True,
        },
        {
            "q": "What happened to South Africa's draft AI policy?",
            "a": "The draft was gazetted on 10 April 2026 but withdrawn approximately 26 April 2026 after AI-hallucinated academic citations were discovered. The 60-day comment window (closing 10 June 2026) was superseded by the withdrawal. A revised draft is expected in 2027.",
            "jsonld_only": True,
        },
        {
            "q": "Does South Africa have an AI Act?",
            "a": "No. The policy Cabinet approved is a policy, not an Act. Sector-specific regulations based on the policy are targeted for the 2027/2028 financial year. Until then, AI systems are governed by existing law: POPIA Section 71, the Copyright Act, the Competition Act, the Patents Act, and the King IV/King V Codes on Corporate Governance.",
            "jsonld_only": True,
        },
        {
            "q": "Will South Africa have a single AI regulator?",
            "a": "No. Reporting on the draft policy indicates a sector-specific, multi-regulator model. AI governance will be embedded within existing supervisory frameworks: the FSCA for financial services, the Information Regulator for data protection, the Council for Medical Schemes for health, ICASA for telecoms, the Department of Higher Education and Training for education, and others. This will be verified against the gazetted text when it publishes.",
            "jsonld_only": True,
        },
        {
            "q": "When does the public comment window open and close?",
            "a": "The comment window opened on 10 April 2026 and was scheduled to close on 10 June 2026, but was superseded when the draft was withdrawn on approximately 26 April 2026. A new comment period will open when a revised draft is published.",
            "jsonld_only": True,
        },
        {
            "q": "How does POPIA apply to AI systems?",
            "a": "POPIA Section 71 governs decisions based solely on automated processing of personal information, including profiling. A data subject is entitled not to be subject to such a decision unless specific exceptions apply. Any AI system deployed in South Africa that processes personal data already falls under POPIA, regardless of whether the draft AI policy has been gazetted.",
            "jsonld_only": True,
        },
        {
            "q": "What does King V require for AI governance?",
            "a": "King V was adopted by the Institute of Directors in South Africa on 31 October 2025 and is in force for financial years commencing on or after January 2026. It consolidates King IV's 17 principles into 13 and introduces explicit AI governance principles alongside enhanced cyber risk provisions. Governing bodies are now expected to oversee AI use and AI-related risk as a board-level matter.",
            "jsonld_only": True,
        },
        {
            "q": "What should South African organisations do now?",
            "a": "Inventory AI systems in production. Document data flows and consent bases. Identify each high-stakes deployment (hiring, credit scoring, healthcare triage, content moderation) and name the human function that reviews or can override the system. Map existing POPIA, Competition Act, and sector regulator obligations. Submit comments during the 60-day public comment window once the draft policy gazettes.",
            "jsonld_only": True,
        },
    ],
    # Visible sources live in sections_html (bespoke markup).
    "sources": [],
    # Hand-authored Article schema richer than the generated one
    # (isBasedOn Legislation entries) — emitted verbatim.
    "jsonld_article_override": json.loads(r'''
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "South Africa Draft AI Policy 2026 — Regula",
  "description": "South Africa's draft National AI Policy was approved by Cabinet in late March 2026, gazetted 10 April 2026, and withdrawn on ~26 April 2026 after fabricated citations were found; a revised draft is reported for January 2027. Live reference page covering what Cabinet approved, the sector-specific multi-regulator governance model, the timeline to gazette publication and sector regulations, the POPIA and King V baseline, and what organisations should do while the draft policy works through the gazette.",
  "image": "https://getregula.com/assets/og-image.png",
  "datePublished": "2026-04-07T00:00:00+02:00",
  "dateModified": "2026-07-16T00:00:00+02:00",
  "author": {
    "@type": "Organization",
    "name": "Regula",
    "url": "https://getregula.com"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Regula",
    "url": "https://getregula.com",
    "logo": {
      "@type": "ImageObject",
      "url": "https://getregula.com/assets/og-image.png"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://getregula.com/regions/south-africa-ai-policy.html"
  },
  "about": [
    {
      "@type": "Thing",
      "name": "South Africa National Artificial Intelligence Policy"
    },
    {
      "@type": "Thing",
      "name": "Department of Communications and Digital Technologies"
    },
    {
      "@type": "Thing",
      "name": "POPIA"
    },
    {
      "@type": "Thing",
      "name": "Artificial Intelligence Governance"
    }
  ],
  "isBasedOn": [
    {
      "@type": "CreativeWork",
      "name": "South Africa National Artificial Intelligence Policy Framework",
      "datePublished": "2024-10",
      "publisher": {
        "@type": "GovernmentOrganization",
        "name": "Department of Communications and Digital Technologies, Republic of South Africa"
      }
    }
  ]
}
'''),
    "head_extra": """
    <meta name="ICBM" content="-25.7479, 28.2293">
    <meta property="article:tag" content="South Africa">
    <meta property="article:tag" content="AI Policy">
    <meta property="article:tag" content="AI Governance">
    <meta property="article:tag" content="POPIA">
    <meta property="article:tag" content="DCDT">
    <link rel="alternate" hreflang="en-za" href="https://getregula.com/regions/south-africa-ai-policy.html">
""",
    "extra_html": """

    <div style="max-width:760px;margin:var(--s7) auto var(--s5);padding:0 var(--s5);">
        <h3 style="font-size:18px;color:var(--text);margin-bottom:var(--s3);">Related reading</h3>
        <ul style="list-style:none;padding:0;margin:0;">
            <li style="margin-bottom:var(--s2);"><a href="/blog/blog-does-ai-act-apply.html" style="color:var(--accent);">Does the EU AI Act Apply to Your AI App?</a> <span style="color:var(--text-dim);font-size:14px;">— Extraterritorial reach and cross-border applicability</span></li>
        </ul>
    </div>
""",
    "body_end_html": """
    <script>
        // Progressive-enhancement tracker: fetch sa-tracker.json and replace
        // the static rows if the JSON is newer. Static HTML remains the SEO
        // and no-JS fallback, so nothing breaks if the fetch fails.
        (function() {
            const STATE_LABELS = {
                verified: { text: 'VERIFIED', cls: 'ok' },
                secondary: { text: 'SECONDARY', cls: 'pend' },
                pending: { text: 'PENDING', cls: 'pend' },
                estimated: { text: 'ESTIMATED', cls: 'est' },
                gazetted: { text: 'GAZETTED', cls: 'ok' }
            };

            function esc(s) {
                return String(s)
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;');
            }

            function renderRow(row) {
                const state = STATE_LABELS[row.state] || null;
                const tag = state
                    ? ' &nbsp;<span class="' + state.cls + '">' + state.text + '</span>'
                    : '';
                return '<div class="tracker-row">'
                    + '<div class="lbl">' + esc(row.label) + '</div>'
                    + '<div class="val">' + esc(row.value) + tag + '</div>'
                    + '</div>';
            }

            const tracker = document.getElementById('sa-tracker');
            if (!tracker) return;
            const src = tracker.getAttribute('data-src');
            if (!src || !window.fetch) return;

            fetch(src, { cache: 'no-cache' })
                .then(function(r) { return r.ok ? r.json() : null; })
                .then(function(data) {
                    if (!data || !Array.isArray(data.rows)) return;
                    const rowsEl = document.getElementById('tracker-rows');
                    const tsEl = document.getElementById('tracker-ts');
                    if (rowsEl) {
                        rowsEl.innerHTML = data.rows.map(renderRow).join('');
                    }
                    if (tsEl && data.last_updated) {
                        tsEl.textContent = '· live · updated ' + data.last_updated;
                        tsEl.classList.add('live');
                    }
                })
                .catch(function() { /* static fallback already rendered */ });
        })();
    </script>
""",
}
