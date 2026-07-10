"""Endpoint read-only do painel que liga margem operacional e caixa."""

from flask import jsonify, request

from app.api import api_bp
from app.core.database import SessionLocal
from app.services.cashflow_panel_service import CashflowPanelService


@api_bp.route("/financial/cashflow-panel", methods=["GET"])
def get_cashflow_panel():
    db = SessionLocal()
    try:
        days = request.args.get("days", 30, type=int) or 30
        return jsonify(CashflowPanelService(db).get_panel(days=days))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    finally:
        db.close()
