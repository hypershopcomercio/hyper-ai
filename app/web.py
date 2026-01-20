import logging
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from app.core.config import settings
from app.services.meli_auth import MeliAuthService
from app.core.database import SessionLocal
from app.models.token import Token

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as origens

from app.api import api_bp
app.register_blueprint(api_bp)

# Scheduler Setup
from apscheduler.schedulers.background import BackgroundScheduler
from app.scheduler.tasks import run_daily_sync
from app.jobs.forecast_jobs import (
    run_daily_predictions,
    run_hourly_reconciliation, 
    run_weekly_calibration,
    run_daily_snapshot
)
from app.jobs.competitor_jobs import (
    run_competitor_metrics_collection,
    run_impact_analysis,
    run_threat_score_calculation
)

scheduler = BackgroundScheduler()

# Daily sync at 04:00 AM
scheduler.add_job(func=run_daily_sync, trigger="cron", hour=4, minute=0, id="run_daily_sync")

# --- Forecast Automation ---
# 1. Daily Prediction Generation: At 00:00 (generates all 24h for next day)
scheduler.add_job(func=run_daily_predictions, trigger="cron", hour=0, minute=0, id="run_daily_predictions")

# 2. Reconciliation: Hourly at :05 (re-reconciles all of today's hours)
scheduler.add_job(func=run_hourly_reconciliation, trigger="cron", minute=5, id="run_hourly_reconciliation")

# 3. Micro-Calibration: Hourly at :10 (1% max adjustment per cycle)
scheduler.add_job(func=run_weekly_calibration, trigger="cron", minute=10, id="run_hourly_calibration")

# 4. Daily Snapshot: At 23:55 (saves day's learning metrics)
scheduler.add_job(func=run_daily_snapshot, trigger="cron", hour=23, minute=55, id="run_daily_snapshot")

# --- Competitor Intelligence Automation ---
# 5. Hourly Metrics Collection: At :15 (collect competitor metrics)
scheduler.add_job(func=run_competitor_metrics_collection, trigger="cron", minute=15, id="competitor_metrics_collection")

# 6. Hourly Impact Analysis: At :20 (analyze events and correlations)
scheduler.add_job(func=run_impact_analysis, trigger="cron", minute=20, id="competitor_impact_analysis")

# 7. Daily Threat Score: At 01:00 (calculate threat scores)
scheduler.add_job(func=run_threat_score_calculation, trigger="cron", hour=1, minute=0, id="competitor_threat_scores")

scheduler.start()
logger.info("Scheduler started: Forecast + Competitor Intelligence (Hourly :05, :10, :15, :20 + Daily 00:00, 01:00, 04:00, 23:55)")



@app.route("/oauth/meli/callback", methods=["GET"])
def meli_callback():
    """
    Rota de callback para o fluxo OAuth2 do Mercado Livre.
    
    Espera receber um parâmetro 'code' na URL.
    Troca este código por um Access Token e Refresh Token e os salva no banco de dados.
    """
    code = request.args.get("code")
    
    # 1. Validação do código
    if not code:
        return jsonify({"error": "Authorization code not provided"}), 400
    
    try:
        # 2. Inicializa o serviço de autenticação
        auth_service = MeliAuthService()
        
        # 3. Troca o código pelo token (POST para API do ML)
        # O serviço lança exceção se falhar
        tokens = auth_service.exchange_code_for_token(code)
        
        # 4. Salvar no banco de dados
        # Conforme arquitetura: SessionLocal e Modelo Token
        db = SessionLocal()
        try:
            # Limpa tokens anteriores (assumindo single-tenant/monousuário para este módulo)
            db.query(Token).delete()
            
            # Cria novo registro
            new_token = Token(
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                user_id=str(tokens["user_id"]),
                # Calcula expiração exata
                expires_at=datetime.datetime.now() + datetime.timedelta(seconds=tokens["expires_in"])
            )
            
            db.add(new_token)
            db.commit()
            
            logger.info(f"Token salvo com sucesso para User ID: {tokens.get('user_id')}")
            
            return jsonify({
                "message": "Autenticação realizada com sucesso!",
                "user_id": tokens.get("user_id"),
                "expires_in": tokens.get("expires_in")
            }), 200
            
        except Exception as db_e:
            db.rollback()
            logger.error(f"Erro ao salvar token no banco: {db_e}")
            return jsonify({"error": "Falha ao persistir dados de autenticação."}), 500
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Erro no fluxo OAuth: {e}")
        # Retorna erro detalhado (em produção, evitar expor exception pura se sensível)
        return jsonify({"error": f"Erro na troca de token: {str(e)}"}), 500

if __name__ == "__main__":
    # Execução para teste local
    print(f"Servidor rodando. Configure o Redirect URI no ML para: {settings.MELI_REDIRECT_URI if settings.MELI_REDIRECT_URI else 'http://localhost:5000/oauth/meli/callback'}")
    app.run(host="0.0.0.0", port=5000, debug=True)
