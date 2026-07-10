-- ============================================================
-- Módulo Full (Fulfillment ML) — Fase 1 — SQL MANUAL (MySQL/prod)
-- Rodar UMA vez na base hyper_sync. Regra do projeto: sem migration automática.
-- create_all no backend só cria tabelas no SQLite de dev; em prod use este arquivo.
-- ============================================================

CREATE TABLE IF NOT EXISTS full_inventory (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  inventory_id      VARCHAR(64)  NOT NULL UNIQUE,
  ad_id             VARCHAR(255) NULL,
  sku               VARCHAR(255) NULL,
  variation_id      VARCHAR(64)  NULL,
  available_qty     INT DEFAULT 0,
  in_transit_qty    INT DEFAULT 0,
  not_available_qty INT DEFAULT 0,
  total_qty         INT DEFAULT 0,
  days_of_stock     FLOAT NULL,
  oldest_stock_days INT NULL,
  raw               JSON NULL,
  updated_at        DATETIME NULL,
  INDEX ix_full_inventory_ad  (ad_id),
  INDEX ix_full_inventory_sku (sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS full_stock_daily (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  inventory_id      VARCHAR(64)  NOT NULL,
  sku               VARCHAR(255) NULL,
  ad_id             VARCHAR(255) NULL,
  day               DATE NOT NULL,
  available_qty     INT DEFAULT 0,
  in_transit_qty    INT DEFAULT 0,
  not_available_qty INT DEFAULT 0,
  UNIQUE KEY ix_full_stock_daily_inv_day (inventory_id, day),
  INDEX ix_full_stock_daily_sku (sku),
  INDEX ix_full_stock_daily_ad  (ad_id),
  INDEX ix_full_stock_daily_day (day)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS full_storage_tariffs (
  id                  INT AUTO_INCREMENT PRIMARY KEY,
  name                VARCHAR(100) NULL,
  min_volume_l        FLOAT DEFAULT 0,        -- litros (>=)
  max_volume_l        FLOAT NULL,             -- litros (<); NULL = sem teto
  daily_fee           DECIMAL(10,4) DEFAULT 0,-- R$/unidade/dia de armazenagem
  inbound_fee         DECIMAL(10,2) DEFAULT 0,-- R$/unidade de envio ao CD
  aged_days_threshold INT DEFAULT 90,         -- a partir de N dias -> estoque antigo
  aged_daily_factor   FLOAT DEFAULT 3,        -- multiplicador da diária após o limiar
  active              TINYINT(1) DEFAULT 1,
  created_at          DATETIME NULL,
  updated_at          DATETIME NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Verificação:
--   SHOW TABLES LIKE 'full_%';
--   DESCRIBE full_inventory;
-- product_financial_metrics já deve existir (job financeiro). Se não:
--   SHOW TABLES LIKE 'product_financial_metrics';
