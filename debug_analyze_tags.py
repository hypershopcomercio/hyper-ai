
import json
from collections import Counter
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def analyze_tags():
    db = SessionLocal()
    import datetime
    
    # Filter Current Month
    now = datetime.datetime.now()
    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    orders = db.query(MlOrder).filter(
        MlOrder.status == 'cancelled',
        MlOrder.date_created >= start_date
    ).all()
    
    print(f"--- CANCELLED ORDERS TAG ANALYSIS (Current Month: {len(orders)} orders) ---")
    
    delivered_count = 0
    not_delivered_count = 0
    
    for o in orders:
        if not o.tags: continue
        if "delivered" in o.tags:
            delivered_count += 1
        elif "not_delivered" in o.tags:
            not_delivered_count += 1
            
    print(f"Delivered: {delivered_count}")
    print(f"Not Delivered: {not_delivered_count}")

    
    tag_patterns = Counter()
    
    for o in orders:
        if not o.tags:
            tag_patterns["NO TAGS"] += 1
            continue
            
        try:
            tags = json.loads(o.tags)
            # Sort tags to create a consistent signature
            signature = "|".join(sorted(tags))
            tag_patterns[signature] += 1
            
            # Print detail for sparse inspection
            # print(f"{o.ml_order_id}: {signature}")
        except:
            tag_patterns["ERROR PARSING"] += 1
            
    print("\nTag Pattern Clusters:")
    for sig, count in tag_patterns.most_common():
        print(f"[{count}] {sig}")
        
    db.close()

if __name__ == "__main__":
    analyze_tags()
