import requests
import json
from typing import Any, Dict

API_URL = "https://api-systembolaget.azure-api.net/sb-api-ecommerce/v1"

# Örebro store mappings
OREBRO_STORES = {
    "1802": "Marieberg",
    "1804": "Tybblekullen", 
    "1801": "Kungsgatan",
    "1803": "Eurostop"
}
def get_header():
    return {
      'authority': 'api-systembolaget.azure-api.net',
      'accept': '*/*',
      'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,sv;q=0.7',
      'access-control-allow-origin': '*',
      'cache-control': 'no-cache',
      'content-type': 'application/json',
      'ocp-apim-subscription-key': 'cfc702aed3094c86b92d6d4ff7a54c84',
      'origin': 'https://www.systembolaget.se',
      'pragma': 'no-cache',
      'referer': 'https://www.systembolaget.se/',
      'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"macOS"',
      'sec-fetch-dest': 'empty',
      'sec-fetch-mode': 'cors',
      'sec-fetch-site': 'cross-site',
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    }

def find_products(page=1, query=""):
    params = {"page": page, "sortBy": "Score"}
    if query:
      params["textQuery"] = query
    return requests.get(
        f'{API_URL}/productsearch/search', 
        headers=get_header(),
        params=params
    ).json()

def list_products():
    return requests.get(
        f'{API_URL}/product', 
        headers=get_header()
    ).json()

def find_stores(search_string):
    return requests.get(
        f'{API_URL}/sitesearch/store', 
        headers=get_header(),
        params={
            "q": search_string
        }
    ).json()

def list_stores():
    return requests.get(
        f'{API_URL}/site/stores', 
        headers=get_header()
    ).json()

def get_store(store_id):
    return requests.get(
        f'{API_URL}/site/store/{store_id}', 
        headers=get_header()
    ).json()

def get_stockbalance(store_id, product_id):
    return requests.get(
        f'{API_URL}/stockbalance/store/{store_id}/{product_id}',
        headers=get_header()
    ).json()

def get_stockbalance_2(store_id, product_id):
    return requests.get(
        f'{API_URL}/stockbalance/store',
        headers=get_header(),
        params={
            "ProductId": product_id,
            "StoreId": store_id
        }
    ).json()

def find_stores_with_product_in_stock(product_id):
    return requests.get(
        f'{API_URL}/site/stores/{product_id}',
        headers=get_header(),
    ).json()


def display_json(data: Any, title: str = ""):
    """Display JSON data in a formatted way"""
    if title:
        print(f"\n{'='*50}")
        print(f"{title}")
        print(f"{'='*50}")
    
    if isinstance(data, dict):
        if 'error' in data or 'message' in data:
            print("Error:", data.get('error', data.get('message', 'Unknown error')))
        else:
            print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))


def get_user_input(prompt: str, input_type: type = str, default=None):
    """Get user input with type validation"""
    while True:
        try:
            if default is not None:
                user_input = input(f"{prompt} (default: {default}): ").strip()
                if not user_input:
                    return default
            else:
                user_input = input(f"{prompt}: ").strip()
            
            if input_type == str:
                return user_input
            elif input_type == int:
                return int(user_input)
            elif input_type == float:
                return float(user_input)
            else:
                return input_type(user_input)
        except ValueError:
            print(f"Invalid input. Please enter a valid {input_type.__name__}.")


def menu_find_products():
    """Menu function for finding products"""
    print("\n--- Find Products ---")
    query = get_user_input("Enter search query (optional)", str, "")
    page = get_user_input("Enter page number", int, 1)
    
    try:
        result = find_products(page, query)
        display_json(result, f"Search Results for '{query}' (Page {page})")
    except Exception as e:
        print(f"Error: {e}")


def menu_list_products():
    """Menu function for listing all products"""
    print("\n--- List All Products ---")
    
    try:
        result = list_products()
        display_json(result, "All Products")
    except Exception as e:
        print(f"Error: {e}")


def menu_find_stores():
    """Menu function for finding stores"""
    print("\n--- Find Stores ---")
    search_string = get_user_input("Enter store search string")
    
    try:
        result = find_stores(search_string)
        display_json(result, f"Stores matching '{search_string}'")
    except Exception as e:
        print(f"Error: {e}")


def menu_list_stores():
    """Menu function for listing all stores"""
    print("\n--- List All Stores ---")
    
    try:
        result = list_stores()
        display_json(result, "All Stores")
    except Exception as e:
        print(f"Error: {e}")


def menu_get_store():
    """Menu function for getting specific store"""
    print("\n--- Get Store Details ---")
    store_id = get_user_input("Enter store ID")
    
    try:
        result = get_store(store_id)
        display_json(result, f"Store Details for ID: {store_id}")
    except Exception as e:
        print(f"Error: {e}")


def menu_get_stockbalance():
    """Menu function for getting stock balance"""
    print("\n--- Get Stock Balance ---")
    store_id = get_user_input("Enter store ID")
    product_id = get_user_input("Enter product ID")
    
    try:
        result = get_stockbalance(store_id, product_id)
        display_json(result, f"Stock Balance for Store {store_id}, Product {product_id}")
    except Exception as e:
        print(f"Error: {e}")


def menu_get_stockbalance_2():
    """Menu function for getting stock balance (alternative method)"""
    print("\n--- Get Stock Balance (Method 2) ---")
    store_id = get_user_input("Enter store ID")
    product_id = get_user_input("Enter product ID")
    
    try:
        result = get_stockbalance_2(store_id, product_id)
        display_json(result, f"Stock Balance (Method 2) for Store {store_id}, Product {product_id}")
    except Exception as e:
        print(f"Error: {e}")


def menu_find_stores_with_product():
    """Menu function for finding stores with product in stock"""
    print("\n--- Find Stores with Product in Stock ---")
    product_id = get_user_input("Enter product ID")
    
    try:
        result = find_stores_with_product_in_stock(product_id)
        display_json(result, f"Stores with Product {product_id} in Stock")
    except Exception as e:
        print(f"Error: {e}")


def format_opening_hours(store_data):
    """Format opening hours for a store in a readable way - showing only today's hours"""
    from datetime import datetime
    
    # Get store ID and use constant mapping for Örebro stores
    site_id = store_data.get('siteId', '')
    store_name = OREBRO_STORES.get(site_id, 
                                   store_data.get('alias') or 
                                   store_data.get('displayName') or 
                                   store_data.get('name') or 
                                   'Unknown Store')
    
    opening_hours = store_data.get('openingHours', [])
    if opening_hours:
        # Get today's date in the format used by the API
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Find today's opening hours
        today_hours = None
        for hour in opening_hours:
            hour_date = hour.get('date', '')[:10]  # Extract just the date part
            if hour_date == today:
                today_hours = hour
                break
        
        if today_hours:
            open_from = today_hours.get('openFrom', '')
            open_to = today_hours.get('openTo', '')
            reason = today_hours.get('reason')
            
            if reason == '-':
                print(f"🏪 {store_name}")
                print(f"🕒 Today ({today}): Closed")
            else:
                print(f"🏪 {store_name}")
                print(f"🕒 Today ({today}): {open_from} - {open_to}")
        else:
            print(f"🏪 {store_name}")
            print(f"🕒 Today ({today}): No hours found")
    else:
        print(f"🏪 {store_name}")
        print("🕒 No opening hours available")


def menu_orebro_opening_hours():
    """Menu function for Örebro opening hours"""
    print("\n--- Örebro Opening Hours ---")
    orebro_store_ids = ["1803", "1801", "1804", "1802"]
    
    print("Fetching opening hours for Örebro stores...")
    print("="*60)
    
    all_stores_data = []
    
    for store_id in orebro_store_ids:
        try:
            print(f"Fetching data for store {store_id}...")
            store_data = get_store(store_id)
            
            if store_data and not ('error' in store_data or 'message' in store_data):
                all_stores_data.append(store_data)
            else:
                print(f"❌ Could not fetch data for store {store_id}")
                # Debug: show what we got
                if store_data:
                    print(f"Debug - API response: {json.dumps(store_data, indent=2)[:200]}...")
                
        except Exception as e:
            print(f"❌ Error fetching store {store_id}: {e}")
    
    if all_stores_data:
        print("\n" + "="*60)
        print("📅 ÖREBRO STORES OPENING HOURS")
        print("="*60)
        
        for store_data in all_stores_data:
            format_opening_hours(store_data)
    else:
        print("❌ No store data could be retrieved")


def show_menu():
    """Display the main menu"""
    print("\n" + "="*60)
    print("           SYSTEMBOLAGET API MENU")
    print("="*60)
    print("1.  Find Products")
    print("2.  List All Products")
    print("3.  Find Stores")
    print("4.  List All Stores")
    print("5.  Get Store Details")
    print("6.  Get Stock Balance")
    print("7.  Get Stock Balance (Method 2)")
    print("8.  Find Stores with Product in Stock")
    print("9.  Örebro Opening Hours")
    print("10. Exit")
    print("="*60)


def main():
    """Main program loop"""
    print("Welcome to Systembolaget API Explorer!")
    
    while True:
        show_menu()
        choice = get_user_input("\nEnter your choice (1-10)", int)
        
        if choice == 1:
            menu_find_products()
        elif choice == 2:
            menu_list_products()
        elif choice == 3:
            menu_find_stores()
        elif choice == 4:
            menu_list_stores()
        elif choice == 5:
            menu_get_store()
        elif choice == 6:
            menu_get_stockbalance()
        elif choice == 7:
            menu_get_stockbalance_2()
        elif choice == 8:
            menu_find_stores_with_product()
        elif choice == 9:
            menu_orebro_opening_hours()
        elif choice == 10:
            print("\nThank you for using Systembolaget API Explorer!")
            break
        else:
            print("Invalid choice. Please enter a number between 1-10.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
