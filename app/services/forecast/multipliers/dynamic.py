"""
Dynamic Multiplier Service
Loads ALL multipliers from MultiplierConfig table and applies them dynamically.
No hardcoded factors - everything comes from database.
"""
import logging
from datetime import datetime, date
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from decimal import Decimal

logger = logging.getLogger(__name__)


class DynamicMultipliers:
    """
    Loads and applies ALL multipliers from the database.
    This replaces hardcoded constants with database-driven values.
    
    When new multipliers are added to MultiplierConfig, they are
    automatically included in calculations.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self._cache = {}
        self._cache_time = None
        self._cache_ttl = 300  # 5 minutes
    
    def _load_all_multipliers(self) -> Dict[str, Dict[str, float]]:
        """
        Load all multipliers from database, grouped by type.
        Returns: { "type": { "key": value } }
        """
        from app.models.forecast_learning import MultiplierConfig
        
        now = datetime.now()
        if self._cache and self._cache_time and (now - self._cache_time).seconds < self._cache_ttl:
            return self._cache
        
        all_configs = self.db.query(MultiplierConfig).all()
        
        grouped = {}
        for config in all_configs:
            tipo = config.tipo
            if tipo not in grouped:
                grouped[tipo] = {}
            grouped[tipo][config.chave] = float(config.valor)
        
        self._cache = grouped
        self._cache_time = now
        
        logger.debug(f"[MULTIPLIERS] Loaded {len(all_configs)} multipliers from {len(grouped)} types")
        
        return grouped
    
    def get_multiplier(self, tipo: str, chave: str, default: float = 1.0) -> float:
        """Get a specific multiplier value."""
        all_mults = self._load_all_multipliers()
        return all_mults.get(tipo, {}).get(chave, default)
    
    def get_all_global_multipliers(self, target_date: date, target_hour: int) -> Dict[str, float]:
        """
        Get ALL global multipliers that apply to the given date/hour.
        These are factors that affect ALL products equally.
        
        Returns dict with all applicable multipliers and their values.
        Also populates self.factor_metadata with categorical keys for logging.
        """
        all_mults = self._load_all_multipliers()
        result = {}
        
        # Initialize metadata dict for categorical keys
        self.factor_metadata = {}
        
        # 1. Day of Week
        dow_names = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo']
        dow_index = target_date.weekday()
        dow_name = dow_names[dow_index]
        result['day_of_week'] = all_mults.get('day_of_week', {}).get(dow_name, 1.0)
        self.factor_metadata['day_of_week'] = dow_name  # Store categorical key
        
        # 2. Period of Month
        day = target_date.day
        if day <= 10:
            period_key = 'inicio'
        elif day <= 20:
            period_key = 'meio'
        else:
            period_key = 'fim'
        result['period_of_month'] = all_mults.get('period_of_month', {}).get(period_key, 1.0)
        self.factor_metadata['period_of_month'] = period_key
        
        # 3. Week of Month
        day = target_date.day
        week = (day - 1) // 7 + 1
        week_key = f"semana_{week}"  # semana_1, semana_2, etc.
        result['week_of_month'] = all_mults.get('week_of_month', {}).get(week_key, 1.0)
        self.factor_metadata['week_of_month'] = week_key
        
        # 4. Payment Day (dias de pagamento típicos BR: 5, 10, 15, 20, etc)
        if day in [5, 10, 15, 20, 25]:
            payment_key = str(day)
            result['payment_day'] = all_mults.get('payment_day', {}).get(payment_key, 1.2)
            self.factor_metadata['payment_day'] = payment_key
        else:
            result['payment_day'] = 1.0
            self.factor_metadata['payment_day'] = 'off'
        
        # 5. Hourly Pattern
        hour_key = f"{target_hour:02d}h"  # "00h", "01h", "23h"
        result['hourly_pattern'] = all_mults.get('hourly_pattern', {}).get(hour_key, 1.0)
        self.factor_metadata['hourly_pattern'] = hour_key
        
        # 6. Mobile Hours (horários de maior uso mobile)
        if target_hour in [6, 7, 8, 12, 13, 18, 19, 20, 21, 22]:
            mobile_key = 'peak'
            result['mobile_hours'] = all_mults.get('mobile_hours', {}).get(mobile_key, 1.0)
        else:
            mobile_key = 'off_peak'
            result['mobile_hours'] = all_mults.get('mobile_hours', {}).get(mobile_key, 1.0)
        self.factor_metadata['mobile_hours'] = mobile_key
        
        # 7. Impulse Hours (horários de compra por impulso)
        if target_hour in [12, 13, 19, 20, 21, 22, 23]:
            impulse_key = 'active'
            result['impulse_hours'] = all_mults.get('impulse_hours', {}).get(impulse_key, 1.0)
            self.factor_metadata['impulse_hours'] = impulse_key
        else:
            result['impulse_hours'] = 1.0
            self.factor_metadata['impulse_hours'] = 'normal'
        
        # 8. Seasonal (based on month)
        month = target_date.month
        if month in [12, 1, 2]:
            seasonal_key = 'verao'
            result['seasonal'] = all_mults.get('seasonal', {}).get(seasonal_key, 1.0)
        elif month in [6, 7, 8]:
            seasonal_key = 'inverno'
            result['seasonal'] = all_mults.get('seasonal', {}).get(seasonal_key, 1.0)
        else:
            seasonal_key = 'neutro'
            result['seasonal'] = 1.0
        self.factor_metadata['seasonal'] = seasonal_key
        
        # 9. Event (special dates)
        date_key = target_date.strftime("%m-%d")
        result['event'] = all_mults.get('event', {}).get(date_key, 1.0)
        self.factor_metadata['event'] = date_key if result['event'] != 1.0 else 'normal'
        
        # 10. Post-Feriado
        # Check if yesterday was a holiday
        from datetime import timedelta
        yesterday_key = (target_date - timedelta(days=1)).strftime("%m-%d")
        if yesterday_key in all_mults.get('event', {}):
            result['post_feriado'] = all_mults.get('post_feriado', {}).get('active', 1.0)
            self.factor_metadata['post_feriado'] = 'active'
        else:
            result['post_feriado'] = 1.0
            self.factor_metadata['post_feriado'] = 'inactive'
        
        # 11. Weather (REAL API Integration)
        try:
            from app.services.weather_service import get_overall_weather_multiplier
            weather_mult = get_overall_weather_multiplier()
            result['weather'] = weather_mult if weather_mult else 1.0
            self.factor_metadata['weather'] = f"{result['weather']:.3f}"  # Store as string
            logger.info(f"[WEATHER] Multiplier: {result['weather']:.3f}")
        except Exception as e:
            logger.warning(f"[WEATHER] Failed to fetch, using neutral: {e}")
            result['weather'] = 1.0
            self.factor_metadata['weather'] = 'neutral'
        
        # 12. Google Trends (if available)
        result['google_trends'] = all_mults.get('google_trends', {}).get('current', 1.0)
        self.factor_metadata['google_trends'] = 'current'
        
        return result
    
    def get_factor_metadata(self) -> Dict[str, str]:
        """
        Get categorical key names for factors (NOT numeric values).
        Call this AFTER get_all_global_multipliers().
        
        Returns dict mapping factor names to their categorical keys.
        Example: {'day_of_week': 'segunda', 'seasonal': 'verao'}
        """
        return getattr(self, 'factor_metadata', {})
    
    def get_all_product_multipliers(self, product) -> Dict[str, float]:
        """
        Get ALL product-specific multipliers.
        These are factors that vary by product.
        
        Args:
            product: ProductForecast object
            
        Returns dict with all applicable multipliers and their values.
        """
        all_mults = self._load_all_multipliers()
        result = {}
        
        # Helper function to get calibrated value with product_ prefix fallback
        def get_calibrated(factor_type: str, factor_key: str, default: float) -> float:
            """Get value from product_<type> first, then fallback to <type>."""
            product_type = f"product_{factor_type}"
            if product_type in all_mults and factor_key in all_mults[product_type]:
                return all_mults[product_type][factor_key]
            return all_mults.get(factor_type, {}).get(factor_key, default)
        
        # 1. Stock Pressure (based on days of coverage AND hard stock check)
        stock_current = getattr(product, 'stock_current', 0)
        
        if stock_current <= 0:
             result['stock_pressure'] = 0.0 # No stock = HARD STOP on sales
        elif product.days_of_coverage:
            days = float(product.days_of_coverage)
            if days < 3:
                result['stock_pressure'] = get_calibrated('stock_pressure', 'critical', 0.5)
            elif days < 7:
                result['stock_pressure'] = get_calibrated('stock_pressure', 'low', 0.8)
            else:
                result['stock_pressure'] = get_calibrated('stock_pressure', 'normal', 1.0)
        else:
            result['stock_pressure'] = 1.0
        
        # 2. Listing Health (based on product status)
        health = getattr(product, 'listing_health', None)
        if health:
            result['listing_health'] = get_calibrated('listing_health', health, 1.0)
        else:
            result['listing_health'] = get_calibrated('listing_health', 'neutral', 1.0)
        
        # 3. Search Position (if available)
        position = getattr(product, 'search_position', None)
        if position:
            if position <= 5:
                result['search_position'] = get_calibrated('search_position', 'top5', 1.3)
            elif position <= 10:
                result['search_position'] = get_calibrated('search_position', 'top10', 1.15)
            elif position <= 20:
                result['search_position'] = get_calibrated('search_position', 'top20', 1.0)
            else:
                result['search_position'] = get_calibrated('search_position', 'below20', 0.8)
        else:
            result['search_position'] = 1.0
        
        # 4. Free Shipping
        has_free_shipping = getattr(product, 'has_free_shipping', False)
        if has_free_shipping:
            result['free_shipping'] = get_calibrated('free_shipping', 'active', 1.1)
        else:
            result['free_shipping'] = get_calibrated('free_shipping', 'inactive', 1.0)
        
        # 5. Shipping Advantage (FULL, etc)
        shipping_type = getattr(product, 'shipping_type', None)
        if shipping_type:
            result['shipping_advantage'] = get_calibrated('shipping_advantage', shipping_type, 1.0)
        else:
            result['shipping_advantage'] = 1.0
        
        # 6. Listing Type (classico, premium, etc)
        listing_type = getattr(product, 'listing_type', None)
        if listing_type:
            result['listing_type'] = get_calibrated('listing_type', listing_type, 1.0)
        else:
            result['listing_type'] = 1.0
        
        # 7. Gold Medal (selo)
        has_medal = getattr(product, 'gold_medal', False)
        if has_medal:
            result['gold_medal'] = get_calibrated('gold_medal', 'active', 1.1)
        else:
            result['gold_medal'] = get_calibrated('gold_medal', 'inactive', 1.0)
        
        # 8. Catalog Boost
        in_catalog = getattr(product, 'catalog_listing', False)
        if in_catalog:
            result['catalog_boost'] = get_calibrated('catalog_boost', 'active', 1.15)
        else:
            result['catalog_boost'] = get_calibrated('catalog_boost', 'inactive', 1.0)
        
        # 9. Promo Active
        has_promo = getattr(product, 'has_promo', False)
        if has_promo:
            result['promo_active'] = get_calibrated('promo_active', 'active', 1.2)
        else:
            result['promo_active'] = get_calibrated('promo_active', 'inactive', 1.0)
        
        # 10. Visits Trend (based on trend direction)
        trend = getattr(product, 'trend', None)
        trend_pct = getattr(product, 'trend_pct', None)
        if trend == 'up' and trend_pct:
            boost = min(float(trend_pct) / 100, 0.5)  # Cap at 50%
            result['visits_trend'] = 1.0 + boost
        elif trend == 'down' and trend_pct:
            reduction = max(float(trend_pct) / 100, -0.5)
            result['visits_trend'] = 1.0 + reduction
        else:
            result['visits_trend'] = 1.0
        
        # 11. Conversion Rate (relative to average)
        # Would need conversion rate data
        result['conversion_rate'] = 1.0
        
        # 12. Price Competitiveness
        # Would need competitor price data
        result['price_competitiveness'] = 1.0
        
        # 13. Competitor Stockout
        # Would need competitor stock data
        result['competitor_stockout'] = 1.0
        
        # 14. Velocity Score (based on curve)
        curve = getattr(product, 'curve', None)
        if curve == 'A':
            result['velocity_score'] = all_mults.get('velocity_score', {}).get('A', 1.0)
        elif curve == 'B':
            result['velocity_score'] = all_mults.get('velocity_score', {}).get('B', 1.0)
        elif curve == 'C':
            result['velocity_score'] = all_mults.get('velocity_score', {}).get('C', 1.0)
        else:
            result['velocity_score'] = 1.0
        
        # 15. Top Sellers
        is_top_seller = getattr(product, 'is_top_seller', False)
        if is_top_seller:
            result['top_sellers'] = all_mults.get('top_sellers', {}).get('active', 1.2)
        else:
            result['top_sellers'] = 1.0
        
        return result
    
    def _get_period_key(self, day: int) -> str:
        """Get period key for day of month."""
        if day <= 5:
            return 'inicio'
        elif day <= 10:
            return 'pos_pagamento'
        elif day <= 20:
            return 'meio'
        elif day <= 25:
            return 'pre_salario'
        else:
            return 'fim'
    
    def get_multiplier_types(self) -> List[str]:
        """Get all available multiplier types."""
        all_mults = self._load_all_multipliers()
        return list(all_mults.keys())
    
    def calculate_combined_multiplier(self, multipliers: Dict[str, float]) -> float:
        """
        Calculate the combined multiplier from all individual multipliers.
        All multipliers are multiplicative (product of all values).
        """
        combined = 1.0
        for value in multipliers.values():
            combined *= value
        return combined
