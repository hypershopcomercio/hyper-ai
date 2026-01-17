from app.core.database import engine, Base
from app.models.financial import FixedCost, ProductFinancialMetric
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Criando tabelas financeiras...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    init_db()
