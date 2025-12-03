"""
Retailer Configuration
----------------------
Configuration for each retailer's scraping selectors and URLs.
This is the ONLY place you need to update when retailers change their site structure.
"""

RETAILER_CONFIGS = {
    'Shoprite': {
        'category_url': 'https://www.shoprite.co.za/c-2540/All-Departments/Food/Frozen-Food',
        'selectors': {
            'product_card': 'div.item-product',
            'product_link': 'a.product-listening-click',
            'next_button': 'a.shoprite-icon-chevron-right',
            'product_name': 'h1.pdp__name',
            'product_id': 'span.pdp__id',
            'price': 'div.special-price__price',
            'description': 'div.pdp__description',
        }
    },
    
    'Checkers': {
        'category_url': 'https://www.checkers.co.za/department/frozen-foods-1-67075db0ff9878113640072b',
        'selectors': {
            'product_card': 'product-card_card__DsB3_.product-card_card-merch__gWn4Y',
            'product_link': 'a.product-link',
            'next_button': '.next-page, button[aria-label="Next"]',
            'product_name': ['h1.product-name', 'h1'],
            'brand': ['.brand', '[itemprop="brand"]'],
            'price': ['.price', '[itemprop="price"]'],
            'description': ['.description'],
            'size': ['.product-size', '.weight'],
            'barcode': ['.barcode', '.sku'],
        }
    },
    
    'PicknPay': {
        'category_url': 'https://www.pnp.co.za/c/frozen-food-423144840',
        'selectors': {
            'product_card': 'ui-product-grid-item.ng-star-inserted',
            'product_link': 'a.product-grid-item__info-container__name.product-action',
            'next_button': 'a.next.ng-star-inserted',
            'product_name': 'div.prod h2',
            'price': 'div.price',
        }
    },
    
    'Makro': {
        'category_url': 'https://www.makro.co.za/food/frozen-food/c/F07',
        'selectors': {
            'product_card': '.product-item',
            'product_link': 'a.product-link',
            'next_button': '.next-page',
            'product_name': ['h1', '.product-name'],
            'brand': ['.brand'],
            'price': ['.price'],
            'description': ['.description'],
            'size': ['.product-size'],
            'barcode': ['.barcode'],
        }
    }
}
