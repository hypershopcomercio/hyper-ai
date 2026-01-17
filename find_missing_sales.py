from app.core.database import SessionLocal
from app.models.ml_order import MlOrder, MlOrderItem
from datetime import datetime
from sqlalchemy import func, and_

db = SessionLocal()

ad_id = "MLB3964133363"
day_start = datetime(2026, 1, 3, 0, 0, 0)
day_end = datetime(2026, 1, 4, 0, 0, 0)

# Buscar TODOS os pedidos (qualquer status) e agrupar por status
pedidos_por_status = db.query(
    MlOrder.status,
    func.count(MlOrderItem.id).label('count'),
    func.coalesce(func.sum(MlOrderItem.quantity), 0).label('qty')
).join(MlOrderItem).filter(
    and_(
        MlOrderItem.ml_item_id == ad_id,
        MlOrder.date_created >= day_start,
        MlOrder.date_created < day_end
    )
).group_by(MlOrder.status).all()

print(f"Produto: {ad_id}")
print(f"Pedidos em 03/01 por STATUS:\n")

total_itens = 0
total_qty = 0

for status, count, qty in pedidos_por_status:
    print(f"{status}: {count} itens, {qty} unidades")
    total_itens += count
    total_qty += qty

print(f"\nTOTAL: {total_itens} itens, {total_qty} unidades")
print(f"\nML mostra: 18 vendas brutas")
print(f"Esperado (sem cancelados): 15 vendas")
print(f"Query atual retorna: 13 vendas")
print(f"\nFaltam: {15 - 13} = 2 vendas!")

db.close()
