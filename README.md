# Systemet Price Tracker

A Python-based tool that tracks and displays product prices from Systembolaget (the Swedish alcohol retail monopoly). The tool fetches product data, stores it in a SQLite database, and generates a web interface to display the information.

## Features

- Fetches product data from Systembolaget's API
- Tracks price changes over time
- Calculates APK (Alcohol Per Krona) for value comparison
- Shows price change history with percentage changes
- Displays products in a sortable, searchable table
- Color-coded price changes (red for increases, green for decreases)

## Requirements

- Python 3.11 or higher
- Required Python packages (see `requirements.txt`):
  - requests
  - beautifulsoup4
  - bs4

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/systemet.git
cd systemet
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Updating the Database

To update the product database with the latest information:

```bash
python main.py
```

This will:
- Fetch the latest product data from Systembolaget
- Update the SQLite database
- Track price changes
- Calculate price change percentages

### Generating the Website

To generate the static website:

```bash
python deploy.py
```

This will:
- Read data from the database
- Generate a static HTML file (`index.html`)
- Include all products with their current prices and price changes

### Viewing the Results

Open `index.html` in your web browser to see:
- All products in a sortable table
- Current prices and price changes
- APK values for value comparison
- Links to product pages on Systembolaget's website

## Data Structure

### Products Table
Stores current product information including:
- Basic product details (name, number, producer, etc.)
- Current price
- Price change percentage
- Alcohol content and volume
- APK value

### Price History Table
Tracks all price changes with:
- Product ID
- Price at the time
- Timestamp of the change

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0) license. This means you are free to:

- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:
- Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.

See the [LICENSE](LICENSE) file for full details. 