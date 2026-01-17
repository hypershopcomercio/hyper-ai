from flask import jsonify, request
from app.api import api_bp
from app.core.database import SessionLocal
from app.models.financial import FixedCost, ProductFinancialMetric
from app.services.financial_service import FinancialService

@api_bp.route("/financial/costs", methods=["GET"])
def get_fixed_costs():
    db = SessionLocal()
    try:
        costs = db.query(FixedCost).filter(FixedCost.active == True).all()
        # Serialize
        result = [
            {
                "id": c.id,
                "name": c.name,
                "amount": float(c.amount),
                "category": c.category,
                "day_of_month": c.day_of_month,
                "active": c.active
            } for c in costs
        ]
        return jsonify(result)
    finally:
        db.close()

@api_bp.route("/financial/costs", methods=["POST"])
def create_fixed_cost():
    data = request.json
    db = SessionLocal()
    try:
        cost = FixedCost(
            name=data.get("name"),
            amount=data.get("amount"),
            category=data.get("category", "operational"),
            day_of_month=data.get("day_of_month", 1),
            active=True
        )
        db.add(cost)
        db.commit()
        db.refresh(cost)
        
        return jsonify({
            "id": cost.id,
            "name": cost.name,
            "amount": float(cost.amount),
            "status": "created"
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@api_bp.route("/financial/costs/<int:cost_id>", methods=["PUT"])
def update_fixed_cost(cost_id):
    data = request.json
    db = SessionLocal()
    try:
        cost = db.query(FixedCost).filter(FixedCost.id == cost_id).first()
        if not cost:
            return jsonify({"error": "Cost not found"}), 404
        
        if "name" in data:
            cost.name = data["name"]
        if "amount" in data:
            cost.amount = data["amount"]
        if "category" in data:
            cost.category = data["category"]
        if "day_of_month" in data:
            cost.day_of_month = data["day_of_month"]
            
        db.commit()
        db.refresh(cost)
        
        return jsonify({
            "id": cost.id,
            "name": cost.name,
            "amount": float(cost.amount),
            "status": "updated"
        })
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@api_bp.route("/financial/costs/<int:cost_id>", methods=["DELETE"])
def delete_fixed_cost(cost_id):
    db = SessionLocal()
    try:
        cost = db.query(FixedCost).filter(FixedCost.id == cost_id).first()
        if not cost:
            return jsonify({"error": "Cost not found"}), 404
        
        cost.active = False
        db.commit()
        return jsonify({"status": "deleted"})
    finally:
        db.close()

@api_bp.route("/financial/calculate-metrics", methods=["POST"])
def trigger_calculation():
    db = SessionLocal()
    try:
        service = FinancialService(db)
        service.calculate_metrics()
        return jsonify({"status": "calculation_completed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@api_bp.route("/financial/metrics/<sku>", methods=["GET"])
def get_sku_metrics(sku):
    db = SessionLocal()
    try:
        metric = db.query(ProductFinancialMetric).filter(ProductFinancialMetric.sku == sku).first()
        if not metric:
            return jsonify({})
        
        return jsonify({
            "sku": metric.sku,
            "return_rate_90d": metric.return_rate_90d,
            "avg_return_cost": float(metric.avg_return_cost),
            "revenue_share_30d": metric.revenue_share_30d,
            "calculated_fixed_cost_share": float(metric.calculated_fixed_cost_share),
            "last_calculated_at": metric.last_calculated_at.isoformat() if metric.last_calculated_at else None
        })
    finally:
        db.close()

@api_bp.route("/financial/ads/<ad_id>/simulation", methods=["GET"])
def get_ad_simulation_data(ad_id):
    """
    Retorna dados financeiros do anúncio para simulação de margem.
    Include: Custos Tiny, Dados Fiscais ML, Métricas Financeiras Calculadas.
    """
    db = SessionLocal()
    from app.models.ad import Ad
    from app.services.tax_service import TaxService
    from app.models.financial import ProductFinancialMetric
    
    try:
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            return jsonify({"error": "Ad not found"}), 404
            
        # Buscar métricas do SKU
        # Storage & Integrity Logic
        l_mm = float(ad.length_mm or 0)
        w_mm = float(ad.width_mm or 0)
        h_mm = float(ad.height_mm or 0)
        
        # Default Rates (ML 2024 Base)
        daily_fee = 0.007 # Small
        inbound_est = 0.50 
        
        dims = sorted([l_mm/10, w_mm/10, h_mm/10]) # cm
        
        if dims[2] <= 25 and dims[1] <= 15 and dims[0] <= 12:
            daily_fee = 0.007
            inbound_est = 0.80
        elif dims[2] <= 51 and dims[1] <= 36 and dims[0] <= 28:
            daily_fee = 0.013
            inbound_est = 1.50
        elif dims[2] <= 70 and dims[1] <= 60 and dims[0] <= 60:
            daily_fee = 0.047
            inbound_est = 4.00
        else:
            daily_fee = 0.107
            inbound_est = 9.00

        # Buscar métricas do SKU
        sku_metrics = {}
        if ad.sku:
            metric = db.query(ProductFinancialMetric).filter(ProductFinancialMetric.sku == ad.sku).first()
            if metric:
                # Use DB values or Dynamic Fallback
                daily_storage = float(metric.daily_storage_fee or daily_fee)
                inbound_cost = float(metric.inbound_freight_cost or inbound_est)
                
                days_stock = float(ad.days_of_stock or 30)
                avg_days_stock = days_stock / 2
                
                total_storage = (daily_storage * avg_days_stock) + inbound_cost
                
                risk_storage = float(metric.storage_risk_cost or 0)
                if days_stock > 120:
                     risk_storage += (days_stock - 120) * (daily_storage * 3)

                sku_metrics = {
                    "return_rate": metric.return_rate_90d,
                    "fixed_cost_share": float(metric.calculated_fixed_cost_share),
                    "avg_return_cost": float(metric.avg_return_cost),
                    "storage_cost": float(total_storage),
                    "daily_storage_fee": daily_storage,
                    "inbound_freight_cost": inbound_cost,
                    "storage_risk_cost": risk_storage
                }
            else:
                 # No metric, use defaults
                 days_stock = float(ad.days_of_stock or 30)
                 total_storage = (daily_fee * (days_stock / 2)) + inbound_est
                 sku_metrics = {
                    "return_rate": 0.03,
                    "fixed_cost_share": 0.0,
                    "avg_return_cost": 20.0,
                    "storage_cost": total_storage,
                    "daily_storage_fee": daily_fee,
                    "inbound_freight_cost": inbound_est,
                    "storage_risk_cost": 0.0
                 }
        
        # Dados para retorno - Estimativas se dados faltantes
        cost = ad.cost if ad.cost else 0.0
        
        # Tax Rate: Buscar valor atual do sistema calculado via TaxService
        # Tenta buscar valor cacheado no config, ou calcula on-the-fly se necessario
        from app.models.system_config import SystemConfig
        sc_tax = db.query(SystemConfig).filter(SystemConfig.key == 'aliquota_simples').first()
        if sc_tax and sc_tax.value:
            tax_rate = float(sc_tax.value) / 100.0
        else:
            ts = TaxService(db)
            tax_rate = ts.update_system_tax_rate() / 100.0
            
        # Commission: Usar dado real do DB ou Fallback
        commission = ad.commission_percent if ad.commission_percent else 0.0
        
        # Tentar calcular baseado no custo salvo se percentual for 0
        if commission == 0.0 and ad.commission_cost and ad.price and ad.price > 0:
            commission = ad.commission_cost / ad.price
        
        # Fallback se não tiver comissão salva nem custo mas tiver tipo de anúncio
        if commission == 0.0 and ad.listing_type_id:
            if 'gold_pro' in ad.listing_type_id:
                commission = 0.19 # Premium (~19%)
            elif 'gold_special' in ad.listing_type_id:
                commission = 0.14 # Clássico (~14%)
        
        shipping = ad.shipping_cost if ad.shipping_cost else 0.0
        
        response = {
            "ad_id": ad.id,
            "sku": ad.sku,
            "price": ad.price,
            "cost_product": cost,
            "shipping_cost": shipping,
            "commission_rate": commission,
            "tax_rate": tax_rate,
            "financial_metrics": sku_metrics
        }
        
        return jsonify(response)
    finally:
        db.close()

@api_bp.route("/financial/otb", methods=["GET"])
def get_otb_data():
    db = SessionLocal()
    try:
        service = FinancialService(db)
        
        days = request.args.get("days", 30, type=int)
        weeks_supply = request.args.get("weeks_supply", 4, type=int)
        
        data = service.calculate_otb(days_period=days, target_weeks_supply=weeks_supply)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@api_bp.route("/financial/cash-flow", methods=["GET"])
def get_cash_flow_data():
    db = SessionLocal()
    try:
        service = FinancialService(db)
        
        days = request.args.get("days", 30, type=int)
        
        data = service.get_cash_flow_projection(days=days)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
