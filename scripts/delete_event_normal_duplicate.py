import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.forecast_learning import MultiplierConfig

db = SessionLocal()

normals = db.query(MultiplierConfig).filter(
    MultiplierConfig.tipo == 'event',
    MultiplierConfig.chave == 'normal'
).all()

print(f'Encontrados {len(normals)} event:normal:')
for n in normals:
    print(f'  ID {n.id}: {n.valor} ({n.calibrado}, conf={n.confianca})')

if len(normals) > 1:
    # Keep the best one (auto > default, higher confidence)
    best = max(normals, key=lambda x: (
        1 if x.calibrado == 'auto' else 0,
        x.confianca or 0
    ))
    
    print(f'\n✅ Mantendo ID {best.id}: {best.valor} ({best.calibrado})')
    
    for n in normals:
        if n.id != best.id:
            print(f'❌ Deletando ID {n.id}: {n.valor}')
            db.delete(n)
    
    db.commit()
    print('\n✅ Duplicata deletada!')
else:
    print('\n✅ Apenas 1 event:normal encontrado')

db.close()
