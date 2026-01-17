from app.core.database import SessionLocal
from app.models.forecast_learning import MultiplierConfig
from sqlalchemy import func

db = SessionLocal()
try:
    print("--- FIXING DUPLICATE MULTIPLIERS ---")
    
    # Identify duplicates
    duplicates = db.query(
        MultiplierConfig.tipo,
        MultiplierConfig.chave,
        func.count(MultiplierConfig.id)
    ).group_by(
        MultiplierConfig.tipo,
        MultiplierConfig.chave
    ).having(
        func.count(MultiplierConfig.id) > 1
    ).all()
    
    deleted_count = 0
    
    for tipo, chave, count in duplicates:
        print(f"Fixing {tipo} - {chave} ({count} copies)...")
        
        # Get all copies ordered by updated_at desc (keep newest)
        copies = db.query(MultiplierConfig).filter(
            MultiplierConfig.tipo == tipo,
            MultiplierConfig.chave == chave
        ).order_by(
            MultiplierConfig.atualizado_em.desc()
        ).all()
        
        # Keep copies[0], delete rest
        to_delete = copies[1:]
        for item in to_delete:
            db.delete(item)
            deleted_count += 1
            
    db.commit()
    print(f"Successfully deleted {deleted_count} duplicate rows.")

except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
