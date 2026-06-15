import sys
import os

# Ensure app path is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import SessionLocal
from app.services.meli_api import MeliApiService
from app.services.sync_v2.initial_load import InitialLoadService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sync_specific_ads(mlb_ids):
    db = SessionLocal()
    try:
        meli = MeliApiService(db_session=db)
        loader = InitialLoadService(db, meli_client=meli)
        
        for mlb_id in mlb_ids:
            logger.info(f"Fazendo sync forçado do anúncio: {mlb_id}")
            resp = meli.request("GET", f"/items/{mlb_id}")
            if resp.status_code == 200:
                data = resp.json()
                loader._upsert_ad(data)
                logger.info(f"Sync concluído para {mlb_id}. Catalog ID: {data.get('catalog_product_id')}")
            else:
                logger.error(f"Erro ao buscar {mlb_id}: {resp.status_code} - {resp.text}")
                
        db.commit()
        logger.info("Todos os anúncios processados com sucesso.")
    except Exception as e:
        logger.error(f"Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python -m app.scripts.sync_specific_ads MLB123 MLB456")
        sys.exit(1)
        
    mlbs = sys.argv[1:]
    sync_specific_ads(mlbs)
