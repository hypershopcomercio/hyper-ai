from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

# from . import routes
from .endpoints import ads, dashboard, logs, alerts, settings, auth, sync, debug, webhooks, sse, forecast, factors, competitors, competitor_intelligence, financial, health, pricing, fiscal, nfe, ads_intelligence, full, cashflow_panel
