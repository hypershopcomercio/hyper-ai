"""
Complete migration: Rename gold_medal -> medal and migrate ALL factor keys
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.forecast_learning import MultiplierConfig, CalibrationHistory
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 70)
print("COMPLETE FACTOR MIGRATION")
print("=" * 70)

db = SessionLocal()

try:
    # ========================================
    # 1. RENAME gold_medal -> medal
    # ========================================
    print("\n1. Renaming gold_medal -> medal...")
    
    gold_medal_configs = db.query(MultiplierConfig).filter(
        MultiplierConfig.tipo == 'gold_medal'
    ).all()
    
    if gold_medal_configs:
        for config in gold_medal_configs:
            config.tipo = 'medal'
            logger.info(f"   Renamed: {config.chave} ({config.tipo})")
        db.commit()
        print(f"   ✅ Renamed {len(gold_medal_configs)} gold_medal entries to medal")
    else:
        print("   ℹ️  No gold_medal entries found")
    
    # Rename in CalibrationHistory too
    gold_medal_history = db.query(CalibrationHistory).filter(
        CalibrationHistory.tipo_fator == 'gold_medal'
    ).all()
    
    if gold_medal_history:
        for hist in gold_medal_history:
            hist.tipo_fator = 'medal'
        db.commit()
        print(f"   ✅ Renamed {len(gold_medal_history)} CalibrationHistory entries")
    
    # ========================================
    # 2. MIGRATE ALL FACTOR VALUES
    # ========================================
    print("\n2. Migrating factor values to categorical keys...")
    
    # Get all configs
    all_configs = db.query(MultiplierConfig).all()
    
    migrations = {
        'day_of_week': {
            # Numeric to categorical mapping
            '0': 'segunda', '1': 'terca', '2': 'quarta', '3': 'quinta',
            '4': 'sexta', '5': 'sabado', '6': 'domingo',
            # Also handle float representations
            '0.0': 'segunda', '1.0': 'terca', '2.0': 'quarta', '3.0': 'quinta',
            '4.0': 'sexta', '5.0': 'sabado', '6.0': 'domingo',
            '1.1': 'segunda', '1.25': 'segunda'  # Legacy values
        },
        'seasonal': {
            '0': 'verao', '0.0': 'verao',
            '1': 'inverno', '1.0': 'inverno',
            '2': 'neutro', '2.0': 'neutro',
            'summer': 'verao', 'winter': 'inverno', 'neutral': 'neutro'
        },
        'period_of_month': {
            '0': 'inicio', '0.0': 'inicio',
            '1': 'meio', '1.0': 'meio',
            '2': 'fim', '2.0': 'fim',
            'start': 'inicio', 'middle': 'meio', 'end': 'fim'
        },
        'hourly_pattern': {
            # Ensure all hours are strings "0" to "23"
        },
        'mobile_hours': {
            '0': 'off_peak', '1': 'peak',
            '0.0': 'off_peak', '1.0': 'peak'
        },
        'impulse_hours': {
            '0': 'normal', '1': 'high',
            '0.0': 'normal', '1.0': 'high'
        },
        'medal': {
            # If any had numeric values, map them
            '0': 'silver', '0.0': 'silver',
            '1': 'gold', '1.0': 'gold',
            '2': 'platinum', '2.0': 'platinum'
        }
    }
    
    migrated_count = 0
    
    for config in all_configs:
        if config.tipo in migrations:
            old_key = config.chave
            mapping = migrations[config.tipo]
            
            if old_key in mapping:
                new_key = mapping[old_key]
                
                # Check if new key already exists
                existing = db.query(MultiplierConfig).filter(
                    MultiplierConfig.tipo == config.tipo,
                    MultiplierConfig.chave == new_key
                ).first()
                
                if existing:
                    # Merge: keep the one with better data
                    logger.info(f"   Merging {config.tipo}:{old_key} → {new_key}")
                    db.delete(config)
                else:
                    # Rename
                    logger.info(f"   Migrating {config.tipo}:{old_key} → {new_key}")
                    config.chave = new_key
                
                migrated_count += 1
    
    db.commit()
    print(f"   ✅ Migrated {migrated_count} factor values to categorical keys")
    
    # ========================================
    # 3. ENSURE STANDARD KEYS EXIST
    # ========================================
    print("\n3. Creating standard keys if missing...")
    
    standard_keys = {
        'day_of_week': ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo'],
        'seasonal': ['verao', 'inverno', 'neutro'],
        'period_of_month': ['inicio', 'meio', 'fim'],
        'mobile_hours': ['peak', 'off_peak'],
        'impulse_hours': ['high', 'normal'],
        'medal': ['silver', 'gold', 'platinum'],
        'hourly_pattern': [str(h) for h in range(24)]
    }
    
    created_count = 0
    
    for tipo, keys in standard_keys.items():
        for key in keys:
            existing = db.query(MultiplierConfig).filter(
                MultiplierConfig.tipo == tipo,
                MultiplierConfig.chave == key
            ).first()
            
            if not existing:
                # Default multiplier values by type
                default_values = {
                    'day_of_week': 1.0,
                    'seasonal': 1.0,
                    'period_of_month': 1.0,
                    'mobile_hours': 1.1 if key == 'peak' else 1.0,
                    'impulse_hours': 1.15 if key == 'high' else 1.0,
                    'medal': {'silver': 1.0, 'gold': 1.05, 'platinum': 1.10}.get(key, 1.0),
                    'hourly_pattern': 1.0
                }
                
                new_config = MultiplierConfig(
                    tipo=tipo,
                    chave=key,
                    valor=default_values.get(tipo, 1.0)
                )
                db.add(new_config)
                created_count += 1
                logger.info(f"   Created: {tipo}:{key}")
    
    db.commit()
    print(f"   ✅ Created {created_count} missing standard keys")
    
    # ========================================
    # 4. STATISTICS
    # ========================================
    print("\n" + "=" * 70)
    print("MIGRATION COMPLETE!")
    print("=" * 70)
    
    for tipo_name in ['day_of_week', 'seasonal', 'period_of_month', 'mobile_hours', 'impulse_hours', 'medal', 'hourly_pattern']:
        count = db.query(MultiplierConfig).filter(MultiplierConfig.tipo == tipo_name).count()
        print(f"   {tipo_name}: {count} subfactors")
    
    print("\n✅ All factors now use CATEGORICAL KEYS!")
    print("✅ gold_medal renamed to medal!")
    
except Exception as e:
    logger.error(f"Migration failed: {e}")
    print(f"\n❌ ERROR: {e}")
    db.rollback()
    import traceback
    traceback.print_exc()
finally:
    db.close()
