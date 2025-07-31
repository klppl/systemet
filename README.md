# Systemet Price Tracker

A Python-based tool that tracks and displays product prices from Systembolaget (the Swedish alcohol retail monopoly). The tool fetches product data, stores it in a SQLite database, and generates a web interface to display the information.

## Features

- **Robust API Integration**: Fetches product data from Systembolaget's API with retry logic and error handling
- **Price Tracking**: Tracks price changes over time with comprehensive history
- **APK Calculation**: Calculates APK (Alcohol Per Krona) for value comparison
- **Modern Web Interface**: Responsive design with advanced filtering and sorting
- **Statistics Dashboard**: Real-time statistics and analytics
- **CLI Interface**: Command-line tools for database management and queries
- **Data Validation**: Comprehensive data validation and error handling
- **Performance Optimized**: Database indexing and batch processing for large datasets

## Requirements

- Python 3.11 or higher
- Required Python packages (see `requirements.txt`):
  - requests
  - beautifulsoup4
  - bs4
  - python-dateutil (optional)

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

### Command Line Interface

The application now includes a comprehensive CLI for easy management:

```bash
# Update the product database
python cli.py update

# Generate the web interface
python cli.py generate

# Show database statistics
python cli.py stats

# Search for products
python cli.py search "vodka"

# Get product details
python cli.py product 12345

# Perform full update (database + web interface)
python cli.py full-update
```

### Manual Usage

#### Updating the Database

To update the product database with the latest information:

```bash
python main.py
```

This will:
- Fetch the latest product data from Systembolaget
- Update the SQLite database with retry logic
- Track price changes with comprehensive logging
- Calculate price change percentages
- Handle errors gracefully

#### Generating the Website

To generate the static website:

```bash
python deploy.py
```

This will:
- Read data from the database
- Generate a modern, responsive HTML file (`index.html`)
- Include statistics dashboard
- Provide advanced filtering and export options

### Viewing the Results

Open `index.html` in your web browser to see:
- **Statistics Dashboard**: Overview of total products, average prices, and price changes
- **Advanced Table**: Sortable, searchable table with all products
- **Price Tracking**: Color-coded price changes (red for increases, green for decreases)
- **APK Analysis**: Value comparison with visual indicators
- **Export Options**: Copy, CSV, Excel, and print functionality
- **Responsive Design**: Works on desktop and mobile devices

## Configuration

The application supports environment variable configuration:

```bash
# API Configuration
export SYSTEMET_API_KEY="your_api_key"
export SYSTEMET_API_URL="https://api-extern.systembolaget.se/sb-api-ecommerce/v1/productsearch/search"

# Database Configuration
export SYSTEMET_DB_NAME="products.db"

# Request Configuration
export SYSTEMET_MAX_RETRIES="3"
export SYSTEMET_RETRY_DELAY="2"
export SYSTEMET_TIMEOUT="30"

# Web Interface Configuration
export SYSTEMET_WEB_TITLE="Systemet Price Tracker"
export SYSTEMET_PAGE_LENGTH="25"
```

## Data Structure

### Products Table
Stores current product information including:
- Basic product details (name, number, producer, etc.)
- Current price and price change percentage
- Alcohol content and volume
- APK value for value comparison
- Category and country information

### Price History Table
Tracks all price changes with:
- Product ID
- Price at the time
- Timestamp of the change

## Architecture Improvements

### Error Handling & Resilience
- Comprehensive logging with file and console output
- Retry logic for API requests with exponential backoff
- Graceful error handling for database operations
- Data validation for all incoming product data

### Performance Optimizations
- Database indexing for faster queries
- Batch processing for large datasets
- Connection pooling and optimized SQLite settings
- Efficient memory usage with streaming processing

### Code Quality
- Type hints throughout the codebase
- Comprehensive documentation
- Modular design with separation of concerns
- Configuration management with environment variable support

### Web Interface Enhancements
- Modern, responsive design with CSS Grid and Flexbox
- Statistics dashboard with real-time data
- Advanced filtering and search capabilities
- Export functionality (CSV, Excel, Print)
- Mobile-friendly interface
- Visual indicators for APK values and price changes

## Development

### Project Structure
```
systemet/
├── main.py          # Main data fetching and processing
├── deploy.py        # Web interface generation
├── cli.py           # Command-line interface
├── config.py        # Configuration management
├── utils.py         # Utility functions
├── url_parser.py    # URL parsing utilities
├── requirements.txt # Python dependencies
├── products.db      # SQLite database
└── index.html       # Generated web interface
```

### Adding New Features
1. Add configuration options to `config.py`
2. Implement core functionality in appropriate modules
3. Add CLI commands to `cli.py` if needed
4. Update web interface in `deploy.py` if UI changes are required
5. Add tests and update documentation

## Contributing

Feel free to submit issues and enhancement requests!

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0) license. This means you are free to:

- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:
- Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.

See the [LICENSE](LICENSE) file for full details. 