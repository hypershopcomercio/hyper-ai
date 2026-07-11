"""
FullService — sincronização read-only do estoque no Full (Fulfillment ML) e
motor de custo real de armazenagem/inbound.

Fase 1:
  - sync_full_inventory(): p/ cada Ad Full, resolve inventory_id(s), lê o estoque
    (disponível / em trânsito / indisponível), calcula dias de cobertura e
    antiguidade (best-effort via operações), grava snapshot + série diária.
  - compute_full_costs(): casa o volume real do produto com a tabela de tarifas
    e grava os campos de armazenagem em ProductFinancialMetric — que ads.py já
    consome no cálculo de margem do modal do produto (custo REAL no lugar do
    estimado por faixa de dimensão).

NÃO escreve nada no Mercado Livre. Tudo auditável (payload cru salvo em full_inventory.raw).
"""
import logging
import datetime

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.ad import Ad
from app.models.oauth_token import OAuthToken
from app.models.financial import ProductFinancialMetric
from app.models.full import FullInventory, FullStockDaily, FullStorageTariff
from app.services.meli_api import MeliApiService

logger = logging.getLogger(__name__)


class FullService:
    def __init__(self, db=None):
        self.db = db or SessionLocal()
        self._owns_db = db is None
        self.meli = MeliApiService(db_session=self.db)

    def close(self):
        if self._owns_db:
            self.db.close()

    def get_seller_id(self):
        token = self.db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
        if token and token.user_id:
            return token.user_id
        return settings.MELI_USER_ID

    # ------------------------------------------------------------------
    # SYNC DE ESTOQUE
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_stock(payload: dict):
        """Normaliza o /stock/fulfillment em (available, in_transit, not_available, total)."""
        available = int(payload.get("available_quantity") or 0)
        total = int(payload.get("total") or 0)
        not_avail_total = int(payload.get("not_available_quantity") or 0)
        in_transit = 0
        for d in payload.get("not_available_detail", []) or []:
            if d.get("status") == "transfer":
                in_transit += int(d.get("quantity") or 0)
        # indisponível "real" (retido/avariado) exclui o que está apenas em trânsito
        not_available = max(0, not_avail_total - in_transit)
        if total == 0:
            total = available + in_transit + not_available
        return available, in_transit, not_available, total

    @staticmethod
    def _daily_sales(ad: Ad) -> float:
        s30 = getattr(ad, "sales_30d", None) or 0
        return (s30 / 30.0) if s30 and s30 > 0 else 0.0

    def _oldest_stock_days(self, seller_id, inventory_id, available):
        """
        Aproxima a antiguidade do lote mais velho ainda em estoque, reconstruindo
        FIFO a partir das recepções (inbound_reception). Best-effort: se a API de
        operações não responder, devolve None (sem sobretaxa de estoque antigo).
        """
        if available <= 0:
            return None
        today = datetime.date.today()
        ops = self.meli.get_fulfillment_operations(
            seller_id=seller_id, inventory_id=inventory_id,
            # The Full operations API only accepts windows shorter than 60 days.
            # A 180-day lookup was returning 400 for every inventory and made
            # the real ageing signal unavailable.
            date_from=(today - datetime.timedelta(days=59)).isoformat(),
            date_to=today.isoformat(), op_type="INBOUND_RECEPTION")
        recs = []
        for o in ops or []:
            # The fallback request may return all operations; only receipts can
            # establish the age of stock currently in the FC.
            if str(o.get("type") or "").lower() != "inbound_reception":
                continue
            qty = int(o.get("quantity") or (o.get("detail") or {}).get("quantity") or 0)
            dt = o.get("date_created") or o.get("date") or o.get("date_time")
            if dt and qty > 0:
                recs.append((str(dt)[:10], qty))
        if not recs:
            return None
        # da recepção mais recente para a mais antiga; acumula até cobrir o disponível
        recs.sort(key=lambda x: x[0], reverse=True)
        cum, oldest_date = 0, recs[-1][0]
        for d, q in recs:
            cum += q
            oldest_date = d
            if cum >= available:
                break
        try:
            return (today - datetime.date.fromisoformat(oldest_date)).days
        except Exception:
            return None

    def sync_full_inventory(self, include_ageing: bool = False):
        """Sync Full inventory; the rate-limited ageing history is opt-in."""
        seller_id = self.get_seller_id()
        today = datetime.date.today()
        ads = self.db.query(Ad).filter(Ad.is_full == True).all()  # noqa: E712
        logger.info(f"[Full] {len(ads)} anúncios marcados como Full.")

        processed = 0
        dimensions_updated = 0
        for ad in ads:
            try:
                item = self.meli.get_item(ad.id)
                dimensions = MeliApiService.extract_shipping_dimensions(item)
                if dimensions:
                    current = (ad.length_mm, ad.width_mm, ad.height_mm)
                    if current != dimensions:
                        ad.length_mm, ad.width_mm, ad.height_mm = dimensions
                        dimensions_updated += 1
                inv_pairs = MeliApiService.extract_inventory_ids(item)
                if not inv_pairs:
                    logger.debug(f"[Full] {ad.id} sem inventory_id no payload.")
                    self.db.commit()  # persist real dimensions without an inventory_id
                    continue

                for inventory_id, variation_id in inv_pairs:
                    payload = self.meli.get_fulfillment_stock(inventory_id)
                    if not payload:
                        continue
                    available, in_transit, not_available, total = self._parse_stock(payload)
                    dsales = self._daily_sales(ad)
                    days_of_stock = round(available / dsales, 1) if dsales > 0 else None
                    oldest = self._oldest_stock_days(seller_id, inventory_id, available) if include_ageing else None

                    row = self.db.query(FullInventory).filter_by(inventory_id=inventory_id).first()
                    if not row:
                        row = FullInventory(inventory_id=inventory_id)
                        self.db.add(row)
                    row.ad_id = ad.id
                    row.sku = ad.sku
                    row.variation_id = variation_id
                    row.available_qty = available
                    row.in_transit_qty = in_transit
                    row.not_available_qty = not_available
                    row.total_qty = total
                    row.days_of_stock = days_of_stock
                    if include_ageing:
                        row.oldest_stock_days = oldest
                    row.raw = payload

                    # série diária idempotente (1 linha por inventory_id x dia)
                    daily = self.db.query(FullStockDaily).filter_by(
                        inventory_id=inventory_id, day=today).first()
                    if not daily:
                        daily = FullStockDaily(inventory_id=inventory_id, day=today)
                        self.db.add(daily)
                    daily.sku = ad.sku
                    daily.ad_id = ad.id
                    daily.available_qty = available
                    daily.in_transit_qty = in_transit
                    daily.not_available_qty = not_available
                    processed += 1

                self.db.commit()
            except Exception as e:
                self.db.rollback()
                logger.error(f"[Full] falha ao sincronizar {ad.id}: {e}")

        logger.info(f"[Full] sync concluído: {processed} unidades de inventário.")
        return {"ads_full": len(ads), "inventories": processed,
                "dimensions_updated": dimensions_updated, "ageing_requested": include_ageing}

    # ------------------------------------------------------------------
    # MOTOR DE CUSTO REAL
    # ------------------------------------------------------------------
    @staticmethod
    def _volume_liters(ad: Ad):
        if ad.length_mm and ad.width_mm and ad.height_mm:
            return (float(ad.length_mm) * float(ad.width_mm) * float(ad.height_mm)) / 1_000_000.0
        return None

    @staticmethod
    def _match_tariff(volume_l, tariffs):
        for t in tariffs:
            lo = float(t.min_volume_l or 0)
            hi = t.max_volume_l
            if volume_l >= lo and (hi is None or volume_l < float(hi)):
                return t
        return None

    def compute_full_costs(self):
        """
        Aplica full_storage_tariffs sobre o volume REAL do produto e grava os 4 campos
        de armazenagem em ProductFinancialMetric (a costura com ads.py / modal do produto).

        Duas fontes de cobertura/antiguidade:
          - full_stock  : há snapshot do CD (full_inventory) — dias e antiguidade REAIS.
          - est_coverage: sem estoque do CD (leitura do Full ainda gated) — usa a cobertura
                          por vendas (ad.days_of_stock) e sem sobretaxa de estoque antigo.
        A tarifa é sempre REAL (tabela do usuário); só a cobertura pode ser estimada.
        """
        tariffs = self.db.query(FullStorageTariff).filter(FullStorageTariff.active == True)\
            .order_by(FullStorageTariff.min_volume_l).all()  # noqa: E712
        if not tariffs:
            logger.warning("[Full] Sem tarifas ativas em full_storage_tariffs — custo real não calculado.")
            return {"updated": 0, "reason": "no_tariffs"}

        # 1) estoque real do CD, quando disponível (por SKU)
        by_sku = {}
        for r in self.db.query(FullInventory).filter(FullInventory.sku.isnot(None)).all():
            by_sku.setdefault(r.sku, []).append(r)

        # 2) todos os anúncios Full (fallback quando não há snapshot do CD)
        ad_by_sku = {}
        for ad in self.db.query(Ad).filter(Ad.is_full == True, Ad.sku.isnot(None)).all():  # noqa: E712
            ad_by_sku.setdefault(ad.sku, ad)

        skus = set(by_sku) | set(ad_by_sku)
        updated = 0
        counts = {"full_stock": 0, "est_coverage": 0}

        for sku in skus:
            ad = ad_by_sku.get(sku) or self.db.query(Ad).filter(Ad.sku == sku).first()
            if not ad:
                continue
            volume_l = self._volume_liters(ad)
            if volume_l is None:
                logger.debug(f"[Full] SKU {sku} sem dimensões — pula custo real.")
                continue
            tariff = self._match_tariff(volume_l, tariffs)
            if not tariff:
                logger.debug(f"[Full] SKU {sku} volume {volume_l:.1f}L sem faixa de tarifa.")
                continue

            daily_fee = float(tariff.daily_fee or 0)
            inbound_fee = float(tariff.inbound_fee or 0)

            inv_rows = by_sku.get(sku, [])
            # Zero days is a valid CD observation (there is no stock available);
            # it must not silently fall back to the estimated listing coverage.
            days_list = [r.days_of_stock for r in inv_rows if r.days_of_stock is not None]
            oldest_list = [r.oldest_stock_days for r in inv_rows if r.oldest_stock_days]
            if days_list:
                avg_days = sum(days_list) / len(days_list)
                source = "full_stock"
            else:
                avg_days = float(ad.days_of_stock or 30)   # cobertura por vendas (estimada)
                source = "est_coverage"
            oldest = max(oldest_list) if oldest_list else None
            counts[source] += 1

            # custo unitário amortizado (metade da cobertura, igual ao estimador de ads.py:651)
            storage_cost = round(daily_fee * (float(avg_days) / 2.0) + inbound_fee, 2)

            storage_risk = 0.0
            thr = int(tariff.aged_days_threshold or 90)
            factor = float(tariff.aged_daily_factor or 3.0)
            if oldest and oldest > thr:  # sobretaxa só com antiguidade REAL do CD
                storage_risk = round((oldest - thr) * daily_fee * factor, 2)

            metric = self.db.query(ProductFinancialMetric).filter_by(sku=sku).first()
            if not metric:
                metric = ProductFinancialMetric(sku=sku)
                self.db.add(metric)
            metric.daily_storage_fee = daily_fee
            metric.inbound_freight_cost = inbound_fee
            metric.storage_cost = storage_cost
            metric.storage_risk_cost = storage_risk
            metric.last_calculated_at = datetime.datetime.utcnow()
            updated += 1

        self.db.commit()
        logger.info(f"[Full] custo gravado em {updated} SKUs "
                    f"(CD real: {counts['full_stock']}, cobertura estimada: {counts['est_coverage']}).")
        return {"updated": updated, **counts}

    def sync_and_cost(self, include_ageing: bool = False):
        """Roda o sync de estoque e, em seguida, o motor de custo. Usado no job diário."""
        stock = self.sync_full_inventory(include_ageing=include_ageing)
        cost = self.compute_full_costs()
        return {"stock": stock, "cost": cost}
