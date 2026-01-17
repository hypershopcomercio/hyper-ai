from app.models.ad import Ad

class StockEngine:
    def analyze_stock(self, ad: Ad, avg_daily_sales: float):
        """
        Analyzes stock health based on current inventory and sales velocity.
        """
        stock = ad.available_quantity
        
        # Avoid division by zero
        velocity = avg_daily_sales if avg_daily_sales > 0 else 0.1
        days_of_stock = stock / velocity
        
        stock_incoming = getattr(ad, 'stock_incoming', 0) or 0
        total_potential_stock = stock + stock_incoming
        potential_days = total_potential_stock / velocity

        score = days_of_stock
        label = "Saudável"
        suggestion = "Estoque equilibrado."
        action = "MONITOR"
        status = "healthy" # healthy, warning, critical, overstock, incoming

        if stock == 0:
            if stock_incoming > 0:
                label = "Esgotado (Chegando)"
                suggestion = f"Sem estoque, mas {stock_incoming} un. estão a caminho."
                action = "WAIT_ARRIVAL"
                status = "incoming" # New status
            else:
                label = "Ruptura Total"
                suggestion = "Você está perdendo vendas. Reponha urgentemente."
                action = "RESTOCK_URGENT"
                status = "critical"
        elif days_of_stock < 7:
            if stock_incoming > 0:
                label = "Abastecimento a Caminho"
                suggestion = f"Estoque baixo ({stock} un), mas {stock_incoming} un. estão chegando."
                action = "MONITOR_ARRIVAL"
                status = "incoming" # Treating as incoming/safe-ish
            else:
                label = "Ruptura Iminente"
                suggestion = f"Estoque para apenas {int(days_of_stock)} dias. Faça pedido agora."
                action = "RESTOCK_NOW"
                status = "critical"
        elif days_of_stock < 30:
            if stock_incoming > 0 and potential_days > 30:
                 label = "Reposição Comprada"
                 suggestion = f"Estoque de segurança garantido com {stock_incoming} un. entrando."
                 action = "MONITOR"
                 status = "healthy"
            else:
                label = "Atenção"
                suggestion = f"Estoque para {int(days_of_stock)} dias. Planeje reposição."
                action = "PLAN_RESTOCK"
                status = "warning"
        elif days_of_stock > 90:
            label = "Excesso (Encalhado)"
            suggestion = f"Estoque para {int(days_of_stock)} dias. Considere promoção para girar caixa."
            action = "LIQUIDATE"
            status = "overstock"
            
        return {
            "days_of_stock": round(days_of_stock, 1),
            "label": label,
            "suggestion": suggestion,
            "action": action,
            "status": status,
            "analysis": f"Com {stock} un. (+{stock_incoming} chegando) e vendendo {round(avg_daily_sales, 1)}/dia."
        }
