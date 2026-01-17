from app.core.database import SessionLocal
from app.models.ml_order import MlOrder, MlOrderItem
from sqlalchemy import func
from datetime import datetime, timedelta

db = SessionLocal()
try:
    print("--- CHECKING ML ORDER ITEM DUPLICATES ---")
    
    duplicates = db.query(
        MlOrderItem.ml_item_id,
        MlOrderItem.ml_order_id,
        func.count(MlOrderItem.id)
    ).group_by(
        MlOrderItem.ml_item_id,
        MlOrderItem.ml_order_id
    ).having(
        func.count(MlOrderItem.id) > 1
    ).all()
    
    if duplicates:
        print(f"FOUND {len(duplicates)} DUPLICATE ITEM ENTRIES!")
        for d in duplicates[:10]:
            print(f"  Item {d[0]} in Order {d[1]}: {d[2]} copies")
    else:
        print("No duplicate items found.")

    print("\n--- CHECKING QUERY SUM FOR MASK ---")
    pid = 'MLB3862661909'
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    
    valid_statuses = ['paid', 'shipped', 'delivered']
    
    # 1. Raw rows
    rows = db.query(MlOrderItem, MlOrder.date_closed).join(MlOrder).filter(
        MlOrderItem.ml_item_id == pid,
        MlOrder.date_closed >= week_ago,
        MlOrder.status.in_(valid_statuses)
    ).all()
    
    print(f"Found {len(rows)} sales rows for {pid}:")
    for r, date_closed in rows:
        print(f"  Item {r.id} (Order {r.ml_order_id}) - Qty: {r.quantity}")
        
    # 2. Sum
    total = db.query(
        func.sum(MlOrderItem.quantity)
    ).join(MlOrder).filter(
        MlOrderItem.ml_item_id == pid,
        MlOrder.date_closed >= week_ago,
        MlOrder.status.in_(valid_statuses)
    ).scalar()
    
    print(f"Total Sum (7d): {total}")
    if total:
        print(f"Avg (7d): {float(total)/7}")

finally:
    db.close()
