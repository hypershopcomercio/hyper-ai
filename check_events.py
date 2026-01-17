from app.core.database import SessionLocal
from app.models.competitor_intelligence import CompetitorImpactEvent

db = SessionLocal()
events = db.query(CompetitorImpactEvent).all()
print(f"Total eventos encontrados: {len(events)}")
for e in events:
    print(f"- {e.event_timestamp}: {e.event_type}")
    print(f"  Diagnosis: {e.diagnosis}")
db.close()
