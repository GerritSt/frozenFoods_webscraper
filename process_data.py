"""
Data Processing Script
----------------------
Processes raw data files from data/raw/ and creates a comparison table.

This script:
1. Loads raw Excel files from data/raw/
2. Normalizes and cleans the data
3. Matches similar products across retailers using fuzzy matching
4. Creates a comparison table showing prices across retailers
5. Saves to data/processed/price_comparison.xlsx
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path
import pandas as pd
from typing import List, Dict, Tuple
from rapidfuzz import fuzz, process

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
    Processes raw retailer data into a price comparison table.
    """
    
    def __init__(self, similarity_threshold: int = 80):
        """
        Initialize the data processor.
        
        Args:
            similarity_threshold: Minimum similarity score (0-100) to consider products as matching
        """
        self.normalizer = DataNormalizer()
        self.similarity_threshold = similarity_threshold
        
        self.raw_dir = Path('data/raw')
        self.processed_dir = Path('data/processed')
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Data Processor initialized (similarity threshold: {similarity_threshold}%)")
    
    def load_raw_files(self) -> pd.DataFrame:
        """
        Load all raw Excel files from data/raw/ directory.
        
        Returns:
            Combined DataFrame with all products from all retailers
        """
        logger.info("\n" + "=" * 80)
        logger.info("LOADING RAW DATA FILES")
        logger.info("=" * 80)
        
        if not self.raw_dir.exists():
            logger.error(f"Raw data directory does not exist: {self.raw_dir}")
            return pd.DataFrame()
        
        # Find all *_raw*.xlsx files
        raw_files = list(self.raw_dir.glob('*_raw*.xlsx'))
        
        if not raw_files:
            logger.warning(f"No raw data files found in {self.raw_dir}")
            return pd.DataFrame()
        
        logger.info(f"Found {len(raw_files)} raw data file(s)")
        
        all_products = []
        
        for filepath in raw_files:
            try:
                # Extract retailer name
                retailer_name = filepath.stem.split('_raw')[0].title()
                
                logger.info(f"Loading: {filepath.name} ({retailer_name})")
                
                # Read Excel file
                df = pd.read_excel(filepath)
                df['retailer'] = retailer_name
                
                all_products.append(df)
                
                logger.info(f"  ✓ Loaded {len(df)} products from {retailer_name}")
                
            except Exception as e:
                logger.error(f"  ✗ Failed to load {filepath.name}: {e}")
                continue
        
        if not all_products:
            return pd.DataFrame()
        
        # Combine all DataFrames
        combined_df = pd.concat(all_products, ignore_index=True)
        logger.info(f"\nTotal products loaded: {len(combined_df)}")
        
        return combined_df
    
    def normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize and clean all product data.
        
        Args:
            df: Raw product DataFrame
            
        Returns:
            Normalized DataFrame
        """
        logger.info("\n" + "=" * 80)
        logger.info("NORMALIZING DATA")
        logger.info("=" * 80)
        
        normalized_products = []
        
        for _, product in df.iterrows():
            try:
                normalized = self.normalizer.normalize_product(product.to_dict())
                normalized_products.append(normalized)
            except Exception as e:
                logger.warning(f"  ⚠ Failed to normalize product: {e}")
                continue
        
        normalized_df = pd.DataFrame(normalized_products)
        logger.info(f"  ✓ Normalized {len(normalized_df)} products")
        
        return normalized_df
    
    def find_similar_products(self, df: pd.DataFrame) -> List[Dict]:
        """
        Find similar products across retailers using fuzzy matching.
        
        Args:
            df: Normalized product DataFrame
            
        Returns:
            List of product groups (similar products from different retailers)
        """
        logger.info("\n" + "=" * 80)
        logger.info("MATCHING SIMILAR PRODUCTS")
        logger.info("=" * 80)
        
        # Group products by retailer
        retailers = df['retailer'].unique()
        logger.info(f"Retailers: {', '.join(retailers)}")
        
        # Use first retailer as base
        base_retailer = retailers[0]
        base_products = df[df['retailer'] == base_retailer].copy()
        
        logger.info(f"Using {base_retailer} as base ({len(base_products)} products)")
        
        matched_groups = []
        matched_base_indices = set()
        
        # For each base product, find matches in other retailers
        for idx, base_product in base_products.iterrows():
            if idx in matched_base_indices:
                continue
            
            base_name = base_product['product_name']
            if not base_name:
                continue
            
            # Normalize name for matching
            base_normalized = self.normalizer.normalize_product_name(base_name)
            
            # Create product group starting with base
            group = {
                'product_name': base_name,
                'brand': base_product.get('brand'),
                'size': base_product.get('size_weight_volume'),
            }
            
            # Add base retailer data
            group[f'{base_retailer}_price'] = base_product.get('price')
            group[f'{base_retailer}_price_per_unit'] = base_product.get('price_per_unit')
            group[f'{base_retailer}_url'] = base_product.get('product_url')
            
            # Try to find matches in other retailers
            for other_retailer in retailers:
                if other_retailer == base_retailer:
                    continue
                
                other_products = df[df['retailer'] == other_retailer]
                
                if len(other_products) == 0:
                    continue
                
                # Get product names for matching
                other_names = other_products['product_name'].tolist()
                other_normalized = [self.normalizer.normalize_product_name(str(name)) for name in other_names]
                
                # Find best match using fuzzy matching
                best_match = process.extractOne(
                    base_normalized,
                    other_normalized,
                    scorer=fuzz.token_sort_ratio
                )
                
                if best_match and best_match[1] >= self.similarity_threshold:
                    match_idx = best_match[2]
                    matched_product = other_products.iloc[match_idx]
                    
                    # Add matched product data
                    group[f'{other_retailer}_price'] = matched_product.get('price')
                    group[f'{other_retailer}_price_per_unit'] = matched_product.get('price_per_unit')
                    group[f'{other_retailer}_url'] = matched_product.get('product_url')
                    
                    logger.debug(f"Matched: {base_name} <-> {matched_product['product_name']} ({best_match[1]}%)")
            
            # Only add group if at least 2 retailers have this product
            retailer_count = sum(1 for key in group.keys() if key.endswith('_price') and group[key] is not None)
            
            if retailer_count >= 2:
                matched_groups.append(group)
                matched_base_indices.add(idx)
        
        logger.info(f"Found {len(matched_groups)} product groups with matches across retailers")
        
        return matched_groups
    
    def create_comparison_table(self, df: pd.DataFrame):
        """
        Create price comparison table from normalized data.
        
        Args:
            df: Normalized product DataFrame
        """
        logger.info("\n" + "=" * 80)
        logger.info("CREATING COMPARISON TABLE")
        logger.info("=" * 80)
        
        if df.empty:
            logger.warning("No data to process!")
            return
        
        # Find similar products
        matched_groups = self.find_similar_products(df)
        
        if not matched_groups:
            logger.warning("No matching products found across retailers!")
            return
        
        # Create comparison DataFrame
        comparison_df = pd.DataFrame(matched_groups)
        
        # Sort by product name
        comparison_df = comparison_df.sort_values('product_name')
        
        # Export to Excel
        output_path = self.processed_dir / 'price_comparison.xlsx'
        comparison_df.to_excel(output_path, index=False, engine='openpyxl')
        
        logger.info(f"✓ Comparison table saved: {output_path}")
        logger.info(f"  Total product matches: {len(comparison_df)}")
        
        # Print statistics
        self._print_statistics(comparison_df)
    
    def _print_statistics(self, comparison_df: pd.DataFrame):
        """Print summary statistics."""
        logger.info("\n" + "=" * 80)
        logger.info("COMPARISON TABLE STATISTICS")
        logger.info("=" * 80)
        
        logger.info(f"\nTotal Product Matches: {len(comparison_df)}")
        
        # Count products per retailer
        retailers = []
        for col in comparison_df.columns:
            if col.endswith('_price'):
                retailer = col.replace('_price', '')
                retailers.append(retailer)
                count = comparison_df[col].notna().sum()
                logger.info(f"  • {retailer}: {count} products")
        
        # Price statistics per retailer
        logger.info("\nPrice Statistics by Retailer:")
        for retailer in retailers:
            price_col = f'{retailer}_price'
            if price_col in comparison_df.columns:
                prices = pd.to_numeric(comparison_df[price_col], errors='coerce').dropna()
                if len(prices) > 0:
                    logger.info(f"  {retailer}:")
                    logger.info(f"    • Average: R{prices.mean():.2f}")
                    logger.info(f"    • Min: R{prices.min():.2f}")
                    logger.info(f"    • Max: R{prices.max():.2f}")
        
        logger.info(f"\nProcess Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def process_all(self):
        """Main processing workflow."""
        logger.info("\n" + "=" * 80)
        logger.info("STARTING DATA PROCESSING")
        logger.info("=" * 80)
        logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load raw files
        df = self.load_raw_files()
        
        if df.empty:
            logger.error("No data loaded. Exiting.")
            return False
        
        # Normalize data
        normalized_df = self.normalize_data(df)
        
        if normalized_df.empty:
            logger.error("No data after normalization. Exiting.")
            return False
        
        # Create comparison table
        self.create_comparison_table(normalized_df)
        
        logger.info("\n" + "=" * 80)
        logger.info("DATA PROCESSING COMPLETE!")
        logger.info("=" * 80)
        logger.info("Output: data/processed/price_comparison.xlsx")
        
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
