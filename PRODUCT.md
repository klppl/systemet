# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Static site: Python (`generate_html_new_beer.py`) renders a Jinja2 template (`templates/index.html`) into `docs/`, served by GitHub Pages at systemet.beer. Vanilla JS (`docs/script.js`) and CSS (`docs/styles.css`); no build step. Regenerated daily by GitHub Actions.

## Users

A broad public audience in Sweden: everyone from value-focused "APK hunters" to craft-beer enthusiasts who check Untappd. They visit in the days before a Systembolaget release to decide what to buy, and often check on a phone.

## Job

Plan the next release: see what drops on the next release day (and the ones after it), spot the beers worth buying, and know when they go on sale (release days usually open at 10:00). Past releases from the last 14 days are secondary reference material.

## What it makes possible

Systembolaget's own site doesn't present upcoming beer launches as one scannable calendar with value (APK) and community rating (Untappd) side by side. This site does, daily, with no account needed.

## Data available per beer

Name, producer, country and region, category (level 2 and 3), style taste text, taste clock values (bitter, body, sweetness, fruit acid, smokiness), price, volume, ABV, APK (computed), assortment type (e.g. Lokalt & Småskaligt, Säsong, Tillfälligt, Ordervaror), launch date, sell start time, product image, and an Untappd match (score, count, link) for about two thirds of beers.

## Constraints

- Unofficial fan site. It must not imitate Systembolaget's branding or look like an official Systembolaget property.
- Swedish UI copy.
- Must work on phones.
- New features may be added (for example a personal watchlist stored in the browser, search, or richer beer details), as long as the site stays a static generated page.

## Terminology

- **APK**: alkohol per krona, ml of pure alcohol per krona.
- **Släpp**: a release day.
