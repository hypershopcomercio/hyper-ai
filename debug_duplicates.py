from app.core.database import SessionLocal
from app.models.product_forecast import ProductForecast
from sqlalchemy import func

db = SessionLocal()
try:
    # Count total rows
    total_count = db.query(ProductForecast).count()
    print(f"Total rows in ProductForecast: {total_count}")

    # Count distinct mlb_ids
    distinct_count = db.query(ProductForecast.mlb_id).distinct().count()
    print(f"Distinct MLB IDs: {distinct_count}")

    # Find duplicates
    duplicates = db.query(
        ProductForecast.mlb_id, 
        func.count(ProductForecast.mlb_id)
    ).group_by(
        ProductForecast.mlb_id
    ).having(
        func.count(ProductForecast.mlb_id) > 1
    ).all()

    if duplicates:
        print(f"Found {len(duplicates)} duplicated IDs.")
        for mlb_id, count in duplicates[:10]:
            print(f"  {mlb_id}: {count} copies")
            
        # Inspect one DUPLICATE to see if they are identical
        first_dup = duplicates[0][0]
        entries = db.query(ProductForecast).filter(ProductForecast.mlb_id == first_dup).all()
        print(f"\nExample duplicates for {first_dup}:")
        for e in entries:
            print(f"  ID: {e.id}, Active: {e.is_active}, Updated: {e.last_updated}")
            
    else:
        print("No duplicates found.")

finally:
    db.close()
