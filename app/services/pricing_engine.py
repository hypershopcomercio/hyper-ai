from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.ml_metrics_daily import MlMetricsDaily
from app.models.ad import Ad
import numpy as np

class PricingEngine:
    def __init__(self, db: Session):
        self.db = db

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
        Calculates safe price adjustment steps based on product elasticity.
        
        - Elastic products (>1.5): small 1% steps
        - Unitary products (0.8-1.5): medium 2% steps  
        - Inelastic products (<0.8): larger 3% steps
        
        Returns list of price steps with dates and reasons.
        """
        elasticity_data = self.calculate_elasticity(item_id)
        elasticity_score = elasticity_data.get("score")
        
        # FIXED STRATEGY: R$ 0.40 per day
        step_fixed_value = 0.40
        reason_base = "Estratégia Fixa: Aumento de R$ 0,40 por dia"
        
        # Calculate steps from current to target
        steps = []
        price = current_price
        step_num = 0
        base_date = datetime.utcnow().date()
        
        # Determine total steps needed
        if target_price > current_price:
             while price < target_price and step_num < 200: # Safety break (200 steps max)
                step_num += 1
                new_price = price + step_fixed_value
                
                if new_price >= target_price - 0.005: 
                    new_price = target_price
                
                step_date = base_date + timedelta(days=step_num * 1) # 1 day per step
                
                steps.append({
                    "step": step_num,
                    "date": step_date.strftime("%Y-%m-%d"),
                    "date_display": step_date.strftime("%d/%m"),
                    "price": round(new_price, 2),
                    "increase_pct": round(((new_price - current_price) / current_price) * 100, 2),
                    "reason": reason_base if step_num == 1 else f"Step {step_num}: +R$ {step_fixed_value:.2f}"
                })
                
                price = new_price
                if price >= target_price:
                    break
        
        return {
            "steps": steps,
            "step_size_fixed": step_fixed_value,
            "elasticity": elasticity_data,
            "total_steps": len(steps),
            "estimated_days": len(steps) * 1
        }

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
        
        if current_metric and current_metric.visits > 0:
            current_conversion = (current_metric.sales_qty / current_metric.visits) * 100
            has_today_data = True

        # 3. Calculate Drop
        if not has_today_data:
             return {
                "triggered": False,
                "reason": "Aguardando dados de visita de hoje",
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

        # Calculate Current State
        # We use stored margin_value if trusted, or recalculate to be safe/consistent
        # Cost + Ship + Fixed
        cost_product = ad.cost or 0.0
        cost_shipping = ad.shipping_cost or 0.0
        
        # Rates
        tax_rate = 0.0
        if ad.tax_cost and ad.price > 0:
            tax_rate = ad.tax_cost / ad.price
            
        comm_rate = 0.0
        if ad.commission_percent:
            comm_rate = ad.commission_percent
        elif ad.commission_cost and ad.price > 0:
            comm_rate = ad.commission_cost / ad.price
            
        # Current Margin Value
        current_margin_value = ad.margin_value
        if current_margin_value is None:
             current_margin_value = ad.price - (ad.price * comm_rate) - (ad.price * tax_rate) - cost_shipping - cost_product

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
            "step_size_pct": price_steps_data.get("step_size_fixed", 0),
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
