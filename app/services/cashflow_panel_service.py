"""Painel read-only que separa margem operacional de pressão de caixa."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.ad import Ad
from app.models.financial import FixedCost
from app.models.ml_ads_item_daily import MlAdsItemDaily
from app.models.ml_order import MlOrder, MlOrderItem
from app.services.financial_classification import is_debt_service
from app.services.financial_service import FinancialService


TZ_BR = timezone(timedelta(hours=-3))
OPERATING_ORDER_STATUSES = ("paid", "shipped", "delivered")


class CashflowPanelService:
    """Monta uma fotografia auditável, sem gravar dados no banco ou no ML."""

    def __init__(self, db: Session):
        self.db = db

    def get_panel(self, days: int = 30) -> dict:
        days = max(7, min(int(days), 90))
        margin = self._margin_snapshot()
        cashflow = FinancialService(self.db).get_cash_flow_projection(days=days)
        fixed_costs = self.db.query(FixedCost).filter(FixedCost.active == True).all()  # noqa: E712

        debt_costs = [cost for cost in fixed_costs if is_debt_service(cost.category)]
        operational_costs = [cost for cost in fixed_costs if not is_debt_service(cost.category)]
        debt_by_date = self._scheduled_costs(debt_costs, days)
        operational_by_date = self._scheduled_costs(operational_costs, days)

        timeline = []
        total_inflow = total_outflow = purchase_commitments = 0.0
        total_operating_fixed = total_debt_service = 0.0
        minimum_accumulated = 0.0

        for item in cashflow:
            date = item["date"]
            purchases = sum(
                float(detail.get("value") or 0)
                for detail in item["details"]
                if detail.get("type") == "purchase"
            )
            operating_fixed = operational_by_date.get(date, 0.0)
            debt_service = debt_by_date.get(date, 0.0)
            inflow = float(item["inflow"] or 0)
            outflow = float(item["outflow"] or 0)
            net_change = inflow - outflow

            total_inflow += inflow
            total_outflow += outflow
            purchase_commitments += purchases
            total_operating_fixed += operating_fixed
            total_debt_service += debt_service
            minimum_accumulated = min(minimum_accumulated, float(item["accumulated"] or 0))
            timeline.append({
                "date": date,
                "inflow": round(inflow, 2),
                "operating_fixed": round(operating_fixed, 2),
                "debt_service": round(debt_service, 2),
                "purchases": round(purchases, 2),
                "outflow": round(outflow, 2),
                "net_change": round(net_change, 2),
                "accumulated_change": round(float(item["accumulated"] or 0), 2),
                "details": item["details"],
            })

        cash_before_debt = total_inflow - total_operating_fixed - purchase_commitments
        debt_coverage_ratio = (
            cash_before_debt / total_debt_service if total_debt_service > 0 else None
        )
        warnings = list(margin["warnings"])
        warnings.append(
            "O fluxo usa a projeção de recebimento já existente (75% das vendas previstas). "
            "Ele mostra variação de caixa; sem saldo bancário inicial não confirma saldo final."
        )
        if not debt_costs:
            warnings.append(
                "Nenhuma obrigação de caixa foi classificada como 'Serviço da dívida'. "
                "Cadastre ou recategorize as parcelas para medir a cobertura."
            )

        return {
            "generated_at": datetime.now(TZ_BR).isoformat(),
            "period_days": days,
            "margin": margin,
            "cash": {
                "projected_inflow": round(total_inflow, 2),
                "projected_outflow": round(total_outflow, 2),
                "operating_fixed_due": round(total_operating_fixed, 2),
                "debt_service_due": round(total_debt_service, 2),
                "purchase_commitments": round(purchase_commitments, 2),
                "cash_before_debt": round(cash_before_debt, 2),
                "projected_net_change": round(total_inflow - total_outflow, 2),
                "minimum_accumulated_change": round(minimum_accumulated, 2),
                "debt_coverage_ratio": round(debt_coverage_ratio, 2) if debt_coverage_ratio is not None else None,
                "status": self._cash_status(debt_coverage_ratio, total_debt_service),
            },
            "obligations": {
                "monthly_debt_service": round(sum(float(cost.amount or 0) for cost in debt_costs), 2),
                "debt_items": [self._cost_to_dict(cost) for cost in debt_costs],
                "operating_fixed_monthly": round(sum(float(cost.amount or 0) for cost in operational_costs), 2),
            },
            "timeline": timeline,
            "audit": {
                "sources": [
                    "ml_orders + ml_order_items: receita e margem de contribuição por SKU",
                    "ads: margem de contribuição atual do SKU",
                    "ml_ads_item_daily: gasto real de Product Ads",
                    "financial_costs: vencimentos operacionais e serviço da dívida",
                    "purchase_orders: compras abertas por data esperada",
                ],
                "warnings": warnings,
            },
        }

    def _margin_snapshot(self) -> dict:
        cutoff = datetime.utcnow() - timedelta(days=30)
        order_lines = self.db.query(
            MlOrderItem.sku,
            MlOrderItem.quantity,
            MlOrderItem.unit_price,
        ).join(MlOrder, MlOrder.ml_order_id == MlOrderItem.ml_order_id).filter(
            MlOrder.date_created >= cutoff,
            MlOrder.status.in_(OPERATING_ORDER_STATUSES),
        ).all()

        # Um SKU pode ter variações de anúncio. A primeira margem disponível é a
        # referência atual, por isso a cobertura fica explícita no retorno.
        margin_by_sku = {}
        for ad in self.db.query(Ad).filter(Ad.sku.isnot(None), Ad.margin_percent.isnot(None)).all():
            margin_by_sku.setdefault(ad.sku, float(ad.margin_percent))

        revenue = contribution = covered_revenue = uncovered_revenue = 0.0
        for line in order_lines:
            line_revenue = float(line.quantity or 0) * float(line.unit_price or 0)
            revenue += line_revenue
            margin_pct = margin_by_sku.get(line.sku)
            if margin_pct is None:
                uncovered_revenue += line_revenue
                continue
            covered_revenue += line_revenue
            contribution += line_revenue * margin_pct / 100.0

        today_br = datetime.now(TZ_BR).date()
        ads_spend = float(self.db.query(func.sum(MlAdsItemDaily.cost)).filter(
            MlAdsItemDaily.date >= today_br - timedelta(days=30),
            MlAdsItemDaily.date <= today_br,
        ).scalar() or 0)
        operating_fixed_monthly = sum(
            float(cost.amount or 0)
            for cost in self.db.query(FixedCost).filter(FixedCost.active == True).all()  # noqa: E712
            if not is_debt_service(cost.category)
        )
        operating_profit = contribution - ads_spend - operating_fixed_monthly
        coverage_pct = covered_revenue / revenue * 100 if revenue else 0.0
        warnings = []
        if not revenue:
            warnings.append("Sem vendas elegíveis nos últimos 30 dias para calcular a margem operacional.")
        if uncovered_revenue:
            warnings.append(
                f"R$ {uncovered_revenue:.2f} de receita não possui margem de contribuição vinculada ao SKU; "
                "o resultado operacional é parcial."
            )

        return {
            "period_days": 30,
            "revenue": round(revenue, 2),
            "contribution": round(contribution, 2),
            "ads_spend": round(ads_spend, 2),
            "operating_fixed": round(operating_fixed_monthly, 2),
            "operating_profit": round(operating_profit, 2),
            "net_margin_pct": round(operating_profit / revenue * 100, 2) if revenue else None,
            "coverage_pct": round(coverage_pct, 2),
            "covered_revenue": round(covered_revenue, 2),
            "uncovered_revenue": round(uncovered_revenue, 2),
            "status": "complete" if revenue and not uncovered_revenue else "partial" if revenue else "unavailable",
            "warnings": warnings,
        }

    def _scheduled_costs(self, costs, days: int) -> dict:
        # Mantém a mesma referência de data de FinancialService.get_cash_flow_projection.
        today = datetime.utcnow().date()
        end_date = today + timedelta(days=days)
        scheduled = {}
        for cost in costs:
            day = int(cost.day_of_month or 1)
            current = today
            while current <= end_date:
                if current.day == day:
                    key = current.isoformat()
                    scheduled[key] = scheduled.get(key, 0.0) + float(cost.amount or 0)
                current += timedelta(days=1)
        return scheduled

    @staticmethod
    def _cost_to_dict(cost: FixedCost) -> dict:
        return {
            "id": cost.id,
            "name": cost.name,
            "amount": round(float(cost.amount or 0), 2),
            "day_of_month": cost.day_of_month,
            "category": cost.category,
        }

    @staticmethod
    def _cash_status(debt_coverage_ratio, debt_service_due: float) -> str:
        if debt_service_due <= 0:
            return "not_configured"
        if debt_coverage_ratio is not None and debt_coverage_ratio >= 1:
            return "covered_in_projection"
        return "pressure_in_projection"
