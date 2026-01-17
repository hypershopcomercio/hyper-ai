from app.core.database import SessionLocal
from app.services.competition_engine import CompetitionEngine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_all_prices():
    db = SessionLocal()
    try:
        engine = CompetitionEngine(db)
        
        # O anúncio específico que precisamos atualizar é 'MLB5864611908' (nosso)
        # Mas vamos atualizar para TODOS anúncios monitorados
        
        # Buscar ID dos nossos anúncios que tem concorrentes
        from app.models.competitor_ad import CompetitorAd
        unique_ads = db.query(CompetitorAd.ad_id).distinct().all()
        
        total_updated = 0
        logger.info(f"Encontrados {len(unique_ads)} anúncios monitorados para atualizar.")
        
        for ad_row in unique_ads:
            ad_id = ad_row[0]
            logger.info(f"Sincronizando concorrentes para Ad: {ad_id}...")
            count = engine.update_competitor_prices(ad_id)
            total_updated += count
            logger.info(f"  -> {count} concorrentes atualizados.")
            
        logger.info(f"✅ Total de concorrentes atualizados com Scraper: {total_updated}")
        
    except Exception as e:
        logger.error(f"Erro ao atualizar preços: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_all_prices()
