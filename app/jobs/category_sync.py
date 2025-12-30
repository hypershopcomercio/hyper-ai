"""
Category Mapping Sync Job
Populates category_mapping table from existing products
"""
import logging
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.product_forecast import CategoryMapping

logger = logging.getLogger(__name__)


def sync_category_mapping():
    """
    Sync category mappings from existing products.
    Creates entries for all unique ML categories found in products.
    User can then set normalized names and seasonal factors.
    """
    db = SessionLocal()
    try:
        # Get all unique categories from Ads
        categories = db.query(Ad.category_name).distinct().all()
        
        created = 0
        updated = 0
        
        for (cat_ml,) in categories:
            if not cat_ml:
                continue
            
            # Check if mapping exists
            existing = db.query(CategoryMapping).filter(
                CategoryMapping.category_ml == cat_ml
            ).first()
            
            if existing:
                updated += 1
                continue
            
            # Create new mapping
            mapping = CategoryMapping(
                category_ml=cat_ml,
                category_ml_name=None,  # To be filled via ML API or manually
                category_normalized=None,  # To be set by user
                multiplier_summer=1.0,
                multiplier_winter=1.0,
                multiplier_fall=1.0,
                multiplier_spring=1.0
            )
            db.add(mapping)
            created += 1
        
        db.commit()
        
        logger.info(f"[CATEGORY SYNC] Synced categories: {created} created, {updated} existing")
        
        return {
            "success": True,
            "created": created,
            "existing": updated,
            "total": len(categories)
        }
        
    except Exception as e:
        logger.error(f"[CATEGORY SYNC] Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def get_category_multiplier(db, category_ml: str) -> float:
    """
    Get seasonal multiplier for a category based on current season.
    Returns 1.0 if no mapping found.
    """
    from datetime import datetime
    
    if not category_ml:
        return 1.0
    
    mapping = db.query(CategoryMapping).filter(
        CategoryMapping.category_ml == category_ml,
        CategoryMapping.is_active == True
    ).first()
    
    if not mapping:
        return 1.0
    
    # Determine current season (Brazil southern hemisphere)
    month = datetime.now().month
    
    if month in [12, 1, 2]:
        # Summer (Dec-Feb)
        return float(mapping.multiplier_summer or 1.0)
    elif month in [3, 4, 5]:
        # Fall (Mar-May)
        return float(mapping.multiplier_fall or 1.0)
    elif month in [6, 7, 8]:
        # Winter (Jun-Aug)
        return float(mapping.multiplier_winter or 1.0)
    else:
        # Spring (Sep-Nov)
        return float(mapping.multiplier_spring or 1.0)


if __name__ == "__main__":
    result = sync_category_mapping()
    print(f"Result: {result}")
