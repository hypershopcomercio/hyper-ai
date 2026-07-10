-- ============================================================
-- SEED APROXIMADO da tabela de tarifas do Full — AJUSTE com os
-- valores EXATOS do seu catálogo (central de vendedores > "Custos
-- por estoque antigo"). Baseado nas faixas informadas pelo usuário:
--   Pequeno ~R$0,07/un/dia · Médio ~R$0,15/un/dia · Grande ~R$0,50/un/dia
--   Estoque antigo: a partir de ~4 meses (demais categorias).
-- Volume (litros) = comprimento×largura×altura (mm) ÷ 1.000.000.
-- inbound_fee (envio ao CD por unidade) é PLACEHOLDER — ML cobra frete de
-- inbound variável; ajuste ou zere conforme sua realidade.
-- ============================================================

INSERT INTO full_storage_tariffs
  (name, min_volume_l, max_volume_l, daily_fee, inbound_fee, aged_days_threshold, aged_daily_factor, active, created_at, updated_at)
VALUES
  ('Pequeno', 0,   10,   0.0700, 0.80, 120, 3, 1, NOW(), NOW()),
  ('Médio',   10,  50,   0.1500, 1.50, 120, 3, 1, NOW(), NOW()),
  ('Grande',  50,  NULL, 0.5000, 4.00, 120, 3, 1, NOW(), NOW());

-- Conferir:
--   SELECT name, min_volume_l, max_volume_l, daily_fee, inbound_fee, aged_days_threshold FROM full_storage_tariffs ORDER BY min_volume_l;
