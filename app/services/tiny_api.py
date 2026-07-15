import logging
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)

from app.core.database import SessionLocal
from app.models.system_config import SystemConfig

class TinyApiService:
    def __init__(self):
        self.base_url = "https://api.tiny.com.br/api2"
        # The API returns rate-limit information in the response rather than
        # as an HTTP error. Keep it available to the synchronizer so it can
        # stop cleanly instead of continuing to hammer Tiny after a block.
        self.last_error = None
        self.last_rate_limit = None
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

    def get_stock(self, tiny_id: str):
        """
        Fetch stock for a specific SKU.
        Endpoint: /produto.obter.estoque.php
        """
        if not self.token:
            return None
        
        url = f"{self.base_url}/produto.obter.estoque.php"
        params = {
            "token": self.token,
            # This endpoint expects the Tiny product ID. Passing the SKU here
            # silently returns no stock for many accounts.
            "id": tiny_id,
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
             self.last_error = None
             response = requests.post(url, data=params, timeout=30)
             response.raise_for_status()
             limit_header = response.headers.get("x-limit-api")
             try:
                 self.last_rate_limit = int(limit_header) if limit_header else None
             except (TypeError, ValueError):
                 self.last_rate_limit = None
             data = response.json()
             
             if data.get("retorno", {}).get("status") == "Erro":
                  response_data = data.get("retorno", {})
                  error_code = str(response_data.get("codigo_erro") or "")
                  self.last_error = {
                      "code": error_code,
                      "errors": response_data.get("erros") or [],
                      "rate_limited": error_code in {"6", "11"},
                  }
                  logger.warning(f"Tiny Stock Error for product {tiny_id}: {self.last_error['errors']}")
                  return None
             
             return data.get("retorno", {}).get("produto")
        except Exception as e:
             self.last_error = {"code": None, "errors": [str(e)], "rate_limited": False}
             logger.error(f"Error fetching stock for product {tiny_id}: {e}")
             return None
