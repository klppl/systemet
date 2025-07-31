"""
Configuration settings for the Systemet price tracker.
"""
import os
from typing import Dict, Any

# API Configuration
API_BASE_URL = "https://api-extern.systembolaget.se/sb-api-ecommerce/v1/productsearch/search"
API_KEY = "cfc702aed3094c86b92d6d4ff7a54c84"
BASE_URL = "https://www.systembolaget.se"

# Database Configuration
DATABASE_NAME = "products.db"

# Request Configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
REQUEST_TIMEOUT = 30  # seconds
PAGE_SIZE = 30

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_FILE = "systemet.log"

# Web Interface Configuration
WEB_TITLE = "Systemet Price Tracker"
WEB_DESCRIPTION = "Track alcohol prices from Systembolaget"
DEFAULT_SORT_COLUMN = 4  # APK column
DEFAULT_SORT_DIRECTION = "desc"
PAGE_LENGTH = 25

# Price Change Thresholds
MIN_PRICE_CHANGE_THRESHOLD = 0.01  # Minimum price change to record
PRICE_PRECISION = 2  # Decimal places for price calculations

# Environment-specific overrides
def get_config() -> Dict[str, Any]:
    """Get configuration with environment variable overrides."""
    config = {
        'api_base_url': os.getenv('SYSTEMET_API_URL', API_BASE_URL),
        'api_key': os.getenv('SYSTEMET_API_KEY', API_KEY),
        'database_name': os.getenv('SYSTEMET_DB_NAME', DATABASE_NAME),
        'max_retries': int(os.getenv('SYSTEMET_MAX_RETRIES', MAX_RETRIES)),
        'retry_delay': int(os.getenv('SYSTEMET_RETRY_DELAY', RETRY_DELAY)),
        'request_timeout': int(os.getenv('SYSTEMET_TIMEOUT', REQUEST_TIMEOUT)),
        'page_size': int(os.getenv('SYSTEMET_PAGE_SIZE', PAGE_SIZE)),
        'log_level': os.getenv('SYSTEMET_LOG_LEVEL', LOG_LEVEL),
        'web_title': os.getenv('SYSTEMET_WEB_TITLE', WEB_TITLE),
        'page_length': int(os.getenv('SYSTEMET_PAGE_LENGTH', PAGE_LENGTH)),
    }
    return config 