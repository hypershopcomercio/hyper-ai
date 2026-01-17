from app.core.database import engine, Base
from app.models.supply import Supplier, PurchaseOrder, PurchaseOrderItem, InboundShipment, StockBatch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Criando tabelas de Supply Chain...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tabelas de Supply criadas com sucesso!")

if __name__ == "__main__":
    init_db()
