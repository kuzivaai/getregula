# I built an EU AI Act scanner. Here is what it cannot see.

**Status:** DRAFT, 14 August 2026. Not published. Platform-agnostic (dev.to, Hashnode, LinkedIn article). Written under the Regula claim freeze of 1 August 2026: no performance figures, no test counts, no pattern counts, no version numbers. Limitation framing only.

**Fraction removed, 15 August 2026.** The draft said static analysis "reaches
roughly a third of the Act" in three places and derived "the other two thirds"
from it. Nothing in the repository grounds that fraction and its denominator
was never defined: articles, obligations, recitals and words all give different
answers, and `references/article_obligations.yaml` lists 7 articles, which is
no basis for a fraction of a 113-article regulation. It is now a qualitative
claim, which is what the article actually demonstrates. Constructing a
defensible-looking number to keep the sentence would have been advocacy for a
figure that was written first and justified afterwards.

**Suggested meta description:** A compliance scanner reads code, not intent. A builder's account of what static analysis can see of the EU AI Act, and what it structurally cannot.

---

Over the past year I built [Regula](https://getregula.com), an open-source scanner for the EU AI Act. You point it at a source-code folder, it flags patterns that may need governance review, and it links each finding to the provisions that might be relevant. The code is public on [GitHub](https://github.com/kuzivaai/getregula), the core scan runs locally, and it does not upload the contents of the files it scans, which matters if the codebase you are scanning is the thing you are worried about.

Building it taught me more about the regulation than reading it did, and the most useful thing it taught me is a limitation. Static analysis reaches a narrow band of the Act, and the interesting part is what the rest of it is made of.

## What a scanner can genuinely see

Code is honest about some things. A scanner can tell you that a codebase calls a generative model, because the import and the API call are sitting right there. It can list the AI libraries a project depends on, check whether there is any logging around the calls that matter, and notice whether output from a model flows into something that looks like a decision. Absences show up too: no provenance marking on generated content, no review step between a model's output and the point where it takes effect.

That is real information, and for a team that has never inventoried its AI usage it can be surprising information. A codebase of any age tends to accumulate model calls nobody remembers adding, and a scanner turns the question of where they all are from an archaeology exercise into a command.

## What it structurally cannot see

The EU AI Act classifies risk by intended purpose and deployment context. The same CV-parsing code can fall into the high-risk category when it is used to screen job applicants, since employment is an Annex III use case, and be unremarkable when it deduplicates a CRM. Nothing in the source distinguishes those two deployments. That fact alone puts legal classification permanently out of reach of static analysis, which is why Regula reports candidate risk categories for a human to review rather than a verdict.

Article 50, the transparency article that began to apply on 2 August 2026, makes the gap concrete. It requires, among other things, that a person interacting with an AI system can tell they are dealing with a machine, that deepfakes are clearly disclosed, and that AI-generated text published on matters of public interest is labelled unless a person has genuinely reviewed it and someone holds editorial responsibility.

Each of those duties lives somewhere a code scanner cannot follow. Whether an interface discloses itself is a property of a rendered view and a design decision, not of the backend the scanner reads. Whether a disclosure is clear and visible is a judgement about a person's experience of a screen. Whether text went through genuine editorial review happens in someone's head and, at best, leaves a trace in a workflow tool the scanner has never heard of. A codebase can be entirely consistent with compliance and entirely consistent with violation at the same time.

The bulk of the Act's high-risk obligations, which the Digital Omnibus (Regulation (EU) 2026/1744, in the Official Journal on 24 July 2026) moved to 2 December 2027 for Annex III and 2 August 2028 for Annex I, are further away still. A risk management system, a quality management system, post-market monitoring: these are organisational processes with documents and named owners. There is no line of code whose presence demonstrates that any of them exist.

## The design consequence

Once you accept that, the honest design follows. A scan with no findings must not be presented as evidence that a system is compliant or low risk, so Regula does not present it that way. Where the answer depends on facts code cannot show, the tool asks a person, records the declared context, and says so in the output. Insufficient information is reported as insufficient information rather than converted into a score, because a made-up number is worse than no number.

I would apply the same test to any tool in this category, including the one I wrote. If a compliance scanner implies it can tell you whether you comply with the EU AI Act, it is promising something it cannot know. The useful question for a vendor is what the tool admits it cannot detect, and whether that admission appears in the output or only in the small print.

## What a scanner is actually for

None of this makes the tooling pointless, but it does narrow what the tooling is for. A scanner gives you an inventory of where AI actually lives in your systems, a set of findings a human can triage, and a review trail showing what was checked and when. That is the starting point of a compliance process, and having it automated and repeatable is worth a lot. Everything that comes after, the purpose analysis, the management processes, the legal judgement, is work a pattern matcher cannot do for you.

If you want to see what the honest version of the boundary looks like, the [Regula repository](https://github.com/kuzivaai/getregula) documents its limitations alongside its capabilities, and the scanner is a `pipx install regula-ai` away. Run it on something you own. Whatever it finds, the more important lesson is in what it declines to claim.

---

*Kuziva Muzondo is a programme manager who explores AI governance outside his day job. He built Regula and StreetSignal, and writes [The Implementation Layer](https://theimplementationlayer.substack.com), a fortnightly newsletter on the gap between AI governance theory and what organisations actually do.*
