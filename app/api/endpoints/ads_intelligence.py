"""
Ads Intelligence — visão read-only de performance de Product Ads por item.

Cruza gasto real (ml_ads_item_daily) com margem do anúncio para classificar
onde o dinheiro está sendo queimado. NÃO altera nada no ML (somente leitura).

Classificações:
  queimando  — gastou e não vendeu NADA via Ads no período
  prejuizo   — ACOS >= margem do produto (cada venda via Ads dá prejuízo)
  atencao    — ACOS >= 70% da margem (lucro via Ads quase zerado)
  saudavel   — ACOS confortável dentro da margem
  escalar    — ACOS <= 40% da margem e vendendo (candidato a aumentar verba)
"""
from flask import request, jsonify
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import func

from app.api import api_bp
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.ml_ads_item_daily import MlAdsItemDaily
# Fonte única da lógica de classificação/sugestão (compartilhada com o job diário)
from app.services.ads_decision_engine import (
    _classify, _suggest_action, AdsDecisionEngine, ads_write_enabled,
    get_finance_context, max_acos_for,
)

logger = logging.getLogger(__name__)

TZ_BR = timezone(timedelta(hours=-3))


@api_bp.route('/ads-intelligence/overview', methods=['GET'])
def ads_intelligence_overview():
    db = SessionLocal()
    try:
        days = int(request.args.get('days', '30'))
        days = max(1, min(days, 120))

        today_br = datetime.now(TZ_BR).date()
        start_date = today_br - timedelta(days=days)

        # 1. Aggregate per item from real daily data
        agg = db.query(
            MlAdsItemDaily.item_id,
            func.sum(MlAdsItemDaily.cost).label('spend'),
            func.sum(MlAdsItemDaily.revenue).label('ads_revenue'),
            func.sum(MlAdsItemDaily.clicks).label('clicks'),
            func.sum(MlAdsItemDaily.prints).label('prints'),
            func.sum(MlAdsItemDaily.units_quantity).label('units'),
            func.count(MlAdsItemDaily.id).label('days_active'),
        ).filter(
            MlAdsItemDaily.date >= start_date,
            MlAdsItemDaily.date <= today_br
        ).group_by(MlAdsItemDaily.item_id).all()

        if not agg:
            return jsonify({
                "has_data": False,
                "message": "Sem dados em ml_ads_item_daily para o período. Rode o backfill: python -m app.scripts.backfill_ads_item_daily",
                "items": [], "summary": {}, "daily_series": []
            })

        # 2. Join Ad metadata (title, price, margin)
        item_ids = [r.item_id for r in agg]
        ads_map = {a.id: a for a in db.query(Ad).filter(Ad.id.in_(item_ids)).all()}

        # Contexto financeiro (custos fixos, meta líquida, OTB) + ciclo de vida
        finance_ctx = get_finance_context(db)
        engine = AdsDecisionEngine(db)
        units_alltime = dict(db.query(
            MlAdsItemDaily.item_id, func.sum(MlAdsItemDaily.units_quantity)
        ).filter(MlAdsItemDaily.item_id.in_(item_ids)).group_by(MlAdsItemDaily.item_id).all())
        burden = finance_ctx["fixed_burden_pct"] if finance_ctx["complete"] else None
        target_net = finance_ctx["target_net_pct"] if finance_ctx["complete"] else None

        items = []
        totals = {"spend": 0.0, "ads_revenue": 0.0, "clicks": 0, "prints": 0, "units": 0}
        class_counts = {}
        burn_total = 0.0
        weighted_contrib = 0.0   # contribuição ponderada pela receita via Ads
        weighted_base = 0.0

        for r in agg:
            spend = float(r.spend or 0)
            ads_revenue = float(r.ads_revenue or 0)
            clicks = int(r.clicks or 0)
            prints = int(r.prints or 0)
            units = int(r.units or 0)

            if spend <= 0 and ads_revenue <= 0:
                continue

            ad = ads_map.get(r.item_id)
            margin_percent = None
            if ad and ad.margin_percent is not None:
                margin_percent = float(ad.margin_percent)

            acos = round(spend / ads_revenue * 100, 2) if ads_revenue > 0 else None
            roas = round(ads_revenue / spend, 2) if spend > 0 else None
            cpc = round(spend / clicks, 2) if clicks > 0 else None
            cvr = round(units / clicks * 100, 2) if clicks > 0 else None

            stage = engine.infer_lifecycle(ad, int(units_alltime.get(r.item_id) or 0))
            m_acos = max_acos_for(margin_percent, finance_ctx, stage)
            classification = _classify(spend, ads_revenue, acos, margin_percent,
                                       max_acos=m_acos, fixed_burden_pct=burden)
            class_counts[classification] = class_counts.get(classification, 0) + 1
            if classification in ("queimando", "prejuizo"):
                burn_total += spend

            # Lucro estimado das vendas via Ads: receita * margem% - gasto
            ads_profit = None
            if margin_percent is not None:
                ads_profit = round(ads_revenue * (margin_percent / 100.0) - spend, 2)

            # Margem líquida REAL: contribuição - ACOS - custos fixos
            net_margin_pct = None
            if burden is not None and margin_percent is not None and acos is not None:
                net_margin_pct = round(margin_percent - acos - burden, 2)
            if margin_percent is not None and ads_revenue > 0:
                weighted_contrib += margin_percent * ads_revenue
                weighted_base += ads_revenue

            totals["spend"] += spend
            totals["ads_revenue"] += ads_revenue
            totals["clicks"] += clicks
            totals["prints"] += prints
            totals["units"] += units

            items.append({
                "item_id": r.item_id,
                "title": ad.title if ad else None,
                "thumbnail": ad.thumbnail if ad else None,
                "permalink": ad.permalink if ad else None,
                "price": float(ad.price) if ad and ad.price else None,
                "status": ad.status if ad else None,
                "sku": ad.sku if ad else None,
                "spend": round(spend, 2),
                "ads_revenue": round(ads_revenue, 2),
                "clicks": clicks,
                "prints": prints,
                "units": units,
                "days_active": int(r.days_active or 0),
                "acos": acos,
                "roas": roas,
                "cpc": cpc,
                "cvr": cvr,
                "margin_percent": margin_percent,
                "ads_profit": ads_profit,
                "classification": classification,
                "lifecycle_stage": stage,
                "max_acos": m_acos,
                "net_margin_pct": net_margin_pct,
                "action": _suggest_action(classification, spend, ads_revenue, acos,
                                          margin_percent, int(r.days_active or 0), days,
                                          max_acos=m_acos, fixed_burden_pct=burden,
                                          target_net_pct=target_net),
            })

        # Worst offenders first: queimando/prejuizo by spend desc
        severity = {"queimando": 0, "prejuizo": 1, "atencao": 2, "saudavel": 3, "escalar": 4}
        items.sort(key=lambda x: (severity.get(x["classification"], 9), -x["spend"]))

        # 3. Daily series (chart)
        daily = db.query(
            MlAdsItemDaily.date,
            func.sum(MlAdsItemDaily.cost),
            func.sum(MlAdsItemDaily.revenue),
        ).filter(
            MlAdsItemDaily.date >= start_date,
            MlAdsItemDaily.date <= today_br
        ).group_by(MlAdsItemDaily.date).order_by(MlAdsItemDaily.date).all()

        daily_series = [{
            "date": d[0].isoformat(),
            "spend": round(float(d[1] or 0), 2),
            "ads_revenue": round(float(d[2] or 0), 2),
        } for d in daily]

        global_acos = round(totals["spend"] / totals["ads_revenue"] * 100, 2) if totals["ads_revenue"] > 0 else None

        # Equação da saúde: contribuição média (ponderada por receita via Ads)
        # - ACOS global - custos fixos % = líquida real do canal Ads
        avg_contribution = round(weighted_contrib / weighted_base, 2) if weighted_base > 0 else None
        global_net_pct = None
        if finance_ctx["complete"] and avg_contribution is not None and global_acos is not None:
            global_net_pct = round(avg_contribution - global_acos - finance_ctx["fixed_burden_pct"], 2)

        finance_block = {
            **finance_ctx,
            "avg_contribution_pct": avg_contribution,
            "global_net_pct": global_net_pct,
        }

        return jsonify({
            "finance": finance_block,
            "has_data": True,
            "period_days": days,
            "date_from": start_date.isoformat(),
            "date_to": today_br.isoformat(),
            "summary": {
                "total_spend": round(totals["spend"], 2),
                "total_ads_revenue": round(totals["ads_revenue"], 2),
                "global_acos": global_acos,
                "global_roas": round(totals["ads_revenue"] / totals["spend"], 2) if totals["spend"] > 0 else None,
                "total_clicks": totals["clicks"],
                "total_prints": totals["prints"],
                "total_units": totals["units"],
                "items_count": len(items),
                "class_counts": class_counts,
                "burn_total": round(burn_total, 2),
            },
            "items": items,
            "daily_series": daily_series,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"has_data": False, "error": str(e)}), 500
    finally:
        db.close()


# ============================================================
# Nível 1 — Fila de recomendações (aceitar/rejeitar com 1 clique)
# ============================================================

def _rec_to_dict(r):
    return {
        "id": r.id,
        "item_id": r.item_id,
        "action_code": r.action_code,
        "classification": r.classification,
        "lifecycle_stage": r.lifecycle_stage,
        "reason": r.reason,
        "impact": r.impact,
        "metrics_snapshot": r.metrics_snapshot,
        "status": r.status,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "decided_at": r.decided_at.isoformat() if r.decided_at else None,
        "executed_at": r.executed_at.isoformat() if r.executed_at else None,
        "execution_result": r.execution_result,
        "outcome": r.outcome,
    }


@api_bp.route('/ads-intelligence/recommendations', methods=['GET'])
def ads_recommendations_list():
    from app.models.ads_recommendation import AdsRecommendation
    db = SessionLocal()
    try:
        status = request.args.get('status', 'pending')
        query = db.query(AdsRecommendation)
        if status != 'all':
            query = query.filter(AdsRecommendation.status == status)
        recs = query.order_by(AdsRecommendation.created_at.desc()).limit(100).all()
        return jsonify({
            "recommendations": [_rec_to_dict(r) for r in recs],
            "ads_write_enabled": ads_write_enabled(),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@api_bp.route('/ads-intelligence/recommendations/generate', methods=['POST'])
def ads_recommendations_generate():
    """Gera recomendações sob demanda (o job diário também faz isso às 04:00)."""
    db = SessionLocal()
    try:
        engine = AdsDecisionEngine(db)
        summary = engine.generate_recommendations(days=int(request.args.get('days', '30')))
        return jsonify(summary)
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@api_bp.route('/ads-intelligence/recommendations/<int:rec_id>/decide', methods=['POST'])
def ads_recommendations_decide(rec_id):
    """
    Decide uma recomendação pendente: {"decision": "accept" | "reject"}.
    accept + ação executável + ADS_WRITE_ENABLED=true -> executa no ML na hora.
    accept com escrita desligada -> fica 'accepted' para execução manual.
    """
    from app.models.ads_recommendation import AdsRecommendation
    db = SessionLocal()
    try:
        payload = request.get_json(silent=True) or {}
        decision = payload.get("decision")
        if decision not in ("accept", "reject"):
            return jsonify({"error": "decision deve ser 'accept' ou 'reject'"}), 400

        rec = db.query(AdsRecommendation).filter_by(id=rec_id).first()
        if not rec:
            return jsonify({"error": "recomendação não encontrada"}), 404
        if rec.status != "pending":
            return jsonify({"error": f"recomendação já está '{rec.status}'"}), 409

        rec.decided_at = datetime.utcnow()
        rec.decided_by = "user"

        if decision == "reject":
            rec.status = "rejected"
            db.commit()
            return jsonify({"status": "rejected", "recommendation": _rec_to_dict(rec)})

        rec.status = "accepted"
        db.commit()

        engine = AdsDecisionEngine(db)
        executed, message = engine.execute_recommendation(rec)

        # Plano B: sem execução automática (escrita desligada, ação manual ou
        # API negou), guia a execução manual via WhatsApp na hora do aceite.
        if not executed:
            try:
                from app.services.notifier import send_whatsapp
                snap = rec.metrics_snapshot or {}
                action_labels = {"pausar": "PAUSAR", "reduzir_ou_pausar": "REDUZIR/PAUSAR", "aumentar": "AUMENTAR verba de"}
                send_whatsapp(
                    f"✅ Você aceitou: {action_labels.get(rec.action_code, rec.action_code)} "
                    f"{(snap.get('title') or rec.item_id)[:60]} ({rec.item_id})\n"
                    f"Execução automática indisponível — faça no Mercado Ads:\n"
                    f"https://ads.mercadolivre.com.br\n"
                    f"Busque pelo código {rec.item_id} na campanha."
                )
            except Exception as e:
                logger.warning(f"WhatsApp do plano B falhou (não-fatal): {e}")

        return jsonify({
            "status": rec.status,   # executed | failed | accepted (escrita off / ação manual)
            "executed": executed,
            "message": message,
            "recommendation": _rec_to_dict(rec),
        })
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
