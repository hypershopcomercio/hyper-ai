/**
 * Hyper AI Translation Utility
 * Maps technical keys and types to user-friendly Portuguese labels.
 */

export const factorTypeTranslations: Record<string, string> = {
    'hourly_pattern': 'Horário',
    'day_of_week': 'Dia da Semana',
    'period_of_month': 'Período do Mês',
    'period_of_day': 'Período do Dia',
    'seasonal': 'Sazonalidade',
    'momentum': 'Tendência',
    'stock': 'Estoque',
    'weather': 'Clima',
    'event': 'Evento',
    'catalog_boost': 'Catálogo',
    'impulse_hours': 'Impulso',
    'holiday': 'Feriado',
    'promotion': 'Promoção'
};

export const factorKeyTranslations: Record<string, string> = {
    // Days of week
    'segunda': 'Segunda-feira',
    'terca': 'Terça-feira',
    'quarta': 'Quarta-feira',
    'quinta': 'Quinta-feira',
    'sexta': 'Sexta-feira',
    'sabado': 'Sábado',
    'domingo': 'Domingo',

    // Period of month
    'inicio': 'Início do Mês',
    'meio': 'Meio do Mês',
    'fim': 'Fim do Mês',

    // Period of day
    'madrugada': 'Madrugada',
    'manha': 'Manhã',
    'tarde': 'Tarde',
    'noite': 'Noite',

    // Catalog / Source
    'catalogo': 'Catálogo Principal',
    'oficial': 'Loja Oficial',
    'parceiro': 'Parceiro',

    // Weather
    'hot': 'Calor',
    'cold': 'Frio',
    'rain': 'Chuva',
    'clear': 'Céu Limpo',
    'clouds': 'Nublado',

    // Impulse
    'active': 'Ativo',
    'none': 'Nenhum',

    // Product Specific Factors
    'catalog_boost': 'Impulso de Catálogo',
    'competitor_stockout': 'Stockout Concorrência',
    'conversion_rate': 'Taxa de Conversão',
    'free_shipping': 'Frete Grátis',
    'gold_medal': 'Medalha Mercado Líder',
    'listing_health': 'Saúde do Anúncio',
    'listing_type': 'Tipo de Anúncio',
    'price_competitiveness': 'Competitividade de Preço',
    'promo_active': 'Promoção Ativa',
    'search_position': 'Posicionamento de Busca',
    'shipping_advantage': 'Vantagem de Frete',
    'stock_pressure': 'Pressão de Estoque',
    'top_sellers': 'Top Sellers',
    'velocity_score': 'Score de Velocidade',
    'visits_trend': 'Tendência de Visitas'
};

/**
 * Translates a factor type to a human-readable string.
 */
export function translateFactorType(type: string): string {
    if (!type) return 'Fator';
    const cleanType = type.toLowerCase().trim();
    return factorTypeTranslations[cleanType] || type.replace(/_/g, ' ');
}

/**
 * Translates a factor key to a human-readable string.
 */
export function translateFactorKey(key: string | number, type?: string): string {
    if (key === null || key === undefined) return '-';

    const keyStr = String(key).toLowerCase().trim();

    // Special case for hourly pattern (e.g. "22h") - usually already readable
    if (type === 'hourly_pattern' && keyStr.endsWith('h')) {
        return keyStr;
    }

    // Check direct mapping
    if (factorKeyTranslations[keyStr]) {
        return factorKeyTranslations[keyStr];
    }

    // Fallback: clean string
    return String(key).replace(/_/g, ' ');
}

/**
 * Returns a combined label like "Horário: 22h" or "Dia da Semana: Sábado"
 */
export function getFactorLabel(type: string, key: string | number): string {
    const t = translateFactorType(type);
    const k = translateFactorKey(key, type);

    // If the key already includes the type name, just return the key
    if (k.toLowerCase().includes(t.toLowerCase())) {
        return k;
    }

    return `${t}: ${k}`;
}
