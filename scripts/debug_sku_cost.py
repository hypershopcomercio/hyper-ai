"""
Investigate SKU cost loss issue
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.tiny_product import TinyProduct
from app.models.ad_tiny_link import AdTinyLink
from app.models.ad_variation import AdVariation

SKU = 'PISTA-COLOR-353M-CARRO'

db = SessionLocal()

print("=" * 60)
print(f"INVESTIGATING SKU: {SKU}")
print("=" * 60)

# 1. Check Ad
print("\n1. ADS with this SKU:")
ads = db.query(Ad).filter(Ad.sku == SKU).all()
if ads:
    for ad in ads:
        print(f"   ID: {ad.id}")
        print(f"   Title: {ad.title[:60]}")
        print(f"   SKU: {ad.sku}")
        print(f"   Cost: {ad.cost}")
        print(f"   Status: {ad.status}")
        print(f"   Last Updated: {ad.last_updated}")
        print()
else:
    print("   NO ADS FOUND with this SKU")

# 2. Check Variations
print("\n2. VARIATIONS with this SKU:")
variations = db.query(AdVariation).filter(AdVariation.sku == SKU).all()
if variations:
    for var in variations:
        print(f"   Var ID: {var.id}")
        print(f"   Ad ID: {var.ad_id}")
        print(f"   SKU: {var.sku}")
        print(f"   Price: {var.price}")
        print(f"   Qty: {var.available_quantity}")
        
        # Check parent ad
        parent_ad = db.query(Ad).filter(Ad.id == var.ad_id).first()
        if parent_ad:
            print(f"   Parent Ad Cost: {parent_ad.cost}")
        print()
else:
    print("   NO VARIATIONS FOUND with this SKU")

# 3. Check TinyProduct
print("\n3. TINY PRODUCT with this SKU:")
tiny_products = db.query(TinyProduct).filter(TinyProduct.sku == SKU).all()
if tiny_products:
    for tp in tiny_products:
        print(f"   Tiny ID: {tp.id}")
        print(f"   SKU: {tp.sku}")
        print(f"   Name: {tp.name}")
        print(f"   Cost: {tp.cost}")
        print(f"   Last Updated: {tp.last_updated}")
        print()
else:
    print("   NO TINY PRODUCT FOUND with this SKU")

# 4. Check Links
print("\n4. AD-TINY LINKS:")
if ads:
    for ad in ads:
        link = db.query(AdTinyLink).filter(AdTinyLink.ad_id == ad.id).first()
        if link:
            print(f"   Ad {link.ad_id} -> Tiny {link.tiny_product_id}")
            
            # Check linked Tiny product
            linked_tp = db.query(TinyProduct).filter(TinyProduct.id == link.tiny_product_id).first()
            if linked_tp:
                print(f"      Linked Tiny SKU: {linked_tp.sku}")
                print(f"      Linked Tiny Cost: {linked_tp.cost}")
        else:
            print(f"   NO LINK for Ad {ad.id}")
        print()

if variations:
    for var in variations:
        parent_ad = db.query(Ad).filter(Ad.id == var.ad_id).first()
        if parent_ad:
            link = db.query(AdTinyLink).filter(AdTinyLink.ad_id == parent_ad.id).first()
            if link:
                print(f"   Variation's Parent Ad {link.ad_id} -> Tiny {link.tiny_product_id}")
                
                linked_tp = db.query(TinyProduct).filter(TinyProduct.id == link.tiny_product_id).first()
                if linked_tp:
                    print(f"      Linked Tiny SKU: {linked_tp.sku}")
                    print(f"      Linked Tiny Cost: {linked_tp.cost}")
            else:
                print(f"   NO LINK for Variation's Parent Ad {parent_ad.id}")
            print()

print("\n" + "=" * 60)
print("DIAGNOSIS:")
print("=" * 60)

if tiny_products and tiny_products[0].cost > 0:
    print("✓ TinyProduct EXISTS with COST")
    
    if ads and ads[0].cost == 0:
        print("✗ Ad has SKU but COST = 0")
        print("  → ISSUE: Ad not linked to TinyProduct or sync failed")
        print("  → SOLUTION: Force sync or create link")
    
    if variations and not ads:
        print("✓ SKU is in VARIATION, not Ad")
        parent_ad = db.query(Ad).filter(Ad.id == variations[0].ad_id).first()
        if parent_ad and parent_ad.cost == 0:
            print("✗ Parent Ad has COST = 0")
            print("  → ISSUE: Parent Ad not linked to variation's Tiny product")
            print("  → SOLUTION: Create link from parent Ad to Tiny product")
else:
    print("✗ NO TinyProduct with cost found")
    print("  → ISSUE: Product not synced from Tiny ERP")
    print("  → SOLUTION: Run Tiny sync for this SKU")

db.close()
