# Systembolaget Product Scraper & Site Generator

A Python tool suite for scraping product data from Systembolaget's API, tracking history, and generating a user-friendly website for upcoming beer releases.

## Features

- **Data Collection**:
  - Fetches product data from Systembolaget API
  - Tracks price and alcohol percentage history
  - Identifies new products and price changes
  - Removes discontinued products after 7 days
- **Website Generation**:
  - Generates a static HTML site for upcoming beer releases
  - Calculates and displays APK (Alcohol Per Krona)
  - Enriches beer data with **Untappd ratings**
  - Responsive design with filtering and sorting options

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
pip install jinja2  # Required for site generation
```

## Usage

### 1. Fetch Data
First, scrape the latest data from Systembolaget. This updates the local JSON database.

```bash
# Scrape beer products only (Recommended)
python getallbeer.py

# OR Scrape all products (Slower)
python getallproducts.py
```

### 2. Generate Website
Generate the static HTML site based on the fetched data. This will filter for upcoming releases, fetch Untappd ratings, and build the site in the `docs/` folder.

```bash
python generate_html_new_beer.py
```

## Output

### Data Files (`data/`)
- `data/beers.json` - Complete beer database with history
- `data/beers_updated.json` - Recently updated beers
- `data/untappd_mapping.json` - Cache of Untappd matches

### Website (`docs/`)
The generated website is located in the `docs/` folder, ready for deployment (e.g., GitHub Pages).
- `docs/index.html` - Main listing page
- `docs/styles.css` - Stylesheet
- `docs/script.js` - Client-side logic

## Data Structure

Products include price history, alcohol history, and change tracking with timestamps.

