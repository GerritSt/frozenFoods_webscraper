"""
Universal Scraper
-----------------
A single, configuration-driven scraper that works for all retailers.
No need for separate scraper files - just update retailer_config.py!
"""

from playwright.sync_api import sync_playwright, Page, Browser
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin
import time
import logging
import random
import re
from datetime import datetime


class UniversalScraper:
    """
    A flexible scraper that adapts to different retailers using configuration.
    """
    
    def __init__(self, retailer_name: str, config: Dict, headless: bool = True):
        """
        Initialize the universal scraper.
        
        Args:
            retailer_name: Name of the retailer (e.g., "Shoprite")
            config: Configuration dictionary from retailer_config.py
            headless: Run browser in headless mode
        """
        self.retailer_name = retailer_name
        self.config = config
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
        # Setup logging
        self.logger = self._setup_logger()
        
        # Scraping settings
        self.min_delay = 1.5
        self.max_delay = 1.0
        self.timeout = 30000
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for this scraper."""
        logger = logging.getLogger(f"{self.retailer_name}Scraper")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - {self.retailer_name} - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def start_browser(self):
        """Initialize Playwright browser."""
        try:
            self.logger.info("Starting browser...")
            self.playwright = sync_playwright().start()
            
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            self.page = context.new_page()
            self.page.set_default_timeout(self.timeout)
            
            self.logger.info("Browser started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}")
            raise
    
    def close_browser(self):
        """Close browser and clean up."""
        try:
            if self.page:
                self.page.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self.logger.info("Browser closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")
    
    def wait_random(self):
        """Wait random time to mimic human behavior."""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)
    
    def close_popups(self):
        """Close any popups that might appear (e.g., PicknPay location popup)."""
        try:
            if self.retailer_name == 'PicknPay':
                # Check for location popup "Do it later" button
                popup_button_selector = 'button.address-popover__actions-do-later.action-button'
                
                # Wait briefly to see if popup appears
                try:
                    self.page.wait_for_selector(popup_button_selector, timeout=1000)
                    # If found, click it
                    self.page.click(popup_button_selector)
                    self.logger.info("Closed PicknPay location popup")
                    self.page.wait_for_timeout(1000)  # Wait for popup to close
                except Exception as e:
                    # Popup might not appear every time, that's fine
                    self.logger.debug(f"No popup found or already closed: {e}")
        except Exception as e:
            self.logger.warning(f"Error handling popups: {e}")
    
    def safe_navigate(self, url: str) -> bool:
        """Safely navigate to a URL."""
        try:
            self.logger.info(f"Navigating to: {url}")
            
            # Try to navigate with networkidle wait (better for JavaScript-heavy sites)
            try:
                self.page.goto(url, wait_until='networkidle', timeout=30000)
            except Exception as e:
                # Fallback to domcontentloaded if networkidle times out
                self.logger.warning(f"Network idle timeout, falling back to domcontentloaded: {e}")
                self.page.goto(url, wait_until='domcontentloaded', timeout=15000)
            
            # Additional wait to ensure page is stable
            self.page.wait_for_timeout(2000)  # Wait 2 seconds
            
            # Handle any popups that might appear
            self.close_popups()
            
            self.wait_random()
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    def has_next_page(self) -> bool:
        """Check if next page exists."""
        try:
            selector = self.config['selectors']['next_button']
            next_button = self.page.query_selector(selector)
            
            if not next_button:
                return False
            
            is_disabled = next_button.get_attribute('disabled')
            aria_disabled = next_button.get_attribute('aria-disabled')
            
            return not (is_disabled or aria_disabled == 'true')
            
        except Exception as e:
            self.logger.warning(f"Error checking for next page: {e}")
            return False
    
    def go_to_next_page(self) -> bool:
        """Navigate to next page."""
        try:
            selector = self.config['selectors']['next_button']
            next_button = self.page.query_selector(selector)
            
            if next_button:
                next_button.click()
                self.page.wait_for_load_state('domcontentloaded')
                self.wait_random()
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error navigating to next page: {e}")
            return False
    
    def handle_pagination(self, max_pages: Optional[int] = None) -> List[str]:
        """Handle pagination and collect page URLs."""
        page_urls = []
        current_page = 1
        
        while True:
            if max_pages and current_page > max_pages:
                break
            
            current_url = self.page.url
            page_urls.append(current_url)
            self.logger.info(f"Collected page {current_page}: {current_url}")
            
            if not self.has_next_page():
                break
            
            if not self.go_to_next_page():
                break
            
            current_page += 1
            self.wait_random()
        
        self.logger.info(f"Total pages collected: {len(page_urls)}")
        return page_urls
    
    def extract_product_urls(self) -> List[str]:
        """Extract product URLs from listing page."""
        product_urls = []
        
        try:
            card_selector = self.config['selectors']['product_card']
            link_selector = self.config['selectors']['product_link']
            
            self.page.wait_for_selector(card_selector, timeout=10000)
            
            product_elements = self.page.query_selector_all(link_selector)
            
            for element in product_elements:
                href = element.get_attribute('href')
                if href:
                    # If relative URL, convert to absolute
                    if not href.startswith('http'):
                        current_url = self.page.url
                        href = urljoin(current_url, href)
                    product_urls.append(href)
            
        except Exception as e:
            self.logger.error(f"Error extracting product URLs: {e}")
        
        return list(set(product_urls))
    
    def extract_text(self, soup: BeautifulSoup, selectors) -> Optional[str]:
        """Try multiple selectors to extract text. Accepts string or list of strings."""
        # Handle both string and list of strings
        if isinstance(selectors, str):
            selectors = [selectors]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return None
    
    def extract_price(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract price with cleaning."""
        selectors = self.config['selectors']['price']
        price_text = self.extract_text(soup, selectors)
        
        if price_text:
            self.logger.debug(f"Found price text: {price_text}")
            price_match = re.search(r'R?\s*(\d+[.,]\d{2})', price_text)
            if price_match:
                price = price_match.group(1).replace(',', '.')
                self.logger.debug(f"Extracted price: {price}")
                return price
        else:
            self.logger.warning("No price found with configured selectors")
        
        return None
    
    def create_product_template(self) -> Dict:
        """Create product data template."""
        return {
            'product_id': None,
            'barcode': None,
            'product_name': None,
            'description': None,
            'brand': None,
            'price': None,
            'size_weight_volume': None,
            'unit_of_measure': None,
            'price_per_unit': None,
            'width': None,
            'height': None,
            'depth': None,
            'length': None,
            'gross_weight': None,
            'net_weight': None,
            'category': 'Frozen Foods',
            'product_url': None,
            'retailer': self.retailer_name,
            'scrape_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def extract_product_details(self, product_url: str) -> Optional[Dict]:
        """Extract product details from product page."""
        product = self.create_product_template()
        product['product_url'] = product_url
        
        try:
            # Navigate to product page first
            if not self.safe_navigate(product_url):
                return None
            
            # For Shoprite: Click dropdown button to reveal product information table
            if self.retailer_name == 'Shoprite':
                try:
                    prodInfo_selector_button = 'li#accessibletabsnavigation0-1'
                    # Wait for the dropdown button to be available
                    self.page.wait_for_selector(prodInfo_selector_button, timeout=5000)
                    # Click it to expand the product information section
                    self.page.click(prodInfo_selector_button)
                    # Wait a moment for the table to expand
                    self.page.wait_for_timeout(1000)
                    self.logger.info("Clicked product information dropdown")
                except Exception as e:
                    self.logger.warning(f"Could not click dropdown button: {e}")
            
            content = self.page.content()
            
            # Debug: Log first 200 characters of content to see what we're getting
            content_preview = content[:200] if content else "EMPTY"
            self.logger.debug(f"Page content preview: {content_preview}")
            
            # Check if content looks like HTML
            if not content or not content.strip().startswith('<'):
                self.logger.error(f"Invalid HTML content received. First 500 chars: {content[:500]}")
                return None
            
            soup = BeautifulSoup(content, 'lxml')
            
            # Extract using configured selectors
            product['product_name'] = self.extract_text(
                soup, self.config['selectors']['product_name']
            )

            # Only extract description if selector exists (not all retailers have it)
            if 'description' in self.config['selectors']:
                product['description'] = self.extract_text(
                    soup, self.config['selectors']['description']
                )
            
            # The product information for Shoprite is in a table
            if self.retailer_name == 'Shoprite':
                table_data = {}
                try:
                    table_selector = 'table.pdp__product-information'
                    # Find the table
                    table = soup.select_one(table_selector)
                    if not table:
                        self.logger.warning(f"Table not found with selector: {table_selector}")
                        return table_data
                    
                    # Extract all rows
                    rows = table.find_all('tr')
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        
                        # Each row should have 2 cells: label and value
                        if len(cells) >= 2:
                            label = cells[0].get_text(strip=True)
                            value = cells[1].get_text(strip=True)
                            
                            # Store with cleaned label as key
                            table_data[label] = value
                    
                    self.logger.info(f"Extracted {len(table_data)} fields from table")
                    
                except Exception as e:
                    self.logger.error(f"Error extracting table data: {e}")

                # extract data from the table
                if table_data:
                    product['brand'] = table_data.get('Product Brand', product['brand'])
                    product['barcode'] = table_data.get('Main Barcode', product['barcode'])
                    product['unit_of_measure'] = table_data.get('Unit of Measure', product['unit_of_measure'])
                    
                    # Extract weight from "Product Weight" or "Product Volume" field (whichever is populated)
                    weight_str = table_data.get('Product Weight', '') or table_data.get('Product Volume', '')
                    if weight_str:
                        product['size_weight_volume'] = weight_str
                        # Parse weight if it's in format like "5kg", "500g", "1l", "500ml"
                        weight_match = re.search(r'([\d.]+)\s*(kg|g|l|ml)', weight_str.lower())
                        if weight_match:
                            product['net_weight'] = f"{weight_match.group(1)} {weight_match.group(2)}"
                            # Get the unit of measure if there is a weight
                            unit = weight_match.group(2)
                            if unit in ['kg', 'g']:
                                product['unit_of_measure'] = 'kg'
                            elif unit in ['l', 'ml']:
                                product['unit_of_measure'] = 'L'
                    
                    # Extract dimensions (width, height, depth/length) - only if present
                    width_str = table_data.get('Product Width (mm)', '')
                    if width_str:
                        product['width'] = width_str
                    
                    height_str = table_data.get('Product Height (mm)', '')
                    if height_str:
                        product['height'] = height_str
                    
                    # Try both "Product Depth" and "Product Length" 
                    depth_str = table_data.get('Product Depth (mm)', '') or table_data.get('Product Length (mm)', '')
                    if depth_str:
                        product['depth'] = depth_str
                        product['length'] = depth_str  # Use same value for both
                    
                    # Extract gross weight if present
                    gross_weight_str = table_data.get('Product Gross Weight (g)', '')
                    if gross_weight_str:
                        product['gross_weight'] = gross_weight_str
            
            # The product information for PicknPay is in h3 headings with content following
            elif self.retailer_name == 'PicknPay':
                try:
                    # Find all span elements with class 'product-details-heading'
                    heading_spans = soup.find_all('span', class_='product-details-heading')
                    
                    product_info = {}
                    for span in heading_spans:
                        # Get the section title from the h3 inside the span
                        h3 = span.find('h3')
                        if not h3:
                            continue
                        
                        section_title = h3.get_text(strip=True)
                        
                        # Collect text from siblings until we hit another span or double br
                        content_parts = []
                        current = span.next_sibling
                        br_count = 0
                        
                        while current:
                            # If we hit another span with product-details-heading, stop
                            if hasattr(current, 'name'):
                                if current.name == 'span' and 'product-details-heading' in current.get('class', []):
                                    break
                                
                                # Count br tags to detect double br separator
                                if current.name == 'br':
                                    br_count += 1
                                    if br_count >= 2:
                                        break
                                else:
                                    # Reset br count if we hit non-br element
                                    br_count = 0
                                    # Get text from this element
                                    text = current.get_text(strip=True)
                                    if text:
                                        content_parts.append(text)
                            elif isinstance(current, str):
                                # Direct text node
                                text = current.strip()
                                if text:
                                    content_parts.append(text)
                                    br_count = 0  # Reset br count
                            
                            current = current.next_sibling
                        
                        # Store the content under the heading
                        if content_parts:
                            product_info[section_title] = ' '.join(content_parts)
                            self.logger.debug(f"Section '{section_title}': {content_parts[0][:50]}...")
                    
                    self.logger.info(f"Extracted {len(product_info)} sections from PicknPay product details")
                    if product_info:
                        self.logger.info(f"Section titles found: {list(product_info.keys())}")
                    
                    # Extract relevant fields
                    if product_info:
                        # Barcode section
                        barcode_text = product_info.get('Barcode', '')
                        if barcode_text:
                            product['barcode'] = barcode_text
                        
                        # Description section
                        description_text = product_info.get('Description', '')
                        if description_text and not product['description']:
                            product['description'] = description_text
                        
                        # Try to extract size/weight from product name (e.g., "1kg" in title)
                        if product['product_name']:
                            size_match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|g|l|ml)\b', product['product_name'], re.IGNORECASE)
                            if size_match:
                                product['size_weight_volume'] = f"{size_match.group(1)}{size_match.group(2)}"
                                product['net_weight'] = f"{size_match.group(1)} {size_match.group(2)}"
                                # Get the unit of measure
                                unit = size_match.group(2)
                                if unit in ['kg', 'g']:
                                    product['unit_of_measure'] = 'kg'
                                elif unit in ['L', 'ml']:
                                    product['unit_of_measure'] = 'L'
                            else: 
                                product['unit_of_measure'] = 'EA'
                
                except Exception as e:
                    self.logger.error(f"Error extracting PicknPay product details: {e}")
            
            else:
                product['brand'] = self.extract_text(
                    soup, self.config['selectors']['brand']
                )
                
                product['size_weight_volume'] = self.extract_text(
                    soup, self.config['selectors']['size']
                )
                
                product['barcode'] = self.extract_text(
                    soup, self.config['selectors']['barcode']
                )
            
            product['price'] = self.extract_price(soup)
            # Extract product ID from URL
            id_match = re.search(r'/(\d{6,})', product_url)
            if id_match:
                product['product_id'] = id_match.group(1)

            # Calculate the price per unit (price per kg or price per liter)
            if product['price']:
                # If unit of measure is EA (Each), price per unit is just the price
                if product['unit_of_measure'] == 'EA':
                    product['price_per_unit'] = product['price']
                # Otherwise calculate based on size/weight/volume
                elif product['size_weight_volume']:
                    try:
                        # Parse the size/weight/volume to get number and unit
                        size_match = re.search(r'([\d.]+)\s*(kg|g|l|ml)', product['size_weight_volume'], re.IGNORECASE)
                        if size_match:
                            amount = float(size_match.group(1))
                            unit = size_match.group(2).lower()
                            price = float(product['price'])
                            
                            # Normalize to kg or L
                            if unit == 'g':
                                normalized_amount = amount / 1000  # Convert g to kg
                            elif unit == 'ml':
                                normalized_amount = amount / 1000  # Convert ml to L
                            else:
                                normalized_amount = amount  # Already kg or L
                            
                            # Calculate price per kg or per L
                            if normalized_amount > 0:
                                price_per_unit = price / normalized_amount
                                product['price_per_unit'] = f"{price_per_unit:.2f}"
                                self.logger.debug(f"Calculated price_per_unit: R{price_per_unit:.2f} per {'kg' if unit in ['kg', 'g'] else 'L'}")
                    
                    except (ValueError, ZeroDivisionError) as e:
                        self.logger.warning(f"Could not calculate price_per_unit: {e}")
            self.logger.info('Product extraction complete')
        except Exception as e:
            self.logger.error(f"Error extracting details for {product_url}: {e}")
            return None
        
        return product
    
    def scrape_category(self, max_pages: Optional[int] = None, max_items: Optional[int] = None) -> List[Dict]:
        """
        Scrape all products from category.
        
        Args:
            max_pages: Maximum number of pages to scrape (None = all pages)
            max_items: Maximum number of products to scrape (None = all products)
        """
        all_products = []
        
        category_url = self.config['category_url']
        
        if not self.safe_navigate(category_url):
            self.logger.error("Failed to navigate to category page")
            return all_products
        
        page_urls = self.handle_pagination(max_pages)
        
        for page_num, page_url in enumerate(page_urls, 1):
            self.logger.info(f"Scraping page {page_num}/{len(page_urls)}")
            
            if page_url != self.page.url:
                if not self.safe_navigate(page_url):
                    continue
            
            product_urls = self.extract_product_urls()
            self.logger.info(f"Found {len(product_urls)} products on page {page_num}")
            
            for product_url in product_urls:
                # Check if we've reached max_items limit
                if max_items and len(all_products) >= max_items:
                    self.logger.info(f"Reached max_items limit of {max_items}. Stopping scrape.")
                    return all_products
                
                try:
                    product_data = self.extract_product_details(product_url)
                    if product_data:
                        all_products.append(product_data)
                        self.logger.info(f"Scraped: {product_data.get('product_name', 'Unknown')} ({len(all_products)}/{max_items or 'unlimited'})")
                except Exception as e:
                    self.logger.error(f"Error scraping product {product_url}: {e}")
                    continue
        
        return all_products
    
    def run(self, max_pages: Optional[int] = None, max_items: Optional[int] = None) -> List[Dict]:
        """
        Main execution method.
        
        Args:
            max_pages: Maximum number of pages to scrape
            max_items: Maximum number of products to scrape
        """
        products = []
        
        try:
            self.start_browser()
            self.logger.info(f"Starting scrape for {self.retailer_name}")
            
            products = self.scrape_category(max_pages, max_items)
            
            self.logger.info(f"Scraping complete. Total products: {len(products)}")
            
        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
            raise
        
        finally:
            self.close_browser()
        
        return products
