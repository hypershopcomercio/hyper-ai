"""
Settings API Endpoints
Unified configuration management for the entire system
"""
import json
import logging
from flask import jsonify, request
from app.api import api_bp
from app.core.database import SessionLocal
from app.models.system_config import SystemConfig
from app.models.system_log import SystemLog

logger = logging.getLogger(__name__)

# Default settings structure with default values
DEFAULT_SETTINGS = {
    "geral": {
        "empresa_nome": "HyperShop",
        "empresa_cnpj": "",
        "empresa_uf": "SP",
        "regime_tributario": "simples",
        "aliquota_simples": 12.5,
        "moeda": "BRL",
        "fuso_horario": "America/Sao_Paulo",
        "formato_data": "DD/MM/YYYY",
        "primeiro_dia_semana": "monday",
        "email_alertas": "",
        "whatsapp_alertas": "",
        "alerta_estoque_critico": True,
        "alerta_resumo_diario": True,
        "alerta_previsao_erro": False
    },
    "financeiro": {
        "margem_minima": 20,
        "meta_faturamento_mensal": 150000,
        "meta_lucro_mensal": 30000,
        "custos_fixos": [],
        "comissao_ml": 16,
        "comissao_amazon": 15,
        "comissao_shopee": 20,
        "taxa_fixa_ml": 5.0,
        "taxa_fixa_amazon": 0,
        "taxa_fixa_shopee": 3.0,
        "calcular_difal": True,
        "uf_origem": "SP",
        "aliquota_interna": 18
    },
    "estoque": {
        "nivel_critico": 3,
        "nivel_baixo": 10,
        "usar_dias_estoque": True,
        "dias_critico": 3,
        "dias_baixo": 7,
        "metodo_seguranca": "auto",
        "multiplicador_seguranca": 1.5,
        "lead_time_padrao": 15,
        "calcular_ponto_pedido": True,
        "alertar_ponto_pedido": True,
        "sugerir_qtd_compra": True,
        "multi_deposito": False
    },
    "hyper_ai": {
        # Reconciliation & Calibration
        "reconciliacao_habilitada": True,
        "reconciliacao_horario": "03:00",
        "calibracao_habilitada": True,
        "calibracao_frequencia": "weekly",
        "calibracao_dia": "sunday",
        "ajuste_maximo": 2,
        "min_amostras_calibrar": 30,
        "erro_max_toleravel": 25,
        "alertar_erro_alto": True,
        "limite_erro_alerta": 15,
        "reverter_se_piorar": True,
        "limite_reversao": 10,
        
        # Feriados personalizados
        "feriados_custom": [],
        
        # ====== MULTIPLICADORES DE PREVISÃO ======
        # Cada multiplicador tem: enabled, weight, min, max
        
        # TEMPORAIS
        "mult_day_of_week": {"enabled": True, "weight": 1.0, "min": 0.5, "max": 1.5, "desc": "Dia da semana (seg-dom)"},
        "mult_hourly_pattern": {"enabled": True, "weight": 1.0, "min": 0.2, "max": 2.0, "desc": "Padrão horário de vendas"},
        "mult_period_of_month": {"enabled": True, "weight": 1.0, "min": 0.7, "max": 1.3, "desc": "Início/meio/fim do mês"},
        "mult_payment_day": {"enabled": True, "weight": 1.0, "min": 0.8, "max": 1.4, "desc": "Dia de pagamento (5º, 20º)"},
        "mult_week_of_month": {"enabled": True, "weight": 1.0, "min": 0.7, "max": 1.3, "desc": "Semana do mês (1-4)"},
        
        # EVENTOS
        "mult_event": {"enabled": True, "weight": 1.0, "min": 0.1, "max": 3.0, "desc": "Feriados e datas especiais"},
        "mult_post_feriado": {"enabled": True, "weight": 1.0, "min": 0.5, "max": 1.0, "desc": "Ressaca pós-feriado"},
        "mult_seasonal": {"enabled": True, "weight": 1.0, "min": 0.5, "max": 2.0, "desc": "Sazonalidade por categoria"},
        
        # TENDÊNCIA/MOMENTUM
        "mult_momentum": {"enabled": True, "weight": 1.0, "min": 0.5, "max": 2.0, "desc": "Tendência 7 dias"},
        "mult_visits_trend": {"enabled": True, "weight": 0.8, "min": 0.5, "max": 2.0, "desc": "Tendência de visitas hoje"},
        "mult_velocity_score": {"enabled": True, "weight": 0.7, "min": 0.5, "max": 2.0, "desc": "Aceleração vendas (7d vs 30d)"},
        
        # CONVERSÃO/PRODUTO
        "mult_conversion_rate": {"enabled": True, "weight": 0.6, "min": 0.7, "max": 1.5, "desc": "Taxa de conversão por produto"},
        "mult_top_sellers": {"enabled": True, "weight": 0.5, "min": 1.0, "max": 1.3, "desc": "Produtos mais vendidos"},
        "mult_promo_active": {"enabled": True, "weight": 1.0, "min": 1.0, "max": 1.4, "desc": "Produto em promoção"},
        "mult_catalog_boost": {"enabled": True, "weight": 0.7, "min": 1.0, "max": 1.25, "desc": "Produtos Full/Catálogo"},
        "mult_listing_health": {"enabled": True, "weight": 0.5, "min": 0.7, "max": 1.2, "desc": "Saúde do anúncio"},
        
        # ESTOQUE/PRESSÃO
        "mult_stock_pressure": {"enabled": True, "weight": 0.6, "min": 0.8, "max": 1.3, "desc": "Pressão de estoque baixo"},
        "mult_shipping_advantage": {"enabled": True, "weight": 0.5, "min": 1.0, "max": 1.2, "desc": "Full vs envio normal"},
        
        # PREÇO/COMPETITIVIDADE
        "mult_price_competitiveness": {"enabled": False, "weight": 0.5, "min": 0.7, "max": 1.4, "desc": "Preço vs mercado"},
        
        # COMPORTAMENTO
        "mult_impulse_hours": {"enabled": True, "weight": 0.6, "min": 0.9, "max": 1.3, "desc": "Horário de impulso (22h-02h)"},
        "mult_mobile_hours": {"enabled": True, "weight": 0.5, "min": 0.9, "max": 1.2, "desc": "Horário mobile (noite)"},
        
        # POSICIONAMENTO/MARKETPLACE
        "mult_search_position": {"enabled": True, "weight": 1.0, "min": 0.3, "max": 1.5, "desc": "Posição na busca (1ª página = mais vendas)"},
        "mult_gold_medal": {"enabled": True, "weight": 0.8, "min": 1.0, "max": 1.3, "desc": "Medalha Gold (reputação)"},
        "mult_listing_type": {"enabled": True, "weight": 0.7, "min": 0.9, "max": 1.3, "desc": "Tipo de anúncio (gold_pro, gold_special)"},
        "mult_free_shipping": {"enabled": True, "weight": 0.8, "min": 1.0, "max": 1.25, "desc": "Frete grátis ativo"},
        
        # EXTERNOS (Futuros - desabilitados por padrão)
        "mult_weather": {"enabled": True, "weight": 0.6, "min": 0.5, "max": 1.5, "desc": "Clima por região dos compradores"},
        "mult_google_trends": {"enabled": False, "weight": 0.3, "min": 0.7, "max": 1.5, "desc": "Google Trends"},
        "mult_competitor_stockout": {"enabled": False, "weight": 0.5, "min": 1.0, "max": 2.0, "desc": "Concorrentes sem estoque"}
    },
    "catalogo": {
        "tipo_anuncio_padrao": "classico",
        "garantia_padrao": "30_dias",
        "condicao_padrao": "novo",
        "prazo_envio_padrao": 2,
        "titulo_max_chars": 60,
        "titulo_sem_abreviacoes": True,
        "titulo_sem_emojis": True,
        "alertar_titulo_longo": True,
        "alertar_margem_baixa": True,
        "margem_minima_alerta": 20,
        "margem_minima_bloqueio": 10,
        "arredondar_precos": False,
        "sugerir_preco": True,
        "imagem_dimensao": "1200x1200",
        "imagem_formato": "webp",
        "alertar_imagem_pequena": True,
        "comprimir_imagem": True
    },
    "integracoes": {
        "ml_sync_estoque": True,
        "ml_sync_precos": True,
        "ml_importar_pedidos": True,
        "ml_intervalo_sync": 15,
        "tiny_importar_custos": True,
        "tiny_sync_bidirecional": True,
        "tiny_criar_produtos_auto": False,
        # OpenWeather API
        "openweather_api_key": "",
        "openweather_cidade": "Votorantim,BR",
        "openweather_enabled": False,
        # Google Trends (pytrends - no API key needed)
        "google_trends_enabled": False,
        "google_trends_keywords": ["piscina", "aquecedor", "ventilador"]
    }
}


@api_bp.route('/settings', methods=['GET'])
def get_all_settings():
    """Get all settings grouped by category"""
    db = SessionLocal()
    try:
        configs = db.query(SystemConfig).all()
        
        # Start with defaults
        settings = {k: dict(v) for k, v in DEFAULT_SETTINGS.items()}
        
        # Override with database values
        for config in configs:
            group = config.group or 'geral'
            key = config.key
            
            if group in settings:
                try:
                    if key in settings[group]:
                        expected_type = type(settings[group][key])
                        if expected_type == bool:
                            settings[group][key] = config.value.lower() in ('true', '1', 'yes')
                        elif expected_type == int:
                            settings[group][key] = int(float(config.value))
                        elif expected_type == float:
                            settings[group][key] = float(config.value)
                        elif expected_type == list:
                            settings[group][key] = json.loads(config.value) if config.value else []
                        else:
                            settings[group][key] = config.value
                    else:
                        settings[group][key] = config.value
                except:
                    settings[group][key] = config.value
        
        return jsonify({"success": True, "data": settings})
        
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@api_bp.route('/settings/<group>', methods=['GET'])
def get_settings_group(group: str):
    """Get settings for a specific category"""
    db = SessionLocal()
    try:
        if group not in DEFAULT_SETTINGS:
            return jsonify({"success": False, "error": f"Unknown group: {group}"}), 400
        
        configs = db.query(SystemConfig).filter(SystemConfig.group == group).all()
        settings = dict(DEFAULT_SETTINGS[group])
        
        for config in configs:
            key = config.key
            if key in settings:
                expected_type = type(settings[key])
                try:
                    if expected_type == bool:
                        settings[key] = config.value.lower() in ('true', '1', 'yes')
                    elif expected_type == int:
                        settings[key] = int(float(config.value))
                    elif expected_type == float:
                        settings[key] = float(config.value)
                    elif expected_type == list:
                        settings[key] = json.loads(config.value) if config.value else []
                    elif expected_type == dict:
                        settings[key] = json.loads(config.value) if config.value else {}
                    else:
                        settings[key] = config.value
                except:
                    settings[key] = config.value
            else:
                # Try to parse as JSON if it looks like JSON
                if config.value and config.value.startswith('{'):
                    try:
                        settings[key] = json.loads(config.value)
                    except:
                        settings[key] = config.value
                else:
                    settings[key] = config.value
        
        return jsonify({"success": True, "data": settings})
        
    except Exception as e:
        logger.error(f"Error getting settings group: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@api_bp.route('/settings/<group>', methods=['PUT'])
def update_settings_group(group: str):
    """Update settings for a specific category"""
    db = SessionLocal()
    try:
        if group not in DEFAULT_SETTINGS:
            return jsonify({"success": False, "error": f"Unknown group: {group}"}), 400
        
        data = request.get_json()
        
        for key, value in data.items():
            if key == "tiny_api_token":
                from app.models.oauth_token import OAuthToken
                from datetime import datetime
                # Fetch or create OAuthToken for Tiny
                tiny_token = db.query(OAuthToken).filter_by(provider="tiny").first()
                if not tiny_token:
                    # Provide empty refresh_token since it's nullable=False
                    tiny_token = OAuthToken(provider="tiny", user_id="1", access_token=str(value), refresh_token="", updated_at=datetime.now())
                    db.add(tiny_token)
                else:
                    tiny_token.access_token = str(value)
                    tiny_token.updated_at = datetime.now()
                # Also save to SystemConfig for consistency with GET /settings/integracoes
                str_value = str(value)
            elif isinstance(value, bool):
                str_value = 'true' if value else 'false'
            elif isinstance(value, (list, dict)):
                str_value = json.dumps(value)
            else:
                str_value = str(value)
            
            existing = db.query(SystemConfig).filter(
                SystemConfig.key == key,
                SystemConfig.group == group
            ).first()
            
            if existing:
                existing.value = str_value
            else:
                new_config = SystemConfig(
                    key=key,
                    value=str_value,
                    group=group,
                    description=f"Setting: {group}.{key}"
                )
                db.add(new_config)
        
        db.commit()
        return jsonify({"success": True, "message": f"Settings for '{group}' updated"})
        
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        db.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@api_bp.route('/settings/defaults', methods=['GET'])
def get_default_settings():
    """Get default settings structure"""
    return jsonify({"success": True, "data": DEFAULT_SETTINGS})
@api_bp.route('/history/hyper_ai', methods=['GET'])
def get_hyper_ai_history():
    """Get history of AI activities (Reconciliations, Calibrations)"""
    print("DEBUG: Hit /settings/hyper_ai/history")
    db = SessionLocal()
    try:
        from datetime import datetime, timedelta
        
        # Parse filters
        start_param = request.args.get('start_date')
        end_param = request.args.get('end_date')
        
        query = db.query(SystemLog).filter(SystemLog.module == 'hyper_ai')
        
        if start_param and end_param:
            try:
                start_date = datetime.strptime(start_param, '%Y-%m-%d')
                end_date = datetime.strptime(end_param, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
                query = query.filter(SystemLog.timestamp >= start_date, SystemLog.timestamp <= end_date)
            except ValueError:
                # Fallback to default limit if date invalid
                query = query.limit(50)
        else:
             # Default behavior
             query = query.limit(50)

        print("DEBUG: DB Session created. Querying...")
        logs = query.order_by(SystemLog.timestamp.desc()).all()
        print(f"DEBUG: Found {len(logs)} logs.")
        
        history = []
        for log in logs:
            details = {}
            try:
                if log.details:
                    details = json.loads(log.details)
            except Exception as e:
                print(f"DEBUG: JSON error: {e}")
                pass
                
            history.append({
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "message": log.message,
                "level": log.level,
                "details": details
            })
            
        print("DEBUG: Returning JSON success")
        return jsonify({"success": True, "data": history})
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error getting AI history: {e}")
        print(f"DEBUG: CRITICAL ERROR: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()
