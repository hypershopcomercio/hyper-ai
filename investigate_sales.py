from app.core.database import SessionLocal
from app.models.competitor_ad import CompetitorAd
from app.models.ml_order import MlOrder, MlOrderItem
from datetime import datetime
from sqlalchemy import func, and_

db = SessionLocal()

# Pegar primeiro concorrente
comp = db.query(CompetitorAd).first()

if comp:
    print(f"Gráfico de Impacto monitora anúncio: {comp.ad_id}\n")
    
    # Vendas do dia 03/01/2026
    start = datetime(2026, 1, 3, 0, 0, 0)
    end = datetime(2026, 1, 4, 0, 0, 0)
    
    # Vendas do anúncio específico
    vendas_ad = db.query(func.coalesce(func.sum(MlOrderItem.quantity), 0)).join(MlOrder).filter(
        and_(
            MlOrderItem.ml_item_id == comp.ad_id,
            MlOrder.date_closed >= start,
            MlOrder.date_closed < end,
            MlOrder.status.in_(['paid', 'shipped', 'delivered'])
        )
    ).scalar()
    
    # Vendas TOTAIS de todos produtos
    vendas_totais = db.query(func.coalesce(func.sum(MlOrderItem.quantity), 0)).join(MlOrder).filter(
        and_(
            MlOrder.date_closed >= start,
            MlOrder.date_closed < end,
            MlOrder.status.in_(['paid', 'shipped', 'delivered'])
        )
    ).scalar()
    
    print(f"03/01/2026:")
    print(f"  Vendas do anúncio {comp.ad_id}: {vendas_ad}")
    print(f"  Vendas TOTAIS (todos produtos): {vendas_totais}")
    print(f"\nCONCLUSÃO:")
    print(f"  - Dashboard mostra: {vendas_totais} (TODOS os produtos)")
    print(f"  - Gráfico de Impacto mostra: {vendas_ad} (apenas produto monitorado)")

db.close()
