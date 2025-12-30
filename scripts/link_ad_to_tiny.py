"""
Find ML Ad with SKU and create link to TinyProduct
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.ad_variation import AdVariation
from app.models.tiny_product import TinyProduct
from app.models.ad_tiny_link import AdTinyLink
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SKU = 'PISTA-COLOR-353M-CARRO'

db = SessionLocal()

print("=" * 60)
print(f"LINKING ML AD TO TINY PRODUCT: {SKU}")
print("=" * 60)

try:
    # 1. Find TinyProduct
    tiny_prod = db.query(TinyProduct).filter(TinyProduct.sku == SKU).first()
    
    if not tiny_prod:
        print(f"\n✗ TinyProduct with SKU {SKU} not found")
        print("  Run force_sync_sku.py first")
        sys.exit(1)
    
    print(f"\n✓ TinyProduct found:")
    print(f"   ID: {tiny_prod.id}")
    print(f"   Cost: R$ {tiny_prod.cost:.2f}")
    
    # 2. Find Ad or Variation with this SKU
    ad = db.query(Ad).filter(Ad.sku == SKU).first()
    
    if not ad:
        # Check variations
        variation = db.query(AdVariation).filter(AdVariation.sku == SKU).first()
        
        if variation:
            print(f"\n✓ Found in VARIATION {variation.id}")
            # Get parent ad
            ad = db.query(Ad).filter(Ad.id == variation.ad_id).first()
            print(f"   Parent Ad: {ad.id if ad else 'NOT FOUND'}")
        else:
            print(f"\n✗ No Ad or Variation with SKU {SKU} found in ML database")
            print("  Possible reasons:")
            print("  - SKU not configured in ML listing")
            print("  - ML sync hasn't run yet")
            print("  - SELLER_SKU attribute not set in ML")
            print("\n  SOLUTION: Run Ads sync or check ML listing configuration")
            sys.exit(1)
    else:
        print(f"\n✓ Found Ad: {ad.id}")
        print(f"   Title: {ad.title[:60]}")
    
    if not ad:
        print("\n✗ No parent Ad found")
        sys.exit(1)
    
    # 3. Check if link already exists
    existing_link = db.query(AdTinyLink).filter(AdTinyLink.ad_id == ad.id).first()
    
    if existing_link:
        if str(existing_link.tiny_product_id) == str(tiny_prod.id):
            print(f"\n✓ Link already exists: Ad {ad.id} -> Tiny {tiny_prod.id}")
        else:
            print(f"\n⚠ Link exists but points to different Tiny product")
            print(f"   Current: Tiny {existing_link.tiny_product_id}")
            print(f"   Should be: Tiny {tiny_prod.id}")
            print(f"   Updating link...")
            existing_link.tiny_product_id = str(tiny_prod.id)
            db.commit()
            print(f"   ✓ Link updated")
    else:
        # Create new link
        print(f"\n✓ Creating link: Ad {ad.id} -> Tiny {tiny_prod.id}")
        new_link = AdTinyLink(
            ad_id=ad.id,
            tiny_product_id=str(tiny_prod.id)
        )
        db.add(new_link)
        db.commit()
        print(f"   ✓ Link created successfully")
    
    # 4. Update Ad cost
    print(f"\n✓ Updating Ad cost from R$ {ad.cost} to R$ {tiny_prod.cost:.2f}")
    ad.cost = tiny_prod.cost
    db.commit()
    
    print("\n" + "=" * 60)
    print("SUCCESS!")
    print("=" * 60)
    print(f"✓ Ad {ad.id} is now linked to TinyProduct {tiny_prod.id}")
    print(f"✓ Cost updated to R$ {tiny_prod.cost:.2f}")
    print(f"\nReload HyperPerform page to see updated cost!")
    
except Exception as e:
    logger.error(f"Error: {e}")
    print(f"\n✗ ERROR: {e}")
    db.rollback()
    import traceback
    traceback.print_exc()
finally:
    db.close()
