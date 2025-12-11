import html
import json
from datetime import datetime, timedelta
from typing import Dict, Any
import untappd
import time

# Constants
APK_HIGH_THRESHOLD = 0.8
APK_MEDIUM_THRESHOLD = 0.6
DATE_RANGE_DAYS = 14
PAST_DATE_RANGE_DAYS = 14

# File paths
BEERS_JSON_PATH = "data/beers.json"
UPCOMING_LAUNCHES_HTML_PATH = "docs/index.html"

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


def calculate_apk(beer: Dict[str, Any]) -> float:
    """Calculate Alcohol Per Krona (ml pure alcohol per krona)"""
    if not beer.get('price') or beer['price'] <= 0:
        return 0
    if not beer.get('alcoholPercentage') or not beer.get('volume'):
        return 0
    return (beer['alcoholPercentage'] * beer['volume'] / 100) / beer['price']






def generate_beer_card(beer: Dict[str, Any]) -> str:
    """Generate HTML for a single beer card"""
    # Use pre-calculated APK value
    apk = beer['apk']
    
    # Determine APK class for coloring
    apk_class = "medium" # default
    if apk >= APK_HIGH_THRESHOLD:
        apk_class = "high"
    elif apk < APK_MEDIUM_THRESHOLD:
        apk_class = "low"
    
    # Format beer info
    name_bold = beer.get('productNameBold', '')
    name_thin = beer.get('productNameThin', '')
    name = html.escape(f"{name_bold} {name_thin}".strip() or "Namnlös öl")
    product_number = html.escape(str(beer.get('productNumber', 'N/A')))
    product_id = beer.get('productId', '')
    price = beer.get('price', 0)
    
    # Specs
    alcohol = beer.get('alcoholPercentage', 0)
    volume_text = beer.get('volumeText', '')
    
    # Category (Simplified for card)
    cat2 = beer.get('categoryLevel2') or ''
    cat3 = beer.get('categoryLevel3') or ''
    # Prefer Cat3 (Style) if available, else Cat2 (Type)
    display_category = html.escape(cat3 if cat3 else cat2)
    
    # URLs
    sys_url = f"{SYSTEMBOLAGET_BASE_URL}/{beer.get('productNumber')}" if product_number != 'N/A' else SYSTEMBOLAGET_BASE_URL
    img_url = f"{SYSTEMBOLAGET_IMAGE_BASE_URL}/{product_id}/{product_id}_400.webp" if product_id else ""
    
    # Untappd
    untappd_data = beer.get('untappd')
    untappd_badge = ""
    rating_val = 0.0
    
    if untappd_data:
        rating_val = untappd_data.get('rating_score', 0)
        bid = untappd_data.get('bid')
        count = untappd_data.get('rating_count', 0)
        
        if rating_val > 0:
            count_str = f"{count/1000:.1f}k" if count >= 1000 else str(count)
            untappd_badge = f'''
            <a href="https://untappd.com/beer/{bid}" target="_blank" rel="noopener" class="badge-untappd" onclick="event.stopPropagation();">
                <img src="untappd_16x16.png" class="untappd-icon" alt="U">
                <span>{rating_val:.2f}</span> <span style="opacity:0.7; font-weight:400">({count_str})</span>
            </a>'''

    # Parent ID placeholder (filled by loop)
    parent_id = beer.get('parent_id', '')

    return f"""
        <div class="beer-card" 
             data-category2="{html.escape(cat2)}" 
             data-apk="{apk:.2f}"
             data-price="{price:.2f}"
             data-rating="{rating_val:.2f}"
             data-parent-id="{parent_id}">
             
            {untappd_badge}
            <div class="badge-apk {apk_class}">APK {apk:.2f}</div>
            
            <a href="{sys_url}" target="_blank" rel="noopener" class="card-link">
                <div class="image-container">
                    <img src="{img_url}" alt="{name}" class="beer-image" loading="lazy" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                    <div class="beer-image-placeholder" style="display: none;">🍺</div>
                </div>
                
                <div class="card-content">
                    <div class="beer-category">{display_category}</div>
                    <div class="beer-name" title="{name}">{name}</div>
                    
                    <div class="product-meta">
                        <div class="price-row">
                            <span class="price">{price:.2f} kr</span>
                        </div>
                        <div class="specs">
                            <span>{alcohol}%</span> • 
                            <span>{volume_text}</span> •
                            <span>#{product_number}</span>
                        </div>
                    </div>
                </div>
            </a>
        </div>
    """


def generate_html_header(today: datetime, two_weeks_forward: datetime, categories: list[str]) -> str:
    """Generate the HTML document header with CSS"""
    
    category_options = '\n'.join([f'<option value="{html.escape(cat)}">{cat}</option>' for cat in categories])
    
    return f"""<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Systemet - Kommande ölsläpp ({today.date()} — {two_weeks_forward.date()})</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🍺</text></svg>">
    <link rel="stylesheet" href="styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <div class="header-content">
            <div class="header-branding">
                <h1>Systemet — Kommande Ölsläpp</h1>
                <div class="date-range">{today.date()} — {two_weeks_forward.date()}</div>
            </div>

            <div class="filter-panel">
                <div class="filter-group">
                    <label class="filter-label">Kategori</label>
                    <select id="category-select" class="filter-select" onchange="window.filterBeers()">
                        <option value="">Alla kategorier</option>
                        {category_options}
                    </select>
                </div>

                <div class="filter-group">
                    <label class="filter-label">APK Filter</label>
                    <select id="apk-select" class="filter-select" onchange="window.filterBeers()">
                        <option value="all">Alla Nivåer</option>
                        <option value="over_2">APK &gt; 2.0 (Topp)</option>
                        <option value="1.5_2">1.5 - 2.0 (Bra)</option>
                        <option value="1_1.5">1.0 - 1.5 (Ok)</option>
                        <option value="under_1">Under 1.0 (Låg)</option>
                    </select>
                </div>

                <div class="filter-group">
                    <label class="filter-label">Sortering</label>
                    <select id="sort-select" class="filter-select" onchange="window.sortBeers()">
                        <option value="date">Standard</option>
                        <option value="rating_desc">Betyg (Högst)</option>
                        <option value="apk_desc">APK (Högst)</option>
                        <option value="price_asc">Pris (Lägst)</option>
                    </select>
                </div>
            </div>
        </div>
    </header>

    <div class="container">
"""


def generate_html_footer() -> str:
    """Generate the HTML document footer"""
    return f"""
        <footer>
            <div class="footer-info">
                Genererad {datetime.now().strftime('%Y-%m-%d %H:%M')} <br>
                APK = Alkohol per krona (ml ren alkohol/kr)
            </div>
        </footer>
    </div>
    <script src="script.js"></script>
</body>
</html>
"""


def filter_upcoming_launches() -> None:
    """
    Filter beers with productLaunchDate from today to two weeks forward.
    Save the results to a tidy file with essential information.
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
    for i, beer in enumerate(beers):
        if "productLaunchDate" in beer and beer["productLaunchDate"]:
            try:
                # Parse launch date (format: "2025-09-01T00:00:00")
                launch_date = datetime.strptime(beer["productLaunchDate"], LAUNCH_DATE_FORMAT)
                
                # Check if launch date is within our range
                if two_weeks_back <= launch_date <= two_weeks_forward:
                    # Extract essential fields
                    filtered_beer = {
                        "productId": beer.get("productId"),
                        "productNumber": beer.get("productNumber"),
                        "productNameBold": beer.get("productNameBold"),
                        "productNameThin": beer.get("productNameThin"),
                        "productLaunchDate": beer.get("productLaunchDate"),
                        "price": beer.get("price"),
                        "volume": beer.get("volume"),
                        "volumeText": beer.get("volumeText"),
                        "alcoholPercentage": beer.get("alcoholPercentage"),
                        "country": beer.get("country"),
                        "producerName": beer.get("producerName"),
                        "categoryLevel1": beer.get("categoryLevel1"),
                        "categoryLevel2": beer.get("categoryLevel2"),
                        "categoryLevel3": beer.get("categoryLevel3"),
                        "assortmentText": beer.get("assortmentText"),
                        "isWebLaunch": beer.get("isWebLaunch", False),
                        "taste": beer.get("taste"),
                        "usage": beer.get("usage"),
                    }
                    
                    upcoming_beers.append(filtered_beer)
                    
            except ValueError:
                # Skip if date format is invalid
                continue
    
    # Sort by launch date
    upcoming_beers.sort(key=lambda x: x["productLaunchDate"])
    
    # Calculate and store APK for each beer once
    for beer in upcoming_beers:
        beer['apk'] = calculate_apk(beer)
    
    print(f"Found {len(upcoming_beers)} beers launching in the period (past 2 weeks + future 2 weeks)")

    # Enrich with Untappd data for these specific beers
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
        
        # Check if we already have data
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
            
        # Rate limit
        time.sleep(0.1)

    print(f"\n✓ Untappd enrichment complete. New matches: {untappd_updates}")
    
    # Save mapping with new updates
    if untappd_updates > 0:
        with open(mapping_file, "w", encoding="utf-8") as f:
            json.dump(untappd_mapping, f, indent=2, ensure_ascii=False)
    
    # Generate HTML
    if upcoming_beers:
        # Group beers by date
        beers_by_date = {}
        for beer in upcoming_beers:
            launch_date = datetime.strptime(beer["productLaunchDate"], LAUNCH_DATE_FORMAT).date()
            if launch_date not in beers_by_date:
                beers_by_date[launch_date] = []
            beers_by_date[launch_date].append(beer)
        
        # Sort beers within each date by APK (highest first)
        for launch_date in beers_by_date:
            beers_by_date[launch_date].sort(
                key=lambda beer: beer['apk'],
                reverse=True
            )
        
        # Collect unique categories for the dropdown
        categories_set = set()
        for beer in upcoming_beers:
            cat = beer.get("categoryLevel2")
            if cat:
                categories_set.add(cat)
        sorted_categories = sorted(list(categories_set))
        
        # Create an HTML file
        html_file = UPCOMING_LAUNCHES_HTML_PATH
        with open(html_file, "w", encoding="utf-8") as f:
            # Write HTML header with server-side categories
            f.write(generate_html_header(today, two_weeks_forward, sorted_categories))
            
            # Use Swedish weekday names from constants
            
            # Split dates into past and future
            sorted_dates = sorted(beers_by_date.keys())
            past_dates = [d for d in sorted_dates if d < today.date()]
            future_dates = [d for d in sorted_dates if d >= today.date()]
            
            # --- Past Releases Accordion ---
            if past_dates:
                f.write(f"""
        <div class="past-releases-header" onclick="togglePastReleases()">
            <span>Tidigare släpp ({min(past_dates)} till {max(past_dates)})</span>
            <span class="accordion-icon">▼</span>
        </div>
        <div id="past-releases-container" style="display: none;">
""")
                for launch_date in past_dates:
                    weekday_english = launch_date.strftime('%A')
                    weekday_swedish = SWEDISH_WEEKDAYS.get(weekday_english, weekday_english)
                    date_str = launch_date.strftime('%Y-%m-%d')
                    list_id = f"list-{date_str}"
                    
                    f.write(f"""
            <div class="date-section past-release" data-date="{date_str}">
                <div class="date-header">
                    📅 {date_str} ({weekday_swedish})
                    <span class="beer-count">{len(beers_by_date[launch_date])} öl</span>
                </div>
                <div class="beer-list" id="{list_id}">
""")
                    for beer in beers_by_date[launch_date]:
                        beer['parent_id'] = list_id
                        f.write(generate_beer_card(beer))
                    f.write("            </div></div>")
                
                f.write("        </div>") # End accordion container
                
            # --- Upcoming Releases ---
            for launch_date in future_dates:
                weekday_english = launch_date.strftime('%A')
                weekday_swedish = SWEDISH_WEEKDAYS.get(weekday_english, weekday_english)
                date_str = launch_date.strftime('%Y-%m-%d')
                list_id = f"list-{date_str}"
                
                f.write(f"""
        <div class="date-section" data-date="{date_str}">
            <div class="date-header">
                📅 {date_str} ({weekday_swedish})
                <span class="beer-count">{len(beers_by_date[launch_date])} öl</span>
            </div>
            <div class="beer-list" id="{list_id}">
""")
                for beer in beers_by_date[launch_date]:
                    beer['parent_id'] = list_id
                    f.write(generate_beer_card(beer))
                    
                f.write("""
            </div>
        </div>
""")
            
            # Global container for sorting
            f.write('<div id="global-beer-list" class="beer-list" style="display:none;"></div>')
            
            f.write("    </div>") # Close container
            f.write("""
""")
            f.write(generate_html_footer())
        
        print(f"✓ Saved HTML to {html_file}")
    else:
        print("No upcoming launches found in the specified period.")


if __name__ == "__main__":
    filter_upcoming_launches()

