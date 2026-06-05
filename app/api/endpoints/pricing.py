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
        
        p_cost = data.get('product_cost', {})
        t_profile = data.get('tax_profile', {})
        m_place = data.get('marketplace', {})
        
        # Hard Lock: Missing required data
        required_tax = ['full_das_rate', 'das_without_icms_rate']
        missing_fields = []
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
                "costs": {}
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
            "trace": [asdict(t) for t in res.trace]
        }
        
        return jsonify(response_payload)
        
    except Exception as e:
        logger.error(f"Error in simulation: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "status": "error",
            "message": str(e)
        }), 500
