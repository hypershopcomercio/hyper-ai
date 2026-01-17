from app.services.scraper_engine import ScraperEngine

scraper = ScraperEngine()
url = "https://produto.mercadolivre.com.br/MLB-4200110239-refrigerador-de-piscina-flutuante-porta-latas-_JM"
print(f"Testando scrap em: {url}")
data = scraper.fetch_price(url)
print(f"Resultado: {data}")
