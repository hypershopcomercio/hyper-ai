import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.models.forecast_learning import ForecastLog
from datetime import datetime, date

# Database setup
DATABASE_URL = "postgresql://postgres:gWh28%40dGcMp@localhost:5432/hypershop"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

today = date(2025, 12, 28)

print(f"Checking for duplicates on {today}...")

# Query logs for today
logs = session.query(ForecastLog).filter(
    func.date(ForecastLog.hora_alvo) == today
).all()

hour_counts = {}
for log in logs:
    h = log.hora_alvo.strftime("%H:%M")
    if h not in hour_counts:
        hour_counts[h] = []
    hour_counts[h].append(log)

deleted_count = 0

for h, entries in hour_counts.items():
    if len(entries) > 1:
        # Sort by ID descending (keep the highest ID)
        entries.sort(key=lambda x: x.id, reverse=True)
        to_keep = entries[0]
        to_delete = entries[1:]
        
        print(f"Hour {h}: Keeping ID {to_keep.id}, Deleting {len(to_delete)} duplicates: {[e.id for e in to_delete]}")
        
        for entry in to_delete:
            session.delete(entry)
            deleted_count += 1

if deleted_count > 0:
    session.commit()
    print(f"Successfully deleted {deleted_count} duplicate logs.")
else:
    print("No duplicates found or deleted.")
