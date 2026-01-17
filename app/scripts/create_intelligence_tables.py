"""
Script para criar tabelas de Intelligence de Concorrentes no banco de dados.

Execute: python -m app.scripts.create_intelligence_tables
"""
import logging
from app.core.database import engine, Base
from app.models.competitor_intelligence import (
    CompetitorMetricsHistory,
    CompetitorImpactEvent,
    CompetitorThreatScore
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Cria todas as tabelas de intelligence de concorrentes."""
    logger.info("Criando tabelas de Intelligence de Concorrentes...")
    
    try:
        # Isso criará apenas as tabelas que ainda não existem
        Base.metadata.create_all(
            bind=engine,
            tables=[
                CompetitorMetricsHistory.__table__,
                CompetitorImpactEvent.__table__,
                CompetitorThreatScore.__table__
            ]
        )
        
        logger.info("✅ Tabelas criadas com sucesso!")
        logger.info("   - competitor_metrics_history")
        logger.info("   - competitor_impact_events")
        logger.info("   - competitor_threat_scores")
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
        raise


if __name__ == "__main__":
    create_tables()
