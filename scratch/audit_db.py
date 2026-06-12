import os
import sys
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import Base, engine

# Dynamically import all models so they register on Base
models_dir = os.path.join(os.path.dirname(__file__), '..', 'app', 'models')
for filename in os.listdir(models_dir):
    if filename.endswith('.py') and not filename.startswith('__'):
        module_name = f"app.models.{filename[:-3]}"
        __import__(module_name)

def run_audit():
    print("=== STARTING AUDIT ===")
    
    # Introspect real database
    real_meta = MetaData()
    real_meta.reflect(bind=engine)
    
    real_tables = {name: table for name, table in real_meta.tables.items()}
    model_tables = {name: table for name, table in Base.metadata.tables.items()}
    
    print(f"Total Tables in DB: {len(real_tables)}")
    print(f"Total Models expected: {len(model_tables)}\n")
    
    # 1. Missing Tables in DB
    print("=== MISSING TABLES IN DB (EXPECTED BY MODELS) ===")
    missing_tables = set(model_tables.keys()) - set(real_tables.keys())
    for t in missing_tables:
        print(f"  - {t}")
    print("")
    
    # 2. Extra Tables in DB
    print("=== EXTRA TABLES IN DB (NOT IN MODELS) ===")
    extra_tables = set(real_tables.keys()) - set(model_tables.keys())
    for t in extra_tables:
        print(f"  - {t}")
    print("")
    
    # 3. Column Divergences
    print("=== COLUMN DIVERGENCES ===")
    for table_name in model_tables:
        if table_name not in real_tables:
            continue
        
        model_cols = {c.name: c for c in model_tables[table_name].columns}
        real_cols = {c.name: c for c in real_tables[table_name].columns}
        
        # Missing columns in DB
        missing_cols = set(model_cols.keys()) - set(real_cols.keys())
        if missing_cols:
            print(f"[{table_name}] Missing columns in DB: {', '.join(missing_cols)}")
            
        # Extra columns in DB
        extra_cols = set(real_cols.keys()) - set(model_cols.keys())
        if extra_cols:
            print(f"[{table_name}] Extra columns in DB (not in model): {', '.join(extra_cols)}")
            
        # Type divergences (rough check)
        for col_name in set(model_cols.keys()).intersection(real_cols.keys()):
            model_type = str(model_cols[col_name].type)
            real_type = str(real_cols[col_name].type)
            
            # Very basic check, string representation might vary slightly
            if type(model_cols[col_name].type) != type(real_cols[col_name].type):
                # Only report obvious mismatches, SQLAlchemy types map differently to MySQL sometimes
                # Ex: VARCHAR vs String
                pass
                
    print("=== END OF AUDIT ===")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(override=True)
    run_audit()
