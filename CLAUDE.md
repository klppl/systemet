# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Step 1: Fetch all beer data from Systembolaget API
python getallbeer.py

# Step 2: Generate the static website
python generate_html_new_beer.py

# Test the Untappd module
python test_untappd_module.py

# Fetch all products (not just beer) — slower, rarely needed
python getallproducts.py
```

## Architecture

This is a two-step pipeline that runs daily via GitHub Actions (`.github/workflows/daily-beer-update.yml`):

1. **Data collection** (`getallbeer.py`) — Calls Systembolaget's public API, paginates through all assortment types for the `Öl` (beer) category, deduplicates, tracks price/alcohol history per product as `{x: timestamp_ms, y: value}` arrays, and marks products not seen for 7 days as removed. Outputs to `data/beers.json` and `data/beers_updated.json`.

2. **Site generation** (`generate_html_new_beer.py`) — Reads `data/beers.json`, filters beers with a `productLaunchDate` within ±14 days of today, enriches each beer with Untappd ratings (via `untappd.py`), then renders `templates/index.html` via Jinja2 into `docs/index.html`. The `docs/` folder is served as GitHub Pages.

### Key modules

- **`untappd.py`** — Wraps Algolia search against Untappd's beer index. Results are cached in `data/untappd_mapping.json` keyed by `productNumber` to avoid repeat API calls. Returns `None` for no-match (also cached to avoid re-querying).

- **`templates/index.html`** — Jinja2 template (autoescaped, `sek` filter formats numbers as `34,90`). Receives `range_text`, `categories`, `upcoming_groups` (today and later, ascending), `past_groups` (descending), `upcoming_count`, `past_count`, and `generated_time`. Each group (dict with `date_str`, `weekday_short`, `day_month`, `relative`, `sell_start`, `list_id`, `is_past`, `beers`) is rendered by the partial **`templates/day.html`**.

- **`docs/script.js`** — Client-side search and filtering (style, minimum APK, minimum Untappd), sorting (date, Untappd, APK, price), expandable beer details, and the "Min lista" watchlist stored in `localStorage` (`systemet.list.v1`) with a running total. Non-date sorts move upcoming rows into `#global-beer-list`; date sort restores them to their `data-parent-id` containers.

- **Design** — see `PRODUCT.md` and the direction contract in `.impeccable/surfaces/`. The look is a quiet receipt: paper ground, ink, one violet accent reserved for saved beers.

### Data flow for a beer card

`beers.json` → filtered by launch date → APK calculated → Untappd enriched → `prepare_beer_view_model()` → Jinja2 template → `docs/index.html`

APK (Alcohol Per Krona) = `(alcoholPercentage × volume / 100) / price` — displayed with CSS classes `high` (≥0.8), `medium`, or `low` (<0.6).
