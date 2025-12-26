"""Compare sales_list calculation vs cash_flow calculation for first 2 orders"""
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

TAX_RATE = 0.056
ads_cache = {a.id: a for a in db.query(Ad).all()}
tiny_cache = {t.sku: t for t in db.query(TinyProduct).all()}

# Get first 2 orders (same as user's screenshot)
first_orders = [o for o in orders if o.status != 'cancelled'][:2]

print("=== DETAILED ANALYSIS OF FIRST 2 ORDERS ===\n")

for o in first_orders:
    dt_local = o.date_created.replace(tzinfo=tz_utc.utc).astimezone(tz_br)
    print(f"Order {o.ml_order_id} - Created: {dt_local}")
    print(f"  Order total_amount: {o.total_amount}")
    print(f"  Order shipping_cost: {o.shipping_cost}")
    
    for item in o.items:
        qty = int(item.quantity or 1)
        unit_price = float(item.unit_price or 0)
        item_revenue = unit_price * qty
        
        ad = ads_cache.get(item.ml_item_id)
        ad_cost = float(ad.cost or 0) if ad else 0.0
        
        tiny_cost = 0.0
        if ad_cost == 0 and item.sku:
            tp = tiny_cache.get(item.sku)
            if tp and tp.cost:
                tiny_cost = float(tp.cost)
        
        unit_cost = ad_cost if ad_cost > 0 else tiny_cost
        prod_cost = unit_cost * qty
        
        # Cash flow calculation
        tax_cost_cf = item_revenue * TAX_RATE
        fee_cost_cf = float(item.sale_fee or 0) * qty
        num_items = len(o.items)
        shipping_cost_cf = (float(o.shipping_cost or 0) / num_items) if num_items > 0 else 0
        
        total_cost_cf = prod_cost + tax_cost_cf + fee_cost_cf + shipping_cost_cf
        lucro_cf = item_revenue - total_cost_cf
        
        print(f"\n  Item: {item.title[:40]}")
        print(f"    SKU: {item.sku}")
        print(f"    Qty: {qty}, Unit Price: {unit_price}, Revenue: {item_revenue}")
        print(f"    Ad Cost: {ad_cost}, Tiny Cost: {tiny_cost}, Unit Cost Used: {unit_cost}")
        print(f"    sale_fee from DB: {item.sale_fee}")
        print(f"    --- CASH FLOW CALCULATION ---")
        print(f"    prod_cost: {prod_cost:.2f}")
        print(f"    tax_cost (5.6%): {tax_cost_cf:.2f}")
        print(f"    fee_cost (sale_fee*qty): {fee_cost_cf:.2f}")
        print(f"    shipping_cost: {shipping_cost_cf:.2f}")
        print(f"    TOTAL COST: {total_cost_cf:.2f}")
        print(f"    LUCRO (rev-cost): {lucro_cf:.2f}")
    print()
