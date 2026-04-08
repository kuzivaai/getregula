# regula-ignore
"""South Korea — AI Basic Act coverage page.

Data file consumed by scripts/build_regulations.py to generate
south-korea-ai-regulation.html. Every claim is traceable to primary or
primary-adjacent sources cited in the `sources` list at the bottom.

Key verified facts (2026-04-08):
- The "Act on the Development of Artificial Intelligence and Establishment
  of Trust" (commonly the AI Basic Act) took effect on 22 January 2026.
- The enforcement decree took effect the same day; detailed subordinate
  regulations from MSIT remain in public consultation.
- MSIT has clarified that AI systems trained with a cumulative compute of
  at least 10^26 FLOPs are designated "high-performance AI" with associated
  safety obligations. Note this is a different threshold from the EU AI Act's
  10^25 FLOP systemic-risk threshold under Article 51.
- The Act introduces "high-impact AI" (contextual, use-based) and
  "high-performance AI" (compute-based) as two overlapping risk categories.
- Generative AI providers have transparency and watermarking obligations.
"""

REGION = {
    "slug": "south-korea-ai-regulation",
    "flag": "🇰🇷",
    "nav_label": "South Korea",
    "lang": "en-US",
    "og_locale": "en_US",
    "hreflang_self": "en",
    "geo_region": "KR",
    "geo_placename": "South Korea",

    "status_cls": "live",
    "status_text": "In force \u00b7 effective 22 January 2026",

    "title_tag": "South Korea AI Basic Act Tracker \u2014 in force 22 Jan 2026 | Regula",
    "title_html": 'South Korea \u2014 <span class="hl">AI Basic Act</span> tracker',
    "meta_description": (
        "Live tracker of South Korea's Act on the Development of Artificial "
        "Intelligence and Establishment of Trust (AI Basic Act). In force since "
        "22 January 2026. High-impact AI, high-performance AI (10^26 FLOPs), "
        "generative AI watermarking, and what Regula can tell you about your "
        "codebase today."
    ),
    "meta_keywords": (
        "South Korea AI Basic Act, AI Framework Act Korea, high-impact AI, "
        "high-performance AI, MSIT AI, Korean AI regulation, generative AI "
        "watermarking Korea, 10^26 FLOPs, Article 31 AI Korea"
    ),
    "og_title": "South Korea AI Basic Act Tracker \u2014 Regula",
    "og_description": (
        "In force since 22 January 2026. High-impact AI, high-performance AI "
        "(10^26 FLOPs), generative AI transparency. Regula's live coverage."
    ),
    "twitter_title": "South Korea AI Basic Act Tracker \u2014 Regula",
    "twitter_description": (
        "Korea AI Basic Act \u2014 in force 22 Jan 2026. Regula's live coverage."
    ),

    "last_updated": "2026-04-08",
    "published_time": "2026-04-08T00:00:00+00:00",
    "modified_time": "2026-04-08T00:00:00+00:00",

    "lede": (
        "South Korea is the second major jurisdiction after the European Union "
        "to enact a horizontal AI statute. The <em>Act on the Development of "
        "Artificial Intelligence and Establishment of Trust</em> \u2014 commonly the "
        "AI Basic Act \u2014 took effect on <strong>22 January 2026</strong>, along "
        "with its Enforcement Decree. The Act is a framework statute: it "
        "defines categories (high-impact AI, high-performance AI, generative "
        "AI), imposes documentation and transparency obligations, and "
        "delegates the technical detail to subordinate regulations from the "
        "Ministry of Science and ICT (MSIT). Those subordinate regulations "
        "are the single most important thing to monitor in 2026 \u2014 they will "
        "define thresholds, watermarking specifications, and audit "
        "expectations. This page tracks what is in force today."
    ),

    "tracker_rows": [
        {
            "label": "Statute",
            "value": "Act on the Development of Artificial Intelligence and Establishment of Trust (AI Basic Act)",
            "state": "verified",
        },
        {
            "label": "Effective date",
            "value": "22 January 2026 (with Enforcement Decree)",
            "state": "verified",
        },
        {
            "label": "Lead ministry",
            "value": "Ministry of Science and ICT (MSIT)",
            "state": "verified",
        },
        {
            "label": "High-performance AI threshold",
            "value": "\u2265 10\u00b2\u2076 cumulative training FLOPs (MSIT clarification)",
            "state": "verified",
        },
        {
            "label": "High-impact AI",
            "value": "Use-based category covering healthcare, energy, public-sector use, identification, hiring, creditworthiness, and other sensitive domains",
            "state": "verified",
        },
        {
            "label": "Generative AI transparency",
            "value": "Disclosure to users \u00b7 watermarking / labelling of AI-generated content",
            "state": "verified",
        },
        {
            "label": "Subordinate regulations",
            "value": "MSIT Enforcement Decree in force \u00b7 detailed thresholds and watermarking spec in public consultation",
            "state": "pending",
        },
        {
            "label": "Extraterritorial reach",
            "value": "Applies to foreign providers whose AI systems affect users in the Republic of Korea",
            "state": "verified",
        },
    ],

    "sections_html": [
        {
            "id": "what-the-statute-does",
            "heading": "What the AI Basic Act actually does",
            "body": """
<p>The AI Basic Act is a framework statute: it establishes definitions, categories, and governance structures, but delegates the technical compliance detail to the MSIT Enforcement Decree and subordinate regulations. Its core design resembles the EU AI Act in structure but is less prescriptive on conformity assessment.</p>
<p>The statute's core concepts:</p>
<ul>
    <li><strong>AI system</strong> \u2014 a broad, EU-aligned definition covering machine-learning and logic-based systems that infer from inputs to generate outputs such as predictions, recommendations, or decisions.</li>
    <li><strong>High-impact AI</strong> \u2014 a use-based risk category. AI systems deployed in healthcare, energy, public-sector contexts, identification, hiring, creditworthiness assessment, and other sensitive domains fall into this tier. Obligations include risk management, human oversight, and impact assessment.</li>
    <li><strong>High-performance AI</strong> \u2014 a compute-based category. MSIT has clarified that systems trained with a cumulative compute of at least <strong>10\u00b2\u2076 FLOPs</strong> are designated high-performance AI with associated safety obligations. This threshold is notably different from the EU AI Act's Article 51 systemic-risk threshold of 10\u00b2\u2075 FLOPs \u2014 a model can be a systemic-risk GPAI under the EU regime without being high-performance AI under the Korean regime, or vice versa, depending on the training run.</li>
    <li><strong>Generative AI</strong> \u2014 providers must clearly disclose to users that they are interacting with AI, and must apply watermarking or labelling to AI-generated content. The specific watermarking standard is delegated to MSIT subordinate regulation.</li>
    <li><strong>Extraterritoriality</strong> \u2014 the Act explicitly applies to foreign providers whose AI systems affect users in the Republic of Korea, similar in architecture to the EU AI Act's Article 2.</li>
</ul>
<p>Enforcement is administered by MSIT. The statute includes investigative powers, corrective orders, and administrative fines, with penalty levels to be specified in subordinate regulation. As of 2026-04-08, no enforcement action has been reported publicly.</p>
""",
        },
        {
            "id": "obligations",
            "heading": "Obligations in force on 22 January 2026",
            "body": """
<p>The statute creates tiered obligations based on the category of the AI system. The summary below is based on the enacted text and the Enforcement Decree; details may shift as subordinate regulations are finalised.</p>
<h3>All AI system providers</h3>
<ul>
    <li>Register as an AI provider where required by MSIT.</li>
    <li>Maintain a designated domestic representative for foreign providers serving Korean users.</li>
    <li>Cooperate with MSIT requests for information during investigations.</li>
</ul>
<h3>High-impact AI providers</h3>
<ul>
    <li>Establish and operate a risk management system across the AI lifecycle.</li>
    <li>Maintain documentation sufficient to demonstrate how the system works, how it is trained, and how it is monitored.</li>
    <li>Ensure meaningful human oversight of decisions that materially affect individuals.</li>
    <li>Conduct impact assessments before deployment in high-impact domains, and on material change.</li>
    <li>Provide users and affected parties with clear information about the system's purpose, capabilities, and limitations.</li>
</ul>
<h3>High-performance AI providers (\u2265 10\u00b2\u2076 FLOPs)</h3>
<ul>
    <li>Additional safety and security obligations, to be specified by MSIT subordinate regulation.</li>
    <li>Documentation of the training process, data sources, and evaluation results.</li>
    <li>Incident reporting to MSIT for identified safety failures.</li>
</ul>
<h3>Generative AI providers</h3>
<ul>
    <li>Disclose clearly to users that they are interacting with an AI system.</li>
    <li>Apply watermarking or labelling to AI-generated content such that downstream users and platforms can identify it as AI-generated. The technical watermarking standard is delegated to MSIT subordinate regulation.</li>
</ul>
""",
        },
        {
            "id": "what-to-do-today",
            "heading": "What Korean operators and foreign providers should do today",
            "body": """
<p>The statute is already in force. Subordinate regulations are still settling. The practical sequence:</p>
<ol>
    <li><strong>Determine whether you are a high-impact AI provider</strong> by reviewing your deployment domains against the statute's list: healthcare, energy, public-sector use, identification, hiring, creditworthiness assessment, and related sensitive sectors. Extraterritorial reach means foreign providers serving Korean users are in scope.</li>
    <li><strong>Estimate your training compute</strong> against the 10\u00b2\u2076 FLOP threshold. Most production models today sit well below this. If you are building a frontier or near-frontier model, Regula's <code>regula inventory</code> command can annotate detected model references with their tier; add your own internal training-run metadata to confirm.</li>
    <li><strong>If you ship generative AI, audit your transparency path.</strong> Clear user disclosure that the output is AI-generated is already required. Watermarking is required; the spec is pending. Build a watermarking hook now so the only outstanding work when MSIT publishes the spec is the payload format.</li>
    <li><strong>Document your risk management and human oversight.</strong> Regula's <code>regula gap</code> and <code>regula oversight</code> commands map cleanly onto the high-impact AI obligations. The outputs are not Korean-statute-specific, but the evidence is the same.</li>
    <li><strong>Appoint a domestic representative</strong> if you are a foreign provider without a Korean legal entity. This is a common pattern in Korean tech regulation and is likely to be explicitly required under MSIT subordinate rules.</li>
    <li><strong>Watch MSIT's rulemaking.</strong> The Enforcement Decree is in force but several subordinate regulations are still in public consultation. These will define the watermarking specification, the high-impact domain list in detail, and the exact investigative procedures.</li>
</ol>
""",
        },
        {
            "id": "korea-vs-eu",
            "heading": "How the AI Basic Act differs from the EU AI Act",
            "body": """
<p>A useful orientation for teams already working on EU AI Act compliance. The two regimes are structurally similar but differ in important details:</p>
<ul>
    <li><strong>Risk taxonomy.</strong> The EU AI Act uses a four-tier taxonomy plus a separate GPAI regime. Korea uses two overlapping categories (high-impact AI + high-performance AI) plus a generative AI transparency layer. A system can be high-impact under both regimes, or high-impact under one but not the other.</li>
    <li><strong>Compute threshold.</strong> EU Article 51 uses 10\u00b2\u2075 FLOPs as the systemic-risk GPAI threshold. Korea uses 10\u00b2\u2076 FLOPs as the high-performance AI threshold. A model trained between 10\u00b2\u2075 and 10\u00b2\u2076 FLOPs is a systemic-risk GPAI in the EU but <em>not</em> high-performance AI under the Korean regime.</li>
    <li><strong>Hard prohibitions.</strong> The EU AI Act has a hard prohibition list under Article 5. The Korean AI Basic Act does not have an equivalent hard prohibition list \u2014 sensitive use cases are channelled into the high-impact AI obligations instead.</li>
    <li><strong>Conformity assessment.</strong> The EU AI Act requires third-party conformity assessment for some Annex I high-risk systems and self-assessment for Annex III. The Korean Act currently relies on provider documentation and MSIT oversight rather than third-party assessment bodies.</li>
    <li><strong>Watermarking.</strong> The EU AI Act's Article 50 transparency rules on AI-generated content apply from 2 August 2026. Korea's watermarking obligation is already in force as of 22 January 2026 \u2014 six months earlier \u2014 though the technical specification is still pending.</li>
    <li><strong>Enforcement.</strong> EU enforcement is decentralised across national authorities plus the AI Office. Korean enforcement is centralised under MSIT.</li>
</ul>
<p>If you are already on a path to EU AI Act readiness, a large share of the evidence and documentation will translate directly \u2014 but the thresholds, categories, and watermarking specifications need to be checked separately.</p>
""",
        },
        {
            "id": "where-regula-fits",
            "heading": "Where Regula fits for Korean operators and foreign providers",
            "body": """
<p>Regula was built primarily against the EU AI Act, but much of its output is also useful for Korean AI Basic Act compliance. Practical starting commands:</p>
<pre><code>pip install regula-ai

regula discover .              # AI systems present in the project
regula check .                 # Risk indicators across all frameworks
regula inventory .             # Model references with GPAI tier (use alongside the Korean 10^26 threshold)
regula gap --project .         # Gap assessment \u2014 maps onto high-impact AI obligations
regula oversight .             # Cross-file human-oversight detection
regula docs .                  # Technical documentation scaffold
regula sbom --ai-bom .         # AI Bill of Materials (CycloneDX 1.6)
</code></pre>
<p>What Regula does <em>not</em> yet do for Korea specifically: generate watermarking hook code, validate a Korean-standard watermark payload, or produce a Korean-language disclosure template. The first two will land once MSIT publishes the watermarking specification. The third is a straightforward localisation task \u2014 <a href="https://github.com/kuzivaai/getregula/issues">open an issue</a> if you need it.</p>
""",
        },
        {
            "id": "what-we-are-tracking",
            "heading": "What we are tracking for the South Korea page",
            "body": """
<p>This page will be updated as the Korean landscape moves. Specifically we are watching for:</p>
<ol>
    <li><strong>MSIT subordinate regulations</strong> specifying the high-performance AI safety obligations, the generative AI watermarking standard, and the high-impact AI documentation format.</li>
    <li><strong>First enforcement actions</strong> \u2014 the first MSIT investigation, corrective order, or administrative fine under the Act.</li>
    <li><strong>Interaction with existing Korean statutes</strong> \u2014 PIPA (Personal Information Protection Act) enforcement on AI training data, the Information and Communications Network Act on generative AI service providers, and sector regulators issuing their own AI guidance.</li>
    <li><strong>Bilateral alignment</strong> with EU AI Act harmonised standards \u2014 whether MSIT references CEN-CENELEC JTC 21 work or the final GPAI Code of Practice in its subordinate regulations.</li>
</ol>
<p>If you spot something we have missed, please <a href="https://github.com/kuzivaai/getregula/issues">open an issue</a>.</p>
""",
        },
    ],

    "faq": [
        {
            "q": "When did the South Korean AI Basic Act take effect?",
            "a": (
                "22 January 2026, along with its Enforcement Decree. The statute is "
                "in force; several subordinate regulations from the Ministry of "
                "Science and ICT remain in public consultation."
            ),
        },
        {
            "q": "What is 'high-performance AI' under the Korean regime?",
            "a": (
                "AI systems trained with a cumulative compute of at least 10\u00b2\u2076 "
                "FLOPs, as clarified by MSIT. This threshold is distinct from the "
                "EU AI Act's Article 51 systemic-risk GPAI threshold of 10\u00b2\u2075 FLOPs \u2014 "
                "a model can cross one threshold without crossing the other."
            ),
        },
        {
            "q": "Does the Korean AI Basic Act apply to foreign providers?",
            "a": (
                "Yes. The statute has extraterritorial reach and applies to foreign "
                "providers whose AI systems affect users in the Republic of Korea. "
                "Foreign providers are likely to need a domestic representative "
                "under MSIT subordinate rules."
            ),
        },
        {
            "q": "Do generative AI providers need to watermark output in Korea?",
            "a": (
                "Yes. Generative AI providers must clearly disclose to users that "
                "output is AI-generated and must apply watermarking or labelling. "
                "The specific technical watermarking standard is delegated to MSIT "
                "subordinate regulation and is still being finalised."
            ),
        },
        {
            "q": "How does the Korean AI Basic Act compare to the EU AI Act?",
            "a": (
                "Structurally similar: both are horizontal, risk-based, extraterritorial "
                "statutes with documentation and human-oversight obligations. Key "
                "differences: no equivalent hard prohibition list, a different compute "
                "threshold (10\u00b2\u2076 vs 10\u00b2\u2075 FLOPs), centralised MSIT enforcement "
                "rather than distributed national authorities, and earlier-in-force "
                "generative AI transparency."
            ),
        },
        {
            "q": "Does Regula cover the Korean AI Basic Act?",
            "a": (
                "Partially. Regula's gap assessment, human oversight trace, "
                "technical documentation scaffold, and AI Bill of Materials all "
                "produce evidence that translates to the Korean regime's high-impact "
                "AI obligations. Regula does not yet ship Korean watermarking "
                "payloads or Korean-language disclosure templates; those will land "
                "after MSIT publishes the watermarking specification."
            ),
        },
    ],

    "sources": [
        {
            "title": "South Korea: Comprehensive AI Legal Framework Takes Effect \u2014 Library of Congress Global Legal Monitor",
            "note": "Primary-adjacent official summary of the AI Basic Act and Enforcement Decree taking effect on 22 January 2026.",
            "url": "https://www.loc.gov/item/global-legal-monitor/2026-02-20/south-korea-comprehensive-ai-legal-framework-takes-effect",
        },
        {
            "title": "Framework Act on the Development of Artificial Intelligence \u2014 English translation (CSET, Georgetown)",
            "note": "English translation of the enacted Korean AI Basic Act.",
            "url": "https://cset.georgetown.edu/wp-content/uploads/t0625_south_korea_ai_law_EN.pdf",
        },
        {
            "title": "South Korea's AI Basic Act: Overview and Key Takeaways \u2014 Cooley, 27 January 2026",
            "note": "Primary-adjacent legal summary published the week the statute took effect.",
            "url": "https://www.cooley.com/news/insight/2026/2026-01-27-south-koreas-ai-basic-act-overview-and-key-takeaways",
        },
        {
            "title": "Analyzing South Korea's Framework Act on the Development of AI \u2014 IAPP",
            "note": "Independent analysis from the International Association of Privacy Professionals.",
            "url": "https://iapp.org/news/a/analyzing-south-korea-s-framework-act-on-the-development-of-ai",
        },
        {
            "title": "South Korea Artificial Intelligence (AI) Basic Act \u2014 US Department of Commerce ITA",
            "note": "US trade agency summary for American exporters and service providers.",
            "url": "https://www.trade.gov/market-intelligence/south-korea-artificial-intelligence-ai-basic-act",
        },
        {
            "title": "Ministry of Science and ICT (MSIT)",
            "note": "Lead enforcement ministry. Subordinate AI regulations are published here.",
            "url": "https://www.msit.go.kr/eng/",
        },
    ],
}
