import os
import sqlite3
import requests
from requests import Session
from datetime import datetime, timezone

base_url = "https://www.systembolaget.se"
api_url = "https://api-extern.systembolaget.se/sb-api-ecommerce/v1/productsearch/search"
api_key = "cfc702aed3094c86b92d6d4ff7a54c84"


def initialize_database(db_name="products.db"):
    """
    Creates (if not exists) the SQLite database and the products table.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            productId TEXT PRIMARY KEY,

            -- Basic product info
            productNumber TEXT,
            productNumberShort TEXT,
            productNameBold TEXT,
            productNameThin TEXT,
            producerName TEXT,
            supplierName TEXT,
            categoryLevel1 TEXT,
            categoryLevel2 TEXT,
            categoryLevel3 TEXT,
            country TEXT,
            productLaunchDate TEXT,   -- Only storing date portion now

            -- Availability
            isTemporaryOutOfStock BOOLEAN,
            isCompletelyOutOfStock BOOLEAN,

            -- Pricing
            price REAL,               -- current/latest price
            originalPrice REAL,       -- the first price we observed
            newPrice REAL,            -- changed price if it differs from original
            lastUpdated TEXT,         -- timestamp of the last price update

            -- Alcohol & Volume
            volume REAL,              -- e.g. 750.0 ml
            alcoholPercentage REAL,   -- e.g. 14.0 for 14%

            -- APK = ml ethanol per krona (rounded to 2 decimals)
            apk REAL
        )
        """
    )

    conn.commit()
    conn.close()


def get_existing_product(conn, product_id):
    """
    Returns the existing row for a product, or None if not found.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE productId = ?", (product_id,))
    return cursor.fetchone()


def format_launch_date(product):
    """
    Returns only the 'YYYY-MM-DD' portion of productLaunchDate if it contains 'T',
    otherwise returns the original string or empty string if None.
    """
    raw_date = product.get("productLaunchDate") or ""
    if "T" in raw_date:
        return raw_date.split("T", 1)[0]  # e.g. '2024-05-27T00:00:00' -> '2024-05-27'
    return raw_date


def insert_new_product(cursor, prod):
    """
    Insert logic for a brand new product row (does not exist yet).
    - Sets originalPrice = current API price
    - newPrice = None initially
    - price = current price
    - lastUpdated = now
    - calculates apk
    - strips time portion from productLaunchDate
    """
    p_id = prod.get("productId")
    current_price = prod.get("price") or 0.0

    originalPrice = current_price
    newPrice = None

    # Use timezone-aware datetime for "lastUpdated"
    lastUpdated = datetime.now(timezone.utc).isoformat()

    # Extract only YYYY-MM-DD for productLaunchDate
    launch_date_str = format_launch_date(prod)

    # Calculate APK in ml ethanol per krona, rounded to 2 decimals
    volume_ml = prod.get("volume") or 0.0
    abv_pct = prod.get("alcoholPercentage") or 0.0
    apk_value = None
    if current_price > 0:
        ml_ethanol = volume_ml * (abv_pct / 100.0)
        apk_value = ml_ethanol / current_price
        apk_value = round(apk_value, 2)

    cursor.execute(
        """
        INSERT INTO products (
            productId,
            productNumber,
            productNumberShort,
            productNameBold,
            productNameThin,
            producerName,
            supplierName,
            categoryLevel1,
            categoryLevel2,
            categoryLevel3,
            country,
            productLaunchDate,
            isTemporaryOutOfStock,
            isCompletelyOutOfStock,
            price,
            originalPrice,
            newPrice,
            lastUpdated,
            volume,
            alcoholPercentage,
            apk
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            p_id,
            prod.get("productNumber"),
            prod.get("productNumberShort"),
            prod.get("productNameBold"),
            prod.get("productNameThin"),
            prod.get("producerName"),
            prod.get("supplierName"),
            prod.get("categoryLevel1"),
            prod.get("categoryLevel2"),
            prod.get("categoryLevel3"),
            prod.get("country"),
            launch_date_str,  # date portion only
            prod.get("isTemporaryOutOfStock"),
            prod.get("isCompletelyOutOfStock"),
            current_price,
            originalPrice,
            newPrice,
            lastUpdated,
            volume_ml,
            abv_pct,
            apk_value
        )
    )


def update_existing_product(cursor, db_row, prod):
    """
    Update logic for an existing row if price has changed.
    - Does NOT change originalPrice
    - If the new API price differs from current stored price, set newPrice, lastUpdated, etc.
    - Strips time from productLaunchDate if needed, though typically if the launch date changes
      we can update it too.
    """
    product_id_db = db_row[0]      # productId is column index 0
    current_price_db = db_row[14]  # price is column index 14

    new_price_api = prod.get("price") or 0.0

    # If the price is unchanged, do nothing
    if abs(new_price_api - current_price_db) < 1e-9:
        # Optionally, we could also check if productLaunchDate changed. Usually it won't.
        return

    lastUpdated = datetime.now(timezone.utc).isoformat()

    # Recalc APK
    volume_ml = prod.get("volume") or 0.0
    abv_pct = prod.get("alcoholPercentage") or 0.0
    apk_value = None
    if new_price_api > 0:
        ml_ethanol = volume_ml * (abv_pct / 100.0)
        apk_value = ml_ethanol / new_price_api
        apk_value = round(apk_value, 2)

    # If you want to re-check the launch date too, do it:
    launch_date_str = format_launch_date(prod)

    cursor.execute(
        """
        UPDATE products
        SET
            price = ?,
            newPrice = ?,
            lastUpdated = ?,
            isTemporaryOutOfStock = ?,
            isCompletelyOutOfStock = ?,
            apk = ?,
            volume = ?,
            alcoholPercentage = ?,
            productLaunchDate = ?
        WHERE productId = ?
        """,
        (
            new_price_api,
            new_price_api,
            lastUpdated,
            prod.get("isTemporaryOutOfStock"),
            prod.get("isCompletelyOutOfStock"),
            apk_value,
            volume_ml,
            abv_pct,
            launch_date_str,   # In case the API changed it
            product_id_db
        )
    )


def insert_or_update_product(conn, prod):
    """
    Decides whether to insert a new product or update an existing one.
    """
    p_id = prod.get("productId")
    if not p_id:
        return  # skip if no productId

    existing_row = get_existing_product(conn, p_id)
    cursor = conn.cursor()

    if existing_row is None:
        # Insert new product
        insert_new_product(cursor, prod)
    else:
        # Possibly update existing product if price changed, or if you want to check other fields
        update_existing_product(cursor, existing_row, prod)

    conn.commit()


def fetch_products_from_api():
    """
    Fetches all products from the Systembolaget API and stores/updates them in the SQLite database.
    """
    db_name = "products.db"
    initialize_database(db_name)

    with Session() as s:
        headers = {"Ocp-Apim-Subscription-Key": api_key}
        # First page
        r = s.get(api_url + "?page=1&size=30&sortBy=Score&sortDirection=Ascending", headers=headers)
        first_page_json = r.json()

        total_pages = first_page_json['metadata']['totalPages']

        # Insert/Update first page
        conn = sqlite3.connect(db_name)
        for prod in first_page_json["products"]:
            insert_or_update_product(conn, prod)
        conn.close()

        # Pages 2..N
        for page in range(2, total_pages + 1):
            query_string = f"?page={page}&size=30&sortBy=Score&sortDirection=Ascending"
            r = s.get(api_url + query_string, headers=headers)
            products_on_page = r.json().get("products", [])

            conn = sqlite3.connect(db_name)
            for prod in products_on_page:
                insert_or_update_product(conn, prod)
            conn.close()

    print("Product data fetched/updated in SQLite database.")


if __name__ == "__main__":
    fetch_products_from_api()
