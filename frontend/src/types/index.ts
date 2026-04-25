export interface Ad {
    id: string;
    title: string;
    price: number;
    status: string;
    thumbnail: string;
    available_quantity: number;
    sold_quantity: number;
    total_visits: number;
    cost: number;
    conversion_rate: number;
    permalink?: string;
    tiny_id?: string;
    weight_g?: number;
    updated_at?: string;
    last_updated?: string;
    created_at?: string;

    // Media & Content
    pictures?: { id: string; url: string; secure_url?: string; size?: string; max_size?: string; quality?: string }[];
    video_id?: string;
    short_description?: string;
    manual_video_verified?: boolean;

    // Prices
    original_price?: number;
    promotion_price?: number;

    // Tiny & Financials
    sku?: string;
    margin_percent?: number;
    margin_value?: number;
    is_margin_alert?: boolean;
    intelligence?: {
        pricing?: {
            score: number;
            label: string;
            suggestion: string;
            action: string;
            analysis: string;
        };
        stock?: {
            days_of_stock: number;
            label: string;
            suggestion: string;
            action: string;
            status: string;
            analysis: string;
        };
        health?: {
            score: number;
            status: 'excellent' | 'warning' | 'critical';
            label: string;
            all_issues?: string[]; // Optional if not always present
            sections: {
                title: { score: number; max_score: number; criteria: { label: string; met: boolean; score: number; max_score: number; hint?: string }[]; issues: string[] };
                media: { score: number; max_score: number; criteria: { label: string; met: boolean; score: number; max_score: number; hint?: string }[]; issues: string[] };
                attributes: { score: number; max_score: number; criteria: { label: string; met: boolean; score: number; max_score: number; hint?: string }[]; issues: string[] };
            };
        };
    };

    // Margin Defense
    target_margin?: number;
    suggested_price?: number;
    strategy_start_price?: number;
    current_step_number?: number;

    // Added for Sync/Supply modules
    stock_local?: number;
    days_to_run_out?: number; // Calculated backend side
    days_of_stock?: number;
    risk_value?: number;
    sales_30d?: number;
    visits_30d?: number;
    visits_7d_change?: number;
    sales_7d_change?: number;

    // Logistics & Stock
    is_full?: boolean;
    shipping_mode?: string;
    listing_type_id?: string;
    health_score?: number;
    start_time?: string;
    is_catalog?: boolean;

    // Flat fields from list view
    tax_cost?: number;
    commission_cost?: number;
    shipping_cost?: number;
    ads_spend_30d?: number;
    stock_incoming?: number;
    fixed_cost_share?: number;
    return_risk_cost?: number;
    storage_cost?: number;
    daily_storage_fee?: number;
    inbound_freight_cost?: number;
    storage_risk_cost?: number;
    stock_status?: string;
    effective_price?: number;

    financials?: {
        commission_cost: number;
        shipping_cost: number;
        tax_cost: number;
        fixed_cost_share?: number;
        return_risk_cost?: number;
        storage_cost?: number;
        net_margin_value?: number;
        net_margin_percent?: number;
        inbound_freight_cost?: number;
        daily_storage_fee?: number;
        storage_risk_cost?: number;
    };

    history?: {
        date: string;
        visits: number;
        sales: number;
        revenue?: number;
    }[];

    // Aggregated Lifetime Data
    total_revenue?: number;
    ads_lifetime?: {
        total_spend: number;
        total_revenue: number;
        roas: number;
        acos: number;
    };
}

export interface DashboardMetrics {
    total_ads: number;
    total_visits: number;
    total_sales: number;
    total_revenue: number;
    average_margin: number;
    conversion_rate_global?: number; // Optional if not used or calculated frontend side
}
