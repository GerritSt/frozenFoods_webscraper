"""
Data Normalizer
---------------
Cleans and standardizes scraped product data for comparison.
"""

import re
from typing import Optional, Dict


class DataNormalizer:
    """
    Utility class for normalizing and cleaning scraped product data.
    """
    
    @staticmethod
    def clean_text(text: Optional[str]) -> Optional[str]:
        """Clean and normalize text fields."""
        if not text or str(text).lower() in ['none', 'nan', '']:
            return None
        
        text = str(text).strip()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text if text else None
    
    @staticmethod
    def clean_price(price) -> Optional[float]:
        """Extract and clean price value."""
        if not price or str(price).lower() in ['none', 'nan', '']:
            return None
        
        # If already a number
        try:
            return float(price)
        except (ValueError, TypeError):
            pass
        
        # Extract from string
        price_match = re.search(r'(\d+[.,]\d{2})', str(price))
        if price_match:
            price_str = price_match.group(1).replace(',', '.')
            try:
                return float(price_str)
            except ValueError:
                return None
        
        return None
    
    @staticmethod
    def normalize_product_name(name: str) -> str:
        """
        Normalize product name for comparison.
        Remove brand names, sizes, and common descriptors to help matching.
        """
        if not name:
            return ""
        
        name = str(name).lower().strip()
        
        # Remove common package indicators
        name = re.sub(r'\d+\s*x\s*\d+\s*(ml|g|kg|l)', '', name)
        name = re.sub(r'\d+(?:\.\d+)?\s*(ml|g|kg|l|mm)', '', name)
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    @staticmethod
    def parse_weight_volume(text: Optional[str]) -> Optional[float]:
        """
        Parse weight/volume and normalize to base units (g or ml).
        Returns value in grams or milliliters.
        """
        if not text or str(text).lower() in ['none', 'nan', '']:
            return None
        
        text = str(text).lower().strip()
        
        # Try to extract number and unit
        match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|g|l|ml)', text)
        if not match:
            return None
        
        value = float(match.group(1))
        unit = match.group(2)
        
        # Normalize to base units
        if unit == 'kg':
            return value * 1000  # Convert to grams
        elif unit == 'g':
            return value
        elif unit == 'l':
            return value * 1000  # Convert to milliliters
        elif unit == 'ml':
            return value
        
        return None
    
    @staticmethod
    def normalize_product(product: Dict) -> Dict:
        """
        Normalize a single product for comparison.
        """
        return {
            'product_name': DataNormalizer.clean_text(product.get('product_name')),
            'brand': DataNormalizer.clean_text(product.get('brand')),
            'price': DataNormalizer.clean_price(product.get('price')),
            'price_per_unit': DataNormalizer.clean_price(product.get('price_per_unit')),
            'size_weight_volume': DataNormalizer.clean_text(product.get('size_weight_volume')),
            'normalized_size': DataNormalizer.parse_weight_volume(product.get('size_weight_volume')),
            'unit_of_measure': DataNormalizer.clean_text(product.get('unit_of_measure')),
            'retailer': DataNormalizer.clean_text(product.get('retailer')),
            'product_url': DataNormalizer.clean_text(product.get('product_url')),
        }
