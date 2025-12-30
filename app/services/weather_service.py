"""
Smart Weather Service - Advanced Weather Impact Analysis
Analyzes weather in buyer regions and applies category-specific multipliers
"""
import logging
import requests
from typing import Optional, Dict, List, Tuple
from collections import Counter
from datetime import datetime, timedelta
from sqlalchemy import func, and_

from app.core.database import SessionLocal
from app.models.system_config import SystemConfig
from app.models.ml_order import MlOrder
from app.models.ad import Ad

logger = logging.getLogger(__name__)


# Category sensitivity to weather conditions
# Format: {category_keyword: {hot: mult, cool: mult, cold: mult, rain: mult}}
# These keywords are matched against product titles
WEATHER_SENSITIVITY_KEYWORDS = {
    # HIGH sensitivity to HOT weather (piscinas, verão)
    "piscina": {"hot": 1.4, "warm": 1.2, "cool": 0.7, "cold": 0.5, "rain": 0.7},
    "inflável": {"hot": 1.35, "warm": 1.15, "cool": 0.6, "cold": 0.4, "rain": 0.6},
    "boia": {"hot": 1.35, "warm": 1.15, "cool": 0.5, "cold": 0.3, "rain": 0.5},
    "praia": {"hot": 1.3, "warm": 1.15, "cool": 0.6, "cold": 0.4, "rain": 0.5},
    "biquíni": {"hot": 1.3, "warm": 1.1, "cool": 0.5, "cold": 0.3, "rain": 0.6},
    "maiô": {"hot": 1.3, "warm": 1.1, "cool": 0.5, "cold": 0.3, "rain": 0.6},
    "sunga": {"hot": 1.3, "warm": 1.1, "cool": 0.5, "cold": 0.3, "rain": 0.6},
    "ventilador": {"hot": 1.45, "warm": 1.2, "cool": 0.5, "cold": 0.3, "rain": 1.0},
    "ar condicionado": {"hot": 1.5, "warm": 1.3, "cool": 0.5, "cold": 0.3, "rain": 1.0},
    "climatizador": {"hot": 1.4, "warm": 1.25, "cool": 0.5, "cold": 0.4, "rain": 1.0},
    "filtro piscina": {"hot": 1.35, "warm": 1.2, "cool": 0.7, "cold": 0.5, "rain": 0.8},
    "bomba piscina": {"hot": 1.3, "warm": 1.15, "cool": 0.7, "cold": 0.5, "rain": 0.8},
    "cloro": {"hot": 1.25, "warm": 1.1, "cool": 0.8, "cold": 0.6, "rain": 0.9},
    "protetor solar": {"hot": 1.4, "warm": 1.2, "cool": 0.6, "cold": 0.4, "rain": 0.5},
    
    # HIGH sensitivity to COLD weather
    "aquecedor": {"hot": 0.3, "warm": 0.5, "cool": 1.3, "cold": 1.5, "rain": 1.2},
    "cobertor": {"hot": 0.3, "warm": 0.5, "cool": 1.2, "cold": 1.4, "rain": 1.1},
    "edredom": {"hot": 0.3, "warm": 0.5, "cool": 1.2, "cold": 1.4, "rain": 1.1},
    "casaco": {"hot": 0.3, "warm": 0.5, "cool": 1.2, "cold": 1.4, "rain": 1.2},
    "jaqueta": {"hot": 0.3, "warm": 0.5, "cool": 1.2, "cold": 1.4, "rain": 1.2},
    "lareira": {"hot": 0.2, "warm": 0.4, "cool": 1.3, "cold": 1.6, "rain": 1.1},
    "guarda-chuva": {"hot": 0.6, "warm": 0.8, "cool": 1.0, "cold": 0.9, "rain": 1.5},
    "capa chuva": {"hot": 0.5, "warm": 0.7, "cool": 1.0, "cold": 0.9, "rain": 1.6},
    
    # MODERATE sensitivity - people shop online when home
    "decoração": {"hot": 1.0, "warm": 1.0, "cool": 1.0, "cold": 1.0, "rain": 1.15},
    "móveis": {"hot": 1.0, "warm": 1.0, "cool": 1.0, "cold": 1.0, "rain": 1.1},
    "eletrônico": {"hot": 1.0, "warm": 1.0, "cool": 1.0, "cold": 1.0, "rain": 1.1},
    "notebook": {"hot": 1.0, "warm": 1.0, "cool": 1.0, "cold": 1.0, "rain": 1.1},
    "celular": {"hot": 1.0, "warm": 1.0, "cool": 1.0, "cold": 1.0, "rain": 1.08},
    
    # No sensitivity (neutral)
    "_default": {"hot": 1.0, "warm": 1.0, "cool": 1.0, "cold": 1.0, "rain": 1.0}
}

# Brazilian state capitals for weather lookup
STATE_CAPITALS = {
    "AC": "Rio Branco,BR", "AL": "Maceio,BR", "AP": "Macapa,BR", "AM": "Manaus,BR",
    "BA": "Salvador,BR", "CE": "Fortaleza,BR", "DF": "Brasilia,BR", "ES": "Vitoria,BR",
    "GO": "Goiania,BR", "MA": "Sao Luis,BR", "MT": "Cuiaba,BR", "MS": "Campo Grande,BR",
    "MG": "Belo Horizonte,BR", "PA": "Belem,BR", "PB": "Joao Pessoa,BR", "PR": "Curitiba,BR",
    "PE": "Recife,BR", "PI": "Teresina,BR", "RJ": "Rio de Janeiro,BR", "RN": "Natal,BR",
    "RS": "Porto Alegre,BR", "RO": "Porto Velho,BR", "RR": "Boa Vista,BR", "SC": "Florianopolis,BR",
    "SP": "Sao Paulo,BR", "SE": "Aracaju,BR", "TO": "Palmas,BR"
}


class SmartWeatherService:
    """
    Intelligent weather service that:
    1. Analyzes where buyers are located
    2. Fetches weather for those regions
    3. Applies category-specific multipliers
    """
    
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    
    def __init__(self):
        self.api_key = None
        self._load_config()
        self._weather_cache = {}
        self._cache_time = None
    
    def _load_config(self):
        """Load API key from database settings"""
        db = SessionLocal()
        try:
            config = db.query(SystemConfig).filter(
                SystemConfig.group == 'integracoes',
                SystemConfig.key == 'openweather_api_key'
            ).first()
            if config and config.value:
                self.api_key = config.value
        except Exception as e:
            logger.error(f"Error loading weather config: {e}")
        finally:
            db.close()
    
    def get_top_buyer_regions(self, days: int = 30, limit: int = 5) -> List[Tuple[str, int]]:
        """
        Analyze order history to find where buyers come from
        
        Returns:
            List of (state, order_count) tuples
        """
        db = SessionLocal()
        try:
            cutoff = datetime.now() - timedelta(days=days)
            
            # Get orders with shipping info
            orders = db.query(MlOrder).filter(
                MlOrder.date_created >= cutoff,
                MlOrder.status.in_(['paid', 'delivered', 'shipped'])
            ).all()
            
            # Extract states from raw_data (shipping address)
            states = []
            for order in orders:
                if order.raw_data and isinstance(order.raw_data, dict):
                    shipping = order.raw_data.get('shipping', {})
                    receiver = shipping.get('receiver_address', {})
                    state = receiver.get('state', {})
                    state_id = state.get('id') if isinstance(state, dict) else None
                    if state_id:
                        states.append(state_id)
            
            # Count by state
            state_counts = Counter(states)
            top_states = state_counts.most_common(limit)
            
            logger.info(f"[WEATHER] Top buyer regions (last {days}d): {top_states}")
            return top_states
            
        except Exception as e:
            logger.error(f"Error analyzing buyer regions: {e}")
            return []
        finally:
            db.close()
    
    def get_weather_for_region(self, city: str) -> Optional[Dict]:
        """Fetch weather for a specific city/region"""
        if not self.api_key:
            return None
        
        # Check cache (15 min)
        cache_key = city.lower()
        if cache_key in self._weather_cache:
            cached_time, cached_data = self._weather_cache[cache_key]
            if datetime.now() - cached_time < timedelta(minutes=15):
                return cached_data
        
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "lang": "pt_br"
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            result = {
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "main": data["weather"][0]["main"],
                "city": data["name"]
            }
            
            # Cache it
            self._weather_cache[cache_key] = (datetime.now(), result)
            return result
            
        except Exception as e:
            logger.error(f"[WEATHER] Failed to fetch for {city}: {e}")
            return None
    
    def get_weighted_weather(self) -> Dict:
        """
        Get weather averaged across top buyer regions,
        weighted by order volume
        """
        top_regions = self.get_top_buyer_regions(days=30, limit=5)
        
        if not top_regions:
            # Fallback to São Paulo (biggest market)
            weather = self.get_weather_for_region("Sao Paulo,BR")
            return weather or {"temp": 25, "main": "Clear"}
        
        total_orders = sum(count for _, count in top_regions)
        weighted_temp = 0
        conditions = []
        
        for state, order_count in top_regions:
            city = STATE_CAPITALS.get(state, f"{state},BR")
            weather = self.get_weather_for_region(city)
            
            if weather:
                weight = order_count / total_orders
                weighted_temp += weather["temp"] * weight
                conditions.append(weather["main"])
        
        # Determine predominant condition
        condition_counts = Counter(conditions)
        main_condition = condition_counts.most_common(1)[0][0] if conditions else "Clear"
        
        return {
            "temp": weighted_temp,
            "main": main_condition,
            "regions_analyzed": len(top_regions)
        }
    
    def classify_weather(self, temp: float, main: str) -> str:
        """Classify weather into category"""
        is_rain = main in ["Rain", "Drizzle", "Thunderstorm"]
        
        if is_rain:
            return "rain"
        elif temp >= 30:
            return "hot"
        elif temp >= 24:
            return "warm"
        elif temp >= 18:
            return "cool"
        else:
            return "cold"
    
    def get_category_multiplier(self, product_title: str, category: Optional[str] = None) -> float:
        """
        Get weather multiplier for a specific product
        
        Args:
            product_title: Product title to analyze keywords
            category: Optional category name
        
        Returns:
            Multiplier (0.3 - 1.5)
        """
        weather = self.get_weighted_weather()
        weather_class = self.classify_weather(weather.get("temp", 25), weather.get("main", "Clear"))
        
        # Find matching category sensitivity
        title_lower = (product_title or "").lower()
        category_lower = (category or "").lower()
        search_text = f"{title_lower} {category_lower}"
        
        sensitivity = WEATHER_SENSITIVITY_KEYWORDS["_default"]
        for keyword, sens in WEATHER_SENSITIVITY_KEYWORDS.items():
            if keyword != "_default" and keyword in search_text:
                sensitivity = sens
                break
        
        multiplier = sensitivity.get(weather_class, 1.0)
        
        logger.info(f"[WEATHER] {weather_class} ({weather.get('temp', 0):.1f}°C) → "
                   f"'{product_title[:30]}...' → {multiplier:.2f}x")
        
        return multiplier
    
    def get_overall_multiplier(self) -> float:
        """
        Get overall weather multiplier for general sales
        Uses an average across categories
        """
        weather = self.get_weighted_weather()
        weather_class = self.classify_weather(weather.get("temp", 25), weather.get("main", "Clear"))
        
        # Simple overall multiplier
        base_multipliers = {
            "hot": 1.1,   # Hot = more impulse buys
            "warm": 1.0,  # Normal
            "cold": 0.95, # Cold = slightly less
            "rain": 1.08  # Rain = people stay home, shop online
        }
        
        return base_multipliers.get(weather_class, 1.0)


# Singleton
_service = None

def get_smart_weather_service() -> SmartWeatherService:
    global _service
    if _service is None:
        _service = SmartWeatherService()
    return _service

def get_weather_multiplier_for_product(title: str, category: str = None) -> float:
    """Convenience function for product-specific multiplier"""
    return get_smart_weather_service().get_category_multiplier(title, category)

def get_overall_weather_multiplier() -> float:
    """Convenience function for overall weather multiplier"""
    return get_smart_weather_service().get_overall_multiplier()
