import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Try verifying imports
try:
    from app.db.base import Base
except ImportError:
    # If app is not a package, maybe we need to adjust or check structure
    # Let's assume standard structure: ./app/db/base.py exists
    print("Error importing app.db.base. Checking path:", sys.path)
    pass

from app.models.ml_order import MlOrder, MlOrderItem
from app.models.tiny_product import TinyProduct

# Database setup
DATABASE_URL = "postgresql://postgres:gWh28%40dGcMp@localhost:5432/hyper"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def debug_roupao():
    print("--- Debugging Roupão Cost ---")
    
    # 1. Find the order item for "Roupão"
    # Search by title likeness
    items = db.query(MlOrderItem).filter(MlOrderItem.title.ilike("%Roupão%")).limit(5).all()
    
    if not items:
        print("No matches for 'Roupão' in MlOrderItem tables.")
        return

    print(f"Found {len(items)} items matching 'Roupão' in orders.")
    
    target_sku = None
    
    for item in items:
        print(f"\nItem: {item.title}")
        print(f"  Item ID: {item.ml_item_id}")
        print(f"  SKU in Order: '{item.sku}'")
        
        target_sku = item.sku
        if target_sku:
            # Check TinyProduct
            tiny_prod = db.query(TinyProduct).filter(TinyProduct.sku == target_sku).first()
            if tiny_prod:
                print(f"  [MATCH] Found in TinyProduct!")
                print(f"    Tiny SKU: '{tiny_prod.sku}'")
                print(f"    Cost: {tiny_prod.cost}")
                print(f"    ID: {tiny_prod.id}")
            else:
                print(f"  [MISSING] SKU '{target_sku}' NOT found in TinyProduct.")
                
                # Try finding in Tiny with loose search
                print("    Trying loose search in Tiny matching SKU content...")
                loose_match = db.query(TinyProduct).filter(TinyProduct.sku.ilike(f"%{target_sku.strip()}%")).first()
                if loose_match:
                     print(f"    [POTENTIAL MATCH] Found '{loose_match.sku}' with cost {loose_match.cost}")
                else:
                     print("    No loose match found either.")

        else:
            print("  SKU is None or empty in Order Item.")

if __name__ == "__main__":
    debug_roupao()
