from app.core.database import SessionLocal
from app.models.ml_order import MlOrder, MlOrderItem
from datetime import datetime
from sqlalchemy import func, and_

db = SessionLocal()

# Produto mostrado na imagem
ad_id = "MLB4200110239"

# Vendas do dia 03/01/2026
start = datetime(2026, 1, 3, 0, 0, 0)
end = datetime(2026, 1, 4, 0, 0, 0)

vendas_reais = db.query(func.coalesce(func.sum(MlOrderItem.quantity), 0)).join(MlOrder).filter(
    and_(
        MlOrderItem.ml_item_id == ad_id,
        MlOrder.date_closed >= start,
        MlOrder.date_closed < end,
        MlOrder.status.in_(['paid', 'shipped', 'delivered'])
    )
).scalar()

print(f"Produto: {ad_id}")
print(f"Vendas REAIS em 03/01/2026: {vendas_reais}")
print(f"Gráfico mostrando: 13")
print(f"\nDivergência: {abs(int(vendas_reais) - 13)} unidades")

db.close()
