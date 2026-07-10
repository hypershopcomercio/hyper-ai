"""
Endpoints do módulo Full (Fulfillment ML) — Fase 1, read-only.

  GET  /full/overview            resumo operacional (unidades, valor imobilizado, alertas)
  GET  /full/inventory           lista por produto (estoque por estado, cobertura, custo real/un)
  GET  /full/inventory/<ad_id>   detalhe + série histórica diária
  POST /full/sync                dispara sync manual (mesmo do job diário)
  GET/POST/PUT/DELETE /full/tariffs[/<id>]   CRUD da tabela de tarifas (Settings)

Nada escreve no ML. O custo real calculado aqui alimenta ProductFinancialMetric.
"""
import logging
from datetime import date, timedelta

from flask import request, jsonify
from sqlalchemy import func

from app.api import api_bp
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.financial import ProductFinancialMetric
from app.models.full import FullInventory, FullStockDaily, FullStorageTariff

logger = logging.getLogger(__name__)

AGED_DEFAULT = 90       # dias — limiar de estoque antigo para os alertas do overview
LOW_COVERAGE_DAYS = 14  # dias — cobertura baixa (risco de ruptura)


@api_bp.route('/full/overview', methods=['GET'])
def full_overview():
    db = SessionLocal()
    try:
        rows = db.query(FullInventory).all()
        if not rows:
            return jsonify({
                "has_data": False,
                "message": "Sem dados de Full. Rode o sync: python -m app.scripts.backfill_full_stock",
                "summary": {}, "alerts": {}
            })

        # custo do produto por ad (valor imobilizado) e custo real de armazenagem por sku
        ad_ids = [r.ad_id for r in rows if r.ad_id]
        ads_map = {a.id: a for a in db.query(Ad).filter(Ad.id.in_(ad_ids)).all()} if ad_ids else {}

        units_available = units_transit = units_na = 0
        immobilized = 0.0
        products = set()
        low_cov = aged = stranded = 0

        for r in rows:
            units_available += r.available_qty or 0
            units_transit += r.in_transit_qty or 0
            units_na += r.not_available_qty or 0
            if r.ad_id:
                products.add(r.ad_id)
            ad = ads_map.get(r.ad_id)
            if ad and ad.cost:
                immobilized += (r.available_qty or 0) * float(ad.cost)
            if r.days_of_stock is not None and r.days_of_stock < LOW_COVERAGE_DAYS:
                low_cov += 1
            if r.oldest_stock_days is not None and r.oldest_stock_days > AGED_DEFAULT:
                aged += 1
            if (r.available_qty or 0) > 0 and (r.days_of_stock is None or r.days_of_stock > 180):
                stranded += 1

        return jsonify({
            "has_data": True,
            "summary": {
                "products_count": len(products),
                "inventories_count": len(rows),
                "units_available": units_available,
                "units_in_transit": units_transit,
                "units_not_available": units_na,
                "immobilized_value": round(immobilized, 2),
            },
            "alerts": {
                "low_coverage": low_cov,   # cobertura < 14 dias
                "aged_stock": aged,        # lote mais velho > 90 dias
                "stranded": stranded,      # com estoque e sem giro (>180d ou sem venda)
            },
        })
    except Exception as e:
        logger.error(f"full_overview: {e}")
        return jsonify({"has_data": False, "error": str(e)}), 500
    finally:
        db.close()


@api_bp.route('/full/inventory', methods=['GET'])
def full_inventory_list():
    db = SessionLocal()
    try:
        sort_by = request.args.get('sort_by', 'coverage')  # coverage | aged | available
        only_alerts = request.args.get('alerts') == '1'

        rows = db.query(FullInventory).all()
        ad_ids = [r.ad_id for r in rows if r.ad_id]
        skus = [r.sku for r in rows if r.sku]
        ads_map = {a.id: a for a in db.query(Ad).filter(Ad.id.in_(ad_ids)).all()} if ad_ids else {}
        metric_map = {}
        if skus:
            metric_map = {m.sku: m for m in db.query(ProductFinancialMetric)
                          .filter(ProductFinancialMetric.sku.in_(skus)).all()}

        items = []
        for r in rows:
            ad = ads_map.get(r.ad_id)
            metric = metric_map.get(r.sku)
            storage_unit = float(metric.storage_cost) if metric and metric.storage_cost else None
            storage_risk = float(metric.storage_risk_cost) if metric and metric.storage_risk_cost else None
            is_aged = r.oldest_stock_days is not None and r.oldest_stock_days > AGED_DEFAULT
            is_low = r.days_of_stock is not None and r.days_of_stock < LOW_COVERAGE_DAYS

            if only_alerts and not (is_aged or is_low):
                continue

            items.append({
                "inventory_id": r.inventory_id,
                "ad_id": r.ad_id,
                "sku": r.sku,
                "variation_id": r.variation_id,
                "title": ad.title if ad else None,
                "thumbnail": ad.thumbnail if ad else None,
                "permalink": ad.permalink if ad else None,
                "available_qty": r.available_qty,
                "in_transit_qty": r.in_transit_qty,
                "not_available_qty": r.not_available_qty,
                "total_qty": r.total_qty,
                "days_of_stock": r.days_of_stock,
                "oldest_stock_days": r.oldest_stock_days,
                "storage_cost_unit": storage_unit,
                "storage_risk_unit": storage_risk,
                "is_aged": is_aged,
                "is_low_coverage": is_low,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            })

        # ordenação: cobertura mais baixa primeiro / mais antigo primeiro / mais estoque
        if sort_by == 'aged':
            items.sort(key=lambda x: (x["oldest_stock_days"] is None, -(x["oldest_stock_days"] or 0)))
        elif sort_by == 'available':
            items.sort(key=lambda x: -(x["available_qty"] or 0))
        else:  # coverage
            items.sort(key=lambda x: (x["days_of_stock"] is None, x["days_of_stock"] or 1e9))

        return jsonify({"has_data": bool(items), "count": len(items), "items": items})
    except Exception as e:
        logger.error(f"full_inventory_list: {e}")
        return jsonify({"has_data": False, "error": str(e)}), 500
    finally:
        db.close()


@api_bp.route('/full/inventory/<ad_id>', methods=['GET'])
def full_inventory_detail(ad_id):
    db = SessionLocal()
    try:
        rows = db.query(FullInventory).filter(FullInventory.ad_id == ad_id).all()
        if not rows:
            return jsonify({"error": "Sem estoque Full para este anúncio."}), 404

        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        inv_ids = [r.inventory_id for r in rows]

        # série diária (últimos 60 dias) agregada por dia
        since = date.today() - timedelta(days=60)
        daily = db.query(
            FullStockDaily.day,
            func.sum(FullStockDaily.available_qty),
            func.sum(FullStockDaily.in_transit_qty),
            func.sum(FullStockDaily.not_available_qty),
        ).filter(
            FullStockDaily.inventory_id.in_(inv_ids),
            FullStockDaily.day >= since,
        ).group_by(FullStockDaily.day).order_by(FullStockDaily.day).all()

        return jsonify({
            "ad_id": ad_id,
            "title": ad.title if ad else None,
            "thumbnail": ad.thumbnail if ad else None,
            "inventories": [{
                "inventory_id": r.inventory_id,
                "variation_id": r.variation_id,
                "available_qty": r.available_qty,
                "in_transit_qty": r.in_transit_qty,
                "not_available_qty": r.not_available_qty,
                "total_qty": r.total_qty,
                "days_of_stock": r.days_of_stock,
                "oldest_stock_days": r.oldest_stock_days,
            } for r in rows],
            "daily_series": [{
                "date": d[0].isoformat(),
                "available": int(d[1] or 0),
                "in_transit": int(d[2] or 0),
                "not_available": int(d[3] or 0),
            } for d in daily],
        })
    except Exception as e:
        logger.error(f"full_inventory_detail: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@api_bp.route('/full/sync', methods=['POST'])
def full_sync():
    """Dispara o sync + custo sob demanda (o job diário também faz isso)."""
    from app.services.full_service import FullService
    svc = FullService()
    try:
        result = svc.sync_and_cost()
        return jsonify({"success": True, **result})
    except Exception as e:
        logger.error(f"full_sync: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        svc.close()


# ------------------------------------------------------------------
# Tarifas (Settings)
# ------------------------------------------------------------------
def _tariff_dict(t: FullStorageTariff):
    return {
        "id": t.id,
        "name": t.name,
        "min_volume_l": t.min_volume_l,
        "max_volume_l": t.max_volume_l,
        "daily_fee": float(t.daily_fee) if t.daily_fee is not None else None,
        "inbound_fee": float(t.inbound_fee) if t.inbound_fee is not None else None,
        "aged_days_threshold": t.aged_days_threshold,
        "aged_daily_factor": t.aged_daily_factor,
        "active": t.active,
    }


@api_bp.route('/full/tariffs', methods=['GET'])
def full_tariffs_list():
    db = SessionLocal()
    try:
        tariffs = db.query(FullStorageTariff).order_by(FullStorageTariff.min_volume_l).all()
        return jsonify({"tariffs": [_tariff_dict(t) for t in tariffs]})
    finally:
        db.close()


@api_bp.route('/full/tariffs', methods=['POST'])
def full_tariffs_create():
    db = SessionLocal()
    try:
        d = request.get_json(silent=True) or {}
        t = FullStorageTariff(
            name=d.get("name"),
            min_volume_l=float(d.get("min_volume_l") or 0),
            max_volume_l=float(d["max_volume_l"]) if d.get("max_volume_l") not in (None, "") else None,
            daily_fee=float(d.get("daily_fee") or 0),
            inbound_fee=float(d.get("inbound_fee") or 0),
            aged_days_threshold=int(d.get("aged_days_threshold") or 90),
            aged_daily_factor=float(d.get("aged_daily_factor") or 3.0),
            active=bool(d.get("active", True)),
        )
        db.add(t)
        db.commit()
        return jsonify({"success": True, "tariff": _tariff_dict(t)}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)}), 400
    finally:
        db.close()


@api_bp.route('/full/tariffs/<int:tariff_id>', methods=['PUT'])
def full_tariffs_update(tariff_id):
    db = SessionLocal()
    try:
        t = db.query(FullStorageTariff).filter_by(id=tariff_id).first()
        if not t:
            return jsonify({"success": False, "error": "Tarifa não encontrada"}), 404
        d = request.get_json(silent=True) or {}
        if "name" in d: t.name = d["name"]
        if "min_volume_l" in d: t.min_volume_l = float(d["min_volume_l"] or 0)
        if "max_volume_l" in d:
            t.max_volume_l = float(d["max_volume_l"]) if d["max_volume_l"] not in (None, "") else None
        if "daily_fee" in d: t.daily_fee = float(d["daily_fee"] or 0)
        if "inbound_fee" in d: t.inbound_fee = float(d["inbound_fee"] or 0)
        if "aged_days_threshold" in d: t.aged_days_threshold = int(d["aged_days_threshold"] or 90)
        if "aged_daily_factor" in d: t.aged_daily_factor = float(d["aged_daily_factor"] or 3.0)
        if "active" in d: t.active = bool(d["active"])
        db.commit()
        return jsonify({"success": True, "tariff": _tariff_dict(t)})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)}), 400
    finally:
        db.close()


@api_bp.route('/full/tariffs/<int:tariff_id>', methods=['DELETE'])
def full_tariffs_delete(tariff_id):
    db = SessionLocal()
    try:
        t = db.query(FullStorageTariff).filter_by(id=tariff_id).first()
        if not t:
            return jsonify({"success": False, "error": "Tarifa não encontrada"}), 404
        db.delete(t)
        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)}), 400
    finally:
        db.close()
