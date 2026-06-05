from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ProductCostInput:
    real_cost: float
    valor_nf: float
    ipi_rate: float = 0.0
    difal_value: float = 0.0
    other_purchase_costs: float = 0.0
    product_origin: str = "nacional"

@dataclass
class TaxProfileInput:
    full_das_rate: float
    das_without_icms_rate: float
    has_st: bool = False
    has_ipi: bool = False
    has_difal: bool = False
    mva_rate: float = 0.0
    origin_icms_rate: float = 0.0
    destination_icms_rate: float = 0.0

@dataclass
class MarketplaceInput:
    selling_price: float
    fee_rate: float = 0.0
    fixed_fee: float = 0.0
    freight_cost: float = 0.0
    other_variable_costs: float = 0.0

@dataclass
class CalculationTrace:
    step: str
    formula: str
    result: float
    details: Optional[Dict[str, Any]] = None

@dataclass
class CostBreakdown:
    real_cost: float
    ipi_value: float
    st_value: float
    difal_value: float
    other_costs: float
    final_product_cost: float

@dataclass
class PricingResult:
    profit_amount: float
    contribution_margin_percent: float
    return_over_cost_percent: float
    sales_tax_value: float
    marketplace_fee_value: float
    freight_cost: float
    cost_breakdown: CostBreakdown
    suggested_selling_price: Optional[float] = None
    warnings: List[str] = field(default_factory=list)
    trace: List[CalculationTrace] = field(default_factory=list)
