import os
import sqlite3
import requests
from requests import Session
from datetime import datetime, timezone
import logging
import time
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('systemet.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global changes log to track changes made during processing.
changes_log = []

base_url = "https://www.systembolaget.se"
api_url = "https://api-extern.systembolaget.se/sb-api-ecommerce/v1/productsearch/search"
api_key = "cfc702aed3094c86b92d6d4ff7a54c84"

# Configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
REQUEST_TIMEOUT = 30  # seconds

def get_database_connection(db_name="products.db"):
    """
    Creates a database connection with proper configuration.
    """
    try:
        conn = sqlite3.connect(db_name)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")  # Better concurrent access
        conn.execute("PRAGMA synchronous = NORMAL")  # Better performance
        conn.execute("PRAGMA cache_size = 10000")  # Increase cache size
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

def initialize_database(db_name="products.db"):
    """
    Creates (if not exists) the SQLite database and the products table.
    Also adds new columns if they don't exist.
    """
    try:
        conn = get_database_connection(db_name)
        cursor = conn.cursor()

        # Create products table if it doesn't exist
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

                -- Current price
                price REAL,
                lastUpdated TEXT,
                price_change_percentage REAL,

                -- Alcohol & Volume
                volume REAL,
                alcoholPercentage REAL,

                -- APK (ml ethanol per krona)
                apk REAL
            )
            """
        )

        # Add indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_apk ON products(apk)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_price ON products(price)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON products(categoryLevel1, categoryLevel2)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_country ON products(country)")

        # Add price_change_percentage column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN price_change_percentage REAL DEFAULT 0.0")
        except sqlite3.OperationalError:
            # Column already exists, ignore the error
            pass
        
        # Create price history table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                productId TEXT,
                price REAL,
                timestamp TEXT,
                FOREIGN KEY (productId) REFERENCES products(productId)
            )
            """
        )
        
        # Add index for price history
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_history_product ON price_history(productId)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_history_timestamp ON price_history(timestamp)")
        
        conn.commit()
        logger.info("Database initialized successfully")
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise
    finally:
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


def format_timestamp():
    """
    Returns current timestamp in a query-friendly format: YYYY-MM-DD HH:MM:SS
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def insert_new_product(cursor, prod):
    """
    Inserts a new product into the database.
    """
    p_id = prod.get("productId")
    current_price = prod.get("price") or 0.0
    lastUpdated = format_timestamp()
    launch_date_str = format_launch_date(prod)
    volume_ml = prod.get("volume") or 0.0
    abv_pct = prod.get("alcoholPercentage") or 0.0
    apk_value = None
    if current_price > 0:
        ml_ethanol = volume_ml * (abv_pct / 100.0)
        apk_value = round(ml_ethanol / current_price, 2)

    # For new products, price change is 0% (first record)
    price_change_percentage = 0.0

    # Record initial price in history
    cursor.execute(
        """
        INSERT INTO price_history (productId, price, timestamp)
        VALUES (?, ?, ?)
        """,
        (p_id, current_price, lastUpdated)
    )

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
            lastUpdated,
            price_change_percentage,
            volume,
            alcoholPercentage,
            apk
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            lastUpdated,
            price_change_percentage,
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

    lastUpdated = format_timestamp()
    volume_ml = prod.get("volume") or 0.0
    abv_pct = prod.get("alcoholPercentage") or 0.0
    apk_value = None
    if new_price_api > 0:
        ml_ethanol = volume_ml * (abv_pct / 100.0)
        apk_value = round(ml_ethanol / new_price_api, 2)
    launch_date_str = format_launch_date(prod)
    
    # Get the first (earliest) price from price history
    cursor.execute("""
        SELECT price 
        FROM price_history 
        WHERE productId = ?
        ORDER BY timestamp ASC
        LIMIT 1
    """, (p_id,))
    first_price_result = cursor.fetchone()
    first_price = first_price_result[0] if first_price_result else new_price_api
    
    # Calculate price change percentage from first recorded price
    price_change_percentage = round(((new_price_api - first_price) / first_price) * 100, 1)
    
    # Record the price change in history
    cursor.execute(
        """
        INSERT INTO price_history (productId, price, timestamp)
        VALUES (?, ?, ?)
        """,
        (p_id, new_price_api, lastUpdated)
    )
    
    cursor.execute(
        """
        UPDATE products
        SET
            price = ?,
            lastUpdated = ?,
            price_change_percentage = ?,
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
            lastUpdated,
            price_change_percentage,
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
    changes_log.append(f"Updated product {p_id} (price: {current_price_db} -> {new_price_api}, change: {price_change_percentage}%)")


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


def batch_insert_products(products: list, db_name="products.db"):
    """
    Batch insert/update products for better performance.
    """
    if not products:
        return
        
    try:
        conn = get_database_connection(db_name)
        cursor = conn.cursor()
        
        # Prepare batch operations
        insert_sql = """
            INSERT OR REPLACE INTO products (
                productId, productNumber, productNumberShort, productNameBold, 
                productNameThin, producerName, supplierName, categoryLevel1, 
                categoryLevel2, categoryLevel3, country, productLaunchDate,
                isTemporaryOutOfStock, isCompletelyOutOfStock, price, lastUpdated,
                price_change_percentage, volume, alcoholPercentage, apk
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        history_sql = """
            INSERT INTO price_history (productId, price, timestamp)
            VALUES (?, ?, ?)
        """
        
        batch_data = []
        history_data = []
        current_time = format_timestamp()
        
        for prod in products:
            p_id = prod.get("productId")
            if not p_id:
                continue
                
            current_price = prod.get("price") or 0.0
            volume_ml = prod.get("volume") or 0.0
            abv_pct = prod.get("alcoholPercentage") or 0.0
            apk_value = None
            if current_price > 0:
                ml_ethanol = volume_ml * (abv_pct / 100.0)
                apk_value = round(ml_ethanol / current_price, 2)
                
            launch_date_str = format_launch_date(prod)
            
            # Calculate price change percentage from first recorded price
            price_change_percentage = 0.0
            
            # Get the first (earliest) price from price history
            cursor.execute("""
                SELECT price 
                FROM price_history 
                WHERE productId = ?
                ORDER BY timestamp ASC
                LIMIT 1
            """, (p_id,))
            first_price_result = cursor.fetchone()
            
            if first_price_result:
                first_price = first_price_result[0]
                if first_price and first_price > 0:
                    price_change_percentage = round(((current_price - first_price) / first_price) * 100, 1)
            
            batch_data.append((
                p_id, prod.get("productNumber"), prod.get("productNumberShort"),
                prod.get("productNameBold"), prod.get("productNameThin"),
                prod.get("producerName"), prod.get("supplierName"),
                prod.get("categoryLevel1"), prod.get("categoryLevel2"),
                prod.get("categoryLevel3"), prod.get("country"), launch_date_str,
                prod.get("isTemporaryOutOfStock"), prod.get("isCompletelyOutOfStock"),
                current_price, current_time, price_change_percentage, volume_ml, abv_pct, apk_value
            ))
            
            history_data.append((p_id, current_price, current_time))
        
        # Execute batch operations
        if batch_data:
            cursor.executemany(insert_sql, batch_data)
            
        if history_data:
            cursor.executemany(history_sql, history_data)
            
        conn.commit()
        logger.info(f"Batch processed {len(batch_data)} products")
        
    except sqlite3.Error as e:
        logger.error(f"Batch insert error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def make_api_request(session: Session, url: str, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """
    Makes an API request with retry logic and proper error handling.
    
    Args:
        session: Requests session object
        url: API endpoint URL
        headers: Request headers
        
    Returns:
        JSON response data or None if failed
    """
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Making API request to {url} (attempt {attempt + 1}/{MAX_RETRIES})")
            response = session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f"API request failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                logger.error(f"All API request attempts failed for {url}")
                return None
        except Exception as e:
            logger.error(f"Unexpected error during API request: {e}")
            return None
    return None


def fetch_products_from_api():
    """
    Fetches all products from the Systembolaget API and updates the SQLite database.
    Displays a progress bar and, at the end, prints a summary of all changes.
    """
    db_name = "products.db"
    initialize_database(db_name)
    processed_products = 0
    failed_requests = 0

    # Get the initial count from the database.
    total_in_db = get_product_count(db_name)
    
    try:
        with Session() as session:
            headers = {"Ocp-Apim-Subscription-Key": api_key}
            
            # Get first page to determine total pages
            first_page_data = make_api_request(session, f"{api_url}?page=1&size=30&sortBy=Score&sortDirection=Ascending", headers)
            if not first_page_data:
                logger.error("Failed to fetch first page from API")
                return
                
            total_pages = first_page_data['metadata']['totalPages']
            logger.info(f"Total pages to process: {total_pages}")

            # If the database was empty, estimate total count from the API.
            if total_in_db == 0:
                total_in_db = 30 * total_pages

            # Process first page.
            conn = sqlite3.connect(db_name)
            try:
                for prod in first_page_data["products"]:
                    insert_or_update_product(conn, prod)
                    processed_products += 1
                    current_total = get_product_count(db_name)
                    print_progress_bar(processed_products, current_total)
            except Exception as e:
                logger.error(f"Error processing first page: {e}")
            finally:
                conn.close()

            # Process remaining pages.
            for page in range(2, total_pages + 1):
                page_data = make_api_request(session, f"{api_url}?page={page}&size=30&sortBy=Score&sortDirection=Ascending", headers)
                if not page_data:
                    failed_requests += 1
                    logger.warning(f"Failed to fetch page {page}")
                    continue
                    
                products_on_page = page_data.get("products", [])
                conn = sqlite3.connect(db_name)
                try:
                    for prod in products_on_page:
                        insert_or_update_product(conn, prod)
                        processed_products += 1
                        current_total = get_product_count(db_name)
                        print_progress_bar(processed_products, current_total)
                except Exception as e:
                    logger.error(f"Error processing page {page}: {e}")
                finally:
                    conn.close()

    except Exception as e:
        logger.error(f"Critical error during API processing: {e}")
        return

    # Finish progress bar line.
    print("\n\nProduct data fetched/updated in SQLite database.")

    # Print a summary of all changes.
    print("\nSummary of changes:")
    if changes_log:
        for change in changes_log:
            print(change)
    else:
        print("No changes made.")
        
    if failed_requests > 0:
        logger.warning(f"Failed to fetch {failed_requests} pages out of {total_pages}")
    
    logger.info(f"Processing completed. Processed {processed_products} products.")


if __name__ == "__main__":
    fetch_products_from_api()
