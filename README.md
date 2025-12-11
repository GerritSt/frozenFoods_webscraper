# Frozen Foods Multi-Retailer Web Scraper

A Python-based web scraping system for collecting frozen food product data from multiple South African retailers (Shoprite, Checkers, Pick n Pay).

## Overview

This project automates the collection of frozen food product information from South African retailer websites. It uses browser automation to navigate product listings, extract detailed product information, normalize the data, and export results to Excel and CSV formats.

**Note on Makro**: After investigation, Makro's frozen foods section was found to be unsuitable for scraping. Their search functionality returns predominantly non-food "Frozen" branded merchandise (Disney products, accessories), with actual frozen food products scattered across multiple subcategories without a dedicated frozen foods landing page.

## Technology Stack

- **Python 3.8+**: Core programming language
- **Playwright**: Browser automation and page interaction
- **BeautifulSoup4**: HTML parsing and data extraction
- **Pandas**: Data manipulation and export
- **Logging**: Built-in Python logging for tracking and debugging

## Project Structure

```
frozenFoods_webscraper/
├── scrapers/
│   ├── universal_scraper.py    # Main scraper with retailer-specific logic
│   ├── retailer_config.py      # Configuration for each retailer (URLs, selectors)
│   └── __pycache__/
├── utils/
│   ├── normalizer.py           # Data cleaning and normalization
│   └── __pycache__/
├── data/
│   ├── raw/                    # Raw scraped data output (Excel)
│   └── processed/              # Cleaned, normalized data output (Excel/CSV)
├── logs/                       # Execution logs
├── collect_data.py             # Main execution script
├── process_data.py             # Data processing and normalization script
├── run_pipeline.py             # End-to-end pipeline orchestrator
├── requirements.txt            # Python dependencies
└── README.md
```

## Process Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     START: run_pipeline.py                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────┐
│              STEP 1: collect_data.py                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Initialize UniversalScraper with retailer configs  │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                        │
│                   ▼                                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │ For each retailer (Shoprite, Checkers, PicknPay):  │    │
│  │                                                    │    │
│  │  1. Launch Playwright browser                      │    │
│  │  2. Navigate to frozen foods section URL           │    │
│  │  3. Handle retailer-specific navigation:           │    │
│  │     - Shoprite/PicknPay: Standard pagination       │    │
│  │     - Checkers: Subsection-based navigation        │    │
│  │  4. Collect product URLs from all pages            │    │
│  │  5. Visit each product page                        │    │
│  │  6. Extract product details:                       │    │
│  │     - Name, brand, price, price_per_unit           │    │
│  │     - Size, weight, unit of measure                │    │
│  │     - Product ID from URL                          │    │
│  │     - Category, retailer, timestamp                │    │
│  │  7. Store in pandas DataFrame                      │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                        │
│                   ▼                                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Export raw data to Excel:                          │    │
│  │  data/raw/{retailer}_raw.xlsx                      │    │
│  └────────────────────────────────────────────────────┘    │
└───────────────────────────┬────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────┐
│              STEP 2: process_data.py                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Load raw data from all retailer Excel files        │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                        │
│                   ▼                                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Apply normalization (utils/normalizer.py):         │    │
│  │  - Clean product names and brands                  │    │
│  │  - Parse and standardize prices                    │    │
│  │  - Extract and normalize weights/volumes           │    │
│  │  - Convert to base units (g or ml)                 │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                        │
│                   ▼                                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Match similar products using RapidFuzz:            │    │
│  │  - Normalize product names for comparison          │    │
│  │  - Use fuzzy matching (token_sort_ratio)           │    │
│  │  - Apply similarity threshold (80%)                │    │
│  │  - Group products from different retailers         │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                        │
│                   ▼                                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Create comparison table with columns:              │    │
│  │  - Product name, brand, size                       │    │
│  │  - {Retailer}_price                                │    │
│  │  - {Retailer}_price_per_unit                       │    │
│  │  - {Retailer}_url                                  │    │
│  │  (One set of columns per retailer)                 │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                        │
│                   ▼                                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Export to Excel:                                   │    │
│  │  data/processed/price_comparison.xlsx              │    │
│  └────────────────────────────────────────────────────┘    │
└───────────────────────────┬────────────────────────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │     DONE     │
                     └──────────────┘
```

## Data Fields Collected

- product_id
- product_name
- brand
- price
- price_per_unit
- size_weight_volume
- unit_of_measure
- category
- department
- product_url
- retailer
- scrape_date

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. Clone or download the project

2. Install dependencies:

   ```cmd
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:
   ```cmd
   python -m playwright install
   ```

## Running the Scraper

### Full Pipeline

Execute the complete data collection and processing pipeline:

```cmd
python run_pipeline.py
```

### Individual Steps

**Data Collection Only:**

```cmd
python collect_data.py
```

**Data Processing Only:**

```cmd
python process_data.py
```

### Configuration

Edit retailer configurations in `scrapers/retailer_config.py`:

- Update URLs for frozen foods sections
- Adjust CSS selectors if websites change
- Modify pagination settings

## Output

The scraper generates files in the `data/` directory:

**Raw Data:**

- `data/raw/shoprite_raw.xlsx`
- `data/raw/checkers_raw.xlsx`
- `data/raw/picknpay_raw.xlsx`

**Processed Data:**

- `data/processed/price_comparison.xlsx` - Comparison table showing matched products across retailers

**Logs:**

- `logs/scraper_YYYYMMDD_HHMMSS.log` - Collection logs
- `logs/processor_log_YYYYMMDD_HHMMSS.log` - Processing logs

## Output File Structure

The `price_comparison.xlsx` file contains the following columns:

- `product_name` - Product name
- `brand` - Product brand
- `size` - Product size/weight/volume
- `{Retailer}_price` - Price at each retailer (e.g., Shoprite_price, Checkers_price)
- `{Retailer}_price_per_unit` - Price per unit at each retailer
- `{Retailer}_url` - Product page URL at each retailer

Only products found at 2 or more retailers are included in the comparison table.

## Requirements

See `requirements.txt` for full dependency list. Key requirements:

- playwright>=1.40.0
- beautifulsoup4>=4.12.0
- pandas>=2.0.0
- openpyxl>=3.1.0
- rapidfuzz>=3.0.0
