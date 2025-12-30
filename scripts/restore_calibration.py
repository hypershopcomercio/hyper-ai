import sys
import os

# Add project root to path
sys.path.insert(0, r'C:\Users\Usuário\OneDrive\Documentos\01 - Projetos\projeto-hyper-ai\hyper-data')

from app.core.database import SessionLocal
from app.models.forecast_learning import MultiplierConfig, CalibrationHistory
from decimal import Decimal

def restore_calibration_data():
    db = SessionLocal()
    try:
        print("--- Restoring Calibration Data to Correct Keys ---\n")
        
        # Mapping of old (bad) keys to correct keys based on value ranges
        # 0.7 ≈ muito_baixo (0.800)
        # 0.818 ≈ baixo (0.900)  
        # 0.905 ≈ normal (1.000) or slightly below
        # 0.970 ≈ normal (1.000) or alto (1.100)
        # 1.0 ≈ normal (1.000)
        
        # Get recent calibration history for momentum
        history = db.query(CalibrationHistory).filter(
            CalibrationHistory.tipo_fator == 'momentum'
        ).order_by(CalibrationHistory.data_calibracao.desc()).limit(20).all()
        
        print(f"Found {len(history)} momentum calibration records\n")
        
        # Group by target key based on old value
        value_to_key_map = {
            # Based on the values we saw in the deleted keys
            '0.7': 'muito_baixo',    # 0.7 is closest to 0.800 (muito_baixo)
            '0.818': 'baixo',        # 0.818 is closest to 0.900 (baixo)
            '0.905': 'normal',       # 0.905 is close to 1.000 (normal)
            '0.970': 'alto',         # 0.970 is between normal and alto
            '1.0': 'normal',         # 1.0 is exactly normal
        }
        
        # Aggregate data by correct key
        key_data = {}
        
        for h in history:
            old_key = h.fator_chave
            
            # Find correct key
            correct_key = value_to_key_map.get(old_key)
            if not correct_key:
                # If not in map, try to infer from value
                try:
                    val = float(h.valor_novo)
                    if val < 0.85:
                        correct_key = 'muito_baixo'
                    elif val < 0.95:
                        correct_key = 'baixo'
                    elif val < 1.05:
                        correct_key = 'normal'
                    elif val < 1.15:
                        correct_key = 'alto'
                    else:
                        correct_key = 'muito_alto'
                except:
                    continue
            
            if correct_key not in key_data:
                key_data[correct_key] = {
                    'errors': [],
                    'samples': 0,
                    'last_value': None
                }
            
            key_data[correct_key]['errors'].append(float(h.erro_medio))
            key_data[correct_key]['samples'] += int(h.amostras)
            key_data[correct_key]['last_value'] = float(h.valor_novo)
        
        # Update MultiplierConfig with aggregated data
        updated_count = 0
        for key, data in key_data.items():
            config = db.query(MultiplierConfig).filter(
                MultiplierConfig.tipo == 'momentum',
                MultiplierConfig.chave == key
            ).first()
            
            if not config:
                print(f"⚠️  Key '{key}' not found in config, skipping...")
                continue
            
            # Calculate average error
            avg_error = sum(data['errors']) / len(data['errors']) if data['errors'] else 0
            
            # Update with real calibration data
            if data['last_value'] is not None:
                config.valor = Decimal(str(round(data['last_value'], 3)))
                config.calibrado = 'auto'
            
            # Set confidence based on samples (cap at 100)
            config.confianca = min(100, data['samples'])
            
            print(f"✓ Updated '{key}':")
            print(f"  - Value: {config.valor}")
            print(f"  - Samples: {data['samples']}")
            print(f"  - Avg Error: {avg_error:.2f}%")
            print(f"  - Confidence: {config.confianca}%")
            print()
            
            updated_count += 1
        
        db.commit()
        print(f"\n--- Complete: Updated {updated_count} momentum keys ---")
        
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    restore_calibration_data()
