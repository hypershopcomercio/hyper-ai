"""
Debug script to test ML Ads Performance API response
"""
import sys
sys.path.insert(0, '.')

from datetime import date, timedelta
from app.core.database import SessionLocal
from app.services.meli_api import MeliApiService
from app.models.ml_order import MlOrder, MlOrderItem
from sqlalchemy.orm import joinedload

def main():
    db = SessionLocal()
    
    try:
        # Get orders from yesterday
        yesterday = date.today() - timedelta(days=1)
        
        print(f"Testing Ads API for date: {yesterday}")
        print("=" * 50)
        
        # Get item IDs from yesterday's orders
        orders = db.query(MlOrder).options(
            joinedload(MlOrder.items)
        ).filter(
            MlOrder.date_closed >= yesterday,
            MlOrder.date_closed < date.today(),
            MlOrder.status.in_(['paid', 'shipped', 'delivered'])
        ).all()
        
        print(f"Found {len(orders)} orders from yesterday")
        
        item_ids = set()
        for o in orders:
            for item in o.items:
                item_ids.add(item.ml_item_id)
        
        item_ids_list = list(item_ids)
        print(f"Unique item IDs: {len(item_ids_list)}")
        for i, item_id in enumerate(item_ids_list[:5]):
            print(f"  {i+1}. {item_id}")
        
        if not item_ids_list:
            print("No items to check")
            return
        
        # Initialize Meli Service and test API
        meli = MeliApiService(db_session=db)
        
        print(f"\nCalling get_ads_performance...")
        print(f"  Date range: {yesterday} to {yesterday}")
        print(f"  Item IDs: {item_ids_list[:3]}...")
        
        result = meli.get_ads_performance(item_ids_list, yesterday, yesterday)
        
        print(f"\nAPI Response:")
        print(f"  Type: {type(result)}")
        print(f"  Keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
        
        if result and "results" in result:
            results = result["results"]
            print(f"  Results count: {len(results)}")
            
            if results:
                for i, res in enumerate(results[:5]):
                    item_id = res.get("item_id")
                    metrics = res.get("metrics", {})
                    cost = metrics.get("cost", 0)
                    clicks = metrics.get("clicks", 0)
                    prints = metrics.get("prints", 0)
                    print(f"  [{i+1}] {item_id}: cost={cost}, clicks={clicks}, prints={prints}")
            else:
                print("  No results returned from API")
        else:
            print(f"  Raw result: {result}")
            
    finally:
        db.close()

if __name__ == "__main__":
    main()
