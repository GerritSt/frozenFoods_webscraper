# Frozen Foods Multi-Retailer Web Scraper

A comprehensive Python-based web scraping system for collecting frozen food product data from multiple South African retailers.

## 🎯 Features

- **Multi-Retailer Support**: Scrapes Shoprite, Checkers, Pick n Pay, and Makro
- **Comprehensive Data Collection**: Extracts 20+ product fields including prices, dimensions, weights, and more
- **Smart Pagination**: Automatically handles multi-page category listings
- **Data Normalization**: Cleans and standardizes all collected data
- **Multiple Export Formats**: Saves to both CSV and Excel formats
- **Robust Error Handling**: Continues scraping even if individual products fail
- **Detailed Logging**: Tracks progress and issues throughout the scraping process
- **Configurable**: Easy to adjust settings like headless mode and page limits

## 📁 Project Structure

```
Webscraper/
│
├── scrapers/                    # Retailer-specific scrapers
│   ├── __init__.py
│   ├── base_scraper.py         # Base class with common functionality
│   ├── shoprite_scraper.py     # Shoprite implementation
│   ├── checkers_scraper.py     # Checkers implementation
│   ├── pnp_scraper.py          # Pick n Pay implementation
│   └── makro_scraper.py        # Makro implementation
│
├── utils/                       # Utility modules
│   ├── __init__.py
│   ├── normalizer.py           # Data cleaning and normalization
│   ├── exporter.py             # CSV/Excel export functionality
│   └── parser.py               # HTML parsing helpers
│
├── data/                        # Output directory
│   ├── raw/                    # Raw scraped data (optional)
│   └── processed/              # Cleaned, exported data
│
├── main.py                      # Main orchestrator script
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or download the project**

2. **Navigate to the project directory**

   ```cmd
   cd "c:\Users\gerri\Documents\besigheid\Work experience\Automation Arcitects\Webscraper"
   ```

3. **Create a virtual environment (recommended)**

   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

4. **Install dependencies**

   ```cmd
   pip install -r requirements.txt
   ```

5. **Install Playwright browsers**
   ```cmd
   python -m playwright install
   ```

## 📊 Data Fields Collected

The scraper collects the following fields for each product:

| Field                | Description                     |
| -------------------- | ------------------------------- |
| `product_id`         | Unique product identifier       |
| `product_name`       | Full product name               |
| `description`        | Product description             |
| `brand`              | Brand name                      |
| `price`              | Current price (cleaned)         |
| `price_per_unit`     | Price per unit (e.g., per kg)   |
| `size_weight_volume` | Size/weight/volume information  |
| `unit_of_measure`    | Unit of measurement             |
| `barcode`            | Product barcode/EAN             |
| `width`              | Product width                   |
| `height`             | Product height                  |
| `depth`              | Product depth                   |
| `length`             | Product length                  |
| `gross_weight`       | Gross weight                    |
| `net_weight`         | Net weight                      |
| `category`           | Product category (Frozen Foods) |
| `department`         | Subcategory/department          |
| `product_url`        | Direct link to product page     |
| `retailer`           | Retailer name                   |
| `scrape_date`        | Date/time of scraping           |

## 🎮 Usage

### Basic Usage

Run the scraper with default settings:

```cmd
python main.py
```

### Configuration

Edit `main.py` to customize behavior:

```python
# Configuration
HEADLESS = True   # Set to False to see browser while scraping
MAX_PAGES = 2     # Set to None to scrape all pages, or limit for testing
```

### Update Category URLs

Before running, update the category URLs in `main.py` with actual retailer URLs:

```python
self.category_urls = {
    'Shoprite': 'https://www.shoprite.co.za/frozen-foods',
    'Checkers': 'https://www.checkers.co.za/frozen',
    'PicknPay': 'https://www.pnp.co.za/frozen-foods',
    'Makro': 'https://www.makro.co.za/frozen'
}
```

### Customize Selectors

Each retailer scraper contains CSS selectors that may need adjustment based on actual website structure. Update these in the respective scraper files:

```python
# In shoprite_scraper.py (similar for other retailers)
self.product_card_selector = ".product-card"
self.next_button_selector = ".pagination-next"
self.product_link_selector = "a.product-link"
```

## 📤 Output

The scraper generates three files in the `data/processed/` directory:

1. **Combined CSV**: All products from all retailers in one file

   - `frozen_foods_combined_YYYYMMDD_HHMMSS.csv`

2. **Combined Excel**: All products in a single Excel sheet

   - `frozen_foods_combined_YYYYMMDD_HHMMSS.xlsx`

3. **Multi-Sheet Excel**: Separate sheet for each retailer
   - `frozen_foods_by_retailer_YYYYMMDD_HHMMSS.xlsx`

## 🔧 Customization

### Adding a New Retailer

1. Create a new scraper file in `scrapers/` (e.g., `woolworths_scraper.py`)
2. Inherit from `BaseScraper`
3. Implement required methods: `_has_next_page()`, `_go_to_next_page()`, `scrape_category()`, `extract_product_details()`
4. Add to `main.py`:

   ```python
   from scrapers.woolworths_scraper import WoolworthsScraper

   self.scrapers['Woolworths'] = WoolworthsScraper(headless=headless)
   self.category_urls['Woolworths'] = 'URL_HERE'
   ```

### Adjusting Request Delays

To avoid rate limiting, adjust delays in `base_scraper.py`:

```python
self.min_delay = 1.5  # Minimum delay (seconds)
self.max_delay = 3.0  # Maximum delay (seconds)
```

## 🐛 Troubleshooting

### Common Issues

1. **"No module named playwright"**

   - Solution: Run `pip install -r requirements.txt`

2. **"Executable doesn't exist" error**

   - Solution: Run `python -m playwright install`

3. **Timeout errors**

   - Increase timeout in `base_scraper.py`: `self.timeout = 30000` (milliseconds)

4. **Selectors not finding elements**
   - Inspect the actual website structure
   - Update CSS selectors in the respective scraper file

### Debugging

Set `HEADLESS = False` in `main.py` to watch the browser in action.

Check log files generated in the project directory for detailed error information.

## ⚠️ Legal and Ethical Considerations

- **Respect robots.txt**: Check each retailer's robots.txt file
- **Rate limiting**: Built-in delays prevent server overload
- **Terms of Service**: Review each retailer's terms before scraping
- **Personal use**: This tool is for educational/research purposes
- **Data privacy**: Don't scrape or store personal information

## 📝 Logging

The scraper creates detailed logs:

- Console output (real-time progress)
- Log file: `scraper_log_YYYYMMDD_HHMMSS.log`

## 🔒 Best Practices

1. **Test incrementally**: Use `MAX_PAGES = 1` for initial testing
2. **Respect rate limits**: Don't decrease delay times excessively
3. **Monitor execution**: Watch for patterns of failures
4. **Update selectors regularly**: Websites change frequently
5. **Back up data**: Export files regularly

## 📈 Performance

- **Speed**: ~2-5 seconds per product (with delays)
- **Memory**: Efficient with streaming pagination
- **Reliability**: Automatic retry logic and error handling

## 🤝 Contributing

To improve this scraper:

1. Update selectors for accuracy
2. Add error handling for edge cases
3. Enhance data normalization rules
4. Optimize performance

## 📄 License

This project is for educational purposes. Ensure compliance with all applicable laws and terms of service.

## 📞 Support

For issues or questions:

- Check log files for error details
- Review website structure changes
- Verify network connectivity

---

**Happy Scraping! 🎉**
