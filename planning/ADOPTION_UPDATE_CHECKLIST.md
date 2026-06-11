# Formal Adoption Update Checklist

**Purpose:** When the EU AI Act Digital Omnibus is formally adopted and published
in the Official Journal, every reference to "pending formal adoption" or
"provisional agreement" must be updated. This checklist enables execution
in under 2 hours.

**Trigger:** Publication in the Official Journal of the EU. Monitor via:
- eur-lex.europa.eu/oj/
- Council and Parliament press releases
- IAPP news feed

---

## Search strings to find all locations

```bash
# Run from repo root:
grep -rn 'pending.*formal.*adoption\|pending.*adoption\|awaiting.*formal\|provisional.*agreement\|7 May 2026\|expected before.*August 2026\|not yet.*adopted' \
  --include='*.py' --include='*.md' --include='*.html' --include='*.yaml' \
  . | grep -v 'planning/' | grep -v '.git/' | grep -v '__pycache__' | grep -v '.venv/'
```

## Replacement template

**Before:**
> "provisional agreement reached 7 May 2026, pending formal adoption"

**After:**
> "adopted [DATE], published in the Official Journal [OJ_DATE] ([OJ_REFERENCE]).
> New deadlines are now legally binding."

---

## File-by-file checklist

### Scripts (user-facing output)
- [ ] `scripts/timeline.py` — Update all `[AGR]` entries from "PENDING FORMAL ADOPTION" to "ADOPTED [DATE]". Change status from `agreed` to `effective`. Update disclaimer text at bottom.
- [ ] `scripts/report.py:950` — Update "regulation is not yet adopted" line

### References and data
- [ ] `references/article_obligations.yaml:172` — Update `omnibus_status` field
- [ ] `docs/spec/regula-evidence-format-v1.md:357` — Update `omnibus_status` in example JSON

### Site (EN + locales)
- [ ] `site/index.html:345` — Update Omnibus status line in terminal demo
- [ ] `site/locales/de.html:346` — Mirror EN change (German)
- [ ] `site/locales/pt-br.html:355` — Mirror EN change (Portuguese)
- [ ] `site/regions/uae.html:329` — Update "pending" language
- [ ] `site/regions/regulations.html:237` — Update "depending on adoption" language

### Blog posts (editor's notes)
- [ ] `site/blog/blog-omnibus-delay.html:223` — Update "pending formal adoption" to "adopted [DATE]"
- [ ] `site/blog/blog-omnibus-decision-framework.html:247` — Same update

### Internal/tooling (non-user-facing but should be correct)
- [ ] `.claude/skills/regulatory-context/SKILL.md:26` — Update "awaiting formal adoption"
- [ ] `.claude/rules/regulatory-content.md:11` — Update the NEVER rule to reference adoption date
- [ ] `docs/superpowers/plans/2026-05-12-project-files-overhaul.md:55` — Update "awaiting formal adoption"
- [ ] `docs/distribution/regula-state-document.py:114` — Update "pending formal adoption"

### Benchmarks
- [ ] `benchmarks/labels.json` — Update all `deadline_note` entries containing "Pending formal adoption" (11 entries as of June 2026). Use: `python3 -c "import json; d=json.load(open('benchmarks/labels.json')); [print(i, e.get('deadline_note','')[:80]) for i,e in enumerate(d) if 'pending' in e.get('deadline_note','').lower()]"`

---

## Post-update verification

```bash
# Should return 0 results (excluding planning/):
grep -rn 'pending.*formal.*adoption\|awaiting.*adoption' \
  --include='*.py' --include='*.md' --include='*.html' --include='*.yaml' \
  . | grep -v 'planning/' | grep -v '.git/' | grep -v '__pycache__'

# Run full verify:
python3 tests/test_classification.py
python3 -m scripts.cli self-test
python3 -m scripts.cli doctor
python3 -m scripts.cli timeline
```

---

**Estimated time:** 1.5–2 hours (including locale sync and verification).
**Owner:** Founder or automated session, triggered by OJ publication.
