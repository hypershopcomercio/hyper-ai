
import sys
import os
import json
from datetime import timedelta, timezone
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.forecast_learning import ForecastLog
from app.models.ml_order import MlOrder, MlOrderItem

def debug_mapping():
    db = SessionLocal()
    try:
        log_id = 664
        log = db.query(ForecastLog).filter(ForecastLog.id == log_id).first()
        print(f"Log ID: {log.id}")
        
        # 1. Get Mix
        fatores = log.fatores_usados or {}
        product_mix = fatores.get('_product_mix') or []
        print(f"Product Mix Size: {len(product_mix)}")
        
        target_title = "780 Litros"
        target_prod = None
        for p in product_mix:
            if target_title in p.get('title', ''):
                target_prod = p
                break
        
        if not target_prod:
            print("Target Product '780 Litros' NOT found in mix!")
            return

        print(f"Target Product ID in Mix: '{target_prod.get('mlb_id')}' (Type: {type(target_prod.get('mlb_id'))})")
        print(f"Target Product SKU: '{target_prod.get('sku')}'")

        # 2. Run Query (Strict Logic)
        tz_br = timezone(timedelta(hours=-3))
        start_naive = log.hora_alvo
        end_naive = start_naive + timedelta(hours=1)
        
        start_local = start_naive.replace(tzinfo=tz_br)
        end_local = end_naive.replace(tzinfo=tz_br)
        start_utc = start_local.astimezone(timezone.utc)
        end_utc = end_local.astimezone(timezone.utc)
        
        start_utc_naive = start_utc.replace(tzinfo=None)
        end_utc_naive = end_utc.replace(tzinfo=None)
        
        print(f"Query Window: {start_utc_naive} to {end_utc_naive}")

        realized_sales_query = db.query(
            MlOrderItem.ml_item_id,
            func.sum(MlOrderItem.quantity),
            MlOrderItem.sku
        ).join(MlOrder, MlOrderItem.ml_order_id == MlOrder.ml_order_id)\
        .filter(MlOrder.date_closed >= start_utc_naive)\
        .filter(MlOrder.date_closed < end_utc_naive)\
        .filter(MlOrder.status == 'paid')\
        .group_by(MlOrderItem.ml_item_id, MlOrderItem.sku).all()
        
        print(f"Sales Found in Window: {len(realized_sales_query)}")
        
        sales_by_id = {}
        for r_item_id, r_qty, r_sku in realized_sales_query:
            if r_item_id == target_prod.get('mlb_id'):
                print(f"MATCH FOUND IN QUERY RESULTS! ID={r_item_id}, Qty={r_qty}")
            sales_by_id[r_item_id] = float(r_qty or 0)
            
        print(f"Sales Keys: {list(sales_by_id.keys())}")
        
        # 3. Match Logic
        mlb_id = str(target_prod.get('mlb_id')).strip()
        print(f"Lookup ID: '{mlb_id}'")
        
        real_qty = sales_by_id.get(mlb_id, 0.0)
        print(f"Direct Match Result: {real_qty}")

    finally:
        db.close()

if __name__ == "__main__":
    debug_mapping()
