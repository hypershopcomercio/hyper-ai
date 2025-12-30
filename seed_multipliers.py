"""
Script to seed ALL sub-factors for each factor type in the Hyper AI system.
Based on the 28 factors in the /api/factors endpoint.
"""
from app.core.database import SessionLocal
from app.models.forecast_learning import MultiplierConfig
from decimal import Decimal
from datetime import datetime

def seed_all_subfactors():
    """Populate the multiplier_config table with ALL expected sub-factors."""
    
    db = SessionLocal()
    
    try:
        # Clear existing multipliers
        db.query(MultiplierConfig).delete()
        db.commit()
        print("Cleared existing multipliers")
        
        multipliers = []
        
        # ========================================
        # 1. mult_day_of_week - Dia da Semana (7)
        # ========================================
        day_of_week = {
            'segunda': 0.95, 'terca': 1.00, 'quarta': 1.00, 
            'quinta': 1.05, 'sexta': 1.15, 'sabado': 1.25, 'domingo': 1.10
        }
        for k, v in day_of_week.items():
            multipliers.append(MultiplierConfig(tipo='day_of_week', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=50))
        
        # ========================================
        # 2. mult_hourly_pattern - Hora do Dia (24)
        # ========================================
        hour = {
            0: 0.20, 1: 0.10, 2: 0.05, 3: 0.05, 4: 0.05, 5: 0.10,
            6: 0.30, 7: 0.50, 8: 0.70, 9: 0.85, 10: 1.00, 11: 1.10,
            12: 1.05, 13: 1.00, 14: 0.95, 15: 1.00, 16: 1.05, 17: 1.10,
            18: 1.15, 19: 1.10, 20: 1.00, 21: 0.90, 22: 0.70, 23: 0.40
        }
        for k, v in hour.items():
            multipliers.append(MultiplierConfig(tipo='hourly_pattern', chave=str(k), valor=Decimal(str(v)), calibrado='default', confianca=50))
        
        # ========================================
        # 3. mult_period_of_month - Período do Mês (3)
        # ========================================
        period_of_month = {'inicio': 1.10, 'meio': 1.00, 'fim': 0.90}
        for k, v in period_of_month.items():
            multipliers.append(MultiplierConfig(tipo='period_of_month', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=50))
        
        # ========================================
        # 4. mult_week_of_month - Semana do Mês (5)
        # ========================================
        week_of_month = {'semana_1': 1.15, 'semana_2': 1.00, 'semana_3': 0.95, 'semana_4': 0.90, 'semana_5': 0.85}
        for k, v in week_of_month.items():
            multipliers.append(MultiplierConfig(tipo='week_of_month', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=50))
        
        # ========================================
        # 5. mult_seasonal - Sazonalidade (15)
        # ========================================
        seasonal = {
            'natal': 1.50, 'black_friday': 2.00, 'cyber_monday': 1.60, 'ano_novo': 1.20,
            'dia_maes': 1.40, 'dia_pais': 1.30, 'dia_namorados': 1.35, 'carnaval': 0.80,
            'pascoa': 1.15, 'volta_aulas': 1.10, 'dia_criancas': 1.25, 'dia_consumidor': 1.30,
            'verao': 1.15, 'inverno': 0.95, 'normal': 1.00
        }
        for k, v in seasonal.items():
            multipliers.append(MultiplierConfig(tipo='seasonal', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=50))
        
        # ========================================
        # 6. mult_momentum - Momentum/Tendência (5)
        # ========================================
        momentum = {'muito_alto': 1.20, 'alto': 1.10, 'normal': 1.00, 'baixo': 0.90, 'muito_baixo': 0.80}
        for k, v in momentum.items():
            multipliers.append(MultiplierConfig(tipo='momentum', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=50))
        
        # ========================================
        # 7. mult_weather - Clima (6)
        # ========================================
        weather = {'muito_quente': 1.20, 'quente': 1.10, 'ameno': 1.00, 'frio': 0.95, 'muito_frio': 0.90, 'chuva': 0.85}
        for k, v in weather.items():
            multipliers.append(MultiplierConfig(tipo='weather', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=30))
        
        # ========================================
        # 8. mult_event - Eventos Especiais (10)
        # ========================================
        event = {
            'feriado': 0.70, 'vespera_feriado': 0.85, 'pos_feriado': 0.90,
            'promocao_relampago': 1.50, 'frete_gratis_geral': 1.30,
            'cupom_desconto': 1.20, 'live_commerce': 1.40, 'lancamento': 1.35,
            'queima_estoque': 1.45, 'normal': 1.00
        }
        for k, v in event.items():
            multipliers.append(MultiplierConfig(tipo='event', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=50))
        
        # ========================================
        # 9. mult_post_feriado - Pós Feriado (4)
        # ========================================
        post_feriado = {'dia_1': 0.85, 'dia_2': 0.90, 'dia_3': 0.95, 'normal': 1.00}
        for k, v in post_feriado.items():
            multipliers.append(MultiplierConfig(tipo='post_feriado', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=50))
        
        # ========================================
        # 10. mult_payment_day - Dia de Pagamento (5)
        # ========================================
        payment_day = {'dia_pagamento': 1.25, 'dia_apos_pagamento': 1.15, 'semana_pagamento': 1.10, 'fora_pagamento': 0.95, 'normal': 1.00}
        for k, v in payment_day.items():
            multipliers.append(MultiplierConfig(tipo='payment_day', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=50))
        
        # ========================================
        # 11. mult_impulse_hours - Horas de Impulso (6)
        # ========================================
        impulse_hours = {'manha_cedo': 0.70, 'manha': 1.00, 'almoco': 1.15, 'tarde': 1.10, 'noite': 1.20, 'madrugada': 0.50}
        for k, v in impulse_hours.items():
            multipliers.append(MultiplierConfig(tipo='impulse_hours', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=50))
        
        # ========================================
        # 12. mult_mobile_hours - Horários Mobile (4)
        # ========================================
        mobile_hours = {'pico_mobile': 1.15, 'medio_mobile': 1.00, 'baixo_mobile': 0.90, 'normal': 1.00}
        for k, v in mobile_hours.items():
            multipliers.append(MultiplierConfig(tipo='mobile_hours', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=40))
        
        # ========================================
        # 13. mult_listing_type - Tipo de Anúncio (4)
        # ========================================
        listing_type = {'gold_special': 1.20, 'gold_pro': 1.15, 'gold': 1.05, 'classico': 1.00}
        for k, v in listing_type.items():
            multipliers.append(MultiplierConfig(tipo='listing_type', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=60))
        
        # ========================================
        # 14. mult_listing_health - Saúde do Anúncio (5)
        # ========================================
        listing_health = {'excelente': 1.20, 'bom': 1.10, 'regular': 1.00, 'ruim': 0.85, 'critico': 0.70}
        for k, v in listing_health.items():
            multipliers.append(MultiplierConfig(tipo='listing_health', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=50))
        
        # ========================================
        # 15. mult_gold_medal - Medalha MercadoLíder (4)
        # ========================================
        gold_medal = {'platinum': 1.20, 'gold': 1.10, 'silver': 1.00, 'none': 0.95}
        for k, v in gold_medal.items():
            multipliers.append(MultiplierConfig(tipo='gold_medal', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=60))
        
        # ========================================
        # 16. mult_free_shipping - Frete Grátis (3)
        # ========================================
        free_shipping = {'frete_gratis': 1.25, 'frete_subsidiado': 1.10, 'frete_pago': 1.00}
        for k, v in free_shipping.items():
            multipliers.append(MultiplierConfig(tipo='free_shipping', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=70))
        
        # ========================================
        # 17. mult_shipping_advantage - Vantagem de Envio (4)
        # ========================================
        shipping_advantage = {'full': 1.30, 'coleta': 1.15, 'flex': 1.10, 'normal': 1.00}
        for k, v in shipping_advantage.items():
            multipliers.append(MultiplierConfig(tipo='shipping_advantage', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=60))
        
        # ========================================
        # 18. mult_catalog_boost - Catálogo Boost (4)
        # ========================================
        catalog_boost = {'catalogo_oficial': 1.25, 'catalogo_parceiro': 1.15, 'catalogo': 1.05, 'normal': 1.00}
        for k, v in catalog_boost.items():
            multipliers.append(MultiplierConfig(tipo='catalog_boost', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=50))
        
        # ========================================
        # 19. mult_search_position - Posição na Busca (6)
        # ========================================
        search_position = {'top_3': 1.40, 'top_10': 1.25, 'top_20': 1.10, 'top_50': 1.00, 'abaixo_50': 0.85, 'fora_busca': 0.60}
        for k, v in search_position.items():
            multipliers.append(MultiplierConfig(tipo='search_position', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=50))
        
        # ========================================
        # 20. mult_conversion_rate - Taxa de Conversão (5)
        # ========================================
        conversion_rate = {'muito_alta': 1.35, 'alta': 1.20, 'media': 1.00, 'baixa': 0.80, 'muito_baixa': 0.60}
        for k, v in conversion_rate.items():
            multipliers.append(MultiplierConfig(tipo='conversion_rate', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=50))
        
        # ========================================
        # 21. mult_visits_trend - Tendência de Visitas (5)
        # ========================================
        visits_trend = {'subindo_rapido': 1.25, 'subindo': 1.10, 'estavel': 1.00, 'descendo': 0.90, 'descendo_rapido': 0.75}
        for k, v in visits_trend.items():
            multipliers.append(MultiplierConfig(tipo='visits_trend', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=50))
        
        # ========================================
        # 22. mult_velocity_score - Velocidade de Vendas (5)
        # ========================================
        velocity_score = {'muito_rapido': 1.30, 'rapido': 1.15, 'normal': 1.00, 'lento': 0.85, 'muito_lento': 0.70}
        for k, v in velocity_score.items():
            multipliers.append(MultiplierConfig(tipo='velocity_score', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=50))
        
        # ========================================
        # 23. mult_price_competitiveness - Competitividade de Preço (5)
        # ========================================
        price_competitiveness = {'muito_competitivo': 1.25, 'competitivo': 1.10, 'media': 1.00, 'alto': 0.85, 'muito_alto': 0.70}
        for k, v in price_competitiveness.items():
            multipliers.append(MultiplierConfig(tipo='price_competitiveness', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=50))
        
        # ========================================
        # 24. mult_stock_pressure - Pressão de Estoque (5)
        # ========================================
        stock_pressure = {'urgente': 1.40, 'alto': 1.20, 'medio': 1.00, 'baixo': 0.90, 'sem_pressao': 0.85}
        for k, v in stock_pressure.items():
            multipliers.append(MultiplierConfig(tipo='stock_pressure', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=50))
        
        # ========================================
        # 25. mult_competitor_stockout - Concorrentes sem Estoque (4)
        # ========================================
        competitor_stockout = {'maioria_sem': 1.35, 'alguns_sem': 1.15, 'normal': 1.00, 'todos_com': 0.95}
        for k, v in competitor_stockout.items():
            multipliers.append(MultiplierConfig(tipo='competitor_stockout', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=40))
        
        # ========================================
        # 26. mult_top_sellers - Top Sellers (5)
        # ========================================
        top_sellers = {'top_10': 1.40, 'top_50': 1.25, 'top_100': 1.10, 'normal': 1.00, 'baixa_venda': 0.85}
        for k, v in top_sellers.items():
            multipliers.append(MultiplierConfig(tipo='top_sellers', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=50))
        
        # ========================================
        # 27. mult_google_trends - Google Trends (5)
        # ========================================
        google_trends = {'viral': 1.50, 'alta': 1.20, 'normal': 1.00, 'baixa': 0.85, 'sem_interesse': 0.70}
        for k, v in google_trends.items():
            multipliers.append(MultiplierConfig(tipo='google_trends', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=30))
        
        # ========================================
        # 28. mult_promo_active - Promoção Ativa (4)
        # ========================================
        promo_active = {'super_promo': 1.50, 'promo': 1.25, 'desconto_leve': 1.10, 'sem_promo': 1.00}
        for k, v in promo_active.items():
            multipliers.append(MultiplierConfig(tipo='promo_active', chave=k, valor=Decimal(str(v)), calibrado='default', confianca=60))
        
        # Add all to database
        for m in multipliers:
            db.add(m)
        
        db.commit()
        
        # Count by type
        type_counts = {}
        for m in multipliers:
            type_counts[m.tipo] = type_counts.get(m.tipo, 0) + 1
        
        print(f"\n✅ Successfully seeded {len(multipliers)} sub-factors:")
        for tipo, count in sorted(type_counts.items()):
            print(f"   - {tipo}: {count} values")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_all_subfactors()
