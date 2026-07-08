# -*- coding: utf-8 -*-
"""
Gera SQL manual (DBeaver) para popular product_tax_profiles a partir da
planilha de MVA do usuario (SKU, NCM, origem, regime ICMS-ST/DIFAL, MVA).

Uso (local, Windows):
    python -X utf8 app/scripts/generate_mva_import_sql.py "C:/caminho/MVA.xlsx" > docs/sql/import_mva.sql

Regras (validadas com a planilha 'MVA (4).xlsx' em 2026-07-07):
  - Coluna B: SKU | E: NCM | F: Origem ('0 - Nacional...' → nacional; 1/2 → importado)
  - Coluna H: 'ICMS-ST' → has_st=1 + mva_rate (coluna I, fracao → %)
              'DIFAL...' → has_difal=1 (aliquotas por origem via config/NF)
              'NCM VAZIO' → pulado com aviso (cadastrar NCM antes)
  - mlb_id resolvido via JOIN com ads pelo SKU (INSERT...SELECT), entao o SQL
    so cria perfil para SKU que existe em ads. Roda quantas vezes quiser
    (ON DUPLICATE KEY UPDATE pela unique de mlb_id).

NAO executa nada no banco — apenas imprime SQL para revisao humana.
"""
import sys
import openpyxl


def esc(s):
    return str(s).replace("'", "''").strip()


def main(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb['Produtos']

    rows_st, rows_difal, skipped = [], [], []

    for row in ws.iter_rows(min_row=2):
        sku = row[1].value  # B
        if not sku:
            continue
        sku = str(sku).strip()
        ncm = str(row[4].value).strip() if row[4].value else None  # E
        origem_raw = str(row[5].value or '')  # F
        regime = str(row[7].value or '').upper()  # H
        mva = row[8].value  # I (fracao: 0.7093)

        origem = 'nacional' if origem_raw.startswith('0') else 'importado'
        inter_rate = 12.0 if origem == 'nacional' else 4.0

        if 'ICMS-ST' in regime:
            if mva is None:
                skipped.append((sku, 'ICMS-ST sem MVA na planilha'))
                continue
            rows_st.append((sku, ncm, origem, round(float(mva) * 100, 4), inter_rate))
        elif 'DIFAL' in regime:
            rows_difal.append((sku, ncm, origem, inter_rate))
        else:
            skipped.append((sku, f'regime nao reconhecido: {regime or "vazio"}'))

    print("-- =============================================================")
    print("-- Import da tabela MVA -> product_tax_profiles (gerado por script)")
    print(f"-- ST: {len(rows_st)} SKUs | DIFAL: {len(rows_difal)} SKUs | Pulados: {len(skipped)}")
    print("-- Rode no DBeaver (hyper_sync). Reexecutavel (upsert por mlb_id).")
    print("-- =============================================================\n")

    for sku, reason in skipped:
        print(f"-- AVISO pulado: {sku} ({reason})")
    if skipped:
        print()

    print("-- ---------- PRODUTOS COM ST (has_st=1, mva_rate) ----------")
    for sku, ncm, origem, mva_pct, inter in rows_st:
        ncm_sql = f"'{esc(ncm)}'" if ncm else "NULL"
        print(f"""INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, '{origem}', NULL, 'SP', {ncm_sql},
       1, 0, 0, {mva_pct}, {inter}, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = '{esc(sku)}'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();""")

    print("\n-- ---------- PRODUTOS COM DIFAL (has_difal=1, sem ST) ----------")
    for sku, ncm, origem, inter in rows_difal:
        ncm_sql = f"'{esc(ncm)}'" if ncm else "NULL"
        print(f"""INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, '{origem}', NULL, 'SP', {ncm_sql},
       0, 0, 1, NULL, {inter}, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = '{esc(sku)}'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();""")

    print("\n-- Conferencia pos-import:")
    print("-- SELECT has_st, has_difal, COUNT(*) FROM product_tax_profiles GROUP BY has_st, has_difal;")
    print("-- SELECT COUNT(*) FROM ads a LEFT JOIN product_tax_profiles p ON p.mlb_id=a.id WHERE p.id IS NULL AND a.status='active';")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python generate_mva_import_sql.py <caminho MVA.xlsx>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
