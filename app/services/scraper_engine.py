import requests
import re
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class ScraperEngine:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch_price(self, url: str):
        """
        Scrapes the product page to find current and original prices.
        Returns dict: { "price": float, "original_price": float|None }
        """
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            if res.status_code != 200:
                logger.error(f"Scraper failed: {res.status_code}")
                return None
            
            html = res.text
            soup = BeautifulSoup(html, 'html.parser')
            
            # --- Preço Atual ---
            current_price = None
            # Tentar meta tag (mais confiável)
            price_meta = soup.find("meta", property="product:price:amount")
            if price_meta:
                try:
                    current_price = float(price_meta["content"])
                except:
                    pass
            
            if not current_price:
                 # Fallback: ui-pdp-price__second-line (preco principal)
                 # Busca o container do preço final
                 price_container = soup.select_one('.ui-pdp-price__second-line .andes-money-amount__fraction')
                 if price_container:
                     current_price = float(price_container.text.replace('.', '').replace(',', '.'))

            # --- Preço Original (De) ---
            original_price = None
            
            # Seletor 1: ui-pdp-price__original-value (preço riscado explícito)
            original_container = soup.select_one('.ui-pdp-price__original-value .andes-money-amount__fraction')
            if original_container:
                original_price = float(original_container.text.replace('.', '').replace(',', '.'))
            
            # Seletor 2: andes-money-amount--previous (padrão antigo/mobile)
            if not original_price:
                prev_container = soup.select_one('.andes-money-amount--previous .andes-money-amount__fraction')
                if prev_container:
                     original_price = float(prev_container.text.replace('.', '').replace(',', '.'))

            # Validação Final
            if current_price:
                return {
                    "price": current_price,
                    "original_price": original_price
                }
            
            logger.warning("Scraper: Preço não encontrado")
            return None
            
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            return None
