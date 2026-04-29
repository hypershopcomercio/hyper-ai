import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from datetime import datetime, timedelta
import urllib.parse

def test_conn(password):
    encoded_pass = urllib.parse.quote_plus(password)
    url = f"mysql+pymysql://root:{encoded_pass}@localhost:3306/hyper_sync"
    try:
        engine = sqlalchemy.create_engine(url)
        Session = sessionmaker(bind=engine)
        db = Session()
        print(f"Testing password: {password} ...")
        res = db.execute(text("SELECT COUNT(*) FROM ml_orders")).scalar()
        print(f"Success! Total orders: {res}")
        
        # Check Yesterday (April 28)
        start = datetime(2026, 4, 28, 0, 0, 0)
        end = datetime(2026, 4, 29, 0, 0, 0)
        
        created = db.execute(text("SELECT COUNT(*) FROM ml_orders WHERE date_created >= :s AND date_created < :e"), {"s": start, "e": end}).scalar()
        closed = db.execute(text("SELECT COUNT(*) FROM ml_orders WHERE date_closed >= :s AND date_closed < :e"), {"s": start, "e": end}).scalar()
        
        print(f"April 28 Created: {created}")
        print(f"April 28 Closed: {closed}")
        
        db.close()
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False

if not test_conn("gWh28@@dGcMp"):
    test_conn("gWh28@@40dGcMp")
