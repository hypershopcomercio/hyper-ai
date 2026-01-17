from app.core.database import SessionLocal
from app.services.financial_service import FinancialService
from app.models.financial import ProductFinancialMetric
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run():
    db = SessionLocal()
    try:
        service = FinancialService(db)
        service.calculate_metrics()
        
        # Verificar resultados para top 5 SKUs
        metrics = db.query(ProductFinancialMetric).order_by(ProductFinancialMetric.revenue_share_30d.desc()).limit(5).all()
        
        print("\n--- TOP 5 SKUs POR RECEITA (RESULTADO DO RATEIO) ---")
        for m in metrics:
            print(f"SKU: {m.sku}")
            print(f"  - Share Receita: {m.revenue_share_30d*100:.2f}%")
            print(f"  - Taxa Devolução: {m.return_rate_90d*100:.2f}%")
            print(f"  - Custo Fixo Unitário Alocado: R$ {m.calculated_fixed_cost_share:.2f}")
            print("------------------------------------------------")
            
    except Exception as e:
        logger.error(f"Erro: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run()
