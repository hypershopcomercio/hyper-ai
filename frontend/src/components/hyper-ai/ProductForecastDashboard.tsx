'use client';

import React, { useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import { Package, RefreshCw, Filter, TrendingUp, TrendingDown, AlertCircle, ShoppingCart, Truck, CheckCircle2, Minus, Activity, Zap, Clock, Info, ChevronUp, ChevronDown, ArrowUpDown } from 'lucide-react';
import { Tooltip } from '@/components/ui/Tooltip';

interface ProductForecast {
    mlb_id: string;
    title: string;
    thumbnail: string;
    sku: string;
    category: string;
    curve: string;
    price: number;
    cost: number;
    margin_pct: number;
    avg_units_7d: number;
    avg_units_30d: number;
    total_units_7d: number;
    total_revenue_7d: number;
    trend: string;
    trend_pct: number;
    stock_current: number;
    stock_full: number;
    stock_local: number;
    stock_incoming: number;
    days_of_coverage: number;
    stock_status: string;
    has_rupture_risk: boolean;
    forecast_units_today: number;
    forecast_revenue_today: number;
}

interface Summary {
    total_products: number;
    total_forecast_today: number;
    rupture_risk_count: number;
    stockout_count: number;
    curve_a: number;
    curve_b: number;
    curve_c: number;
}

const api = {
    get: async (url: string) => {
        const res = await fetch(`http://localhost:5000/api${url}`);
        return res.json();
    },
    post: async (url: string) => {
        const res = await fetch(`http://localhost:5000/api${url}`, { method: 'POST' });
        return res.json();
    }
};

export interface ProductForecastDashboardRef {
    handleSync: () => Promise<void>;
    isSyncing: boolean;
}

const ProductForecastDashboard = forwardRef<ProductForecastDashboardRef, {}>((props, ref) => {
    const [products, setProducts] = useState<ProductForecast[]>([]);
    const [summary, setSummary] = useState<Summary | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isSyncing, setIsSyncing] = useState(false);
    const [filter, setFilter] = useState<'all' | 'rupture' | 'a' | 'b' | 'c'>('all');
    const [hideOutOfStock, setHideOutOfStock] = useState(false);
    const [sortKey, setSortKey] = useState<'curve' | 'avg_units_7d' | 'trend_pct' | 'days_of_coverage' | 'stock_current'>('days_of_coverage');
    const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');

    // Sort handler
    const handleSort = (key: typeof sortKey) => {
        if (sortKey === key) {
            setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
        } else {
            setSortKey(key);
            setSortDir(key === 'days_of_coverage' ? 'asc' : 'desc');
        }
    };

    // Sorted products
    const sortedProducts = [...products].sort((a, b) => {
        let aVal: number = 0;
        let bVal: number = 0;

        if (sortKey === 'curve') {
            const curveOrder: Record<string, number> = { 'A': 3, 'B': 2, 'C': 1 };
            aVal = curveOrder[a.curve] || 0;
            bVal = curveOrder[b.curve] || 0;
        } else {
            aVal = a[sortKey] as number;
            bVal = b[sortKey] as number;
        }

        if (sortDir === 'asc') return aVal - bVal;
        return bVal - aVal;
    });

    const fetchData = async () => {
        try {
            let url = '/forecast/products';
            if (filter === 'rupture') url += '?rupture_only=true';
            else if (filter === 'a') url += '?curve=A';
            else if (filter === 'b') url += '?curve=B';
            else if (filter === 'c') url += '?curve=C';

            const prodRes = await api.get(url);
            if (prodRes.success) {
                setProducts(prodRes.data.products);
                setSummary(prodRes.data.summary);
            }
        } catch (error) {
            console.error('Error fetching data:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSync = async () => {
        setIsSyncing(true);
        try {
            await api.post('/forecast/products/sync');
            await fetchData();
        } catch (error) {
            console.error('Error syncing:', error);
        } finally {
            setIsSyncing(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [filter]);

    const getTrendIcon = (trend: string, pct: number) => {
        if (trend === 'up') return <TrendingUp className="w-4 h-4 text-emerald-400" />;
        if (trend === 'down') return <TrendingDown className="w-4 h-4 text-red-400" />;
        return <Minus className="w-4 h-4 text-slate-400" />;
    };

    const getCurveBadge = (curve: string) => {
        const styles: Record<string, string> = {
            A: 'bg-purple-500/20 text-purple-400 border border-purple-500/30',
            B: 'bg-blue-500/20 text-blue-400 border border-blue-500/30',
            C: 'bg-slate-500/20 text-slate-400 border border-slate-500/30'
        };
        return (
            <span className={`px-2 py-0.5 rounded text-xs font-bold ${styles[curve] || styles.C}`}>
                {curve || '-'}
            </span>
        );
    };

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
    };

    useImperativeHandle(ref, () => ({
        handleSync,
        isSyncing
    }));

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Summary Cards */}
            {summary && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="premium-border-container group/card">
                        <div className="premium-border-beam" />
                        <div className="premium-card rounded-xl p-4 h-full relative">
                            <div className="flex justify-between items-start mb-2">
                                <div className="text-slate-400 text-sm flex items-center gap-1.5 font-medium">
                                    Previsão Hoje
                                    <Tooltip
                                        title="Previsão de Faturamento"
                                        content="Faturamento projetado para hoje com base na inteligência do Hyper AI, considerando histórico e fatores dinâmicos."
                                    >
                                        <Info className="w-3.5 h-3.5 text-slate-600 group-hover/card:text-cyan-400 transition-colors cursor-help" />
                                    </Tooltip>
                                </div>
                                <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400">
                                    <TrendingUp className="w-4 h-4 animate-pulse" />
                                </div>
                            </div>
                            <p className="text-2xl font-bold text-white group-hover/card:text-cyan-400 transition-colors">{formatCurrency(summary.total_forecast_today)}</p>
                        </div>
                    </div>
                    <div className="premium-border-container group/card">
                        <div className="premium-border-beam" />
                        <div className="premium-card rounded-xl p-4 h-full relative">
                            <div className="flex justify-between items-start mb-2">
                                <div className="text-slate-400 text-sm flex items-center gap-1.5 font-medium">
                                    Produtos Ativos
                                    <Tooltip
                                        title="Inventário Ativo"
                                        content="Quantidade total de anúncios ativos no Mercado Livre que estão sincronizados e sendo monitorados pelo Hyper AI."
                                    >
                                        <Info className="w-3.5 h-3.5 text-slate-600 group-hover/card:text-blue-400 transition-colors cursor-help" />
                                    </Tooltip>
                                </div>
                                <div className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400">
                                    <Package className="w-4 h-4" />
                                </div>
                            </div>
                            <p className="text-2xl font-bold text-white">{summary.total_products}</p>
                        </div>
                    </div>
                    <div className="premium-border-container group/card">
                        <div className="premium-border-beam" />
                        <div className="premium-card rounded-xl p-4 h-full relative">
                            <div className="flex justify-between items-start mb-2">
                                <div className="text-slate-400 text-sm flex items-center gap-1.5 font-medium">
                                    Risco de Ruptura
                                    <Tooltip
                                        title="Alerta de Ruptura"
                                        content="Produtos com estoque projetado para zerar nos próximos dias. Considera estoque local, Full e em trânsito."
                                    >
                                        <Info className="w-3.5 h-3.5 text-slate-600 group-hover/card:text-orange-400 transition-colors cursor-help" />
                                    </Tooltip>
                                </div>
                                <div className="p-1.5 rounded-lg bg-orange-500/10 text-orange-400">
                                    <AlertCircle className="w-4 h-4" />
                                </div>
                            </div>
                            <p className="text-2xl font-bold text-white group-hover/card:text-orange-400 transition-colors">{summary.rupture_risk_count}</p>
                        </div>
                    </div>
                    <div className="premium-border-container group/card">
                        <div className="premium-border-beam" />
                        <div className="premium-card rounded-xl p-4 h-full relative">
                            <div className="flex justify-between items-start mb-2">
                                <div className="text-slate-400 text-sm flex items-center gap-1.5 font-medium">
                                    Curva ABC
                                    <Tooltip
                                        title="Classificação ABC"
                                        content="Curva A (80% da receita), Curva B (15%) e Curva C (5%). Essencial para priorizar reposições."
                                    >
                                        <Info className="w-3.5 h-3.5 text-slate-600 group-hover/card:text-purple-400 transition-colors cursor-help" />
                                    </Tooltip>
                                </div>
                                <div className="p-1.5 rounded-lg bg-purple-500/10 text-purple-400">
                                    <Filter className="w-4 h-4" />
                                </div>
                            </div>
                            <div className="flex gap-2 mt-1">
                                <span className="px-2 py-1 bg-purple-500/10 text-purple-400 rounded text-[10px] font-bold border border-purple-500/20">A:{summary.curve_a}</span>
                                <span className="px-2 py-1 bg-blue-500/10 text-blue-400 rounded text-[10px] font-bold border border-blue-500/20">B:{summary.curve_b}</span>
                                <span className="px-2 py-1 bg-slate-500/10 text-slate-400 rounded text-[10px] font-bold border border-slate-500/20">C:{summary.curve_c}</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Filters Row */}
            <div className="flex flex-col md:flex-row md:items-center gap-4">
                <div className="flex flex-wrap gap-2">
                    <button
                        onClick={() => setFilter('all')}
                        className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 border cursor-pointer ${filter === 'all'
                            ? 'bg-cyan-500/20 text-cyan-400 border-cyan-500/40 shadow-[0_0_15px_rgba(34,211,238,0.1)]'
                            : 'bg-slate-900/40 text-slate-500 border-slate-800/50 hover:text-slate-300 hover:border-slate-700'
                            }`}
                    >
                        Todos
                    </button>
                    <button
                        onClick={() => setFilter('rupture')}
                        className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 border cursor-pointer flex items-center gap-2 ${filter === 'rupture'
                            ? 'bg-orange-500/20 text-orange-400 border-orange-500/40 shadow-[0_0_15px_rgba(249,115,22,0.1)]'
                            : 'bg-slate-900/40 text-slate-500 border-slate-800/50 hover:text-slate-300 hover:border-slate-700'
                            }`}
                    >
                        <AlertCircle className="w-4 h-4" />
                        Risco Ruptura
                    </button>
                    <button
                        onClick={() => setFilter('a')}
                        className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 border cursor-pointer ${filter === 'a'
                            ? 'bg-purple-500/20 text-purple-400 border-purple-500/40 shadow-[0_0_15px_rgba(168,85,247,0.1)]'
                            : 'bg-slate-900/40 text-slate-500 border-slate-800/50 hover:text-slate-300 hover:border-slate-700'
                            }`}
                    >
                        Curva A
                    </button>
                    <button
                        onClick={() => setFilter('b')}
                        className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 border cursor-pointer ${filter === 'b'
                            ? 'bg-blue-500/20 text-blue-400 border-blue-500/40 shadow-[0_0_15px_rgba(59,130,246,0.1)]'
                            : 'bg-slate-900/40 text-slate-500 border-slate-800/50 hover:text-slate-300 hover:border-slate-700'
                            }`}
                    >
                        Curva B
                    </button>
                    <button
                        onClick={() => setFilter('c')}
                        className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 border cursor-pointer ${filter === 'c'
                            ? 'bg-slate-700/40 text-slate-400 border-slate-600/40'
                            : 'bg-slate-900/40 text-slate-500 border-slate-800/50 hover:text-slate-300 hover:border-slate-700'
                            }`}
                    >
                        Curva C
                    </button>
                </div>

                <div className="flex-1" />

                <button
                    onClick={() => setHideOutOfStock(!hideOutOfStock)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider transition-all duration-300 border cursor-pointer ${hideOutOfStock
                        ? 'bg-orange-500/20 text-orange-400 border-orange-500/40 shadow-[0_0_15px_rgba(249,115,22,0.1)]'
                        : 'bg-slate-900/40 text-slate-500 border-slate-800/50 hover:text-white hover:border-slate-700'
                        }`}
                    title="Ocultar produtos com estoque zero e sem entrada pendente"
                >
                    <Filter className="w-4 h-4" />
                    {hideOutOfStock ? 'Ocultando Ruptura' : 'Mostrar Ruptura'}
                </button>
            </div>

            {/* Products Table */}
            <div className="premium-border-container shadow-2xl">
                <div className="premium-border-beam" />
                <div className="premium-card rounded-xl relative" style={{ overflow: 'visible' }}>
                    <div className="overflow-x-auto overflow-y-visible">
                        <table className="w-full">
                            <thead className="sticky top-0 z-10 bg-[#0a0a0f] border-t border-slate-800/50">
                                <tr className="text-left text-slate-500 text-[10px] uppercase tracking-widest border-b border-slate-800/50">
                                    <th className="px-4 py-3 font-bold whitespace-nowrap border-r border-slate-800/30 last:border-r-0">
                                        <div className="flex items-center gap-1.5">
                                            <Package className="w-3 h-3" />
                                            Produto
                                        </div>
                                    </th>
                                    <th
                                        className="px-4 py-3 font-bold whitespace-nowrap border-r border-slate-800/30 last:border-r-0 cursor-pointer hover:bg-slate-800/50 hover:text-cyan-400 transition-colors group"
                                        onClick={() => handleSort('curve')}
                                    >
                                        <div className="flex items-center gap-1.5">
                                            <TrendingUp className="w-3 h-3" />
                                            Curva
                                            {sortKey === 'curve' && (sortDir === 'asc' ? <ChevronUp className="w-3 h-3 text-cyan-400" /> : <ChevronDown className="w-3 h-3 text-cyan-400" />)}
                                        </div>
                                    </th>
                                    <th
                                        className="px-4 py-3 font-bold whitespace-nowrap border-r border-slate-800/30 last:border-r-0 cursor-pointer hover:bg-slate-800/50 hover:text-cyan-400 transition-colors group"
                                        onClick={() => handleSort('avg_units_7d')}
                                    >
                                        <div className="flex items-center gap-1.5">
                                            <Activity className="w-3 h-3" />
                                            Giro Médio
                                            {sortKey === 'avg_units_7d' && (sortDir === 'asc' ? <ChevronUp className="w-3 h-3 text-cyan-400" /> : <ChevronDown className="w-3 h-3 text-cyan-400" />)}
                                        </div>
                                    </th>
                                    <th
                                        className="px-4 py-3 font-bold whitespace-nowrap border-r border-slate-800/30 last:border-r-0 cursor-pointer hover:bg-slate-800/50 hover:text-cyan-400 transition-colors group"
                                        onClick={() => handleSort('trend_pct')}
                                    >
                                        <div className="flex items-center gap-1.5">
                                            <TrendingUp className="w-3 h-3" />
                                            Tendência
                                            {sortKey === 'trend_pct' && (sortDir === 'asc' ? <ChevronUp className="w-3 h-3 text-cyan-400" /> : <ChevronDown className="w-3 h-3 text-cyan-400" />)}
                                        </div>
                                    </th>
                                    <th
                                        className="px-4 py-3 font-bold text-center whitespace-nowrap border-r border-slate-800/30 last:border-r-0 cursor-pointer hover:bg-slate-800/50 hover:text-cyan-400 transition-colors group"
                                        onClick={() => handleSort('stock_current')}
                                    >
                                        <div className="flex items-center justify-center gap-1.5">
                                            <ShoppingCart className="w-3 h-3" />
                                            Estoque
                                            {sortKey === 'stock_current' && (sortDir === 'asc' ? <ChevronUp className="w-3 h-3 text-cyan-400" /> : <ChevronDown className="w-3 h-3 text-cyan-400" />)}
                                        </div>
                                    </th>
                                    <th
                                        className="px-4 py-3 font-bold whitespace-nowrap border-r border-slate-800/30 last:border-r-0 cursor-pointer hover:bg-slate-800/50 hover:text-cyan-400 transition-colors group"
                                        onClick={() => handleSort('days_of_coverage')}
                                    >
                                        <div className="flex items-center gap-1.5">
                                            <Clock className="w-3 h-3" />
                                            Cobertura
                                            {sortKey === 'days_of_coverage' && (sortDir === 'asc' ? <ChevronUp className="w-3 h-3 text-cyan-400" /> : <ChevronDown className="w-3 h-3 text-cyan-400" />)}
                                        </div>
                                    </th>

                                    <th className="px-4 py-3 font-bold text-center whitespace-nowrap bg-cyan-500/5">
                                        <div className="flex items-center justify-center gap-1.5 text-cyan-400">
                                            <Activity className="w-3 h-3" />
                                            Ação Sugerida
                                        </div>
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800/50">
                                {sortedProducts
                                    .filter(p => !hideOutOfStock || p.stock_current > 0 || p.stock_incoming > 0)
                                    .map((product) => (
                                        <tr
                                            key={product.mlb_id}
                                            className="hover:bg-[#1a1c22] border-b border-slate-700/40 group transition-colors odd:bg-slate-900/20"
                                        >
                                            <td className="px-4 py-2">
                                                <div className="flex items-center gap-3">
                                                    {product.thumbnail ? (
                                                        <div className="w-8 h-8 rounded-md overflow-hidden bg-white border border-slate-800/50 flex-shrink-0">
                                                            <img src={product.thumbnail} alt="" className="w-full h-full object-contain" />
                                                        </div>
                                                    ) : (
                                                        <div className="w-8 h-8 rounded-md bg-slate-800 border border-slate-700/50 flex items-center justify-center flex-shrink-0">
                                                            <Package className="w-4 h-4 text-slate-600" />
                                                        </div>
                                                    )}
                                                    <div className="flex flex-col max-w-[200px]">
                                                        <p className="text-white font-medium text-xs group-hover:text-cyan-400 transition-colors leading-tight truncate" title={product.title}>{product.title}</p>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-4 py-4">{getCurveBadge(product.curve)}</td>
                                            <td className="px-4 py-4">
                                                <div className="flex items-baseline gap-1.5">
                                                    <span className="text-sm font-bold text-cyan-400">{product.avg_units_7d.toFixed(1)}</span>
                                                    <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">un/dia</span>
                                                </div>
                                            </td>
                                            <td className="px-4 py-4">
                                                <div className="flex items-center gap-1.5 p-1 rounded-lg bg-slate-900/30 w-fit">
                                                    {getTrendIcon(product.trend, product.trend_pct)}
                                                    <span className={`text-xs font-bold ${product.trend === 'up' ? 'text-emerald-400' :
                                                        product.trend === 'down' ? 'text-red-400' : 'text-slate-400'
                                                        }`}>
                                                        {Math.abs(product.trend_pct) > 999 ? '>999%' : `${product.trend_pct > 0 ? '+' : ''}${product.trend_pct.toFixed(0)}%`}
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="px-4 py-2">
                                                <div className="flex items-center justify-center gap-4 min-w-[120px]">
                                                    <div className="flex flex-col items-center">
                                                        <span className="text-[8px] text-slate-500 uppercase font-black tracking-tighter leading-none mb-1">Full</span>
                                                        <span className="text-[11px] text-white font-bold">{product.stock_full}</span>
                                                    </div>
                                                    <div className="w-px h-4 bg-slate-800/50" />
                                                    <div className="flex flex-col items-center">
                                                        <span className="text-[8px] text-slate-500 uppercase font-black tracking-tighter leading-none mb-1">Local</span>
                                                        <span className="text-[11px] text-slate-300 font-bold">{product.stock_local}</span>
                                                    </div>
                                                    <div className="w-px h-4 bg-slate-800/50" />
                                                    <div className="flex flex-col items-center">
                                                        <span className="text-[8px] text-slate-500 uppercase font-black tracking-tighter leading-none mb-1">Trans</span>
                                                        <span className="text-[11px] text-blue-400 font-bold">{product.stock_incoming}</span>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-4 py-2">
                                                <Tooltip
                                                    title="Cobertura de Estoque"
                                                    content={
                                                        (() => {
                                                            const leadTime = 9;
                                                            const marginDays = product.curve === 'A' ? 4 : product.curve === 'B' ? 3 : 2;
                                                            const targetDays = leadTime + marginDays;

                                                            return (
                                                                <div className="flex flex-col gap-2 p-1 min-w-[200px]">
                                                                    <span className="text-xs leading-relaxed">
                                                                        Dias restantes de estoque. A linha <span className="text-cyan-400 font-bold">azul</span> marca a meta ideal.
                                                                    </span>

                                                                    <div className="bg-slate-950/50 p-2 rounded border border-slate-800 flex justify-between items-center gap-3">
                                                                        <span className="text-[10px] text-slate-400 uppercase tracking-wider font-bold">Meta Dinâmica</span>
                                                                        <span className="text-cyan-400 font-mono font-bold text-sm">{targetDays} dias</span>
                                                                    </div>

                                                                    <div className="text-[10px] text-slate-500 flex flex-col gap-1">
                                                                        <div className="flex justify-between">
                                                                            <span>Tempo de Reposição (Lead Time):</span>
                                                                            <span className="font-mono text-slate-400">{leadTime}d</span>
                                                                        </div>
                                                                        <div className="flex justify-between">
                                                                            <span>Margem Curva {product.curve}:</span>
                                                                            <span className="font-mono text-slate-400">{marginDays}d</span>
                                                                        </div>
                                                                    </div>

                                                                    <div className="h-px bg-slate-800 my-1" />

                                                                    <div className="flex gap-3 text-[10px]">
                                                                        <span className="flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-rose-500" /> Urgente</span>
                                                                        <span className="flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-amber-500" /> Atenção</span>
                                                                        <span className="flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> Saudável</span>
                                                                    </div>
                                                                </div>
                                                            );
                                                        })()
                                                    }
                                                    position="bottom"
                                                >
                                                    <div className="flex flex-col cursor-help w-full">
                                                        <span className={`text-[11px] font-bold ${product.days_of_coverage < 3 ? 'text-rose-500' : product.days_of_coverage < 7 ? 'text-amber-500' : 'text-slate-400'}`}>
                                                            {product.days_of_coverage < 999 ? `${product.days_of_coverage.toFixed(1)} dias` : '∞'}
                                                        </span>
                                                        <div className="w-full h-1.5 bg-slate-800 rounded-full mt-1 overflow-hidden relative">
                                                            {(() => {
                                                                // Meta Dinâmica
                                                                const leadTime = 9; // 7 fornecedor + 2 full
                                                                const marginDays = product.curve === 'A' ? 4 : product.curve === 'B' ? 3 : 2;
                                                                const targetDays = leadTime + marginDays;
                                                                const maxScale = 30; // Fixo em 30 dias para visualização
                                                                const targetPercentage = Math.min((targetDays / maxScale) * 100, 100);
                                                                const currentPercentage = Math.min((product.days_of_coverage / maxScale) * 100, 100);

                                                                return (
                                                                    <>
                                                                        {/* Marcador de meta ideal */}
                                                                        <div
                                                                            className="absolute top-0 bottom-0 w-0.5 bg-cyan-400/80 z-10 shadow-[0_0_8px_rgba(34,211,238,0.5)]"
                                                                            style={{ left: `${targetPercentage}%` }}
                                                                            title={`Meta: ${targetDays} dias`}
                                                                        />
                                                                        <div
                                                                            className={`h-full rounded-full ${product.days_of_coverage < 3 ? 'bg-rose-500' : product.days_of_coverage < targetDays ? 'bg-amber-500' : 'bg-emerald-500'}`}
                                                                            style={{ width: `${currentPercentage}%` }}
                                                                        />
                                                                    </>
                                                                );
                                                            })()}
                                                        </div>
                                                    </div>
                                                </Tooltip>
                                            </td>

                                            <td className="px-4 py-2">
                                                <div className="flex items-center justify-center">
                                                    {product.days_of_coverage <= 3 && product.stock_incoming === 0 ? (
                                                        <button className="group/btn relative px-3 py-1 bg-red-500/10 hover:bg-red-500/20 text-red-400 text-[10px] font-black uppercase tracking-tighter rounded border border-red-500/20 transition-all flex items-center gap-1.5 animate-pulse cursor-pointer">
                                                            <ShoppingCart className="w-3 h-3" />
                                                            Comprar
                                                        </button>
                                                    ) : product.days_of_coverage <= 7 ? (
                                                        <button className="px-3 py-1 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 text-[10px] font-black uppercase tracking-tighter rounded border border-amber-500/20 transition-all flex items-center gap-1.5 cursor-pointer">
                                                            <Truck className="w-3 h-3" />
                                                            Enviar Full
                                                        </button>
                                                    ) : product.stock_local > product.stock_full && product.days_of_coverage < 15 ? (
                                                        <button className="px-3 py-1 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 text-[10px] font-black uppercase tracking-tighter rounded border border-blue-500/20 transition-all flex items-center gap-1.5 cursor-pointer">
                                                            <RefreshCw className="w-3 h-3 group-hover:animate-spin" />
                                                            Transferir
                                                        </button>
                                                    ) : product.days_of_coverage > 60 ? (
                                                        <div className="px-3 py-1 bg-emerald-500/5 text-emerald-500/60 text-[9px] font-bold uppercase tracking-tighter rounded border border-emerald-500/10 flex items-center gap-1.5">
                                                            <CheckCircle2 className="w-3 h-3" />
                                                            Saudável
                                                        </div>
                                                    ) : (
                                                        <div className="px-3 py-1 text-slate-600 text-[9px] font-bold uppercase tracking-tighter flex items-center gap-1.5">
                                                            <Clock className="w-3 h-3" />
                                                            OK
                                                        </div>
                                                    )}
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                            </tbody>
                        </table>
                    </div>
                    {products.length === 0 && (
                        <div className="text-center py-12 text-slate-500">
                            Nenhum produto encontrado com os filtros selecionados
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
});

export default ProductForecastDashboard;
