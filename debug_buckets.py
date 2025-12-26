"""Debug script to check cash flow bucket calculations"""
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder, MlOrderItem
from app.models.ad import Ad
from app.models.tiny_product import TinyProduct
from datetime import datetime, timezone as tz_utc
from pytz import timezone
from sqlalchemy.orm import joinedload

db = SessionLocal()
tz_br = timezone('America/Sao_Paulo')
today = datetime.now(tz_br).date()

start = datetime.combine(today, datetime.min.time())
orders = db.query(MlOrder).options(joinedload(MlOrder.items)).filter(
    MlOrder.date_created >= start
).all()

buckets = {}
TAX_RATE = 0.056
ads_cache = {a.id: a for a in db.query(Ad).all()}
tiny_cache = {t.sku: t for t in db.query(TinyProduct).all()}

print(f"Total orders today (date_created >= {start}): {len(orders)}")
print()

for o in orders:
    if o.status == 'cancelled': 
        continue
    
    dt_local = o.date_created.replace(tzinfo=tz_utc.utc).astimezone(tz_br)
    h = (dt_local.hour // 2) * 2
    key = f'{h:02}h'
    
    if key not in buckets:
        buckets[key] = {'receita': 0, 'custo': 0, 'orders': 0}
    
    buckets[key]['orders'] += 1
    order_receita = float(o.total_amount or 0)
    order_custo = 0
    
    for item in o.items:
        qty = int(item.quantity or 1)
        unit_price = float(item.unit_price or 0)
        item_revenue = unit_price * qty
        
        ad = ads_cache.get(item.ml_item_id)
        unit_cost = float(ad.cost or 0) if ad else 0.0
        if unit_cost == 0 and item.sku:
            tp = tiny_cache.get(item.sku)
            if tp and tp.cost:
                unit_cost = float(tp.cost)
        
        prod_cost = unit_cost * qty
        tax_cost = item_revenue * TAX_RATE
        fee_cost = float(item.sale_fee or 0) * qty
        num_items = len(o.items)
        shipping_cost = (float(o.shipping_cost or 0) / num_items) if num_items > 0 else 0
        
        item_cost = prod_cost + tax_cost + fee_cost + shipping_cost
        order_custo += item_cost
    
    buckets[key]['receita'] += order_receita
    buckets[key]['custo'] += order_custo

print("Bucket breakdown:")
print("-" * 60)
for k in sorted(buckets.keys()):
    v = buckets[k]
    lucro = v['receita'] - v['custo']
    print(f"{k}: Orders={v['orders']:2}, Receita=R${v['receita']:8.2f}, Custo=R${v['custo']:8.2f}, Lucro=R${lucro:8.2f}")

print("-" * 60)
totals = {'receita': sum(v['receita'] for v in buckets.values()),
          'custo': sum(v['custo'] for v in buckets.values())}
print(f"TOTAL: Receita=R${totals['receita']:.2f}, Custo=R${totals['custo']:.2f}, Lucro=R${totals['receita']-totals['custo']:.2f}")
