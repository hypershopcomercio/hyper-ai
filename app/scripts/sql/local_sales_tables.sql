-- Módulo Venda Local / Precificação Local
-- Execute uma vez na base de produção antes de publicar a funcionalidade.
-- Compatível com MySQL 8+. O ambiente SQLite de desenvolvimento pode usar
-- Base.metadata.create_all para estas mesmas tabelas.

CREATE TABLE IF NOT EXISTS sales_channels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    channel_type VARCHAR(30) NOT NULL DEFAULT 'online',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT IGNORE INTO sales_channels (`key`, name, channel_type, is_active)
VALUES ('mercado_livre', 'Mercado Livre', 'marketplace', TRUE),
       ('local', 'Loja física', 'local', TRUE);

CREATE TABLE IF NOT EXISTS local_product_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(255) NOT NULL,
    channel_key VARCHAR(50) NOT NULL DEFAULT 'local',
    ad_id VARCHAR(255) NULL,
    selling_price DOUBLE NOT NULL,
    target_margin_percent DOUBLE NOT NULL DEFAULT 10.0,
    calculated_cost DOUBLE NOT NULL DEFAULT 0.0,
    tax_rate_percent DOUBLE NOT NULL DEFAULT 0.0,
    is_manual_price BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(30) NOT NULL DEFAULT 'ready',
    notes TEXT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_local_product_price_sku_channel (sku, channel_key),
    KEY idx_local_product_prices_sku (sku)
);

CREATE TABLE IF NOT EXISTS local_sales (
    id VARCHAR(64) PRIMARY KEY,
    channel_key VARCHAR(50) NOT NULL DEFAULT 'local',
    customer_name VARCHAR(255) NULL,
    payment_method VARCHAR(80) NULL,
    subtotal DOUBLE NOT NULL DEFAULT 0.0,
    discount_amount DOUBLE NOT NULL DEFAULT 0.0,
    total_amount DOUBLE NOT NULL DEFAULT 0.0,
    status VARCHAR(30) NOT NULL DEFAULT 'completed',
    notes TEXT NULL,
    completed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cancelled_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_local_sales_completed_at (completed_at),
    KEY idx_local_sales_status (status)
);

CREATE TABLE IF NOT EXISTS local_sale_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id VARCHAR(64) NOT NULL,
    sku VARCHAR(255) NOT NULL,
    product_name VARCHAR(500) NOT NULL,
    tiny_product_id VARCHAR(255) NULL,
    ad_id VARCHAR(255) NULL,
    quantity INT NOT NULL,
    unit_price DOUBLE NOT NULL,
    unit_cost DOUBLE NOT NULL DEFAULT 0.0,
    target_margin_percent DOUBLE NOT NULL DEFAULT 0.0,
    tax_rate_percent DOUBLE NOT NULL DEFAULT 0.0,
    tax_amount DOUBLE NOT NULL DEFAULT 0.0,
    line_total DOUBLE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_local_sale_item_sale FOREIGN KEY (sale_id) REFERENCES local_sales(id),
    KEY idx_local_sale_items_sku (sku)
);

CREATE TABLE IF NOT EXISTS inventory_movements (
    id VARCHAR(64) PRIMARY KEY,
    sku VARCHAR(255) NOT NULL,
    movement_type VARCHAR(50) NOT NULL,
    quantity_delta INT NOT NULL,
    quantity_before INT NOT NULL,
    quantity_after INT NOT NULL,
    reference_type VARCHAR(50) NOT NULL,
    reference_id VARCHAR(64) NOT NULL,
    sync_status VARCHAR(30) NOT NULL DEFAULT 'pending',
    notes TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_inventory_movements_sku (sku),
    KEY idx_inventory_movements_reference (reference_id),
    KEY idx_inventory_movements_sync (sync_status)
);
