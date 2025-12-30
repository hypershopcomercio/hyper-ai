import sys
import os
from sqlalchemy import func, text

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.forecast_learning import MultiplierConfig

def cleanup_subfactors():
    db = SessionLocal()
    try:
        print("\n=== CLEANING GARBAGE KEYS ===")
        # Find entries with spaces or "Vendas" or "abaixo"
        garbage = db.query(MultiplierConfig).filter(
            text("length(chave) > 30 OR chave LIKE '%Vendas%' OR chave LIKE '% %'")
        ).all()
        
        if garbage:
            print(f"Found {len(garbage)} garbage entries. Deleting...")
            for g in garbage:
                print(f"  - Deleting [{g.id}] {g.tipo}: {g.chave}")
                db.delete(g)
            db.commit()
            print("Garbage deleted.")
        else:
            print("No garbage entries found.")
            
        print("\n=== CLEANING DUPLICATES ===")
        # Find duplicates
        duplicates = db.query(
            MultiplierConfig.tipo,
            MultiplierConfig.chave,
            func.count(MultiplierConfig.id).label('count')
        ).group_by(
            MultiplierConfig.tipo,
            MultiplierConfig.chave
        ).having(func.count(MultiplierConfig.id) > 1).all()
        
        for tipo, chave, count in duplicates:
            print(f"Resolving duplicates for [{tipo}] {chave} ({count} entries)...")
            
            # Get all entries for this dup set, order by update time desc (keep newest)
            entries = db.query(MultiplierConfig).filter_by(
                tipo=tipo, chave=chave
            ).order_by(MultiplierConfig.atualizado_em.desc()).all()
            
            # Keep first (newest), delete others
            to_keep = entries[0]
            to_delete = entries[1:]
            
            for item in to_delete:
                print(f"  - Deleting duplicate ID {item.id} (kept {to_keep.id})")
                db.delete(item)
                
        db.commit()
        print("Duplicates cleaned.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_subfactors()
