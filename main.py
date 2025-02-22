import os
import sqlite3
import requests
from requests import Session
from datetime import datetime, timezone

# Global changes log to track changes made during processing.
changes_log = []

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
            productLaunchDate TEXT,

            -- Availability
            isTemporaryOutOfStock BOOLEAN,
            isCompletelyOutOfStock BOOLEAN,

            -- Pricing
            price REAL,
            originalPrice REAL,
            newPrice REAL,
            lastUpdated TEXT,

            -- Alcohol & Volume
            volume REAL,
            alcoholPercentage REAL,

            -- APK (ml ethanol per krona)
            apk REAL
        )
        """
    )
    conn.commit()
    conn.close()


def get_product_count(db_name="products.db"):
    """
    Returns the current number of products in the database.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def print_progress_bar(processed, total, bar_length=40):
    """
    Prints a simple progress bar on the same line.
    """
    fraction = processed / total if total > 0 else 1
    filled_length = int(bar_length * fraction)
    bar = '#' * filled_length + '-' * (bar_length - filled_length)
    print(f"\rProgress: [{bar}] {processed}/{total}", end='', flush=True)


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
    otherwise returns the original string.
    """
    raw_date = product.get("productLaunchDate") or ""
    if "T" in raw_date:
        return raw_date.split("T", 1)[0]
    return raw_date


def insert_new_product(cursor, prod):
    """
    Inserts a new product into the database.
    """
    p_id = prod.get("productId")
    current_price = prod.get("price") or 0.0
    originalPrice = current_price
    newPrice = None
    lastUpdated = datetime.now(timezone.utc).isoformat()
    launch_date_str = format_launch_date(prod)
    volume_ml = prod.get("volume") or 0.0
    abv_pct = prod.get("alcoholPercentage") or 0.0
    apk_value = None
    if current_price > 0:
        ml_ethanol = volume_ml * (abv_pct / 100.0)
        apk_value = round(ml_ethanol / current_price, 2)

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
            launch_date_str,
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
    # Log the new insertion.
    changes_log.append(f"Inserted product {p_id} (price: {current_price})")


def update_existing_product(cursor, db_row, prod):
    """
    Updates an existing product in the database if the price has changed.
    """
    p_id = prod.get("productId")
    current_price_db = db_row[14]  # price column from the database
    new_price_api = prod.get("price") or 0.0

    # If the price is unchanged, do nothing.
    if abs(new_price_api - current_price_db) < 1e-9:
        return

    lastUpdated = datetime.now(timezone.utc).isoformat()
    volume_ml = prod.get("volume") or 0.0
    abv_pct = prod.get("alcoholPercentage") or 0.0
    apk_value = None
    if new_price_api > 0:
        ml_ethanol = volume_ml * (abv_pct / 100.0)
        apk_value = round(ml_ethanol / new_price_api, 2)
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
            launch_date_str,
            p_id
        )
    )
    # Log the update with details.
    changes_log.append(f"Updated product {p_id} (price: {current_price_db} -> {new_price_api})")


def insert_or_update_product(conn, prod):
    """
    Checks whether to insert a new product or update an existing one.
    """
    p_id = prod.get("productId")
    if not p_id:
        return  # Skip if no productId
    existing_row = get_existing_product(conn, p_id)
    cursor = conn.cursor()
    if existing_row is None:
        insert_new_product(cursor, prod)
    else:
        update_existing_product(cursor, existing_row, prod)
    conn.commit()


def fetch_products_from_api():
    """
    Fetches all products from the Systembolaget API and updates the SQLite database.
    Displays a progress bar and, at the end, prints a summary of all changes.
    """
    db_name = "products.db"
    initialize_database(db_name)
    processed_products = 0

    # Get the initial count from the database.
    total_in_db = get_product_count(db_name)
    with Session() as s:
        headers = {"Ocp-Apim-Subscription-Key": api_key}
        r = s.get(api_url + "?page=1&size=30&sortBy=Score&sortDirection=Ascending", headers=headers)
        first_page_json = r.json()
        total_pages = first_page_json['metadata']['totalPages']

        # If the database was empty, estimate total count from the API.
        if total_in_db == 0:
            total_in_db = 30 * total_pages

        # Process first page.
        conn = sqlite3.connect(db_name)
        for prod in first_page_json["products"]:
            insert_or_update_product(conn, prod)
            processed_products += 1
            current_total = get_product_count(db_name)
            print_progress_bar(processed_products, current_total)
        conn.close()

        # Process remaining pages.
        for page in range(2, total_pages + 1):
            r = s.get(api_url + f"?page={page}&size=30&sortBy=Score&sortDirection=Ascending", headers=headers)
            products_on_page = r.json().get("products", [])
            conn = sqlite3.connect(db_name)
            for prod in products_on_page:
                insert_or_update_product(conn, prod)
                processed_products += 1
                current_total = get_product_count(db_name)
                print_progress_bar(processed_products, current_total)
            conn.close()

    # Finish progress bar line.
    print("\n\nProduct data fetched/updated in SQLite database.")

    # Print a summary of all changes.
    print("\nSummary of changes:")
    if changes_log:
        for change in changes_log:
            print(change)
    else:
        print("No changes made.")


if __name__ == "__main__":
    fetch_products_from_api()
