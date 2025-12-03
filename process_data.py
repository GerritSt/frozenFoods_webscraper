"""
Data Processing Script
----------------------
Processes raw data files from data/raw/ and creates comparison tables.

This script:
1. Loads raw Excel files from data/raw/
2. Normalizes and cleans the data
3. Creates comparison tables
4. Saves processed data to data/processed/
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path
import pandas as pd
from typing import List, Dict

# Import utilities
from utils.normalizer import DataNormalizer


# Configure logging
log_filename = f'logs/processor_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_filename)
    ]
)

logger = logging.getLogger("DataProcessor")


class DataProcessor:
    """
    Processes raw retailer data into comparison tables.
    """
    
    def __init__(self):
        """Initialize the data processor."""
        self.normalizer = DataNormalizer()
        
        self.raw_dir = Path('data/raw')
        self.processed_dir = Path('data/processed')
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Data Processor initialized")
    
    def load_raw_files(self) -> Dict[str, List[Dict]]:
        """
        Load all raw Excel files from data/raw/ directory.
        
        Returns:
            Dictionary mapping retailer name to list of products
        """
        logger.info("\n" + "=" * 80)
        logger.info("LOADING RAW DATA FILES")
        logger.info("=" * 80)
        
        if not self.raw_dir.exists():
            logger.error(f"Raw data directory does not exist: {self.raw_dir}")
            return {}
        
        # Find all *_raw_*.xlsx files
        raw_files = list(self.raw_dir.glob('*_raw_*.xlsx'))
        
        if not raw_files:
            logger.warning(f"No raw data files found in {self.raw_dir}")
            return {}
        
        logger.info(f"Found {len(raw_files)} raw data file(s)")
        
        data_by_retailer = {}
        
        for filepath in raw_files:
            try:
                # Extract retailer name from filename (e.g., "shoprite_raw_20251130_123456.xlsx" -> "Shoprite")
                retailer_name = filepath.stem.split('_raw_')[0].title()
                
                logger.info(f"Loading: {filepath.name} ({retailer_name})")
                
                # Read Excel file
                df = pd.read_excel(filepath)
                
                # Convert DataFrame to list of dictionaries
                products = df.to_dict('records')
                
                data_by_retailer[retailer_name] = products
                
                logger.info(f"  ✓ Loaded {len(products)} products from {retailer_name}")
                
            except Exception as e:
                logger.error(f"  ✗ Failed to load {filepath.name}: {e}")
                continue
        
        logger.info(f"\nTotal retailers loaded: {len(data_by_retailer)}")
        
        return data_by_retailer
    
    def normalize_data(self, data_by_retailer: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """
        Normalize and clean all product data.
        
        Args:
            data_by_retailer: Raw data by retailer
            
        Returns:
            Normalized data by retailer
        """
        logger.info("\n" + "=" * 80)
        logger.info("NORMALIZING DATA")
        logger.info("=" * 80)
        
        normalized = {}
        
        for retailer, products in data_by_retailer.items():
            logger.info(f"Normalizing {retailer}...")
            
            try:
                normalized_products = [
                    self.normalizer.normalize_product_data(product)
                    for product in products
                ]
                
                normalized[retailer] = normalized_products
                logger.info(f"  ✓ Normalized {len(normalized_products)} products")
                
            except Exception as e:
                logger.error(f"  ✗ Failed to normalize {retailer}: {e}")
                normalized[retailer] = products  # Use raw data as fallback
        
        return normalized
    
    def create_comparison_table(self, data_by_retailer: Dict[str, List[Dict]]):
        """
        Create comparison tables from normalized data.
        
        Args:
            data_by_retailer: Normalized data by retailer
        """
        logger.info("\n" + "=" * 80)
        logger.info("CREATING COMPARISON TABLES")
        logger.info("=" * 80)
        
        # Combine all data
        combined_data = []
        for retailer, products in data_by_retailer.items():
            combined_data.extend(products)
        
        if not combined_data:
            logger.warning("No data to process!")
            return
        
        logger.info(f"Total products: {len(combined_data)}")
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export combined comparison table (CSV)
        csv_path = self.processed_dir / f"comparison_table_{timestamp}.csv"
        df_combined = pd.DataFrame(combined_data)
        df_combined.to_csv(csv_path, index=False, encoding='utf-8')
        logger.info(f"✓ CSV comparison table: {csv_path}")
        
        # Export combined comparison table (Excel)
        excel_path = self.processed_dir / f"comparison_table_{timestamp}.xlsx"
        df_combined.to_excel(excel_path, index=False, engine='openpyxl')
        logger.info(f"✓ Excel comparison table: {excel_path}")
        
        # Export multi-sheet Excel (one sheet per retailer)
        multi_excel_path = self.processed_dir / f"comparison_by_retailer_{timestamp}.xlsx"
        with pd.ExcelWriter(multi_excel_path, engine='openpyxl') as writer:
            for retailer, products in data_by_retailer.items():
                if products:
                    df = pd.DataFrame(products)
                    df.to_excel(writer, sheet_name=retailer, index=False)
        logger.info(f"✓ Multi-sheet comparison: {multi_excel_path}")
        
        # Print statistics
        self._print_statistics(data_by_retailer, combined_data)
    
    def _print_statistics(self, data_by_retailer: Dict[str, List[Dict]], 
                         combined_data: List[Dict]):
        """Print summary statistics."""
        logger.info("\n" + "=" * 80)
        logger.info("COMPARISON TABLE STATISTICS")
        logger.info("=" * 80)
        
        # Per-retailer counts
        logger.info("\nProducts by Retailer:")
        for retailer, products in data_by_retailer.items():
            logger.info(f"  • {retailer}: {len(products)} products")
        
        # Get detailed statistics
        df = pd.DataFrame(combined_data)
        
        logger.info(f"\nTotal Products: {len(df)}")
        logger.info(f"Unique Brands: {df['brand'].nunique() if 'brand' in df else 0}")
        
        if 'price' in df and df['price'].notna().any():
            logger.info(f"\nPrice Statistics:")
            logger.info(f"  • Average: R{df['price'].mean():.2f}")
            logger.info(f"  • Minimum: R{df['price'].min():.2f}")
            logger.info(f"  • Maximum: R{df['price'].max():.2f}")
        
        logger.info(f"\nProducts with Barcode: {df['barcode'].notna().sum() if 'barcode' in df else 0}")
        logger.info(f"Process Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def process_all(self):
        """Main processing workflow."""
        logger.info("\n" + "=" * 80)
        logger.info("STARTING DATA PROCESSING")
        logger.info("=" * 80)
        logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load raw files
        data_by_retailer = self.load_raw_files()
        
        if not data_by_retailer:
            logger.error("No data loaded. Exiting.")
            return False
        
        # Normalize data
        normalized_data = self.normalize_data(data_by_retailer)
        
        # Create comparison tables
        self.create_comparison_table(normalized_data)
        
        logger.info("\n" + "=" * 80)
        logger.info("DATA PROCESSING COMPLETE!")
        logger.info("=" * 80)
        
        return True


def main():
    """Main execution function."""
    
    logger.info("=" * 80)
    logger.info("FROZEN FOODS DATA PROCESSING")
    logger.info("=" * 80)
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create processor and run
    processor = DataProcessor()
    success = processor.process_all()
    
    logger.info(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
