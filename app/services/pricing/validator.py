from typing import List
from app.services.pricing.types import ProductCostInput, TaxProfileInput, MarketplaceInput, PricingResult

class PricingValidator:
    @staticmethod
    def validate_inputs(product_cost: ProductCostInput, tax_profile: TaxProfileInput, marketplace: MarketplaceInput) -> List[str]:
        warnings = []
        
        # Numeric range validations
        if marketplace.selling_price <= 0:
            warnings.append("ERRO: O preço de venda deve ser maior que zero.")
            
        if product_cost.real_cost < 0:
            warnings.append("ERRO: O custo real não pode ser negativo.")
            
        if product_cost.valor_nf < 0:
            warnings.append("ERRO: O valor da nota fiscal (NF) não pode ser negativo.")
            
        if tax_profile.mva_rate < 0:
            warnings.append("ERRO: A MVA (Margem de Valor Agregado) não pode ser negativa.")
            
        # Rate validations (0 to 100)
        rates_to_check = {
            "Alíquota IPI": product_cost.ipi_rate,
            "ICMS Origem": tax_profile.origin_icms_rate,
            "ICMS Destino": tax_profile.destination_icms_rate,
            "DAS (Cheio)": tax_profile.full_das_rate,
            "DAS (Sem ICMS)": tax_profile.das_without_icms_rate,
            "Comissão Marketplace": marketplace.fee_rate
        }
        
        for name, rate in rates_to_check.items():
            if rate < 0:
                warnings.append(f"ERRO: A alíquota/taxa de '{name}' não pode ser negativa ({rate}%).")
            elif rate > 100:
                warnings.append(f"ERRO: A alíquota/taxa de '{name}' não pode exceder 100% ({rate}%).")

        # Origin vs ICMS checks
        origin = product_cost.product_origin.lower()
        icms_origin = tax_profile.origin_icms_rate
        
        if origin == 'nacional' and icms_origin == 4.0:
            warnings.append("ALERTA FISCAL: O produto está marcado como 'nacional', mas a alíquota de ICMS interestadual está configurada para 4% (comum para importados). Verifique se a origem ou a alíquota estão corretas.")
            
        if origin == 'importado' and icms_origin in [12.0, 7.0]:
            warnings.append(f"ALERTA FISCAL: O produto está marcado como 'importado', mas a alíquota de ICMS interestadual está {icms_origin}%. Geralmente, importados utilizam 4%.")
            
        # ST Checks
        if tax_profile.has_st and tax_profile.mva_rate <= 0:
            warnings.append("ALERTA FISCAL: O produto possui ST ativa, mas a MVA está zerada ou ausente.")
            
        # Cost checks
        if 0 <= product_cost.real_cost < product_cost.valor_nf:
            warnings.append("ALERTA DE CUSTO: O Custo Real informado é menor que o Valor da NF. Geralmente o Valor NF é igual ou inferior (meia nota) ao custo real. Confirme os valores.")
            
        return warnings

    @staticmethod
    def validate_result(result: PricingResult) -> List[str]:
        warnings = []
        
        if result.contribution_margin_percent < 0:
            warnings.append("ALERTA DE PREJUÍZO: A margem de contribuição projetada é negativa. Esta venda resultará em perda de dinheiro.")
            
        elif result.contribution_margin_percent < 5.0:
            warnings.append("ALERTA DE MARGEM BAIXA: A margem de contribuição projetada está abaixo de 5%. Risco elevado.")
            
        if result.profit_amount < 0:
            warnings.append("ALERTA DE PREJUÍZO: O lucro projetado em Reais (R$) é negativo.")
            
        return warnings
