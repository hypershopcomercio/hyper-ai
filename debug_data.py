from app.core.database import SessionLocal
from app.models.competitor_intelligence import CompetitorMetricsHistory

db = SessionLocal()
metrics = db.query(CompetitorMetricsHistory).order_by(CompetitorMetricsHistory.timestamp.desc()).limit(10).all()

print("Últimos 10 registros salvos:\n")
for m in metrics:
    print(f"{m.timestamp.strftime('%d/%m/%Y')}:")
    print(f"  Nossas vendas: {m.our_sales} | Preço: R$ {m.our_price}")
    print(f"  Concorrente: {m.sales} | Preço: R$ {m.price}")
    print()

db.close()
