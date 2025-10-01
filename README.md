# Systembolaget Product Scraper

A Python tool for scraping product data from Systembolaget's API and tracking price/alcohol changes over time.

## Features

- Fetches all products and beer-only data from Systembolaget API
- Tracks price and alcohol percentage history
- Identifies new products and price changes
- Removes discontinued products after 7 days
- Exports data to JSON format

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Scrape all products
python getallproducts.py

# Scrape beer products only
python beer.py
```

## Output

- `data/products.json` - Complete product database
- `data/beers.json` - Beer-only product database  
- `data/updated.json` - Recently updated products
- `data/beers_updated.json` - Recently updated beers

## Data Structure

Products include price history, alcohol history, and change tracking with timestamps.
