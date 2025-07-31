"""
Utility functions for the Systemet price tracker.
"""
import sqlite3
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def get_database_connection(db_name="products.db"):
    """Get a configured database connection."""
    try:
        conn = sqlite3.connect(db_name)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

def get_price_statistics(db_name="products.db") -> Dict[str, Any]:
    """
    Get comprehensive price statistics from the database.
    
    Returns:
        Dictionary with price statistics
    """
    try:
        conn = get_database_connection(db_name)
        cursor = conn.cursor()
        
        stats = {}
        
        # Basic statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_products,
                AVG(price) as avg_price,
                MIN(price) as min_price,
                MAX(price) as max_price,
                AVG(apk) as avg_apk,
                COUNT(CASE WHEN price_change_percentage > 0 THEN 1 END) as price_increases,
                COUNT(CASE WHEN price_change_percentage < 0 THEN 1 END) as price_decreases,
                COUNT(CASE WHEN price_change_percentage = 0 THEN 1 END) as price_stable
            FROM products
        """)
        
        row = cursor.fetchone()
        if row:
            stats.update({
                'total_products': row[0],
                'avg_price': row[1] or 0,
                'min_price': row[2] or 0,
                'max_price': row[3] or 0,
                'avg_apk': row[4] or 0,
                'price_increases': row[5],
                'price_decreases': row[6],
                'price_stable': row[7]
            })
        
        # Category statistics
        cursor.execute("""
            SELECT 
                categoryLevel1,
                COUNT(*) as count,
                AVG(price) as avg_price,
                AVG(apk) as avg_apk
            FROM products 
            WHERE categoryLevel1 IS NOT NULL
            GROUP BY categoryLevel1
            ORDER BY count DESC
            LIMIT 10
        """)
        
        stats['top_categories'] = [
            {
                'category': row[0],
                'count': row[1],
                'avg_price': row[2] or 0,
                'avg_apk': row[3] or 0
            }
            for row in cursor.fetchall()
        ]
        
        # Best value products (highest APK)
        cursor.execute("""
            SELECT 
                productNameBold,
                productNameThin,
                price,
                apk,
                volume,
                alcoholPercentage
            FROM products 
            WHERE apk IS NOT NULL AND apk > 0
            ORDER BY apk DESC
            LIMIT 10
        """)
        
        stats['best_value'] = [
            {
                'name': f"{row[0]} {row[1]}".strip(),
                'price': row[2],
                'apk': row[3],
                'volume': row[4],
                'alcohol': row[5]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return stats
        
    except sqlite3.Error as e:
        logger.error(f"Error getting price statistics: {e}")
        return {}

def get_price_history(product_id: str, days: int = 30, db_name="products.db") -> List[Dict]:
    """
    Get price history for a specific product.
    
    Args:
        product_id: Product ID to get history for
        days: Number of days to look back
        db_name: Database name
        
    Returns:
        List of price history entries
    """
    try:
        conn = get_database_connection(db_name)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT price, timestamp
            FROM price_history
            WHERE productId = ? AND timestamp >= ?
            ORDER BY timestamp ASC
        """, (product_id, cutoff_date.strftime("%Y-%m-%d %H:%M:%S")))
        
        history = [
            {
                'price': row[0],
                'timestamp': row[1]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return history
        
    except sqlite3.Error as e:
        logger.error(f"Error getting price history: {e}")
        return []

def validate_product_data(product: Dict) -> Tuple[bool, List[str]]:
    """
    Validate product data from API.
    
    Args:
        product: Product data dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    required_fields = ['productId', 'productNameBold', 'price']
    for field in required_fields:
        if not product.get(field):
            errors.append(f"Missing required field: {field}")
    
    # Validate price
    price = product.get('price')
    if price is not None:
        try:
            price_float = float(price)
            if price_float < 0:
                errors.append("Price cannot be negative")
        except (ValueError, TypeError):
            errors.append("Invalid price format")
    
    # Validate volume
    volume = product.get('volume')
    if volume is not None:
        try:
            volume_float = float(volume)
            if volume_float < 0:
                errors.append("Volume cannot be negative")
        except (ValueError, TypeError):
            errors.append("Invalid volume format")
    
    # Validate alcohol percentage
    alcohol = product.get('alcoholPercentage')
    if alcohol is not None:
        try:
            alcohol_float = float(alcohol)
            if alcohol_float < 0 or alcohol_float > 100:
                errors.append("Alcohol percentage must be between 0 and 100")
        except (ValueError, TypeError):
            errors.append("Invalid alcohol percentage format")
    
    return len(errors) == 0, errors

def calculate_apk(volume_ml: float, alcohol_percentage: float, price: float) -> Optional[float]:
    """
    Calculate APK (Alcohol Per Krona) value.
    
    Args:
        volume_ml: Volume in milliliters
        alcohol_percentage: Alcohol percentage (0-100)
        price: Price in SEK
        
    Returns:
        APK value or None if calculation fails
    """
    try:
        if price <= 0:
            return None
        
        ml_ethanol = volume_ml * (alcohol_percentage / 100.0)
        apk = ml_ethanol / price
        return round(apk, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        return None

def format_currency(amount: float) -> str:
    """Format amount as Swedish currency."""
    return f"{amount:.2f} kr"

def format_percentage(amount: float) -> str:
    """Format amount as percentage."""
    return f"{amount:+.1f}%"

def get_product_by_id(product_id: str, db_name="products.db") -> Optional[Dict]:
    """
    Get a single product by ID.
    
    Args:
        product_id: Product ID to find
        db_name: Database name
        
    Returns:
        Product data dictionary or None if not found
    """
    try:
        conn = get_database_connection(db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products WHERE productId = ?", (product_id,))
        row = cursor.fetchone()
        
        if row:
            # Convert row to dictionary
            columns = [description[0] for description in cursor.description]
            product = dict(zip(columns, row))
            conn.close()
            return product
        
        conn.close()
        return None
        
    except sqlite3.Error as e:
        logger.error(f"Error getting product by ID: {e}")
        return None

def search_products(query: str, limit: int = 50, db_name="products.db") -> List[Dict]:
    """
    Search products by name or producer.
    
    Args:
        query: Search query
        limit: Maximum number of results
        db_name: Database name
        
    Returns:
        List of matching products
    """
    try:
        conn = get_database_connection(db_name)
        cursor = conn.cursor()
        
        search_pattern = f"%{query}%"
        
        cursor.execute("""
            SELECT 
                productId, productNameBold, productNameThin, 
                producerName, price, apk, volume, alcoholPercentage
            FROM products
            WHERE 
                productNameBold LIKE ? OR 
                productNameThin LIKE ? OR 
                producerName LIKE ?
            ORDER BY apk DESC
            LIMIT ?
        """, (search_pattern, search_pattern, search_pattern, limit))
        
        columns = [description[0] for description in cursor.description]
        products = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return products
        
    except sqlite3.Error as e:
        logger.error(f"Error searching products: {e}")
        return [] 