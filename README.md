# Systemet: Systembolaget Data Fetch

A Python script that:
1. Fetches product data from the Systembolaget API.
2. Saves or updates products in a local SQLite database.
3. Tracks:
   - Original price and changed price
   - Launch date (date only)
   - APK (ml ethanol per krona)
   - Timestamps for updates

## Usage
1. Clone or download this repo.
2. Run `python3 main.py` to fetch/update data in `products.db`.


