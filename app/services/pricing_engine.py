from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.ml_metrics_daily import MlMetricsDaily
from app.models.ad import Ad
from app.models.system_config import SystemConfig
import numpy as np

class PricingEngine:
    def __init__(self, db: Session):
        self.db = db

    def get_repricer_config(self) -> dict:
        """
        Loads repricer parameters from SystemConfig (group='repricer'), falling back
        to the defaults declared in app.api.endpoints.settings.DEFAULT_SETTINGS.
        This is the SINGLE source of truth for step sizing — used both by the
        preview/simulation (this file) and by the scheduled execution job
        (app/jobs/pricing_job.py), so the two never diverge.
        """
        from app.api.endpoints.settings import DEFAULT_SETTINGS
        config = dict(DEFAULT_SETTINGS["repricer"])

        rows = self.db.query(SystemConfig).filter(SystemConfig.group == "repricer").all()
        for row in rows:
            if row.key not in config:
                continue
            expected_type = type(config[row.key])
            try:
                if expected_type == bool:
                    config[row.key] = row.value.lower() in ("true", "1", "yes")
                elif expected_type == int:
                    config[row.key] = int(float(row.value))
                else:
                    config[row.key] = float(row.value)
            except (ValueError, TypeError):
                pass
        return config

    def calculate_elasticity(self, item_id: str, days: int = 30):
        """
        Calculates Price Elasticity of Demand (PED) for a given item.
        Returns a dictionary with the score, classification, and suggestion.
        """
        cutoff_date = datetime.utcnow().date() - timedelta(days=days)
        
        # 1. Fetch History
        history = self.db.query(
            MlMetricsDaily.date,
            MlMetricsDaily.avg_price,
            MlMetricsDaily.sales_qty
        ).filter(
            MlMetricsDaily.item_id == item_id,
            MlMetricsDaily.date >= cutoff_date,
            MlMetricsDaily.sales_qty > 0  # Filter days with sales for velocity calc
        ).order_by(MlMetricsDaily.date).all()

        if len(history) < 5:
            return {
                "score": None,
                "label": "Dados Insuficientes",
                "suggestion": "Aguarde mais histórico de vendas."
            }

        # 2. Group by Price (Binning)
        # Round price to nearest whole number to group variations like 100.00 and 100.50
        price_points = {}
        for day in history:
            price = float(day.avg_price) if day.avg_price else 0
            if price == 0: continue
            
            rounded_price = round(price)
            if rounded_price not in price_points:
                price_points[rounded_price] = []
            price_points[rounded_price].append(day.sales_qty)

        if len(price_points) < 2:
            return {
                "score": None,
                "label": "Preço Estável",
                "suggestion": "Não houve variação de preço para calcular elasticidade."
            }

        # 3. Calculate Average Velocity per Price Point
        data = []
        for p, sales_list in price_points.items():
            avg_daily_sales = sum(sales_list) / len(sales_list)
            data.append({"price": p, "velocity": avg_daily_sales})

        # Sort by price ascending
        data.sort(key=lambda x: x["price"])

        # 4. Compare High vs Low Price (Simplified Arc Elasticity or Point Elasticity)
        # We take the lowest price and the highest price to see the major impact
        low_point = data[0]
        high_point = data[-1]

        p1, q1 = low_point["price"], low_point["velocity"]
        p2, q2 = high_point["price"], high_point["velocity"]

        # % Change in Quantity / % Change in Price
        pct_change_q = (q2 - q1) / q1 if q1 > 0 else 0
        pct_change_p = (p2 - p1) / p1 if p1 > 0 else 0

        if pct_change_p == 0:
             return {"score": 0, "label": "Erro", "suggestion": "Variação de preço nula."}

        elasticity = abs(pct_change_q / pct_change_p)

        # 5. Interpret Elasticity
        if elasticity > 1.5:
             label = "Elástica (Sensível)"
             suggestion = "Cuidado ao subir preço. Demanda cai muito rápido."
             action = "HOLD_OR_LOWER"
        elif elasticity < 0.8:
             label = "Inelástica (Resistente)"
             suggestion = "Oportunidade! Subir preço provavelmente aumentará o lucro."
             action = "RAISE"
        else:
             label = "Unitária (Equilibrada)"
             suggestion = "Preço ideal próximo. Monitore a margem."
             action = "OPTIMIZE_MARGIN"
             
        return {
            "score": round(elasticity, 2),
            "label": label,
            "suggestion": suggestion,
            "action": action,
            "analysis": f"Ao subir de R$ {p1} para R$ {p2}, a venda média mudou de {round(q1,1)} para {round(q2,1)}/dia."
        }

    def calculate_conversion_threshold(self, item_id: str, days: int = 90):
        """
        Calculates the minimum acceptable conversion rate for a product.
        Uses historical data if available, otherwise falls back to ML benchmark (1.5%).
        
        Returns:
            dict with threshold, method used, and explanation
        """
        ML_BENCHMARK = 1.5  # Média do Mercado Livre
        
        cutoff_date = datetime.utcnow().date() - timedelta(days=days)
        
        # Fetch historical conversion data
        history = self.db.query(
            MlMetricsDaily.date,
            MlMetricsDaily.visits,
            MlMetricsDaily.sales_qty
        ).filter(
            MlMetricsDaily.item_id == item_id,
            MlMetricsDaily.date >= cutoff_date,
            MlMetricsDaily.visits > 0
        ).all()
        
        if len(history) < 14:  # Need at least 2 weeks of data
            return {
                "threshold": ML_BENCHMARK,
                "method": "benchmark",
                "explanation": f"Sem histórico suficiente. Usando média do Mercado Livre: {ML_BENCHMARK}%",
                "days_analyzed": len(history)
            }
        
        # Calculate daily conversion rates
        conversion_rates = []
        for day in history:
            if day.visits > 0:
                rate = (day.sales_qty / day.visits) * 100
                conversion_rates.append(rate)
        
        if not conversion_rates:
            return {
                "threshold": ML_BENCHMARK,
                "method": "benchmark",
                "explanation": f"Dados insuficientes. Usando média do Mercado Livre: {ML_BENCHMARK}%",
                "days_analyzed": 0
            }
        
        # Calculate mean and standard deviation
        mean_conv = float(np.mean(conversion_rates))
        std_conv = float(np.std(conversion_rates))
        
        # Threshold = mean - 1 std, but never below benchmark
        calculated_threshold = max(ML_BENCHMARK, mean_conv - std_conv)
        
        return {
            "threshold": round(calculated_threshold, 2),
            "method": "historical",
            "mean": round(mean_conv, 2),
            "std": round(std_conv, 2),
            "explanation": f"Calculado do histórico: média {mean_conv:.1f}% - 1σ ({std_conv:.1f}%) = {calculated_threshold:.1f}%",
            "days_analyzed": len(history)
        }

    def calculate_safe_price_steps(self, item_id: str, current_price: float, target_price: float):
        """
        Calculates safe price adjustment steps based on ticket value and product elasticity.

        - Ticket baixo (preço < low_ticket_threshold): step fixo em R$/dia
        - Ticket alto: step em % por dia, conforme elasticidade
            - Elástica (>1.5): step pequeno (sensível à subida)
            - Unitária (0.8-1.5): step médio
            - Inelástica (<0.8): step maior (resistente, pode subir mais rápido)
        - max_step_percent é um teto de segurança absoluto, sempre respeitado.

        Todos os parâmetros vêm de get_repricer_config() (configuráveis em
        Configurações > Repricer) — esta é a ÚNICA função que decide o tamanho do
        step, tanto para a prévia (aqui) quanto para a execução real (pricing_job.py).

        Returns list of price steps with dates and reasons.
        """
        config = self.get_repricer_config()
        elasticity_data = self.calculate_elasticity(item_id)
        elasticity_score = elasticity_data.get("score")

        is_low_ticket = current_price < config["low_ticket_threshold"]

        if is_low_ticket:
            step_mode = "fixed"
            step_value = config["low_ticket_step_value"]
            reason_base = f"Ticket baixo (< R$ {config['low_ticket_threshold']:.2f}): +R$ {step_value:.2f}/dia"
        else:
            if elasticity_score is None:
                step_pct = config["step_pct_unitary"]
                elasticity_label = "indefinida (sem dados suficientes)"
            elif elasticity_score > 1.5:
                step_pct = config["step_pct_elastic"]
                elasticity_label = "elástica (sensível)"
            elif elasticity_score < 0.8:
                step_pct = config["step_pct_inelastic"]
                elasticity_label = "inelástica (resistente)"
            else:
                step_pct = config["step_pct_unitary"]
                elasticity_label = "unitária (equilibrada)"

            step_pct = min(step_pct, config["max_step_percent"])
            step_mode = "percent"
            step_value = step_pct
            reason_base = f"Ticket alto, elasticidade {elasticity_label}: +{step_pct:.1f}%/dia"

        # Calculate steps from current to target
        steps = []
        price = current_price
        step_num = 0
        base_date = datetime.utcnow().date()

        if target_price > current_price:
            while price < target_price and step_num < 200:  # Safety break (200 steps max)
                step_num += 1

                if step_mode == "fixed":
                    new_price = price + step_value
                else:
                    new_price = price * (1 + step_value / 100.0)

                if new_price >= target_price - 0.005:
                    new_price = target_price

                step_date = base_date + timedelta(days=step_num * 1)  # 1 day per step

                steps.append({
                    "step": step_num,
                    "date": step_date.strftime("%Y-%m-%d"),
                    "date_display": step_date.strftime("%d/%m"),
                    "price": round(new_price, 2),
                    "increase_pct": round(((new_price - current_price) / current_price) * 100, 2),
                    "reason": reason_base if step_num == 1 else f"Step {step_num}"
                })

                price = new_price
                if price >= target_price:
                    break

        return {
            "steps": steps,
            "step_mode": step_mode,
            "step_value": step_value,
            "is_low_ticket": is_low_ticket,
            "elasticity": elasticity_data,
            "total_steps": len(steps),
            "estimated_days": len(steps) * 1
        }

    def get_next_step_price(self, item_id: str, current_price: float, target_price: float) -> float:
        """
        Returns just the very next step price (today's adjustment), reusing the
        exact same logic/config as calculate_safe_price_steps — used by the
        scheduled execution job so preview and reality never diverge.
        """
        plan = self.calculate_safe_price_steps(item_id, current_price, target_price)
        if not plan["steps"]:
            return target_price
        return plan["steps"][0]["price"]

    def check_auto_reversion_status(self, item_id: str):
        """
        Checks if the item triggers the Automatic Reversion logic:
        Condition: Conversion drops > 15% compared to 7-day average.
        """
        today = datetime.utcnow().date()
        cutoff_7d = today - timedelta(days=7)

        # 1. 7-Day Average (excluding today)
        metrics_7d = self.db.query(
            func.sum(MlMetricsDaily.sales_qty).label('total_sales'),
            func.sum(MlMetricsDaily.visits).label('total_visits')
        ).filter(
            MlMetricsDaily.item_id == item_id,
            MlMetricsDaily.date >= cutoff_7d,
            MlMetricsDaily.date < today
        ).first()

        total_sales_7d = metrics_7d.total_sales or 0
        total_visits_7d = metrics_7d.total_visits or 0
        
        avg_conversion_7d = 0.0
        if total_visits_7d > 0:
            avg_conversion_7d = (total_sales_7d / total_visits_7d) * 100

        # 2. Current Status (Today or latest available data point)
        # We try to get today's data first
        current_metric = self.db.query(MlMetricsDaily).filter(
            MlMetricsDaily.item_id == item_id,
            MlMetricsDaily.date == today
        ).first()

        current_conversion = 0.0
        has_today_data = False
        
        MIN_VISITS_FOR_REVERSION = 10  # avoid triggering on sparse early-morning data
        if current_metric and current_metric.visits >= MIN_VISITS_FOR_REVERSION:
            current_conversion = (current_metric.sales_qty / current_metric.visits) * 100
            has_today_data = True

        # 3. Calculate Drop
        if not has_today_data:
             return {
                "triggered": False,
                "reason": f"Aguardando dados de visita de hoje (mínimo {MIN_VISITS_FOR_REVERSION} visitas)",
                "avg_7d": round(avg_conversion_7d, 2),
                "current": 0.0,
                "drop_pct": 0.0
            }

        if avg_conversion_7d == 0:
             return {
                "triggered": False,
                "reason": "Histórico insuficiente (Média 0)",
                "avg_7d": 0.0,
                "current": round(current_conversion, 2),
                "drop_pct": 0.0
            }

        # Drop formula: (Old - New) / Old
        drop_pct = (avg_conversion_7d - current_conversion) / avg_conversion_7d

        # Threshold: 15% drop (0.15)
        triggered = drop_pct > 0.15

        return {
            "triggered": triggered,
            "reason": f"ALERTA: Queda de {drop_pct*100:.1f}% (Meta 7d: {avg_conversion_7d:.1f}%)" if triggered else "Conversão dentro da margem segura",
            "avg_7d": round(avg_conversion_7d, 2),
            "current": round(current_conversion, 2),
            "drop_pct": round(drop_pct * 100, 1)
        }

    def calculate_break_even_conversion(self, item_id: str, new_price: float):
        """
        Calculates the conversion rate required at 'new_price' to maintain the same
        Total Profit (in Reais) as the current price, assuming constant traffic.
        
        Formula: NewConv = (OldMarginValue * OldConv) / NewMarginValue
        """
        ad = self.db.query(Ad).filter(Ad.id == item_id).first()
        if not ad or not ad.price or ad.price <= 0:
            return 0.0

        # All Ad columns here are Numeric/Decimal in the DB; cast to float up front
        # so they can mix freely with the float current_price/new_price args below.
        ad_price = float(ad.price)
        cost_product = float(ad.cost or 0.0)
        cost_shipping = float(ad.shipping_cost or 0.0)
        tax_cost = float(ad.tax_cost or 0.0)
        commission_percent = float(ad.commission_percent or 0.0)
        commission_cost = float(ad.commission_cost or 0.0)
        margin_value = float(ad.margin_value) if ad.margin_value is not None else None

        # Rates
        tax_rate = 0.0
        if tax_cost and ad_price > 0:
            tax_rate = tax_cost / ad_price

        comm_rate = 0.0
        if commission_percent:
            comm_rate = commission_percent
        elif commission_cost and ad_price > 0:
            comm_rate = commission_cost / ad_price

        # Current Margin Value
        current_margin_value = margin_value
        if current_margin_value is None:
             current_margin_value = ad_price - (ad_price * comm_rate) - (ad_price * tax_rate) - cost_shipping - cost_product

        # Current Conversion
        current_conversion = 0.0
        if ad.total_visits and ad.total_visits > 0:
            current_conversion = (ad.sold_quantity or 0) / ad.total_visits # Ratio (0.05 for 5%)

        if current_conversion == 0 or current_margin_value <= 0:
            return 0.0

        # Calculate New Margin Value
        new_comm_cost = new_price * comm_rate
        new_tax_cost = new_price * tax_rate
        
        new_margin_value = new_price - new_comm_cost - new_tax_cost - cost_shipping - cost_product
        
        if new_margin_value <= 0:
            return 999.0 # Impossible to break even if losing money per unit
            
        # Break-even Conversion Formula
        # OldProfitPerVisitor = OldMarginValue * OldConv
        # NewProfitPerVisitor = NewMarginValue * NewConv
        # NewConv = (OldMarginValue * OldConv) / NewMarginValue
        
        required_conversion = (current_margin_value * current_conversion) / new_margin_value
        
        return round(required_conversion * 100, 2) # Return as Percentage

    def get_strategy_data(self, item_id: str, current_price: float, target_price: float):
        """
        Returns complete strategy data for frontend display.
        Includes conversion threshold, elasticity, price steps, and reversion status.
        """
        # Get ad for current conversion
        ad = self.db.query(Ad).filter(Ad.id == item_id).first()
        
        current_conversion = 0.0
        if ad and ad.total_visits and ad.total_visits > 0:
            current_conversion = (ad.sold_quantity or 0) / ad.total_visits * 100
        
        conversion_data = self.calculate_conversion_threshold(item_id)
        price_steps_data = self.calculate_safe_price_steps(item_id, current_price, target_price)
        reversion_status = self.check_auto_reversion_status(item_id)
        break_even_at_target = self.calculate_break_even_conversion(item_id, target_price)
        
        return {
            "conversion": {
                "current": round(current_conversion, 2),
                "threshold": conversion_data["threshold"],
                "method": conversion_data["method"],
                "explanation": conversion_data["explanation"],
                "break_even_at_target": break_even_at_target
            },
            "reversion_status": reversion_status,
            "elasticity": price_steps_data["elasticity"],
            "price_steps": price_steps_data["steps"],
            "step_mode": price_steps_data.get("step_mode", "percent"),
            "step_value": price_steps_data.get("step_value", 0),
            "is_low_ticket": price_steps_data.get("is_low_ticket", False),
            "estimated_days": price_steps_data["estimated_days"],
            "tooltips": {
                "conversion": f"Taxa de conversão = (Vendas ÷ Visitas) × 100. Atual: {current_conversion:.2f}%",
                "threshold": conversion_data["explanation"],
                "elasticity": price_steps_data["elasticity"].get("suggestion", "Calculado do histórico de preços × vendas"),
                "steps": "Ajustes inteligentes buscando preços psicológicos (.40, .74, .90)",
                "reversion": reversion_status["reason"],
                "break_even": f"Para manter o mesmo lucro total, a conversão não pode cair abaixo de {break_even_at_target}%"
            }
        }
