from playwright.sync_api import sync_playwright
import sqlite3
import datetime
import os
import sys
import re

# Add project root to path to import database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import insert_price

# Product URLs (BigBasket)
PRODUCTS = [
    {"name": "Milk (1L)", "url": "https://www.bigbasket.com/pd/306926/amul-taaza-toned-milk-1-l-pouch/", "website": "BigBasket"},
    {"name": "Eggs (12)", "url": "https://www.bigbasket.com/pd/40033819/fresho-farm-eggs-regular-medium-antibiotic-residue-free-12-pcs/", "website": "BigBasket"},
    {"name": "Bread", "url": "https://www.bigbasket.com/pd/10000570/super-white-bread-400-g/", "website": "BigBasket"},
    {"name": "Rice (1kg)", "url": "https://www.bigbasket.com/pd/10000455/bb-royal-basmati-rice-premium-1-kg/", "website": "BigBasket"},
    {"name": "Cooking Oil (1L)", "url": "https://www.bigbasket.com/pd/10000207/freedom-refined-sunflower-oil-1-l-pouch/", "website": "BigBasket"}
]

def get_price_from_page(page, url):
    """
    Extracts price from BigBasket product page using Playwright.
    """
    try:
        page.goto(url, timeout=60000)
        # Wait for title to load
        page.wait_for_load_state("domcontentloaded")
        
        title = page.title().strip()
        
        # Look for "Rs" or "Price of Rs" in title
        match = re.search(r'Rs\s*([\d\.]+)', title)
        if match:
            return float(match.group(1))
        
        # Fallback: Try to find price element if title fails (BigBasket specific selectors could be added here)
        # For now, stick to title as it was working before, but Playwright renders JS so it might be more reliable.
        
        print(f"Price not found in title: {title}")
        return None
        
    except Exception as e:
        print(f"Exception scraping {url}: {e}")
        return None

def main():
    today = datetime.date.today().strftime("%Y-%m-%d")
    print(f"Starting scrape for {today}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Set User Agent
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

        for product in PRODUCTS:
            print(f"Scraping {product['name']}...")
            price = get_price_from_page(page, product['url'])
            
            if price is not None:
                print(f"Found price: {price}")
                insert_price(today, product['name'], price, product['website'])
            else:
                print(f"Failed to scrape {product['name']}")
        
        browser.close()

if __name__ == "__main__":
    main()
