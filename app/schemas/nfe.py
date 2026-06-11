from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum

class NfeStatusEnum(str, Enum):
    imported = "imported"
    pending_link = "pending_link"
    linked = "linked"
    conflict = "conflict"
    ignored = "ignored"

class LinkStatusEnum(str, Enum):
    pending = "pending"
    suggested = "suggested"
    confirmed = "confirmed"

class LinkConfidenceEnum(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"

class ParseStatusEnum(str, Enum):
    success = "success"
    error = "error"

class TaxDetail(BaseModel):
    value: Decimal = Decimal('0.0')
    rate: Decimal = Decimal('0.0')
    base: Optional[Decimal] = Decimal('0.0')

class AllocationDetail(BaseModel):
    freight: Decimal = Decimal('0.0')
    insurance: Decimal = Decimal('0.0')
    discount: Decimal = Decimal('0.0')
    other: Decimal = Decimal('0.0')
    formula: Optional[str] = None

class NfeItemSchema(BaseModel):
    id: Optional[int] = None
    n_item: int
    sku_supplier: Optional[str] = None
    description: str
    ean: Optional[str] = None
    ncm: Optional[str] = None
    cest: Optional[str] = None
    cfop: Optional[str] = None
    cst_csosn: Optional[str] = None
    
    unit: Optional[str] = None
    quantity: Decimal
    unit_value: Decimal
    product_value: Decimal
    
    unit_trib: Optional[str] = None
    quantity_trib: Optional[Decimal] = None
    unit_value_trib: Optional[Decimal] = None
    
    allocations: AllocationDetail = Field(default_factory=AllocationDetail)
    
    taxes: Dict[str, TaxDetail] = Field(default_factory=dict)
    
    calculated_costs: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Links
    linked_sku: Optional[str] = None
    linked_mlb_id: Optional[str] = None
    link_status: LinkStatusEnum = LinkStatusEnum.pending
    link_confidence: Optional[LinkConfidenceEnum] = None
    link_method: Optional[str] = None

    class Config:
        from_attributes = True

class NfeIssuer(BaseModel):
    cnpj: str
    name: str

class NfeTotals(BaseModel):
    products_value: Decimal = Decimal('0.0')
    invoice_value: Decimal = Decimal('0.0')
    freight: Decimal = Decimal('0.0')
    insurance: Decimal = Decimal('0.0')
    discount: Decimal = Decimal('0.0')
    other: Decimal = Decimal('0.0')

class NfeMetadata(BaseModel):
    nfe_number: Optional[str] = None
    series: Optional[str] = None
    model: Optional[str] = None
    operation_nature: Optional[str] = None
    environment: Optional[str] = None
    protocol_number: Optional[str] = None
    xml_sha256: Optional[str] = None

class NfeImportSchema(BaseModel):
    id: Optional[int] = None
    access_key: str
    status: NfeStatusEnum = NfeStatusEnum.imported
    issue_date: datetime
    
    issuer: NfeIssuer
    totals: NfeTotals
    metadata: NfeMetadata = Field(default_factory=NfeMetadata)
    
    parse_status: ParseStatusEnum = ParseStatusEnum.success
    parse_error: Optional[str] = None
    
    items: List[NfeItemSchema] = []

    class Config:
        from_attributes = True
