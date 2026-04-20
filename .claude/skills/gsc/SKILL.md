# Google Search Console

GSC is connected via OAuth. Requires `.venv` activated (dependencies: `google-auth`, `google-auth-oauthlib`, `google-api-python-client`).

```bash
source .venv/bin/activate

# Top queries, last 28 days
python3 scripts/gsc_fetch.py --days 28 --dimensions query --limit 25

# Top pages
python3 scripts/gsc_fetch.py --days 28 --dimensions page --limit 25

# Blog pages only
python3 scripts/gsc_fetch.py --days 28 --page-filter "/blog"

# Daily trend for a query
python3 scripts/gsc_fetch.py --days 28 --dimensions date --query-filter "eu ai act"

# By country
python3 scripts/gsc_fetch.py --days 28 --dimensions country

# JSON output
python3 scripts/gsc_fetch.py --days 28 --format json

# Other properties (validground.com, streetsignal.co.za)
python3 scripts/gsc_fetch.py --site "sc-domain:validground.com" --days 28
```

Auth files (`credentials.json`, `token.json`) are gitignored. Token auto-refreshes. If it expires fully, re-run `gsc_auth.py` with the `.venv` activated.
