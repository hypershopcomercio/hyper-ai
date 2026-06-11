import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.nfe_parser_service import NfeParserService

dummy_xml = """<?xml version="1.0" encoding="UTF-8"?>
<nfeProc versao="4.00" xmlns="http://www.portalfiscal.inf.br/nfe">
    <NFe>
        <infNFe Id="NFe35231011222333444555550010001234561001234567" versao="4.00">
            <ide>
                <nNF>123456</nNF>
                <serie>1</serie>
                <dhEmi>2023-10-01T14:30:00-03:00</dhEmi>
            </ide>
            <emit>
                <CNPJ>11222333444555</CNPJ>
                <xNome>FORNECEDOR LTDA</xNome>
            </emit>
            <det nItem="1">
                <prod>
                    <cProd>PRD-001</cProd>
                    <cEAN>SEM GTIN</cEAN>
                    <xProd>PRODUTO TESTE</xProd>
                    <NCM>85171231</NCM>
                    <CFOP>5102</CFOP>
                    <uCom>UN</uCom>
                    <qCom>10.0000</qCom>
                    <vUnCom>100.00</vUnCom>
                    <vProd>1000.00</vProd>
                </prod>
                <imposto>
                    <ICMS>
                        <ICMS00>
                            <CST>00</CST>
                            <vBC>1000.00</vBC>
                            <pICMS>18.00</pICMS>
                            <vICMS>180.00</vICMS>
                        </ICMS00>
                    </ICMS>
                    <IPI>
                        <IPITrib>
                            <CST>50</CST>
                            <vBC>1000.00</vBC>
                            <pIPI>5.00</pIPI>
                            <vIPI>50.00</vIPI>
                        </IPITrib>
                    </IPI>
                </imposto>
            </det>
            <total>
                <ICMSTot>
                    <vProd>1000.00</vProd>
                    <vFrete>100.00</vFrete>
                    <vSeg>0.00</vSeg>
                    <vDesc>0.00</vDesc>
                    <vOutro>0.00</vOutro>
                    <vNF>1150.00</vNF>
                </ICMSTot>
            </total>
        </infNFe>
    </NFe>
</nfeProc>"""

parsed = NfeParserService.parse_xml(dummy_xml)
print(f"Status: {parsed.parse_status}")
if parsed.parse_error:
    print(f"Error: {parsed.parse_error}")

print(f"Chave: {parsed.access_key}")
print(f"Valor Prod: {parsed.totals.products_value}")
print(f"Frete: {parsed.totals.freight}")
for item in parsed.items:
    print(f"Item {item.n_item}: {item.description} - vProd: {item.product_value} - Frete Rateado: {item.allocations.freight} - vIPI: {item.taxes['ipi'].value}")
    print(f"Calculated Unit Cost: {item.calculated_costs['unit_cost_nf']}")
