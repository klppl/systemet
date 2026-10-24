---
version: 1
slug: "templates-index-html"
primary_target: "templates/index.html"
related_targets: ["docs/script.js","docs/styles.css"]
---

# Surface: release list (templates/index.html → docs/index.html)

Mode: Operate. The visitor plans what to buy on the coming release days.

Audience/job: broad Swedish public, often on a phone, scanning every upcoming release in the next ~2 weeks in one scroll, no tabs or menus (user steer). Past 14 days are secondary and live below the upcoming days.

Constraints: static Jinja2 render, vanilla JS, unofficial (no Systembolaget branding), Swedish copy. Watchlist stored in localStorage.

## Direction contract

THESIS: Every upcoming release as one long, quiet receipt you can read top to bottom; refuses the webshop card grid and the day-tab menu.

OWN-WORLD: Thermal-paper white ground (#F5F5F3), carbon ink (#111), one grey for secondary, one violet accent (#5B4FD6) reserved for what the visitor saved. Geist for names, Geist Mono for every figure (tabular). Dashed rules divide days, dotted hairlines divide lines. Rating reads as a fixed dot ramp. No cards, no shadows except the paper slip of Min lista.

STORY: The visitor sees the next release at the top with the count and time, scrolls through all coming days, marks beers, and the receipt on the right totals items and kronor to take to the store.

FIRST VIEWPORT: Slim header (wordmark, range and count, search, filters). Left: column headers, then day blocks: mono date stub at left (FRE 30 OKT / 10:00 · 11 öl), rows with mark circle, name + style/country, price, APK, Untappd, number. Right 340px: sticky Min lista receipt with running total. Phone: receipt becomes a bottom bar that expands.

FORM: Kvittot, candidate 7 of the grounded list after two re-rolls; seed key 05961b2a. Signature move: the watchlist prints as a running receipt (items, total kr, first release day). Raises: past releases print grey; time as one threaded line; rating dot ramp; two values plus one accent.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
