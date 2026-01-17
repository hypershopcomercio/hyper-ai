from app.core.database import SessionLocal
from app.models.forecast_learning import MultiplierConfig
from sqlalchemy import func

db = SessionLocal()
try:
    print("--- INSPECTING MULTIPLIER CONFIG ---")
    multipliers = db.query(MultiplierConfig).order_by(MultiplierConfig.tipo, MultiplierConfig.chave).all()
    
    for m in multipliers:
        print(f"ID: {m.id} | Type: {m.tipo} | Key: {m.chave} | Val: {m.valor} | Updated: {m.atualizado_em}")
        
    print("\n--- CHECKING FOR DUPLICATES ---")
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
    
    if duplicates:
        print("FOUND DUPLICATES:")
        for d in duplicates:
            print(f"  {d[0]} - {d[1]}: {d[2]} copies")
    else:
        print("No duplicate multipliers found.")

finally:
    db.close()
