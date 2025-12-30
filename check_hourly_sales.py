
import sys
sys.path.append('.')

from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

db = SessionLocal()
target_date = datetime(2025, 12, 26)

print('Vendas reais por hora em 26/12 (usando date_closed):')
total = 0
for h in range(24):
    hour_start = target_date.replace(hour=h, minute=0, second=0)
    hour_end = hour_start + timedelta(hours=1)
    
    revenue = db.query(func.sum(MlOrder.total_amount)).filter(
        and_(
            MlOrder.date_closed >= hour_start,
            MlOrder.date_closed < hour_end,
            MlOrder.status.in_(['paid', 'shipped', 'delivered'])
        )
    ).scalar()
    
    revenue = float(revenue or 0)
    total += revenue
    print(f'{h:02d}:00 -> R$ {revenue:,.2f}')

print(f'\nTOTAL: R$ {total:,.2f}')
db.close()
