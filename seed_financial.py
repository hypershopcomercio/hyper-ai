from app.core.database import SessionLocal
from app.models.financial import FixedCost
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_financial_data():
    db = SessionLocal()
    try:
        # Verificar se já existem dados
        if db.query(FixedCost).count() > 0:
            logger.info("Dados financeiros já existem. Pulando seed.")
            return

        costs = [
            FixedCost(name="Aluguel Galpão", amount=2500.00, category="operational", day_of_month=5),
            FixedCost(name="Internet/Telefone", amount=250.00, category="operational", day_of_month=10),
            FixedCost(name="Sistema ERP (Tiny)", amount=199.90, category="software", day_of_month=15),
            FixedCost(name="Sistema Hyper AI", amount=499.00, category="software", day_of_month=20),
            FixedCost(name="Pro-labore Sócios", amount=5000.00, category="personnel", day_of_month=5),
            FixedCost(name="Salário Exp. + Encargos", amount=2800.00, category="personnel", day_of_month=5),
            FixedCost(name="Contabilidade", amount=600.00, category="administrative", day_of_month=10),
        ]
        
        db.add_all(costs)
        db.commit()
        logger.info(f"✅ Inseridos {len(costs)} custos fixos de exemplo.")
        
    except Exception as e:
        logger.error(f"Erro ao popular dados: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_financial_data()
