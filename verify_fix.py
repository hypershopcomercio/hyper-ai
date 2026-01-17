from app.core.database import SessionLocal
from app.models.ml_order import MlOrder, MlOrderItem
from datetime import datetime
from sqlalchemy import func, and_

db = SessionLocal()

# Vendas de 03/01 com date_created (como o Dashboard)
ad_id = "MLB3964133363"
day_start = datetime(2026, 1, 3, 0, 0, 0)
day_end = datetime(2026, 1, 4, 0, 0, 0)

vendas_created = db.query(func.coalesce(func.sum(MlOrderItem.quantity), 0)).join(MlOrder).filter(
    and_(
        MlOrderItem.ml_item_id == ad_id,
        MlOrder.date_created >= day_start,
        MlOrder.date_created < day_end,
        MlOrder.status.in_(['paid', 'shipped', 'delivered'])
    )
).scalar()

vendas_closed = db.query(func.coalesce(func.sum(MlOrderItem.quantity), 0)).join(MlOrder).filter(
    and_(
        MlOrderItem.ml_item_id == ad_id,
        MlOrder.date_closed >= day_start,
        MlOrder.date_closed < day_end,
        MlOrder.status.in_(['paid', 'shipped', 'delivered'])
    )
).scalar()

print(f"Produto: {ad_id}")
print(f"\nVendas 03/01 usando date_created: {vendas_created}")
print(f"Vendas 03/01 usando date_closed: {vendas_closed}")
print(f"\nDashboard deveria mostrar: {vendas_created}")

if vendas_created == 15:
    print(f"\n✅ CORRETO! Agora bate com o Dashboard!")
elif vendas_created == 13:
    print(f"\n❌ Ainda divergente. Preciso investigar mais...")
else:
    print(f"\n⚠️  Valor inesperado: {vendas_created}")

db.close()
