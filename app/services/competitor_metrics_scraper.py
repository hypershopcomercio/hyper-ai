"""
Serviço de scraping de métricas de concorrentes via API do Mercado Livre.

Coleta dados públicos disponíveis: preço, vendas, visitas, reputação, etc.
"""
import logging
from typing import Dict, Optional
from datetime import datetime
import requests
from sqlalchemy.orm import Session
from app.models.competitor_intelligence import CompetitorMetricsHistory
from app.models.ad import Ad

logger = logging.getLogger(__name__)

ML_API_BASE = "https://api.mercadolibre.com"


class CompetitorMetricsScraper:
    """
    Scraper de métricas públicas de concorrentes no Mercado Livre.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def fetch_competitor_item_data(self, ml_id: str) -> Optional[Dict]:
        """
        Busca dados públicos de um item do ML via API.
        
        Args:
            ml_id: ID do MLB (ex: MLB1234567890)
            
        Returns:
            Dict com dados do item ou None se falhar
        """
        try:
            # Endpoint público de informações do item
            url = f"{ML_API_BASE}/items/{ml_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"ML API retornou {response.status_code} para {ml_id}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar dados do ML para {ml_id}: {e}")
            return None
    
    def fetch_competitor_visits(self, ml_id: str) -> Optional[int]:
        """
        Busca quantidade de visitas do item (via endpoint público).
        
        Nota: A API do ML expõe visitas em alguns endpoints públicos,
        mas pode ser necessário autenticação para dados mais detalhados.
        """
        try:
            # Endpoint de visitas (pode variar dependendo da disponibilidade)
            url = f"{ML_API_BASE}/items/{ml_id}/visits"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # ML retorna total de visitas históricas
                return data.get('total', 0)
            else:
                logger.debug(f"Visits endpoint não disponível para {ml_id}")
                return None
                
        except Exception as e:
            logger.debug(f"Não foi possível obter visitas para {ml_id}: {e}")
            return None
    
    def extract_metrics_from_item(self, item_data: Dict) -> Dict:
        """
        Extrai métricas relevantes dos dados do item.
        
        Args:
            item_data: Resposta JSON da API /items/{id}
            
        Returns:
            Dict com métricas processadas
        """
        metrics = {}
        
        try:
            # Preço
            metrics['price'] = item_data.get('price', 0)
            
            # Vendas (quantidade vendida)
            metrics['sales'] = item_data.get('sold_quantity', 0)
            
            # Stock disponível
            metrics['stock_available'] = item_data.get('available_quantity', 0)
            
            # Frete grátis
            shipping = item_data.get('shipping', {})
            metrics['has_free_shipping'] = shipping.get('free_shipping', False)
            
            # Promoção ativa (verifica se há desconto ou preço original diferente)
            original_price = item_data.get('original_price')
            current_price = metrics['price']
            metrics['has_promotion'] = original_price is not None and original_price > current_price
            
            # Reputação do vendedor
            seller_id = item_data.get('seller_id')
            if seller_id:
                seller_metrics = self._fetch_seller_reputation(seller_id)
                metrics.update(seller_metrics)
            
            # Status/saúde do anúncio
            metrics['status'] = item_data.get('status', 'unknown')
            
        except Exception as e:
            logger.error(f"Erro ao extrair métricas: {e}")
        
        return metrics
    
    def _fetch_seller_reputation(self, seller_id: int) -> Dict:
        """
        Busca métricas de reputação do vendedor.
        """
        try:
            url = f"{ML_API_BASE}/users/{seller_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                seller_rep = data.get('seller_reputation', {})
                
                return {
                    'seller_reputation': seller_rep.get('level_id', 'unknown'),  # red, orange, yellow, light_green, green
                    'rating': seller_rep.get('power_seller_status'),  # Pode variar
                    'reviews_count': seller_rep.get('transactions', {}).get('total', 0)
                }
        except Exception as e:
            logger.debug(f"Não foi possível obter reputação do vendedor {seller_id}: {e}")
        
        return {
            'seller_reputation': 'unknown',
            'rating': None,
            'reviews_count': 0
        }
    
    def collect_and_save_metrics(self, competitor_ml_id: str, our_ad_id: str) -> bool:
        """
        Coleta métricas do concorrente e salva no histórico.
        
        Args:
            competitor_ml_id: MLB ID do concorrente
            our_ad_id: MLB ID do nosso anúncio
            
        Returns:
            True se sucesso, False se falhar
        """
        try:
            # 1. Buscar dados do concorrente
            item_data = self.fetch_competitor_item_data(competitor_ml_id)
            if not item_data:
                logger.warning(f"Não foi possível obter dados do concorrente {competitor_ml_id}")
                return False
            
            # 2. Extrair métricas
            metrics = self.extract_metrics_from_item(item_data)
            
            # 3. Tentar buscar visitas (se disponível)
            visits = self.fetch_competitor_visits(competitor_ml_id)
            metrics['visits'] = visits
            
            # 4. Calcular conversão (se temos visitas)
            if visits and visits > 0:
                metrics['conversion_rate'] = (metrics.get('sales', 0) / visits) * 100
            else:
                metrics['conversion_rate'] = None
            
            # 5. Buscar nossas métricas atuais para snapshot comparativo
            our_ad = self.db.query(Ad).filter(Ad.id == our_ad_id).first()
            our_metrics = {}
            
            if our_ad:
                our_metrics = {
                    'our_price': our_ad.price,
                    'our_visits': getattr(our_ad, 'visits', None),
                    'our_sales': getattr(our_ad, 'sales', None),
                    'our_conversion_rate': None,  # Calcular se tiver visitas
                    'our_search_position': None  # TODO: implementar scraping de posição
                }
            
            # 6. Criar registro no histórico
            history_entry = CompetitorMetricsHistory(
                competitor_id=competitor_ml_id,
                our_ad_id=our_ad_id,
                timestamp=datetime.utcnow(),
                
                # Métricas do concorrente
                price=metrics.get('price'),
                visits=metrics.get('visits'),
                sales=metrics.get('sales'),
                conversion_rate=metrics.get('conversion_rate'),
                stock_available=metrics.get('stock_available'),
                has_free_shipping=metrics.get('has_free_shipping'),
                has_promotion=metrics.get('has_promotion'),
                seller_reputation=metrics.get('seller_reputation'),
                reviews_count=metrics.get('reviews_count'),
                
                # Nossas métricas (snapshot)
                **our_metrics
            )
            
            self.db.add(history_entry)
            self.db.commit()
            
            logger.info(f"✅ Métricas coletadas para concorrente {competitor_ml_id}: Preço R${metrics.get('price')}, Vendas {metrics.get('sales')}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao coletar e salvar métricas do concorrente {competitor_ml_id}: {e}")
            self.db.rollback()
            return False
    
    def collect_all_competitors_metrics(self, our_ad_id: str):
        """
        Coleta métricas de todos os concorrentes monitorados para um anúncio.
        
        Args:
            our_ad_id: MLB ID do nosso anúncio
        """
        # TODO: Buscar lista de concorrentes do banco de dados
        # Por enquanto, placeholder
        logger.info(f"Coletando métricas de todos concorrentes para {our_ad_id}")
        
        # Implementar quando tivermos modelo de Competitor
        pass
