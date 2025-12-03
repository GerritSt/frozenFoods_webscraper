"""
Data Normalizer
---------------
Cleans and standardizes scraped product data.
Handles text cleaning, size/weight parsing, and unit conversion.
"""

import re
from typing import Optional, Dict, Tuple


class DataNormalizer:
    """
    Utility class for normalizing and cleaning scraped product data.
    """
    
    @staticmethod
    def clean_text(text: Optional[str]) -> Optional[str]:
        """
        Clean and normalize text fields.
        
        Args:
            text: Raw text string
            
        Returns:
            Cleaned text or None
        """
        if not text:
            return None
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,\-–—()&/]', '', text)
        
        # Normalize dashes
        text = text.replace('–', '-').replace('—', '-')
        
        return text if text else None
    
    @staticmethod
    def clean_price(price: Optional[str]) -> Optional[float]:
        """
        Extract and clean price value.
        
        Args:
            price: Raw price string (e.g., "R 45.99", "$12.50")
            
        Returns:
            Float price value or None
        """
        if not price:
            return None
        
        # Remove currency symbols and extract number
        price_match = re.search(r'(\d+[.,]\d{2})', str(price))
        
        if price_match:
            price_str = price_match.group(1).replace(',', '.')
            try:
                return float(price_str)
            except ValueError:
                return None
        
        return None
    
    @staticmethod
    def parse_size_weight_volume(text: Optional[str]) -> Dict[str, Optional[str]]:
        """
        Parse size, weight, or volume information from text.
        
        Args:
            text: Text containing size info (e.g., "500g", "1.5L", "250ml")
            
        Returns:
            Dictionary with 'value', 'unit', and 'type' keys
        """
        result = {
            'value': None,
            'unit': None,
            'type': None  # 'weight', 'volume', or 'count'
        }
        
        if not text:
            return result
        
        text = text.lower().strip()
        
        # Pattern for number + unit
        pattern = r'(\d+(?:[.,]\d+)?)\s*([a-z]+)'
        match = re.search(pattern, text)
        
        if match:
            value = match.group(1).replace(',', '.')
            unit = match.group(2)
            
            result['value'] = value
            result['unit'] = unit
            
            # Determine type
            if unit in DataNormalizer.WEIGHT_UNITS or unit in ['kg', 'g', 'mg']:
                result['type'] = 'weight'
            elif unit in DataNormalizer.VOLUME_UNITS or unit in ['l', 'ml']:
                result['type'] = 'volume'
            else:
                result['type'] = 'unknown'
        
        return result
    
    @staticmethod
    def normalize_brand(brand: Optional[str]) -> Optional[str]:
        """
        Normalize brand names (capitalize properly, remove extra text).
        
        Args:
            brand: Raw brand name
            
        Returns:
            Normalized brand name
        """
        if not brand:
            return None
        
        brand = DataNormalizer.clean_text(brand)
        
        # Capitalize first letter of each word
        brand = ' '.join(word.capitalize() for word in brand.split())
        
        return brand
    
    @staticmethod
    def validate_barcode(barcode: Optional[str]) -> Optional[str]:
        """
        Validate and clean barcode (should be numeric).
        
        Args:
            barcode: Raw barcode string
            
        Returns:
            Cleaned barcode or None
        """
        if not barcode:
            return None
        
        # Extract only digits
        barcode = re.sub(r'\D', '', str(barcode))
        
        # Barcodes are typically 8, 12, 13, or 14 digits
        if len(barcode) in [8, 12, 13, 14]:
            return barcode
        
        return None
    
    @staticmethod
    def normalize_product_data(product: Dict) -> Dict:
        """
        Apply all normalization functions to a product dictionary.
        
        Args:
            product: Raw product data dictionary
            
        Returns:
            Normalized product data dictionary
        """
        normalized = product.copy()
        
        # Clean text fields
        text_fields = ['product_name', 'description', 'brand', 'category', 'department']
        for field in text_fields:
            if field in normalized:
                normalized[field] = DataNormalizer.clean_text(normalized[field])
        
        # Clean price
        if 'price' in normalized:
            normalized['price'] = DataNormalizer.clean_price(normalized['price'])
        
        # Normalize brand
        if 'brand' in normalized:
            normalized['brand'] = DataNormalizer.normalize_brand(normalized['brand'])
        
        # Validate barcode
        if 'barcode' in normalized:
            normalized['barcode'] = DataNormalizer.validate_barcode(normalized['barcode'])
        
        # Parse size/weight/volume
        if 'size_weight_volume' in normalized and normalized['size_weight_volume']:
            parsed = DataNormalizer.parse_size_weight_volume(normalized['size_weight_volume'])
            normalized['unit_of_measure'] = parsed['unit']
        
        return normalized
