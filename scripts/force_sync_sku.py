"""
Force sync specific SKU from Tiny ERP
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.tiny_product import TinyProduct
from app.services.tiny_api import TinyApiService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SKU = 'PISTA-COLOR-353M-CARRO'

db = SessionLocal()
tiny_service = TinyApiService()

print("=" * 60)
print(f"FORCING TINY SYNC FOR SKU: {SKU}")
print("=" * 60)

try:
    # 1. Search product in Tiny
    logger.info(f"Searching for SKU {SKU} in Tiny API...")
    product_data = tiny_service.search_product(SKU)
    
    if not product_data:
        logger.error(f"Product {SKU} NOT FOUND in Tiny ERP")
        print("\n✗ Product NOT FOUND in Tiny ERP API")
        print("  Possible reasons:")
        print("  - SKU doesn't exist in Tiny")
        print("  - SKU name is different in Tiny")
        print("  - Tiny API token invalid/expired")
        db.close()
        sys.exit(1)
    
    logger.info(f"Found product: {product_data.get('nome')}")
    print(f"\n✓ Found in Tiny: {product_data.get('nome')}")
    
    # 2. Get full details
    tiny_id = product_data.get('id')
    logger.info(f"Getting full details for Tiny ID {tiny_id}...")
    details = tiny_service.get_product_details(str(tiny_id))
    
    if details:
        product_data = details  # Use full details
        logger.info("Got full product details")
    
    # 3. Extract data
    cost = float(product_data.get('preco_custo', 0))
    name = product_data.get('nome', '')
    sku_from_tiny = product_data.get('codigo', SKU)
    
    print(f"   Tiny ID: {tiny_id}")
    print(f"   SKU: {sku_from_tiny}")
    print(f"   Name: {name}")
    print(f"   Cost: R$ {cost:.2f}")
    
    # 4. Save to database
    logger.info("Saving to database...")
    existing = db.query(TinyProduct).filter(TinyProduct.id == str(tiny_id)).first()
    
    if existing:
        logger.info(f"Updating existing TinyProduct {tiny_id}")
        existing.sku = sku_from_tiny
        existing.name = name
        existing.cost = cost
        print(f"\n✓ UPDATED existing TinyProduct {tiny_id}")
    else:
        logger.info(f"Creating new TinyProduct {tiny_id}")
        new_tp = TinyProduct(
            id=str(tiny_id),
            sku=sku_from_tiny,
            name=name,
            cost=cost
        )
        db.add(new_tp)
        print(f"\n✓ CREATED new TinyProduct {tiny_id}")
    
    db.commit()
    print(f"\n✓ Successfully synced SKU {SKU} with cost R$ {cost:.2f}")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. Run ML Ads sync to fetch ads with this SKU")
    print("2. System will auto-link Ad to TinyProduct")
    print("3. Cost will be updated on next sync_metrics run")
    
except Exception as e:
    logger.error(f"Error syncing SKU: {e}")
    print(f"\n✗ ERROR: {e}")
    db.rollback()
finally:
    db.close()
