from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, DateTime, Date, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class NfeImport(Base):
    __tablename__ = "nfe_imports"

    id = Column(Integer, primary_key=True, index=True)
    access_key = Column(String(44), unique=True, nullable=False, index=True)
    status = Column(Enum('imported', 'pending_link', 'linked', 'conflict', 'ignored', name='nfe_status_enum'), default='imported')
    
    nfe_number = Column(String(20), nullable=True)
    series = Column(String(10), nullable=True)
    model = Column(String(5), nullable=True)
    operation_nature = Column(String(255), nullable=True)
    environment = Column(String(20), nullable=True)
    protocol_number = Column(String(50), nullable=True)
    
    issue_date = Column(DateTime, nullable=False, index=True)
    issuer_cnpj = Column(String(14), nullable=False, index=True)
    issuer_name = Column(String(200), nullable=False)
    recipient_cnpj = Column(String(14), nullable=True)
    
    total_products_value = Column(DECIMAL(15, 4), default=0)
    total_invoice_value = Column(DECIMAL(15, 4), default=0)
    total_freight = Column(DECIMAL(15, 4), default=0)
    total_insurance = Column(DECIMAL(15, 4), default=0)
    total_discount = Column(DECIMAL(15, 4), default=0)
    total_other = Column(DECIMAL(15, 4), default=0)
    
    raw_xml = Column(Text, nullable=True)
    xml_sha256 = Column(String(64), unique=True, nullable=True)
    
    parse_status = Column(Enum('success', 'error', name='nfe_parse_status_enum'), default='success')
    parse_error = Column(Text, nullable=True)
    imported_by = Column(String(100), nullable=True)
    import_source = Column(String(50), default='manual_upload')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = relationship("NfeItem", back_populates="nfe")

class NfeItem(Base):
    __tablename__ = "nfe_items"

    id = Column(Integer, primary_key=True, index=True)
    nfe_id = Column(Integer, ForeignKey("nfe_imports.id"), nullable=False, index=True)
    n_item = Column(Integer, nullable=False)
    
    sku_supplier = Column(String(100), nullable=True, index=True) # cProd
    description = Column(String(255), nullable=False) # xProd
    ean = Column(String(30), nullable=True, index=True) # ean pode ser SEM GTIN
    ncm = Column(String(10), nullable=True)
    cest = Column(String(10), nullable=True)
    cfop = Column(String(4), nullable=True)
    cst_csosn = Column(String(4), nullable=True)
    
    unit = Column(String(10), nullable=True)
    quantity = Column(DECIMAL(15, 4), nullable=False)
    unit_value = Column(DECIMAL(15, 4), nullable=False)
    product_value = Column(DECIMAL(15, 4), nullable=False)
    
    unit_trib = Column(String(10), nullable=True)
    quantity_trib = Column(DECIMAL(15, 4), nullable=True)
    unit_value_trib = Column(DECIMAL(15, 4), nullable=True)
    
    freight_allocated = Column(DECIMAL(15, 4), default=0)
    insurance_allocated = Column(DECIMAL(15, 4), default=0)
    discount_allocated = Column(DECIMAL(15, 4), default=0)
    other_allocated = Column(DECIMAL(15, 4), default=0)
    
    ipi_value = Column(DECIMAL(15, 4), default=0)
    ipi_rate = Column(DECIMAL(10, 4), default=0)
    icms_value = Column(DECIMAL(15, 4), default=0)
    icms_rate = Column(DECIMAL(10, 4), default=0)
    icms_base = Column(DECIMAL(15, 4), default=0)
    st_value = Column(DECIMAL(15, 4), default=0)
    st_rate = Column(DECIMAL(10, 4), default=0)
    st_base = Column(DECIMAL(15, 4), default=0)
    
    total_item_cost_nf = Column(DECIMAL(15, 4), default=0)
    unit_cost_nf = Column(DECIMAL(15, 4), default=0)
    
    linked_sku = Column(String(100), nullable=True, index=True)
    linked_mlb_id = Column(String(255), nullable=True, index=True)
    link_status = Column(Enum('pending', 'suggested', 'confirmed', name='nfe_item_link_status_enum'), default='pending', index=True)
    link_confidence = Column(Enum('high', 'medium', 'low', name='nfe_link_confidence_enum'), nullable=True)
    link_method = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    nfe = relationship("NfeImport", back_populates="items")

class NfeReconciliation(Base):
    __tablename__ = "nfe_reconciliations"

    id = Column(Integer, primary_key=True, index=True)
    nfe_id = Column(Integer, ForeignKey("nfe_imports.id", ondelete="CASCADE"), nullable=False, index=True)
    supplier_cnpj = Column(String(14), nullable=False, index=True)
    
    is_active = Column(Boolean, default=True)
    
    fiscal_value_xml = Column(DECIMAL(15, 4), nullable=False)
    financial_value_real = Column(DECIMAL(15, 4), nullable=False)
    
    coverage_percent = Column(DECIMAL(10, 4), nullable=False)
    financial_multiplier = Column(DECIMAL(10, 4), nullable=False)
    
    reconciliation_status = Column(Enum('suggested', 'confirmed', 'conflict', 'ignored', name='reconciliation_status_enum'), nullable=False)
    source_type = Column(Enum('user_input', 'imported_erp', 'bank_match', 'supplier_agreement', name='reconciliation_source_enum'), nullable=False)
    
    evidence_reference = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    
    created_by = Column(String(100), nullable=True)
    confirmed_by = Column(String(100), nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    
    payment_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    
    financial_document_id = Column(String(100), nullable=True)
    bank_transaction_id = Column(String(100), nullable=True)
    accounts_payable_id = Column(String(100), nullable=True)
    
    confidence = Column(Enum('high', 'medium', 'low', name='reconciliation_confidence_enum'), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    nfe = relationship("NfeImport", backref="reconciliations")

