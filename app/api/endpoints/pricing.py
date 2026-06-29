from flask import jsonify, request
from app.api import api_bp
from app.api.endpoints.auth import require_auth
import logging

logger = logging.getLogger(__name__)

@api_bp.route('/pricing/status', methods=['GET'])
@require_auth
def get_pricing_status():
    """Retorna o status atual do módulo de precificação."""
    return jsonify({
        "module": "pricing",
        "status": "initialized",
        "automation_enabled": False,
        "message": "Módulo de precificação pronto para configuração."
    })

@api_bp.route('/pricing/strategies', methods=['GET'])
@require_auth
def get_strategies():
    """Lista as estratégias de precificação disponíveis."""
    # Placeholder para futuras estratégias
    strategies = [
        {"id": "competitor_match", "name": "Acompanhar Concorrente", "description": "Mantém o preço igual ou ligeiramente abaixo do concorrente principal."},
        {"id": "margin_safe", "name": "Margem de Segurança", "description": "Garante uma margem de lucro mínima em todas as vendas."},
        {"id": "inventory_clearance", "name": "Queima de Estoque", "description": "Reduz o preço progressivamente para itens com baixo giro."}
    ]
    return jsonify(strategies)

@api_bp.route('/pricing/simulate', methods=['POST'])
@require_auth
def simulate_pricing():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing payload"}), 400
            
        ad_id = data.get('ad_id', 'unknown')
        sim_price = data.get('simulate_price', 0.0)
        
        target_margin_percent = data.get('target_margin_percent', 0.0)
        
        p_cost = data.get('product_cost')
        t_profile = data.get('tax_profile')
        m_place = data.get('marketplace')
        
        is_mocked = True
        missing_fields = []
        hard_locks = []
        status = "approved"
        block_reason = None
        
        if not p_cost or not t_profile:
            is_mocked = False
            from app.core.database import SessionLocal
            from app.models.fiscal import MonthlyTaxConfig, ProductTaxProfile, ProductPurchaseCost
            from app.models.ad import Ad
            db = SessionLocal()
            try:
                ad = db.query(Ad).filter(Ad.id == ad_id).first()
                if not ad:
                    return jsonify({"success": False, "status": "blocked", "hard_locks": ["AD_NOT_FOUND"], "is_mocked": False}), 400
                
                m_config = db.query(MonthlyTaxConfig).filter(MonthlyTaxConfig.is_active == True).order_by(MonthlyTaxConfig.reference_month.desc()).first()
                if not m_config:
                    status = "blocked"
                    block_reason = "MISSING_MONTHLY_TAX_CONFIG"
                    hard_locks.append("MISSING_MONTHLY_TAX_CONFIG")
                    
                t_prof = db.query(ProductTaxProfile).filter(ProductTaxProfile.mlb_id == ad_id, ProductTaxProfile.is_active == True).first()
                if not t_prof:
                    status = "blocked"
                    if "MISSING_MONTHLY_TAX_CONFIG" not in hard_locks:
                        block_reason = "MISSING_PRODUCT_TAX_PROFILE"
                    hard_locks.append("MISSING_PRODUCT_TAX_PROFILE")
                    
                p_costs = db.query(ProductPurchaseCost).filter(ProductPurchaseCost.mlb_id == ad_id, ProductPurchaseCost.is_active == True).order_by(ProductPurchaseCost.effective_from.desc()).first()
                if not p_costs:
                    status = "blocked"
                    if not block_reason:
                        block_reason = "MISSING_PURCHASE_COST"
                    hard_locks.append("MISSING_PURCHASE_COST")
                
                if t_prof and t_prof.has_st:
                    if t_prof.mva_rate is None or t_prof.origin_icms_rate is None or t_prof.destination_icms_rate is None:
                        status = "blocked"
                        if not block_reason:
                            block_reason = "MISSING_ST_DATA"
                        hard_locks.append("MISSING_ST_DATA")
                        
                    if p_costs and p_costs.nf_value is None:
                        status = "blocked"
                        if not block_reason:
                            block_reason = "MISSING_NF_VALUE"
                        if "MISSING_NF_VALUE" not in hard_locks:
                            hard_locks.append("MISSING_NF_VALUE")
                        
                if t_prof and t_prof.has_ipi:
                    if t_prof.ipi_rate is None:
                        status = "blocked"
                        if not block_reason:
                            block_reason = "MISSING_IPI_DATA"
                        hard_locks.append("MISSING_IPI_DATA")
                        
                    if p_costs and p_costs.nf_value is None:
                        status = "blocked"
                        if not block_reason:
                            block_reason = "MISSING_NF_VALUE"
                        if "MISSING_NF_VALUE" not in hard_locks:
                            hard_locks.append("MISSING_NF_VALUE")

                if hard_locks:
                    return jsonify({
                        "success": False,
                        "mode": "simulation_only",
                        "ad_id": ad_id,
                        "simulated_price": sim_price,
                        "status": status,
                        "block_reason": block_reason,
                        "hard_locks": hard_locks,
                        "is_mocked": False
                    }), 400

                p_cost = {
                    'real_cost': p_costs.real_cost,
                    'valor_nf': p_costs.nf_value or 0.0,
                    'ipi_rate': t_prof.ipi_rate or 0.0,
                    'difal_value': 0.0, 
                    'other_purchase_costs': (p_costs.freight_cost or 0) + (p_costs.packaging_cost or 0) + (p_costs.other_costs or 0),
                    'product_origin': t_prof.product_origin.value if hasattr(t_prof.product_origin, 'value') else t_prof.product_origin
                }
                
                t_profile = {
                    'full_das_rate': m_config.full_das_rate,
                    'das_without_icms_rate': m_config.das_without_icms_rate,
                    'has_st': t_prof.has_st,
                    'has_ipi': t_prof.has_ipi,
                    'has_difal': t_prof.has_difal,
                    'mva_rate': t_prof.mva_rate or 0.0,
                    'origin_icms_rate': t_prof.origin_icms_rate or 0.0,
                    'destination_icms_rate': t_prof.destination_icms_rate or 0.0
                }
                
                m_place = {
                    'fee_rate': ad.commission_percent or 16.0,
                    'fixed_fee': 6.0 if sim_price < 79.0 else 0.0,
                    'freight_cost': ad.shipping_cost or 0.0,
                    'other_variable_costs': 0.0
                }
            finally:
                db.close()
        else:
            p_cost = p_cost or {}
            t_profile = t_profile or {}
            m_place = m_place or {}
            required_tax = ['full_das_rate', 'das_without_icms_rate']
            for f in required_tax:
                if f not in t_profile:
                    missing_fields.append(f)
            
            if 'real_cost' not in p_cost or 'valor_nf' not in p_cost:
                missing_fields.extend(['real_cost', 'valor_nf'])
                
            if missing_fields:
                return jsonify({
                    "success": False,
                    "mode": "simulation_only",
                    "ad_id": ad_id,
                    "simulated_price": sim_price,
                    "status": "blocked",
                    "block_reason": "MISSING_TAX_DATA",
                    "missing_required_fields": missing_fields,
                    "hard_locks": ["MISSING_TAX_DATA"],
                    "warnings": ["Dados fiscais incompletos para simulação segura."],
                    "trace": [],
                    "costs": {},
                    "is_mocked": True
                }), 400

        from app.services.pricing.types import ProductCostInput, TaxProfileInput, MarketplaceInput
        from app.services.pricing.core_calculator import PricingCoreCalculator
        from dataclasses import asdict

        product_cost = ProductCostInput(
            real_cost=float(p_cost.get('real_cost', 0.0)),
            valor_nf=float(p_cost.get('valor_nf', 0.0)),
            ipi_rate=float(p_cost.get('ipi_rate', 0.0)),
            difal_value=float(p_cost.get('difal_value', 0.0)),
            other_purchase_costs=float(p_cost.get('other_purchase_costs', 0.0)),
            product_origin=p_cost.get('product_origin', 'nacional')
        )
        
        tax_profile = TaxProfileInput(
            full_das_rate=float(t_profile.get('full_das_rate', 0.0)),
            das_without_icms_rate=float(t_profile.get('das_without_icms_rate', 0.0)),
            has_st=bool(t_profile.get('has_st', False)),
            has_ipi=bool(t_profile.get('has_ipi', False)),
            has_difal=bool(t_profile.get('has_difal', False)),
            mva_rate=float(t_profile.get('mva_rate', 0.0)),
            origin_icms_rate=float(t_profile.get('origin_icms_rate', 0.0)),
            destination_icms_rate=float(t_profile.get('destination_icms_rate', 0.0))
        )
        
        marketplace = MarketplaceInput(
            selling_price=float(sim_price),
            fee_rate=float(m_place.get('fee_rate', 0.0)),
            fixed_fee=float(m_place.get('fixed_fee', 0.0)),
            freight_cost=float(m_place.get('freight_cost', 0.0)),
            other_variable_costs=float(m_place.get('other_variable_costs', 0.0))
        )
        
        calc = PricingCoreCalculator()
        
        # 1. Calculate Minimum Prices
        min_price_zero = calc.find_minimum_price_zero_profit(product_cost, tax_profile, marketplace)
        min_price_target = calc.find_minimum_price_target_margin(product_cost, tax_profile, marketplace, target_margin_percent) if target_margin_percent > 0 else min_price_zero
        
        # 2. Run simulation for the requested price
        res = calc.calculate(product_cost, tax_profile, marketplace)
        
        # 3. Determine status and locks
        status = "approved"
        block_reason = None
        hard_locks = []
        is_price_allowed = True
        
        if res.profit_amount < 0:
            status = "blocked"
            block_reason = "ZERO_PROFIT_VIOLATION"
            hard_locks.append("NEGATIVE_PROFIT")
            is_price_allowed = False
        elif target_margin_percent > 0 and res.contribution_margin_percent < target_margin_percent:
            status = "blocked"
            block_reason = "TARGET_MARGIN_VIOLATION"
            hard_locks.append("TARGET_MARGIN_VIOLATION")
            is_price_allowed = False
        elif min_price_target == 0.0 and target_margin_percent > 0:
            status = "blocked"
            block_reason = "TARGET_MARGIN_NOT_REACHABLE"
            hard_locks.append("TARGET_MARGIN_NOT_REACHABLE")
            is_price_allowed = False
        elif res.warnings:
            status = "warning"

        response_payload = {
            "success": True,
            "mode": "simulation_only",
            "ad_id": ad_id,
            "simulated_price": res.suggested_selling_price,
            "profit_amount": res.profit_amount,
            "contribution_margin_percent": res.contribution_margin_percent,
            "return_over_cost_percent": res.return_over_cost_percent,
            
            "minimum_price_zero_profit": min_price_zero,
            "minimum_price_target_margin": min_price_target,
            "target_margin_percent": target_margin_percent,
            
            "is_price_allowed": is_price_allowed,
            "status": status,
            "block_reason": block_reason,
            
            "costs": {
                "final_product_cost": res.cost_breakdown.final_product_cost,
                "st_value": res.cost_breakdown.st_value,
                "ipi_value": res.cost_breakdown.ipi_value,
                "difal_value": res.cost_breakdown.difal_value,
                "marketplace_fee_value": res.marketplace_fee_value,
                "fixed_fee": marketplace.fixed_fee,
                "freight_cost": res.freight_cost,
                "sales_tax_value": res.sales_tax_value,
                "other_variable_costs": marketplace.other_variable_costs
            },
            
            "warnings": res.warnings,
            "hard_locks": hard_locks,
            "missing_required_fields": missing_fields,
            "trace": [asdict(t) for t in res.trace],
            "is_mocked": is_mocked
        }
        
        return jsonify(response_payload)
        
    except Exception as e:
        logger.error(f"Error in simulation: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "status": "error",
            "message": str(e)
        }), 500

@api_bp.route('/pricing/resolve/<ad_id>', methods=['GET'])
@require_auth
def resolve_pricing_data(ad_id):
    """Retorna os metadados de auditoria e os inputs calculados pelo PricingDataResolver."""
    from app.core.database import SessionLocal
    from app.services.pricing.resolver import PricingDataResolver

    db = SessionLocal()
    try:
        resolver = PricingDataResolver(db)
        result = resolver.resolve(ad_id)
        if "error" in result:
            return jsonify(result), 404
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error resolving pricing data for {ad_id}: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@api_bp.route('/pricing/simulate-resolved/<ad_id>', methods=['GET'])
@require_auth
def simulate_pricing_from_resolver(ad_id):
    """
    Simulação de precificação usando PricingDataResolver como fonte de custo.
    Usa custo real da NF-e + conciliação financeira quando disponível.
    100% read-only — não altera preço, ML, ou qualquer dado.
    Query param: target_margin (float, default 20.0)
    """
    import math
    from app.core.database import SessionLocal
    from app.services.pricing.resolver import PricingDataResolver
    from app.services.pricing.types import ProductCostInput, TaxProfileInput, MarketplaceInput
    from app.services.pricing.core_calculator import PricingCoreCalculator
    from app.models.ad import Ad
    from app.models.fiscal import ProductTaxProfile, MonthlyTaxConfig
    from dataclasses import asdict

    target_margin = float(request.args.get('target_margin', 20.0))

    db = SessionLocal()
    try:
        resolver = PricingDataResolver(db)
        resolved = resolver.resolve(ad_id)

        if "error" in resolved:
            return jsonify(resolved), 404

        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad or not ad.price or float(ad.price) <= 0:
            return jsonify({"error": "Anúncio sem preço cadastrado"}), 400

        m_config = db.query(MonthlyTaxConfig).filter(
            MonthlyTaxConfig.is_active == True
        ).order_by(MonthlyTaxConfig.reference_month.desc()).first()

        if not m_config:
            return jsonify({"error": "Configuração de imposto mensal não encontrada"}), 400

        t_prof = db.query(ProductTaxProfile).filter(
            ProductTaxProfile.mlb_id == ad_id,
            ProductTaxProfile.is_active == True
        ).first()

        calc_inputs = resolved['calculator_inputs']
        base_cost = float(calc_inputs.get('product_base_cost') or 0)
        nf_val = float(calc_inputs.get('nf_value') or 0) or base_cost
        ipi_rate = float(calc_inputs.get('ipi_rate') or 0)
        extra_costs = float(calc_inputs.get('purchase_extra_costs') or 0)

        product_cost = ProductCostInput(
            real_cost=base_cost,
            valor_nf=nf_val,
            ipi_rate=ipi_rate,
            difal_value=0.0,
            other_purchase_costs=extra_costs,
        )

        has_st = t_prof.has_st if t_prof else False
        tax_profile = TaxProfileInput(
            full_das_rate=float(m_config.full_das_rate),
            das_without_icms_rate=float(m_config.das_without_icms_rate),
            has_st=has_st,
            has_ipi=ipi_rate > 0,
            has_difal=False,
            mva_rate=float(t_prof.mva_rate or 0) if t_prof else 0.0,
            origin_icms_rate=float(t_prof.origin_icms_rate or 0) if t_prof else 0.0,
            destination_icms_rate=float(t_prof.destination_icms_rate or 0) if t_prof else 0.0,
        )

        is_premium = getattr(ad, 'listing_type_id', '') == "gold_pro"
        current_price = float(ad.price)
        commission_rate = 0.165 if is_premium else 0.11

        marketplace = MarketplaceInput(
            selling_price=current_price,
            fee_rate=commission_rate * 100,
            fixed_fee=6.0 if current_price < 79.90 else 0.0,
            freight_cost=float(getattr(ad, 'shipping_cost', 0) or 0),
            other_variable_costs=0.0,
        )

        calc = PricingCoreCalculator()
        result = calc.calculate(product_cost, tax_profile, marketplace)

        min_price_zero = calc.find_minimum_price_zero_profit(product_cost, tax_profile, marketplace)
        min_price_target = (
            calc.find_minimum_price_target_margin(product_cost, tax_profile, marketplace, target_margin)
            if target_margin > 0 else min_price_zero
        )

        def next_price_90(min_p: float) -> float:
            if min_p <= 0:
                return 0.0
            tens = math.floor(min_p / 10)
            candidate = tens * 10 + 9.90
            if candidate < min_p:
                candidate += 10
            return round(candidate, 2)

        recommended_price = next_price_90(min_price_target)

        return jsonify({
            "ad_id": ad_id,
            "mode": "simulation_only",
            "cost_source": resolved['selected_cost_source'],
            "data_sources": resolved['data_sources'],
            "resolver_status": resolved['status'],
            "is_usable_for_automation": resolved['is_usable_for_automation'],
            "resolver_warnings": resolved['warnings'],
            "hard_locks": resolved['hard_locks'],

            "current_price": current_price,
            "current_profit": result.profit_amount,
            "current_margin_percent": result.contribution_margin_percent,

            "minimum_price_zero_profit": min_price_zero,
            "minimum_price_target_margin": min_price_target,
            "target_margin_percent": target_margin,
            "recommended_price": recommended_price,

            "costs": {
                "product_base_cost": base_cost,
                "ipi_value": result.cost_breakdown.ipi_value,
                "st_value": result.cost_breakdown.st_value,
                "purchase_extra_costs": extra_costs,
                "final_product_cost": result.cost_breakdown.final_product_cost,
                "marketplace_commission": result.marketplace_fee_value,
                "shipping_cost": result.freight_cost,
                "sales_tax_value": result.sales_tax_value,
                "total_deductions": round(
                    result.cost_breakdown.final_product_cost
                    + result.marketplace_fee_value
                    + result.freight_cost
                    + result.sales_tax_value, 2
                ),
            },

            "resolver_audit": resolved['audit'],
            "calculation_trace": [asdict(t) for t in result.trace],
        }), 200

    except Exception as e:
        logger.error(f"Error in simulate-resolved for {ad_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
