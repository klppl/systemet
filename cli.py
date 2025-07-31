#!/usr/bin/env python3
"""
Command-line interface for the Systemet price tracker.
"""
import argparse
import sys
import os
from datetime import datetime
from typing import Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main
import deploy
import utils
from config import get_config

def main_cli():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Systemet Price Tracker - Track alcohol prices from Systembolaget",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py update          # Update product database
  python cli.py generate        # Generate web interface
  python cli.py stats           # Show database statistics
  python cli.py search "vodka"  # Search for products
  python cli.py product 12345   # Get product details
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update product database from API')
    update_parser.add_argument('--force', action='store_true', help='Force update even if recent data exists')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate web interface')
    generate_parser.add_argument('--output', default='index.html', help='Output file name')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    stats_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for products')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=10, help='Maximum number of results')
    
    # Product command
    product_parser = subparsers.add_parser('product', help='Get product details')
    product_parser.add_argument('product_id', help='Product ID')
    product_parser.add_argument('--history', type=int, default=30, help='Days of price history to show')
    
    # Full update command
    full_parser = subparsers.add_parser('full-update', help='Update database and generate web interface')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'update':
            handle_update(args)
        elif args.command == 'generate':
            handle_generate(args)
        elif args.command == 'stats':
            handle_stats(args)
        elif args.command == 'search':
            handle_search(args)
        elif args.command == 'product':
            handle_product(args)
        elif args.command == 'full-update':
            handle_full_update(args)
        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def handle_update(args):
    """Handle the update command."""
    print("Updating product database from Systembolaget API...")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    main.fetch_products_from_api()
    
    print(f"Update completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def handle_generate(args):
    """Handle the generate command."""
    print(f"Generating web interface to {args.output}...")
    
    # Call the original generate function
    deploy.generate_html()
    
    # Move the file if a different output name was specified
    if args.output != 'index.html':
        import shutil
        shutil.move('index.html', args.output)
    
    print(f"Web interface generated successfully: {args.output}")

def handle_stats(args):
    """Handle the stats command."""
    print("Getting database statistics...")
    
    stats = utils.get_price_statistics()
    
    if args.json:
        import json
        print(json.dumps(stats, indent=2))
    else:
        print("\n=== Database Statistics ===")
        print(f"Total Products: {stats.get('total_products', 0):,}")
        print(f"Average Price: {stats.get('avg_price', 0):.2f} kr")
        print(f"Average APK: {stats.get('avg_apk', 0):.2f}")
        print(f"Price Increases: {stats.get('price_increases', 0)}")
        print(f"Price Decreases: {stats.get('price_decreases', 0)}")
        print(f"Price Stable: {stats.get('price_stable', 0)}")
        
        top_categories = stats.get('top_categories', [])
        if top_categories:
            print("\n=== Top Categories ===")
            for cat in top_categories[:5]:
                print(f"{cat['category']}: {cat['count']} products, avg price: {cat['avg_price']:.2f} kr")
        
        best_value = stats.get('best_value', [])
        if best_value:
            print("\n=== Best Value Products ===")
            for product in best_value[:5]:
                print(f"{product['name']}: {product['price']:.2f} kr (APK: {product['apk']:.2f})")

def handle_search(args):
    """Handle the search command."""
    print(f"Searching for: '{args.query}'")
    
    results = utils.search_products(args.query, args.limit)
    
    if not results:
        print("No products found.")
        return
    
    print(f"\nFound {len(results)} products:")
    print("-" * 80)
    
    for product in results:
        name = f"{product['productNameBold']} {product['productNameThin']}".strip()
        print(f"ID: {product['productId']}")
        print(f"Name: {name}")
        print(f"Producer: {product['producerName'] or 'N/A'}")
        print(f"Price: {product['price']:.2f} kr")
        print(f"APK: {product['apk']:.2f}")
        print(f"Volume: {product['volume']:.0f} ml, Alcohol: {product['alcoholPercentage']:.1f}%")
        print("-" * 80)

def handle_product(args):
    """Handle the product command."""
    print(f"Getting details for product: {args.product_id}")
    
    product = utils.get_product_by_id(args.product_id)
    
    if not product:
        print("Product not found.")
        return
    
    print("\n=== Product Details ===")
    print(f"ID: {product['productId']}")
    print(f"Name: {product['productNameBold']} {product['productNameThin']}")
    print(f"Producer: {product['producerName']}")
    print(f"Price: {product['price']:.2f} kr")
    print(f"APK: {product['apk']:.2f}")
    print(f"Volume: {product['volume']:.0f} ml")
    print(f"Alcohol: {product['alcoholPercentage']:.1f}%")
    print(f"Category: {product['categoryLevel1']} > {product['categoryLevel2']} > {product['categoryLevel3']}")
    print(f"Country: {product['country']}")
    print(f"Price Change: {product['price_change_percentage']:+.1f}%")
    print(f"Last Updated: {product['lastUpdated']}")
    
    # Get price history
    history = utils.get_price_history(args.product_id, args.history)
    
    if history:
        print(f"\n=== Price History (Last {args.history} days) ===")
        for entry in history[-10:]:  # Show last 10 entries
            print(f"{entry['timestamp']}: {entry['price']:.2f} kr")

def handle_full_update(args):
    """Handle the full-update command."""
    print("Performing full update (database + web interface)...")
    
    # Update database
    print("1. Updating database...")
    main.fetch_products_from_api()
    
    # Generate web interface
    print("2. Generating web interface...")
    deploy.generate_html()
    
    print("Full update completed successfully!")

if __name__ == "__main__":
    main_cli() 