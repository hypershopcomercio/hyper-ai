import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import func
from decimal import Decimal

# Add project root to path - ROBUSTLY
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.ml_order import MlOrder, MlOrderItem
from app.models.product_forecast import ProductForecast

def test_sync():
    db = SessionLocal()
    try:
        # Find the product
        print("Searching for Piscina Intex...")
        product = db.query(Ad).filter(Ad.title.ilike("%Piscina Intex Redonda 168%")).first()
        
        if not product:
            print("Product not found in Ad table!")
            return
            
        print(f"Found Ad: {product.title} (ID: {product.id})")
        
        # Calculate date ranges
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        valid_statuses = ['paid', 'shipped', 'delivered']
        
        print(f"Week ago: {week_ago}")
        
        # Sales 7d
        sales_7d = db.query(
            func.sum(MlOrderItem.quantity).label('qty'),
            func.sum(MlOrderItem.unit_price * MlOrderItem.quantity).label('revenue')
        ).join(MlOrder).filter(
            MlOrderItem.ml_item_id == product.id,
            MlOrder.date_closed >= week_ago,
            MlOrder.status.in_(valid_statuses)
        ).first()
        
        qty_7d = sales_7d.qty or 0
        rev_7d = sales_7d.revenue or 0
        avg_7d = qty_7d / 7
        
        print(f"Sales 7d: Qty={qty_7d}, Rev={rev_7d}")
        print(f"Avg Units 7d: {avg_7d}")
        
        # Check ProductForecast current value
        pf = db.query(ProductForecast).filter(ProductForecast.mlb_id == product.id).first()
        if pf:
            print(f"Current PF Avg 7d: {pf.avg_units_7d}")
        else:
            print("No ProductForecast record found.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_sync()
