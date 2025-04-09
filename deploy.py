import sqlite3
from datetime import datetime

def generate_html():
    """
    Generates a static HTML file with the product data from the database.
    """
    # Connect to the database
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    # Query all products
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
    products = cursor.fetchall()
    conn.close()

    # Generate the HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Systemet</title>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.min.css">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
        table.dataTable thead th,
        table.dataTable thead td {{
            border-bottom: 1px solid #ddd;
        }}
        .last-updated {{
            font-size: 0.8em;
            color: #666;
            margin-bottom: 20px;
        }}
        .price-up {{
            color: red;
        }}
        .price-down {{
            color: green;
        }}
    </style>
</head>
<body>
    <h1>Systemet</h1>
    <div class="last-updated">Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
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

    # Add product rows
    for product in products:
        price_change = product[6]  # price_change_percentage
        price_change_class = "price-up" if price_change > 0 else "price-down" if price_change < 0 else ""
        price_change_text = f"{price_change:+.1f}%" if price_change != 0 else "0%"
        
        html_content += f"""            <tr>
                <td><a href="https://systembolaget.se/{product[0]}" target="_blank">{product[0]}</a></td>
                <td>{product[1]}</td>
                <td>{product[2]}</td>
                <td>{product[3]}</td>
                <td>{product[4]}</td>
                <td>{product[5]}</td>
                <td class="{price_change_class}">{price_change_text}</td>
                <td>{product[7]}</td>
                <td>{product[8]}</td>
                <td>{product[9]}</td>
                <td>{product[10]}</td>
                <td>{product[11]}</td>
                <td>{product[12]}</td>
                <td>{product[13]}</td>
            </tr>
"""

    # Close the HTML content
    html_content += """        </tbody>
    </table>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
    <script>
        $(document).ready(function() {
            $('#productsTable').DataTable({
                pageLength: 25,
                order: [[4, "desc"]],  // Sort by APK column in descending order
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.13.4/i18n/sv.json'
                }
            });
        });
    </script>
</body>
</html>"""

    # Write the HTML content to index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == "__main__":
    generate_html()
    print("Website generated successfully!") 