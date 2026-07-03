"""
AdsAttributionService — atribui gasto de Product Ads a vendas individuais.

Por que este modelo: o ML entrega gasto agregado por item x dia (nunca por
pedido). A atribuição em camadas é a aproximação mais honesta possível:

  Nível 1 — custo do item NO DIA da venda ÷ unidades do item vendidas no dia.
  Nível 2 — custo do item em dias SEM venda no período ÷ unidades do item
            vendidas no período (residual; garante que o custo não evapora).
  Órfão   — custo de itens com gasto e ZERO vendas no período. Não pertence a
            nenhuma venda; é devolvido separado (orphan_cost) para que o lucro
            total do período continue verdadeiro.

Fonte primária: tabela ml_ads_item_daily (populada pelo sync diário/backfill).
Se o período inclui HOJE (dia ainda sem sync), faz top-up via API live com o
mesmo cache de 15 min que o dashboard já usava.
"""
import json
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

TZ_BR = timezone(timedelta(hours=-3))


class AdsAttributionService:

    def __init__(self, db):
        self.db = db

    def build(self, start_date, end_date, item_day_sold_qty, item_period_sold_qty,
              top_up_today_live=True):
        """
        start_date / end_date: datetime.date (dias no fuso BR, inclusivos)
        item_day_sold_qty: {(item_id, date): qty} vendas válidas por item x dia
        item_period_sold_qty: {item_id: qty} vendas válidas por item no período

        Retorna None quando não há NENHUM dado de Ads no período (caller decide
        fallback), ou um dict com os mapas de atribuição.
        """
        from app.models.ml_ads_item_daily import MlAdsItemDaily

        rows = self.db.query(MlAdsItemDaily).filter(
            MlAdsItemDaily.date >= start_date,
            MlAdsItemDaily.date <= end_date
        ).all()

        item_day_cost = {}
        total_cost = 0.0
        total_ads_revenue = 0.0
        dates_with_data = set()

        for r in rows:
            cost = float(r.cost or 0)
            item_day_cost[(r.item_id, r.date)] = item_day_cost.get((r.item_id, r.date), 0.0) + cost
            total_cost += cost
            total_ads_revenue += float(r.revenue or 0)
            dates_with_data.add(r.date)

        # Top-up de HOJE via API live (dia corrente ainda não passou pelo sync)
        today_br = datetime.now(TZ_BR).date()
        if top_up_today_live and start_date <= today_br <= end_date and today_br not in dates_with_data:
            for r in self._fetch_today_live(today_br):
                item_id = r.get("item_id")
                if not item_id:
                    continue
                cost = float(r.get("cost") or 0)
                amount = float(r.get("amount") or 0)
                if cost <= 0 and amount <= 0:
                    continue
                if cost > 0:
                    item_day_cost[(item_id, today_br)] = item_day_cost.get((item_id, today_br), 0.0) + cost
                    total_cost += cost
                total_ads_revenue += amount
                dates_with_data.add(today_br)

        if not item_day_cost:
            return None

        # Nível 1: custo do dia ÷ unidades vendidas do item no dia
        per_unit_day = {}
        residual_item_cost = {}
        for (item_id, d), cost in item_day_cost.items():
            qty_day = item_day_sold_qty.get((item_id, d), 0)
            if qty_day > 0:
                per_unit_day[(item_id, d)] = cost / qty_day
            else:
                residual_item_cost[item_id] = residual_item_cost.get(item_id, 0.0) + cost

        # Nível 2: custo residual do item ÷ unidades do item no período
        per_unit_fallback = {}
        orphan_cost = 0.0
        for item_id, cost in residual_item_cost.items():
            qty_period = item_period_sold_qty.get(item_id, 0)
            if qty_period > 0:
                per_unit_fallback[item_id] = cost / qty_period
            else:
                orphan_cost += cost

        return {
            "per_unit_day": per_unit_day,
            "per_unit_fallback": per_unit_fallback,
            "orphan_cost": round(orphan_cost, 2),
            "total_cost": round(total_cost, 2),
            "total_ads_revenue": round(total_ads_revenue, 2),
            "days_with_data": len(dates_with_data),
        }

    def _fetch_today_live(self, today_br):
        """Busca o gasto de hoje na API (cache de 15 min em system_config)."""
        try:
            from app.models.system_config import SystemConfig
            from app.services.meli_api import MeliApiService

            d_str = today_br.strftime("%Y-%m-%d")
            cache_key = f"ads_cache_{d_str}_{d_str}"

            sc = self.db.query(SystemConfig).filter_by(key=cache_key).first()
            if sc and sc.value:
                try:
                    cached_obj = json.loads(sc.value)
                    if (datetime.now().timestamp() - cached_obj.get("timestamp", 0)) < 900:
                        return cached_obj.get("data", [])
                except Exception:
                    pass

            meli = MeliApiService(self.db)
            data = meli.get_ads_performance(None, d_str, d_str, fast=True)
            if data:
                if not sc:
                    sc = SystemConfig(key=cache_key, group='cache')
                    self.db.add(sc)
                sc.value = json.dumps({"timestamp": datetime.now().timestamp(), "data": data})
                self.db.commit()
            return data or []
        except Exception as e:
            logger.warning(f"Ads today live top-up failed (non-fatal): {e}")
            return []
