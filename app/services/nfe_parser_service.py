import xml.etree.ElementTree as ET
from decimal import Decimal
import hashlib
from datetime import datetime
from app.schemas.nfe import (
    NfeImportSchema, NfeItemSchema, NfeIssuer, NfeTotals, NfeMetadata,
    ParseStatusEnum, AllocationDetail, TaxDetail
)

class NfeParserService:
    @staticmethod
    def _strip_ns(tag):
        if '}' in tag:
            return tag.split('}')[1]
        return tag

    @staticmethod
    def _find_ns(elem, match_tag):
        for child in elem:
            if NfeParserService._strip_ns(child.tag) == match_tag:
                return child
        return None

    @staticmethod
    def _find_all_ns(elem, match_tag):
        results = []
        for child in elem:
            if NfeParserService._strip_ns(child.tag) == match_tag:
                results.append(child)
        return results
        
    @staticmethod
    def _get_text(elem, match_tag, default=None):
        child = NfeParserService._find_ns(elem, match_tag)
        if child is not None and child.text is not None:
            return child.text
        return default

    @staticmethod
    def _get_decimal(elem, match_tag, default=Decimal('0.0')):
        val = NfeParserService._get_text(elem, match_tag)
        if val:
            try:
                return Decimal(val)
            except:
                pass
        return default

    @staticmethod
    def parse_xml(xml_content: str) -> NfeImportSchema:
        try:
            root = ET.fromstring(xml_content.encode('utf-8'))
            
            # Find the actual NFe tag regardless of wrapper (like nfeProc)
            nfe_node = root
            if NfeParserService._strip_ns(root.tag) == 'nfeProc':
                nfe_child = NfeParserService._find_ns(root, 'NFe')
                if nfe_child is not None:
                    nfe_node = nfe_child
            
            infNFe = NfeParserService._find_ns(nfe_node, 'infNFe')
            if infNFe is None:
                raise ValueError("Tag infNFe not found in XML")
                
            access_key = infNFe.attrib.get('Id', '').replace('NFe', '')
            if not access_key:
                raise ValueError("Access key not found in infNFe Id attribute")
                
            # ProtNFe
            prot_number = None
            if NfeParserService._strip_ns(root.tag) == 'nfeProc':
                protNFe = NfeParserService._find_ns(root, 'protNFe')
                if protNFe is not None:
                    infProt = NfeParserService._find_ns(protNFe, 'infProt')
                    if infProt is not None:
                        prot_number = NfeParserService._get_text(infProt, 'nProt')
            
            ide = NfeParserService._find_ns(infNFe, 'ide')
            nfe_number = NfeParserService._get_text(ide, 'nNF')
            series = NfeParserService._get_text(ide, 'serie')
            model = NfeParserService._get_text(ide, 'mod')
            operation_nature = NfeParserService._get_text(ide, 'natOp')
            environment = NfeParserService._get_text(ide, 'tpAmb')
            issue_date_str = NfeParserService._get_text(ide, 'dhEmi')
            if issue_date_str:
                # Handle ISO 8601 with timezone from NFe
                try:
                    issue_date = datetime.fromisoformat(issue_date_str)
                except:
                    issue_date = datetime.utcnow()
            else:
                issue_date = datetime.utcnow()
                
            emit = NfeParserService._find_ns(infNFe, 'emit')
            issuer_cnpj = NfeParserService._get_text(emit, 'CNPJ') or NfeParserService._get_text(emit, 'CPF')
            issuer_name = NfeParserService._get_text(emit, 'xNome')
            
            total = NfeParserService._find_ns(infNFe, 'total')
            icms_tot = NfeParserService._find_ns(total, 'ICMSTot')
            
            total_products = NfeParserService._get_decimal(icms_tot, 'vProd')
            total_invoice = NfeParserService._get_decimal(icms_tot, 'vNF')
            total_freight = NfeParserService._get_decimal(icms_tot, 'vFrete')
            total_insurance = NfeParserService._get_decimal(icms_tot, 'vSeg')
            total_discount = NfeParserService._get_decimal(icms_tot, 'vDesc')
            total_other = NfeParserService._get_decimal(icms_tot, 'vOutro')
            
            xml_sha256 = hashlib.sha256(xml_content.encode('utf-8')).hexdigest()
            
            schema = NfeImportSchema(
                access_key=access_key,
                issue_date=issue_date,
                issuer=NfeIssuer(cnpj=issuer_cnpj, name=issuer_name),
                totals=NfeTotals(
                    products_value=total_products,
                    invoice_value=total_invoice,
                    freight=total_freight,
                    insurance=total_insurance,
                    discount=total_discount,
                    other=total_other
                ),
                metadata=NfeMetadata(
                    nfe_number=nfe_number,
                    series=series,
                    model=model,
                    operation_nature=operation_nature,
                    environment=environment,
                    protocol_number=prot_number,
                    xml_sha256=xml_sha256
                ),
                items=[]
            )
            
            dets = NfeParserService._find_all_ns(infNFe, 'det')
            for det in dets:
                n_item = int(det.attrib.get('nItem', '0'))
                prod = NfeParserService._find_ns(det, 'prod')
                
                sku_supplier = NfeParserService._get_text(prod, 'cProd')
                description = NfeParserService._get_text(prod, 'xProd')
                ean = NfeParserService._get_text(prod, 'cEAN')
                if ean in ["SEM GTIN", "NO GTIN"]:
                    ean = "SEM GTIN"
                    
                ncm = NfeParserService._get_text(prod, 'NCM')
                cest = NfeParserService._get_text(prod, 'CEST')
                cfop = NfeParserService._get_text(prod, 'CFOP')
                unit = NfeParserService._get_text(prod, 'uCom')
                quantity = NfeParserService._get_decimal(prod, 'qCom')
                unit_value = NfeParserService._get_decimal(prod, 'vUnCom')
                product_value = NfeParserService._get_decimal(prod, 'vProd')
                
                unit_trib = NfeParserService._get_text(prod, 'uTrib')
                quantity_trib = NfeParserService._get_decimal(prod, 'qTrib')
                unit_value_trib = NfeParserService._get_decimal(prod, 'vUnTrib')
                
                alloc_freight = Decimal('0.0')
                alloc_ins = Decimal('0.0')
                alloc_desc = Decimal('0.0')
                alloc_other = Decimal('0.0')
                formula = None
                
                if total_products > 0:
                    ratio = product_value / total_products
                    alloc_freight = ratio * total_freight
                    alloc_ins = ratio * total_insurance
                    alloc_desc = ratio * total_discount
                    alloc_other = ratio * total_other
                    formula = "item.product_value / nfe.total_products_value * total_x"
                
                # Parse Taxes
                imposto = NfeParserService._find_ns(det, 'imposto')
                
                icms_dict = TaxDetail()
                st_dict = TaxDetail()
                cst_csosn = None
                
                if imposto is not None:
                    icms_node = NfeParserService._find_ns(imposto, 'ICMS')
                    if icms_node is not None and len(icms_node) > 0:
                        inner_icms = icms_node[0] # ICMS00, ICMS10, etc
                        cst_csosn = NfeParserService._get_text(inner_icms, 'CST') or NfeParserService._get_text(inner_icms, 'CSOSN')
                        icms_dict.base = NfeParserService._get_decimal(inner_icms, 'vBC')
                        icms_dict.value = NfeParserService._get_decimal(inner_icms, 'vICMS')
                        icms_dict.rate = NfeParserService._get_decimal(inner_icms, 'pICMS')
                        st_dict.base = NfeParserService._get_decimal(inner_icms, 'vBCST')
                        st_dict.value = NfeParserService._get_decimal(inner_icms, 'vICMSST')
                        st_dict.rate = NfeParserService._get_decimal(inner_icms, 'pICMSST')
                    
                    ipi_dict = TaxDetail()
                    ipi_node = NfeParserService._find_ns(imposto, 'IPI')
                    if ipi_node is not None:
                        ipi_trib = NfeParserService._find_ns(ipi_node, 'IPITrib')
                        if ipi_trib is not None:
                            ipi_dict.value = NfeParserService._get_decimal(ipi_trib, 'vIPI')
                            ipi_dict.rate = NfeParserService._get_decimal(ipi_trib, 'pIPI')
                            ipi_dict.base = NfeParserService._get_decimal(ipi_trib, 'vBC')
                
                # Custo Unitário da NF (Produto + Rateios + ST + IPI)
                # Obs: ICMS normal já está embutido no vProd, exceto quando ICMS Desonerado etc. Na regra geral, ST e IPI somam ao custo.
                item_total_nf_cost = product_value + alloc_freight + alloc_ins + alloc_other - alloc_desc + ipi_dict.value + st_dict.value
                unit_cost_nf = item_total_nf_cost / quantity if quantity > 0 else Decimal('0.0')

                item = NfeItemSchema(
                    n_item=n_item,
                    sku_supplier=sku_supplier,
                    description=description,
                    ean=ean,
                    ncm=ncm,
                    cest=cest,
                    cfop=cfop,
                    cst_csosn=cst_csosn,
                    unit=unit,
                    quantity=quantity,
                    unit_value=unit_value,
                    product_value=product_value,
                    unit_trib=unit_trib,
                    quantity_trib=quantity_trib,
                    unit_value_trib=unit_value_trib,
                    allocations=AllocationDetail(
                        freight=alloc_freight,
                        insurance=alloc_ins,
                        discount=alloc_desc,
                        other=alloc_other,
                        formula=formula
                    ),
                    taxes={
                        "icms": icms_dict,
                        "st": st_dict,
                        "ipi": ipi_dict
                    },
                    calculated_costs={
                        "total_item_cost_nf": item_total_nf_cost,
                        "unit_cost_nf": unit_cost_nf
                    }
                )
                schema.items.append(item)
                
            return schema
            
        except Exception as e:
            return NfeImportSchema(
                access_key="",
                issue_date=datetime.utcnow(),
                issuer=NfeIssuer(cnpj="", name=""),
                totals=NfeTotals(),
                parse_status=ParseStatusEnum.error,
                parse_error=str(e)
            )
