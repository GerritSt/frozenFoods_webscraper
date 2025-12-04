"""
Data Collection Script
----------------------
Scrapes product data from all retailers and saves raw data to individual Excel files.

This script:
1. Scrapes each retailer independently
2. Saves raw data to data/raw/{retailer}_raw.xlsx
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path
import pandas as pd

# Import the universal scraper and configurations
from scrapers.universal_scraper import UniversalScraper
from scrapers.retailer_config import RETAILER_CONFIGS


# Configure logging
log_filename = f'logs/scraper_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_filename)
    ]
)

logger = logging.getLogger("DataCollector")


class DataCollector:
    """
    Collects raw data from all retailers and saves to individual files.
    """
    
    def __init__(self, headless: bool = True, max_pages: int = None, max_items: int = None):
        """
        Initialize the data collector.
        
        Args:
            headless: Run browsers in headless mode
            max_pages: Maximum pages to scrape per retailer (None = all)
            max_items: Maximum items to scrape per retailer (None = all)
        """
        self.headless = headless
        self.max_pages = max_pages
        self.max_items = max_items
        
        # Ensure raw data directory exists
        self.raw_dir = Path('data/raw')
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Data Collector initialized")
        logger.info(f"Configuration: headless={headless}, max_pages={max_pages}, max_items={max_items}")
    
    def collect_from_retailer(self, retailer_name: str, config: dict) -> bool:
        """
        Scrape data from a single retailer and save to file.
        
        Args:
            retailer_name: Name of the retailer (e.g., "Shoprite")
            config: Configuration dictionary for the retailer
            
        Returns:
            True if successful, False otherwise
        """
        logger.info("\n" + "=" * 80)
        logger.info(f"COLLECTING DATA FROM: {retailer_name}")
        logger.info("=" * 80)
        
        try:
            # Create scraper instance
            scraper = UniversalScraper(
                retailer_name=retailer_name,
                config=config,
                headless=self.headless
            )
            
            # Run the scraper
            logger.info(f"Starting scrape for {retailer_name}...")
            products = scraper.run(max_pages=self.max_pages, max_items=self.max_items)
            
            # No need to truncate - scraper already respects max_items
            if not products:
                logger.warning(f"No products scraped from {retailer_name}")
                return False
            
            # Save raw data to Excel
            filename = f"{retailer_name.lower()}_raw.xlsx"
            filepath = self.raw_dir / filename
            
            # Convert to DataFrame
            df = pd.DataFrame(products)
            
            # Fill missing values with appropriate defaults
            fill_values = {
                'product_id': 'N/A',
                'barcode': 'N/A',
                'product_name': 'Unknown Product',
                'description': 'No description available',
                'brand': 'N/A',
                'price': '0.00',
                'size_weight_volume': 'N/A',
                'unit_of_measure': 'EA',
                'price_per_unit': '0.00',
                'width': 'N/A',
                'height': 'N/A',
                'depth': 'N/A',
                'length': 'N/A',
                'gross_weight': 'N/A',
                'net_weight': 'N/A',
                'category': 'Frozen Foods',
                'product_url': 'N/A',
                'retailer': retailer_name,
                'scrape_date': ''
            }
            
            # Apply fill na for each column if it exists in the DataFrame
            for column, fill_value in fill_values.items():
                if column in df.columns:
                    df[column] = df[column].fillna(fill_value)
            
            # Save to Excel
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            logger.info(f"✓ Successfully saved {len(products)} products to: {filepath}")
            logger.info(f"✓ {retailer_name} collection complete!")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to collect data from {retailer_name}: {e}", exc_info=True)
            return False
    
    def collect_all(self) -> dict:
        """
        Collect data from all retailers.
        
        Returns:
            Dictionary with results: {retailer_name: success_boolean}
        """
        logger.info("\n" + "=" * 80)
        logger.info("STARTING DATA COLLECTION FROM ALL RETAILERS")
        logger.info("=" * 80)
        logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {}
        
        for retailer_name, config in RETAILER_CONFIGS.items():
            # Only shoprite and PicknPay for testing
            if not retailer_name in ['Checkers']:
                continue
            success = self.collect_from_retailer(retailer_name, config)
            results[retailer_name] = success
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def _print_summary(self, results: dict):
        """Print summary of collection results."""
        logger.info("\n" + "=" * 80)
        logger.info("COLLECTION SUMMARY")
        logger.info("=" * 80)
        
        successful = [name for name, success in results.items() if success]
        failed = [name for name, success in results.items() if not success]
        
        logger.info(f"\nTotal Retailers: {len(results)}")
        logger.info(f"Successful: {len(successful)}")
        logger.info(f"Failed: {len(failed)}")
        
        if successful:
            logger.info("\n✓ Successfully collected from:")
            for name in successful:
                logger.info(f"  • {name}")
        
        if failed:
            logger.info("\n✗ Failed to collect from:")
            for name in failed:
                logger.info(f"  • {name}")
        
        logger.info(f"\nRaw data saved to: {self.raw_dir.absolute()}")
        logger.info("\n" + "=" * 80)
        logger.info("DATA COLLECTION COMPLETE!")
        logger.info("=" * 80)


def main():
    """Main execution function."""
    
    # Configuration
    HEADLESS = False  # Set to True for production
    MAX_PAGES = None     # Number of pages to scrape per retailer
    MAX_ITEMS = 10  # Maximum items per retailer (None = no limit)
    
    logger.info("=" * 80)
    logger.info("FROZEN FOODS DATA COLLECTION")
    logger.info("=" * 80)
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create collector and run
    collector = DataCollector(headless=HEADLESS, max_pages=MAX_PAGES, max_items=MAX_ITEMS)
    results = collector.collect_all()
    
    logger.info(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Exit with error code if any collection failed
    if not all(results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
