"""
Hyper Forecast API Endpoints
Provides sales forecast data for the dashboard
"""
import logging
from flask import jsonify, request
from datetime import datetime
from app.api import api_bp
from app.core.database import SessionLocal
from app.services.forecast import HyperForecast

logger = logging.getLogger(__name__)


@api_bp.route('/forecast/today', methods=['GET'])
def get_today_forecast():
    """
    Get today's forecast with actuals and projections
    Perfect for the dashboard cash flow chart
    """
    db = SessionLocal()
    try:
        forecast = HyperForecast(db)
        result = forecast.get_today_with_actuals()
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"Error generating forecast: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        db.close()


@api_bp.route('/forecast/day/<target_date>', methods=['GET'])
def get_day_forecast(target_date: str):
    """
    Get forecast for a specific date
    Date format: YYYY-MM-DD
    """
    db = SessionLocal()
    try:
        parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        category = request.args.get('category', None)
        
        forecast = HyperForecast(db)
        result = forecast.predict_day(parsed_date, category)
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": f"Invalid date format. Use YYYY-MM-DD. {e}"
        }), 400
    except Exception as e:
        logger.error(f"Error generating forecast: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        db.close()


@api_bp.route('/forecast/hour/<int:target_hour>', methods=['GET'])
def get_hour_forecast(target_hour: int):
    """
    Get forecast for a specific hour today
    """
    db = SessionLocal()
    try:
        if not 0 <= target_hour <= 23:
            return jsonify({
                "success": False,
                "error": "Hour must be between 0 and 23"
            }), 400
        
        category = request.args.get('category', None)
        
        forecast = HyperForecast(db)
        result = forecast.predict_hour(target_hour, category=category)
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"Error generating forecast: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        db.close()


@api_bp.route('/forecast/chart-data', methods=['GET'])
def get_forecast_chart_data():
    """
    Get formatted data for the CashFlowChart component
    Returns actuals, predictions, and previous period in chart-ready format
    """
    db = SessionLocal()
    try:
        forecast = HyperForecast(db)
        data = forecast.get_today_with_actuals()
        
        # Format for chart
        labels = [f"{h:02d}h" for h in range(24)]
        current_hour = data["current_hour"]
        
        # Previous period line (dashed)
        previous_data = [h["revenue"] for h in data["hourly"]["previous"]]
        
        # Actual sales (solid, up to current hour)
        actual_data = [None] * 24
        for h in data["hourly"]["actuals"]:
            actual_data[h["hour"]] = h["revenue"]
        
        # Forecast line (dashed, for future hours)
        forecast_data = [None] * 24
        for p in data["hourly"]["predictions"]:
            if p["hour"] > current_hour:
                forecast_data[p["hour"]] = p["prediction"]
        
        # Confidence band (for future hours)
        confidence_min = [None] * 24
        confidence_max = [None] * 24
        for p in data["hourly"]["predictions"]:
            if p["hour"] > current_hour:
                confidence_min[p["hour"]] = p["min"]
                confidence_max[p["hour"]] = p["max"]
        
        return jsonify({
            "success": True,
            "data": {
                "labels": labels,
                "datasets": {
                    "previous": previous_data,
                    "actual": actual_data,
                    "forecast": forecast_data,
                    "confidence_min": confidence_min,
                    "confidence_max": confidence_max,
                },
                "summary": {
                    "current_hour": current_hour,
                    "actual_total": data["actual_total"],
                    "projected_total": data["projected_total"],
                    "projected_min": data["projected_min"],
                    "projected_max": data["projected_max"],
                    "vs_previous_percent": data["vs_previous_percent"],
                    "avg_confidence": data["avg_confidence"],
                    "peak_hour": data["peak_hour"],
                    "valley_hour": data["valley_hour"]
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating chart data: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        db.close()


@api_bp.route('/forecast/learning/status', methods=['GET'])
def get_learning_status():
    """
    Get the current status of the learning system
    - Total predictions logged
    - Reconciliation status
    - Average error
    - Recent calibrations
    - Current multiplier values
    """
    try:
        from app.jobs.forecast_jobs import get_calibration_status
        
        status = get_calibration_status()
        
        return jsonify({
            "success": True,
            "data": status
        })
        
    except Exception as e:
        logger.error(f"Error getting learning status: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route('/forecast/learning/reconcile', methods=['POST'])
def trigger_reconciliation():
    """
    Manually trigger the daily reconciliation job
    """
    try:
        from app.jobs.forecast_jobs import run_daily_reconciliation
        
        result = run_daily_reconciliation()
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"Error running reconciliation: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route('/forecast/learning/calibrate', methods=['POST'])
def trigger_calibration():
    """
    Manually trigger the weekly calibration job
    """
    try:
        from app.jobs.forecast_jobs import run_weekly_calibration
        
        result = run_weekly_calibration()
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"Error running calibration: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route('/forecast/learning/test-log', methods=['POST'])
def test_prediction_logging():
    """
    Test endpoint to create a sample prediction log
    Useful for verifying the learning system is working
    """
    db = SessionLocal()
    try:
        from datetime import datetime
        
        forecast = HyperForecast(db)
        current_hour = datetime.now().hour
        
        # Generate and log predictions for the next 3 hours
        logged = []
        for h in range(current_hour + 1, min(current_hour + 4, 24)):
            result = forecast.predict_hour_with_logging(h)
            logged.append({
                "hour": h,
                "prediction": result["prediction"],
                "log_id": result.get("log_id", -1)
            })
        
        return jsonify({
            "success": True,
            "message": f"Logged {len(logged)} predictions",
            "data": logged
        })
        
    except Exception as e:
        logger.error(f"Error testing prediction log: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        db.close()


@api_bp.route('/forecast/projection/today', methods=['GET'])
def get_today_projection():
    """
    Get real data + projections for remaining hours
    Perfect for the CashFlowChart integration
    
    Returns:
    - hora_atual: current hour
    - dados_reais: sales data up to current hour
    - projecao: predictions for remaining hours
    - totais: summary totals
    """
    from datetime import datetime, timedelta
    from sqlalchemy import func, and_
    from app.models.ml_order import MlOrder
    from app.models.forecast_learning import ForecastLog
    from decimal import Decimal
    
    db = SessionLocal()
    try:
        now = datetime.now()
        today = now.date()
        current_hour = now.hour
        
        # Get real sales data for each hour up to current
        dados_reais = []
        receita_total_real = 0
        
        for h in range(current_hour + 1):
            hour_start = datetime.combine(today, datetime.min.time()).replace(hour=h)
            hour_end = hour_start + timedelta(hours=1)
            
            receita = db.query(func.sum(MlOrder.total_amount)).filter(
                and_(
                    MlOrder.date_closed >= hour_start,
                    MlOrder.date_closed < hour_end,
                    MlOrder.status.in_(['paid', 'shipped', 'delivered'])
                )
            ).scalar()
            
            receita = float(receita or 0)
            receita_total_real += receita
            
            dados_reais.append({
                "hora": h,
                "hora_label": f"{h:02d}h",
                "receita": round(receita, 2),
                "tipo": "real"
            })
        
        # Get projections for remaining hours and LOG them
        projecao = []
        receita_projetada = 0
        forecast = HyperForecast(db)
        
        for h in range(current_hour + 1, 24):
            # Use predict_hour_with_logging to track predictions
            pred = forecast.predict_hour_with_logging(h, today)
            
            projecao.append({
                "hora": h,
                "hora_label": f"{h:02d}h",
                "receita_prevista": pred["prediction"],
                "confianca": pred["confidence"],
                "tipo": "projecao"
            })
            receita_projetada += pred["prediction"]
        
        # Calculate totals
        receita_fim_dia = receita_total_real + receita_projetada
        
        # Get yesterday for comparison
        yesterday = today - timedelta(days=1)
        yesterday_start = datetime.combine(yesterday, datetime.min.time())
        yesterday_end = datetime.combine(yesterday, datetime.max.time())
        
        receita_ontem = db.query(func.sum(MlOrder.total_amount)).filter(
            and_(
                MlOrder.date_closed >= yesterday_start,
                MlOrder.date_closed <= yesterday_end,
                MlOrder.status.in_(['paid', 'shipped', 'delivered'])
            )
        ).scalar()
        receita_ontem = float(receita_ontem or 0)
        
        variacao_ontem = ((receita_fim_dia - receita_ontem) / receita_ontem * 100) if receita_ontem > 0 else 0
        
        return jsonify({
            "success": True,
            "data": {
                "hora_atual": current_hour,
                "dados_reais": dados_reais,
                "projecao": projecao,
                "totais": {
                    "receita_realizada": round(receita_total_real, 2),
                    "receita_projetada_restante": round(receita_projetada, 2),
                    "receita_projetada_fim_dia": round(receita_fim_dia, 2),
                    "receita_ontem": round(receita_ontem, 2),
                    "variacao_vs_ontem": round(variacao_ontem, 1)
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting projection: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        db.close()


@api_bp.route('/forecast/learning/multipliers', methods=['GET'])
def get_multipliers():
    """
    Get all active multipliers with their current values
    For the Hyper AI admin panel
    """
    from app.models.forecast_learning import MultiplierConfig
    
    db = SessionLocal()
    try:
        configs = db.query(MultiplierConfig).order_by(
            MultiplierConfig.tipo,
            MultiplierConfig.chave
        ).all()
        
        return jsonify({
            "success": True,
            "data": {
                "multipliers": [
                    {
                        "tipo": c.tipo,
                        "chave": c.chave,
                        "valor": float(c.valor),
                        "fonte": c.calibrado,
                        "confianca": c.confianca,
                        "atualizado_em": c.atualizado_em.isoformat() if c.atualizado_em else None
                    } for c in configs
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting multipliers: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        db.close()


@api_bp.route('/forecast/learning/calibration-history', methods=['GET'])
def get_calibration_history():
    """
    Get calibration history (last 50 entries)
    For the Hyper AI admin panel
    """
    from app.models.forecast_learning import CalibrationHistory
    
    db = SessionLocal()
    try:
        history = db.query(CalibrationHistory).order_by(
            CalibrationHistory.data_calibracao.desc()
        ).limit(50).all()
        
        return jsonify({
            "success": True,
            "data": {
                "historico": [
                    {
                        "id": h.id,
                        "data": h.data_calibracao.isoformat() if h.data_calibracao else None,
                        "tipo_fator": h.tipo_fator,
                        "fator_chave": h.fator_chave,
                        "valor_anterior": float(h.valor_anterior) if h.valor_anterior else None,
                        "valor_novo": float(h.valor_novo) if h.valor_novo else None,
                        "erro_medio": float(h.erro_medio) if h.erro_medio else None,
                        "amostras": h.amostras,
                        "notas": h.notas
                    } for h in history
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting calibration history: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        db.close()


@api_bp.route('/forecast/learning/logs', methods=['GET'])
def get_forecast_logs():
    """
    Get paginated list of forecast logs with filters
    Perfect for the detailed logs table in Hyper AI panel
    """
    from datetime import datetime, timedelta
    from sqlalchemy import and_, desc
    from app.models.forecast_learning import ForecastLog
    
    db = SessionLocal()
    try:
        # Parse query params
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        status_filter = request.args.get('status', 'all')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Build query
        query = db.query(ForecastLog)
        
        # Date filters
        if date_from:
            query = query.filter(ForecastLog.hora_alvo >= datetime.fromisoformat(date_from))
        if date_to:
            query = query.filter(ForecastLog.hora_alvo <= datetime.fromisoformat(date_to))
        
        # Status filter
        if status_filter == 'pending':
            query = query.filter(ForecastLog.valor_real.is_(None))
        elif status_filter == 'reconciled':
            query = query.filter(ForecastLog.valor_real.isnot(None))
        elif status_filter == 'high_error':
            query = query.filter(
                and_(
                    ForecastLog.erro_percentual.isnot(None),
                    (ForecastLog.erro_percentual > 20) | (ForecastLog.erro_percentual < -20)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Paginate
        logs = query.order_by(desc(ForecastLog.timestamp_previsao)).offset(
            (page - 1) * per_page
        ).limit(per_page).all()
        
        # Determine status for each log
        now = datetime.now()
        
        def get_status(log):
            if log.valor_real is not None:
                if log.erro_percentual and abs(float(log.erro_percentual)) > 20:
                    return 'high_error'
                return 'reconciled'
            elif log.hora_alvo < now:
                return 'awaiting'
            else:
                return 'pending'
        
        return jsonify({
            "success": True,
            "data": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page,
                "logs": [
                    {
                        "id": log.id,
                        "timestamp_previsao": log.timestamp_previsao.isoformat() if log.timestamp_previsao else None,
                        "hora_alvo": log.hora_alvo.isoformat() if log.hora_alvo else None,
                        "valor_previsto": float(log.valor_previsto) if log.valor_previsto else 0,
                        "valor_real": float(log.valor_real) if log.valor_real else None,
                        "erro_percentual": float(log.erro_percentual) if log.erro_percentual else None,
                        "status": get_status(log),
                        "baseline": float(log.baseline_usado) if log.baseline_usado else None,
                        "modelo_versao": log.modelo_versao,
                        "fatores_usados": log.fatores_usados or {}
                    } for log in logs
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting forecast logs: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        db.close()


@api_bp.route('/forecast/learning/logs/<int:log_id>', methods=['GET'])
def get_forecast_log_detail(log_id: int):
    """
    Get detailed information about a specific forecast log
    For the detail modal
    """
    from app.models.forecast_learning import ForecastLog
    from datetime import datetime
    
    db = SessionLocal()
    try:
        log = db.query(ForecastLog).filter(ForecastLog.id == log_id).first()
        
        if not log:
            return jsonify({
                "success": False,
                "error": "Log not found"
            }), 404
        
        # Determine status
        now = datetime.now()
        if log.valor_real is not None:
            status = 'high_error' if log.erro_percentual and abs(float(log.erro_percentual)) > 20 else 'reconciled'
        elif log.hora_alvo < now:
            status = 'awaiting'
        else:
            status = 'pending'
        
        return jsonify({
            "success": True,
            "data": {
                "id": log.id,
                "timestamp_previsao": log.timestamp_previsao.isoformat() if log.timestamp_previsao else None,
                "hora_alvo": log.hora_alvo.isoformat() if log.hora_alvo else None,
                "valor_previsto": float(log.valor_previsto) if log.valor_previsto else 0,
                "valor_real": float(log.valor_real) if log.valor_real else None,
                "erro_percentual": float(log.erro_percentual) if log.erro_percentual else None,
                "status": status,
                "baseline_usado": float(log.baseline_usado) if log.baseline_usado else None,
                "modelo_versao": log.modelo_versao,
                "fatores_usados": log.fatores_usados or {}
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting forecast log detail: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        db.close()


@api_bp.route('/forecast/learning/analytics', methods=['GET'])
def get_forecast_analytics():
    """
    Get analytics data for the Hyper AI panel
    - Precision evolution by week
    - Precision by factor type
    - Auto-generated insights
    """
    from datetime import datetime, timedelta
    from sqlalchemy import func, and_, extract
    from app.models.forecast_learning import ForecastLog
    
    db = SessionLocal()
    try:
        now = datetime.now()
        
        # Get reconciled logs from last 30 days
        thirty_days_ago = now - timedelta(days=30)
        
        logs = db.query(ForecastLog).filter(
            and_(
                ForecastLog.timestamp_previsao >= thirty_days_ago,
                ForecastLog.valor_real.isnot(None),
                ForecastLog.erro_percentual.isnot(None)
            )
        ).all()
        
        # Group by week
        from collections import defaultdict
        weekly_data = defaultdict(lambda: {"errors": [], "count": 0})
        
        for log in logs:
            week = log.timestamp_previsao.strftime("%Y-W%W")
            weekly_data[week]["errors"].append(abs(float(log.erro_percentual)))
            weekly_data[week]["count"] += 1
        
        precision_by_week = []
        for week in sorted(weekly_data.keys()):
            errors = weekly_data[week]["errors"]
            precision_by_week.append({
                "semana": week,
                "erro_medio": round(sum(errors) / len(errors), 1) if errors else 0,
                "total_previsoes": weekly_data[week]["count"]
            })
        
        # Group by factor - analyze which factors have highest errors
        factor_errors = defaultdict(lambda: defaultdict(list))
        for log in logs:
            fatores = log.fatores_usados or {}
            erro = abs(float(log.erro_percentual))
            for fator_tipo, valor in fatores.items():
                if isinstance(valor, (int, float)):
                    key = f"{valor:.2f}"
                else:
                    key = str(valor)
                factor_errors[fator_tipo][key].append(erro)
        
        precision_by_factor = {}
        for fator_tipo, keys in factor_errors.items():
            precision_by_factor[fator_tipo] = {}
            for key, errors in keys.items():
                precision_by_factor[fator_tipo][key] = round(sum(errors) / len(errors), 1) if errors else 0
        
        # Generate insights
        insights = []
        
        # Overall precision
        if logs:
            all_errors = [abs(float(log.erro_percentual)) for log in logs]
            avg_error = sum(all_errors) / len(all_errors)
            
            if avg_error <= 10:
                insights.append({
                    "tipo": "success",
                    "mensagem": f"Precisão excelente! Erro médio de {avg_error:.1f}%",
                    "recomendacao": "Mantenha o sistema coletando dados para melhorias contínuas"
                })
            elif avg_error <= 20:
                insights.append({
                    "tipo": "info",
                    "mensagem": f"Precisão boa. Erro médio de {avg_error:.1f}%",
                    "recomendacao": "O sistema está aprendendo, precisão deve melhorar com mais dados"
                })
            else:
                insights.append({
                    "tipo": "warning",
                    "mensagem": f"Precisão em desenvolvimento. Erro médio de {avg_error:.1f}%",
                    "recomendacao": "Aguarde mais dados para calibração automática"
                })
        
        # Check for high-error factors
        for fator_tipo, keys in precision_by_factor.items():
            for key, erro in keys.items():
                if erro > 25:
                    insights.append({
                        "tipo": "warning",
                        "mensagem": f"Fator '{fator_tipo}={key}' tem erro alto ({erro}%)",
                        "recomendacao": "Considere coletar mais dados para este cenário"
                    })
        
        # Trend analysis
        if len(precision_by_week) >= 2:
            first_week_error = precision_by_week[0]["erro_medio"]
            last_week_error = precision_by_week[-1]["erro_medio"]
            
            if last_week_error < first_week_error - 2:
                insights.append({
                    "tipo": "success",
                    "mensagem": "Tendência de melhoria detectada!",
                    "recomendacao": f"Erro reduziu de {first_week_error}% para {last_week_error}%"
                })
            elif last_week_error > first_week_error + 2:
                insights.append({
                    "tipo": "warning",
                    "mensagem": "Precisão diminuiu recentemente",
                    "recomendacao": "Verifique se houve mudanças no padrão de vendas"
                })
        
        # Pending reconciliation count
        pending = db.query(ForecastLog).filter(
            ForecastLog.valor_real.is_(None)
        ).count()
        
        if pending > 0:
            insights.append({
                "tipo": "info",
                "mensagem": f"{pending} previsões aguardando reconciliação",
                "recomendacao": "Próxima reconciliação automática: 03:00"
            })
        
        return jsonify({
            "success": True,
            "data": {
                "precisao_por_semana": precision_by_week,
                "precisao_por_fator": precision_by_factor,
                "insights": insights,
                "total_logs_analisados": len(logs)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting forecast analytics: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        db.close()
