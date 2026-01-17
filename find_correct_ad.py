from app.core.database import SessionLocal
from app.models.ml_order import MlOrder, MlOrderItem
from app.models.ad import Ad
from datetime import datetime
from sqlalchemy import func, and_

db = SessionLocal()

# Vendas de 03/01/2026
day_start = datetime(2026, 1, 3, 0, 0, 0)
day_end = datetime(2026, 1, 4, 0, 0, 0)

# Buscar TODOS os anúncios e suas vendas em 03/01
ads = db.query(Ad).all()

print("Vendas por anúncio em 03/01/2026:\n")
total_vendas = 0

for ad in ads:
    vendas = db.query(func.coalesce(func.sum(MlOrderItem.quantity), 0)).join(MlOrder).filter(
        and_(
            MlOrderItem.ml_item_id == ad.id,
            MlOrder.date_closed >= day_start,
            MlOrder.date_closed < day_end,
            MlOrder.status.in_(['paid', 'shipped', 'delivered'])
        )
    ).scalar()
    
    if vendas > 0:
        total_vendas += vendas
        print(f"{ad.id}: {vendas} vendas")

print(f"\nTOTAL: {total_vendas} vendas")
print(f"\nSe dashboard mostra 15, o anúncio que vendeu 15 é o correto!")

db.close()
