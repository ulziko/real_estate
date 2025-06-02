from playwright.sync_api import sync_playwright
import json
import re
from datetime import datetime

class UneguiScraper:
    def __init__(self):
        self.base_url = "https://www.unegui.mn/l-hdlh/l-hdlh-treesllne/oron-suuts/"
        self.selectors = {
            'listings': "div.js-item-listing",
            'title': "a.advert__content-title",
            'price': ".advert__content-price",
            'location': ".advert__content-place"
        }
    
    def parse_price(self, text):
        if not text: return None
        nums = re.findall(r'[\d,]+', text)
        if not nums: return None
        price = float(nums[0].replace(',', ''))
        if 'сая' in text: price *= 1000000
        elif 'мянга' in text: price *= 1000
        return int(price)
    
    def scrape(self, pages=3):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            data = []
            
            for i in range(1, pages + 1):
                print(f"Scraping page {i}...")
                try:
                    page.goto(f"{self.base_url}?page={i}", wait_until="domcontentloaded")
                    page.wait_for_timeout(2000)
                    
                    for item in page.query_selector_all(self.selectors['listings']):
                        try:
                            title = item.query_selector(self.selectors['title'])
                            price = item.query_selector(self.selectors['price'])
                            location = item.query_selector(self.selectors['location'])
                            text = item.inner_text()
                            
                            data.append({
                                "title": title.inner_text() if title else "",
                                "price_text": price.inner_text() if price else "",
                                "price_value": self.parse_price(price.inner_text() if price else ""),
                                "location": location.inner_text() if location else "",
                                "district": location.inner_text().split(',')[0] if location else "",
                                "area_sqm": float(m.group(1)) if (m := re.search(r'(\d+(?:\.\d+)?)\s*мк', text)) else None,
                                "rooms": int(r.group(1)) if (r := re.search(r'(\d+)\s*өрөө', text.lower())) else None,
                                "page": i,
                                "scraped_at": datetime.now().isoformat()
                            })
                        except: continue
                except Exception as e:
                    print(f"Error on page {i}: {e}")
                    
            browser.close()
            return data
    
    def save(self, data, filename="rental_data.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(data)} listings to {filename}")

# Usage
if __name__ == "__main__":
    scraper = UneguiScraper()
    data = scraper.scrape(pages=3)
    if data: scraper.save(data)