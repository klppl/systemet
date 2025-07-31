import sqlite3
from datetime import datetime
import json
from typing import Dict, Any, List
import os

def get_database_connection(db_name="products.db"):
    """
    Creates a database connection with proper configuration.
    """
    try:
        conn = sqlite3.connect(db_name)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        raise

def get_categories():
    """Get all unique categories for pre-filtered pages."""
    conn = get_database_connection('products.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT categoryLevel1 
        FROM products 
        WHERE categoryLevel1 IS NOT NULL 
        ORDER BY categoryLevel1
    """)
    categories = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return categories

def get_products_by_category(category: str, limit: int = 50, offset: int = 0):
    """Get products for a specific category with pagination."""
    conn = get_database_connection('products.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            productNumber, 
            productNameBold, 
            productNameThin, 
            supplierName, 
            apk, 
            price, 
            price_change_percentage,
            volume, 
            alcoholPercentage, 
            categoryLevel1, 
            categoryLevel2, 
            categoryLevel3, 
            country, 
            productLaunchDate 
        FROM products
        WHERE categoryLevel1 = ?
        ORDER BY apk DESC
        LIMIT ? OFFSET ?
    """, (category, limit, offset))
    
    products = cursor.fetchall()
    conn.close()
    return products

def get_search_results(query: str, limit: int = 50):
    """Get search results for a query."""
    conn = get_database_connection('products.db')
    cursor = conn.cursor()
    
    search_pattern = f"%{query}%"
    cursor.execute("""
        SELECT 
            productNumber, 
            productNameBold, 
            productNameThin, 
            supplierName, 
            apk, 
            price, 
            price_change_percentage,
            volume, 
            alcoholPercentage, 
            categoryLevel1, 
            categoryLevel2, 
            categoryLevel3, 
            country, 
            productLaunchDate 
        FROM products
        WHERE 
            productNameBold LIKE ? OR 
            productNameThin LIKE ? OR 
            supplierName LIKE ?
        ORDER BY apk DESC
        LIMIT ?
    """, (search_pattern, search_pattern, search_pattern, limit))
    
    products = cursor.fetchall()
    conn.close()
    return products

def generate_category_page(category: str):
    """Generate a static page for a specific category."""
    products = get_products_by_category(category, limit=100)  # Show top 100 by APK
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{category} - Systemet Price Tracker</title>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.min.css">
    <style>
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.4;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            border: 1px solid #ddd;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        
        .header {{
            padding: 20px;
            border-bottom: 1px solid #ddd;
            background-color: #fafafa;
        }}
        
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 1.8em;
            font-weight: normal;
            color: #333;
        }}
        
        .nav {{
            margin-bottom: 15px;
        }}
        
        .nav a {{
            color: #333;
            text-decoration: none;
            margin-right: 15px;
        }}
        
        .nav a:hover {{
            text-decoration: underline;
        }}
        
        .dataTable {{
            width: 100% !important;
            min-width: 1500px;
        }}
        
        .dataTable thead th {{
            background: #f5f5f5;
            color: #333;
            border: 1px solid #ddd;
            padding: 8px 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.8em;
            white-space: nowrap;
        }}
        
        .dataTable tbody td {{
            border: 1px solid #eee;
            padding: 6px 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.75em;
            white-space: normal;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }}
        
        .price-up {{ color: #d32f2f; }}
        .price-down {{ color: #388e3c; }}
        .price-stable {{ color: #666; }}
        .apk-value {{ font-weight: bold; }}
        .product-link {{ color: #333; text-decoration: none; }}
        .product-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{category}</h1>
            <div class="nav">
                <a href="index.html">← Back to All Products</a>
            </div>
        </div>
        
        <div class="main-content">
            <table id="productsTable" class="display" style="width:100%">
                <thead>
                    <tr>
                        <th>Artikelnummer</th>
                        <th>Namn</th>
                        <th>Namn 2</th>
                        <th>Bryggeri</th>
                        <th>APK</th>
                        <th>Pris</th>
                        <th>Prisändring</th>
                        <th>Volym</th>
                        <th>Alkohol %</th>
                        <th>Kategori 1</th>
                        <th>Kategori 2</th>
                        <th>Kategori 3</th>
                        <th>Land</th>
                        <th>Lansering</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for product in products:
        price_change = product[6]
        apk_value = product[4]
        
        if price_change > 0:
            price_change_class = "price-up"
            price_change_text = f"+{price_change:.1f}%"
        elif price_change < 0:
            price_change_class = "price-down"
            price_change_text = f"{price_change:.1f}%"
        else:
            price_change_class = "price-stable"
            price_change_text = "0%"
        
        html_content += f"""            <tr>
                <td><a href="https://systembolaget.se/{product[0]}" target="_blank" class="product-link">{product[0]}</a></td>
                <td>{product[1] or ''}</td>
                <td>{product[2] or ''}</td>
                <td>{product[3] or ''}</td>
                <td class="apk-value">{apk_value or 'N/A'}</td>
                <td>{product[5]:.2f} kr</td>
                <td class="{price_change_class}">{price_change_text}</td>
                <td>{product[7]:.0f} ml</td>
                <td>{product[8]:.1f}%</td>
                <td>{product[9] or ''}</td>
                <td>{product[10] or ''}</td>
                <td>{product[11] or ''}</td>
                <td>{product[12] or ''}</td>
                <td>{product[13] or ''}</td>
            </tr>
"""
    
    html_content += """                </tbody>
            </table>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
    <script>
        $(document).ready(function() {
            $('#productsTable').DataTable({
                pageLength: 25,
                order: [[4, "desc"]],
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.13.4/i18n/sv.json'
                },
                columnDefs: [
                    { targets: [4], type: 'num' },
                    { targets: [5], type: 'num' },
                    { 
                        targets: [6], 
                        type: 'num',
                        render: function(data, type, row) {
                            if (type === 'display') return data;
                            return parseFloat(data.replace(/[+%]/g, ''));
                        }
                    }
                ]
            });
        });
    </script>
</body>
</html>"""
    
    # Create category directory if it doesn't exist
    os.makedirs('categories', exist_ok=True)
    
    # Write the category page
    filename = f"categories/{category.lower().replace(' ', '_').replace('&', 'and')}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filename

def generate_search_api():
    """Generate a simple search API endpoint."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search - Systemet Price Tracker</title>
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: 'Courier New', monospace; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5; 
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background-color: white; 
            border: 1px solid #ddd; 
            padding: 20px; 
        }
        .search-box { 
            width: 100%; 
            padding: 10px; 
            font-family: 'Courier New', monospace; 
            border: 1px solid #ddd; 
            margin-bottom: 20px; 
        }
        .results { margin-top: 20px; }
        .product { 
            border-bottom: 1px solid #eee; 
            padding: 10px 0; 
        }
        .product-name { font-weight: bold; }
        .product-details { color: #666; font-size: 0.9em; }
        .price-up { color: #d32f2f; }
        .price-down { color: #388e3c; }
        .nav { margin-bottom: 15px; }
        .nav a { color: #333; text-decoration: none; margin-right: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="index.html">← Back to All Products</a>
        </div>
        
        <h1>Search Products</h1>
        <input type="text" id="searchInput" class="search-box" placeholder="Search for products, breweries, or categories...">
        <div id="results" class="results"></div>
    </div>

    <script>
        const searchInput = document.getElementById('searchInput');
        const resultsDiv = document.getElementById('results');
        let searchTimeout;

        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length < 2) {
                resultsDiv.innerHTML = '';
                return;
            }
            
            searchTimeout = setTimeout(() => {
                fetch(`/api/search?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        displayResults(data);
                    })
                    .catch(error => {
                        console.error('Search error:', error);
                        resultsDiv.innerHTML = '<p>Search temporarily unavailable. Please try again.</p>';
                    });
            }, 300);
        });

        function displayResults(products) {
            if (products.length === 0) {
                resultsDiv.innerHTML = '<p>No products found.</p>';
                return;
            }
            
            const html = products.map(product => `
                <div class="product">
                    <div class="product-name">${product.productNameBold} ${product.productNameThin}</div>
                    <div class="product-details">
                        ${product.supplierName} • ${product.price} kr • APK: ${product.apk} • 
                        <span class="${product.price_change_percentage > 0 ? 'price-up' : product.price_change_percentage < 0 ? 'price-down' : ''}">
                            ${product.price_change_percentage > 0 ? '+' : ''}${product.price_change_percentage}%
                        </span>
                    </div>
                </div>
            `).join('');
            
            resultsDiv.innerHTML = html;
        }
    </script>
</body>
</html>"""
    
    with open('search.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_main_page():
    """Generate the main page with category navigation and statistics."""
    conn = get_database_connection('products.db')
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*), AVG(price), AVG(apk) FROM products")
    stats = cursor.fetchone()
    total_products, avg_price, avg_apk = stats
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE price_change_percentage > 0")
    price_increases = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE price_change_percentage < 0")
    price_decreases = cursor.fetchone()[0]
    
    # Get categories
    categories = get_categories()
    
    conn.close()
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Systemet Price Tracker</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ 
            font-family: 'Courier New', monospace; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5; 
            color: #333; 
        }}
        .container {{ 
            max-width: 1400px; 
            margin: 0 auto; 
            background-color: white; 
            border: 1px solid #ddd; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        }}
        .header {{ 
            padding: 20px; 
            border-bottom: 1px solid #ddd; 
            background-color: #fafafa; 
        }}
        .header h1 {{ 
            margin: 0 0 10px 0; 
            font-size: 1.8em; 
            font-weight: normal; 
            color: #333; 
        }}
        .stats {{ 
            display: flex; 
            flex-wrap: wrap; 
            gap: 15px; 
            margin-bottom: 20px; 
        }}
        .stat {{ 
            background-color: white; 
            border: 1px solid #ddd; 
            padding: 10px 15px; 
            font-size: 0.9em; 
        }}
        .stat-number {{ font-weight: bold; color: #333; }}
        .stat-label {{ color: #666; font-size: 0.8em; }}
        .main-content {{ padding: 20px; }}
        .categories {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 15px; 
            margin-bottom: 30px; 
        }}
        .category-card {{ 
            border: 1px solid #ddd; 
            padding: 15px; 
            text-decoration: none; 
            color: #333; 
            background-color: #fafafa; 
        }}
        .category-card:hover {{ 
            background-color: #f0f0f0; 
        }}
        .category-name {{ font-weight: bold; margin-bottom: 5px; }}
        .category-count {{ font-size: 0.8em; color: #666; }}
        .actions {{ 
            display: flex; 
            gap: 10px; 
            margin-bottom: 20px; 
        }}
        .action-btn {{ 
            padding: 10px 15px; 
            border: 1px solid #ddd; 
            background: white; 
            color: #333; 
            text-decoration: none; 
            font-family: 'Courier New', monospace; 
        }}
        .action-btn:hover {{ background: #f0f0f0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Systemet Price Tracker</h1>
            <div class="subtitle">Track alcohol prices and find the best value for money</div>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">{total_products:,}</div>
                    <div class="stat-label">Total Products</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{avg_price:.2f} kr</div>
                    <div class="stat-label">Average Price</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{avg_apk:.2f}</div>
                    <div class="stat-label">Average APK</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{price_increases}</div>
                    <div class="stat-label">Price Increases</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{price_decreases}</div>
                    <div class="stat-label">Price Decreases</div>
                </div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="actions">
                <a href="search.html" class="action-btn">🔍 Search Products</a>
                <a href="index.html" class="action-btn">📊 All Products</a>
            </div>
            
            <p>Click "All Products" to view the complete product database with sorting and filtering capabilities.</p>
        </div>
    </div>
</body>
</html>"""
    
    with open('main.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_all_products_page():
    """Generate the main page with statistics and all products."""
    conn = get_database_connection('products.db')
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*), AVG(price), AVG(apk) FROM products")
    stats = cursor.fetchone()
    total_products, avg_price, avg_apk = stats
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE price_change_percentage > 0")
    price_increases = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE price_change_percentage < 0")
    price_decreases = cursor.fetchone()[0]
    
    conn.close()
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Systemet Price Tracker</title>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.min.css">
    <style>
        * {{ box-sizing: border-box; }}
        body {{ 
            font-family: 'Courier New', monospace; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5; 
            color: #333; 
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background-color: white; 
            border: 1px solid #ddd; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
            overflow-x: auto; 
        }}
        .header {{ 
            padding: 20px; 
            border-bottom: 1px solid #ddd; 
            background-color: #fafafa; 
        }}
        .header h1 {{ 
            margin: 0 0 10px 0; 
            font-size: 1.8em; 
            font-weight: normal; 
            color: #333; 
        }}
        .header .subtitle {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 15px;
        }}
        .stats {{ 
            display: flex; 
            flex-wrap: wrap; 
            gap: 15px; 
            margin-bottom: 15px; 
        }}
        .stat {{ 
            background-color: white; 
            border: 1px solid #ddd; 
            padding: 10px 15px; 
            font-size: 0.9em; 
        }}
        .stat-number {{ font-weight: bold; color: #333; }}
        .stat-label {{ color: #666; font-size: 0.8em; }}
        .main-content {{ padding: 20px; }}
        .last-updated {{
            font-size: 0.8em;
            color: #666;
            margin-bottom: 15px;
            text-align: right;
        }}
        .dataTable {{ width: 100% !important; min-width: 1200px; }}
        .dataTable thead th {{ 
            background: #f5f5f5; 
            color: #333; 
            border: 1px solid #ddd; 
            padding: 8px 4px; 
            font-family: 'Courier New', monospace; 
            font-size: 0.8em; 
            white-space: nowrap; 
        }}
        .dataTable tbody td {{ 
            border: 1px solid #eee; 
            padding: 4px 3px; 
            font-family: 'Courier New', monospace; 
            font-size: 0.7em; 
            white-space: normal; 
            word-wrap: break-word; 
            overflow-wrap: break-word; 
        }}
        .dataTable thead th:nth-child(1) {{ width: 80px; max-width: 80px; }} /* Artikelnummer */
        .dataTable thead th:nth-child(2) {{ width: 120px; max-width: 120px; }} /* Bryggeri */
        .dataTable thead th:nth-child(3) {{ width: 200px; max-width: 200px; }} /* Namn */
        .dataTable thead th:nth-child(4) {{ width: 70px; max-width: 70px; }} /* Pris */
        .dataTable thead th:nth-child(5) {{ width: 60px; max-width: 60px; }} /* APK */
        .dataTable thead th:nth-child(6) {{ width: 80px; max-width: 80px; }} /* Prisändring */
        .dataTable thead th:nth-child(7) {{ width: 60px; max-width: 60px; }} /* Volym */
        .dataTable thead th:nth-child(8) {{ width: 70px; max-width: 70px; }} /* Alkohol % */
        .price-up {{ color: #d32f2f; }}
        .price-down {{ color: #388e3c; }}
        .price-stable {{ color: #666; }}
        .apk-value {{ font-weight: bold; }}
        .product-link {{ color: #333; text-decoration: none; }}
        .product-link:hover {{ text-decoration: underline; }}
        .filters {{
            margin-bottom: 15px;
            padding: 10px;
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 3px;
        }}
        .filter-group {{
            display: block;
            margin-bottom: 10px;
        }}
        .filter-group label {{
            font-size: 0.8em;
            color: #666;
            margin-right: 5px;
        }}
        .filter-group select {{
            font-family: 'Courier New', monospace;
            font-size: 0.8em;
            padding: 4px 8px;
            border: 1px solid #ddd;
            background-color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Systemet Price Tracker</h1>
            <div class="subtitle">Track alcohol prices and find the best value for money</div>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">{total_products:,}</div>
                    <div class="stat-label">Total Products</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{avg_price:.2f} kr</div>
                    <div class="stat-label">Average Price</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{avg_apk:.2f}</div>
                    <div class="stat-label">Average APK</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{price_increases}</div>
                    <div class="stat-label">Price Increases</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{price_decreases}</div>
                    <div class="stat-label">Price Decreases</div>
                </div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="filters">
                <div class="filter-group">
                    <label for="countryFilter">Land:</label>
                    <select id="countryFilter">
                        <option value="">Alla länder</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="category1Filter">Dryckestyp:</label>
                    <select id="category1Filter">
                        <option value="">Alla dryckestyper</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="category2Filter">Dryckesgrupp:</label>
                    <select id="category2Filter">
                        <option value="">Alla dryckesgrupper</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="category3Filter">Stil/Sort:</label>
                    <select id="category3Filter">
                        <option value="">Alla stilar/sorter</option>
                    </select>
                </div>
            </div>
            
            <div class="last-updated">
                Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            </div>
            
            <table id="productsTable" class="display" style="width:100%">
                <thead>
                    <tr>
                        <th>Artikelnummer</th>
                        <th>Bryggeri</th>
                        <th>Namn</th>
                        <th>Pris</th>
                        <th>APK</th>
                        <th>Prisändring</th>
                        <th>Volym</th>
                        <th>Alkohol %</th>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            </table>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
    <script>
        $(document).ready(function() {{
            var table = $('#productsTable').DataTable({{
                pageLength: 25,
                order: [[4, "desc"]],
                language: {{
                    url: '//cdn.datatables.net/plug-ins/1.13.4/i18n/sv.json'
                }},
                serverSide: false,
                processing: true,
                ajax: {{
                    url: 'data/products.json',
                    dataSrc: ''
                }},
                columns: [
                    {{ 
                        data: 'productNumber',
                        render: function(data, type, row) {{
                            return '<a href="https://systembolaget.se/' + data + '" target="_blank" class="product-link">' + data + '</a>';
                        }}
                    }},
                    {{ data: 'supplierName' }},
                    {{ 
                        data: null,
                        render: function(data, type, row) {{
                            var name = row.productNameBold || '';
                            var name2 = row.productNameThin || '';
                            if (name && name2) {{
                                return name + ' ' + name2;
                            }} else if (name) {{
                                return name;
                            }} else if (name2) {{
                                return name2;
                            }}
                            return '';
                        }}
                    }},
                    {{ 
                        data: 'price',
                        render: function(data) {{
                            return data.toFixed(2) + ' kr';
                        }}
                    }},
                    {{ data: 'apk', className: 'apk-value' }},
                    {{ 
                        data: 'price_change_percentage',
                        render: function(data, type, row) {{
                            if (type === 'display') {{
                                if (data > 0) return '+' + data.toFixed(1) + '%';
                                if (data < 0) return data.toFixed(1) + '%';
                                return '0%';
                            }}
                            return data;
                        }},
                        createdCell: function(td, cellData, rowData, row, col) {{
                            if (cellData > 0) {{
                                $(td).addClass('price-up');
                            }} else if (cellData < 0) {{
                                $(td).addClass('price-down');
                            }} else {{
                                $(td).addClass('price-stable');
                            }}
                        }}
                    }},
                    {{ 
                        data: 'volume',
                        render: function(data) {{
                            return data.toFixed(0) + ' ml';
                        }}
                    }},
                    {{ 
                        data: 'alcoholPercentage',
                        render: function(data) {{
                            return data.toFixed(1) + '%';
                        }}
                    }}
                ]
            }});
            
            // Global variables to store all data and current filters
            var allData = [];
            var currentFilters = {{
                country: '',
                category1: '',
                category2: '',
                category3: ''
            }};
            
            // Populate all filters after data is loaded
            table.on('xhr', function() {{
                var data = table.ajax.json();
                if (data) {{
                    allData = data;
                    populateFilters();
                }}
            }});
            
            function populateFilters() {{
                var countries = [];
                var categories1 = [];
                var categories2 = [];
                var categories3 = [];
                
                // Get filtered data based on current selections
                var filteredData = allData.filter(function(product) {{
                    if (currentFilters.country && product.country !== currentFilters.country) return false;
                    if (currentFilters.category1 && product.categoryLevel1 !== currentFilters.category1) return false;
                    if (currentFilters.category2 && product.categoryLevel2 !== currentFilters.category2) return false;
                    if (currentFilters.category3 && product.categoryLevel3 !== currentFilters.category3) return false;
                    return true;
                }});
                
                // Extract unique values from filtered data
                filteredData.forEach(function(product) {{
                    if (product.country && countries.indexOf(product.country) === -1) {{
                        countries.push(product.country);
                    }}
                    if (product.categoryLevel1 && categories1.indexOf(product.categoryLevel1) === -1) {{
                        categories1.push(product.categoryLevel1);
                    }}
                    if (product.categoryLevel2 && categories2.indexOf(product.categoryLevel2) === -1) {{
                        categories2.push(product.categoryLevel2);
                    }}
                    if (product.categoryLevel3 && categories3.indexOf(product.categoryLevel3) === -1) {{
                        categories3.push(product.categoryLevel3);
                    }}
                }});
                
                // Sort all arrays
                countries.sort();
                categories1.sort();
                categories2.sort();
                categories3.sort();
                
                // Populate country filter
                var countryFilter = $('#countryFilter');
                var currentCountry = countryFilter.val();
                countryFilter.find('option:not(:first)').remove();
                countries.forEach(function(countryName) {{
                    countryFilter.append('<option value="' + countryName + '">' + countryName + '</option>');
                }});
                if (currentCountry && countries.indexOf(currentCountry) !== -1) {{
                    countryFilter.val(currentCountry);
                }}
                
                // Populate category filters
                var category1Filter = $('#category1Filter');
                var currentCategory1 = category1Filter.val();
                category1Filter.find('option:not(:first)').remove();
                categories1.forEach(function(category) {{
                    category1Filter.append('<option value="' + category + '">' + category + '</option>');
                }});
                if (currentCategory1 && categories1.indexOf(currentCategory1) !== -1) {{
                    category1Filter.val(currentCategory1);
                }}
                
                var category2Filter = $('#category2Filter');
                var currentCategory2 = category2Filter.val();
                category2Filter.find('option:not(:first)').remove();
                categories2.forEach(function(category) {{
                    category2Filter.append('<option value="' + category + '">' + category + '</option>');
                }});
                if (currentCategory2 && categories2.indexOf(currentCategory2) !== -1) {{
                    category2Filter.val(currentCategory2);
                }}
                
                var category3Filter = $('#category3Filter');
                var currentCategory3 = category3Filter.val();
                category3Filter.find('option:not(:first)').remove();
                categories3.forEach(function(category) {{
                    category3Filter.append('<option value="' + category + '">' + category + '</option>');
                }});
                if (currentCategory3 && categories3.indexOf(currentCategory3) !== -1) {{
                    category3Filter.val(currentCategory3);
                }}
            }}
            
            function applyFilters() {{
                // Clear any existing custom filters
                $.fn.dataTable.ext.search.splice(0, $.fn.dataTable.ext.search.length);
                
                // Add custom filter
                $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {{
                    var rowData = table.row(dataIndex).data();
                    
                    if (currentFilters.country && rowData.country !== currentFilters.country) return false;
                    if (currentFilters.category1 && rowData.categoryLevel1 !== currentFilters.category1) return false;
                    if (currentFilters.category2 && rowData.categoryLevel2 !== currentFilters.category2) return false;
                    if (currentFilters.category3 && rowData.categoryLevel3 !== currentFilters.category3) return false;
                    
                    return true;
                }});
                
                table.draw();
            }}
            
            // Handle country filter
            $('#countryFilter').on('change', function() {{
                currentFilters.country = $(this).val();
                currentFilters.category1 = '';
                currentFilters.category2 = '';
                currentFilters.category3 = '';
                $('#category1Filter').val('');
                $('#category2Filter').val('');
                $('#category3Filter').val('');
                populateFilters();
                applyFilters();
            }});
            
            // Handle category1 filter
            $('#category1Filter').on('change', function() {{
                currentFilters.category1 = $(this).val();
                currentFilters.category2 = '';
                currentFilters.category3 = '';
                $('#category2Filter').val('');
                $('#category3Filter').val('');
                populateFilters();
                applyFilters();
            }});
            
            // Handle category2 filter
            $('#category2Filter').on('change', function() {{
                currentFilters.category2 = $(this).val();
                currentFilters.category3 = '';
                $('#category3Filter').val('');
                populateFilters();
                applyFilters();
            }});
            
            // Handle category3 filter
            $('#category3Filter').on('change', function() {{
                currentFilters.category3 = $(this).val();
                applyFilters();
            }});
        }});
    </script>
</body>
</html>"""
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_products_json():
    """Generate a JSON file with all products for AJAX loading."""
    conn = get_database_connection('products.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            productNumber, 
            productNameBold, 
            productNameThin, 
            supplierName, 
            apk, 
            price, 
            price_change_percentage,
            volume, 
            alcoholPercentage, 
            categoryLevel1, 
            categoryLevel2, 
            categoryLevel3, 
            country, 
            productLaunchDate 
        FROM products
        ORDER BY apk DESC
    """)
    
    products = []
    for row in cursor.fetchall():
        products.append({
            'productNumber': row[0],
            'productNameBold': row[1] or '',
            'productNameThin': row[2] or '',
            'supplierName': row[3] or '',
            'apk': row[4] or 0,
            'price': row[5] or 0,
            'price_change_percentage': row[6] or 0,
            'volume': row[7] or 0,
            'alcoholPercentage': row[8] or 0,
            'categoryLevel1': row[9] or '',
            'categoryLevel2': row[10] or '',
            'categoryLevel3': row[11] or '',
            'country': row[12] or '',
            'productLaunchDate': row[13] or ''
        })
    
    conn.close()
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Write JSON file
    with open('data/products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def main():
    """Generate the simplified static pages."""
    print("Generating simplified static pages...")
    
    # Generate products JSON for AJAX loading
    print("1. Generating products JSON...")
    generate_products_json()
    
    # Generate main page with statistics and all products
    print("2. Generating main page with statistics and all products...")
    generate_all_products_page()
    
    print("Done! Generated files:")
    print("- data/products.json (AJAX data)")
    print("- index.html (main page with statistics and all products)")

if __name__ == "__main__":
    main() 