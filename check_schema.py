from app.core.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
columns = [c['name'] for c in inspector.get_columns('system_logs')]
print(f"Columns in system_logs: {columns}")

if 'module' in columns:
    print("Column 'module' EXISTS.")
else:
    print("Column 'module' MISSING!")
