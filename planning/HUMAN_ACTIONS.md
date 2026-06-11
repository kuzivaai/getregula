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
