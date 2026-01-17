from app.core.database import SessionLocal
from app.models.competitor_ad import CompetitorAd
from app.models.ml_order import MlOrder, MlOrderItem
from app.models.ad import Ad
from datetime import datetime
from sqlalchemy import func, and_

db = SessionLocal()

print("="*70)
print("INVESTIGANDO ESTRUTURA DE DADOS")
print("="*70)

# Listar todos os concorrentes
competitors = db.query(CompetitorAd).all()

print(f"\nTotal de concorrentes cadastrados: {len(competitors)}\n")

for comp in competitors:
    print(f"\nConcorrente: {comp.competitor_id}")
    print(f"  Nosso anúncio (ad_id): {comp.ad_id}")
    
    # Buscar info do nosso anúncio
    our_ad = db.query(Ad).filter(Ad.id == comp.ad_id).first()
    if our_ad:
        print(f"  Título: {our_ad.title}")
        print(f"  Preço: R$ {our_ad.price}")
    
    # Vendas de 03/01
    day_start = datetime(2026, 1, 3, 0, 0, 0)
    day_end = datetime(2026, 1, 4, 0, 0, 0)
    
    vendas = db.query(func.coalesce(func.sum(MlOrderItem.quantity), 0)).join(MlOrder).filter(
        and_(
            MlOrderItem.ml_item_id == comp.ad_id,
            MlOrder.date_closed >= day_start,
            MlOrder.date_closed < day_end,
            MlOrder.status.in_(['paid', 'shipped', 'delivered'])
        )
    ).scalar()
    
    print(f"  Vendas em 03/01: {vendas}")
    
    if vendas == 15:
        print(f"  ✅ ESTE É O PRODUTO CORRETO! (vendeu 15)")

print("\n" + "="*70)
print("CONCLUSÃO:")
print("Se algum mostrou 15 vendas, esse é o produto que o gráfico deveria usar!")
print("="*70)

db.close()
