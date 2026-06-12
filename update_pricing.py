import re
import sys

file_path = 'app/api/endpoints/pricing.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = """        p_cost = data.get('product_cost')
        t_profile = data.get('tax_profile')
        m_place = data.get('marketplace')
        
        is_mocked = True
        missing_fields = []
        hard_locks = []
        status = "approved"
        block_reason = None
        
        if not p_cost or not t_profile:
            is_mocked = False
            # Lookup real data
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
                
                # Validation of required fields
                if t_prof and t_prof.has_st:
                    if t_prof.mva_rate is None or t_prof.origin_icms_rate is None or t_prof.destination_icms_rate is None or (p_costs and p_costs.nf_value is None):
                        status = "blocked"
                        if not block_reason:
                            block_reason = "MISSING_ST_DATA"
                        hard_locks.append("MISSING_ST_DATA")
                        
                if t_prof and t_prof.has_ipi:
                    if t_prof.ipi_rate is None or (p_costs and p_costs.nf_value is None):
                        status = "blocked"
                        if not block_reason:
                            block_reason = "MISSING_IPI_DATA"
                        hard_locks.append("MISSING_IPI_DATA")

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

                # Data mapping to internal dicts if approved
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
                
        # ... Rest of the simulation code"""

# Now we need to replace the original block
original_block = """        p_cost = data.get('product_cost', {})
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
            }), 400"""

if original_block in content:
    content = content.replace(original_block, replacement)
    
    # Also add is_mocked to the success response payload
    if '"is_mocked": is_mocked' not in content:
        content = content.replace(
            '"trace": [asdict(t) for t in res.trace]',
            '"trace": [asdict(t) for t in res.trace],\n            "is_mocked": is_mocked'
        )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Backend endpoint modified.")
else:
    print("Could not find the original block to replace.")
