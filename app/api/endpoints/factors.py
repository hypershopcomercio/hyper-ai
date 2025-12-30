"""
Factors API - Simple endpoints for forecast factor management
"""
import json
import logging
from flask import jsonify, request
from app.api import api_bp
from app.core.database import SessionLocal
from app.models.system_config import SystemConfig

logger = logging.getLogger(__name__)

# Default factors with descriptions
DEFAULT_FACTORS = {
    "mult_day_of_week": {"enabled": True, "weight": 1.0, "min": 0.1, "max": 3.0, "desc": "Dia da semana"},
    "mult_hourly_pattern": {"enabled": True, "weight": 1.0, "min": 0.5, "max": 2.0, "desc": "Padrão horário"},
    "mult_period_of_month": {"enabled": True, "weight": 1.0, "min": 0.5, "max": 1.0, "desc": "Período do mês"},
    "mult_payment_day": {"enabled": True, "weight": 1.0, "min": 0.5, "max": 1.0, "desc": "Dia de pagamento"},
    "mult_week_of_month": {"enabled": True, "weight": 1.0, "min": 0.5, "max": 1.0, "desc": "Semana do mês"},
    "mult_event": {"enabled": True, "weight": 1.0, "min": 0.1, "max": 3.0, "desc": "Feriados e datas especiais"},
    "mult_post_feriado": {"enabled": True, "weight": 1.0, "min": 0.5, "max": 1.0, "desc": "Ressaca pós-feriado"},
    "mult_seasonal": {"enabled": True, "weight": 1.0, "min": 0.5, "max": 2.0, "desc": "Sazonalidade por categoria"},
    "mult_momentum": {"enabled": True, "weight": 1.0, "min": 0.5, "max": 2.0, "desc": "Tendência 7 dias"},
    "mult_visits_trend": {"enabled": True, "weight": 0.8, "min": 0.5, "max": 2.0, "desc": "Tendência de visitas hoje"},
    "mult_velocity_score": {"enabled": True, "weight": 0.7, "min": 0.5, "max": 2.0, "desc": "Aceleração vendas (7d vs 30d)"},
    "mult_conversion_rate": {"enabled": True, "weight": 0.6, "min": 0.7, "max": 1.5, "desc": "Taxa de conversão por produto"},
    "mult_top_sellers": {"enabled": True, "weight": 0.5, "min": 1.0, "max": 1.3, "desc": "Produtos mais vendidos"},
    "mult_promo_active": {"enabled": True, "weight": 1.0, "min": 1.0, "max": 1.4, "desc": "Produto em promoção"},
    "mult_catalog_boost": {"enabled": True, "weight": 0.7, "min": 1.0, "max": 1.25, "desc": "Produtos Full/Catálogo"},
    "mult_listing_health": {"enabled": True, "weight": 0.5, "min": 0.7, "max": 1.2, "desc": "Saúde do anúncio"},
    "mult_stock_pressure": {"enabled": True, "weight": 0.6, "min": 0.8, "max": 1.3, "desc": "Pressão de estoque baixo"},
    "mult_shipping_advantage": {"enabled": True, "weight": 0.5, "min": 1.0, "max": 1.2, "desc": "Full vs envio normal"},
    "mult_price_competitiveness": {"enabled": False, "weight": 0.5, "min": 0.7, "max": 1.4, "desc": "Preço vs mercado"},
    "mult_impulse_hours": {"enabled": True, "weight": 0.6, "min": 0.9, "max": 1.3, "desc": "Horário de impulso (22h-02h)"},
    "mult_mobile_hours": {"enabled": True, "weight": 0.5, "min": 0.9, "max": 1.2, "desc": "Horário mobile (noite)"},
    "mult_search_position": {"enabled": True, "weight": 1.0, "min": 0.3, "max": 1.5, "desc": "Posição na busca (1ª página = mais vendas)"},
    "mult_gold_medal": {"enabled": True, "weight": 0.8, "min": 1.0, "max": 1.3, "desc": "Medalha Gold (reputação)"},
    "mult_listing_type": {"enabled": True, "weight": 0.7, "min": 0.9, "max": 1.3, "desc": "Tipo de anúncio (gold_pro, gold_special)"},
    "mult_free_shipping": {"enabled": True, "weight": 0.8, "min": 1.0, "max": 1.25, "desc": "Frete grátis ativo"},
    "mult_weather": {"enabled": True, "weight": 0.6, "min": 0.5, "max": 1.5, "desc": "Clima por região dos compradores"},
    "mult_google_trends": {"enabled": False, "weight": 0.3, "min": 0.7, "max": 1.5, "desc": "Google Trends"},
    "mult_competitor_stockout": {"enabled": False, "weight": 0.5, "min": 1.0, "max": 2.0, "desc": "Concorrentes sem estoque"}
}


@api_bp.route('/factors', methods=['GET'])
def get_factors():
    """Get all factors with their enabled status"""
    db = SessionLocal()
    try:
        # Start with defaults
        factors = {k: dict(v) for k, v in DEFAULT_FACTORS.items()}
        
        # Override with saved values
        # Override with saved values - Fetch all mult factors regardless of group
        configs = db.query(SystemConfig).filter(
            SystemConfig.key.in_(DEFAULT_FACTORS.keys())
        ).all()
        
        for config in configs:
            if config.key in factors:
                try:
                    saved = json.loads(config.value)
                    factors[config.key]['enabled'] = saved.get('enabled', factors[config.key]['enabled'])
                    factors[config.key]['weight'] = saved.get('weight', factors[config.key]['weight'])
                except:
                    pass
        
        return jsonify({'success': True, 'data': factors})
        
    except Exception as e:
        logger.error(f"Error getting factors: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        db.close()


@api_bp.route('/factors/<key>/toggle', methods=['POST'])
def toggle_factor(key: str):
    """Toggle a specific factor on/off"""
    db = SessionLocal()
    try:
        if key not in DEFAULT_FACTORS:
            return jsonify({'success': False, 'error': f'Unknown factor: {key}'}), 400
        
        # Get current value - Key is PK, so unique across all groups
        existing = db.query(SystemConfig).filter(
            SystemConfig.key == key
        ).first()
        
        if existing:
            try:
                current = json.loads(existing.value)
            except:
                current = dict(DEFAULT_FACTORS[key])
            
            # Toggle enabled status
            current['enabled'] = not current.get('enabled', True)
            
            existing.value = json.dumps(current)
            # Optionally migrate group to 'factors' if needed, but not strictly required
            if existing.group != 'factors':
                existing.group = 'factors'
                
        else:
            new_value = dict(DEFAULT_FACTORS[key])
            new_value['enabled'] = not new_value['enabled']
            new_config = SystemConfig(
                key=key,
                value=json.dumps(new_value),
                group='factors',
                description=DEFAULT_FACTORS[key]['desc']
            )
            db.add(new_config)
        
        db.commit()
        
        # Return new state
        final_enabled = current['enabled'] if existing else new_value['enabled']
        return jsonify({'success': True, 'enabled': final_enabled})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"ERROR TOGGLING {key}: {e}")
        logger.error(f"Error toggling factor {key}: {e}")
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        db.close()


@api_bp.route('/factors/<key>/weight', methods=['PUT'])
def update_factor_weight(key: str):
    """Update factor weight"""
    db = SessionLocal()
    try:
        if key not in DEFAULT_FACTORS:
            return jsonify({'success': False, 'error': f'Unknown factor: {key}'}), 400
        
        data = request.get_json()
        weight = float(data.get('weight', 1.0))
        
        existing = db.query(SystemConfig).filter(
            SystemConfig.key == key
        ).first()
        
        if existing:
            try:
                current = json.loads(existing.value)
            except:
                current = dict(DEFAULT_FACTORS[key])
            current['weight'] = weight
            existing.value = json.dumps(current)
        else:
            new_value = dict(DEFAULT_FACTORS[key])
            new_value['weight'] = weight
            new_config = SystemConfig(
                key=key,
                value=json.dumps(new_value),
                group='factors',
                description=DEFAULT_FACTORS[key]['desc']
            )
            db.add(new_config)
        
        db.commit()
        return jsonify({'success': True, 'weight': weight})
        
    except Exception as e:
        logger.error(f"Error updating weight for {key}: {e}")
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        db.close()
