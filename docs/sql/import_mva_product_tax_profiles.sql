-- =============================================================
-- Import da tabela MVA -> product_tax_profiles (gerado por script)
-- ST: 57 SKUs | DIFAL: 194 SKUs | Pulados: 12
-- Rode no DBeaver (hyper_sync). Reexecutavel (upsert por mlb_id).
-- =============================================================

-- AVISO pulado: CAIXA-DE-MASSA-ARQPLAST-20L-PRETA (regime nao reconhecido: NCM VAZIO)
-- AVISO pulado: ESTOJO-ORGANIZADOR-ARQPLAST-MASTER-CASE-PRETO (regime nao reconhecido: NCM VAZIO)
-- AVISO pulado: LANTERNA-HAWAPI-CABEÇA-PRETA (regime nao reconhecido: ACREDITO QUE ESSE NCM ESTEJA INCORRETO)
-- AVISO pulado: MALETA-ARQPLAST-CARBOX-PRETA (regime nao reconhecido: NCM VAZIO)
-- AVISO pulado: MALETA-ARQPLAST-COMBAT-PRETA (regime nao reconhecido: NCM VAZIO)
-- AVISO pulado: MALETA-ARQPLAST-ECONOMICA-PRETA (regime nao reconhecido: NCM VAZIO)
-- AVISO pulado: MALETA-ARQPLAST-MASTER-BOX-PRETA (regime nao reconhecido: NCM VAZIO)
-- AVISO pulado: MALETA-ARQPLAST-MULTIUSO-VERDE (regime nao reconhecido: NCM VAZIO)
-- AVISO pulado: MALETA-ARQPLAST-MULTI USO-FEMININA-ROSA (regime nao reconhecido: NCM VAZIO)
-- AVISO pulado: MALETA-ARQPLAST-FERRAMENTAS-PRETA (regime nao reconhecido: NCM VAZIO)
-- AVISO pulado: ORGANIZADOR-ARQPLAST-QUADRUPLO-PRETO (regime nao reconhecido: NCM VAZIO)
-- AVISO pulado: PLACA–ARQPLAST-SINALIZADORA-AMARELO (regime nao reconhecido: NCM VAZIO)

-- ---------- PRODUTOS COM ST (has_st=1, mva_rate) ----------
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       1, 0, 0, 72.1, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'AIR-FRYER-BAK-5,5-FAMILY'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       1, 0, 0, 72.1, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'AIR-FRYER-BAK-5,5-FAMILY-OFF-WHITE-127V'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       1, 0, 0, 72.1, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'AIR-FRYER-BAK-5,5-FAMILY-PRETO-127V'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       1, 0, 0, 72.1, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'AIR-FRYER-BAK-5,5-FAMILY-OFF-WHITE-220V'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       1, 0, 0, 72.1, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'AIR-FRYER-BAK-5,5-FAMILY-PRETO-220V'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       1, 0, 0, 72.1, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'AIR-FRYER-BAK-3,7L-SUPER'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       1, 0, 0, 72.1, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'AIR-FRYER-BAK-3,7L-SUPER-127V'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       1, 0, 0, 72.1, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'AIR-FRYER-BAK-3,7L-SUPER-220V'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8509.40.20',
       1, 0, 0, 61.56, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BATEDEIRA-BAK-ELETRICA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8509.40.20',
       1, 0, 0, 61.56, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BATEDEIRA-BAK-ELETRICA-127V-BRANCO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8509.40.20',
       1, 0, 0, 61.56, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BATEDEIRA-BAK-ELETRICA-220V-BRANCO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8509.40.20',
       1, 0, 0, 61.56, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BATEDEIRA-BAK-ELETRICA-127V-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8509.40.20',
       1, 0, 0, 61.56, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BATEDEIRA-BAK-ELETRICA-220V-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8509.40.20',
       1, 0, 0, 61.56, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BATEDEIRA-BAK-ELETRICA-127V-VERMELHO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8509.40.20',
       1, 0, 0, 61.56, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BATEDEIRA-BAK-ELETRICA-220V-VERMELHO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8509.40.20',
       1, 0, 0, 61.56, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BATEDEIRA-BAK-127-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8211.93.20',
       1, 0, 0, 80.29, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CANIVETE-HAWAPI-KURA-MADEIRA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8211.93.20',
       1, 0, 0, 80.29, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CANIVETE-HAWAPI-RUMI-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8516.60.00',
       1, 0, 0, 72.1, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CHURRASQUEIRA-BAK-ELETRICA-PRETA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8516.60.00',
       1, 0, 0, 72.1, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CHURRASQUEIRA-BAK-ELETRICA-127V-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8516.60.00',
       1, 0, 0, 72.1, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CHURRASQUEIRA-BAK-ELETRICA-220V-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8211.92.90',
       1, 0, 0, 80.29, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'FACA-HAWAPI-BAINHA-VERDE'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '7321.11.00',
       1, 0, 0, 70.93, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'FOGAREIRO-HAWAPI-GLP-VERDE-LIMAO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '7321.11.00',
       1, 0, 0, 70.93, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'FOGAREIRO-HAWAPI-AÇO-VERDE-LIMAO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8516.60.00',
       1, 0, 0, 70.93, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'FORNO-BAK-10L-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8516.60.00',
       1, 0, 0, 70.93, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'FORNO-BAK-10L-127V-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8516.60.00',
       1, 0, 0, 70.93, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'FORNO-BAK-10L-220V-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8516.60.00',
       1, 0, 0, 70.93, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'FORNO-BAK-21L-127V-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8516.60.00',
       1, 0, 0, 70.93, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'FORNO-BAK-21L-220V-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8471.60.52',
       1, 0, 0, 52.73, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'KIT-GAMER-BAK-4EM1-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8201.40.00',
       1, 0, 0, 67.41, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MACHADO-HAWAPI-2 EM 1-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8516.79.90',
       1, 0, 0, 72.1, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MINI-GRILL-BAK-ELETRICO-INOX-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8516.79.90',
       1, 0, 0, 72.1, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MINI-GRILL-BAK-750W-127V'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8516.79.90',
       1, 0, 0, 72.1, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MINI-GRILL-BAK-750W-220V'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8509.40.90',
       1, 0, 0, 61.56, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MIXER-BAK-127V-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8509.40.90',
       1, 0, 0, 61.56, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MIXER-BAK-127V-300W-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8509.40.90',
       1, 0, 0, 61.56, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MIXER-BAK-220V-300W-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8509.40.50',
       1, 0, 0, 61.56, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MIXER-BAK-3EM1'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8509.40.50',
       1, 0, 0, 61.56, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MIXER-BAK-3EM1-127V-BRANCO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8509.40.50',
       1, 0, 0, 61.56, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MIXER-BAK-3EM1-127V-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8509.40.50',
       1, 0, 0, 61.56, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MIXER-BAK-3EM1-220V-BRANCO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8509.40.50',
       1, 0, 0, 61.56, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MIXER-BAK-3EM1-220V-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8203.20.10',
       1, 0, 0, 81.46, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MULTITOOL-HAWAPI-15EM1-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8201.10.00',
       1, 0, 0, 67.41, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PÁ-HAWAPI-3EM1-PRETA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       1, 0, 0, 72.1, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PANELA-BAK-ELETRICA-900W'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       1, 0, 0, 72.1, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PANELA-BAK-ELETRICA-900W-127V-INOX'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       1, 0, 0, 72.1, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PANELA-BAK-ELETRICA-900W-220V-INOX'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       1, 0, 0, 72.1, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PANELA-BAK-ELETRICA-900W-127V-VERMELHO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       1, 0, 0, 72.1, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PANELA-BAK-ELETRICA-900W-220V-VERMELHO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8516.79.90',
       1, 0, 0, 72.1, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PIPOQUEIRA-BAK-ELETRICA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8516.79.90',
       1, 0, 0, 72.1, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PIPOQUEIRA-BAK-ELETRICA-127V-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8516.79.90',
       1, 0, 0, 72.1, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PIPOQUEIRA-BAK-ELETRICA-220V-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8516.79.90',
       1, 0, 0, 72.1, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PIPOQUEIRA-BAK-ELETRICA-127V-VERMELHO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8516.79.90',
       1, 0, 0, 72.1, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PIPOQUEIRA-BAK-ELETRICA-220V-VERMELHO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8516.79.90',
       1, 0, 0, 72.1, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'SANDUICHEIRA-BAK-ELETRICA-PRETA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8516.79.90',
       1, 0, 0, 72.1, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'SANDUICHEIRA-BAK-ELETRICA-127V-PRETA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8516.79.90',
       1, 0, 0, 72.1, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'SANDUICHEIRA-BAK-ELETRICA-220V-PRETA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=1, has_difal=0, mva_rate=VALUES(mva_rate),
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();

-- ---------- PRODUTOS COM DIFAL (has_difal=1, sem ST) ----------
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '3924.90.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BANDEJA-ARQPLAST-PINTURA-PRETA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9503.00.99',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'COOLER-INTEX-24LATAS-AZUL'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6306.22.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BARRACA-HAWAPI-AYLLU-VERDELIMAO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-AZUL-CLARO-G'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-AZUL-CLARO-M'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-AZUL-CLARO-P'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-ROSA-CLARO-G'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-ROSA-CLARO-M'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-ROSA-CLARO-P'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CROPPED-MULTIFORMAS-SUPLEX'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CROPPED-MULTIFORMAS-SUPLEX-AZUL-UNICO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CROPPED-MULTIFORMAS-SUPLEX-BRANCO-UNICO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CROPPED-MULTIFORMAS-SUPLEX-MARROM-UNICO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CROPPED-MULTIFORMAS-SUPLEX-PRETO-UNICO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CROPPED-MULTIFORMAS-SUPLEX-VERMELHO-UNICO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BLUSINHA-BOJO-BRANCO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BLUSINHA-DUNA-BABADO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BLUSINHA-AZUL'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BLUSINHA-BEGE'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BLUSINHA-BRANCA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BLUSINHA-PRETA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6307.20.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BOIA-INFANTIL-NASH-SIRI-AZUL-CLARO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6307.20.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BOIA-INFANTIL-NASH-ESTRELA-ROSA-CLARO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6307.20.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BOIA-INFANTIL-NASH-CHASE-AZUL'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6307.20.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BOIA-INFANTIL-NASH-SKYE-PINK'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6307.20.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BOIA-INFANTIL-NASH-FLAMINGO-ROSA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6307.20.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BOIA-INFANTIL-NASH-UNICORNIO-ROSA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8414.20.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BOMBA-INTEX-MANUAL-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '9503.00.22',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'BONECA-MILK-SAPEKINHA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9401.79.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CADEIRA-HAWAPI-KAYPI-VERDE-LIMAO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9401.79.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CADEIRA-HAWAPI-KAYPI-AZUL'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9401.79.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CADEIRA-HAWAPI-PICCHU-LARANJA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9401.79.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CADEIRA-HAWAPI-PICCHU-VERDE-LIMAO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9401.79.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CADEIRA-HAWAPI-PICCHU-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '3924.90.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MALETA-ARQPLAST-BAIXA13-PRETA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '3924.90.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MALETA-ARQPLAST-ALTA16-PRETA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '3924.10.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CAIXA-TERMICA-ARQPLAST-32L-AZUL'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '9503.00.10',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CARRINHO-SAMBA-TOYS-BONECA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6404.19.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CHINELO-PANTUFA-BENECASA-LADY'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6404.19.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CHINELO-PANTUFA-BENECASA-LADY-MARROM'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6404.19.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CHINELO-PANTUFA-BENECASA-LADY-ROSA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', NULL,
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'COLCHAO-BESTWAY-INFLAVEL-BOMBA-AZUL'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '3926.90.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'COLCHÃO-INFLÁVEL-HAWAPI-CASAL-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8215.99.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CONJUNTO-TALHERES-HAWAPI-8 EM 1-VERDE'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CORRENTE-PLASTICA-ZEBRADA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ESCOVA-SANITARIA-ARQPLAST-SUPORTE-BRANCA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '3924.90.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ESTOJO-ARQPLAST-ORGANIZADOR-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'GORRO-INFANTIL-BENECASA-FUNNY'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6505.00.22',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'GORRO-INFANTIL-BENECASA-POMPOM'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6505.00.22',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'GORRO-INFANTIL-BENECASA-POMPOM-AZUL-UNICO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6505.00.22',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'GORRO-INFANTIL-BENECASA-POMPOM-CINZA-UNICO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6505.00.22',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'GORRO-INFANTIL-BENECASA-POMPOM-ROSA-CHICLETE-UNICO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6505.00.22',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'GORRO-INFANTIL-BENECASA-POMPOM-ROSA-VELHO-UNICO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CROCODILO-ARTBRINK-BRINQUEDO-VERDE'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6302.32.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'JOGO-CAMA-BENECASA-BORDADO-INGLES'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6302.32.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'JOGO-CAMA-BORDADO-INGLES-CASAL-CINZA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6302.32.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'JOGO-CAMA-BORDADO-INGLES-KING-CINZA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6302.32.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'JOGO-CAMA-BORDADO-INGLES-QUEEN-CINZA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6302.32.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'JOGO-CAMA-BORDADO-INGLES-CASAL-FENDI'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6302.32.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'JOGO-CAMA-BORDADO-INGLES-KING-FENDI'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6302.32.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'JOGO-CAMA-BORDADO-INGLES-QUEEN-FENDI'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9503.00.99',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'KIT-2-BASQUETE-BESTWAY-PISCINA-AZUL-AMARELO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9503.00.99',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'KIT-2-COOLER-INTEX-24LATAS-AZUL'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9503.00.99',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'CESTA-BASQUETE-BESTWAY-PISCINA-AZUL-AMARELO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9617.00.20',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'KIT-BICO-THERMOS-SILICONE'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9503.00.22',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'KIT-BONECA-MILK-CARRINHO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9503.00.99',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'GOL-BESTWAY-PISCINA-AMARELO-AZUL'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'KIT-PISCINA-BESTWAY-AMARELO-AZUL'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PLAYGROUND-PISCINA-INTEX-CANDY-AZUL'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9503.00.99',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PISCINA-INTEX-275L-COLORIDA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9503.00.99',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'KIT-PISCINA-INTEX-780L-COLORIDA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9503.00.99',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'KIT-COOLER-INTEX-24LATAS-AZUL'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9503.00.99',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'KIT-VOLEI-BESTWAY-PISCINA-AMARELO-AZUL'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '8513.10.10',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'LAMPIÃO-HAWAPI-KILLA-VERDE-LIMAO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '3924.10.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'LANCHEIRA-THERMOS-BENTO-BOX'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '3924.10.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'LANCHEIRA-THERMOS-BENTO-BOX-CORAL'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '3924.10.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'LANCHEIRA-THERMOS-BENTO-BOX-VERDE-CLARO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '3924.90.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'LIXEIRA-ARQPLAST-7L-PRETA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'LIXEIRA-ARQPLAST-9L-BEGE'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'LIXEIRA-ARQPLAST-9L-PRETA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '3926.90.90',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MALETA-ARQPLAST-PRIMEIRO-SOCORROS-VERMELHA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '3924.90.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MALETA-ARQPLAST-ALTA13-PRETA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6301.40.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MANTA-TESSI-LUXOR-MANGA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6301.40.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MANTA-TESSI-LUXOR-MANGA-ARGILA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6301.40.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MANTA-TESSI-LUXOR-MANGA-BLUSH'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6301.40.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MANTA-TESSI-LUXOR-MANGA-CONCRETE'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6301.40.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MANTA-TESSI-LUXOR-MANGA-LUA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6301.40.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MANTA-TESSI-LUXOR-MANGA-PEACH'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9503.00.39',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MASCARA-ARTBRINK-DINOSSAURO-VERDE'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9403.20.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MESA-HAWAPI-46X68-VERDE-LIMAO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9403.20.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MESA-HAWAPI-40X56-VERDE-LIMAO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MOLETOM-JUVENIL'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MOLETOM-JUVENIL-AZUL-MARINHO-G'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MOLETOM-JUVENIL-AZUL-MARINHO-GG'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MOLETOM-JUVENIL-AZUL-MARINHO-M'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MOLETOM-JUVENIL-AZUL-MARINHO-P'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MOLETOM-JUVENIL-BORDÔ-G'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MOLETOM-JUVENIL-BORDÔ-GG'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MOLETOM-JUVENIL-BORDÔ-M'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MOLETOM-JUVENIL-BORDÔ-P'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MOLETOM-JUVENIL-BRANCO-G'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MOLETOM-JUVENIL-BRANCO-GG'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MOLETOM-JUVENIL-BRANCO-M'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MOLETOM-JUVENIL-BRANCO-P'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MOLETOM-JUVENIL-PRETO-G'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MOLETOM-JUVENIL-PRETO-GG'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MOLETOM-JUVENIL-PRETO-M'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'MOLETOM-JUVENIL-PRETO-P'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PANTUFA-BENECASA-BICHINHOS'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PANTUFA-BENECASA-BICHINHOS-CACHORRINHO-CINZA-38'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PANTUFA-BENECASA-BICHINHOS-GATINHO-ROSA-38'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PANTUFA-BENECASA-BICHINHOS-RAPOSA-ROSA-38'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PANTUFA-BENECASA-BICHINHOS-URSINHO-BEGE-38'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6404.19.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'SAPATINHO-INFANTIL-BENECASA-ANIMAIS'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6404.19.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'SAPATINHO-INFANTIL-BENECASA-ANIMAIS-AZUL-16'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6404.19.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'SAPATINHO-INFANTIL-BENECASA-ANIMAIS-AZUL-18'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6404.19.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'SAPATINHO-INFANTIL-BENECASA-ANIMAIS-AZUL-20'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6404.19.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'SAPATINHO-INFANTIL-BENECASA-ANIMAIS-ROSA-16'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6404.19.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'SAPATINHO-INFANTIL-BENECASA-ANIMAIS-ROSA-18'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6404.19.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'SAPATINHO-INFANTIL-BENECASA-ANIMAIS-ROSA-20'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9506.99.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PISCINA-INTEX-581L-AZUL'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9506.99.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PLAYGROUND-INTEX-CANDY-AZUL'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9506.99.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PISCINA-INTEX-275L-POR DO SOL'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9503.00.99',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PISCINA-INTEX-780L-COLORIDA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9506.99.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PISCINA-MOR-550L-ARCO-IRIS'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9503.00.97',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PISTA-COLOR-353M-CARRO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '9506.29.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'PLAY-CENTER-MOR-VOLEIBOL-VERMELHO-AZUL'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-MICROFIBRA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-MICROFIBRA-AZUL-G'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-MICROFIBRA-AZUL-M'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-MICROFIBRA-AZUL-P'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-MICROFIBRA-CINZA-G'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-MICROFIBRA-CINZA-M'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-MICROFIBRA-CINZA-P'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-MICROFIBRA-ROSA-G'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-MICROFIBRA-ROSA-M'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-MICROFIBRA-ROSA-P'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-MICROFIBRA-ROSA-CHICLETE-G'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-MICROFIBRA-ROSA-CHICLETE-M'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-MICROFIBRA-ROSA-CHICLETE-P'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPÃO-INFANTIL-HYPERSHOP-MICROFIBRA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPÃO-INFANTIL-HYPERSHOP-MICROFIBRA-ABELHINHA-G'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPÃO-INFANTIL-HYPERSHOP-MICROFIBRA-LISTRADO-G'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPÃO-INFANTIL-HYPERSHOP-MICROFIBRA-ABELHINHA-M'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPÃO-INFANTIL-HYPERSHOP-MICROFIBRA-LISTRADO-M'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPÃO-INFANTIL-HYPERSHOP-MICROFIBRA-ABELHINHA-P'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6108.92.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPÃO-INFANTIL-HYPERSHOP-MICROFIBRA-LISTRADO-P'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL- BENECASA-FELPUDO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-BRANCO-DINOSSAURO-G'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-BRANCO-DINOSSAURO-M'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-BRANCO-DINOSSAURO-P'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-LILAS-GATINHO-G'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-LILAS-GATINHO-M'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-LILAS-GATINHO-P'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-AZUL-CLARO-LEAO-G'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-AZUL-CLARO-LEAO-M'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-AZUL-CLARO-LEAO-P'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-BRANCO-PANDA-G'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-BRANCO-PANDA-M'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-BRANCO-PANDA-P'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-ROSA-CLARO-UNICORNIO-G'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-ROSA-CLARO-UNICORNIO-M'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6208.91.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPAO-INFANTIL-BENECASA-FELPUDO-ROSA-CLARO-UNICORNIO-P'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '4201.00.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPINHA-MEUPET-CACHORRO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '4201.00.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPINHA-MEUPET-CACHORRO-AMARELO-PRETO-TAM2'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '4201.00.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPINHA-MEUPET-CACHORRO-LARANJA-AZUL-TAM2'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '4201.00.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPINHA-MEUPET-CACHORRO-LARANJA-CINZA-TAM2'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '4201.00.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPINHA-MEUPET-CACHORRO-AMARELO-PRETO-TAM3'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '4201.00.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPINHA-MEUPET-CACHORRO-LARANJA-AZUL-TAM3'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '4201.00.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPINHA-MEUPET-CACHORRO-LARANJA-CINZA-TAM3'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '4201.00.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPINHA-MEUPET-CACHORRO-AMARELO-PRETO-TAM4'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '4201.00.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPINHA-MEUPET-CACHORRO-LARANJA-AZUL-TAM4'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '4201.00.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPINHA-MEUPET-CACHORRO-LARANJA-CINZA-TAM4'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '4201.00.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPINHA-MEUPET-CACHORRO-AMARELO-PRETO-TAM5'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '4201.00.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPINHA-MEUPET-CACHORRO-LARANJA-AZUL-TAM5'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '4201.00.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'ROUPINHA-MEUPET-CACHORRO-LARANJA-CINZA-TAM5'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '4202.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'SACO-HAWAPI-10L-CINZA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '4202.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'SACO-HAWAPI-30L-CINZA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '4202.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'SACO-HAWAPI-30L-VERDE'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '4202.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'SACO-HAWAPI-10L-VERDE'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '4202.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'SACO-HAWAPI-20L-CINZA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '4202.92.00',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'SACO-HAWAPI-20L-VERDE'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '3506.10.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'SILICONE-TEKBOND-ACETICO-BRANCO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '3506.10.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'SILICONE-TEKBOND-ACETICO-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'importado', NULL, 'SP', '3506.10.90',
       0, 0, 1, NULL, 4.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'SILICONE-TEKBOND-ACETICO-INCOLOR'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6104.43.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'VESTIDO-KHLOE'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6104.43.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'VESTIDO-KHLOE-MARROM'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6104.43.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'VESTIDO-KHLOE-BRANCO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', '6104.43.00',
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'VESTIDO-KHLOE-PRETO'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'VESTIDO-MIDI-RIBANA-FENDA'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'VESTIDO-MIDI-RIBANA-FENDA-3'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'VESTIDO-MIDI-RIBANA-FENDA-1'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();
INSERT INTO product_tax_profiles
  (mlb_id, sku, tiny_product_id, product_origin, origin_uf, destination_uf_default, ncm,
   has_st, has_ipi, has_difal, mva_rate, origin_icms_rate, destination_icms_rate, is_active, created_at, updated_at)
SELECT a.id, a.sku, NULL, 'nacional', NULL, 'SP', NULL,
       0, 0, 1, NULL, 12.0, 18.0, 1, NOW(), NOW()
FROM ads a WHERE a.sku = 'VESTIDO-MIDI-RIBANA-FENDA-2'
ON DUPLICATE KEY UPDATE
  sku=VALUES(sku), product_origin=VALUES(product_origin), ncm=VALUES(ncm),
  has_st=0, has_difal=1, mva_rate=NULL,
  origin_icms_rate=VALUES(origin_icms_rate), destination_icms_rate=VALUES(destination_icms_rate),
  is_active=1, updated_at=NOW();

-- Conferencia pos-import:
-- SELECT has_st, has_difal, COUNT(*) FROM product_tax_profiles GROUP BY has_st, has_difal;
-- SELECT COUNT(*) FROM ads a LEFT JOIN product_tax_profiles p ON p.mlb_id=a.id WHERE p.id IS NULL AND a.status='active';
