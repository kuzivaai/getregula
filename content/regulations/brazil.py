# regula-ignore — sourced regulatory prose for the Brazil page quotes the law's own risk vocabulary
"""Brazil — LGPD & Marco Legal da IA coverage page.

Data file consumed by scripts/build_regulations.py to generate
brazil-ai-regulation.html. Converted from the hand-maintained page
on 16 July 2026 (DQ-7); content carried verbatim from the reviewed
16 Jul state except: the tracker's entry-into-force row, which still
carried the pre-a0aa5e4 'one year per Art. 45' claim and now states
the verified 730/180-day phasing (Senado Notícias, 10 Dec 2024);
two stray Guides link artifacts removed; last-updated refreshed.

Key verified facts: PL 2338/2023 is NOT law — Senate approved
10 Dec 2024, Chamber Special Commission created 4 Apr 2025,
awaiting rapporteur's report (camara.leg.br, last action 17 Jun
2026). LGPD Lei 13.709/2018 in force; Art. 20 requires review of
solely-automated decisions but does NOT mandate human review."""

import json

REGION = {
    "slug": "brazil-ai-regulation",
    "flag": "🇧🇷",
    "nav_label": "Brazil",
    "lang": "en",
    "og_locale": "pt_BR",
    "hreflang_self": "en",
    "geo_region": "BR",
    "geo_placename": "Brazil",
    "status_cls": "",
    "status_text": "In committee &middot; Chamber of Deputies",
    "title_tag": "Brazil AI Regulation &mdash; LGPD &amp; Marco Legal da IA | Regula",
    "title_html": "Brazil AI Regulation &mdash; <span class=\"hl\">LGPD &amp; Marco Legal da IA</span>",
    "meta_description": "Brazil AI regulation tracker. PL 2338/2023 (Marco Legal da IA) status, LGPD automated decision rights, ANPD priorities, and developer guidance.",
    "meta_keywords": "Brazil AI regulation, LGPD AI compliance, Marco Legal da IA, regulamentação IA Brasil, PL 2338/2023, ANPD AI enforcement, Lei 13.709/2018, Brazil AI Act, LGPD Article 20, RIPD data protection impact report",
    "og_title": "Brazil AI Regulation — LGPD & Marco Legal da IA | Regula",
    "og_description": "PL 2338/2023 in committee. LGPD already applies to AI. Live tracker covering legislative status, ANPD enforcement, and developer guidance.",
    "twitter_title": "Brazil AI Regulation — LGPD & Marco Legal da IA | Regula",
    "twitter_description": "PL 2338/2023 in committee. LGPD already applies. Legislative tracker, ANPD enforcement priorities, developer checklist.",
    "last_updated": "4 August 2026",
    "published_time": "2026-04-25T00:00:00-03:00",
    "modified_time": "2026-08-04T00:00:00-03:00",
    "lede": "Brazil's Marco Legal da Inteligencia Artificial (PL 2338/2023) passed the Senate on 10 December 2024 and is now in a Special Commission at the Chamber of Deputies. It is not yet law. In the meantime, the LGPD already applies to AI systems that process personal data, including automated decision-making under Article 20. This page is the live reference &mdash; what is in force, what is pending, and what developers building for the Brazilian market should do now.",
    # Bespoke tracker (verbatim from the reviewed page) — used instead
    # of builder-rendered tracker_rows.
    "tracker_html": """
<div class="tracker">
            <h2>Legislative tracker</h2>
            <div>
                <div class="tracker-row">
                    <div class="lbl">Senate vote</div>
                    <div class="val">10 December 2024 &mdash; approved by symbolic vote &nbsp;<span class="ok">CONFIRMED</span></div>
                </div>
                <div class="tracker-row">
                    <div class="lbl">Chamber Special Commission</div>
                    <div class="val">Created 4 April 2025 &nbsp;<span class="ok">CONFIRMED</span></div>
                </div>
                <div class="tracker-row">
                    <div class="lbl">Current status</div>
                    <div class="val">Awaiting rapporteur's report in Special Commission (official Chamber status checked 4 August 2026; latest recorded action 17 June 2026) &nbsp;<span class="pend">IN COMMITTEE</span></div>
                </div>
                <div class="tracker-row">
                    <div class="lbl">Entry into force</div>
                    <div class="val">Phased in the Senate-approved text: 730 days after publication for most provisions; 180 days for generative/general-purpose systems, prohibited practices and author rights (Senado Notícias, 10 Dec 2024); the Chamber may modify this timeline &nbsp;<span class="est">ESTIMATED</span></div>
                </div>
                <div class="tracker-row">
                    <div class="lbl">Penalties (draft)</div>
                    <div class="val">Penalty ceilings are specified in the Senate-approved bill; the text may change in the Chamber</div>
                </div>
                <div class="tracker-row">
                    <div class="lbl">LGPD</div>
                    <div class="val">Lei 13.709/2018 &mdash; in force since September 2020 &nbsp;<span class="ok">IN FORCE</span></div>
                </div>
                <div class="tracker-row">
                    <div class="lbl">ANPD AI enforcement</div>
                    <div class="val">AI and automated decisions listed as 2026&ndash;2027 enforcement priorities</div>
                </div>
            </div>
        </div>
""",
    "tracker_rows": [],
    "sections_html": [
        {
            "id": "what-is-pl-2338",
            "heading": "What is PL 2338/2023?",
            "body": """\
            <p>PL 2338/2023, known as the <strong>Marco Legal da Inteligencia Artificial</strong>, is a bill that would establish a comprehensive legal framework for the development and use of artificial intelligence in Brazil. It originated in the Senate, where it was approved by symbolic vote on 10 December 2024.</p>

            <p>The bill was then sent to the Chamber of Deputies. On 4 April 2025, the Chamber created a Special Commission to analyse the text. The <a href="https://www.camara.leg.br/propostas-legislativas/2555663" target="_blank" rel="noopener">official Chamber status page</a>, checked on 4 August 2026, records that it is awaiting the rapporteur's report and lists 17 June 2026 as the latest legislative action. The Chamber may amend the text before voting; if it does, the bill returns to the Senate for conciliation.</p>

            <p>The Senate-approved text phases entry into force, but the Chamber may modify the implementation timeline and penalties before enactment. <a href="https://www25.senado.leg.br/web/atividade/materias/-/materia/157233" target="_blank" rel="noopener">Senado Federal: bill text and procedural history</a>.</p>

            <p class="note-inline">PL 2338/2023 is not yet law. The penalty ranges, risk classifications, and obligations described on this page reflect the Senate-approved text and may be modified by the Chamber of Deputies.</p>
""",
        },
        {
            "id": "risk-classification",
            "heading": "Risk classification under the Marco Legal",
            "body": """\
            <p>The Senate-approved text of PL 2338/2023 establishes three risk tiers. These broadly parallel the EU AI Act's risk pyramid but use different terminology and scope.</p>

            <h3>Excessive risk (risco excessivo) &mdash; prohibited</h3>
            <ul>
                <li>Social scoring by government entities</li>
                <li>Indiscriminate biometric surveillance in public spaces (with law-enforcement exceptions)</li>
                <li>AI systems that exploit vulnerabilities of specific groups (children, elderly, persons with disabilities) in ways that cause harm</li>
            </ul>

            <h3>High risk (alto risco)</h3>
            <ul>
                <li>AI used in <strong>employment</strong> decisions (recruitment, evaluation, dismissal)</li>
                <li>AI used in <strong>credit and insurance</strong> decisions</li>
                <li>AI used in <strong>education</strong> (admissions, grading, allocation)</li>
                <li>AI used in <strong>healthcare</strong> (diagnosis, treatment recommendations)</li>
                <li>AI used in <strong>criminal justice</strong> and law enforcement</li>
                <li>AI used in <strong>essential public services</strong> (welfare, utilities)</li>
                <li>AI used in <strong>autonomous vehicles</strong></li>
            </ul>
            <p>High-risk systems would be subject to impact assessments, human oversight requirements, transparency obligations, and documentation duties.</p>

            <h3>Non-high risk</h3>
            <p>All other AI systems would be subject to general transparency and good-practice obligations, including the right of users to know they are interacting with an AI system.</p>
""",
        },
        {
            "id": "lgpd-and-ai",
            "heading": "LGPD and AI: what applies today",
            "body": """\
            <p>While the Marco Legal works through the Chamber, the <strong>LGPD (Lei Geral de Protecao de Dados, Lei 13.709/2018)</strong> is already in force and already applies to AI systems that process personal data. Three articles are particularly relevant.</p>

            <h3>Article 20 &mdash; automated decision review</h3>
            <p>Data subjects have the right to request a <strong>review of decisions made solely by automated processing</strong> that affect their interests &mdash; including profiling, credit scoring, and hiring decisions. The data controller must provide clear and adequate information about the criteria and procedures used. Note: the original draft required <em>human</em> review, but a legislative amendment removed that requirement. Article 20 requires a review, but does not mandate that it be performed by a human. This applies to any AI system making decisions that affect individuals, regardless of whether the Marco Legal is enacted.</p>

            <h3>Article 38 &mdash; RIPD (data protection impact report)</h3>
            <p>The ANPD may require a <strong>Relatorio de Impacto a Protecao de Dados Pessoais (RIPD)</strong> for processing activities that present high risk to data subjects' fundamental rights and freedoms. AI-driven profiling, automated credit decisions, and large-scale processing of sensitive data are all candidates for a RIPD. This is Brazil's equivalent of a DPIA under the GDPR.</p>

            <h3>Article 11 &mdash; sensitive personal data</h3>
            <p>Processing of sensitive personal data (racial or ethnic origin, religious belief, political opinion, health data, biometric data, genetic data) requires explicit and specific consent or one of the narrow legal bases listed in Article 11. AI systems trained on or processing sensitive data face a higher compliance bar under the LGPD, regardless of the Marco Legal's status.</p>
""",
        },
        {
            "id": "anpd-enforcement",
            "heading": "ANPD enforcement priorities 2026&ndash;2027",
            "body": """\
            <p>The <strong>Autoridade Nacional de Protecao de Dados (ANPD)</strong> has signalled that AI and automated decisions are among its enforcement priorities for the 2026&ndash;2027 cycle. This means that even without the Marco Legal, the ANPD is actively looking at how organisations use AI in ways that touch personal data.</p>

            <p>Areas of particular ANPD focus include:</p>
            <ul>
                <li><strong>Automated decision-making</strong> that affects individuals' rights (Article 20 enforcement)</li>
                <li><strong>Transparency</strong> in algorithmic processing of personal data</li>
                <li><strong>Impact assessments</strong> for high-risk automated processing</li>
                <li><strong>Cross-border data transfers</strong> involving AI systems</li>
            </ul>

            <p>Organisations deploying AI in Brazil should not wait for the Marco Legal to become law. The ANPD already has enforcement authority under the LGPD, and AI-related processing is squarely in its sights.</p>
""",
        },
        {
            "id": "what-to-do",
            "heading": "What developers should do now",
            "body": """\
            <p>Whether or not PL 2338/2023 is enacted this year, the following steps are worth taking today. All are grounded in obligations that already exist under the LGPD or that will apply under the Marco Legal regardless of final text.</p>
            <ol>
                <li><strong>Inventory your AI systems.</strong> List every AI-powered feature in production: what data it processes, what decisions it makes or influences, and which user categories it affects. The LGPD already requires you to know this.</li>
                <li><strong>Map your automated decisions.</strong> Identify every system that makes decisions solely by automated processing. Under LGPD Article 20, data subjects can request a review of these decisions. Document the criteria, the logic, and the review mechanism for each one. While Article 20 does not require human review specifically, implementing a human review path is a best practice that also prepares you for Marco Legal obligations.</li>
                <li><strong>Assess whether you need a RIPD.</strong> If your AI system processes personal data at scale, profiles individuals, or handles sensitive data categories, you likely need a data protection impact report under LGPD Article 38.</li>
                <li><strong>Review your sensitive data processing.</strong> AI systems trained on or inferring sensitive personal data (health, biometrics, racial/ethnic origin) face stricter requirements under LGPD Article 11. Confirm your legal basis.</li>
                <li><strong>Prepare for Marco Legal high-risk obligations.</strong> If your system falls into any of the high-risk categories (employment, credit, education, healthcare, criminal justice, essential services, autonomous vehicles), start documenting risk assessments, human oversight provisions, and transparency measures now. You will need them if the bill passes.</li>
                <li><strong>Track the bill.</strong> Follow the Special Commission proceedings at the <a href="https://www.camara.leg.br" target="_blank" rel="noopener">Camara dos Deputados</a>. The rapporteur's report will signal what the final text looks like.</li>
            </ol>
""",
        },
        {
            "id": "regula",
            "heading": "How Regula helps",
            "body": """\
            <p>Regula is an <strong>open-source compliance CLI</strong> that combines code scanning with governance questionnaires for AI risk assessment. Its framework crosswalk already includes both the LGPD and the Marco Legal da IA, so you can map risk findings to the relevant Brazilian articles today.</p>

            <p>For a team building AI for the Brazilian market, the practically useful commands are:</p>

<pre><code><span class="term-comment"># Install</span>
<span class="term-cmd">pipx install regula-ai</span>

<span class="term-comment"># Scan for risk indicators with Brazil-specific mapping</span>
<span class="term-cmd">regula check --jurisdictions brazil .</span>  <span class="term-comment"># Maps findings to LGPD articles</span>

<span class="term-comment"># Gap analysis against Brazilian frameworks</span>
<span class="term-cmd">regula gap --framework lgpd</span>            <span class="term-comment"># LGPD article-by-article gap assessment</span>
<span class="term-cmd">regula gap --framework marco-legal-ia</span>  <span class="term-comment"># Marco Legal gap assessment</span>

<span class="term-comment"># Inventory what you have</span>
<span class="term-cmd">regula discover .</span>                      <span class="term-comment"># AI systems present in the project</span>
<span class="term-cmd">regula inventory</span>                       <span class="term-comment"># AI library / model references</span>

<span class="term-comment"># Generate compliance evidence</span>
<span class="term-cmd">regula conform</span>                         <span class="term-comment"># Conformity evidence pack</span>
<span class="term-cmd">regula oversight</span>                       <span class="term-comment"># Human oversight detection</span>

<span class="term-comment"># Health and reproducibility</span>
<span class="term-cmd">regula self-test</span>
<span class="term-cmd">regula doctor</span></code></pre>

            <p>The framework crosswalk covers all 7 EU AI Act obligation articles (Articles 9&ndash;15), each mapped to both LGPD and Marco Legal articles. This means you can use the same scan to understand your compliance posture across the EU AI Act, the LGPD, and the Marco Legal simultaneously.</p>

            <p>Regula is open source, written in Python with <strong>zero production dependencies</strong>, and the entire detection ruleset is in the repository. Brazilian teams can fork it, add Brazil-specific patterns, and contribute them back.</p>

            <div class="cta-row">
                <div class="cta-card">
                    <h3>Install Regula</h3>
                    <p>Open source, zero dependencies, runs locally.</p>
                    <a href="https://github.com/kuzivaai/getregula" target="_blank" rel="noopener">github.com/kuzivaai/getregula &rarr;</a>
                </div>
                <div class="cta-card">
                    <h3>Contribute BR patterns</h3>
                    <p>LGPD, ANPD, sector-specific markers welcome.</p>
                    <a href="https://github.com/kuzivaai/getregula/issues" target="_blank" rel="noopener">Open an issue &rarr;</a>
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
                    <summary>What is PL 2338/2023 (Marco Legal da IA)?</summary>
                    <p>PL 2338/2023, known as the Marco Legal da Inteligencia Artificial, is a bill that would establish a legal framework for AI in Brazil. The Senate approved it by symbolic vote on 10 December 2024. It was sent to the Chamber of Deputies, where a Special Commission was created on 4 April 2025. The official Chamber status page, checked on 4 August 2026, records that the bill is awaiting the rapporteur's report. It is not yet law.</p>
                </details>
                <details>
                    <summary>Does Brazil have an AI law?</summary>
                    <p>Not yet. PL 2338/2023 passed the Senate on 10 December 2024 but is still being considered by the Chamber of Deputies. The Senate-approved text phases entry into force: most provisions apply 730 days (two years) after publication, while rules on generative and general-purpose systems, prohibited practices and author rights apply after 180 days (Senado Noticias, 10 Dec 2024). The Chamber may modify this timeline. In the meantime, the LGPD (Lei 13.709/2018) already applies to AI systems that process personal data, including automated decision-making under Article 20.</p>
                </details>
                <details>
                    <summary>How does the LGPD apply to AI systems?</summary>
                    <p>The LGPD applies to any AI system that processes personal data of individuals in Brazil. Article 20 gives data subjects the right to request a review of decisions made solely by automated processing that affect their interests (note: the original draft required human review, but that requirement was removed by legislative amendment). Article 38 requires a RIPD (data protection impact report) for high-risk processing. Article 11 imposes stricter rules when sensitive personal data is involved. The ANPD has signalled that AI and automated decisions are enforcement priorities for 2026&ndash;2027.</p>
                </details>
                <details>
                    <summary>What are the penalties under the Marco Legal da IA?</summary>
                    <p>The Senate-approved bill specifies financial penalties, but those provisions may change during Chamber deliberation and are not current law. <a href="https://www25.senado.leg.br/web/atividade/materias/-/materia/157233" target="_blank" rel="noopener">Senado Federal: bill text and status</a>.</p>
                </details>
                <details>
                    <summary>What risk categories does the Marco Legal define?</summary>
                    <p>The bill as approved by the Senate establishes three risk tiers: excessive risk (prohibited uses such as social scoring by government and indiscriminate biometric surveillance), high risk (AI used in employment, credit, education, healthcare, criminal justice, essential services, and autonomous vehicles), and non-high risk (subject to general transparency and good-practice obligations). The Chamber may modify these categories.</p>
                </details>
                <details>
                    <summary>What should Brazilian developers do now?</summary>
                    <p>Inventory AI systems in production. Map every automated decision to its LGPD Article 20 review mechanism. Assess whether a RIPD is needed under Article 38. Review sensitive data processing against Article 11. Prepare documentation for Marco Legal high-risk obligations. Track the Special Commission proceedings at the Chamber of Deputies.</p>
                </details>
                <details>
                    <summary>Can Regula scan for LGPD and Marco Legal compliance?</summary>
                    <p>Yes. Regula's framework crosswalk includes both LGPD and Marco Legal da IA. The commands <code>regula gap --framework lgpd</code> and <code>regula gap --framework marco-legal-ia</code> map risk findings to the relevant articles of each framework. The command <code>regula check --jurisdictions brazil</code> applies LGPD-mapped rules to your scan results.</p>
                </details>
                <details>
                    <summary>How does the Marco Legal compare to the EU AI Act?</summary>
                    <p>Both use a risk-based approach, but their categories, institutions, and procedures differ. The Brazilian bill remains subject to Chamber amendment. <a href="https://www25.senado.leg.br/web/atividade/materias/-/materia/157233" target="_blank" rel="noopener">Senado Federal bill record</a>.</p>
                </details>
            </div>
""",
        },
        {
            "id": "honest-gaps",
            "heading": "What we are tracking and what may change",
            "body": """\
            <p>The Marco Legal is still in committee. The final text may differ significantly from the Senate-approved version. Here is what we are watching as of 4 August 2026:</p>
            <div class="gaps-box">
                <h3>To verify on enactment</h3>
                <ol>
                    <li><strong>High-risk category definitions.</strong> The Chamber may add, remove, or redefine high-risk categories. Autonomous vehicles, in particular, were a late addition and may be scoped differently.</li>
                    <li><strong>Penalty ranges.</strong> The Senate-approved provisions may be adjusted during Chamber deliberation.</li>
                    <li><strong>Supervisory authority.</strong> The Senate text assigns oversight roles but the final institutional arrangement (single authority vs sector-specific model) may change.</li>
                    <li><strong>Transition period.</strong> The Senate-approved text phases entry into force: 730 days for most provisions, 180 days for generative/prohibited-practice/author-rights rules (Senado Noticias, 10 Dec 2024; some analyses cite Art. 80 of the approved substitute). An earlier version of this page stated a single one-year window citing Art. 45 — that was wrong. The final timeline will be confirmed upon enactment.</li>
                    <li><strong>ANPD role.</strong> Whether the ANPD becomes the primary AI regulator or shares authority with sector-specific regulators.</li>
                    <li><strong>Senate conciliation.</strong> If the Chamber amends the text, it returns to the Senate. The final text may differ from both the Senate-approved and Chamber-amended versions.</li>
                </ol>
            </div>
            <p>We update this page as the bill progresses. If you want to be notified when the tracker changes, <a href="https://github.com/kuzivaai/getregula" target="_blank" rel="noopener">watch the repository</a>.</p>
""",
        },
        {
            "id": "sources",
            "heading": "Sources",
            "body": """\
            <div class="sources">
                <h3>Primary and secondary sources</h3>
                <ul>
                    <li><strong>Senado Federal &mdash; PL 2338/2023</strong> &mdash; full legislative text, voting record, and procedural history. <a href="https://www25.senado.leg.br/web/atividade/materias/-/materia/157233" target="_blank" rel="noopener">senado.leg.br/materia/157233</a></li>
                    <li><strong>Camara dos Deputados</strong> &mdash; Special Commission creation (4 April 2025), rapporteur appointment, and procedural updates. <a href="https://www.camara.leg.br" target="_blank" rel="noopener">www.camara.leg.br</a></li>
                    <li><strong>LGPD (Lei 13.709/2018)</strong> &mdash; full text of the Lei Geral de Protecao de Dados. Articles 11, 20, and 38 govern sensitive data, automated decisions, and data protection impact reports respectively.</li>
                    <li><strong>ANPD &mdash; Autoridade Nacional de Protecao de Dados</strong> &mdash; enforcement priorities and regulatory agenda. <a href="https://www.gov.br/anpd" target="_blank" rel="noopener">gov.br/anpd</a></li>
                    <li><strong>Securiti</strong> &mdash; analysis of PL 2338/2023 risk classification and penalty structure. Used as a secondary source for the risk tier summary.</li>
                    <li><strong>Baker McKenzie</strong> &mdash; legal analysis of the Marco Legal da IA and its interaction with the LGPD. Used as a secondary source for the framework comparison.</li>
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
            "q": "What is PL 2338/2023 (Marco Legal da IA)?",
            "a": "PL 2338/2023, known as the Marco Legal da Inteligência Artificial, is a bill that would establish a legal framework for AI in Brazil. The Senate approved it by symbolic vote on 10 December 2024. The official Chamber status page, checked on 4 August 2026, records that the bill is awaiting the rapporteur's report in the Special Commission. It is not yet law.",
            "jsonld_only": True,
        },
        {
            "q": "O que é o PL 2338/2023 (Marco Legal da IA)?",
            "a": "O PL 2338/2023, conhecido como Marco Legal da Inteligência Artificial, é um projeto de lei que estabeleceria um marco regulatório para IA no Brasil. O Senado aprovou por votação simbólica em 10 de dezembro de 2024. Foi enviado à Câmara dos Deputados, onde uma Comissão Especial foi criada em 4 de abril de 2025. Em abril de 2026, aguarda relatório do relator na Comissão Especial. Ainda não é lei.",
            "jsonld_only": True,
        },
        {
            "q": "Does Brazil have an AI law?",
            "a": "Not yet. PL 2338/2023 passed the Senate on 10 December 2024 but is still being considered by the Chamber of Deputies. The Senate-approved text phases entry into force: most provisions apply 730 days (two years) after publication, while rules on generative and general-purpose systems, prohibited practices and author rights apply after 180 days (Senado Noticias, 10 Dec 2024). The Chamber may modify this timeline. In the meantime, the LGPD (Lei 13.709/2018) already applies to AI systems that process personal data, including automated decision-making under Article 20.",
            "jsonld_only": True,
        },
        {
            "q": "How does the LGPD apply to AI systems?",
            "a": "The LGPD applies to any AI system that processes personal data of individuals in Brazil. Article 20 gives data subjects the right to request a review of decisions made solely by automated processing that affect their interests (note: the original draft required human review, but a legislative amendment removed that requirement — Article 20 requires a review but does not mandate it be performed by a human). Article 38 requires a RIPD (Relatório de Impacto à Proteção de Dados Pessoais) for high-risk processing. Article 11 imposes stricter rules when sensitive personal data is involved. The ANPD has signalled that AI and automated decisions are enforcement priorities for 2026–2027.",
            "jsonld_only": True,
        },
        {
            "q": "What are the penalties under the Marco Legal da IA?",
            "a": "If PL 2338/2023 is enacted as currently drafted, penalties include fines of up to R$50,000,000 (fifty million reais) or 2% of the gross revenue of the group or conglomerate in Brazil, per infraction (Senado Noticias, 10 Dec 2024). These penalty ranges are subject to change during Chamber deliberation.",
            "jsonld_only": True,
        },
        {
            "q": "What risk categories does the Marco Legal define?",
            "a": "The bill as approved by the Senate establishes three risk tiers: excessive risk (prohibited uses such as social scoring by government and indiscriminate biometric surveillance), high risk (AI used in employment, credit, education, healthcare, criminal justice, essential services, and autonomous vehicles), and non-high risk (subject to general transparency and good-practice obligations). The Chamber may modify these categories.",
            "jsonld_only": True,
        },
        {
            "q": "Quais são as penalidades previstas no Marco Legal da IA?",
            "a": "Conforme aprovado pelo Senado, as sanções incluem multa de até R$50.000.000 (cinquenta milhões de reais) ou 2% do faturamento anual por infração, o que for maior. Esses valores podem ser alterados durante a tramitação na Câmara dos Deputados.",
            "jsonld_only": True,
        },
        {
            "q": "Can Regula scan for LGPD and Marco Legal compliance?",
            "a": "Yes. Regula's framework crosswalk includes both LGPD and Marco Legal da IA. The commands 'regula gap --framework lgpd' and 'regula gap --framework marco-legal-ia' map risk findings to the relevant articles of each framework. The command 'regula check --jurisdictions brazil' applies LGPD-mapped rules to your scan results.",
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
  "headline": "Brazil AI Regulation — LGPD & Marco Legal da IA | Regula",
  "description": "PL 2338/2023 (Marco Legal da IA) is awaiting a rapporteur's report in the Chamber of Deputies Special Commission. LGPD already governs automated decisions via Article 20. Live reference covering legislative status, risk classification under the bill, ANPD enforcement priorities, and what developers should do now.",
  "image": "https://getregula.com/assets/og-image.png",
  "datePublished": "2026-04-25T00:00:00-03:00",
  "dateModified": "2026-07-16T00:00:00-03:00",
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
    "@id": "https://getregula.com/regions/brazil-ai-regulation.html"
  },
  "about": [
    {
      "@type": "Thing",
      "name": "PL 2338/2023 Marco Legal da Inteligência Artificial"
    },
    {
      "@type": "Thing",
      "name": "LGPD Lei Geral de Proteção de Dados"
    },
    {
      "@type": "Thing",
      "name": "ANPD Autoridade Nacional de Proteção de Dados"
    },
    {
      "@type": "Thing",
      "name": "Artificial Intelligence Governance"
    }
  ],
  "isBasedOn": [
    {
      "@type": "Legislation",
      "name": "PL 2338/2023 — Marco Legal da Inteligência Artificial",
      "url": "https://www25.senado.leg.br/web/atividade/materias/-/materia/157233",
      "publisher": {
        "@type": "GovernmentOrganization",
        "name": "Senado Federal do Brasil"
      }
    },
    {
      "@type": "Legislation",
      "name": "Lei 13.709/2018 — Lei Geral de Proteção de Dados (LGPD)",
      "datePublished": "2018-08-14",
      "publisher": {
        "@type": "GovernmentOrganization",
        "name": "Presidência da República Federativa do Brasil"
      }
    }
  ]
}
'''),
    "head_extra": """
    <meta name="ICBM" content="-15.7801, -47.9292">
    <meta property="article:tag" content="Brazil">
    <meta property="article:tag" content="LGPD">
    <meta property="article:tag" content="Marco Legal da IA">
    <meta property="article:tag" content="AI Regulation">
    <meta property="article:tag" content="ANPD">
    <link rel="alternate" hreflang="pt-br" href="https://getregula.com/regions/brazil-ai-regulation.html">
""",
    "extra_html": """

    <div style="max-width:760px;margin:var(--s7) auto var(--s5);padding:0 var(--s5);">
        <h3 style="font-size:18px;color:var(--text);margin-bottom:var(--s3);">Related reading</h3>
        <ul style="list-style:none;padding:0;margin:0;">
            <li style="margin-bottom:var(--s2);"><a href="/blog/blog-does-ai-act-apply.html" style="color:var(--accent);">Does the EU AI Act Apply to Your AI App?</a> <span style="color:var(--text-dim);font-size:14px;">&mdash; Extraterritorial reach and cross-border applicability</span></li>
            <li style="margin-bottom:var(--s2);"><a href="/regions/south-africa-ai-policy.html" style="color:var(--accent);">South Africa Draft National AI Policy</a> <span style="color:var(--text-dim);font-size:14px;">&mdash; Another emerging-market AI governance framework</span></li>
        </ul>
    </div>
""",
}
