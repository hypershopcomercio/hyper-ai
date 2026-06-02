from app.services.pricing.types import ProductCostInput, TaxProfileInput, MarketplaceInput
from app.services.pricing.core_calculator import PricingCoreCalculator

def test_electric_pressure_cooker_base_case():
    """Panela de Pressão Elétrica Nacional, meia nota, com ST e MVA."""
    calculator = PricingCoreCalculator()
    
    product_input = ProductCostInput(real_cost=189.38, valor_nf=94.69, ipi_rate=7.8, product_origin='nacional')
    tax_input = TaxProfileInput(has_st=True, has_ipi=True, mva_rate=72.10, origin_icms_rate=12.0, destination_icms_rate=18.0, full_das_rate=6.68, das_without_icms_rate=4.83)
    marketplace_input = MarketplaceInput(selling_price=399.90, fee_rate=10.0, freight_cost=44.05)
    
    result = calculator.calculate(product_input, tax_input, marketplace_input)
    
    assert result.cost_breakdown.ipi_value == 7.39
    assert result.cost_breakdown.st_value == 20.26
    assert result.cost_breakdown.final_product_cost == 217.03
    assert result.sales_tax_value == 19.32
    assert result.marketplace_fee_value == 39.99
    assert abs(result.profit_amount - 79.51) <= 0.02 
    assert abs(result.contribution_margin_percent - 19.88) <= 0.01
    assert len(result.warnings) == 0

def test_no_st_with_full_das():
    """Produto sem ST usando DAS cheio."""
    calculator = PricingCoreCalculator()
    product_input = ProductCostInput(real_cost=100.0, valor_nf=100.0)
    tax_input = TaxProfileInput(has_st=False, full_das_rate=10.0, das_without_icms_rate=5.0)
    marketplace_input = MarketplaceInput(selling_price=200.0)
    
    result = calculator.calculate(product_input, tax_input, marketplace_input)
    assert result.cost_breakdown.st_value == 0.0
    assert result.sales_tax_value == 20.0 # 10% de 200

def test_st_with_das_without_icms():
    """Produto com ST usando DAS sem ICMS."""
    calculator = PricingCoreCalculator()
    product_input = ProductCostInput(real_cost=100.0, valor_nf=100.0)
    tax_input = TaxProfileInput(has_st=True, mva_rate=50.0, origin_icms_rate=12.0, destination_icms_rate=18.0, full_das_rate=10.0, das_without_icms_rate=5.0)
    marketplace_input = MarketplaceInput(selling_price=200.0)
    
    result = calculator.calculate(product_input, tax_input, marketplace_input)
    assert result.cost_breakdown.st_value > 0
    assert result.sales_tax_value == 10.0 # 5% de 200

def test_difal():
    """Produto com DIFAL manual."""
    calculator = PricingCoreCalculator()
    product_input = ProductCostInput(real_cost=100.0, valor_nf=100.0, difal_value=15.50)
    tax_input = TaxProfileInput(has_difal=True, full_das_rate=10.0, das_without_icms_rate=5.0)
    marketplace_input = MarketplaceInput(selling_price=200.0)
    
    result = calculator.calculate(product_input, tax_input, marketplace_input)
    assert result.cost_breakdown.difal_value == 15.50
    assert result.cost_breakdown.final_product_cost == 115.50

def test_negative_margin():
    """Margem negativa gera alerta de prejuízo."""
    calculator = PricingCoreCalculator()
    product_input = ProductCostInput(real_cost=200.0, valor_nf=200.0)
    tax_input = TaxProfileInput(full_das_rate=10.0, das_without_icms_rate=5.0)
    marketplace_input = MarketplaceInput(selling_price=100.0) # Vende mais barato que custa
    
    result = calculator.calculate(product_input, tax_input, marketplace_input)
    assert result.profit_amount < 0
    assert result.contribution_margin_percent < 0
    assert any("PREJUÍZO" in w for w in result.warnings)

def test_zero_mva_with_st_active():
    """MVA zerada com ST ativa deve gerar alerta."""
    calculator = PricingCoreCalculator()
    product_input = ProductCostInput(real_cost=100.0, valor_nf=100.0)
    tax_input = TaxProfileInput(has_st=True, mva_rate=0.0, origin_icms_rate=12.0, destination_icms_rate=18.0, full_das_rate=10.0, das_without_icms_rate=5.0)
    marketplace_input = MarketplaceInput(selling_price=200.0)
    
    result = calculator.calculate(product_input, tax_input, marketplace_input)
    assert any("MVA está zerada" in w for w in result.warnings)

def test_national_with_4_percent():
    """Produto nacional com ICMS 4%."""
    calculator = PricingCoreCalculator()
    product_input = ProductCostInput(real_cost=100.0, valor_nf=100.0, product_origin="nacional")
    tax_input = TaxProfileInput(origin_icms_rate=4.0, full_das_rate=10.0, das_without_icms_rate=5.0)
    marketplace_input = MarketplaceInput(selling_price=200.0)
    
    result = calculator.calculate(product_input, tax_input, marketplace_input)
    assert any("marcado como 'nacional', mas a alíquota de ICMS interestadual está configurada para 4%" in w for w in result.warnings)

def test_imported_with_12_percent():
    """Produto importado com ICMS 12%."""
    calculator = PricingCoreCalculator()
    product_input = ProductCostInput(real_cost=100.0, valor_nf=100.0, product_origin="importado")
    tax_input = TaxProfileInput(origin_icms_rate=12.0, full_das_rate=10.0, das_without_icms_rate=5.0)
    marketplace_input = MarketplaceInput(selling_price=200.0)
    
    result = calculator.calculate(product_input, tax_input, marketplace_input)
    assert any("marcado como 'importado', mas a alíquota de ICMS interestadual está 12.0%" in w for w in result.warnings)

def test_fixed_fee_and_variable_costs():
    """Testa taxa fixa e custos variáveis no Marketplace."""
    calculator = PricingCoreCalculator()
    product_input = ProductCostInput(real_cost=100.0, valor_nf=100.0)
    tax_input = TaxProfileInput(full_das_rate=10.0, das_without_icms_rate=5.0)
    marketplace_input = MarketplaceInput(selling_price=200.0, fee_rate=10.0, fixed_fee=6.00, freight_cost=15.00, other_variable_costs=4.00)
    
    result = calculator.calculate(product_input, tax_input, marketplace_input)
    
    assert result.marketplace_fee_value == 20.0
    assert result.freight_cost == 15.0
    
    # Total Marketplace Costs = 20.0 (fee) + 6.00 (fixed) + 15.00 (freight) = 41.0
    # Sales Tax = 20.0
    # Other Variable = 4.0
    # Total Deductions = 100.0 (Product) + 41.0 + 20.0 + 4.0 = 165.0
    # Profit = 200.0 - 165.0 = 35.0
    assert result.profit_amount == 35.0

def test_negative_validations():
    """Testa validações duras como custo negativo, preço zero e taxa acima de 100%."""
    calculator = PricingCoreCalculator()
    product_input = ProductCostInput(real_cost=-10.0, valor_nf=-5.0)
    tax_input = TaxProfileInput(full_das_rate=110.0, das_without_icms_rate=-5.0, origin_icms_rate=150.0)
    marketplace_input = MarketplaceInput(selling_price=0.0, fee_rate=120.0)
    
    result = calculator.calculate(product_input, tax_input, marketplace_input)
    
    warnings = result.warnings
    assert any("preço de venda deve ser maior que zero" in w for w in warnings)
    assert any("custo real não pode ser negativo" in w for w in warnings)
    assert any("valor da nota fiscal (NF) não pode ser negativo" in w for w in warnings)
    assert any("exceder 100%" in w and "DAS (Cheio)" in w for w in warnings)
    assert any("não pode ser negativa" in w and "DAS (Sem ICMS)" in w for w in warnings)
    assert any("exceder 100%" in w and "Comissão Marketplace" in w for w in warnings)

if __name__ == "__main__":
    test_electric_pressure_cooker_base_case()
    test_no_st_with_full_das()
    test_st_with_das_without_icms()
    test_difal()
    test_negative_margin()
    test_zero_mva_with_st_active()
    test_national_with_4_percent()
    test_imported_with_12_percent()
    test_fixed_fee_and_variable_costs()
    test_negative_validations()
    print("All tests passed successfully!")
