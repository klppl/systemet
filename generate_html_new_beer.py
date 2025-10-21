import html
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# Constants
APK_HIGH_THRESHOLD = 0.8
APK_MEDIUM_THRESHOLD = 0.6
DATE_RANGE_DAYS = 14

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


def get_css_styles() -> str:
    """Return the CSS styles for the HTML page"""
    return """        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(180deg, #1e8449 0%, #166534 100%);
            color: #FFD100;
            padding: 26px 20px 20px 20px;
            border-bottom: 5px solid #FFD100;
            position: relative;
            overflow: hidden;
        }
        
        .header-top {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
            gap: 3rem;
        }
        
        @media (max-width: 1024px) {
            .header-top {
                flex-direction: column;
                align-items: flex-start;
                gap: 1.5rem;
            }
            
            .header-left {
                width: 100%;
            }
            
            .header-right {
                width: 100%;
            }
        }
        
        @media (max-width: 768px) {
            .header-top {
                flex-direction: column;
                align-items: center;
                text-align: center;
            }
            
            .header-left {
                align-items: center;
            }
            
            .header-right {
                width: 100%;
            }
            
            .header-filters {
                flex-direction: column;
                align-items: center;
                gap: 1rem;
            }
            
            .header-filter-group {
                width: 100%;
                max-width: 280px;
                align-items: stretch;
            }
            
            .header-filter-select {
                width: 100%;
            }
        }
        
        @media (max-width: 480px) {
            .header {
                padding: 15px;
            }
            
            .header-title {
                font-size: 1.5em;
            }
            
            .header-subtitle {
                font-size: 0.85em;
            }
            
            .header-logo {
                max-height: 80px;
            }
        }
        
        .header-left {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .header-right {
            display: flex;
            align-items: center;
        }
        
        .header-filters {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 1.2rem;
            flex-wrap: wrap;
            background: rgba(0, 0, 0, 0.05);
            padding: 10px 20px;
            border-radius: 8px;
            margin-top: 0.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .header-title {
            font-size: 2em;
            margin: 0;
            font-weight: 700;
            text-shadow: 3px 3px 0px rgba(0,0,0,0.3), -1px -1px 0px rgba(255,255,255,0.1);
            letter-spacing: 2px;
            color: #FFD100;
        }
        
        .date-range {
            font-size: 0.95em;
            opacity: 0.95;
            font-weight: 600;
            color: #FFD100;
            margin: 0;
        }
        
        .header-filter-group {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
        }
        
        .header-filter-label {
            font-size: 0.85rem;
            color: rgba(255, 255, 255, 0.8);
            font-weight: 400;
            margin-bottom: 4px;
            padding: 0 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .filter-icon {
            opacity: 0.8;
        }
        
        .header-filter-select {
            border: 2px solid transparent;
            border-radius: 6px;
            padding: 6px 10px;
            background-color: #fff;
            color: #111;
            font-weight: 500;
            min-width: 180px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .header-filter-select:hover {
            border-color: #facc15;
            box-shadow: 0 0 6px rgba(255, 255, 0, 0.3), 0 2px 8px rgba(250, 204, 21, 0.2);
        }
        
        .header-filter-select:focus {
            outline: none;
            border-color: #facc15;
            box-shadow: 0 0 0 3px rgba(250, 204, 21, 0.3), 0 2px 8px rgba(250, 204, 21, 0.2);
        }
        
        .filter-container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            gap: 20px;
            align-items: flex-end;
            flex-wrap: wrap;
        }
        
        .filter-dropdowns {
            display: flex;
            gap: 12px;
            align-items: flex-end;
        }
        
        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .filter-label {
            font-size: 0.85em;
            font-weight: 600;
            color: #495057;
        }
        
        .filter-select {
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            background: white;
            font-size: 0.9em;
            color: #495057;
            min-width: 160px;
            cursor: pointer;
        }
        
        .filter-select:focus {
            outline: none;
            border-color: #006442;
            box-shadow: 0 0 0 2px rgba(0, 100, 66, 0.25);
        }
        
        .filter-actions {
            display: flex;
            gap: 8px;
            margin-left: 10px;
        }
        
        .filter-btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            font-size: 0.9em;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .filter-btn.primary {
            background: #006442;
            color: white;
        }
        
        .filter-btn.primary:hover {
            background: #004d32;
        }
        
        .filter-btn.secondary {
            background: #6c757d;
            color: white;
        }
        
        .filter-btn.secondary:hover {
            background: #5a6268;
        }
        
        .filter-results {
            margin-top: 6px;
            font-size: 0.85em;
            color: #6c757d;
        }
        
        .date-section {
            margin: 15px 40px;
        }
        
        .date-header {
            background: #006442;
            color: #FFD100;
            padding: 12px 16px;
            border-radius: 4px;
            margin-bottom: 12px;
            font-size: 1.1em;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .beer-count {
            background: #FFD100;
            color: #006442;
            padding: 2px 10px;
            border-radius: 10px;
            font-size: 0.8em;
            font-weight: 700;
        }
        
        .beer-list {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            column-gap: 18px;
            row-gap: 28px;
        }
        
        .beer-item {
            background: white;
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            display: flex;
            flex-direction: column;
            height: fit-content;
            text-decoration: none;
            color: inherit;
            cursor: pointer;
        }
        
        .beer-item.hidden {
            display: none;
        }
        
        @media (max-width: 1400px) {
            .beer-list {
                grid-template-columns: repeat(4, 1fr);
            }
        }
        
        .beer-item:hover {
            transform: translateY(-6px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.18);
            text-decoration: none;
            color: inherit;
        }
        
        .beer-item:hover .beer-name {
            color: #004d32;
        }
        
        .beer-item:active {
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.12);
        }
        
        .beer-image-container {
            width: 100%;
            height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #fafafa;
            border-bottom: 2px solid #006442;
        }
        
        .beer-image {
            max-width: 90%;
            max-height: 110px;
            object-fit: contain;
        }
        
        .beer-image-placeholder {
            width: 100%;
            height: 120px;
            background: linear-gradient(135deg, #e0e0e0 0%, #d0d0d0 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            font-size: 32px;
        }
        
        .beer-content {
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 7px;
        }
        
        .beer-name {
            font-weight: 700;
            font-size: 0.85em;
            color: #006442;
            margin-bottom: 2px;
            line-height: 1.25;
            min-height: 2.5em;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        
        .beer-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 6px;
            flex-wrap: wrap;
        }
        
        .product-number {
            color: #666;
            font-size: 0.7em;
            font-family: 'Courier New', monospace;
        }
        
        .category-info {
            color: #2b2b2b;
            font-size: 0.65em;
            font-style: italic;
            margin-top: 2px;
            line-height: 1.2;
        }
        
        .price {
            font-weight: 700;
            color: #2b2b2b;
            font-size: 0.85em;
        }
        
        .apk {
            background: #ca8a04;
            color: #fff;
            border-radius: 6px;
            padding: 2px 8px;
            font-weight: 600;
            font-size: 0.75em;
            text-align: center;
            width: 100%;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
        }
        
        .apk.high {
            background: #15803d;
            color: #fff;
        }
        
        .apk.medium {
            background: #d97706;
            color: #fff;
        }
        
        footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
            background: #f5f5f5;
        }
        
        @media (max-width: 1024px) {
            .beer-list {
                grid-template-columns: repeat(3, 1fr);
            }
        }
        
        @media (max-width: 768px) {
            .beer-list {
                grid-template-columns: repeat(2, 1fr);
            }
            
            header h1 {
                font-size: 1.8em;
            }
            
            .date-section {
                margin: 20px;
            }
        }
        
        @media (max-width: 480px) {
            .beer-list {
                grid-template-columns: 1fr;
            }
        }"""


def generate_beer_card(beer: Dict[str, Any]) -> str:
    """Generate HTML for a single beer card"""
    # Use pre-calculated APK value
    apk = beer['apk']
    
    # Determine APK class for coloring
    apk_class = ""
    if apk >= APK_HIGH_THRESHOLD:
        apk_class = "high"
    elif apk >= APK_MEDIUM_THRESHOLD:
        apk_class = "medium"
    
    # Format beer info
    name_bold = beer.get('productNameBold', '')
    name_thin = beer.get('productNameThin', '')
    name = html.escape(f"{name_bold} {name_thin}".strip() or "Namnlös öl")
    product_number = html.escape(str(beer.get('productNumber', 'N/A')))
    product_id = beer.get('productId', '')
    price = beer.get('price', 0)  # Numeric value, no escaping needed
    
    # Format category info
    category_level2 = beer.get('categoryLevel2') or ''
    category_level3 = beer.get('categoryLevel3') or ''
    category_text = ""
    if category_level2 and category_level3:
        category_text = f"{html.escape(category_level2)} • {html.escape(category_level3)}"
    elif category_level2:
        category_text = html.escape(category_level2)
    elif category_level3:
        category_text = html.escape(category_level3)
    
    # Build URLs with safe fallbacks
    if product_number != 'N/A':
        systembolaget_url = f"{SYSTEMBOLAGET_BASE_URL}/{beer.get('productNumber')}"
    else:
        systembolaget_url = SYSTEMBOLAGET_BASE_URL
        
    if product_id:
        image_url = f"{SYSTEMBOLAGET_IMAGE_BASE_URL}/{product_id}/{product_id}_400.webp"
    else:
        image_url = ""  # Will trigger the placeholder in the HTML
    
    return f"""                <a href="{systembolaget_url}" target="_blank" rel="noopener" class="beer-item" data-category2="{html.escape(category_level2)}" data-category3="{html.escape(category_level3)}" data-apk="{apk:.2f}">
                    <div class="beer-image-container">
                        <img src="{image_url}" alt="{name}" class="beer-image" loading="lazy" onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\\'beer-image-placeholder\\'>🍺</div>';">
                    </div>
                    <div class="beer-content">
                        <div class="beer-name">
                            {name}
                        </div>
                        <div class="beer-meta">
                            <span class="product-number">#{product_number}</span>
                            <span class="price">{price:.2f} kr</span>
                        </div>
                        {f'<div class="category-info">{category_text}</div>' if category_text else ''}
                        <div class="apk {apk_class}">APK: {apk:.2f}</div>
                    </div>
                </a>
"""


def generate_html_header(today: datetime, two_weeks_forward: datetime) -> str:
    """Generate the HTML document header with CSS"""
    return f"""<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ölsläpp som kommer förstöra din ekonomi - Systembolaget</title>
    <style>
{get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-top">
                <div class="header-left">
                    <h1 class="header-title">KOMMANDE ÖLSLÄPP</h1>
                    <p class="date-range">⭐ {today.date()} till {two_weeks_forward.date()} ⭐</p>
                </div>
                <div class="header-right">
                    <div class="header-filters">
                    <div class="header-filter-group">
                        <label class="header-filter-label" for="category2-filter">
                            <span class="filter-icon">🗂</span>
                            <span>Kategori:</span>
                        </label>
                        <select id="category2-filter" class="header-filter-select">
                            <option value="">Alla kategorier</option>
                        </select>
                    </div>
                    <div class="header-filter-group">
                        <label class="header-filter-label" for="category3-filter">
                            <span class="filter-icon">⚙️</span>
                            <span>Underkategori:</span>
                        </label>
                        <select id="category3-filter" class="header-filter-select">
                            <option value="">Alla kategorier</option>
                        </select>
                    </div>
                    <div class="header-filter-group">
                        <label class="header-filter-label" for="apk-filter">
                            <span class="filter-icon">🧮</span>
                            <span>APK:</span>
                        </label>
                        <select id="apk-filter" class="header-filter-select">
                            <option value="">Alla APK-värden</option>
                            <option value="0.8+">Hög APK (0.8+)</option>
                            <option value="0.6-0.8">Medium APK (0.6-0.8)</option>
                            <option value="0.4-0.6">Låg APK (0.4-0.6)</option>
                            <option value="0.2-0.4">Mycket låg APK (0.2-0.4)</option>
                            <option value="0-0.2">Minimal APK (0-0.2)</option>
                        </select>
                    </div>
                    </div>
                </div>
            </div>
            <div class="filter-results" id="filter-results"></div>
        </header>
"""


def generate_html_footer() -> str:
    """Generate the HTML document footer"""
    return f"""
        <footer>
            <p>Genererad {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | APK = Alkohol per krona (ml ren alkohol/kr)</p>
        </footer>
    </div>
    <script>
        // Extract unique categories from beer data
        function extractCategories() {{
            const beers = document.querySelectorAll('.beer-item');
            const category2Set = new Set();
            const category3Set = new Set();
            
            beers.forEach(beer => {{
                const cat2 = beer.getAttribute('data-category2');
                const cat3 = beer.getAttribute('data-category3');
                
                if (cat2 && cat2.trim()) {{
                    category2Set.add(cat2);
                }}
                if (cat3 && cat3.trim()) {{
                    category3Set.add(cat3);
                }}
            }});
            
            return {{
                category2: Array.from(category2Set).sort(),
                category3: Array.from(category3Set).sort()
            }};
        }}
        
        // Get available category3 options based on selected category2
        function getAvailableCategory3Options(selectedCategory2) {{
            const beers = document.querySelectorAll('.beer-item');
            const category3Set = new Set();
            
            beers.forEach(beer => {{
                const beerCategory2 = beer.getAttribute('data-category2') || '';
                const beerCategory3 = beer.getAttribute('data-category3') || '';
                
                // If no category2 filter or this beer matches the selected category2
                if (!selectedCategory2 || beerCategory2 === selectedCategory2) {{
                    if (beerCategory3 && beerCategory3.trim()) {{
                        category3Set.add(beerCategory3);
                    }}
                }}
            }});
            
            return Array.from(category3Set).sort();
        }}
        
        // Populate filter dropdowns
        function populateFilters() {{
            const categories = extractCategories();
            const category2Select = document.getElementById('category2-filter');
            const category3Select = document.getElementById('category3-filter');
            
            // Clear existing options except first
            category2Select.innerHTML = '<option value="">Alla kategorier</option>';
            category3Select.innerHTML = '<option value="">Alla kategorier</option>';
            
            // Add category2 options
            categories.category2.forEach(cat => {{
                const option = document.createElement('option');
                option.value = cat;
                option.textContent = cat;
                category2Select.appendChild(option);
            }});
            
            // Add all category3 options initially
            categories.category3.forEach(cat => {{
                const option = document.createElement('option');
                option.value = cat;
                option.textContent = cat;
                category3Select.appendChild(option);
            }});
        }}
        
        // Update category3 dropdown based on category2 selection
        function updateCategory3Options() {{
            const category2Select = document.getElementById('category2-filter');
            const category3Select = document.getElementById('category3-filter');
            const selectedCategory2 = category2Select.value;
            
            // Get available category3 options for the selected category2
            const availableCategory3 = getAvailableCategory3Options(selectedCategory2);
            
            // Clear existing options except first
            category3Select.innerHTML = '<option value="">Alla kategorier</option>';
            
            // Add available category3 options
            availableCategory3.forEach(cat => {{
                const option = document.createElement('option');
                option.value = cat;
                option.textContent = cat;
                category3Select.appendChild(option);
            }});
            
            // Reset category3 selection if it's no longer available
            if (selectedCategory2 && !availableCategory3.includes(category3Select.value)) {{
                category3Select.value = '';
            }}
        }}
        
        // Check if APK value matches the selected range
        function matchesApkRange(apkValue, range) {{
            if (!range) return true;
            
            const apk = parseFloat(apkValue);
            
            switch(range) {{
                case '0.8+':
                    return apk >= 0.8;
                case '0.6-0.8':
                    return apk >= 0.6 && apk < 0.8;
                case '0.4-0.6':
                    return apk >= 0.4 && apk < 0.6;
                case '0.2-0.4':
                    return apk >= 0.2 && apk < 0.4;
                case '0-0.2':
                    return apk >= 0 && apk < 0.2;
                default:
                    return true;
            }}
        }}
        
        // Filter beers based on selected categories and APK range
        function filterBeers() {{
            const category2Filter = document.getElementById('category2-filter').value;
            const category3Filter = document.getElementById('category3-filter').value;
            const apkFilter = document.getElementById('apk-filter').value;
            const beers = document.querySelectorAll('.beer-item');
            const resultsDiv = document.getElementById('filter-results');
            let visibleCount = 0;
            
            beers.forEach(beer => {{
                const beerCategory2 = beer.getAttribute('data-category2') || '';
                const beerCategory3 = beer.getAttribute('data-category3') || '';
                const beerApk = beer.getAttribute('data-apk') || '0';
                
                let showBeer = true;
                
                if (category2Filter && beerCategory2 !== category2Filter) {{
                    showBeer = false;
                }}
                
                if (category3Filter && beerCategory3 !== category3Filter) {{
                    showBeer = false;
                }}
                
                if (apkFilter && !matchesApkRange(beerApk, apkFilter)) {{
                    showBeer = false;
                }}
                
                if (showBeer) {{
                    beer.classList.remove('hidden');
                    visibleCount++;
                }} else {{
                    beer.classList.add('hidden');
                }}
            }});
            
            // Update results text
            const totalCount = beers.length;
            if (category2Filter || category3Filter || apkFilter) {{
                resultsDiv.textContent = `Visar ${{visibleCount}} av ${{totalCount}} öl`;
            }} else {{
                resultsDiv.textContent = '';
            }}
        }}
        
        // Clear all filters
        function clearFilters() {{
            document.getElementById('category2-filter').value = '';
            document.getElementById('category3-filter').value = '';
            document.getElementById('apk-filter').value = '';
            
            // Reset category3 dropdown to show all options
            updateCategory3Options();
            
            const beers = document.querySelectorAll('.beer-item');
            beers.forEach(beer => {{
                beer.classList.remove('hidden');
            }});
            
            document.getElementById('filter-results').textContent = '';
        }}
        
        // Initialize filters when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            populateFilters();
            
            // Auto-filter on dropdown change
            document.getElementById('category2-filter').addEventListener('change', function() {{
                updateCategory3Options();
                filterBeers();
            }});
            document.getElementById('category3-filter').addEventListener('change', filterBeers);
            document.getElementById('apk-filter').addEventListener('change', filterBeers);
        }});
    </script>
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
    
    print(f"Filtering beers launching between {today.date()} and {two_weeks_forward.date()}")
    
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
                if today <= launch_date <= two_weeks_forward:
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
    
    print(f"Found {len(upcoming_beers)} beers launching in the next two weeks")
    
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
        
        # Create an HTML file
        html_file = UPCOMING_LAUNCHES_HTML_PATH
        with open(html_file, "w", encoding="utf-8") as f:
            # Write HTML header
            f.write(generate_html_header(today, two_weeks_forward))
            
            # Use Swedish weekday names from constants
            
            # Iterate through dates in order
            for launch_date in sorted(beers_by_date.keys()):
                weekday_english = launch_date.strftime('%A')
                weekday_swedish = SWEDISH_WEEKDAYS.get(weekday_english, weekday_english)
                date_str = launch_date.strftime('%Y-%m-%d')
                
                f.write(f"""
        <div class="date-section">
            <div class="date-header">
                📅 {date_str} ({weekday_swedish})
                <span class="beer-count">{len(beers_by_date[launch_date])} öl</span>
            </div>
            <div class="beer-list">
""")
                
                for beer in beers_by_date[launch_date]:
                    f.write(generate_beer_card(beer))
                
                f.write("""            </div>
        </div>
""")
            
            # Write HTML footer
            f.write(generate_html_footer())
        
        print(f"✓ Saved HTML to {html_file}")
    else:
        print("No upcoming launches found in the specified period.")


if __name__ == "__main__":
    filter_upcoming_launches()

