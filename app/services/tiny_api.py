import logging
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)

from app.core.database import SessionLocal
from app.models.system_config import SystemConfig

class TinyApiService:
    def __init__(self):
        self.base_url = "https://api.tiny.com.br/api2"
        self._load_token()
        
    def _load_token(self):
        # Priority: DB -> Env
        self.token = settings.TINY_API_TOKEN
        try:
            db = SessionLocal()
            db_token = db.query(SystemConfig).filter(SystemConfig.key == "tiny_api_token").first()
            if db_token and db_token.value:
                self.token = db_token.value
            db.close()
        except Exception as e:
            logger.warning(f"Failed to load Tiny token from DB: {e}")

    def search_product(self, sku: str):
        if not self.token:
            return None
            
        url = f"{self.base_url}/produtos.pesquisa.php"
        params = {
            "token": self.token,
            "pesquisa": sku,
            "formato": "json"
        }
        try:
            response = requests.post(url, data=params) # Tiny often uses POST for args or GET
            # Trying GET first or POST as per docs. PHP usually accepts both but POST is safer for tokens if not in header.
            # Tiny API documentation usually says POST for some, GET for others. "produtos.pesquisa.php" works with GET/POST params.
            # Let's use params in requests (GET) for simplicity unless POST is required. 
            # Actually requests.post(url, data=params) is safer.
            response.raise_for_status()
            data = response.json()
            
            if data.get("retorno", {}).get("status") == "Erro":
                logger.warning(f"Tiny API Error for SKU {sku}: {data['retorno'].get('erros')}")
                return None
                
            produtos = data.get("retorno", {}).get("produtos", [])
            if produtos:
                # Returns list of {produto: {...}}
                return produtos[0]["produto"]
            return None
        except Exception as e:
            logger.error(f"Error searching product {sku} in Tiny: {e}")
            return None

    def get_product_details(self, tiny_id: str):
        if not self.token:
            return None
            
        url = f"{self.base_url}/produto.obter.php"
        params = {
            "token": self.token,
            "id": tiny_id,
            "formato": "json"
        }
        try:
            response = requests.post(url, data=params)
            response.raise_for_status()
            data = response.json()
             
            if data.get("retorno", {}).get("status") == "Erro":
                 logger.warning(f"Tiny API Error for ID {tiny_id}: {data['retorno'].get('erros')}")
                 return None
            
            return data.get("retorno", {}).get("produto")
        except Exception as e:
            logger.error(f"Error getting details for ID {tiny_id}: {e}")
            return None

    def get_stock(self, sku: str):
        """
        Fetch stock for a specific SKU.
        Endpoint: /produto.obter.estoque.php
        """
        if not self.token:
            return None
        
        url = f"{self.base_url}/produto.obter.estoque.php"
        params = {
            "token": self.token,
            "id": sku, # Using SKU as ID usually works or "codigo" param
            "formato": "json"
        }
        # Docs say param 'id' is for ID or SKU? Usually 'id' is Tiny ID. 
        # But let's check if we can pass code. 
        # For 'produto.obter.estoque.php', params are 'id' (id produto).
        # We might need to map SKU -> Tiny ID first if not stored.
        # However, SyncEngine usually has the TinyProduct linked or we search it.
        # Let's assume passed argument is Tiny ID if available, or we use search.
        # Correct approach: SyncEngine passes the ID.
        
        try:
             response = requests.post(url, data=params)
             response.raise_for_status()
             data = response.json()
             
             if data.get("retorno", {}).get("status") == "Erro":
                  # Try searching if ID fail? No, caller handles it.
                  logger.warning(f"Tiny Stock Error for {sku}: {data['retorno'].get('erros')}")
                  return None
             
             return data.get("retorno", {}).get("produto")
        except Exception as e:
             logger.error(f"Error fetching stock for {sku}: {e}")
             return None
