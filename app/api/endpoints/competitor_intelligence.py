"""
Endpoints Flask para Intelligence de Concorrentes.
"""
from flask import jsonify, request
from sqlalchemy import and_, desc, func
from datetime import datetime, timedelta
from app.api import api_bp
from app.core.database import SessionLocal
from app.models.competitor_intelligence import (
    CompetitorMetricsHistory,
    CompetitorImpactEvent,
    CompetitorThreatScore
)


@api_bp.route("/competitor-intelligence/ads/<ad_id>/competitors/metrics", methods=["GET"])
def get_competitor_metrics_history(ad_id):
    """
    Retorna histórico de métricas de concorrentes.
    """
    db = SessionLocal()
    try:
        hours = request.args.get('hours', 168, type=int)  # 7 dias por padrão
        competitor_id = request.args.get('competitor_id')
        
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = db.query(CompetitorMetricsHistory).filter(
            and_(
                CompetitorMetricsHistory.our_ad_id == ad_id,
                CompetitorMetricsHistory.timestamp >= since
            )
        )
        
        if competitor_id:
            query = query.filter(CompetitorMetricsHistory.competitor_id == competitor_id)
        
        metrics = query.order_by(desc(CompetitorMetricsHistory.timestamp)).limit(1000).all()
        
        # Agrupar por concorrente
        result = {}
        for metric in metrics:
            comp_id = metric.competitor_id
            if comp_id not in result:
                result[comp_id] = []
            
            result[comp_id].append({
                "timestamp": metric.timestamp.isoformat(),
                "price": float(metric.price) if metric.price else None,
                "visits": metric.visits,
                "sales": metric.sales,
                "conversion_rate": float(metric.conversion_rate) if metric.conversion_rate else None,
                "has_free_shipping": metric.has_free_shipping,
                "has_promotion": metric.has_promotion,
                "stock_available": metric.stock_available,
                "seller_reputation": metric.seller_reputation,
                "reviews_count": metric.reviews_count
            })
        
        return jsonify(result)
    finally:
        db.close()


@api_bp.route("/competitor-intelligence/ads/<ad_id>/competitors/impact-events", methods=["GET"])
def get_impact_events(ad_id):
    """
    Retorna eventos de impacto competitivo.
    """
    db = SessionLocal()
    try:
        competitor_id = request.args.get('competitor_id')
        limit = request.args.get('limit', 50, type=int)
        
        query = db.query(CompetitorImpactEvent).filter(
            CompetitorImpactEvent.our_ad_id == ad_id
        )
        
        if competitor_id:
            query = query.filter(CompetitorImpactEvent.competitor_id == competitor_id)
        
        events = query.order_by(desc(CompetitorImpactEvent.event_timestamp)).limit(limit).all()
        
        return jsonify([{
            "id": e.id,
            "competitor_id": e.competitor_id,
            "event_type": e.event_type,
            "event_timestamp": e.event_timestamp.isoformat(),
            "change_percentage": float(e.change_percentage) if e.change_percentage else None,
            "estimated_sales_lost": e.estimated_sales_lost,
            "correlation_score": float(e.correlation_score) if e.correlation_score else None,
            "confidence_level": e.confidence_level,
            "threat_score": e.threat_score,
            "diagnosis": e.diagnosis,
            "recommendation": e.recommendation,
            "action_taken": e.action_taken
        } for e in events])
    finally:
        db.close()


@api_bp.route("/competitor-intelligence/ads/<ad_id>/competitors/threat-scores", methods=["GET"])
def get_threat_scores(ad_id):
    """
    Retorna scores de ameaça dos concorrentes (mais recentes).
    """
    db = SessionLocal()
    try:
        # Pegar o score mais recente de cada concorrente
        subquery = db.query(
            CompetitorThreatScore.competitor_id,
            func.max(CompetitorThreatScore.calculated_at).label('max_date')
        ).filter(
            CompetitorThreatScore.our_ad_id == ad_id
        ).group_by(CompetitorThreatScore.competitor_id).subquery()
        
        scores = db.query(CompetitorThreatScore).join(
            subquery,
            and_(
                CompetitorThreatScore.competitor_id == subquery.c.competitor_id,
                CompetitorThreatScore.calculated_at == subquery.c.max_date
            )
        ).all()
        
        return jsonify([{
            "competitor_id": s.competitor_id,
            "total_threat_score": s.total_threat_score,
            "threat_level": s.threat_level,
            "summary": s.summary,
            "calculated_at": s.calculated_at.isoformat()
        } for s in scores])
    finally:
        db.close()


@api_bp.route("/competitor-intelligence/ads/<ad_id>/competitors/<competitor_id>/timeline", methods=["GET"])
def get_competitor_timeline(ad_id, competitor_id):
    """
    Retorna timeline completa de um concorrente: métricas + eventos.
    """
    db = SessionLocal()
    try:
        days = request.args.get('days', 30, type=int)
        since = datetime.utcnow() - timedelta(days=days)
        
        # Buscar métricas
        metrics = db.query(CompetitorMetricsHistory).filter(
            and_(
                CompetitorMetricsHistory.competitor_id == competitor_id,
                CompetitorMetricsHistory.our_ad_id == ad_id,
                CompetitorMetricsHistory.timestamp >= since
            )
        ).order_by(CompetitorMetricsHistory.timestamp).all()
        
        # Buscar eventos
        events = db.query(CompetitorImpactEvent).filter(
            and_(
                CompetitorImpactEvent.competitor_id == competitor_id,
                CompetitorImpactEvent.our_ad_id == ad_id,
                CompetitorImpactEvent.event_timestamp >= since
            )
        ).order_by(CompetitorImpactEvent.event_timestamp).all()
        
        return jsonify({
            "competitor_id": competitor_id,
            "period_start": since.isoformat(),
            "period_end": datetime.utcnow().isoformat(),
            "metrics": [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "competitor_price": float(m.price) if m.price else None,
                    "competitor_sales": m.sales,
                    "competitor_visits": m.visits,
                    "competitor_conversion": float(m.conversion_rate) if m.conversion_rate else None,
                    "our_price": float(m.our_price) if m.our_price else None,
                    "our_sales": m.our_sales,
                    "our_visits": m.our_visits,
                    "our_conversion": float(m.our_conversion_rate) if m.our_conversion_rate else None
                }
                for m in metrics
            ],
            "events": [
                {
                    "timestamp": e.event_timestamp.isoformat(),
                    "type": e.event_type,
                    "diagnosis": e.diagnosis,
                    "recommendation": e.recommendation,
                    "threat_score": e.threat_score,
                    "estimated_sales_lost": e.estimated_sales_lost
                }
                for e in events
            ]
        })
    finally:
        db.close()


@api_bp.route("/competitor-intelligence/ads/<ad_id>/competitors/<competitor_id>/force-update", methods=["POST"])
def force_competitor_update(ad_id, competitor_id):
    """
    Força atualização imediata das métricas de um concorrente.
    """
    db = SessionLocal()
    try:
        from app.services.competitor_metrics_scraper import CompetitorMetricsScraper
        
        scraper = CompetitorMetricsScraper(db)
        success = scraper.collect_and_save_metrics(competitor_id, ad_id)
        
        if success:
            return jsonify({"status": "success", "message": "Métricas atualizadas"})
        else:
            return jsonify({"status": "error", "message": "Falha ao atualizar métricas"}), 500
    finally:
        db.close()


@api_bp.route("/competitor-intelligence/ads/<ad_id>/impact-events/<int:event_id>/mark-action", methods=["POST"])
def mark_event_action_taken(ad_id, event_id):
    """
    Marca que uma ação foi tomada em resposta a um evento.
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        action_type = data.get('action_type', 'ignore')
        
        event = db.query(CompetitorImpactEvent).filter(
            and_(
                CompetitorImpactEvent.id == event_id,
                CompetitorImpactEvent.our_ad_id == ad_id
            )
        ).first()
        
        if not event:
            return jsonify({"error": "Evento não encontrado"}), 404
        
        event.action_taken = True
        event.action_type = action_type
        event.action_timestamp = datetime.utcnow()
        
        db.commit()
        
        return jsonify({"status": "success", "message": f"Ação '{action_type}' registrada"})
    finally:
        db.close()
