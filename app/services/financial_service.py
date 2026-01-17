from sqlalchemy import func, and_, case
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.ml_order import MlOrder, MlOrderItem
from app.models.financial import FixedCost, ProductFinancialMetric
from app.models.ad import Ad
from app.models.supply import PurchaseOrder, PurchaseStatus
import logging

logger = logging.getLogger(__name__)

class FinancialService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_metrics(self):
        """
        Calcula métricas financeiras (taxa de devolução e rateio de custos) para todos os SKUs
        com vendas nos últimos 30-90 dias.
        """
        logger.info("Iniciando cálculo de métricas financeiras...")
        
        # 1. Calcular Custo Fixo Total
        total_fixed_cost = self.db.query(func.sum(FixedCost.amount)).filter(FixedCost.active == True).scalar() or 0
        logger.info(f"Custo Fixo Total Mensal da Operação: R$ {total_fixed_cost:.2f}")

        # Definir janelas de tempo
        now = datetime.utcnow()
        last_90d = now - timedelta(days=90)
        last_30d = now - timedelta(days=30)

        # 2. Obter SKUs únicos vendidos nos últimos 90 dias
        # Usamos 90d para ter base de cálculo de devolução mais sólida
        skus = self.db.query(MlOrderItem.sku).join(MlOrder).filter(
            MlOrder.date_created >= last_90d,
            MlOrderItem.sku.isnot(None)
        ).distinct().all()
        
        sku_list = [s[0] for s in skus if s[0]] # Filtrar vazios
        logger.info(f"Processando {len(sku_list)} SKUs ativos recentemente.")

        # 3. Calcular Receita Total da Empresa (30 dias) para Rateio
        # Consideramos apenas vendas concretizadas (paid) para receita
        total_revenue_30d = self.db.query(
            func.sum(MlOrderItem.quantity * MlOrderItem.unit_price)
        ).join(MlOrder).filter(
            MlOrder.date_created >= last_30d,
            MlOrder.status == 'paid'
        ).scalar() or 0
        
        logger.info(f"Faturamento Total (30d): R$ {total_revenue_30d:.2f}")

        for sku in sku_list:
            self._process_sku(sku, total_revenue_30d, total_fixed_cost, last_30d, last_90d)
        
        self.db.commit()
        logger.info("Cálculo financeiro concluído.")

    def _process_sku(self, sku: str, total_revenue_company: float, total_fixed_cost: float, date_30d: datetime, date_90d: datetime):
        """Calcula métricas específicas para um SKU e salva no banco."""
        
        # --- A. Taxa de Devolução (Risco) - Janela 90 dias ---
        # Total de itens vendidos
        total_items_90d = self.db.query(func.sum(MlOrderItem.quantity)).join(MlOrder).filter(
            MlOrderItem.sku == sku,
            MlOrder.date_created >= date_90d
        ).scalar() or 0

        if total_items_90d == 0:
            return # Sem vendas, sem métrica

        # Itens devolvidos/cancelados
        # Consideramos 'cancelled' como proxy de devolução/cancelamento por enquanto
        # TODO: Refinar com status de 'refunded' ou tags de claims se disponível
        returned_items_90d = self.db.query(func.sum(MlOrderItem.quantity)).join(MlOrder).filter(
            MlOrderItem.sku == sku,
            MlOrder.date_created >= date_90d,
            MlOrder.status != 'paid' # Qualquer coisa que não seja pago é problema
        ).scalar() or 0
        
        return_rate = returned_items_90d / total_items_90d

        # Estimativa de Custo de Devolução (Frete Ida + Volta)
        # Se não temos dado real, usamos heurística baseada no preço (ex: 20% do valor) ou fixo
        # Por enquanto vamos fixar um valor base de R$ 20.00 como placeholder de frete reverso
        avg_return_cost = 20.00 

        # --- B. Rateio de Custos Fixos - Janela 30 dias ---
        sku_revenue_30d = self.db.query(
            func.sum(MlOrderItem.quantity * MlOrderItem.unit_price)
        ).join(MlOrder).filter(
            MlOrderItem.sku == sku,
            MlOrder.date_created >= date_30d,
            MlOrder.status == 'paid'
        ).scalar() or 0

        revenue_share = 0.0
        calculated_share_value = 0.0
        
        if total_revenue_company > 0:
            revenue_share = float(sku_revenue_30d) / float(total_revenue_company)
            # O quanto esse SKU deve pagar da conta de luz?
            # Se ele representa 10% do faturamento, ele paga 10% dos custos fixos
            total_share_amount = float(total_fixed_cost) * revenue_share
            
            # Mas queremos o valor UNITÁRIO para embutir no preço
            # Custo Fixo por Unidade = (Total Share) / (Qtd Vendida 30d)
            sku_units_30d = self.db.query(func.sum(MlOrderItem.quantity)).join(MlOrder).filter(
                MlOrderItem.sku == sku,
                MlOrder.date_created >= date_30d,
                MlOrder.status == 'paid'
            ).scalar() or 1 # Evitar div zero
            
            if sku_units_30d > 0:
                calculated_share_value = total_share_amount / sku_units_30d

        # --- C. Persistir ---
        metric = self.db.query(ProductFinancialMetric).filter(ProductFinancialMetric.sku == sku).first()
        if not metric:
            metric = ProductFinancialMetric(sku=sku)
            self.db.add(metric)
        
        metric.return_rate_90d = return_rate
        metric.avg_return_cost = avg_return_cost
        metric.revenue_share_30d = revenue_share
        metric.calculated_fixed_cost_share = calculated_share_value
        metric.last_calculated_at = datetime.utcnow()
        
        # logger.debug(f"SKU {sku}: Return Rate={return_rate:.1%}, Rev Share={revenue_share:.1%}, Fixed Cost Unit=R$ {calculated_share_value:.2f}")

    def calculate_otb(self, days_period=30, target_weeks_supply=4):
        """
        Calcula o Open-to-Buy (Verba Disponível para Compra) Global.
        OTB = (Vendas Previstas + Estoque Final Desejado) - (Estoque Atual + Pedidos em Aberto)
        Retorna valor monetário (R$).
        """
        # 1. Obter Vendas Previstas (R$)
        # Somar (Forecast * Preço) para todos os Ads ativos
        ads = self.db.query(Ad).filter(Ad.status == 'active').all()
        
        projected_revenue = 0.0
        projected_cogs = 0.0 # Cost of Goods Sold
        current_inventory_value = 0.0
        
        for ad in ads:
            # Forecast (simplificado: sales_30d projectado para o periodo)
            daily_sales = (ad.sales_30d or 0) / 30.0
            forecast_qty = daily_sales * days_period
            
            price = ad.price or 0
            cost = ad.cost or 0
            
            projected_revenue += forecast_qty * price
            projected_cogs += forecast_qty * cost
            
            # Estoque Atual (Valuation)
            current_inv = (ad.available_quantity or 0) + (ad.stock_full or 0)
            current_inventory_value += current_inv * cost

        # 2. Estoque Final Desejado (R$)
        # Target Weeks Supply * Weekly COGS
        weekly_cogs = (projected_cogs / days_period) * 7
        target_ending_inventory = weekly_cogs * target_weeks_supply
        
        # 3. Pedidos em Aberto (On Order) (R$)
        on_order_value = self.db.query(func.sum(PurchaseOrder.total_cost))\
            .filter(PurchaseOrder.status.in_([
                PurchaseStatus.SENT, 
                PurchaseStatus.CONFIRMED, 
                PurchaseStatus.SHIPPING
            ])).scalar() or 0.0
            
        # Fórmula OTB (Base Custo)
        # OTB = (COGS Previsto + Estoque Final Desejado) - (Estoque Atual + On Order)
        otb_value = (projected_cogs + target_ending_inventory) - (current_inventory_value + on_order_value)
        
        return {
            "otb_value": max(0, float(otb_value)),
            "projected_sales_value": float(projected_revenue),
            "projected_cogs": float(projected_cogs),
            "target_ending_inventory": float(target_ending_inventory),
            "current_inventory_value": float(current_inventory_value),
            "on_order_value": float(on_order_value),
            "period_days": days_period,
            "calculation_date": datetime.utcnow()
        }

    def get_cash_flow_projection(self, days=30):
        """
        Gera fluxo de caixa projetado diário.
        Inflows: Vendas diárias previstas.
        Outflows: Contas Fixas (no dia de pagamento), Pedidos de Compra (na data esperada).
        """
        today = datetime.utcnow().date()
        end_date = today + timedelta(days=days)
        
        # Inicializar timeline
        timeline = {} # date_str -> {inflow: 0, outflow: 0, distinct_outflows: []}
        
        current = today
        while current <= end_date:
            d_str = current.strftime('%Y-%m-%d')
            timeline[d_str] = {"date": d_str, "inflow": 0.0, "outflow": 0.0, "details": [], "accumulated": 0.0}
            current += timedelta(days=1)
            
        # 1. Inflows (Vendas Projetadas)
        ads = self.db.query(Ad).filter(Ad.status == 'active').all()
        daily_revenue = 0.0
        for ad in ads:
             daily_sales = (ad.sales_30d or 0) / 30.0
             daily_revenue += daily_sales * (ad.price or 0)
        
        avg_net_rate = 0.75 # 75% sobra após taxas
        estimated_daily_inflow = daily_revenue * avg_net_rate
        
        for d_str in timeline:
            timeline[d_str]["inflow"] += estimated_daily_inflow
            
        # 2. Outflows (Fixed Costs)
        fixed_costs = self.db.query(FixedCost).filter(FixedCost.active == True).all()
        
        for cost in fixed_costs:
            day = cost.day_of_month or 1
            check_date = today
            while check_date <= end_date:
                if check_date.day == day:
                    d_str = check_date.strftime('%Y-%m-%d')
                    if d_str in timeline:
                        timeline[d_str]["outflow"] += float(cost.amount)
                        timeline[d_str]["details"].append({"name": cost.name, "value": float(cost.amount), "type": "fixed"})
                check_date += timedelta(days=1)
        
        # 3. Outflows (Purchases)
        orders = self.db.query(PurchaseOrder).filter(
            PurchaseOrder.status.in_([PurchaseStatus.SENT, PurchaseStatus.CONFIRMED, PurchaseStatus.SHIPPING])
        ).all()
        
        for order in orders:
            due_date = order.expected_date
            if due_date:
                # Ensure due_date is date object
                if isinstance(due_date, datetime):
                    due_date = due_date.date()
                    
                if today <= due_date <= end_date:
                    d_str = due_date.strftime('%Y-%m-%d')
                    if d_str in timeline:
                        val = float(order.total_cost or 0) + float(order.additional_costs or 0)
                        timeline[d_str]["outflow"] += val
                        timeline[d_str]["details"].append({"name": f"Pedido #{order.id}", "value": val, "type": "purchase"})

        # Converter para lista ordenada
        result = sorted(timeline.values(), key=lambda x: x['date'])
        
        # Calcular Acumulado
        accumulated = 0.0
        for item in result:
            net = item["inflow"] - item["outflow"]
            accumulated += net
            item["accumulated"] = accumulated
            
        return result

