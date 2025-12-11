import requests
import json
import time
import os
from urllib.parse import quote

# Algolia Credentials for Untappd
# Updated with working credentials provided by user
APP_ID = "9WBO4RQ3HO"
API_KEY = "1d347324d67ec472bb7132c66aead485"

ALGOLIA_URL = f"https://{APP_ID}-dsn.algolia.net/1/indexes/beer/query"

# Using these as headers matches the standard Algolia usage usually, 
# although the user showed them as 'params' in their snippet, they look like headers.
# I will try them as headers first as that's cleaner API usage.
HEADERS = {
    "x-algolia-agent": "Algolia for JavaScript (3.35.1); Browser (lite)",
    "x-algolia-application-id": APP_ID,
    "x-algolia-api-key": API_KEY,
    "User-Agent": "SystemetAPK/1.0"
}

def search_beer(query):
    """
    Search for a beer on Untappd via Algolia.
    Returns the top result or None.
    """
    if not query:
        return None

    try:
        # URL encode the query to handle special characters like '&'
        encoded_query = quote(query)
        data = {
            "params": f"query={encoded_query}&hitsPerPage=1"
        }
        
        # Requests.post with json argument automatically sets Content-Type: application/json
        response = requests.post(ALGOLIA_URL, headers=HEADERS, json=data, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("hits"):
                hit = result["hits"][0]
                return {
                    "bid": hit.get("bid"),
                    "beer_name": hit.get("beer_name"),
                    "brewery_name": hit.get("brewery_name"),
                    "rating_score": hit.get("rating_score"),
                    "rating_count": hit.get("rating_count"),
                    "beer_slug": hit.get("beer_slug"),
                    "beer_label": hit.get("beer_label")
                }
        else:
            # Fallback debug print if it fails
            print(f"Untappd API Error {response.status_code}: {response.text}")

    except Exception as e:
        print(f"Error searching Untappd for '{query}': {e}")
    
    return None
