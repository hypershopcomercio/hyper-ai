"""
Hyper Forecast - Calendar Multipliers
Adjustments based on day of week, period of month, and special events
"""
import logging
from datetime import datetime, date
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)


# Day of week multipliers (empirical e-commerce patterns)
# 0=Monday, 6=Sunday
DAY_OF_WEEK_MULTIPLIERS = {
    0: 0.85,   # Segunda - início de semana mais fraco
    1: 0.92,   # Terça
    2: 0.95,   # Quarta
    3: 1.00,   # Quinta - baseline
    4: 1.15,   # Sexta - pré-fim de semana
    5: 1.25,   # Sábado - pico
    6: 1.20,   # Domingo - alto mas menor que sábado
}

# Period of month multipliers (based on payment cycles in Brazil)
PERIOD_OF_MONTH_RANGES = [
    (1, 5, 1.35),    # Pós-pagamento, alto consumo
    (6, 10, 1.15),   # Ainda com dinheiro
    (11, 20, 0.85),  # Meio do mês, mais apertado
    (21, 25, 0.90),  # Pré-salário
    (26, 31, 1.10),  # Antecipação de compras
]

# Brazilian holidays and special events
SPECIAL_EVENTS = {
    # Fixed dates (MM-DD)
    "01-01": {"name": "Ano Novo", "mult": 0.40, "category_boost": []},
    "12-25": {"name": "Natal", "mult": 0.30, "category_boost": []},
    "12-24": {"name": "Véspera de Natal", "mult": 0.65, "category_boost": ["presentes"]},
    "12-31": {"name": "Véspera Ano Novo", "mult": 0.50, "category_boost": []},
    "10-12": {"name": "Dia das Crianças", "mult": 1.80, "category_boost": ["infantil", "brinquedos"]},
    "02-14": {"name": "Dia dos Namorados (BR: 12/06)", "mult": 1.00, "category_boost": []},
    "06-12": {"name": "Dia dos Namorados", "mult": 1.50, "category_boost": ["presentes", "joias"]},
    "08-11": {"name": "Dia dos Pais", "mult": 1.40, "category_boost": ["ferramentas", "eletronicos"]},
    "11-15": {"name": "Proclamação República", "mult": 1.10, "category_boost": []},
    "09-07": {"name": "Independência", "mult": 0.90, "category_boost": []},
    "04-21": {"name": "Tiradentes", "mult": 0.95, "category_boost": []},
    "05-01": {"name": "Dia do Trabalho", "mult": 0.85, "category_boost": []},
    
    # Mother's Day (second Sunday of May - approximate)
    "05-11": {"name": "Dia das Mães (aprox)", "mult": 1.60, "category_boost": ["cama_banho", "roupao", "presentes"]},
    "05-12": {"name": "Dia das Mães (aprox)", "mult": 1.60, "category_boost": ["cama_banho", "roupao", "presentes"]},
}

# Black Friday typically last Friday of November
# Will be calculated dynamically

# Seasonal patterns
SEASONAL_PATTERNS = {
    "verao": {
        "months": [12, 1, 2],
        "categories": {
            "piscina": 2.50,
            "boia": 2.80,
            "praia": 2.20,
            "ventilador": 1.80,
            "brinquedo_agua": 2.40,
        }
    },
    "inverno": {
        "months": [6, 7, 8],
        "categories": {
            "cobertor": 2.20,
            "manta": 2.40,
            "roupao": 1.90,
            "aquecedor": 2.50,
        }
    },
    "volta_aulas": {
        "months": [1, 2, 7, 8],
        "categories": {
            "papelaria": 1.60,
            "mochila": 1.80,
            "escolar": 1.70,
        }
    }
}


class CalendarMultipliers:
    """
    Provides calendar-based adjustment multipliers for forecasting
    """
    
    def __init__(self, custom_dow_pattern: Optional[Dict[int, float]] = None):
        """
        Initialize with optional custom day-of-week pattern from actual data
        """
        self.dow_pattern = custom_dow_pattern or DAY_OF_WEEK_MULTIPLIERS
    
    def get_day_of_week_multiplier(self, target_date: date) -> float:
        """
        Get multiplier based on day of week
        """
        dow = target_date.weekday()  # 0=Monday, 6=Sunday
        return self.dow_pattern.get(dow, 1.0)
    
    def get_period_of_month_multiplier(self, day_of_month: int) -> float:
        """
        Get multiplier based on period within month (payment cycle effect)
        """
        for start, end, mult in PERIOD_OF_MONTH_RANGES:
            if start <= day_of_month <= end:
                return mult
        return 1.0
    
    def get_event_multiplier(
        self, 
        target_date: date, 
        category: Optional[str] = None
    ) -> Tuple[float, Optional[str]]:
        """
        Get multiplier for special events/holidays
        Returns (multiplier, event_name or None)
        """
        date_key = target_date.strftime("%m-%d")
        
        if date_key in SPECIAL_EVENTS:
            event = SPECIAL_EVENTS[date_key]
            mult = event["mult"]
            
            # Additional boost if product category matches event
            if category and category.lower() in [c.lower() for c in event.get("category_boost", [])]:
                mult *= 1.30  # 30% extra boost for matching categories
            
            return mult, event["name"]
        
        # Check if it's Black Friday (last Friday of November)
        if target_date.month == 11:
            if self._is_black_friday(target_date):
                return 3.50, "Black Friday"
            # Days leading up to Black Friday
            bf_date = self._get_black_friday(target_date.year)
            days_until = (bf_date - target_date).days
            if 0 < days_until <= 7:
                return 1.30 + (0.1 * (7 - days_until)), f"Semana Black Friday (-{days_until}d)"
        
        return 1.0, None
    
    def get_seasonal_multiplier(
        self, 
        target_date: date, 
        category: Optional[str] = None
    ) -> Tuple[float, Optional[str]]:
        """
        Get seasonal multiplier for product category
        """
        if not category:
            return 1.0, None
        
        month = target_date.month
        category_lower = category.lower()
        
        for season_name, config in SEASONAL_PATTERNS.items():
            if month in config["months"]:
                for cat_pattern, mult in config["categories"].items():
                    if cat_pattern in category_lower:
                        return mult, season_name
        
        return 1.0, None
    
    def get_all_calendar_multipliers(
        self, 
        target_date: date,
        category: Optional[str] = None
    ) -> Dict:
        """
        Get all calendar-related multipliers combined
        """
        dow_mult = self.get_day_of_week_multiplier(target_date)
        period_mult = self.get_period_of_month_multiplier(target_date.day)
        event_mult, event_name = self.get_event_multiplier(target_date, category)
        season_mult, season_name = self.get_seasonal_multiplier(target_date, category)
        
        # Combined multiplier
        combined = dow_mult * period_mult * event_mult * season_mult
        
        return {
            "day_of_week": dow_mult,
            "period_of_month": period_mult,
            "event": event_mult,
            "event_name": event_name,
            "seasonal": season_mult,
            "season_name": season_name,
            "combined": combined
        }
    
    def _is_black_friday(self, target_date: date) -> bool:
        """Check if date is Black Friday"""
        if target_date.month != 11 or target_date.weekday() != 4:
            return False
        
        # Last Friday of November
        bf = self._get_black_friday(target_date.year)
        return target_date == bf
    
    def _get_black_friday(self, year: int) -> date:
        """Get Black Friday date for a given year"""
        # Find last Friday of November
        # Start from Nov 30 and go back to find Friday
        nov_30 = date(year, 11, 30)
        days_since_friday = (nov_30.weekday() - 4) % 7
        return nov_30 - __import__('datetime').timedelta(days=days_since_friday)
