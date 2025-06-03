import requests
from bs4 import BeautifulSoup
import json
import os
import time
import random

def scrape_unegui_listings(page_url):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    response = requests.get(page_url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    listings = soup.select("div.js-item-listing")  

    data = []
    for item in listings:
        # Гарчиг
        title_tag = item.select_one("a.advert__content-title") or item.select_one("h2")
        title = title_tag.get_text(strip=True) if title_tag else ""

        # Үнэ
        price_tag = item.select_one(".advert__content-price")
        price = price_tag.get_text(strip=True) if price_tag else ""

        # Байршил
        location_tag = item.select_one(".advert__content-place")
        location = location_tag.get_text(strip=True) if location_tag else ""

        # Талбай (м²)
        raw_text = item.get_text(separator=" ", strip=True)
        size = ""
        if "м²" in raw_text or "мк" in raw_text:
            parts = raw_text.replace("м²", "мк").split(" ")
            for p in parts:
                if p.endswith("мк"):
                    size = p.replace("мк", "").strip()
                    break

        link_tag = item.select_one("a.advert__content-title")
        link = ""
        if link_tag and link_tag.has_attr("href"):
            href = link_tag["href"]
            if href.startswith("http"):
                link = href
            else:
                base = "https://www.unegui.mn"
                link = base + href

        data.append({
            "title": title,
            "price": price,
            "location": location,
            "size_sqm": size,   
            "link": link
        })

    return data

def scrape_multiple_pages(base_url, pages=5, delay=(1, 3)):
    all_data = []
    for page_num in range(1, pages + 1):

        page_url = base_url
        print(f"Scraping page {page_num}: {page_url}")
        try:
            page_data = scrape_unegui_listings(page_url)
            all_data.extend(page_data)
        except Exception as e:
            print(f"  Алдаа гарлаа page {page_num}-т: {e}")
        time.sleep(random.uniform(delay[0], delay[1]))
    return all_data


if __name__ == "__main__":
    base_url = "https://www.unegui.mn/l-hdlh/l-hdlh-zarna/ub-hanuul/"
    pages_to_scrape = 1
    scraped_data = scrape_multiple_pages(base_url, pages=pages_to_scrape)
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "listings.json")

    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(scraped_data, json_file, ensure_ascii=False, indent=4)

    print(f"өгөгдөл амжилттай хадгалагдлаа: {output_path}")
