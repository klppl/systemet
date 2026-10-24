---
name: systemet.beer
description: Every upcoming Systembolaget beer release, printed as one long receipt.
colors:
  paper: "#F5F5F3"
  slip: "#FFFFFF"
  ink: "#111111"
  ink-2: "#5C5C5A"
  rule: "rgba(17, 17, 17, 0.14)"
  rule-strong: "rgba(17, 17, 17, 0.9)"
  accent: "#5B4FD6"
  accent-ink: "#FFFFFF"
  accent-wash: "#EDEBFB"
typography:
  wordmark:
    fontFamily: "Geist Mono, ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "15px"
    fontWeight: 600
    letterSpacing: "0.04em"
  headline:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "20px"
    fontWeight: 600
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 500
    lineHeight: 1.45
  body:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.45
  body-sm:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.45
  figure:
    fontFamily: "Geist Mono, ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "15px"
    fontWeight: 400
    letterSpacing: "-0.01em"
    fontFeature: "tnum"
  date-stub:
    fontFamily: "Geist Mono, ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "15px"
    fontWeight: 600
    letterSpacing: "0.02em"
  receipt:
    fontFamily: "Geist Mono, ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: "Geist Mono, ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "11px"
    fontWeight: 400
    letterSpacing: "0.06em"
rounded:
  sm: "4px"
  md: "6px"
  round: "50%"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  day-gap: "28px"
  layout-gap: "48px"
  gutter: "clamp(16px, 4vw, 64px)"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.md}"
    padding: "0 16px"
    height: "40px"
  button-primary-hover:
    backgroundColor: "{colors.ink-2}"
  button-link:
    textColor: "{colors.ink}"
    typography: "{typography.body-sm}"
    padding: "0"
  field:
    backgroundColor: "{colors.slip}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    height: "40px"
  field-label:
    textColor: "{colors.ink-2}"
    typography: "{typography.label}"
    padding: "0 0 0 12px"
  detail-link:
    backgroundColor: "{colors.slip}"
    textColor: "{colors.ink}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.md}"
    padding: "0 10px 0 12px"
    height: "36px"
  beer-line:
    textColor: "{colors.ink}"
    typography: "{typography.title}"
    padding: "11px 0"
  beer-line-saved:
    textColor: "{colors.accent}"
  beer-line-past:
    textColor: "{colors.ink-2}"
  mark:
    textColor: "{colors.ink}"
    width: "28px"
    height: "44px"
  mark-saved:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.accent-ink}"
  day-stub:
    textColor: "{colors.ink-2}"
    typography: "{typography.receipt}"
    padding: "14px 0 18px 20px"
    width: "148px"
  slip:
    backgroundColor: "{colors.slip}"
    textColor: "{colors.ink}"
    typography: "{typography.receipt}"
    padding: "24px 22px 30px"
    width: "320px"
---

# Design System: systemet.beer

## Overview

**Creative North Star: "Kvittot" (The Receipt)**

The whole release calendar reads as one long, quiet till receipt: thermal-paper ground, carbon ink, figures set in a monospace that lines up like a printout. The visitor reads top to bottom through every coming release day in a single scroll; days are torn off by dashed rules, lines are separated by dotted hairlines, and a thin vertical thread runs down the left through every day's date stub. Nothing is boxed into a card. The only object that sits above the paper is the visitor's own receipt, Min lista, which totals what they have marked.

Density is ledger-like: one beer per line, name and style on the left, price, APK, Untappd and article number in right-aligned tabular columns. Hierarchy comes from weight and from the ink/grey split, never from size jumps or colour. Colour is almost absent: two values (paper and ink), one grey for everything secondary, and one violet that means "you saved this". Past releases do not disappear; they print grey.

The site is an unofficial fan site and must never borrow Systembolaget's visual identity; the receipt world is deliberately its own.

**Key Characteristics:**
- Two values plus one grey plus one accent; the accent marks what the visitor saved.
- Geist for names and prose, Geist Mono for every figure, date and label, always tabular.
- Dashed rules divide days and sections; dotted hairlines divide lines.
- Flat paper everywhere; the only shadow belongs to the Min lista slip.
- Ratings read on a fixed three-step dot ramp, not stars or colour.
- Past releases print grey and stay in the list.

## Colors

A monochrome thermal-paper palette with a single cool violet held in reserve.

### Primary
- **Saved Violet** (accent): the visitor's own marks. Fills the saved mark circle, colours a saved beer's name, and stands in for the system affordances that belong to the visitor's hand (focus ring, text selection, caret, mark hover). It never decorates content, data or categories.
- **Violet Wash** (accent-wash): the brief highlight under a line as it prints onto the receipt; exists only during that animation.
- **Violet Ink** (accent-ink): the tick drawn inside a filled saved mark and text on violet selection.

### Neutral
- **Thermal Paper** (paper): the page ground, sticky header backgrounds and the mobile scrim (at 92% opacity).
- **Slip White** (slip): the Min lista receipt, input fields, detail-link pills and the product-image tile; anything that is a separate piece of paper laid on the ground.
- **Carbon Ink** (ink): names, figures, primary buttons, the filled dot of the next release day.
- **Faded Ink** (ink-2): every secondary reading: style and country, column headers, field labels, article numbers, past releases, the colophon.
- **Hairline** (rule): dotted line separators, field borders, the day thread, dashed separators inside the slip.
- **Tear Line** (rule-strong): dashed day separators, the receipt total rule, the past-releases and colophon rules.

### Named Rules
**The Two Values Rule.** Content is ink or faded ink on paper. A third tone appears only as the violet accent, and only for something the visitor did.

**The Saved Is Violet Rule.** Violet means "mine". Never use it for a category, a high APK, a good rating or a link; those are carried by weight and the dot ramp.

## Typography

**Display Font:** none; there is no display tier.
**Body Font:** Geist (with ui-sans-serif, system-ui)
**Label/Mono Font:** Geist Mono (with ui-monospace, SFMono-Regular, Menlo)

**Character:** Geist carries the words a person reads (beer names, taste notes, buttons); Geist Mono carries everything a till would print (prices, APK, ratings, dates, counts, labels, the whole receipt). The pairing is quiet and mechanical rather than expressive.

### Hierarchy
- **Wordmark** (Geist Mono 600, 15px, 0.04em, uppercase): the site name in the masthead only.
- **Headline** (Geist 600, 20px, -0.01em): the "Redan släppta" section heading; the largest type in the system.
- **Title** (Geist 500, 16px, 1.45): beer names on each line. Masthead h1 sits at 15px/600 beside the wordmark.
- **Body** (Geist 400, 16px, 1.45): base text; taste notes run at 15px with a 68ch measure.
- **Body small** (Geist 400, 14px): the style/country sub-line, detail facts, buttons, links, filter status.
- **Figure** (Geist Mono 400, 15px, -0.01em, tabular): price, APK, rating and article number columns; 13px inside sub-lines and on phone.
- **Date stub** (Geist Mono 600, 15px, 0.02em, uppercase): the day date ("FRE 23 OKT"); relative day and time below it at 13px.
- **Receipt** (Geist Mono 400, 13px): all Min lista content; the title is 600 at 0.12em uppercase, the total 600 at 15px.
- **Label** (Geist Mono 400, 11px, 0.06em, uppercase): column headers, field labels, detail fact terms, day headings inside the slip.

### Named Rules
**The Every Figure Is Mono Rule.** Any number a visitor compares (price, APK, rating, volume, ABV, count, article number, time) is set in Geist Mono with tabular figures, so columns line up like a printout.

**The Weight Not Size Rule.** Emphasis is weight (500 for names, 600 for dates, totals, high APK of 0,80+ and top-tier ratings), not a bigger size or a colour.

**The Label Floor Rule.** Uppercase mono labels stop at 11px; they name a column or field and never introduce a heading.

## Layout

A single long ledger with a sticky receipt beside it. The page is capped at 1440px with a fluid gutter (clamp 16px to 64px). On wide screens the layout is two columns: the ledger and a 320px Min lista slip, 48px apart, the slip sticky at 24px from the top.

Each release day is a two-column grid: a 148px date stub (sticky, so the date stays visible while its lines scroll) and the lines, 28px apart. A 1px thread runs down the left edge through every day, with a 9px ring at each stub; the next release day's ring is filled with ink. A sticky column header, built with the same grid, aligns with every row. Each line is a 28px mark column then a five-column grid: name (fluid), price 92px, APK 64px, Untappd 84px, article number 68px, 16px apart, figures right-aligned. Section elements below the days (filter status, empty state, past heading, colophon) indent to the lines column, not the page edge.

Rhythm: 11px vertical padding per line, 28px under each day, 4/8/12/16/24px for internal gaps.

Responsive: at 1180px and below the slip leaves the column and becomes a fixed bottom bar (56px) that expands upward over a paper scrim. At 760px and below the date stub turns into a sticky full-width bar with a dashed underline, the thread and column header are dropped, the toolbar becomes a two-column grid with search spanning both, and each line restacks to name + price on top, APK and Untappd (with inline unit labels) below; country and article number are hidden. The mark grows to a 40px column with a 56px touch height.

## Elevation & Depth

Flat by default. The ledger, header and fields sit directly on the paper with no shadow; separation comes from dashed and dotted rules and the paper/slip white difference. The one exception is the Min lista slip, which is a physical piece of receipt paper and so may cast a soft shadow and carry a torn, zig-zag edge (an 8px conic-gradient mask on desktop's bottom edge, 6px on the mobile bar's top edge).

### Shadow Vocabulary
- **Slip rest** (`box-shadow: 0 1px 2px rgba(17,17,17,0.06), 0 8px 24px -12px rgba(17,17,17,0.18)`): the desktop receipt.
- **Slip bar** (`box-shadow: 0 -8px 24px -12px rgba(17,17,17,0.18)`): the collapsed mobile bar.
- **Slip lifted** (`filter: drop-shadow(0 -6px 18px rgba(17,17,17,0.12))`): the mobile slip while open, with a paper scrim behind it.

### Named Rules
**The One Slip Rule.** Only the visitor's receipt casts a shadow or has a torn edge. Nothing in the ledger is lifted, and no other surface borrows the torn edge.

## Shapes

Almost square. Interactive pieces of slip paper (fields, buttons, detail-link pills) take gently softened corners (6px); small tiles and hit areas (product image, remove button, focus ring) take 4px. Circles are reserved for meaning: the save mark ring, the day-thread rings and the rating dots. The slip itself has no radius; its silhouette is the torn edge. Lines and days have no containers at all, only rules.

## Components

### Buttons
Plain and inked, used sparingly.
- **Shape:** 6px corners, 40px tall.
- **Primary:** carbon ink fill with paper text, Geist 500 at 14px, 16px horizontal padding. Used for "Kopiera listan" and "Rensa filter" in the empty state.
- **Hover / Focus:** fill eases to faded ink (0.15s); focus is the 2px violet ring offset 2px.
- **Link button:** no box; ink text at 14px, 1px underline offset 3px. Used for "Töm" and "Rensa filter".

### Inputs / Fields
- **Style:** slip-white fill, 1px hairline border, 6px corners, 40px tall; a mono 11px uppercase label sits inside the field before the value ("STIL Alla"). Selects use a custom 16px chevron; search has a 20px stroke magnifier inset left.
- **Hover:** border darkens to 35% ink.
- **Focus:** border goes to ink and the whole field takes the 2px violet ring.
- **Active filter:** a select holding a non-default value takes a 2px ink border (1px border plus 1px inset ring), so applied filters read at a glance without colour.

### Navigation
There is no navigation menu or tabs. The masthead is a single baseline row: wordmark, h1, then range and count in faded ink, with the toolbar (search and four selects) beneath.

### Beer Line (signature)
One beer per line, a full-width button that expands its detail.
- **Mark:** a 20px stroked ring (1.5px). Hover strokes it violet; pressed shrinks to 0.88; saved fills it violet and draws a white tick by stroke-dash.
- **Name:** Geist 500, underlined in faded ink on hover. Saved lines colour the name violet.
- **Sub-line:** faded ink, 14px, segments joined with " · ", volume and ABV in mono. Order items carry a mono uppercase "Beställs" tag.
- **Figures:** right-aligned mono columns; APK of 0,80+ prints in 600; a missing rating prints as an en dash in faded ink.
- **Past:** names and figures drop to faded ink at 400 and rating dots to 55% opacity.
- **Detail:** unfolds under the name column (0.32s, 4px rise): a 112px slip-white image tile, taste note, a grid of mono-labelled facts, and outlined detail-link pills (36px, hairline border going ink on hover, 16px arrow icon).

### Rating Dot Ramp (signature)
A 9px dot before the Untappd score, fixed tiers: 3.50+ a small 5px dot, 3.75+ a 7px dot, 4.00+ a full 9px dot with the score in 600. Below 3.50 the score prints without a dot.

### Day Stub (signature)
Mono date block at the left of each day: date in ink 600 uppercase, relative day ("I dag", "Om 6 dagar") in ink, sell time and count in faded ink. A 9px ring sits on the thread; the next release day's ring is filled.

### Min lista (signature)
The receipt. Slip-white, mono 13px, centred spaced title, a note that it saves in the browser, lines grouped under uppercase day headings with dashed hairlines, each line name, price and a 24px remove button. A dashed tear-line rule precedes the total (count and kronor, 600, 15px), then the primary button and a link button. New lines print in: a clip-path reveal from the top with a brief violet wash (0.42s). On phones the slip collapses to a bottom bar reading "MIN LISTA" and the count and total, with a chevron that rotates when opened.

## Do's and Don'ts

### Do:
- **Do** set every comparable figure in Geist Mono with tabular numerals, right-aligned in its column.
- **Do** divide release days with a 1px dashed tear-line rule and lines with a 1px dotted hairline.
- **Do** keep violet for the visitor's own marks and the focus ring, selection and caret.
- **Do** print past releases in faded ink rather than hiding them.
- **Do** carry emphasis with weight (500 / 600), not size or colour.
- **Do** ease motion with cubic-bezier(0.16, 1, 0.3, 1) and drop all animation under prefers-reduced-motion.
- **Do** use 20px stroked line icons (1.5px stroke, round caps) drawn as inline SVG.

### Don't:
- **Don't** put beers in cards, tiles or a grid; every beer is a line on the receipt.
- **Don't** cast shadows or tear edges on anything but the Min lista slip.
- **Don't** use violet for ratings, APK, categories or links.
- **Don't** split release days into tabs or a day menu; all days read in one scroll.
- **Don't** borrow Systembolaget's colours, logo or typography.
- **Don't** use stars or colour scales for Untappd ratings; use the three-step dot ramp.
