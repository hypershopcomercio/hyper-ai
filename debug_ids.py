
import sys
import os
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.forecast_learning import ForecastLog

def debug_ids():
    db = SessionLocal()
    try:
        log_id = 664
        print(f"--- Debugging Log {log_id} ---")
        
        log = db.query(ForecastLog).filter(ForecastLog.id == log_id).first()
        if not log:
            print("Log not found")
            return

        print(f"Log Realized Value: {log.valor_real}")
        
        # Find Product ID by Title
        from app.models.product_forecast import ProductForecast
        target_title_part = "780 Litros"
        
        pf = db.query(ProductForecast).filter(ProductForecast.title.ilike(f"%{target_title_part}%")).first()
        if pf:
             print(f"--- Product Forecast Item ---")
             print(f"Title: {pf.title}")
             print(f"MLB ID: {pf.mlb_id}")
             print(f"SKU: {pf.sku}")
        else:
             print("Product NOT found in Forecast.")

        # Find Sale for this item by keyword
        from app.models.ml_order import MlOrderItem, MlOrder
        
        print(f"--- Searching for Sales of 780 Litros ---")
        # Join with MlOrder to get date
        results = db.query(MlOrderItem, MlOrder).join(MlOrder, MlOrderItem.ml_order_id == MlOrder.ml_order_id)\
            .filter(MlOrderItem.title.ilike(f"%{target_title_part}%"))\
            .order_by(MlOrder.date_created.desc())\
            .limit(5).all()
            
        for item, order in results:
            print(f"Sold: {item.title}")
            print(f"  ID: {item.ml_item_id}")
            print(f"  Price: {item.unit_price}")
            print(f"  Date Created: {order.date_created}")



        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_ids()
