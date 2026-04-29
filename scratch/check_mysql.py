import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Password from screenshot: gWh28@@40dGcMp
# URL encoded @ is %40
url = "mysql+pymysql://root:gWh28%40%4040dGcMp@localhost:3306/hyper_sync"
engine = sqlalchemy.create_all_engine(url) if hasattr(sqlalchemy, 'create_all_engine') else sqlalchemy.create_engine(url)
Session = sessionmaker(bind=engine)
db = Session()

try:
    print("Testing connection...")
    res = db.execute(text("SELECT COUNT(*) FROM ml_orders")).scalar()
    print(f"Total orders: {res}")
    
    # Check for today's orders
    from datetime import datetime, timedelta
    now_utc = datetime.utcnow()
    start_of_today = now_utc - timedelta(hours=24) # rough today
    
    res_today = db.execute(text("SELECT COUNT(*) FROM ml_orders WHERE date_created >= :d"), {"d": start_of_today}).scalar()
    print(f"Orders last 24h: {res_today}")
    
    # Check ML Sync status
    res_sync = db.execute(text("SELECT * FROM sync_control WHERE entity = 'orders'")).first()
    print(f"Sync Control: {res_sync}")

except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
