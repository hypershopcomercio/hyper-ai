"""
Script to sync variation costs from Tiny API.
Fetches all unique SKUs from MlOrderItem that don't have a TinyProduct record,
then creates TinyProduct records with cost from Tiny API.
"""

from app.core.database import SessionLocal
from app.models.ml_order import MlOrderItem
from app.models.tiny_product import TinyProduct
from app.services.tiny_api import TinyApiService
from sqlalchemy import distinct

def sync_variation_costs():
    db = SessionLocal()
    tiny_api = TinyApiService()
    
    try:
        # Get all unique SKUs from order items
        all_skus = db.query(distinct(MlOrderItem.sku)).filter(MlOrderItem.sku != None).all()
        all_skus = [sku[0] for sku in all_skus if sku[0]]
        
        print(f"Found {len(all_skus)} unique SKUs in order items")
        
        synced = 0
        skipped = 0
        errors = 0
        
        for sku in all_skus:
            # Check if already exists
            existing = db.query(TinyProduct).filter(TinyProduct.sku == sku).first()
            if existing:
                if existing.cost and existing.cost > 0:
                    skipped += 1
                    continue
                else:
                    # Exists but no cost, update it
                    pass
            
            # Fetch from Tiny API
            try:
                p_data = tiny_api.search_product(sku)
                if p_data and p_data.get("id"):
                    cost = float(p_data.get("preco_custo", 0) or 0)
                    
                    if existing:
                        existing.cost = cost
                        existing.name = p_data.get("nome", existing.name)
                        print(f"  Updated: {sku} -> cost={cost}")
                    else:
                        new_tp = TinyProduct(
                            id=str(p_data.get("id")),
                            sku=p_data.get("codigo"),
                            name=p_data.get("nome"),
                            cost=cost
                        )
                        db.add(new_tp)
                        print(f"  Created: {sku} -> cost={cost}")
                    
                    synced += 1
                else:
                    print(f"  Not found in Tiny: {sku}")
                    errors += 1
            except Exception as e:
                print(f"  Error for {sku}: {e}")
                errors += 1
        
        db.commit()
        print(f"\n=== SYNC COMPLETE ===")
        print(f"Synced: {synced}")
        print(f"Skipped (already had cost): {skipped}")
        print(f"Errors/Not found: {errors}")
        
    except Exception as e:
        print(f"Fatal error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    sync_variation_costs()
