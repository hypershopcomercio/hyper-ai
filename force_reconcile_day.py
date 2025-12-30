
import sys
import os
import json
from datetime import timedelta, timezone, datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.attributes import flag_modified

sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.forecast_learning import ForecastLog
from app.models.ml_order import MlOrder, MlOrderItem

def force_reconcile_day():
    db = SessionLocal()
    try:
        # Target Day: 2025-12-28
        target_day_start = datetime(2025, 12, 28, 0, 0, 0)
        target_day_end = datetime(2025, 12, 28, 23, 59, 59)
        
        logs = db.query(ForecastLog).filter(
            ForecastLog.hora_alvo >= target_day_start,
            ForecastLog.hora_alvo <= target_day_end
        ).all()
        
        print(f"Found {len(logs)} logs for {target_day_start.date()}")
        
        updated_count = 0
        total_items_updated = 0
        
        tz_br = timezone(timedelta(hours=-3))

        for log in logs:
            print(f"Processing Log {log.id} ({log.hora_alvo})...")
            
            # 1. Strict Timezone Logic
            start_naive = log.hora_alvo
            end_naive = start_naive + timedelta(hours=1)
            
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
            
            # Query
            realized_sales_query = db.query(
                MlOrderItem.ml_item_id,
                func.sum(MlOrderItem.quantity),
                MlOrderItem.sku,
                func.sum(MlOrderItem.unit_price * MlOrderItem.quantity) # Total Value
            ).join(MlOrder, MlOrderItem.ml_order_id == MlOrder.ml_order_id)\
            .filter(MlOrder.date_closed >= start_utc_naive)\
            .filter(MlOrder.date_closed < end_utc_naive)\
            .filter(MlOrder.status == 'paid')\
            .group_by(MlOrderItem.ml_item_id, MlOrderItem.sku).all()
            
            sales_by_id = {}
            total_real_value = 0.0
            
            for r_item_id, r_qty, r_sku, r_val in realized_sales_query:
                qty = float(r_qty or 0)
                sales_by_id[r_item_id] = qty
                total_real_value += float(r_val or 0)
                
            # Update Mix
            fatores = log.fatores_usados or {}
            product_mix = fatores.get('_product_mix') or []
            
            enhanced_mix = []
            log_items_updated = 0
            
            for p in product_mix:
                p_copy = p.copy()
                mlb_id = str(p.get('mlb_id')).strip()
                
                real_qty = sales_by_id.get(mlb_id, 0.0)
                p_copy['realized_units'] = real_qty
                
                if real_qty > 0:
                    log_items_updated += 1
                    
                # Accuracy logic (simple check)
                p_copy['accuracy_hit'] = (real_qty > 0 and p.get('units_expected', 0) > 0.1)
                enhanced_mix.append(p_copy)

            enhanced_mix.sort(key=lambda x: (x.get('realized_units', 0), x.get('units_expected', 0)), reverse=True)
            
            # Commit Updates
            fatores['_product_mix'] = enhanced_mix
            log.fatores_usados = fatores
            log.calibrated = 'Y'
            
            valor_previsto_f = float(log.valor_previsto or 0)
            
            if total_real_value > 0 and valor_previsto_f > 0:
                 error = ((valor_previsto_f - total_real_value) / total_real_value) * 100
                 log.erro_percentual = error
            elif total_real_value == 0 and valor_previsto_f > 0:
                 log.erro_percentual = 100.0
            else:
                 log.erro_percentual = 0.0

            flag_modified(log, 'fatores_usados')
            updated_count += 1
            total_items_updated += log_items_updated
            print(f"  -> Updated {log_items_updated} items. Total Real: {total_real_value}")

        db.commit()
        print(f"DONE. Updated {updated_count} logs with {total_items_updated} item matches.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    force_reconcile_day()
