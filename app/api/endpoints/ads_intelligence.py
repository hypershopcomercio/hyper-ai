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

logger = logging.getLogger(__name__)

TZ_BR = timezone(timedelta(hours=-3))


def _classify(spend, ads_revenue, acos, margin_percent):
    if spend > 0 and ads_revenue <= 0:
        return "queimando"
    if margin_percent is not None and margin_percent > 0 and acos is not None:
        if acos >= margin_percent:
            return "prejuizo"
        if acos >= margin_percent * 0.7:
            return "atencao"
        if acos <= margin_percent * 0.4:
            return "escalar"
        return "saudavel"
    # Margem desconhecida: bandas fixas conservadoras de ACOS
    if acos is None:
        return "saudavel"
    if acos >= 25:
        return "atencao"
    if acos <= 10:
        return "escalar"
    return "saudavel"


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

        items = []
        totals = {"spend": 0.0, "ads_revenue": 0.0, "clicks": 0, "prints": 0, "units": 0}
        class_counts = {}
        burn_total = 0.0

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

            classification = _classify(spend, ads_revenue, acos, margin_percent)
            class_counts[classification] = class_counts.get(classification, 0) + 1
            if classification in ("queimando", "prejuizo"):
                burn_total += spend

            # Lucro estimado das vendas via Ads: receita * margem% - gasto
            ads_profit = None
            if margin_percent is not None:
                ads_profit = round(ads_revenue * (margin_percent / 100.0) - spend, 2)

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

        return jsonify({
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
