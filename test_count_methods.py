from app.core.database import SessionLocal
from app.models.ml_order import MlOrder, MlOrderItem
from datetime import datetime
from sqlalchemy import func, and_

db = SessionLocal()

ad_id = "MLB3964133363"
day_start = datetime(2026, 1, 3, 0, 0, 0)
day_end = datetime(2026, 1, 4, 0, 0, 0)

# Quantidade de PEDIDOS
pedidos = db.query(func.count(MlOrder.id.distinct())).join(MlOrderItem).filter(
    and_(
        MlOrderItem.ml_item_id == ad_id,
        MlOrder.date_created >= day_start,
        MlOrder.date_created < day_end,
        MlOrder.status.in_(['paid', 'shipped', 'delivered'])
    )
).scalar()

# Quantidade de ITENS dentro dos pedidos
itens = db.query(func.count(MlOrderItem.id)).join(MlOrder).filter(
    and_(
        MlOrderItem.ml_item_id == ad_id,
        MlOrder.date_created >= day_start,
        MlOrder.date_created < day_end,
        MlOrder.status.in_(['paid', 'shipped', 'delivered'])
    )
).scalar()

# SOMA de quantidades
quantidade_total = db.query(func.coalesce(func.sum(MlOrderItem.quantity), 0)).join(MlOrder).filter(
    and_(
        MlOrderItem.ml_item_id == ad_id,
        MlOrder.date_created >= day_start,
        MlOrder.date_created < day_end,
        MlOrder.status.in_(['paid', 'shipped', 'delivered'])
    )
).scalar()

print(f"Produto: {ad_id} em 03/01/2026:")
print(f"\nPedidos (COUNT DISTINCT order_id): {pedidos}")
print(f"Itens (COUNT item_id): {itens}")
print(f"Quantidade Total (SUM quantity): {quantidade_total}")
print(f"\nDashboard mostra: 15")
print(f"\nSe algum dos valores acima = 15, esse é o que está usando!")

db.close()
