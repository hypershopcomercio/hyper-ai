"""Debug shipping and all costs for 00h bucket orders"""
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

TAX_RATE = 0.056
ads_cache = {a.id: a for a in db.query(Ad).all()}
tiny_cache = {t.sku: t for t in db.query(TinyProduct).all()}

start = datetime.combine(today, datetime.min.time())
orders = db.query(MlOrder).options(joinedload(MlOrder.items)).filter(
    MlOrder.date_closed >= start
).all()

print("=== 00h BUCKET ORDERS - DETAILED ===\n")
total_cf_cost = 0
total_expected_cost = 0

for o in orders:
    if o.status == 'cancelled':
        continue
    
    dt_local = (o.date_closed or o.date_created).replace(tzinfo=tz_utc.utc).astimezone(tz_br)
    h = dt_local.hour
    bucket = (h // 2) * 2
    
    if bucket == 0:
        print(f"Order: {o.ml_order_id}")
        print(f"  date_closed: {o.date_closed}")
        print(f"  shipping_cost in DB: {o.shipping_cost}")
        print(f"  total_amount: {o.total_amount}")
        
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
            
            total_item_cost = prod_cost + tax_cost + fee_cost + shipping_cost
            total_cf_cost += total_item_cost
            
            print(f"\n  Item: {item.title[:40]}")
            print(f"    SKU: {item.sku}")
            print(f"    Revenue: {item_revenue}")
            print(f"    prod_cost: {prod_cost} (unit_cost={unit_cost} from ad={ad.cost if ad else None}, tiny={tiny_cache.get(item.sku).cost if tiny_cache.get(item.sku) else None})")
            print(f"    tax_cost: {tax_cost:.2f} (revenue * {TAX_RATE})")
            print(f"    fee_cost: {fee_cost} (sale_fee={item.sale_fee} * qty={qty})")
            print(f"    ship_cost: {shipping_cost:.2f} (order_ship={o.shipping_cost} / {num_items} items)")
            print(f"    TOTAL item cost: {total_item_cost:.2f}")
        print()

print(f"=== CASH FLOW CALCULATION TOTAL ===")
print(f"Total cost from manual calculation: {total_cf_cost:.2f}")
