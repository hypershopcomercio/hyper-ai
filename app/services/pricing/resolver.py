from sqlalchemy.orm import Session
from typing import Dict, Any, Tuple
from datetime import datetime
from app.models.ad import Ad
from app.models.tiny_product import TinyProduct
from app.models.fiscal import ProductPurchaseCost, ProductTaxProfile, MonthlyTaxConfig
from app.models.nfe import NfeItem, NfeImport, NfeReconciliation
import logging

logger = logging.getLogger(__name__)

class PricingDataResolver:
    """
    Resolver que orquestra a descoberta de dados financeiros e fiscais 
    para o motor de precificação.
    """
    
    def __init__(self, db: Session):
        self.db = db

    def resolve(self, ad_id: str) -> Dict[str, Any]:
        ad = self.db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            return self._build_empty_response(error="Ad not found")

        sku = ad.sku
        tiny_prod = self.db.query(TinyProduct).filter(TinyProduct.sku == sku).first() if sku else None
        
        purchase_cost_record = self.db.query(ProductPurchaseCost).filter(
            ProductPurchaseCost.mlb_id == ad_id, 
            ProductPurchaseCost.is_active == True
        ).order_by(ProductPurchaseCost.effective_from.desc()).first()

        tax_profile_record = self.db.query(ProductTaxProfile).filter(
            ProductTaxProfile.mlb_id == ad_id, 
            ProductTaxProfile.is_active == True
        ).first()

        monthly_config = self.db.query(MonthlyTaxConfig).filter(
            MonthlyTaxConfig.is_active == True
        ).order_by(MonthlyTaxConfig.reference_month.desc()).first()

        VALID_NFE_STATUSES = ['imported', 'linked', 'pending_link']

        latest_nfe_item = self.db.query(NfeItem).join(NfeImport).filter(
            NfeItem.linked_sku == sku,
            NfeItem.link_status == 'confirmed',
            NfeImport.status.in_(VALID_NFE_STATUSES)
        ).order_by(NfeImport.issue_date.desc()).first()

        latest_reconciliation = None
        if latest_nfe_item and latest_nfe_item.nfe.reconciliations:
            latest_reconciliation = next((r for r in latest_nfe_item.nfe.reconciliations if r.reconciliation_status == 'confirmed' and r.is_active), None)

        candidate_nfe_item = None
        if not latest_nfe_item:
            candidate_nfe_item = self.db.query(NfeItem).join(NfeImport).filter(
                NfeItem.linked_sku == sku,
                NfeItem.link_status == 'suggested',
                NfeImport.status.in_(VALID_NFE_STATUSES)
            ).order_by(NfeImport.issue_date.desc()).first()

        audit = {}
        inputs = {}
        missing_fields = []
        hard_locks = []
        warnings = []
        data_sources = []

        # Base Cost
        base_cost_val, base_cost_audit = self._resolve_product_base_cost(ad, tiny_prod, purchase_cost_record, latest_nfe_item, latest_reconciliation)
        inputs['product_base_cost'] = base_cost_val
        audit['product_base_cost'] = base_cost_audit
        if base_cost_audit['is_missing']:
            missing_fields.append("product_base_cost")
            hard_locks.append("MISSING_BASE_COST")

        # NF Value
        nf_value_val, nf_value_audit = self._resolve_nf_value(ad, tiny_prod, purchase_cost_record, base_cost_val, latest_nfe_item, latest_reconciliation)
        inputs['nf_value'] = nf_value_val
        audit['nf_value'] = nf_value_audit
        if nf_value_audit['is_missing']:
            missing_fields.append("nf_value")

        # Fiscal Parameters (IPI, ST)
        ipi_rate_val, ipi_val, ipi_audit = self._resolve_ipi_value(nf_value_val, base_cost_val, tax_profile_record, latest_nfe_item, latest_reconciliation)
        inputs['ipi_rate'] = ipi_rate_val
        inputs['ipi_value'] = ipi_val
        audit['ipi_value'] = ipi_audit
        audit['ipi_rate'] = self._build_audit_entry(
            ipi_rate_val,
            ipi_audit.get('source', 'product_tax_profiles'),
            ipi_audit.get('source_type', 'automatic'),
            ipi_audit.get('confidence', 'high'),
            formula=f"Taxa IPI: {ipi_rate_val}%",
            is_missing=False,
            is_usable=True
        )
        if ipi_audit['is_missing']:
            missing_fields.append("ipi_value")

        st_val, st_audit = self._resolve_st_value(nf_value_val, ipi_val, base_cost_val, tax_profile_record, latest_nfe_item, latest_reconciliation)
        inputs['st_value'] = st_val
        audit['st_value'] = st_audit
        if st_audit['is_missing']:
            missing_fields.append("st_value")
            hard_locks.append("MISSING_ST_DATA")

        # Extra Costs
        extra_costs_val, extra_costs_audit = self._resolve_purchase_extra_costs(purchase_cost_record, latest_nfe_item, latest_reconciliation)
        inputs['purchase_extra_costs'] = extra_costs_val
        audit['purchase_extra_costs'] = extra_costs_audit

        # Final Product Cost (Custo Fiscal)
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

        # Marketplace Costs
        mkp_costs_val, mkp_costs_audit = self._resolve_marketplace_costs(ad)
        inputs['marketplace_costs'] = mkp_costs_val
        audit['marketplace_costs'] = mkp_costs_audit

        # Sales Tax (DAS)
        das_rate_val, das_rate_audit = self._resolve_sales_tax_rate(monthly_config, tax_profile_record)
        inputs['sales_tax_rate'] = das_rate_val
        audit['sales_tax_rate'] = das_rate_audit
        if das_rate_audit['is_missing']:
            missing_fields.append("sales_tax_rate")
            hard_locks.append("MISSING_SALES_TAX_CONFIG")
        
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

        # Final Profit
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

        # Cost Candidates & Comparison
        ad_cost_tiny = getattr(ad, 'cost', 0.0)
        override_cost = purchase_cost_record.real_cost if purchase_cost_record and getattr(purchase_cost_record, 'data_source', '') == 'manual' else 0.0
        
        cost_candidates = {
            "tiny_ads_cost": ad_cost_tiny,
            "override_manual_base": override_cost,
            "resolved_final_cost": final_cost,
            "resolved_base_cost": base_cost_val,
        }

        if latest_nfe_item:
            cost_candidates['nfe_confirmed_cost'] = float(latest_nfe_item.unit_value)
            cost_candidates['nfe_confirmed_nfe_number'] = latest_nfe_item.nfe.nfe_number if latest_nfe_item.nfe else None

        if candidate_nfe_item:
            cost_candidates['candidate_nfe_cost'] = float(candidate_nfe_item.unit_value)
        
        comparison = {}
        status = "approved"
        selection_status = "automatic_used"
        
        is_override = any(m['source_type'] == 'override' for m in audit.values())
        if is_override:
            selection_status = "override_used"
        
        if ad_cost_tiny > 0 and final_cost > 0:
            diff = abs(final_cost - ad_cost_tiny)
            diff_percent = (diff / ad_cost_tiny) * 100
            
            comparison['ad_cost_divergence'] = {
                "ad_cost_tiny": ad_cost_tiny,
                "resolved_final_cost": final_cost,
                "diff": diff,
                "diff_percent": diff_percent
            }
            
            if is_override and (diff > 5.0 or diff_percent > 3.0):
                status = "needs_review"
                selection_status = "conflict_detected"
                hard_locks.append("COST_SOURCE_CONFLICT")
                conflict_msg = f"Override manual diverge do custo automático em R$ {diff:.2f}. Revisão obrigatória antes de automação."
                warnings.append(conflict_msg)
                
                # Demote overrides
                for field, meta in audit.items():
                    if meta['source_type'] == 'override':
                        meta['confidence'] = 'low'
                        meta['is_usable_for_automation'] = False
                        if 'warnings' not in meta:
                            meta['warnings'] = []
                        meta['warnings'].append(conflict_msg)

        # Collect data sources and warnings
        for field, meta in audit.items():
            if meta['source'] not in data_sources and meta['source'] != "none":
                data_sources.append(meta['source'])
            if meta.get('warnings'):
                for w in meta['warnings']:
                    if w not in warnings:
                        warnings.append(w)

        # Re-calc confidence summary
        confidence_summary = {
            "high": sum(1 for m in audit.values() if m['confidence'] == 'high'),
            "medium": sum(1 for m in audit.values() if m['confidence'] == 'medium'),
            "low": sum(1 for m in audit.values() if m['confidence'] == 'low')
        }

        is_usable_for_automation = status == "approved" and not hard_locks and confidence_summary['low'] == 0
        
        if latest_nfe_item and not latest_reconciliation:
            is_usable_for_automation = False
            if status == "approved":
                status = "needs_review"
            warnings.append("Falta conciliação financeira confirmada para a NF-e.")

        return {
            "status": status,
            "is_usable_for_automation": is_usable_for_automation,
            "calculator_inputs": inputs,
            "cost_candidates": cost_candidates,
            "selected_cost_source": (
                "product_purchase_costs" if is_override
                else "nfe_items + nfe_reconciliations" if latest_nfe_item
                else "ads/tiny"
            ),
            "selection_status": selection_status,
            "audit": audit,
            "missing_fields": missing_fields,
            "hard_locks": list(set(hard_locks)),
            "data_sources": data_sources,
            "confidence_summary": confidence_summary,
            "comparison": comparison,
            "warnings": warnings
        }

    def _resolve_product_base_cost(self, ad: Ad, tiny_prod: TinyProduct, p_cost: ProductPurchaseCost, latest_nfe_item: Any = None, latest_reconciliation: Any = None) -> Tuple[float, Dict]:
        if p_cost and getattr(p_cost, 'data_source', '') == 'manual' and p_cost.real_cost and p_cost.real_cost > 0:
            reason = getattr(p_cost, 'notes', '') or 'Sem motivo informado'
            is_test = 'teste' in reason.lower() or 'correção' in reason.lower()
            confidence = 'medium' if is_test else 'high'
            
            return p_cost.real_cost, self._build_audit_entry(
                p_cost.real_cost, 
                "product_purchase_costs", 
                "override", 
                confidence,
                formula="Valor exato salvo como Custo Base",
                is_missing=False,
                is_usable=True,
                extra={
                    "is_active": True,
                    "validated_at": getattr(p_cost, 'updated_at', datetime.utcnow()).isoformat(),
                    "reason": reason,
                    "warnings": ["Override manual ativo (teste/temporário)." if is_test else "Override manual ativo. Este dado sobrepõe o ERP e a NF-e."]
                }
            )
            
        if latest_nfe_item and latest_reconciliation:
            multiplier = float(latest_reconciliation.financial_multiplier)
            raw_value = float(latest_nfe_item.unit_value)
            adjusted_value = raw_value * multiplier
            return adjusted_value, self._build_audit_entry(
                adjusted_value,
                "nfe_items + nfe_reconciliations",
                "automatic",
                "high",
                formula=f"Valor Unitário Fiscal ({raw_value}) * Multiplicador Financeiro ({multiplier})",
                is_missing=False,
                is_usable=True,
                extra=self._build_nfe_audit_extra(latest_nfe_item, latest_reconciliation, raw_value, adjusted_value, multiplier)
            )
        
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

        if ad and getattr(ad, 'cost', 0) and getattr(ad, 'cost', 0) > 0:
            return ad.cost, self._build_audit_entry(
                ad.cost,
                "ads",
                "automatic",
                "medium",
                formula="Sincronizado do ERP (ads.cost legacy)",
                is_missing=False,
                is_usable=True
            )

        return 0.0, self._build_audit_entry(0.0, "none", "estimated", "low", formula="Não encontrado em nenhuma base", is_missing=True, is_usable=False)

    def _resolve_nf_value(self, ad: Ad, tiny_prod: TinyProduct, p_cost: ProductPurchaseCost, base_cost: float, latest_nfe_item: Any = None, latest_reconciliation: Any = None) -> Tuple[float, Dict]:
        if p_cost and getattr(p_cost, 'data_source', '') == 'manual' and getattr(p_cost, 'nf_value', 0) and getattr(p_cost, 'nf_value', 0) > 0:
            reason = getattr(p_cost, 'notes', '') or ''
            is_test = 'teste' in reason.lower()
            confidence = 'medium' if is_test else 'high'
            
            return p_cost.nf_value, self._build_audit_entry(
                p_cost.nf_value,
                "product_purchase_costs",
                "override", 
                confidence,
                formula="Valor exato salvo da NF",
                is_missing=False,
                is_usable=True,
                extra={
                    "is_active": True,
                    "validated_at": getattr(p_cost, 'updated_at', datetime.utcnow()).isoformat(),
                    "warnings": ["Override manual ativo para NF."]
                }
            )
            
        if latest_nfe_item and latest_reconciliation:
            multiplier = float(latest_reconciliation.financial_multiplier)
            raw_value = float(latest_nfe_item.unit_value)
            adjusted_value = raw_value * multiplier
            return adjusted_value, self._build_audit_entry(
                adjusted_value,
                "nfe_items + nfe_reconciliations",
                "automatic",
                "high",
                formula=f"Valor Unitário Fiscal NF ({raw_value}) * Multiplicador Financeiro ({multiplier})",
                is_missing=False,
                is_usable=True,
                extra=self._build_nfe_audit_extra(latest_nfe_item, latest_reconciliation, raw_value, adjusted_value, multiplier)
            )
        
        return 0.0, self._build_audit_entry(0.0, "none", "estimated", "low", formula="Valor NF não cadastrado", is_missing=True, is_usable=False)

    def _resolve_ipi_value(self, nf_value: float, base_cost: float, t_prof: ProductTaxProfile, latest_nfe_item: Any = None, latest_reconciliation: Any = None) -> Tuple[float, float, Dict]:
        if latest_nfe_item and latest_reconciliation:
            # IPI is the actual tax paid on the fiscal note value.
            # financial_multiplier applies only to the base cost (meia nota),
            # NOT to IPI — the IPI amount on the NF is what was really paid.
            qty = float(latest_nfe_item.quantity) or 1.0
            ipi_per_unit = float(latest_nfe_item.ipi_value) / qty
            ipi_rate_from_nf = float(latest_nfe_item.ipi_rate) if latest_nfe_item.ipi_rate else 0.0
            multiplier = float(latest_reconciliation.financial_multiplier)
            return ipi_rate_from_nf, ipi_per_unit, self._build_audit_entry(
                ipi_per_unit,
                "nfe_items + nfe_reconciliations",
                "automatic",
                "high",
                formula=f"IPI NF-e ({latest_nfe_item.ipi_value}) / qty({qty}) — taxa {ipi_rate_from_nf}% (imposto real pago)",
                is_missing=False,
                is_usable=True,
                extra=self._build_nfe_audit_extra(latest_nfe_item, latest_reconciliation, ipi_per_unit, ipi_per_unit, multiplier)
            )

        if not t_prof or not getattr(t_prof, 'has_ipi', False):
            return 0.0, 0.0, self._build_audit_entry(0.0, "product_tax_profiles", "automatic", "high", formula="IPI não exigido para este NCM", is_missing=False, is_usable=True)
            
        if getattr(t_prof, 'ipi_rate', None) is not None:
            if nf_value <= 0:
                # Without a known NF value we can't safely compute IPI from the tax profile.
                # The base_cost from Tiny/ads likely already includes IPI+ST — applying
                # the rate on top would double-count. Return 0 and warn.
                return 0.0, 0.0, self._build_audit_entry(
                    0.0, "none", "estimated", "medium",
                    formula="IPI não calculado: Valor NF ausente. Vincule a NF-e para cálculo preciso.",
                    is_missing=False, is_usable=True
                )
            base = nf_value
            rate = t_prof.ipi_rate
            val = base * (rate / 100.0)
            is_override = getattr(t_prof, 'data_source', '') == 'manual'
            return rate, val, self._build_audit_entry(
                val,
                "calculated",
                "override" if is_override else "automatic",
                "medium" if is_override else "high",
                formula=f"Base ({base}) * Alíquota IPI ({rate}%)",
                is_missing=False,
                is_usable=True
            )

        return 0.0, 0.0, self._build_audit_entry(0.0, "none", "estimated", "low", formula="IPI exigido mas alíquota ausente", is_missing=True, is_usable=False)

    def _resolve_st_value(self, nf_value: float, ipi_value: float, base_cost: float, t_prof: ProductTaxProfile, latest_nfe_item: Any = None, latest_reconciliation: Any = None) -> Tuple[float, Dict]:
        if latest_nfe_item and latest_reconciliation:
            qty = float(latest_nfe_item.quantity) or 1.0
            st_per_unit = float(latest_nfe_item.st_value) / qty
            multiplier = float(latest_reconciliation.financial_multiplier)

            if st_per_unit > 0:
                # ST is explicit on the NF — use as-is (no multiplier).
                return st_per_unit, self._build_audit_entry(
                    st_per_unit,
                    "nfe_items + nfe_reconciliations",
                    "automatic",
                    "high",
                    formula=f"ST NF-e ({latest_nfe_item.st_value}) / qty({qty}) — imposto real pago",
                    is_missing=False,
                    is_usable=True,
                    extra=self._build_nfe_audit_extra(latest_nfe_item, latest_reconciliation, st_per_unit, st_per_unit, multiplier)
                )

            # ST = 0 on NF → likely CSOSN 500 (ST pre-collected at origin).
            # Fall back to MVA calculation using the NF unit_value as the base.
            nf_unit_val = float(latest_nfe_item.unit_value)
            if t_prof and getattr(t_prof, 'has_st', False) and nf_unit_val > 0 and \
               getattr(t_prof, 'mva_rate', None) is not None and \
               getattr(t_prof, 'origin_icms_rate', None) is not None and \
               getattr(t_prof, 'destination_icms_rate', None) is not None:
                base_st = (nf_unit_val + ipi_value) * (1 + (t_prof.mva_rate / 100.0))
                st_val = max(0.0, (base_st * (t_prof.destination_icms_rate / 100.0)) - (nf_unit_val * (t_prof.origin_icms_rate / 100.0)))
                return st_val, self._build_audit_entry(
                    st_val,
                    "calculated",
                    "automatic",
                    "medium",
                    formula=f"ST via MVA (NF st=0, CSOSN500): Base [({nf_unit_val}+{ipi_value})×{1+(t_prof.mva_rate/100)}] × {t_prof.destination_icms_rate}% − {nf_unit_val}×{t_prof.origin_icms_rate}%",
                    is_missing=False,
                    is_usable=True
                )

            return 0.0, self._build_audit_entry(
                0.0, "nfe_items", "automatic", "medium",
                formula="ST=0 na NF-e (CSOSN 500 provável) e tax profile insuficiente para recalcular",
                is_missing=False, is_usable=True
            )

        if not t_prof or not getattr(t_prof, 'has_st', False):
            return 0.0, self._build_audit_entry(0.0, "product_tax_profiles", "automatic", "high", formula="ST não exigida para este NCM", is_missing=False, is_usable=True)
            
        if getattr(t_prof, 'mva_rate', None) is not None and getattr(t_prof, 'origin_icms_rate', None) is not None and getattr(t_prof, 'destination_icms_rate', None) is not None:
            if nf_value <= 0:
                # Without a known NF value we can't safely compute ST from the tax profile.
                # The base_cost from Tiny/ads likely already includes ST — applying
                # MVA on top would double-count. Return 0 and warn.
                return 0.0, self._build_audit_entry(
                    0.0, "none", "estimated", "medium",
                    formula="ST não calculado: Valor NF ausente. Vincule a NF-e para cálculo preciso.",
                    is_missing=False, is_usable=True
                )
            base = nf_value
            base_st = (base + ipi_value) * (1 + (t_prof.mva_rate / 100.0))
            st_val = (base_st * (t_prof.destination_icms_rate / 100.0)) - (base * (t_prof.origin_icms_rate / 100.0))
            st_val = max(0, st_val)
            is_override = getattr(t_prof, 'data_source', '') == 'manual'
            
            return st_val, self._build_audit_entry(
                st_val,
                "calculated",
                "override" if is_override else "automatic",
                "medium" if is_override else "high",
                formula=f"Base ST [({base} + {ipi_value}) * {1 + (t_prof.mva_rate / 100.0)}] * ICMS Dest({t_prof.destination_icms_rate}%) - Crédito [{base} * ICMS Orig({t_prof.origin_icms_rate}%)]",
                is_missing=False,
                is_usable=True
            )

        return 0.0, self._build_audit_entry(0.0, "none", "estimated", "low", formula="ST exigida mas parâmetros ausentes (MVA/ICMS)", is_missing=True, is_usable=False)

    def _resolve_purchase_extra_costs(self, p_cost: ProductPurchaseCost, latest_nfe_item: Any = None, latest_reconciliation: Any = None) -> Tuple[float, Dict]:
        if p_cost and getattr(p_cost, 'data_source', '') == 'manual':
            val = (getattr(p_cost, 'freight_cost', 0) or 0) + \
                  (getattr(p_cost, 'packaging_cost', 0) or 0) + \
                  (getattr(p_cost, 'other_costs', 0) or 0)
            return val, self._build_audit_entry(
                val,
                "product_purchase_costs",
                "override",
                "medium",
                formula="Frete + Embalagem + Outros",
                is_missing=False,
                is_usable=True,
                extra={
                    "is_active": True,
                    "warnings": ["Custos extras preenchidos via override manual."]
                }
            )

        if latest_nfe_item and latest_reconciliation:
            multiplier = float(latest_reconciliation.financial_multiplier)
            qty = float(latest_nfe_item.quantity) or 1.0
            raw_value = float((latest_nfe_item.freight_allocated or 0) + (latest_nfe_item.insurance_allocated or 0) + (latest_nfe_item.other_allocated or 0) - (latest_nfe_item.discount_allocated or 0)) / qty
            adjusted_value = raw_value * multiplier
            return adjusted_value, self._build_audit_entry(
                adjusted_value,
                "nfe_items + nfe_reconciliations",
                "automatic",
                "high",
                formula=f"Extra Rateado NF-e ({raw_value}) * Multiplicador Financeiro ({multiplier})",
                is_missing=False,
                is_usable=True,
                extra=self._build_nfe_audit_extra(latest_nfe_item, latest_reconciliation, raw_value, adjusted_value, multiplier)
            )

        return 0.0, self._build_audit_entry(0.0, "none", "estimated", "high", formula="Sem custos extras registrados", is_missing=False, is_usable=True)

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

    def _build_nfe_audit_extra(self, nfe_item: Any, reconciliation: Any, raw_value: float, adjusted_value: float, multiplier: float) -> Dict[str, Any]:
        return {
            "raw_value": raw_value,
            "adjusted_value": adjusted_value,
            "multiplier": multiplier,
            "nfe_id": nfe_item.nfe.id,
            "nfe_number": nfe_item.nfe.nfe_number,
            "issue_date": nfe_item.nfe.issue_date.isoformat() if getattr(nfe_item.nfe, 'issue_date', None) else None,
            "supplier": f"{nfe_item.nfe.issuer_cnpj} / {nfe_item.nfe.issuer_name}",
            "n_item": nfe_item.n_item,
            "linked_sku": nfe_item.linked_sku,
            "link_status": nfe_item.link_status,
            "reconciliation_id": reconciliation.id if reconciliation else None,
        }

    def _build_empty_response(self, error: str) -> Dict[str, Any]:
        return {
            "status": "error",
            "is_usable_for_automation": False,
            "calculator_inputs": {},
            "audit": {},
            "missing_fields": [],
            "hard_locks": ["AD_NOT_FOUND"],
            "data_sources": [],
            "confidence_summary": {},
            "comparison": {},
            "error": error
        }
