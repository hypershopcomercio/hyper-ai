from sqlalchemy.orm import Session
from typing import Dict, Any, Tuple
from datetime import datetime
from app.models.ad import Ad
from app.models.tiny_product import TinyProduct
from app.models.fiscal import ProductPurchaseCost, ProductTaxProfile, MonthlyTaxConfig
import logging

logger = logging.getLogger(__name__)

class PricingDataResolver:
    """
    Resolver que orquestra a descoberta de dados financeiros e fiscais 
    para o motor de precificação.
    Retorna calculator_inputs, audit e summaries.
    """
    
    def __init__(self, db: Session):
        self.db = db

    def resolve(self, ad_id: str) -> Dict[str, Any]:
        """
        Resolve all variables required for PricingCoreCalculator.
        """
        ad = self.db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            return self._build_empty_response(error="Ad not found")

        # Base Entities
        sku = ad.sku
        tiny_prod = self.db.query(TinyProduct).filter(TinyProduct.sku == sku).first() if sku else None
        
        # O purchase cost atual do BD
        purchase_cost_record = self.db.query(ProductPurchaseCost).filter(
            ProductPurchaseCost.mlb_id == ad_id, 
            ProductPurchaseCost.is_active == True
        ).order_by(ProductPurchaseCost.effective_from.desc()).first()

        # O tax profile atual do BD
        tax_profile_record = self.db.query(ProductTaxProfile).filter(
            ProductTaxProfile.mlb_id == ad_id, 
            ProductTaxProfile.is_active == True
        ).first()

        # Config mensal de DAS
        monthly_config = self.db.query(MonthlyTaxConfig).filter(
            MonthlyTaxConfig.is_active == True
        ).order_by(MonthlyTaxConfig.reference_month.desc()).first()

        audit = {}
        inputs = {}
        missing_fields = []
        hard_locks = []
        warnings = []
        data_sources = []

        # 1. Product Base Cost
        base_cost_val, base_cost_audit = self._resolve_product_base_cost(ad, tiny_prod, purchase_cost_record)
        inputs['product_base_cost'] = base_cost_val
        audit['product_base_cost'] = base_cost_audit
        if base_cost_audit['is_missing']:
            missing_fields.append("product_base_cost")
            hard_locks.append("MISSING_BASE_COST")

        # 2. NF Value
        nf_value_val, nf_value_audit = self._resolve_nf_value(ad, tiny_prod, purchase_cost_record, base_cost_val)
        inputs['nf_value'] = nf_value_val
        audit['nf_value'] = nf_value_audit
        if nf_value_audit['is_missing']:
            missing_fields.append("nf_value")

        # 3. Fiscal Parameters (IPI, ST)
        ipi_rate_val, ipi_val, ipi_audit = self._resolve_ipi_value(nf_value_val, base_cost_val, tax_profile_record)
        inputs['ipi_rate'] = ipi_rate_val
        inputs['ipi_value'] = ipi_val
        audit['ipi_value'] = ipi_audit
        if ipi_audit['is_missing']:
            missing_fields.append("ipi_value")

        st_val, st_audit = self._resolve_st_value(nf_value_val, ipi_val, base_cost_val, tax_profile_record)
        inputs['st_value'] = st_val
        audit['st_value'] = st_audit
        if st_audit['is_missing']:
            missing_fields.append("st_value")
            hard_locks.append("MISSING_ST_DATA")

        # 4. Extra Costs (Freight, packaging)
        extra_costs_val, extra_costs_audit = self._resolve_purchase_extra_costs(purchase_cost_record)
        inputs['purchase_extra_costs'] = extra_costs_val
        audit['purchase_extra_costs'] = extra_costs_audit

        # 5. Final Product Cost (Custo Fiscal)
        if base_cost_audit['is_missing']:
            final_cost = 0.0
            final_cost_audit = self._build_audit_entry(0.0, "none", "estimated", "low", formula="Missing Base Cost", is_missing=True, is_usable=False)
            missing_fields.append("final_product_cost")
        else:
            final_cost = base_cost_val + ipi_val + st_val + extra_costs_val
            final_cost_audit = self._build_audit_entry(
                final_cost, 
                "calculated", 
                "automatic", 
                "high" if not (ipi_audit['is_missing'] or st_audit['is_missing']) else "medium",
                formula="Base Cost + IPI + ST + Extra Costs",
                is_missing=False,
                is_usable=True
            )
        inputs['final_product_cost'] = final_cost
        audit['final_product_cost'] = final_cost_audit

        # 6. Marketplace Costs
        mkp_costs_val, mkp_costs_audit = self._resolve_marketplace_costs(ad)
        inputs['marketplace_costs'] = mkp_costs_val
        audit['marketplace_costs'] = mkp_costs_audit

        # 7. Sales Tax (DAS)
        das_rate_val, das_rate_audit = self._resolve_sales_tax_rate(monthly_config, tax_profile_record)
        inputs['sales_tax_rate'] = das_rate_val
        audit['sales_tax_rate'] = das_rate_audit
        if das_rate_audit['is_missing']:
            missing_fields.append("sales_tax_rate")
            hard_locks.append("MISSING_SALES_TAX_CONFIG")
        
        # Calculate Sales Tax Value based on Ad Price
        sales_tax_val = 0.0
        if ad.price and ad.price > 0:
            sales_tax_val = ad.price * (das_rate_val / 100.0)
            
        inputs['sales_tax_value'] = sales_tax_val
        audit['sales_tax_value'] = self._build_audit_entry(
            sales_tax_val,
            "calculated",
            "automatic",
            "high",
            formula=f"Preço Venda ({ad.price}) * DAS ({das_rate_val}%)",
            is_missing=False,
            is_usable=True
        )

        # 8. Final Profit
        if ad.price and ad.price > 0 and not base_cost_audit['is_missing']:
            profit = ad.price - mkp_costs_val['total'] - sales_tax_val - final_cost
            inputs['final_profit'] = profit
            audit['final_profit'] = self._build_audit_entry(
                profit,
                "calculated",
                "automatic",
                "high",
                formula="Preço Venda - Marketplace - DAS - Custo Final Produto",
                is_missing=False,
                is_usable=True
            )
        else:
            inputs['final_profit'] = 0.0
            audit['final_profit'] = self._build_audit_entry(0.0, "none", "estimated", "low", formula="Faltam dados base para cálculo do lucro", is_missing=True, is_usable=False)

        # Collect data sources and warnings
        for field, meta in audit.items():
            if meta['source'] not in data_sources and meta['source'] != "none":
                data_sources.append(meta['source'])
            if meta.get('warnings'):
                warnings.extend(meta['warnings'])

        confidence_summary = {
            "high": sum(1 for m in audit.values() if m['confidence'] == 'high'),
            "medium": sum(1 for m in audit.values() if m['confidence'] == 'medium'),
            "low": sum(1 for m in audit.values() if m['confidence'] == 'low')
        }

        # Comparison (if needed)
        comparison = {}
        if getattr(ad, 'cost', 0) > 0 and getattr(ad, 'cost', 0) != final_cost:
            comparison['ad_cost_divergence'] = {
                "ad_cost_legacy": getattr(ad, 'cost', 0),
                "resolved_final_cost": final_cost,
                "diff": final_cost - getattr(ad, 'cost', 0)
            }

        return {
            "calculator_inputs": inputs,
            "audit": audit,
            "missing_fields": missing_fields,
            "hard_locks": list(set(hard_locks)),
            "data_sources": data_sources,
            "confidence_summary": confidence_summary,
            "comparison": comparison,
            "warnings": warnings
        }

    # --- Resolution Methods ---

    def _resolve_product_base_cost(self, ad: Ad, tiny_prod: TinyProduct, p_cost: ProductPurchaseCost) -> Tuple[float, Dict]:
        # Priority 1: Validated Manual Override
        if p_cost and getattr(p_cost, 'data_source', '') == 'manual' and p_cost.real_cost and p_cost.real_cost > 0:
            return p_cost.real_cost, self._build_audit_entry(
                p_cost.real_cost, 
                "product_purchase_costs", 
                "override", 
                "high",
                formula="Valor exato salvo como Custo Base",
                is_missing=False,
                is_usable=True,
                extra={
                    "is_active": True,
                    "validated_at": getattr(p_cost, 'updated_at', datetime.utcnow()).isoformat(),
                    "reason": getattr(p_cost, 'notes', 'Override manual de teste/correção'),
                    "warnings": ["Override manual ativo. Este dado sobrepõe as automações do ERP."]
                }
            )
        
        # Priority 2: NF/XML (Not implemented yet, placeholder for future table)
        
        # Priority 3: Tiny Last Purchase (Placeholder)

        # Priority 4: Internal Avg Cost (Placeholder)

        # Priority 5: Tiny Product Cost
        if tiny_prod and getattr(tiny_prod, 'cost', 0) and getattr(tiny_prod, 'cost', 0) > 0:
            return tiny_prod.cost, self._build_audit_entry(
                tiny_prod.cost,
                "tiny_products",
                "automatic",
                "high",
                formula="Sincronizado do ERP (preco_custo)",
                is_missing=False,
                is_usable=True
            )

        # Priority 6: Estimation/Legacy
        if ad and getattr(ad, 'cost', 0) and getattr(ad, 'cost', 0) > 0:
            return ad.cost, self._build_audit_entry(
                ad.cost,
                "ads",
                "estimated",
                "medium",
                formula="Sincronizado do ERP (ads.cost legacy)",
                is_missing=False,
                is_usable=True
            )

        return 0.0, self._build_audit_entry(0.0, "none", "estimated", "low", formula="Não encontrado em nenhuma base", is_missing=True, is_usable=False)

    def _resolve_nf_value(self, ad: Ad, tiny_prod: TinyProduct, p_cost: ProductPurchaseCost, base_cost: float) -> Tuple[float, Dict]:
        if p_cost and getattr(p_cost, 'data_source', '') == 'manual' and getattr(p_cost, 'nf_value', 0) and getattr(p_cost, 'nf_value', 0) > 0:
            return p_cost.nf_value, self._build_audit_entry(
                p_cost.nf_value,
                "product_purchase_costs",
                "override", 
                "high",
                formula="Valor exato salvo da NF",
                is_missing=False,
                is_usable=True,
                extra={
                    "is_active": True,
                    "validated_at": getattr(p_cost, 'updated_at', datetime.utcnow()).isoformat(),
                    "warnings": ["Override manual ativo para NF."]
                }
            )
        
        return 0.0, self._build_audit_entry(0.0, "none", "estimated", "low", formula="Valor NF não cadastrado", is_missing=True, is_usable=False)

    def _resolve_ipi_value(self, nf_value: float, base_cost: float, t_prof: ProductTaxProfile) -> Tuple[float, float, Dict]:
        if not t_prof or not getattr(t_prof, 'has_ipi', False):
            return 0.0, 0.0, self._build_audit_entry(0.0, "product_tax_profiles", "automatic", "high", formula="IPI não exigido para este NCM", is_missing=False, is_usable=True)
            
        if getattr(t_prof, 'ipi_rate', None) is not None:
            base = nf_value if nf_value > 0 else base_cost
            rate = t_prof.ipi_rate
            val = base * (rate / 100.0)
            return rate, val, self._build_audit_entry(
                val,
                "calculated",
                "override" if getattr(t_prof, 'data_source', '') == 'manual' else "automatic",
                "high",
                formula=f"Base ({base}) * Alíquota IPI ({rate}%)",
                is_missing=False,
                is_usable=True
            )

        return 0.0, 0.0, self._build_audit_entry(0.0, "none", "estimated", "low", formula="IPI exigido mas alíquota ausente", is_missing=True, is_usable=False)

    def _resolve_st_value(self, nf_value: float, ipi_value: float, base_cost: float, t_prof: ProductTaxProfile) -> Tuple[float, Dict]:
        if not t_prof or not getattr(t_prof, 'has_st', False):
            return 0.0, self._build_audit_entry(0.0, "product_tax_profiles", "automatic", "high", formula="ST não exigida para este NCM", is_missing=False, is_usable=True)
            
        if getattr(t_prof, 'mva_rate', None) is not None and getattr(t_prof, 'origin_icms_rate', None) is not None and getattr(t_prof, 'destination_icms_rate', None) is not None:
            base = nf_value if nf_value > 0 else base_cost
            base_st = (base + ipi_value) * (1 + (t_prof.mva_rate / 100.0))
            st_val = (base_st * (t_prof.destination_icms_rate / 100.0)) - (base * (t_prof.origin_icms_rate / 100.0))
            st_val = max(0, st_val)

            return st_val, self._build_audit_entry(
                st_val,
                "calculated",
                "override" if getattr(t_prof, 'data_source', '') == 'manual' else "automatic",
                "high",
                formula=f"Base ST [({base} + {ipi_value}) * {1 + (t_prof.mva_rate / 100.0)}] * ICMS Dest({t_prof.destination_icms_rate}%) - Crédito [{base} * ICMS Orig({t_prof.origin_icms_rate}%)]",
                is_missing=False,
                is_usable=True
            )

        return 0.0, self._build_audit_entry(0.0, "none", "estimated", "low", formula="ST exigida mas parâmetros ausentes (MVA/ICMS)", is_missing=True, is_usable=False)

    def _resolve_purchase_extra_costs(self, p_cost: ProductPurchaseCost) -> Tuple[float, Dict]:
        if p_cost and getattr(p_cost, 'data_source', '') == 'manual':
            val = (getattr(p_cost, 'freight_cost', 0) or 0) + \
                  (getattr(p_cost, 'packaging_cost', 0) or 0) + \
                  (getattr(p_cost, 'other_costs', 0) or 0)
            return val, self._build_audit_entry(
                val,
                "product_purchase_costs",
                "override",
                "high",
                formula="Frete + Embalagem + Outros",
                is_missing=False,
                is_usable=True,
                extra={
                    "is_active": True,
                    "warnings": ["Custos extras preenchidos via override manual."]
                }
            )
        return 0.0, self._build_audit_entry(0.0, "none", "estimated", "medium", formula="Sem custos extras registrados", is_missing=False, is_usable=True)

    def _resolve_marketplace_costs(self, ad: Ad) -> Tuple[Dict[str, float], Dict]:
        commission_rate = 0.16 if getattr(ad, 'listing_type_id', '') == "gold_pro" else 0.11
        commission_val = (getattr(ad, 'price', 0) or 0) * commission_rate
        shipping_val = getattr(ad, 'shipping_cost', 0) or 0
        
        mkp_costs = {
            "commission_rate": commission_rate,
            "commission_value": commission_val,
            "shipping_cost": shipping_val,
            "total": commission_val + shipping_val
        }
        
        return mkp_costs, self._build_audit_entry(
            mkp_costs['total'],
            "ads",
            "automatic",
            "high",
            formula=f"Comissão ({commission_rate*100}%) + Frete ML ({shipping_val})",
            is_missing=False,
            is_usable=True
        )

    def _resolve_sales_tax_rate(self, m_config: MonthlyTaxConfig, t_prof: ProductTaxProfile) -> Tuple[float, Dict]:
        if not m_config:
            return 0.0, self._build_audit_entry(0.0, "none", "estimated", "low", formula="Configuração de imposto mensal não encontrada", is_missing=True, is_usable=False)
            
        rate = getattr(m_config, 'full_das_rate', 0.0)
        if t_prof and getattr(t_prof, 'has_st', False):
            rate = getattr(m_config, 'das_without_icms_rate', 0.0)
            
        return rate, self._build_audit_entry(
            rate,
            "monthly_tax_configs",
            "automatic",
            "high",
            formula=f"Alíquota DAS {'sem ICMS (ST paga na origem)' if t_prof and getattr(t_prof, 'has_st', False) else 'Cheia'}",
            is_missing=False,
            is_usable=True
        )

    def _build_audit_entry(self, value: Any, source: str, source_type: str, confidence: str, formula: str, is_missing: bool, is_usable: bool, extra: Dict = None) -> Dict[str, Any]:
        entry = {
            "value": value,
            "source": source,
            "source_type": source_type,
            "confidence": confidence,
            "formula": formula,
            "updated_at": datetime.utcnow().isoformat(),
            "warnings": [],
            "is_missing": is_missing,
            "is_usable_for_automation": is_usable
        }
        if extra:
            entry.update(extra)
        return entry

    def _build_empty_response(self, error: str) -> Dict[str, Any]:
        return {
            "calculator_inputs": {},
            "audit": {},
            "missing_fields": [],
            "hard_locks": ["AD_NOT_FOUND"],
            "data_sources": [],
            "confidence_summary": {},
            "comparison": {},
            "error": error
        }
