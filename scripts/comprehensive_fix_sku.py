"""
Search for SKU in all possible locations and fix cost
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.ad_variation import AdVariation
from app.models.tiny_product import TinyProduct
from app.models.ad_tiny_link import AdTinyLink

SKU_PATTERN = 'PISTA-COLOR-353M-CARRO'

db = SessionLocal()

print("=" * 60)
print(f"COMPREHENSIVE SEARCH FOR: {SKU_PATTERN}")
print("=" * 60)

# Search in Ads
print("\n1. Searching in ADS table:")
ads = db.query(Ad).filter(Ad.sku.like(f'%{SKU_PATTERN}%')).all()
if ads:
    for ad in ads:
        print(f"   ✓ Found Ad: {ad.id}")
        print(f"     SKU: {ad.sku}")
        print(f"     Cost: {ad.cost}")
        print(f"     Title: {ad.title[:60]}")
else:
    print("   No Ads found")

# Search in Variations
print("\n2. Searching in VARIATIONS table:")
variations = db.query(AdVariation).filter(AdVariation.sku.like(f'%{SKU_PATTERN}%')).all()
if variations:
    for var in variations:
        print(f"   ✓ Found Variation: {var.id}")
        print(f"     SKU: {var.sku}")
        print(f"     Ad ID: {var.ad_id}")
        
        # Get parent ad
        parent = db.query(Ad).filter(Ad.id == var.ad_id).first()
        if parent:
            print(f"     Parent Ad Cost: {parent.cost}")
            print(f"     Parent Ad Title: {parent.title[:60]}")
else:
    print("   No Variations found")

# Search in TinyProduct
print("\n3. Searching in TINY_PRODUCTS table:")
tiny_prods = db.query(TinyProduct).filter(TinyProduct.sku.like(f'%{SKU_PATTERN}%')).all()
if tiny_prods:
    for tp in tiny_prods:
        print(f"   ✓ Found TinyProduct: {tp.id}")
        print(f"     SKU: {tp.sku}")
        print(f"     Cost: {tp.cost}")
        print(f"     Name: {tp.name}")
else:
    print("   No TinyProducts found")

print("\n" + "=" * 60)
print("FIX STRATEGY:")
print("=" * 60)

# Try to fix
if tiny_prods and tiny_prods[0].cost > 0:
    tiny_prod = tiny_prods[0]
    print(f"\n✓ TinyProduct has cost: R$ {tiny_prod.cost:.2f}")
    
    # Find the ad to link
    target_ad = None
    if ads:
        target_ad = ads[0]
    elif variations:
        target_ad = db.query(Ad).filter(Ad.id == variations[0].ad_id).first()
    
    if target_ad:
        print(f"\n✓ Target Ad found: {target_ad.id}")
        
        # Check/create link
        link = db.query(AdTinyLink).filter(AdTinyLink.ad_id == target_ad.id).first()
        
        if link:
            if str(link.tiny_product_id) != str(tiny_prod.id):
                print(f"   ⚠ Link exists but wrong target: {link.tiny_product_id} -> {tiny_prod.id}")
                link.tiny_product_id = str(tiny_prod.id)
                db.commit()
                print(f"   ✓ Link updated")
            else:
                print(f"   ✓ Link already correct")
        else:
            print(f"   Creating link...")
            new_link = AdTinyLink(ad_id=target_ad.id, tiny_product_id=str(tiny_prod.id))
            db.add(new_link)
            db.commit()
            print(f"   ✓ Link created")
        
        # Update cost
        print(f"\n   Updating Ad cost: {target_ad.cost} -> {tiny_prod.cost}")
        target_ad.cost = tiny_prod.cost
        db.commit()
        print(f"   ✓ Cost updated to R$ {tiny_prod.cost:.2f}")
        
        print(f"\n✅ SUCCESS! Reload dashboard to see updated cost.")
    else:
        print(f"\n✗ No Ad found to link")
else:
    print(f"\n✗ No TinyProduct with cost found")

db.close()
