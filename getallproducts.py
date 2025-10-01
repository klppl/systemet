import requests
import json
import os
from datetime import datetime, timedelta


def get_all_products(product_id_map):
    start_url = "https://api-extern.systembolaget.se/sb-api-ecommerce/v1/productsearch/search?size=30"
    products = []
    
    updated_products = []
    try:
        with open("data/updated.json", "r") as f:
            updated_products = json.load(f)
    except FileNotFoundError:
        print("Updated.json not found.")
    except Exception as e:
        print(f"Error with updated.json: {e}")
    
    # Calculate changedDate: yesterday if less than 10 hours ago
    now = datetime.now()
    ten_hours_ago = now - timedelta(hours=10)
    changed_date = int(ten_hours_ago.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
    
    headers = {
        "accept": "application/json",
        "access-control-allow-origin": "*",
        "ocp-apim-subscription-key": "cfc702aed3094c86b92d6d4ff7a54c84",
        "Referer": "https://www.systembolaget.se/",
    }
    
    url_parameters = [
        "&assortmentText=S%C3%A4song",
        "&assortmentText=Tillf%C3%A4lligt%20sortiment",
        "&assortmentText=Webblanseringar",
        "&assortmentText=Fast%20sortiment",
        "&assortmentText=Lokalt%20%26%20Sm%C3%A5skaligt",
        "&assortmentText=Presentartiklar",
        "&assortmentText=Ordervaror&price.max=250",
        "&assortmentText=Ordervaror&price.min=251",
    ]
    
    for url_param in url_parameters:
        url = start_url + url_param
        print(f"\nStarting: {url}")
        
        for i in range(1, 500):
            try:
                response = requests.get(f"{url}&page={i}", headers=headers)
                json_data = response.json()
                
                if i > json_data["metadata"]["nextPage"] and json_data["metadata"]["nextPage"] > 0:
                    print("Aborted, something is wrong...")
                    print(f"Last page: {json_data['metadata']['nextPage']}")
                    break
                elif json_data["metadata"]["nextPage"] == -1:
                    products.extend(json_data["products"])
                    print(f"  Page {i} - Fetched {len(json_data['products'])} products")
                    print(f"✓ Done after {i} pages")
                    break
                else:
                    products.extend(json_data["products"])
                    print(f"  Page {i} - Fetched {len(json_data['products'])} products", end="\r")
            except Exception as error:
                print(f"\nError on page {i}: {error}")
    
    new_product_num = len(products)
    
    print(f"\n{'='*60}")
    print(f"Processing {new_product_num} fetched products...")
    
    dup_count = 0
    found_ids = []
    
    # Iterate backwards to safely remove duplicates
    for i in range(len(products) - 1, -1, -1):
        product = products[i]
        
        if product["productNumber"] in found_ids:
            products.pop(i)
            dup_count += 1
            continue
        
        found_ids.append(product["productNumber"])
        
        if (product["productNumber"] in product_id_map and 
            "changedDate" in product_id_map[product["productNumber"]]):
            # Add old data
            old_product = product_id_map[product["productNumber"]]
            product["changedDate"] = old_product["changedDate"]
            product["priceHistory"] = old_product["priceHistory"]
            product["alcoholHistory"] = old_product["alcoholHistory"]
            product["soldVolume"] = old_product["soldVolume"]
            
            # Add new data
            updated = False
            reason = ""
            
            if product["price"] != old_product["price"]:
                product["priceHistory"].append({"x": changed_date, "y": product["price"]})
                updated = True
                reason = f"Priset ändrades från {old_product['price']} till {product['price']} kr."
            
            if product["alcoholPercentage"] != old_product["alcoholPercentage"]:
                product["alcoholHistory"].append({
                    "x": changed_date,
                    "y": product.get("alcoholPercentage", 0)
                })
                # updated = True
                # reason = f"Alkoholhalten ändrades från {old_product['alcoholPercentage']} till {product['alcoholPercentage']} %."
            
            if updated:
                product["changedDate"] = changed_date
                updated_products.append({
                    "id": product["productNumber"],
                    "date": changed_date,
                    "reason": reason,
                })
        else:
            product["changedDate"] = changed_date
            product["priceHistory"] = [{"x": changed_date, "y": product["price"]}]
            product["alcoholHistory"] = [
                {"x": changed_date, "y": product.get("alcoholPercentage", 0)}
            ]
            updated_products.append({
                "id": product["productNumber"],
                "date": changed_date,
                "reason": "Ny produkt.",
            })
    
    del_count = 0
    for product_id in list(product_id_map.keys()):
        if product_id not in found_ids:
            old_product = product_id_map[product_id]
            
            if "lastFound" in old_product:
                if old_product["lastFound"] + 1000 * 60 * 60 * 24 * 7 < changed_date:
                    # Product not found for a week, remove it
                    print(f"Product removed: {product_id}")
                    del_count += 1
                    continue
            else:
                old_product["lastFound"] = changed_date
                old_product["isTemporaryOutOfStock"] = True  # High chance it is
            
            products.append(old_product)
    
    print(f"\n{'='*60}")
    print(f"SUMMARY:")
    print(f"  Found: {new_product_num} products")
    print(f"  Delta: {len(found_ids) - len(product_id_map)} products")
    print(f"  Duplicates: {dup_count} products")
    print(f"  Deleted: {del_count} products")
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    print(f"\nWriting to files...")
    # Write products to file
    with open("data/products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Wrote {len(products)} products to data/products.json")
    
    # Filter products updated more than 7 days ago
    updated_products = [
        product for product in updated_products
        if product["date"] + 1000 * 60 * 60 * 24 * 7 > changed_date
    ]
    
    # Write updated products to file
    with open("data/updated.json", "w", encoding="utf-8") as f:
        json.dump(updated_products, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Wrote {len(updated_products)} updated products to data/updated.json")
    print(f"{'='*60}\n")
    
    return products


if __name__ == "__main__":
    # Example usage
    # Load existing products to create product_id_map
    product_id_map = {}
    try:
        with open("data/products.json", "r") as f:
            existing_products = json.load(f)
            product_id_map = {p["productNumber"]: p for p in existing_products}
    except FileNotFoundError:
        print("No existing products file found, starting fresh.")
    
    products = get_all_products(product_id_map)
    print(f"✓ Complete! Total products in database: {len(products)}")

