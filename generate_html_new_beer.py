import html
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import untappd
import time
import jinja2
import os

# Constants
APK_HIGH_THRESHOLD = 0.8
APK_MEDIUM_THRESHOLD = 0.6
DATE_RANGE_DAYS = 14
PAST_DATE_RANGE_DAYS = 14

# File paths
BEERS_JSON_PATH = "data/beers.json"
UPCOMING_LAUNCHES_HTML_PATH = "docs/index.html"
TEMPLATE_DIR = "templates"
TEMPLATE_FILE = "index.html"

# Date format
LAUNCH_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

# URL patterns
SYSTEMBOLAGET_BASE_URL = "https://www.systembolaget.se"
SYSTEMBOLAGET_IMAGE_BASE_URL = "https://product-cdn.systembolaget.se/productimages"

# Swedish weekday names
SWEDISH_WEEKDAYS = {
    'Monday': 'Måndag',
    'Tuesday': 'Tisdag',
    'Wednesday': 'Onsdag',
    'Thursday': 'Torsdag',
    'Friday': 'Fredag',
    'Saturday': 'Lördag',
    'Sunday': 'Söndag'
}

SWEDISH_MONTHS = {
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'Maj', 6: 'Jun',
    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Okt', 11: 'Nov', 12: 'Dec'
}


def calculate_apk(beer: Dict[str, Any]) -> float:
    """Calculate Alcohol Per Krona (ml pure alcohol per krona)"""
    if not beer.get('price') or beer['price'] <= 0:
        return 0
    if not beer.get('alcoholPercentage') or not beer.get('volume'):
        return 0
    return (beer['alcoholPercentage'] * beer['volume'] / 100) / beer['price']


def get_apk_class(apk: float) -> str:
    """Determine CSS class for APK value"""
    if apk >= APK_HIGH_THRESHOLD:
        return "high"
    elif apk < APK_MEDIUM_THRESHOLD:
        return "low"
    return "medium"


def prepare_beer_view_model(beer: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare a single beer dictionary for the view (template)"""
    apk = beer.get('apk', 0)
    
    # Name formatting
    name_bold = beer.get('productNameBold', '')
    name_thin = beer.get('productNameThin', '')
    name = f"{name_bold} {name_thin}".strip() or "Namnlös öl"
    
    product_number = str(beer.get('productNumber', 'N/A'))
    product_id = beer.get('productId', '')
    
    # Category
    cat2 = beer.get('categoryLevel2') or ''
    cat3 = beer.get('categoryLevel3') or ''
    display_category = cat3 if cat3 else cat2
    
    # URLs
    sys_url = f"{SYSTEMBOLAGET_BASE_URL}/{beer.get('productNumber')}" if product_number != 'N/A' else SYSTEMBOLAGET_BASE_URL
    img_url = f"{SYSTEMBOLAGET_IMAGE_BASE_URL}/{product_id}/{product_id}_400.webp" if product_id else ""
    
    return {
        "name": name,
        "productNumber": product_number,
        "productId": product_id,
        "price": beer.get('price', 0),
        "alcoholPercentage": beer.get('alcoholPercentage', 0),
        "volumeText": beer.get('volumeText', ''),
        "categoryLevel2": cat2,
        "display_category": display_category,
        "apk": apk,
        "apk_class": get_apk_class(apk),
        "sys_url": sys_url,
        "img_url": img_url,
        "untappd": beer.get('untappd'), # Pass whole dict or None
    }


def filter_upcoming_launches() -> None:
    """
    Filter beers, enrich with Untappd, and generate HTML via Jinja2 template.
    """
    # Define date range
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    two_weeks_forward = today + timedelta(days=DATE_RANGE_DAYS)
    two_weeks_back = today - timedelta(days=PAST_DATE_RANGE_DAYS)
    
    print(f"Filtering beers launching between {two_weeks_back.date()} and {two_weeks_forward.date()}")
    
    # Read beers.json
    try:
        with open(BEERS_JSON_PATH, "r", encoding="utf-8") as f:
            beers = json.load(f)
        print(f"Loaded {len(beers)} beers from {BEERS_JSON_PATH}")
    except FileNotFoundError:
        print(f"Error: {BEERS_JSON_PATH} not found!")
        return
    except Exception as e:
        print(f"Error reading {BEERS_JSON_PATH}: {e}")
        return
    
    # Filter beers by launch date
    upcoming_beers = []
    for beer in beers:
        if "productLaunchDate" in beer and beer["productLaunchDate"]:
            try:
                launch_date = datetime.strptime(beer["productLaunchDate"], LAUNCH_DATE_FORMAT)
                # Check range
                if two_weeks_back <= launch_date <= two_weeks_forward:
                    # Use the raw beer dict initially, will transform later
                    beer_copy = beer.copy()
                    beer_copy['launch_date_obj'] = launch_date # Store for sorting/grouping
                    upcoming_beers.append(beer_copy)
            except ValueError:
                continue
    
    # Sort by launch date
    upcoming_beers.sort(key=lambda x: x["productLaunchDate"])
    
    if upcoming_beers:
        min_date = upcoming_beers[0]["productLaunchDate"]
        max_date = upcoming_beers[-1]["productLaunchDate"]
        print(f"DEBUG: Found {len(upcoming_beers)} beers. First date: {min_date}, Last date: {max_date}")
        past_count = sum(1 for b in upcoming_beers if b["productLaunchDate"] < str(today))
        print(f"DEBUG: Found {past_count} past beers (before {today.date()})")
    
    # Calculate APK
    for beer in upcoming_beers:
        beer['apk'] = calculate_apk(beer)
    
    print(f"Found {len(upcoming_beers)} beers launching in the period")

    # Enrich with Untappd
    print(f"Fetching Untappd ratings for {len(upcoming_beers)} beers...")
    
    untappd_mapping = {}
    mapping_file = "data/untappd_mapping.json"
    
    try:
        with open(mapping_file, "r", encoding="utf-8") as f:
            untappd_mapping = json.load(f)
    except FileNotFoundError:
        print("No existing Untappd mapping found.")
    
    untappd_updates = 0
    for i, beer in enumerate(upcoming_beers):
        p_num = beer["productNumber"]
        
        # Check mapping
        if p_num in untappd_mapping:
            if untappd_mapping[p_num]:
                beer["untappd"] = untappd_mapping[p_num]
            continue
            
        # Construct query
        name_bold = beer.get("productNameBold") or ""
        name_thin = beer.get("productNameThin") or ""
        query = f"{name_bold} {name_thin}".strip()
        
        if not query:
            continue
            
        print(f"Searching Untappd for: {query} ({i+1}/{len(upcoming_beers)})", end="\r")
        
        # Search
        result = untappd.search_beer(query)
        untappd_mapping[p_num] = result
        untappd_updates += 1
        
        if result:
            beer["untappd"] = result
            
        time.sleep(0.1)

    print(f"\n✓ Untappd enrichment complete. New matches: {untappd_updates}")
    
    # Save mapping updates
    if untappd_updates > 0:
        with open(mapping_file, "w", encoding="utf-8") as f:
            json.dump(untappd_mapping, f, indent=2, ensure_ascii=False)
    
    if upcoming_beers:
        # Group beers by date
        beers_by_date = {}
        for beer in upcoming_beers:
            launch_date = beer['launch_date_obj'].date()
            if launch_date not in beers_by_date:
                beers_by_date[launch_date] = []
            beers_by_date[launch_date].append(beer)
        
        # Prepare Data for Template
        date_groups = []
        sorted_dates = sorted(beers_by_date.keys())
        categories_set = set()
        
        for launch_date in sorted_dates:
            group_beers_raw = beers_by_date[launch_date]
            
            # Sort by APK within date
            group_beers_raw.sort(key=lambda b: b['apk'], reverse=True)
            
            # Transform to View Models
            group_beers_view = []
            for b in group_beers_raw:
                group_beers_view.append(prepare_beer_view_model(b))
                # Collect categories
                cat = b.get("categoryLevel2")
                if cat:
                    categories_set.add(cat)
            
            # Date Formatting
            weekday_english = launch_date.strftime('%A')
            weekday_swedish = SWEDISH_WEEKDAYS.get(weekday_english, weekday_english)
            day = launch_date.day
            month = SWEDISH_MONTHS.get(launch_date.month, launch_date.strftime('%b'))
            friendly_date = f"{weekday_swedish} {day} {month}"
            date_str = launch_date.strftime('%Y-%m-%d')
            list_id = f"list-{date_str}"
            
            is_past = launch_date < today.date()
            
            date_groups.append({
                "date_obj": launch_date,
                "date_str": date_str,
                "friendly_date": friendly_date,
                "list_id": list_id,
                "is_past": is_past,
                "beers": group_beers_view
            })
            
        sorted_categories = sorted(list(categories_set))
        
        # JINJA2 RENDERING
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template(TEMPLATE_FILE)
        
        context = {
            "today": today.date(),
            "end_date": two_weeks_forward.date(),
            "categories": sorted_categories,
            "date_groups": date_groups,
            "generated_time": datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        
        rendered_html = template.render(context)
        
        with open(UPCOMING_LAUNCHES_HTML_PATH, "w", encoding="utf-8") as f:
            f.write(rendered_html)
            
        print(f"✓ Saved HTML to {UPCOMING_LAUNCHES_HTML_PATH}")

    else:
        print("No upcoming launches found in the specified period.")


if __name__ == "__main__":
    filter_upcoming_launches()

