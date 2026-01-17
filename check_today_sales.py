from app.core.database import SessionLocal
from app.models.ml_order import MlOrder, MlOrderItem
from app.models.competitor_ad import CompetitorAd
from datetime import datetime
from sqlalchemy import func, and_

db = SessionLocal()

# Pegar ID do produto monitorado
comp = db.query(CompetitorAd).first()
if not comp:
    print("Nenhum concorrente encontrado")
    exit()

our_ad_id = comp.ad_id
print(f"Produto monitorado: {our_ad_id}\n")

# Vendas de ONTEM (03/01)
yesterday = datetime(2026, 1, 3, 0, 0, 0)
yesterday_end = datetime(2026, 1, 4, 0, 0, 0)

vendas_ontem = db.query(func.coalesce(func.sum(MlOrderItem.quantity), 0)).join(MlOrder).filter(
    and_(
        MlOrderItem.ml_item_id == our_ad_id,
        MlOrder.date_closed >= yesterday,
        MlOrder.date_closed < yesterday_end,
        MlOrder.status.in_(['paid', 'shipped', 'delivered'])
    )
).scalar()

# Vendas de HOJE (04/01)
today = datetime(2026, 1, 4, 0, 0, 0)
today_end = datetime(2026, 1, 5, 0, 0, 0)

vendas_hoje = db.query(func.coalesce(func.sum(MlOrderItem.quantity), 0)).join(MlOrder).filter(
    and_(
        MlOrderItem.ml_item_id == our_ad_id,
        MlOrder.date_closed >= today,
        MlOrder.date_closed < today_end,
        MlOrder.status.in_(['paid', 'shipped', 'delivered'])
    )
).scalar()

print(f"Vendas 03/01 (ONTEM): {vendas_ontem}")
print(f"Vendas 04/01 (HOJE): {vendas_hoje}")
print(f"\nDashboard provavelmente mostra: HOJE ({vendas_hoje})")
print(f"Gráfico mostra último ponto: ONTEM ({vendas_ontem})")

if vendas_hoje == 15:
    print(f"\n✅ CONFIRMADO! Dashboard mostra HOJE (15)")
    print(f"   Gráfico precisa incluir dados de HOJE também!")

db.close()
