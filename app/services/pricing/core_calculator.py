from typing import List, Dict, Any
from app.services.pricing.types import (
    ProductCostInput, 
    TaxProfileInput, 
    MarketplaceInput, 
    PricingResult, 
    CostBreakdown, 
    CalculationTrace
)
from app.services.pricing.validator import PricingValidator

def round_money(value: float) -> float:
    """Arredonda valores monetários para 2 casas decimais."""
    return round(value, 2)

class PricingCoreCalculator:
    """
    Motor matemático puro para cálculo de custos e precificação.
    Não possui dependência de banco de dados ou APIs externas.
    """
    
    def __init__(self):
        self.traces: List[CalculationTrace] = []
        
    def _add_trace(self, step: str, formula: str, result: float, details: Dict[str, Any] = None):
        self.traces.append(CalculationTrace(
            step=step,
            formula=formula,
            result=result,
            details=details or {}
        ))

    def calculate(
        self, 
        product_cost: ProductCostInput, 
        tax_profile: TaxProfileInput, 
        marketplace: MarketplaceInput
    ) -> PricingResult:
        
        self.traces = [] # Reset traces for this run
        warnings = PricingValidator.validate_inputs(product_cost, tax_profile, marketplace)
        
        # 1. IPI Calculation
        ipi_value = 0.0
        if tax_profile.has_ipi and product_cost.ipi_rate > 0:
            ipi_value = round_money(product_cost.valor_nf * (product_cost.ipi_rate / 100.0))
            self._add_trace(
                "Cálculo de IPI", 
                "Valor NF * (Alíquota IPI / 100)", 
                ipi_value, 
                {"valor_nf": product_cost.valor_nf, "ipi_rate": product_cost.ipi_rate}
            )

        # 2. ST (Substituição Tributária) Calculation
        st_value = 0.0
        if tax_profile.has_st:
            base_with_ipi = round_money(product_cost.valor_nf + ipi_value)
            st_base = round_money(base_with_ipi * (1 + (tax_profile.mva_rate / 100.0)))
            dest_icms = round_money(st_base * (tax_profile.destination_icms_rate / 100.0))
            own_icms = round_money(product_cost.valor_nf * (tax_profile.origin_icms_rate / 100.0))
            st_value = round_money(max(0.0, dest_icms - own_icms))
            
            self._add_trace(
                "Cálculo de ST (Base + IPI)", 
                "Valor NF + IPI", 
                base_with_ipi
            )
            self._add_trace(
                "Cálculo de ST (Base ST com MVA)", 
                "(Valor NF + IPI) * (1 + MVA)", 
                st_base,
                {"mva_rate": tax_profile.mva_rate}
            )
            self._add_trace(
                "Cálculo de ST (ICMS Destino)", 
                "Base ST * ICMS Destino", 
                dest_icms,
                {"icms_destino": tax_profile.destination_icms_rate}
            )
            self._add_trace(
                "Cálculo de ST (ICMS Próprio)", 
                "Valor NF * ICMS Origem", 
                own_icms,
                {"icms_origem": tax_profile.origin_icms_rate}
            )
            self._add_trace(
                "Cálculo de ST (Valor a Pagar)", 
                "ICMS Destino - ICMS Próprio", 
                st_value
            )

        # 3. DIFAL Calculation
        difal_value = round_money(product_cost.difal_value) if tax_profile.has_difal else 0.0
        if difal_value > 0:
            self._add_trace("DIFAL", "Valor manual preenchido", difal_value)

        # 4. Final Product Cost Calculation
        final_product_cost = round_money(
            product_cost.real_cost + ipi_value + st_value + difal_value + product_cost.other_purchase_costs
        )
        self._add_trace(
            "Custo Final do Produto", 
            "Custo Real + IPI + ST + DIFAL + Outros", 
            final_product_cost
        )

        cost_breakdown = CostBreakdown(
            real_cost=round_money(product_cost.real_cost),
            ipi_value=ipi_value,
            st_value=st_value,
            difal_value=difal_value,
            other_costs=round_money(product_cost.other_purchase_costs),
            final_product_cost=final_product_cost
        )

        # 5. Sales Tax (Simples Nacional / DAS)
        active_das_rate = tax_profile.das_without_icms_rate if tax_profile.has_st else tax_profile.full_das_rate
        sales_tax_value = round_money(marketplace.selling_price * (active_das_rate / 100.0))
        
        self._add_trace(
            "Imposto sobre Venda (DAS)", 
            f"Preço de Venda * {'DAS (sem ICMS)' if tax_profile.has_st else 'DAS (Full)'}", 
            sales_tax_value,
            {"active_rate": active_das_rate, "has_st": tax_profile.has_st}
        )

        # 6. Marketplace Costs
        fee_value = round_money(marketplace.selling_price * (marketplace.fee_rate / 100.0))
        self._add_trace(
            "Comissão Marketplace", 
            "Preço Venda * Taxa Marketplace", 
            fee_value,
            {"fee_rate": marketplace.fee_rate}
        )

        total_marketplace_costs = round_money(fee_value + marketplace.fixed_fee + marketplace.freight_cost)
        self._add_trace(
            "Custo Total Marketplace", 
            "Comissão + Taxa Fixa + Frete", 
            total_marketplace_costs,
            {"fixed_fee": marketplace.fixed_fee, "freight": marketplace.freight_cost}
        )

        # 7. Deduções Totais e Lucro
        total_deductions = round_money(final_product_cost + total_marketplace_costs + sales_tax_value + marketplace.other_variable_costs)
        self._add_trace(
            "Deduções Totais", 
            "Custo Final + Total Marketplace + Imposto Venda + Outros Variáveis", 
            total_deductions,
            {"other_variable_costs": marketplace.other_variable_costs}
        )

        profit = round_money(marketplace.selling_price - total_deductions)
        self._add_trace(
            "Lucro Final", 
            "Preço Venda - Deduções Totais", 
            profit
        )

        # 8. Margins
        contribution_margin_pct = 0.0
        if marketplace.selling_price > 0:
            contribution_margin_pct = round_money((profit / marketplace.selling_price) * 100.0)
            self._add_trace(
                "Margem de Contribuição", 
                "(Lucro / Preço Venda) * 100", 
                contribution_margin_pct
            )
            
        return_over_cost_pct = 0.0
        if total_deductions > 0:
            return_over_cost_pct = round_money((profit / total_deductions) * 100.0)
            self._add_trace(
                "Retorno sobre Custo Total (Markup Equivalente)", 
                "(Lucro / Deduções Totais) * 100", 
                return_over_cost_pct
            )

        # Final Assembly
        result = PricingResult(
            suggested_selling_price=marketplace.selling_price,
            profit_amount=profit,
            contribution_margin_percent=contribution_margin_pct,
            return_over_cost_percent=return_over_cost_pct,
            sales_tax_value=sales_tax_value,
            marketplace_fee_value=fee_value,
            freight_cost=round_money(marketplace.freight_cost),
            cost_breakdown=cost_breakdown,
            trace=self.traces,
            warnings=warnings
        )
        
        # Additional post-calculation validation
        result.warnings.extend(PricingValidator.validate_result(result))
        
        return result
