import json
from datetime import datetime, timedelta

# Constants
APK_HIGH_THRESHOLD = 0.8
APK_MEDIUM_THRESHOLD = 0.6
DATE_RANGE_DAYS = 14

# File paths
BEERS_JSON_PATH = "data/beers.json"
UPCOMING_LAUNCHES_HTML_PATH = "data/upcoming_launches.html"

# Date format
LAUNCH_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

# URL patterns
SYSTEMBOLAGET_BASE_URL = "https://www.systembolaget.se"
SYSTEMBOLAGET_IMAGE_BASE_URL = "https://product-cdn.systembolaget.se/productimages"


def calculate_apk(beer):
    """Calculate Alcohol Per Krona (ml pure alcohol per krona)"""
    if beer['price'] <= 0:
        return 0
    return (beer['alcoholPercentage'] * beer['volume'] / 100) / beer['price']


def filter_upcoming_launches():
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
            f.write("""<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kommande ölsläpp - Systembolaget</title>
    <style>
        * {
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
            background: linear-gradient(90deg, #006442 0%, #008855 50%, #006442 100%);
            color: #FFD100;
            padding: 20px;
            text-align: center;
            border-bottom: 5px solid #FFD100;
            position: relative;
            overflow: hidden;
        }
        
        header::before {
            content: "🍻";
            position: absolute;
            left: 20px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 3em;
            animation: bounce 2s infinite;
        }
        
        header::after {
            content: "🎉";
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 3em;
            animation: bounce 2s infinite 1s;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(-50%); }
            50% { transform: translateY(-60%); }
        }
        
        header h1 {
            font-size: 2em;
            margin-bottom: 5px;
            font-weight: 700;
            text-shadow: 3px 3px 0px rgba(0,0,0,0.3), -1px -1px 0px rgba(255,255,255,0.1);
            letter-spacing: 2px;
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from { text-shadow: 3px 3px 0px rgba(0,0,0,0.3), 0 0 10px #FFD100; }
            to { text-shadow: 3px 3px 0px rgba(0,0,0,0.3), 0 0 20px #FFD100, 0 0 30px #FFD100; }
        }
        
        header p {
            font-size: 0.95em;
            opacity: 0.95;
            font-weight: 600;
        }
        
        .date-section {
            margin: 25px 40px;
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
            gap: 18px;
        }
        
        .beer-item {
            background: white;
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            display: flex;
            flex-direction: column;
            height: fit-content;
        }
        
        @media (max-width: 1400px) {
            .beer-list {
                grid-template-columns: repeat(4, 1fr);
            }
        }
        
        .beer-item:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
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
            color: #2b2b2b;
            margin-bottom: 2px;
            line-height: 1.25;
            min-height: 2.5em;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .beer-name a {
            color: #006442;
            text-decoration: none;
            transition: color 0.2s;
        }
        
        .beer-name a:hover {
            color: #004d32;
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
        
        .price {
            font-weight: 700;
            color: #2b2b2b;
            font-size: 0.85em;
        }
        
        .apk {
            background: #555;
            color: #ffffff;
            padding: 4px 8px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 0.75em;
            text-align: center;
            width: 100%;
        }
        
        .apk.high {
            background: #004225;
            color: #ffffff;
        }
        
        .apk.medium {
            background: #b8860b;
            color: #ffffff;
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
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>✨🍺 KOMMANDE ÖLSLÄPP 🍺✨</h1>
            <p>⭐ """ + f"{today.date()} till {two_weeks_forward.date()}" + """ ⭐</p>
        </header>
""")
            
            # Swedish weekday names
            swedish_weekdays = {
                'Monday': 'Måndag',
                'Tuesday': 'Tisdag',
                'Wednesday': 'Onsdag',
                'Thursday': 'Torsdag',
                'Friday': 'Fredag',
                'Saturday': 'Lördag',
                'Sunday': 'Söndag'
            }
            
            # Iterate through dates in order
            for launch_date in sorted(beers_by_date.keys()):
                weekday_english = launch_date.strftime('%A')
                weekday_swedish = swedish_weekdays.get(weekday_english, weekday_english)
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
                    # Use pre-calculated APK value
                    apk = beer['apk']
                    
                    # Determine APK class for coloring
                    apk_class = ""
                    if apk >= APK_HIGH_THRESHOLD:
                        apk_class = "high"
                    elif apk >= APK_MEDIUM_THRESHOLD:
                        apk_class = "medium"
                    
                    # Format beer info
                    name = f"{beer['productNameBold']} {beer['productNameThin']}"
                    systembolaget_url = f"{SYSTEMBOLAGET_BASE_URL}/{beer['productNumber']}"
                    image_url = f"{SYSTEMBOLAGET_IMAGE_BASE_URL}/{beer['productId']}/{beer['productId']}_400.webp"
                    
                    f.write(f"""                <div class="beer-item">
                    <div class="beer-image-container">
                        <img src="{image_url}" alt="{name}" class="beer-image" loading="lazy" onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\\'beer-image-placeholder\\'>🍺</div>';">
                    </div>
                    <div class="beer-content">
                        <div class="beer-name">
                            <a href="{systembolaget_url}" target="_blank" rel="noopener">{name}</a>
                        </div>
                        <div class="beer-meta">
                            <span class="product-number">#{beer['productNumber']}</span>
                            <span class="price">{beer['price']:.2f} kr</span>
                        </div>
                        <div class="apk {apk_class}">APK: {apk:.2f}</div>
                    </div>
                </div>
""")
                
                f.write("""            </div>
        </div>
""")
            
            f.write(f"""
        <footer>
            <p>Genererad {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | APK = Alkohol per krona (ml ren alkohol/kr)</p>
        </footer>
    </div>
</body>
</html>
""")
        
        print(f"✓ Saved HTML to {html_file}")
    else:
        print("No upcoming launches found in the specified period.")


if __name__ == "__main__":
    filter_upcoming_launches()

