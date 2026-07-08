"""
AdsDecisionEngine — nível 1 da escada de autonomia (docs/ads-decision-engine.md).

Gera recomendações persistidas (ads_recommendations) a partir dos dados reais
de ml_ads_item_daily, com consciência de:
  - ciclo de vida do anúncio (lançamento tolera ACOS ≈ margem);
  - significância estatística (não decide com amostra pequena);
  - estoque (não recomenda escalar item com risco de ruptura).

Execução no ML SOMENTE via execute_recommendation, que exige
ADS_WRITE_ENABLED=true (env; default false — regra crítica do projeto).
Feedback loop: measure_outcomes compara 7d antes vs 7d depois da execução.
"""
import os
import json
import logging
import datetime

from sqlalchemy import func

logger = logging.getLogger(__name__)

# --- Thresholds aprovados pelo usuário em 2026-07-07 (calibrar via feedback loop) ---
LAUNCH_MAX_AGE_DAYS = 21          # fase lançamento: primeiros 21 dias...
LAUNCH_MAX_UNITS = 30             # ...ou <30 vendas via Ads (para anúncios de até 60 dias)
LAUNCH_UNITS_MAX_AGE_DAYS = 60
GROWTH_MAX_AGE_DAYS = 90          # até 90 dias = crescimento; depois maturidade
LIQUIDATION_MIN_DAYS_OF_STOCK = 120  # estoque p/ 120+ dias = liquidação (acelerar giro)
MIN_CLICKS_SIGNIFICANCE = 30      # mínimo de evidência antes de recomendar
MIN_SPEND_SIGNIFICANCE = 30.0     # ou R$30 gastos
STOCK_GUARD_MIN_DAYS = 14         # nunca recomendar "aumentar" com menos de 14 dias de estoque
RECOMMENDATION_TTL_DAYS = 7       # pendente some após 7 dias sem decisão
DECISION_COOLDOWN_DAYS = 14       # não recriar item+ação decidido (executado/rejeitado) há menos de 14 dias

# ACOS-alvo como fração da margem, por fase
ACOS_TARGET_BY_STAGE = {
    "lancamento": 1.0,
    "crescimento": 0.7,
    "maturidade": 0.5,
    "liquidacao": 1.0,
}

EXECUTABLE_ACTIONS = {"pausar"}   # única ação executável automaticamente no nível 1

# Meta de margem LÍQUIDA pós-tudo (contribuição - Ads - custos fixos) para
# crescimento saudável em marketplace. 8% = default; configurável via
# system_config key 'ads_target_net_margin'. Racional: <5% qualquer soluço
# (devolução, atraso de repasse) quebra o ciclo de recompra; >15% em fase de
# crescimento normalmente significa subinvestir em Ads/estoque.
DEFAULT_TARGET_NET_MARGIN = 8.0
SCALE_HEADROOM_FACTOR = 0.6       # "aumentar" exige ACOS <= 60% do teto (folga p/ crescer sem estourar)


def get_finance_context(db) -> dict:
    """
    Fotografia financeira da empresa usada nas decisões de Ads:
      fixed_burden_pct — quanto da receita os custos fixos consomem hoje
      target_net_pct   — meta de margem líquida pós-tudo (crescimento saudável)
      otb_value        — verba disponível para recompra (guard: não escalar Ads
                         de item que não conseguimos reabastecer)
      complete=False   — sem contas fixas cadastradas ou sem receita: o motor
                         cai no modo antigo (bandas sobre a margem de contribuição).
    """
    from app.models.financial import FixedCost
    from app.models.ml_order import MlOrder, MlOrderItem
    from app.models.system_config import SystemConfig
    from sqlalchemy import func as sqlfunc

    ctx = {
        "fixed_monthly": 0.0,
        "revenue_30d": 0.0,
        "fixed_burden_pct": None,
        "target_net_pct": DEFAULT_TARGET_NET_MARGIN,
        "otb_value": None,
        "complete": False,
    }
    try:
        fixed_monthly = float(db.query(sqlfunc.sum(FixedCost.amount)).filter(
            FixedCost.active == True  # noqa: E712
        ).scalar() or 0)

        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        revenue_30d = float(db.query(
            sqlfunc.sum(MlOrderItem.quantity * MlOrderItem.unit_price)
        ).join(MlOrder, MlOrder.ml_order_id == MlOrderItem.ml_order_id).filter(
            MlOrder.date_created >= cutoff,
            MlOrder.status.in_(["paid", "shipped", "delivered"]),
        ).scalar() or 0)

        try:
            sc = db.query(SystemConfig).filter_by(key="ads_target_net_margin").first()
            if sc and sc.value:
                ctx["target_net_pct"] = float(sc.value)
        except Exception:
            pass  # config opcional — mantém default

        ctx["fixed_monthly"] = round(fixed_monthly, 2)
        ctx["revenue_30d"] = round(revenue_30d, 2)
        if fixed_monthly > 0 and revenue_30d > 0:
            ctx["fixed_burden_pct"] = round(fixed_monthly / revenue_30d * 100, 2)
            ctx["complete"] = True

        try:
            from app.services.financial_service import FinancialService
            otb = FinancialService(db).calculate_otb()
            ctx["otb_value"] = round(float(otb.get("otb_value") or 0), 2)
        except Exception as e:
            logger.warning(f"OTB indisponível para contexto de Ads (não-fatal): {e}")
    except Exception as e:
        logger.warning(f"Contexto financeiro indisponível (não-fatal): {e}")
    return ctx


def max_acos_for(contribution_pct, finance_ctx, stage: str = "maturidade"):
    """
    Teto de ACOS que ainda entrega a meta de crescimento:
      teto = margem de contribuição - custos fixos % - meta líquida %
    Fases lançamento/liquidação abrem mão da meta líquida (investem o lucro
    em ranking/giro), mas nunca do break-even pós-fixos.
    Retorna None quando não há dados financeiros completos.
    """
    if not finance_ctx or not finance_ctx.get("complete") or contribution_pct is None:
        return None
    burden = finance_ctx["fixed_burden_pct"]
    target = finance_ctx["target_net_pct"]
    if stage in ("lancamento", "liquidacao"):
        ceiling = contribution_pct - burden
    else:
        ceiling = contribution_pct - burden - target
    return round(max(0.0, ceiling), 2)


def ads_write_enabled() -> bool:
    return os.getenv("ADS_WRITE_ENABLED", "false").lower() == "true"


def _classify(spend, ads_revenue, acos, margin_percent, max_acos=None, fixed_burden_pct=None):
    """
    margin_percent = margem de CONTRIBUIÇÃO (pós comissão/frete/imposto/custo,
    ANTES de Ads e custos fixos). Com dados financeiros (max_acos), as bandas
    são ancoradas na margem LÍQUIDA real; sem eles, cai nas bandas antigas.
    """
    if spend > 0 and ads_revenue <= 0:
        return "queimando"

    # --- Modo finance-aware: teto de ACOS = contribuição - fixos - meta ---
    if max_acos is not None and acos is not None and margin_percent:
        if acos >= margin_percent:
            return "prejuizo"          # perde dinheiro antes mesmo dos fixos
        if fixed_burden_pct is not None and acos >= margin_percent - fixed_burden_pct:
            return "prejuizo"          # líquida real negativa (fixos não fecham)
        if acos >= max_acos:
            return "atencao"           # paga as contas mas come a meta de crescimento
        if acos <= max_acos * SCALE_HEADROOM_FACTOR:
            return "escalar"
        return "saudavel"

    # --- Fallback: bandas sobre a margem de contribuição ---
    if margin_percent is not None and margin_percent > 0 and acos is not None:
        if acos >= margin_percent:
            return "prejuizo"
        if acos >= margin_percent * 0.7:
            return "atencao"
        if acos <= margin_percent * 0.4:
            return "escalar"
        return "saudavel"
    # Margem desconhecida: bandas fixas conservadoras de ACOS
    if acos is None:
        return "saudavel"
    if acos >= 25:
        return "atencao"
    if acos <= 10:
        return "escalar"
    return "saudavel"


def _suggest_action(classification, spend, ads_revenue, acos, margin_percent, days_active, period_days,
                    max_acos=None, fixed_burden_pct=None, target_net_pct=None):
    """Sugestão read-only por item (nível 0 — usada pela página Ads Intelligence)."""
    monthly_spend = (spend / days_active * 30) if days_active > 0 else 0.0
    finance_aware = max_acos is not None and fixed_burden_pct is not None

    # Margem líquida REAL do item vendido via Ads: contribuição - ACOS - fixos
    net_pct = None
    if finance_aware and margin_percent is not None and acos is not None:
        net_pct = round(margin_percent - acos - fixed_burden_pct, 2)

    if classification == "queimando":
        return {
            "code": "pausar",
            "label": "Pausar Ads deste item",
            "reason": f"Gastou R${spend:.2f} em {days_active} dia(s) sem NENHUMA venda via Ads no período.",
            "impact": f"Economia estimada de R${monthly_spend:.2f}/mês",
        }
    if classification == "prejuizo":
        loss = ads_revenue * (margin_percent / 100.0) - spend if margin_percent else -spend
        if net_pct is not None and acos < (margin_percent or 0):
            reason = (f"Margem líquida REAL {net_pct:.1f}% negativa: contribuição {margin_percent:.1f}% "
                      f"− ACOS {acos:.1f}% − custos fixos {fixed_burden_pct:.1f}% — a venda existe mas não paga as contas.")
        else:
            reason = f"ACOS {acos:.1f}% >= margem {margin_percent:.1f}% — cada venda via Ads dá prejuízo (resultado no período: R${loss:.2f})."
        return {
            "code": "reduzir_ou_pausar",
            "label": "Reduzir lance/verba ou pausar",
            "reason": reason,
            "impact": f"Estancar perda de ~R${abs(loss) / max(days_active, 1) * 30:.2f}/mês",
        }
    if classification == "atencao":
        if finance_aware and net_pct is not None:
            reason = (f"ACOS {acos:.1f}% acima do teto de {max_acos:.1f}% — sobra líquida de {net_pct:.1f}%, "
                      f"abaixo da meta de {target_net_pct:.1f}% para crescer com saúde.")
        elif margin_percent is not None:
            reason = f"ACOS {acos:.1f}% consome mais de 70% da margem ({margin_percent:.1f}%) — lucro via Ads quase zerado."
        else:
            reason = f"ACOS {acos:.1f}% elevado e margem do produto desconhecida — cadastre o custo para avaliar."
        return {
            "code": "monitorar",
            "label": "Monitorar de perto / reduzir lance",
            "reason": reason,
            "impact": "Risco de virar prejuízo com pequena piora de CPC",
        }
    if classification == "escalar":
        if finance_aware and net_pct is not None:
            reason = (f"ACOS {acos:.1f}% com teto de {max_acos:.1f}% — líquida real de {net_pct:.1f}% "
                      f"já descontando custos fixos ({fixed_burden_pct:.1f}%) e acima da meta ({target_net_pct:.1f}%).")
        else:
            headroom = (margin_percent - acos) if (margin_percent and acos is not None) else None
            reason = (f"ACOS {acos:.1f}% bem abaixo da margem {margin_percent:.1f}% — folga de {headroom:.1f}pp para escalar."
                      if headroom is not None else f"ACOS {acos:.1f}% baixo com vendas consistentes.")
        return {
            "code": "aumentar",
            "label": "Aumentar investimento",
            "reason": reason,
            "impact": f"Receita via Ads atual R${ads_revenue:.2f} em {period_days}d com espaço para crescer",
        }
    return {
        "code": "manter",
        "label": "Manter como está",
        "reason": ("Líquida real dentro da meta." if finance_aware else "ACOS confortável dentro da margem."),
        "impact": None,
    }


class AdsDecisionEngine:

    def __init__(self, db):
        self.db = db

    # ---------- Ciclo de vida ----------

    def infer_lifecycle(self, ad, units_ads_alltime: int) -> str:
        now = datetime.datetime.utcnow()
        age_days = None
        if ad is not None and ad.start_time is not None:
            start = ad.start_time
            if hasattr(start, 'tzinfo') and start.tzinfo is not None:
                start = start.replace(tzinfo=None)
            age_days = (now - start).days

        if age_days is not None and age_days <= LAUNCH_MAX_AGE_DAYS:
            return "lancamento"
        if units_ads_alltime < LAUNCH_MAX_UNITS and (age_days is None or age_days <= LAUNCH_UNITS_MAX_AGE_DAYS):
            return "lancamento"

        days_of_stock = None
        if ad is not None and ad.days_of_stock is not None:
            days_of_stock = float(ad.days_of_stock)
        if days_of_stock is not None and days_of_stock >= LIQUIDATION_MIN_DAYS_OF_STOCK:
            return "liquidacao"

        if age_days is not None and age_days <= GROWTH_MAX_AGE_DAYS:
            return "crescimento"
        return "maturidade"

    # ---------- Geração de recomendações ----------

    def _decide_action(self, classification, stage, significant, spend, ads_revenue,
                       acos, margin_percent, days_active, period_days, days_of_stock,
                       max_acos=None, finance_ctx=None):
        """
        Converte o diagnóstico em UMA recomendação acionável (ou None), aplicando
        os guardrails de fase, significância, estoque e caixa de recompra (OTB).
        """
        if not significant:
            return None  # aguardar dados

        fc = finance_ctx or {}
        burden = fc.get("fixed_burden_pct") if fc.get("complete") else None
        target = fc.get("target_net_pct") if fc.get("complete") else None

        if classification == "queimando":
            if stage == "lancamento":
                return None  # lançamento compra ranking; tolerar
            return _suggest_action(classification, spend, ads_revenue, acos,
                                   margin_percent, days_active, period_days,
                                   max_acos=max_acos, fixed_burden_pct=burden, target_net_pct=target)

        if classification == "prejuizo":
            # Em lançamento só recomenda se estourar 20% ALÉM da margem
            if stage == "lancamento" and margin_percent and acos is not None and acos < margin_percent * 1.2:
                return None
            return _suggest_action(classification, spend, ads_revenue, acos,
                                   margin_percent, days_active, period_days,
                                   max_acos=max_acos, fixed_burden_pct=burden, target_net_pct=target)

        if classification == "escalar":
            # Guard de estoque: não escalar com risco de ruptura
            if days_of_stock is not None and days_of_stock < STOCK_GUARD_MIN_DAYS:
                return None
            # Guard de caixa: escalar Ads gera venda que exige recompra — sem
            # OTB (verba de compra disponível), crescer aqui quebra o ciclo.
            otb = fc.get("otb_value")
            if otb is not None and otb <= 0:
                logger.info(f"Escalar bloqueado por OTB<=0 (sem verba de recompra).")
                return None
            action = _suggest_action(classification, spend, ads_revenue, acos,
                                     margin_percent, days_active, period_days,
                                     max_acos=max_acos, fixed_burden_pct=burden, target_net_pct=target)
            if stage == "liquidacao":
                action["reason"] += " Item em liquidação (estoque alto) — acelerar giro."
            return action

        # atencao/saudavel: sem recomendação persistida (aparece só na página)
        return None

    def generate_recommendations(self, days: int = 30) -> dict:
        """
        Roda o diagnóstico e materializa recomendações em ads_recommendations.
        Dedup: não recria pendente igual (item+ação). Expira pendentes obsoletas
        (TTL ou diagnóstico mudou). Retorna resumo para notificação.
        """
        from app.models.ml_ads_item_daily import MlAdsItemDaily
        from app.models.ads_recommendation import AdsRecommendation
        from app.models.ad import Ad

        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=days)

        agg = self.db.query(
            MlAdsItemDaily.item_id,
            func.sum(MlAdsItemDaily.cost).label('spend'),
            func.sum(MlAdsItemDaily.revenue).label('ads_revenue'),
            func.sum(MlAdsItemDaily.clicks).label('clicks'),
            func.count(MlAdsItemDaily.id).label('days_active'),
        ).filter(
            MlAdsItemDaily.date >= start_date
        ).group_by(MlAdsItemDaily.item_id).all()

        if not agg:
            return {"created": [], "expired": 0, "skipped": 0, "no_data": True}

        item_ids = [r.item_id for r in agg]
        ads_map = {a.id: a for a in self.db.query(Ad).filter(Ad.id.in_(item_ids)).all()}

        # Unidades via Ads acumuladas (todo o histórico) para o ciclo de vida
        units_alltime = dict(self.db.query(
            MlAdsItemDaily.item_id, func.sum(MlAdsItemDaily.units_quantity)
        ).filter(MlAdsItemDaily.item_id.in_(item_ids)).group_by(MlAdsItemDaily.item_id).all())

        finance_ctx = get_finance_context(self.db)
        if finance_ctx["complete"]:
            logger.info(f"Motor de Ads com contexto financeiro: fixos R${finance_ctx['fixed_monthly']:.2f}/mês "
                        f"= {finance_ctx['fixed_burden_pct']:.1f}% da receita 30d; meta líquida {finance_ctx['target_net_pct']:.1f}%.")
        else:
            logger.info("Motor de Ads SEM contexto financeiro (cadastre custos fixos) — usando bandas de contribuição.")

        pending = self.db.query(AdsRecommendation).filter(
            AdsRecommendation.status == "pending"
        ).all()
        pending_by_key = {(p.item_id, p.action_code): p for p in pending}

        # Cooldown: decisões recentes (executada, aceita ou rejeitada) valem por
        # 14 dias — o gasto antigo ainda na janela não deve recriar a mesma
        # recomendação, nem desrespeitar um "não" do usuário.
        cooldown_cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=DECISION_COOLDOWN_DAYS)
        recent_decided = self.db.query(AdsRecommendation).filter(
            AdsRecommendation.status.in_(["executed", "accepted", "rejected", "failed"]),
            AdsRecommendation.decided_at >= cooldown_cutoff,
        ).all()
        cooldown_keys = {(d.item_id, d.action_code) for d in recent_decided}

        created = []
        current_keys = set()

        for r in agg:
            spend = float(r.spend or 0)
            ads_revenue = float(r.ads_revenue or 0)
            clicks = int(r.clicks or 0)
            days_active = int(r.days_active or 0)
            if spend <= 0 and ads_revenue <= 0:
                continue

            ad = ads_map.get(r.item_id)
            margin_percent = float(ad.margin_percent) if (ad and ad.margin_percent is not None) else None
            days_of_stock = float(ad.days_of_stock) if (ad and ad.days_of_stock is not None) else None
            acos = round(spend / ads_revenue * 100, 2) if ads_revenue > 0 else None

            stage = self.infer_lifecycle(ad, int(units_alltime.get(r.item_id) or 0))
            m_acos = max_acos_for(margin_percent, finance_ctx, stage)
            burden = finance_ctx["fixed_burden_pct"] if finance_ctx["complete"] else None
            classification = _classify(spend, ads_revenue, acos, margin_percent,
                                       max_acos=m_acos, fixed_burden_pct=burden)
            significant = clicks >= MIN_CLICKS_SIGNIFICANCE or spend >= MIN_SPEND_SIGNIFICANCE

            action = self._decide_action(classification, stage, significant, spend,
                                         ads_revenue, acos, margin_percent,
                                         days_active, days, days_of_stock,
                                         max_acos=m_acos, finance_ctx=finance_ctx)
            if not action:
                continue

            key = (r.item_id, action["code"])
            if key in cooldown_keys:
                continue  # decidido recentemente — respeitar cooldown
            current_keys.add(key)
            if key in pending_by_key:
                continue  # já existe pendente igual

            rec = AdsRecommendation(
                item_id=r.item_id,
                action_code=action["code"],
                classification=classification,
                lifecycle_stage=stage,
                reason=action["reason"],
                impact=action.get("impact"),
                metrics_snapshot={
                    "period_days": days, "spend": spend, "ads_revenue": ads_revenue,
                    "clicks": clicks, "acos": acos, "margin_percent": margin_percent,
                    "days_active": days_active, "days_of_stock": days_of_stock,
                    "title": ad.title if ad else None, "sku": ad.sku if ad else None,
                    "max_acos": m_acos,
                    "fixed_burden_pct": burden,
                    "target_net_pct": finance_ctx["target_net_pct"] if finance_ctx["complete"] else None,
                    "otb_value": finance_ctx.get("otb_value"),
                },
                status="pending",
            )
            self.db.add(rec)
            created.append(rec)

        # Expira pendentes obsoletas: TTL vencido OU diagnóstico atual não sustenta mais
        expired = 0
        ttl_cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=RECOMMENDATION_TTL_DAYS)
        for p in pending:
            stale_ttl = p.created_at is not None and p.created_at < ttl_cutoff
            no_longer_valid = (p.item_id, p.action_code) not in current_keys
            if stale_ttl or no_longer_valid:
                p.status = "expired"
                p.decided_at = datetime.datetime.utcnow()
                p.decided_by = "auto"
                expired += 1

        self.db.commit()
        logger.info(f"AdsDecisionEngine: {len(created)} recomendações criadas, {expired} expiradas.")
        return {
            "created": [{
                "id": c.id, "item_id": c.item_id, "action_code": c.action_code,
                "title": (c.metrics_snapshot or {}).get("title"),
                "impact": c.impact,
            } for c in created],
            "expired": expired,
            "skipped": len(pending_by_key),
            "no_data": False,
        }

    # ---------- Execução (nível 1: 1-click humano) ----------

    def execute_recommendation(self, rec) -> tuple:
        """
        Executa uma recomendação ACEITA. Retorna (ok: bool, message: str).
        Regra crítica: só roda com ADS_WRITE_ENABLED=true e só ações do
        catálogo executável (v1: pausar).
        """
        from app.services.meli_api import MeliApiService

        if rec.action_code not in EXECUTABLE_ACTIONS:
            return False, f"Ação '{rec.action_code}' não é executável automaticamente — faça manualmente no painel do ML."
        if not ads_write_enabled():
            return False, "Escrita de Ads desabilitada (ADS_WRITE_ENABLED=false). Recomendação aceita; execute manualmente ou habilite a flag."

        meli = MeliApiService(self.db)
        result = meli.update_product_ad_status(rec.item_id, "paused")
        rec.executed_at = datetime.datetime.utcnow()
        rec.execution_result = json.dumps(result, ensure_ascii=False)[:2000]
        if result.get("ok"):
            rec.status = "executed"
            self.db.commit()
            return True, f"Anúncio {rec.item_id} pausado no Product Ads."
        rec.status = "failed"
        self.db.commit()
        return False, f"Falha ao pausar {rec.item_id}: HTTP {result.get('status_code')} {str(result.get('body'))[:200]}"

    # ---------- Feedback loop ----------

    def measure_outcomes(self, window_days: int = 7) -> int:
        """
        Para recomendações executadas há >= window_days sem outcome medido,
        compara gasto/receita de Ads na janela ANTES vs DEPOIS da execução.
        É o que permite calibrar os thresholds com dados próprios.
        """
        from app.models.ml_ads_item_daily import MlAdsItemDaily
        from app.models.ads_recommendation import AdsRecommendation

        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=window_days)
        recs = self.db.query(AdsRecommendation).filter(
            AdsRecommendation.status == "executed",
            AdsRecommendation.outcome_measured_at.is_(None),
            AdsRecommendation.executed_at <= cutoff,
        ).all()

        measured = 0
        for rec in recs:
            exec_date = rec.executed_at.date()

            def window_sum(d_from, d_to):
                row = self.db.query(
                    func.sum(MlAdsItemDaily.cost), func.sum(MlAdsItemDaily.revenue)
                ).filter(
                    MlAdsItemDaily.item_id == rec.item_id,
                    MlAdsItemDaily.date >= d_from,
                    MlAdsItemDaily.date < d_to,
                ).first()
                return {"spend": round(float(row[0] or 0), 2), "ads_revenue": round(float(row[1] or 0), 2)}

            before = window_sum(exec_date - datetime.timedelta(days=window_days), exec_date)
            after = window_sum(exec_date, exec_date + datetime.timedelta(days=window_days))

            spend_saved = round(before["spend"] - after["spend"], 2)
            revenue_lost = round(before["ads_revenue"] - after["ads_revenue"], 2)
            rec.outcome = {
                "window_days": window_days,
                "before": before,
                "after": after,
                "spend_saved": spend_saved,
                "ads_revenue_lost": revenue_lost,
            }
            rec.outcome_measured_at = datetime.datetime.utcnow()
            measured += 1

        if measured:
            self.db.commit()
            logger.info(f"AdsDecisionEngine: outcome medido para {measured} recomendações.")
        return measured
