import os
import sys
import tempfile
import io

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from app.core.database import SessionLocal
from app.models.nfe import NfeImport, NfeItem

dummy_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<nfeProc versao="4.00" xmlns="http://www.portalfiscal.inf.br/nfe">
    <NFe>
        <infNFe Id="NFe35231011222333444555550010001234561001234999" versao="4.00">
            <ide>
                <nNF>999999</nNF>
                <serie>1</serie>
                <dhEmi>2023-11-01T14:30:00-03:00</dhEmi>
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

def run_tests():
    # Bypass require_auth for testing by mocking if needed, 
    # but currently we can just use app.test_client() 
    # Wait, require_auth might block it. Let's see if we can pass a dummy auth or if it's strict.
    # We will pass a dummy token header that usually works in this project if the middleware allows test tokens or if we just test the logic inside.
    # Actually, the user asked for curl commands. Testing via flask test_client requires a token.
    # Let's clean up existing before test
    db = SessionLocal()
    try:
        existing = db.query(NfeImport).filter(NfeImport.access_key == '35231011222333444555550010001234561001234999').first()
        if existing:
            db.delete(existing)
            db.commit()
    finally:
        db.close()

    print("DB Cleaned. Ready to run curl commands for manual testing.")

if __name__ == "__main__":
    run_tests()
