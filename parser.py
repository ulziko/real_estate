from playwright.sync_api import sync_playwright
import json

def scrape_unegui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.unegui.mn/l-hdlh/l-hdlh-zarna/ub-hanuul/", timeout=100000, wait_until="domcontentloaded")
        listings = page.query_selector_all("div.js-item-listing")
        data = []
        for item in listings:
            title = item.query_selector("a.advert__content-title") or item.query_selector("h2")
            price = item.query_selector(".advert__content-price")
            location = item.query_selector(".advert__content-place")
            size =( item.inner_text().split("мк")[0]).split(" ")[-1] if "мк" in item.inner_text() else ""

            data.append({
                "title": title.inner_text().strip() if title else "",
                "price": price.inner_text().strip() if price else "",
                "location": location.inner_text().strip() if location else "",
                "size": size.strip(),
                "link": item.query_selector("a").get_attribute("href")
            })
        browser.close()

        with open("unegui_listings.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

scrape_unegui()
