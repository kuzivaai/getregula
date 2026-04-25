# regula-ignore
"""United Kingdom — AI regulation coverage page.

Data file consumed by scripts/build_regulations.py to generate
uk-ai-regulation.html. Schema is defined by REGION_SCHEMA in the
build script. Every claim here is either verifiable against a
primary source or explicitly labelled as pending verification.
"""

REGION = {
    "slug": "uk-ai-regulation",
    "flag": "🇬🇧",
    "nav_label": "UK",
    "lang": "en-GB",
    "og_locale": "en_GB",
    "hreflang_self": "en-gb",
    "geo_region": "GB",
    "geo_placename": "United Kingdom",

    "status_cls": "live",
    "status_text": "Coverage in progress · frameworks live",

    "title_tag": "UK AI Regulation Tracker — ICO, DSIT, principles-based | Regula",
    "title_html": 'United Kingdom — <span class="hl">AI regulation</span> tracker',
    "meta_description": (
        "Live tracker of the UK's principles-based, sector-specific AI regulation. "
        "ICO data protection guidance, DSIT AI policy, Regula's framework crosswalk "
        "to UK DSIT/ICO principles, and what UK organisations should do today — "
        "regardless of whether a dedicated AI Act materialises."
    ),
    "meta_keywords": (
        "UK AI regulation, ICO AI guidance, DSIT AI policy, UK AI Bill, "
        "sector-specific AI regulation, UK data protection AI, principles-based AI"
    ),
    "og_title": "UK AI Regulation Tracker — Regula",
    "og_description": (
        "The UK's principles-based, sector-specific approach to AI regulation. "
        "What's in force, what's in consultation, and what UK organisations should do today."
    ),
    "twitter_title": "UK AI Regulation Tracker — Regula",
    "twitter_description": (
        "ICO + DSIT-led, principles-based, sector-specific. Regula's live coverage."
    ),

    "last_updated": "2026-04-08",
    "published_time": "2026-04-08T00:00:00+00:00",
    "modified_time": "2026-04-08T00:00:00+00:00",

    "lede": (
        "The United Kingdom has taken a deliberately different path to the EU. "
        "Instead of a single AI Act, the UK approach is principles-based and "
        "sector-specific: existing regulators (ICO, MHRA, Ofcom, FCA, CMA) are "
        "asked to interpret AI through their own mandates, guided by the "
        "government's five cross-cutting principles. This page tracks what is "
        "already in force, what is in consultation, and what Regula can tell "
        "you about your code today — regardless of whether a dedicated UK AI "
        "Act materialises."
    ),

    "tracker_rows": [
        {
            "label": "Regulatory model",
            "value": "Principles-based, sector-specific — no dedicated AI Act",
            "state": "verified",
        },
        {
            "label": "Lead departments",
            "value": "DSIT (policy) · ICO (data protection)",
            "state": "verified",
        },
        {
            "label": "Five cross-cutting principles",
            "value": (
                "Safety/security/robustness · appropriate transparency/explainability · "
                "fairness · accountability/governance · contestability/redress"
            ),
            "state": "verified",
        },
        {
            "label": "ICO AI guidance",
            "value": (
                "In force — automated decision-making (UK GDPR Art. 22), "
                "DPIAs for AI, explainability under the AI & Data Protection toolkit"
            ),
            "state": "verified",
        },
        {
            "label": "Regula framework coverage",
            "value": "ICO / DSIT principles mapped in references/framework_crosswalk.yaml",
            "state": "verified",
        },
        {
            "label": "Dedicated AI Act",
            "value": "Not currently on the government's legislative agenda",
            "state": "pending",
        },
    ],

    "sections_html": [
        {
            "id": "what-is-in-force",
            "heading": "What is already in force in the UK",
            "body": """
<p>Unlike the EU AI Act, the UK does not have a single piece of AI legislation. But UK organisations deploying AI are already bound by a substantial body of existing law and regulator guidance. None of this requires waiting for a future Act.</p>
<ul>
    <li><strong>UK GDPR and the Data Protection Act 2018</strong> — in particular <strong>Article 22</strong> on automated decision-making, which gives data subjects the right not to be subject to decisions based solely on automated processing where those decisions produce legal or similarly significant effects. The ICO's <strong>AI and Data Protection Risk Toolkit</strong> is the operational guidance. This already binds every UK AI deployment that touches personal data.</li>
    <li><strong>ICO Guidance on Explaining Decisions Made with AI</strong> (co-developed with the Alan Turing Institute) — the working standard for what "appropriate transparency" looks like in practice. Sets expectations for rationale, responsibility, data, fairness, safety and impact explanations.</li>
    <li><strong>Sector regulator guidance</strong> — the FCA on algorithmic trading and credit decisions, the MHRA on software as a medical device, Ofcom on online safety (including the Online Safety Act 2023 illegal-harms and children's-safety duties where AI is a material part of the service), the CMA on algorithmic pricing and consumer protection. Each of these applies independently of any future AI Act.</li>
    <li><strong>Equality Act 2010</strong> — the non-statutory legal baseline for AI fairness claims. An AI system that produces discriminatory outputs on protected characteristics is actionable today under existing anti-discrimination law, not in 2027 under a new Act.</li>
    <li><strong>Employment law on automated monitoring and hiring</strong> — a growing area of ICO enforcement and tribunal activity. Organisations using AI for CV screening or workplace monitoring are already in scope.</li>
</ul>
<p>The government's March 2023 white paper <em>"A pro-innovation approach to AI regulation"</em> and subsequent responses set out <strong>five cross-cutting principles</strong> that existing regulators are expected to apply: safety/security/robustness; appropriate transparency and explainability; fairness; accountability and governance; and contestability and redress. These are non-statutory principles, but they shape regulator expectations and are the framework Regula maps its findings against.</p>
""",
        },
        {
            "id": "where-the-regulatory-model-stands",
            "heading": "Where the UK regulatory model stands",
            "body": """
<p>The UK's position, in plain language: the government has so far chosen <em>not</em> to create an EU-style AI Act. The argument is that existing regulators already have the powers they need and that a horizontal AI Act would stifle innovation. Critics argue that this creates a coordination problem and leaves gaps in areas no single regulator owns cleanly.</p>
<p>What has actually happened:</p>
<ul>
    <li><strong>ICO has scaled up AI enforcement</strong> — the 2023 Snap "My AI" consultation, Clearview AI enforcement, ongoing work on generative AI and training data.</li>
    <li><strong>The AI Safety Institute</strong> (formerly the AI Safety Summit apparatus) focuses on frontier model evaluations, not day-to-day code compliance.</li>
    <li><strong>DSIT</strong> publishes periodic policy updates and has proposed, but not legislated, a statutory duty on regulators to have regard to the five principles.</li>
    <li><strong>Parliamentary debate</strong> continues over whether to introduce a UK AI Bill. Multiple private members' bills have been tabled. None have become law.</li>
</ul>
<p>We do not speculate here about what the UK <em>might</em> legislate. The tracker above will flip the "dedicated AI Act" row from pending to verified the moment a bill receives Royal Assent or enters formal consultation with a published text.</p>
""",
        },
        {
            "id": "what-to-do-today",
            "heading": "What UK organisations should do today",
            "body": """
<p>Because the UK approach is principles-based and sector-specific rather than prescriptive, the work UK organisations need to do looks more like mature data protection and risk management than EU AI Act-style conformity assessment. The five practical steps:</p>
<ol>
    <li><strong>Complete an AI-focused DPIA</strong> for every high-stakes AI deployment — hiring, credit, healthcare, benefits, content moderation, biometric processing. The ICO's AI and Data Protection Risk Toolkit is the operational spec. Regula's <code>regula gap</code> and <code>regula oversight</code> commands produce inputs that map directly onto the ICO's risk categories.</li>
    <li><strong>Document human oversight</strong> for each automated decision path. UK GDPR Article 22 plus ICO guidance plus the "contestability and redress" principle all point at the same control: a named human function that can review and override. Regula's <code>regula oversight</code> traces AI model outputs through call chains cross-file and flags the gate-or-no-gate question.</li>
    <li><strong>Map your exposure to sector regulators.</strong> If you are in finance, the FCA's algorithmic trading and consumer credit guidance applies. If medical, MHRA SaMD guidance. If online services, Ofcom's Online Safety Act duties. Do this mapping before a regulator asks you to.</li>
    <li><strong>Run a framework crosswalk scan.</strong> Regula ships with the UK DSIT / ICO principles in <code>references/framework_crosswalk.yaml</code>. A single <code>regula check</code> run reports findings against the five cross-cutting principles alongside EU AI Act, NIST AI RMF, ISO 42001 and the ten other frameworks it covers.</li>
    <li><strong>Keep a watching brief on the AI Safety Institute's evaluations</strong> — they set the standard for what "safety" means in practice for frontier-scale models. If you are fine-tuning or deploying GPAI, their evaluation methodology is the closest thing the UK has to an operational safety bar today.</li>
</ol>
""",
        },
        {
            "id": "where-regula-fits",
            "heading": "Where Regula fits for UK teams",
            "body": """
<p>Regula is an open-source compliance CLI that combines code scanning with governance questionnaires for AI risk assessment. It was built primarily against the EU AI Act, but every finding is also mapped to UK DSIT / ICO principles (among twelve other frameworks). For a UK team the practically useful starting commands are:</p>
<pre><code>pip install regula-ai

regula discover .              # AI systems present in the project
regula check .                 # Risk indicators against all twelve frameworks
regula gap --project .         # Principles-based gap assessment
regula oversight .             # Cross-file human oversight detection (Art 22 / contestability)
regula conform .               # Evidence pack — works for DPIA source material too
regula sbom --ai-bom .         # AI Bill of Materials (CycloneDX 1.7 ML-BOM)
regula doctor                  # Installation health check
</code></pre>
<p>The framework crosswalk at <code>references/framework_crosswalk.yaml</code> is where the UK principle mapping lives. If a UK-specific pattern is missing (for example an ICO guidance update or a new sector regulator expectation), <a href="https://github.com/kuzivaai/getregula/issues">open an issue</a>.</p>
""",
        },
        {
            "id": "what-we-are-tracking",
            "heading": "What we are tracking for the UK page",
            "body": """
<p>This page will be updated as the UK landscape moves. Specifically we are watching for:</p>
<ol>
    <li><strong>Any UK AI Bill</strong> that reaches formal consultation or First Reading with a published text, at which point we document it and flip the tracker row.</li>
    <li><strong>ICO AI enforcement actions</strong> — specific monetary penalties or enforcement notices against AI deployments, which become useful precedent for DPIA scope.</li>
    <li><strong>Sector regulator guidance updates</strong> from FCA, MHRA, Ofcom, CMA — where a new or revised rule materially changes what developers need to do.</li>
    <li><strong>AI Safety Institute evaluation results</strong> when they are published and applicable to deployed commercial systems rather than closed frontier labs.</li>
    <li><strong>UK GDPR reform</strong> — the Data (Use and Access) Bill continues through Parliament and may change the Article 22 framing. We will document any material change.</li>
</ol>
<p>If you spot something we have missed, please <a href="https://github.com/kuzivaai/getregula/issues">open an issue</a>. We update by reader demand and source quality, not marketing signal.</p>
""",
        },
    ],

    "faq": [
        {
            "q": "Does the UK have an AI Act?",
            "a": (
                "No. The UK has deliberately chosen a principles-based, sector-specific "
                "approach instead of a dedicated AI Act. Existing regulators (ICO, FCA, "
                "MHRA, Ofcom, CMA, and others) apply their own mandates to AI, guided by "
                "the government's five cross-cutting principles."
            ),
        },
        {
            "q": "What are the UK's five AI principles?",
            "a": (
                "Safety, security and robustness; appropriate transparency and "
                "explainability; fairness; accountability and governance; and contestability "
                "and redress. Set out in the March 2023 DSIT white paper and subsequent "
                "responses. Non-statutory but expected to guide regulator behaviour."
            ),
        },
        {
            "q": "Does UK GDPR apply to AI systems?",
            "a": (
                "Yes, comprehensively. Any AI system processing personal data falls under "
                "UK GDPR. Article 22 gives data subjects the right not to be subject to "
                "decisions based solely on automated processing where those decisions "
                "produce legal or similarly significant effects. The ICO's AI and Data "
                "Protection Risk Toolkit is the operational guidance."
            ),
        },
        {
            "q": "Which UK regulator owns AI?",
            "a": (
                "No single regulator. The model is deliberately sector-specific: ICO for "
                "data protection, FCA for financial services, MHRA for medical devices, "
                "Ofcom for online safety and broadcasting, CMA for competition and consumer "
                "protection, HSE for workplace safety. DSIT is the lead policy department "
                "but does not have direct enforcement powers."
            ),
        },
        {
            "q": "What should UK organisations do about AI compliance today?",
            "a": (
                "Complete an AI-focused DPIA for every high-stakes deployment. Document "
                "human oversight for each automated decision path. Map your sector regulator "
                "exposure. Run a framework crosswalk scan against the UK DSIT/ICO principles. "
                "Keep a watching brief on the AI Safety Institute and on any UK AI Bill in "
                "Parliament. None of this requires waiting for a future Act."
            ),
        },
        {
            "q": "Does Regula cover UK frameworks?",
            "a": (
                "Yes. Regula's framework crosswalk includes the UK DSIT/ICO principles "
                "alongside the EU AI Act, NIST AI RMF, NIST AI 600-1, ISO 42001, ISO 27001, "
                "SOC 2, OWASP LLM Top 10, MITRE ATLAS, CRA, LGPD and Marco Legal IA. A "
                "single regula check run reports findings against all of them."
            ),
        },
    ],

    "sources": [
        {
            "title": "DSIT — A pro-innovation approach to AI regulation",
            "note": "March 2023 white paper and subsequent responses setting out the five cross-cutting principles.",
            "url": "https://www.gov.uk/government/publications/ai-regulation-a-pro-innovation-approach",
        },
        {
            "title": "ICO — Guidance on AI and data protection",
            "note": "Operational guidance for AI deployments touching personal data, including the AI and Data Protection Risk Toolkit.",
            "url": "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/",
        },
        {
            "title": "ICO / Alan Turing Institute — Explaining Decisions Made with AI",
            "note": "The working standard for what 'appropriate transparency' looks like under UK GDPR.",
            "url": "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/explaining-decisions-made-with-artificial-intelligence/",
        },
        {
            "title": "Data Protection Act 2018 and UK GDPR",
            "note": "Article 22 on automated decision-making is the single most important article for UK AI deployments.",
            "url": "https://www.legislation.gov.uk/ukpga/2018/12/contents",
        },
        {
            "title": "Online Safety Act 2023",
            "note": "Relevant where AI is a material part of an online service: illegal harms, children's safety duties.",
            "url": "https://www.legislation.gov.uk/ukpga/2023/50/contents",
        },
    ],
}
