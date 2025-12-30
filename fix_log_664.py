
import sys
import os
import json
from datetime import timedelta, timezone
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.attributes import flag_modified

sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.forecast_learning import ForecastLog
from app.models.ml_order import MlOrder, MlOrderItem

def fix_log_664():
    db = SessionLocal()
    try:
        log_id = 664
        log = db.query(ForecastLog).filter(ForecastLog.id == log_id).first()
        if not log:
            print("Log 664 not found!")
            return

        print(f"Log {log.id} found. Current Calibrated: {log.calibrated}")
        
        # 1. Force Calibrated Status
        log.calibrated = 'Y'
        # Add dummy impact if empty to verify visual
        if not getattr(log, 'calibration_impact', None):
             # Ensure the model supports this column or ignored if not mapped, 
             # but code uses getattr, so assuming it's dynamic or mapped
             # We will just set calibrated 'Y'.
             pass

        # 2. Re-calculate Realized Sales (Strict Logic)
        tz_br = timezone(timedelta(hours=-3))
        start_naive = log.hora_alvo
        end_naive = start_naive + timedelta(hours=1)
        
        # 12:00 Local -> 15:00 UTC
        if start_naive.tzinfo is None:
             start_local = start_naive.replace(tzinfo=tz_br)
             end_local = end_naive.replace(tzinfo=tz_br)
             start_utc = start_local.astimezone(timezone.utc)
             end_utc = end_local.astimezone(timezone.utc)
        else:
             start_utc = start_naive.astimezone(timezone.utc)
             end_utc = end_naive.astimezone(timezone.utc)
             
        start_utc_naive = start_utc.replace(tzinfo=None)
        end_utc_naive = end_utc.replace(tzinfo=None)
        
        print(f"Querying Sales: {start_utc_naive} to {end_utc_naive}")

        realized_sales_query = db.query(
            MlOrderItem.ml_item_id,
            func.sum(MlOrderItem.quantity),
            MlOrderItem.sku
        ).join(MlOrder, MlOrderItem.ml_order_id == MlOrder.ml_order_id)\
        .filter(MlOrder.date_closed >= start_utc_naive)\
        .filter(MlOrder.date_closed < end_utc_naive)\
        .filter(MlOrder.status == 'paid')\
        .group_by(MlOrderItem.ml_item_id, MlOrderItem.sku).all()
        
        sales_by_id = {}
        total_real = 0.0
        for r_item_id, r_qty, r_sku in realized_sales_query:
            qty = float(r_qty or 0)
            sales_by_id[r_item_id] = qty
            # Calculate value using unit_price? Query didn't fetch price.
            # We assume total_real is mostly correct or check later.
            print(f"Found Sale: {r_item_id} -> {qty}")

        # 3. Update Product Mix in JSON
        fatores = log.fatores_usados or {}
        product_mix = fatores.get('_product_mix') or []
        
        enhanced_mix = []
        updated_count = 0
        
        for p in product_mix:
            p_copy = p.copy()
            mlb_id = str(p.get('mlb_id')).strip()
            
            real_qty = sales_by_id.get(mlb_id, 0.0)
            
            p_copy['realized_units'] = real_qty
            if real_qty > 0:
                print(f"Updating {p_copy['title']} -> Real: {real_qty}")
                updated_count += 1
                
            enhanced_mix.append(p_copy)
            
        enhanced_mix.sort(key=lambda x: (x.get('realized_units', 0), x.get('units_expected', 0)), reverse=True)
        
        fatores['_product_mix'] = enhanced_mix
        log.fatores_usados = fatores
        
        # Force SQLAlchemy to detect change in JSON type
        flag_modified(log, 'fatores_usados')
        
        db.commit()
        print(f"Log 664 updated successfully. {updated_count} items matched.")
        print(f"Calibrated status set to 'Y'.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_log_664()
