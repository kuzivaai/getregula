# Human Actions Required

Items that require the founder's hands — cannot be automated in a build session.

---

## 1. Bing Webmaster Tools — Sitemap Submission (D7)

**Why:** ChatGPT's web search uses Bing's index. If getregula.com's sitemap is
not submitted to Bing, the site may be absent from ChatGPT search results.

**Steps:**
1. Go to https://www.bing.com/webmasters/
2. Sign in with a Microsoft account
3. Add site: `https://getregula.com`
4. Verify ownership (options: CNAME record, meta tag, or XML file upload)
   - Recommended: XML file — download the verification file, place in `site/`,
     commit and deploy
5. Once verified, go to "Sitemaps" in the left panel
6. Submit: `https://getregula.com/sitemap.xml`
7. Wait for crawl confirmation (usually 24-48 hours)

**Sitemap status (verified 11 June 2026):**
- Well-formed XML, 23 URLs, no errors
- Missing: `pricing.html` (add to sitemap if pricing page should be indexed)
- All lastmod dates are 2026-04-22 to 2026-05-02 — consider updating to
  current date after this session's content changes

**Priority:** Do before Session 2 distribution blitz — Bing indexing takes days.

---

## 2. IAPP Vendor Report Submission (D5, Session 2)

**Why:** The IAPP AI Governance Vendor Report is the primary discovery channel
for compliance buyers. Regula is not listed.

**Steps:**
1. Email acasovan@iapp.org
2. Subject: "AI Governance Vendor Report — Regula submission"
3. Include: tool name, URL (getregula.com), GitHub URL, category
   (Technical Assessments and Evaluations), 2-sentence description,
   key capabilities (risk classification, evidence packs, 12-framework mapping)

**Priority:** Session 2.

---

## 3. Lobste.rs Invite (D8 prep, Session 2)

**Why:** Lobste.rs is invite-only. New users are restricted for 70 days.
Starting the clock now enables a submission in August 2026.

**Steps:**
1. Find an existing Lobste.rs member (HN/Twitter/Mastodon networking)
2. Request an invite
3. After signup, 70-day restriction period begins — no domain submissions,
   no flagging, no meta tags during this period

**Priority:** Start immediately; not blocking for Sessions 2-3.

---

## 4. UK Visa — Revenue Gate Resolution (H1)

**Why:** All revenue-generating work is blocked. See planning/REVENUE_GATE.md.

**Steps:**
1. Consult professional immigration adviser
2. Confirm whether digital product sales (evidence packs) are permitted
   under current visa conditions
3. If yes: lift the revenue gate and proceed with Starter tier (EUR 49)
4. If no: identify the path to resolution (visa change, entity structure, etc.)

**Priority:** Whenever the founder is ready. Not blocking any open-source work.

---

## 5. Sitemap lastmod Dates (Found, Not Fixed)

The sitemap.xml lastmod dates (2026-04-22 to 2026-05-02) are now stale for
pages modified in this session. After pushing this session's commits:
1. Update `site/sitemap.xml` lastmod for modified pages (uae.html, colorado,
   3 blog posts) to current date
2. Or run site_facts.py if it auto-generates the sitemap

Not a build-session task — quick manual edit after deploy.

---

## 6. MCP Registry Submissions (D4) — PREPARED

The `mcp-server.json` manifest is committed to the repo. `<!-- mcp-name: regula -->`
is in README.md. Submissions to each registry require web forms or CLI tools:

### Official MCP Registry (registry.modelcontextprotocol.io)
1. Install the publisher CLI: `npm install -g @modelcontextprotocol/publisher`
2. Run `mcp publish` from the repo root
3. Alternatively, publish via PyPI — the registry auto-discovers packages
   with `mcp-name` in README

### mcp.so
1. Go to https://mcp.so/submit (or open a GitHub issue at the mcp.so repo)
2. Fill in: name=regula, description="EU AI Act static analysis CLI. 389 detection
   patterns, 8 languages, offline, zero dependencies.", transport=stdio,
   GitHub=https://github.com/kuzivaai/getregula, homepage=https://getregula.com

### Smithery.ai
1. Install: `npm install -g smithery`
2. Run: `smithery mcp publish https://github.com/kuzivaai/getregula -n regula`
3. Or submit at https://smithery.ai/submit

### PulseMCP
1. Submit via https://pulsemcp.com/submit
2. Or open a GitHub issue — PulseMCP is hand-reviewed daily

---

## 7. IAPP AI Governance Vendor Report Submission (D5) — PREPARED

**Email draft** (send from founder's address):

**To:** acasovan@iapp.org
**Subject:** AI Governance Vendor Report — Regula submission

Dear Ms Casovan,

I would like to submit Regula for inclusion in the next edition of the
IAPP AI Governance Vendor Report, under the "Technical Assessments and
Evaluations" category.

Regula is an open-source CLI tool that scans codebases for EU AI Act
compliance indicators. It classifies AI systems into the Act's four risk
tiers, maps findings to 12 compliance frameworks (including ISO 42001,
NIST AI RMF, and OWASP LLM Top 10), and generates Annex IV documentation
scaffolds and conformity evidence packs. It runs entirely offline with
zero runtime dependencies — code never leaves the user's machine.

- Website: https://getregula.com
- GitHub: https://github.com/kuzivaai/getregula
- PyPI: https://pypi.org/project/regula-ai/
- Trust pack (reproducible benchmarks): https://github.com/kuzivaai/getregula/blob/main/docs/TRUST.md
- Licence: Apache 2.0

Regula is maintained by The Implementation Layer. I am happy to provide
any additional information needed for the report.

Best regards,
Kuziva Muzondo
The Implementation Layer
support@getregula.com

---

## 8. Show HN Submission (D8) — PREPARED, Founder Decision Required

**Do not launch without reading the engagement protocol below.**

### Title (technical framing, not product announcement)

> Show HN: 389 regex patterns for classifying code against the EU AI Act

### Body text

Regula is an open-source CLI that scans your codebase for EU AI Act
compliance indicators. It classifies your AI system into one of the Act's
four risk tiers (prohibited, high-risk, limited-risk, minimal-risk) and
tells you which articles apply.

Technical approach: 389 tiered regex patterns across Python, JS/TS, Java,
Go, Rust, and C/C++. Python has full AST analysis for cross-file data flow
(Article 14 human oversight). Everything else is regex-based import and
pattern detection — honest about the depth disparity.

Zero runtime dependencies (stdlib-only Python). Fully offline — no API keys,
no data leaves your machine, no account needed.

Benchmark: 83.5% precision on a blind-labelled random corpus of 50 Python
repos (N=115 production-code findings). Zero false positives at the BLOCK/CI
tier. The high-risk tier is weakest at 33% precision on N=6 findings —
domain gating helps but we need more labelled data. Full methodology and
corpus published at benchmarks/labels.json.

What it does not do: legal advice, runtime monitoring, semantic understanding
of code, non-English pattern matching. It finds risk indicators for human
review — it does not determine compliance.

https://github.com/kuzivaai/getregula

### Maker comment (post within 5 minutes of submission)

Built this as a solo project over the past 3 months. The EU AI Act's
high-risk obligations were originally due August 2026 but the Omnibus
agreement on 7 May pushed Annex III to December 2027. The requirements
don't change — just the timeline.

Hardest problem: false positive management. AI libraries like scikit-learn
and LangChain are full of risk-sounding vocabulary ("pipeline", "agent",
"predict") that isn't actually regulatory risk. Our library-corpus precision
is only 15.2% — we publish that number alongside the 83.5% production-code
figure because hiding it would be dishonest.

The pattern database is the moat — 389 regex patterns mapped to specific
EU AI Act articles and 12 compliance frameworks. Each finding includes the
article reference, a confidence score, and a citation to the regex in
risk_patterns.py so you can read it yourself.

Happy to answer questions about the technical approach, the precision trade-
offs, or the regulatory landscape.

### Engagement protocol (binding)

- **Timing:** Founder's decision. Research suggests Monday 00:00 UTC
  (Sunday 7pm ET) for best visibility. Must be available to respond for
  2+ hours after posting.
- **NO coordinated voting.** You may tell people the post exists. You must
  NOT ask for upvotes, coordinate timing of engagement, or arrange reciprocal
  voting. HN detects voting rings and will flag the post and account
  permanently.
- **Respond to every substantive comment** personally and promptly (within
  15 minutes for the first hour, within 1 hour thereafter).
- **Be honest about limitations.** If someone asks about recall, say it's
  unmeasured on real code. If someone asks about the 33% high-risk figure,
  explain domain gating and the N=6 sample size.
- **No defensive responses.** If someone says "this is just regex matching",
  agree — it is. Then explain why that's still useful.

---

## 9. Benchmark Labelling Pipeline (A2/A3) — HUMAN ACTION REQUIRED

### What the founder must do (Rater 1)

**Time estimate:** 3-4 hours total

1. **Generate the targeted corpus manifest** (`benchmarks/targeted_manifest.json`):
   - The repo sourcing research identified candidate repos (see session summary)
   - Create the manifest with repo URLs, pinned commits, licences, and domains
   - Run: `python3 benchmarks/harvest_targeted.py --manifest benchmarks/targeted_manifest.json`
   - Review the output in `benchmarks/targeted_corpus/candidates.json`

2. **Label the targeted findings** (Rater 1):
   - Open `benchmarks/targeted_corpus/candidates.json`
   - For each finding, set `"label": "tp"` or `"label": "fp"` with `"notes"`
   - Time estimate: ~2 minutes per finding, ~1 hour for 30 findings

3. **Label the blind subset** (Rater 1 copy):
   - Open `benchmarks/rater2_blind_subset.json`, make a COPY as `rater1_blind_subset.json`
   - Label independently (do not look at original labels in labels.json)
   - This enables direct comparison with Rater 2

### What the independent Rater 2 must do

**Recruitment (founder action):**
- Reach out to academic contacts in AI auditing, fairness, or compliance
- Offer: co-authorship/acknowledgement on the published benchmark corpus
- Requirement: technical background, independence from the project
- Time commitment: ~2-3 hours for ~80 findings (50 blind subset + 30 targeted)

**Rating task:**
- Rater 2 receives `benchmarks/rater2_blind_subset.json` (50 entries) AND
  the targeted corpus `candidates.json` (all findings)
- Labels each as "tp" or "fp" with notes
- Returns completed file(s)

### After both raters complete

Run: `python3 benchmarks/compute_kappa.py rater1_labels.json rater2_labels.json`

This produces:
- Cohen's kappa with 95% CI
- Agreement matrix
- Disagreement list for adjudication

If kappa >= 0.75: publishable. If 0.60-0.74: publishable with disclosure.
If < 0.60: review labelling criteria for ambiguity before publishing.

### Gate

**No precision figure from the targeted corpus is publishable until both
raters complete and kappa is computed.** This is non-negotiable.

## 10. EN 18228/18282 Publication Tracking (G1/G2)

**When:** Expected Q4 2026 (CEN-CENELEC). Monitor via ai-act-standards.com
**Action:** Revise references/en18228_mapping.yaml and en18282_mapping.yaml
against the final published text. Update draft-status headers. Check for
clause renumbering. Update the docs page.
