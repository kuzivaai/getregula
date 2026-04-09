# Primary-source reference documents

Regula cites statistics from a small number of primary research PDFs.
To keep the repo lean, the PDFs themselves are gitignored. This file
lists each one, its canonical fetch URL, and its SHA-256 hash so
contributors can verify their local copy.

Drop fetched PDFs into `references/` at the path shown and citations
in `docs/landscape.md`, `scripts/timeline.py`, and `README.md` will
resolve to the correct file.

## References

### AICDI 2025 Global Insights

- **Local path:** `references/aicdi_2025_global_insights.pdf`
- **Title:** *Responsible AI in practice: 2025 global insights from the AI Company Data Initiative*
- **Publisher:** Thomson Reuters Foundation + UNESCO, 2026
- **ISBN:** 978-92-3-100863-4
- **DOI:** `https://doi.org/10.54678/YJWP8855`
- **License:** CC-BY-SA 3.0 IGO (UNESCO Open Access)
- **Fetch URL:** <https://unesdoc.unesco.org/ark:/48223/pf0000397817_eng>
  (note: unesdoc is gated behind Cloudflare Bot Protection — must be
  downloaded in a browser; curl/wget receive a challenge page)
- **SHA-256:** `895f48950284458b5dc77436b2337297434a20f03c7bbc0f8a79eb9c58def9fe`
- **Pages:** 94
- **Cited in:** `docs/landscape.md`, `scripts/timeline.py`,
  `README.md` (AICDI gap table with page references)
