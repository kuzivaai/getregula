# regula-ignore
"""Colorado (US) — Colorado AI Act coverage page.

Data file consumed by scripts/build_regulations.py to generate
colorado-ai-regulation.html. Every claim is traceable to primary or
primary-adjacent sources cited in the `sources` list at the bottom.

Key verified facts (2026-04-08):
- Senate Bill 24-205 ("Colorado Artificial Intelligence Act") was signed in 2024.
- Senate Bill 25B-004 ("Increase Transparency for Algorithmic Systems Act") was
  signed by Governor Polis on 28 August 2025, delaying the effective date from
  1 February 2026 to 30 June 2026. Substance of the 2024 Act was not altered.
- Developers: reasonable-care duty to prevent algorithmic discrimination,
  technical documentation, public statements, regulator + deployer notices.
- Deployers: risk management policy, initial + annual impact assessments,
  pre-decision and adverse-decision consumer notices, website disclosures.
- Attorney General enforcement; rebuttable presumptions and affirmative
  defences take effect 30 June 2026.
"""

REGION = {
    "slug": "colorado-ai-regulation",
    "flag": "🇺🇸",
    "nav_label": "Colorado",
    "lang": "en-US",
    "og_locale": "en_US",
    "hreflang_self": "en-us",
    "geo_region": "US-CO",
    "geo_placename": "Colorado",

    "status_cls": "live",
    "status_text": "Effective 30 June 2026 · statute live",

    "title_tag": "Colorado AI Act Tracker — SB 24-205 + SB 25B-004, 30 June 2026 | Regula",
    "title_html": 'Colorado — <span class="hl">Colorado AI Act</span> tracker',
    "meta_description": (
        "Live tracker of the Colorado Artificial Intelligence Act (SB 24-205) as "
        "amended by SB 25B-004. Effective 30 June 2026. What developers and "
        "deployers of high-risk AI systems must do, what 'algorithmic "
        "discrimination' means under the statute, and what Regula can tell you "
        "about your code today."
    ),
    "meta_keywords": (
        "Colorado AI Act, SB 24-205, SB 25B-004, algorithmic discrimination, "
        "high-risk artificial intelligence, consequential decision, Colorado AG, "
        "AI impact assessment, reasonable care AI"
    ),
    "og_title": "Colorado AI Act Tracker — Regula",
    "og_description": (
        "SB 24-205 as amended by SB 25B-004. Effective 30 June 2026. "
        "Developer and deployer obligations for high-risk AI systems. "
        "Regula's live coverage and framework crosswalk."
    ),
    "twitter_title": "Colorado AI Act Tracker — Regula",
    "twitter_description": (
        "SB 24-205 + SB 25B-004. Effective 30 June 2026. Regula's live coverage."
    ),

    "last_updated": "2026-04-08",
    "published_time": "2026-04-08T00:00:00+00:00",
    "modified_time": "2026-04-08T00:00:00+00:00",

    "lede": (
        "Colorado was the first US state to pass a comprehensive, horizontal "
        "AI statute. Senate Bill 24-205 — the Colorado Artificial Intelligence "
        "Act — imposes duties on both developers and deployers of <em>high-risk "
        "artificial intelligence systems</em> used to make <em>consequential "
        "decisions</em>. After a special legislative session failed to reach a "
        "broader compromise, Governor Polis signed SB 25B-004 on 28 August "
        "2025, pushing the effective date from 1 February 2026 to <strong>30 "
        "June 2026</strong>. The substance of the 2024 Act was not otherwise "
        "amended. This page tracks what the statute actually requires, what "
        "'reasonable care' looks like in practice, and what Regula can tell "
        "you about your codebase today."
    ),

    "tracker_rows": [
        {
            "label": "Statute",
            "value": "SB 24-205 (Colorado Artificial Intelligence Act), as amended by SB 25B-004",
            "state": "verified",
        },
        {
            "label": "Effective date",
            "value": "30 June 2026 (delayed from 1 February 2026 by SB 25B-004)",
            "state": "verified",
        },
        {
            "label": "Scope",
            "value": "High-risk AI systems used to make consequential decisions affecting Colorado consumers",
            "state": "verified",
        },
        {
            "label": "Developer duties",
            "value": "Reasonable care · technical documentation · public statement · notices to AG and deployers",
            "state": "verified",
        },
        {
            "label": "Deployer duties",
            "value": "Risk management policy · initial + annual impact assessments · consumer notices · website disclosure",
            "state": "verified",
        },
        {
            "label": "Enforcement",
            "value": "Colorado Attorney General — exclusive civil enforcement, no private right of action",
            "state": "verified",
        },
        {
            "label": "Rebuttable presumption / affirmative defence",
            "value": "Available to parties demonstrating compliance with a recognised AI risk management framework",
            "state": "verified",
        },
        {
            "label": "Implementing regulations",
            "value": "Colorado AG rulemaking in progress — no final rules published as of 2026-04-08",
            "state": "pending",
        },
    ],

    "sections_html": [
        {
            "id": "what-the-statute-does",
            "heading": "What the Colorado AI Act actually does",
            "body": """
<p>The Colorado AI Act is the first US state statute to impose horizontal, sector-agnostic duties on developers and deployers of AI systems used in consequential decisions. It borrows structure from the EU AI Act but is narrower in two important ways: it applies only to <em>high-risk</em> systems (defined by consequential-decision use, not by Annex III category), and it enforces only through the Colorado Attorney General with no private right of action.</p>
<p>The statute's core concepts:</p>
<ul>
    <li><strong>High-risk artificial intelligence system</strong> — an AI system that, when deployed, makes or is a substantial factor in making a consequential decision. Narrow carve-outs exist for anti-fraud, cybersecurity, and certain generative AI uses.</li>
    <li><strong>Consequential decision</strong> — a decision that has a material legal or similarly significant effect on access to, or the cost or terms of, one of the listed domains: education enrollment or opportunity, employment or employment opportunity, a financial or lending service, an essential government service, healthcare services, housing, insurance, or a legal service.</li>
    <li><strong>Algorithmic discrimination</strong> — unlawful differential treatment or disparate impact on a protected class basis, as informed by existing federal and state civil rights law.</li>
    <li><strong>Developer</strong> — a person doing business in Colorado that develops or intentionally and substantially modifies a high-risk AI system.</li>
    <li><strong>Deployer</strong> — a person doing business in Colorado that uses a high-risk AI system to make a consequential decision.</li>
</ul>
<p>The Act's design choice is important: <em>consequential-decision use</em>, not technical category, triggers coverage. A model trained for credit underwriting is only covered when actually deployed to make lending decisions for Colorado consumers. A general-purpose model is not itself in scope unless and until a deployer puts it to a consequential-decision use.</p>
""",
        },
        {
            "id": "developer-duties",
            "heading": "Developer duties under SB 24-205",
            "body": """
<p>A developer of a high-risk AI system doing business in Colorado must, on and after 30 June 2026:</p>
<ol>
    <li><strong>Use reasonable care</strong> to protect consumers from any known or reasonably foreseeable risks of algorithmic discrimination arising from the intended and contracted uses of the system.</li>
    <li><strong>Provide a statement disclosing</strong> the types of high-risk AI systems the developer has developed or substantially modified, and how the developer manages known or reasonably foreseeable risks of algorithmic discrimination.</li>
    <li><strong>Make technical documentation available</strong> to deployers — including a general description of the system, its intended uses and benefits, reasonably foreseeable uses, and harmful or inappropriate uses; the type of data used to train the system and the limitations of the data; the purpose of the system, intended outputs, and how the outputs should be interpreted and used; measures taken to mitigate risks of algorithmic discrimination; and how the system should be used, not be used, and monitored when used to make a consequential decision.</li>
    <li><strong>Notify the Colorado Attorney General and known deployers</strong> within 90 days of discovering that the developer's system has caused, or is reasonably likely to have caused, algorithmic discrimination.</li>
    <li><strong>Publish a public statement</strong> summarising the types of high-risk systems the developer has developed or substantially modified that are currently available to deployers.</li>
</ol>
<p>Reasonable-care compliance is evidenced by following a recognised AI risk management framework (the statute explicitly references the NIST AI RMF and ISO/IEC 42001 as examples). Developers who document their adherence to such a framework qualify for a <strong>rebuttable presumption</strong> of reasonable care.</p>
""",
        },
        {
            "id": "deployer-duties",
            "heading": "Deployer duties under SB 24-205",
            "body": """
<p>A deployer of a high-risk AI system doing business in Colorado must, on and after 30 June 2026:</p>
<ol>
    <li><strong>Implement a risk management policy and program</strong> to govern the deployer's use of the high-risk system. The policy must be reasonable considering the deployer's size and complexity and the nature of the system's use. Adherence to a recognised risk management framework (NIST AI RMF, ISO/IEC 42001) is again evidence of reasonableness.</li>
    <li><strong>Complete an impact assessment</strong> before deploying the system, and annually thereafter, and within 90 days of any intentional and substantial modification. The assessment must cover the purpose and intended use, the categories of data used, the benefits, the known or reasonably foreseeable risks of algorithmic discrimination, the steps taken to mitigate those risks, and the post-deployment monitoring and safeguards.</li>
    <li><strong>Notify consumers</strong> before a high-risk AI system is used to make a consequential decision about them, and provide a statement of the purpose of the system, the nature of the decision, and the deployer's contact information.</li>
    <li><strong>Provide an adverse-decision notice</strong> where a consequential decision is adverse to the consumer, including the principal reasons for the decision, an opportunity to correct incorrect personal data, and an opportunity to appeal for human review.</li>
    <li><strong>Publish a website disclosure</strong> summarising the types of high-risk AI systems the deployer currently deploys, how the deployer manages known or reasonably foreseeable risks of algorithmic discrimination, and the nature and source of information collected and used.</li>
    <li><strong>Notify the Colorado Attorney General</strong> within 90 days of discovering algorithmic discrimination caused by the deployed system.</li>
</ol>
<p>Small deployers (those with fewer than 50 employees who do not use their own data to train the system) have a narrower set of obligations.</p>
""",
        },
        {
            "id": "what-to-do-today",
            "heading": "What Colorado developers and deployers should do today",
            "body": """
<p>The 30 June 2026 effective date gives organisations a short runway. The practical sequence:</p>
<ol>
    <li><strong>Map your Colorado exposure.</strong> If your system is used — or is contracted to be used — to make consequential decisions affecting Colorado consumers, you are in scope regardless of where you are headquartered. Enumerate each such deployment path.</li>
    <li><strong>Adopt a recognised AI risk management framework.</strong> NIST AI RMF 1.0 and ISO/IEC 42001:2023 are explicitly referenced by the statute. Pick one and document your implementation. This is how you earn the rebuttable presumption of reasonable care.</li>
    <li><strong>Produce developer technical documentation</strong> for every high-risk system. Regula's <code>regula docs</code> and <code>regula conform</code> commands generate Annex IV-style scaffolds that cover most of the Colorado disclosure categories — training data description, intended use, foreseeable misuse, mitigation measures, monitoring. The EU template goes further than Colorado requires, which is fine.</li>
    <li><strong>Run the Article 14 oversight trace.</strong> Colorado's consumer adverse-decision notice requires an opportunity to appeal for human review. Regula's <code>regula oversight</code> command traces AI model outputs through call chains cross-file and flags where a human review gate is absent. This is the exact control Colorado expects.</li>
    <li><strong>Stand up a deployer impact assessment process.</strong> The initial assessment must be complete before deployment on 30 June 2026. Annual thereafter. Regula's <code>regula gap</code> and <code>regula evidence-pack</code> commands provide inputs that map onto the statute's assessment categories.</li>
    <li><strong>Monitor the Colorado Attorney General's rulemaking.</strong> The AG is empowered to issue implementing regulations. As of 2026-04-08 no final rules have been published. This page will update when they are.</li>
</ol>
""",
        },
        {
            "id": "where-regula-fits",
            "heading": "Where Regula fits for Colorado teams",
            "body": """
<p>Regula was built primarily against the EU AI Act, but the Colorado AI Act's developer and deployer categories map cleanly onto work Regula already does. Practical starting commands:</p>
<pre><code>pip install regula-ai

regula discover .              # AI systems present in the project
regula check .                 # Risk indicators across all frameworks
regula gap --project .         # Gap assessment (reuses Art 9-15 structure)
regula oversight .              # Cross-file human-review gate detection
regula docs .                  # Technical documentation scaffold
regula conform .               # Evidence pack — maps to deployer impact assessment
regula sbom --ai-bom .         # AI Bill of Materials (CycloneDX 1.6)
</code></pre>
<p>The NIST AI RMF mapping that gets you the Colorado rebuttable presumption is already shipped in Regula's <code>references/framework_crosswalk.yaml</code>. A single <code>regula check</code> run reports findings against the EU AI Act, NIST AI RMF, ISO/IEC 42001, OWASP LLM Top 10, and the other frameworks Regula supports.</p>
<p>What Regula does <em>not</em> do for Colorado: issue your consumer notices, track your deployer impact assessment history, or act as a compliance certificate. The statute is enforced by the Colorado AG against real organisations — Regula helps you produce the evidence, not the legal conclusion.</p>
""",
        },
        {
            "id": "what-we-are-tracking",
            "heading": "What we are tracking for the Colorado page",
            "body": """
<p>This page will be updated as the Colorado landscape moves. Specifically we are watching for:</p>
<ol>
    <li><strong>Colorado Attorney General implementing rules</strong> under SB 24-205. The AG is empowered to issue regulations defining documentation formats, notice content, and risk management framework criteria. No final rules as of 2026-04-08.</li>
    <li><strong>Further legislative amendments.</strong> SB 25B-004 was intended to be one of multiple corrective bills. Further amendment is expected before the 30 June 2026 effective date.</li>
    <li><strong>Enforcement signals</strong> — the first AG complaint, consent decree, or public enforcement action under the Act.</li>
    <li><strong>Other US state statutes</strong> following Colorado's lead. Texas (TRAIGA), California (SB 53 successors), and Connecticut have active AI legislation. We will add state pages where statutes are enacted.</li>
</ol>
<p>If you spot something we have missed, please <a href="https://github.com/kuzivaai/getregula/issues">open an issue</a>.</p>
""",
        },
    ],

    "faq": [
        {
            "q": "When does the Colorado AI Act take effect?",
            "a": (
                "30 June 2026. The original effective date of 1 February 2026 was "
                "delayed by SB 25B-004, signed by Governor Polis on 28 August 2025. "
                "The substance of the 2024 Act was not otherwise amended."
            ),
        },
        {
            "q": "Who does the Colorado AI Act apply to?",
            "a": (
                "Developers and deployers of high-risk AI systems doing business in "
                "Colorado. 'High-risk' is defined by use — systems that make or are a "
                "substantial factor in making a consequential decision affecting "
                "Colorado consumers in education, employment, finance, essential "
                "government services, healthcare, housing, insurance, or legal services."
            ),
        },
        {
            "q": "What is a 'consequential decision' under the statute?",
            "a": (
                "A decision that has a material legal or similarly significant effect "
                "on access to, or the cost or terms of, education enrollment or "
                "opportunity, employment or employment opportunity, a financial or "
                "lending service, an essential government service, healthcare services, "
                "housing, insurance, or a legal service. Narrow carve-outs exist for "
                "anti-fraud, cybersecurity, and certain generative AI uses."
            ),
        },
        {
            "q": "Is there a private right of action under the Colorado AI Act?",
            "a": (
                "No. Enforcement is exclusive to the Colorado Attorney General. "
                "Individuals harmed by algorithmic discrimination retain their rights "
                "under existing federal and state civil rights statutes, but they "
                "cannot sue under SB 24-205 directly."
            ),
        },
        {
            "q": "Does the Colorado AI Act recognise a compliance safe harbour?",
            "a": (
                "Yes — a rebuttable presumption of reasonable care is available to "
                "parties who document adherence to a recognised AI risk management "
                "framework. The statute explicitly references the NIST AI RMF and "
                "ISO/IEC 42001 as examples. This is not an absolute defence; the "
                "Attorney General can rebut it with evidence of actual algorithmic "
                "discrimination."
            ),
        },
        {
            "q": "Does Regula cover Colorado AI Act obligations?",
            "a": (
                "Partially. Regula's NIST AI RMF mapping, Article 14 cross-file "
                "oversight trace, technical documentation generator, and gap "
                "assessment all produce evidence that maps onto Colorado's developer "
                "and deployer duties. Regula does not generate consumer notices, "
                "track impact assessment history over time, or replace legal advice. "
                "See the 'Where Regula fits' section above for practical commands."
            ),
        },
    ],

    "sources": [
        {
            "title": "SB 24-205 — Consumer Protections for Artificial Intelligence (Colorado General Assembly)",
            "note": "The enacted text of the Colorado Artificial Intelligence Act.",
            "url": "https://leg.colorado.gov/bills/sb24-205",
        },
        {
            "title": "SB 25B-004 — Increase Transparency for Algorithmic Systems Act",
            "note": "The 2025 special-session amendment that delayed the effective date to 30 June 2026.",
            "url": "https://leg.colorado.gov/bills/sb25b-004",
        },
        {
            "title": "Colorado Attorney General — Office of the Attorney General",
            "note": "Enforcement authority under the Colorado AI Act. Rulemaking portal and guidance will appear here.",
            "url": "https://coag.gov/",
        },
        {
            "title": "Enforcement of Colorado AI Act Delayed Until June 2026 — Hunton Andrews Kurth",
            "note": "Primary-adjacent legal summary of SB 25B-004 and the substantive scope of the 2024 Act.",
            "url": "https://www.hunton.com/privacy-and-cybersecurity-law-blog/enforcement-of-colorado-ai-act-delayed-until-june-2026",
        },
        {
            "title": "NIST AI Risk Management Framework 1.0",
            "note": "Explicitly referenced by SB 24-205 as a recognised framework for the reasonable-care rebuttable presumption.",
            "url": "https://www.nist.gov/itl/ai-risk-management-framework",
        },
        {
            "title": "ISO/IEC 42001:2023 — Artificial intelligence management system",
            "note": "Also explicitly referenced by SB 24-205 as a recognised framework.",
            "url": "https://www.iso.org/standard/81230.html",
        },
    ],
}
