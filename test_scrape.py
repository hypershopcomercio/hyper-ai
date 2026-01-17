
import requests
from bs4 import BeautifulSoup
import time
import random

URLS = [
    "https://produto.mercadolivre.com.br/MLB-4200110239-bar-cooler-inflavel-flutuante-intex-piscina-24-latas-boia-_JM",
    "https://produto.mercadolivre.com.br/MLB-4113724473-bar-cooler-inflavel-flutuante-piscina-30-latas-boia-intex-_JM"
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0'
}

def test_scrape():
    for url in URLS:
        print(f"Testing: {url}")
        try:
            # Add random delay
            time.sleep(random.uniform(1, 3))
            
            response = requests.get(url, headers=HEADERS, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                print(f"Page Title: {soup.title.string if soup.title else 'No Title'}")
                
                # Save first 2000 chars to debug
                with open("scrape_debug.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                
                # Check for "meta property='og:price:amount'"
                price_meta = soup.find("meta", property="product:price:amount")
                if not price_meta:
                     # Try other common meta
                     price_meta = soup.find("meta", property="og:price:amount")
                
                if price_meta:
                    print(f"Price found (Meta): {price_meta.get('content')}")
                    continue

                # Fallback: parsing UI elements (fragile)
                # Look for 'ui-pdp-price__second-line'
                price_tag = soup.find('span', class_='andes-money-amount__fraction')
                if price_tag:
                    print(f"Price found (Tag): {price_tag.text}")
                else:
                    print("Price Not Found in HTML")
                    # print(response.text[:500]) # Debug
            else:
                print("Failed to fetch")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_scrape()
