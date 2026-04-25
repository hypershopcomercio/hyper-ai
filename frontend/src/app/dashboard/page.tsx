
'use client';

import {
    TrendingUp,
    TrendingDown,
    Users,
    DollarSign,
    ShoppingCart,
    ArrowUpRight,
    ArrowDownRight,
    AlertTriangle,
    RefreshCw,
    BarChart2
} from 'lucide-react';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { CashFlowChart } from '@/components/dashboard/CashFlowChart';
import { SalesTable } from '@/components/dashboard/SalesTable';
import { SyncStatus } from '@/components/dashboard/SyncStatus';
import { PremiumLoader } from '@/components/ui/PremiumLoader';
import { AnimatedInt, AnimatedCurrency, AnimatedPercent } from '@/components/ui/AnimatedNumber';
import { DigitalClock } from '@/components/ui/DigitalClock';
import { SalesFireworks } from '@/components/ui/SalesFireworks';

export default function DashboardPage() {
    const [period, setPeriod] = useState('Hoje');
    const [dashboardData, setDashboardData] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [showLoader, setShowLoader] = useState(true);
    const [refreshKey, setRefreshKey] = useState(0);
    const [showFireworks, setShowFireworks] = useState(false);
    const [lastSaleProduct, setLastSaleProduct] = useState<string | undefined>(undefined);

    // Initial Load Only
    useEffect(() => {
        // Force loader on mount
        setShowLoader(true);
    }, []);

    // Refetch function for data updates
    const refetchMetrics = () => {
        console.log('[Dashboard] Data refresh triggered');
        setRefreshKey(prev => prev + 1);
    };

    // Handle new sale celebration - ONLY from SSE order_update webhook
    const handleNewSale = (productName?: string) => {
        if (showFireworks) return; // Guard against multiple triggers
        console.log('[Dashboard] 🎉 NOVA VENDA via SSE:', productName);
        setLastSaleProduct(productName || 'Novo Pedido Confirmado!');
        setShowFireworks(true);
    };


    // Trigger quick sync on mount to ensure fresh data
    useEffect(() => {
        api.post('/jobs/trigger')
            .then(() => {
                // Refresh metrics after 1.5s to reflect new data
                setTimeout(() => setRefreshKey(prev => prev + 1), 1500);
            })
            .catch(e => console.error("Quick sync trigger failed:", e));
    }, []);

    useEffect(() => {
        async function fetchMetrics() {
            // Only show internal loading state if NOT showing the full screen loader
            if (refreshKey === 0 && !showLoader) setIsLoading(true);
            try {
                // Map Period to Days
                let days: any = 7;
                if (period === 'Hoje') days = 1;
                if (period === 'Ontem') days = 0;
                if (period === 'Mês Atual') days = 'current_month';
                if (period === 'Mês Passado') days = 'last_month';

                const res = await api.get(`/dashboard/metrics?days=${days}`);
                setDashboardData(res.data);
            } catch (error) {
                console.error("Erro ao buscar métricas:", error);
            } finally {
                setIsLoading(false);
            }
        }

        fetchMetrics();
    }, [period, refreshKey]);

    // Auto-refresh every 10 seconds for TV display mode
    useEffect(() => {
        const interval = setInterval(() => {
            console.log('[Dashboard] Auto-refresh triggered');
            setRefreshKey(prev => prev + 1);
        }, 10000); // Reduzido de 30s para 10s
        return () => clearInterval(interval);
    }, []);


    const handleLoaderComplete = useCallback(() => {
        setShowLoader(false);
    }, []);

    // Blocking loader removed for Simultaneous Render
    // if (showLoader) return ...

    // Calculate aggregates from sales_list (more reliable than backend pre-calc)
    const salesList = dashboardData?.sales_list || [];
    const totalProfit = salesList.reduce((sum: number, item: any) => sum + (item.net_margin || 0), 0);
    const totalAdsCost = salesList.reduce((sum: number, item: any) => sum + (item.costs?.ads || 0), 0);
    const totalRevenue = dashboardData?.revenue_7d || 0;
    const averageMargin = totalRevenue > 0 ? (totalProfit / totalRevenue) * 100 : 0;

    // Count items with missing product cost
    const itemsMissingCost = salesList.filter((item: any) => (item.costs?.product || 0) === 0).length;
    const hasMissingCosts = itemsMissingCost > 0;

    // Fallback/Skeleton or previous data could be used, but for now simple loading text or null check
    // Logic to structure 'metrics' array based on fetched data
    const metrics = dashboardData ? [
        {
            title: 'VISITAS',
            value: dashboardData.visits_7d.toLocaleString('pt-BR'),
            rawValue: showLoader ? 0 : dashboardData.visits_7d,
            valueType: 'int',
            change: dashboardData.visits_trend > 0 ? `+${dashboardData.visits_trend}%` : `${dashboardData.visits_trend}%`,
            rawAdsValue: showLoader ? 0 : Math.round(dashboardData.visits_7d * 0.4),
            rawOrganicValue: showLoader ? 0 : Math.round(dashboardData.visits_7d * 0.6),
            adsValue: Math.round(dashboardData.visits_7d * 0.4).toLocaleString('pt-BR'),
            organicValue: Math.round(dashboardData.visits_7d * 0.6).toLocaleString('pt-BR'),
            isPositive: dashboardData.visits_trend >= 0,
            icon: Users,
            color: 'text-blue-400',
            bgIcon: 'bg-blue-400/10',
            badges: dashboardData.conversion_badges?.distribution || []
        },
        {
            title: 'VENDAS',
            value: new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(dashboardData.revenue_7d),
            rawValue: showLoader ? 0 : dashboardData.revenue_7d,
            valueType: 'currency',

            // Profitability Section (calculated from sales_list)

            profitValue: new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(totalProfit),
            rawProfitValue: showLoader ? 0 : totalProfit,
            profitTrend: dashboardData?.profit_trend || 0,

            marginValue: `${(averageMargin || 0).toFixed(1)}%`,
            rawMarginValue: showLoader ? 0 : averageMargin,

            adsValue: new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(totalAdsCost),
            rawAdsValue: showLoader ? 0 : totalAdsCost,

            change: dashboardData.revenue_trend > 0 ? `+${dashboardData.revenue_trend}%` : `${dashboardData.revenue_trend}%`,
            subtext: `${dashboardData.sales_count_7d} vendas`, // Keeping count here
            rawSalesCount: showLoader ? 0 : dashboardData.sales_count_7d,

            // Tooltip Breakdown Data (Safe)
            tooltipData: {
                organicRevenue: dashboardData.revenue_organic || 0,
                adsRevenue: dashboardData.revenue_ads || 0,
                cancelledRevenue: dashboardData.revenue_cancelled_7d || 0,
                validCount: dashboardData.sales_count_7d || 0,
                cancelledCount: dashboardData.sales_count_cancelled || 0
            },

            // Missing cost indicator
            hasMissingCosts: hasMissingCosts,
            missingCostCount: itemsMissingCost,

            isPositive: dashboardData.revenue_trend >= 0,
            icon: DollarSign,
            color: 'text-emerald-400',
            bgIcon: 'bg-emerald-400/10'
        },
        {
            title: 'CONVERSÃO',
            value: period === 'Hoje' && dashboardData.visits_7d === 0
                ? 'Calculando...'
                : (dashboardData.conversion_badges?.current_rate
                    ? `${dashboardData.conversion_badges.current_rate}%`
                    : (dashboardData.visits_7d > 0
                        ? `${((dashboardData.sales_count_7d / dashboardData.visits_7d) * 100 || 0).toFixed(2)}%`
                        : '0.00%')),
            change: dashboardData.conversion_badges?.trend
                ? (dashboardData.conversion_badges.trend > 0
                    ? `+${dashboardData.conversion_badges.trend}%`
                    : `${dashboardData.conversion_badges.trend}%`)
                : '0%',
            isPositive: dashboardData.conversion_badges?.is_positive ?? true,
            icon: TrendingUp,
            color: period === 'Hoje' && dashboardData.visits_7d === 0 ? 'text-slate-400' : 'text-amber-400',
            bgIcon: period === 'Hoje' && dashboardData.visits_7d === 0 ? 'bg-slate-400/10' : 'bg-amber-400/10',
            badges: period === 'Hoje' && dashboardData.visits_7d === 0
                ? [{ label: 'LATÊNCIA', val: 'ML D-1', color: 'text-slate-500' }]
                : (dashboardData.conversion_badges?.distribution || [])
        },
        {
            title: 'RISCO ESTOQUE',
            value: showLoader ? 0 : (dashboardData.stock_risk_count ?? (dashboardData.stock_risks?.length || 0)),
            rawValue: showLoader ? 0 : (dashboardData.stock_risk_count ?? (dashboardData.stock_risks?.length || 0)),
            valueType: 'int',
            subtext: dashboardData.stock_risk_value
                ? `${new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(dashboardData.stock_risk_value)} em risco`
                : 'R$ 0,00 em risco',
            rawRiskValue: showLoader ? 0 : (dashboardData.stock_risk_value || 0),
            icon: AlertTriangle,
            color: 'text-rose-500',
            bgIcon: 'bg-rose-500/10',
            isAlert: true
        }
    ] : [];



    return (
        <div className={`relative bg-[#0f1014] ${showLoader ? 'h-[calc(100vh-106px)] overflow-hidden' : 'min-h-screen'}`}>
            {showLoader && <PremiumLoader onComplete={handleLoaderComplete} />}

            <div className="p-8 max-w-[1600px] mx-auto min-h-screen">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4 animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-300 ease-out fill-mode-both relative">
                    <div className="shrink-0">
                        <div className="flex items-center gap-3 mb-1">
                            <h1 className="text-2xl font-bold text-white">Dashboard <span className="text-slate-500 font-medium">Decision</span></h1>
                            <SyncStatus onDataRefresh={refetchMetrics} onNewSale={handleNewSale} />
                        </div>
                        <p className="text-slate-400 text-sm">Visão estratégica da operação</p>
                    </div>

                    {/* Digital Clock - absolutely centered */}
                    <div className="hidden lg:block absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
                        <DigitalClock />
                    </div>

                    <div className="flex items-center gap-4">
                        {/* Period Selector */}
                        {/* Period Selector */}
                        <div className="bg-[#1A1A2E] border border-slate-700/50 rounded-lg p-0.5 flex items-center gap-1">
                            {['Hoje', 'Ontem', '7D', 'Mês Atual', 'Mês Passado'].map((p) => (
                                <button
                                    key={p}
                                    onClick={() => setPeriod(p)}
                                    className={`px-2 py-0.5 text-[10px] font-bold rounded-md transition-all cursor-pointer whitespace-nowrap ${period === p
                                        ? 'text-white bg-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.4)] border border-emerald-400/20'
                                        : 'text-slate-400 hover:text-white hover:bg-slate-800'
                                        }`}
                                >
                                    {p}
                                </button>
                            ))}
                        </div>

                    </div>
                </div>

                {/* Metrics Grid */}
                <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8 transition-all duration-300 animate-in fade-in slide-in-from-bottom-8 duration-[1500ms] ease-out delay-700 fill-mode-both`}>
                    {metrics.map((metric: any, i) => {
                        const Icon = metric.icon;
                        return (
                            <div key={i} className="bg-[#151520] border border-slate-800/60 px-4 pt-4 pb-3 rounded-2xl shadow-sm hover:border-slate-700 hover:shadow-lg transition-all duration-200 relative overflow-visible group">

                                <div className="flex justify-between items-start mb-1">
                                    <span className="text-slate-500 text-[10px] font-bold uppercase tracking-widest">{metric.title}</span>
                                    <div className={`p-1.5 rounded-lg ${metric.bgIcon} ${metric.color} opacity-80 group-hover:opacity-100 transition-opacity`}>
                                        <Icon size={16} />
                                    </div>
                                </div>

                                {/* Content */}
                                <div className="flex flex-col h-full">
                                    {/* Top Section: Value + Percentage/Badge */}

                                    <div className="flex items-end justify-between gap-1 mb-2 min-w-0">
                                        <div className="h-9 flex items-center gap-1 min-w-0 flex-shrink">
                                            {metric.value === 'Calculando...' ? (
                                                <span className="text-xl text-slate-400 font-bold tracking-tight">{metric.value}</span>
                                            ) : metric.valueType === 'currency' ? (
                                                <AnimatedCurrency
                                                    value={metric.rawValue}
                                                    duration={2000}
                                                    className="text-xl xl:text-2xl text-white font-bold tracking-tight"
                                                />
                                            ) : metric.valueType === 'int' ? (
                                                <AnimatedInt
                                                    value={metric.rawValue}
                                                    duration={2000}
                                                    className="text-xl xl:text-2xl text-white font-bold tracking-tight"
                                                />
                                            ) : (
                                                <span className="text-xl xl:text-2xl text-white font-bold tracking-tight">{metric.value}</span>
                                            )}
                                        </div>

                                        <div className="flex flex-col items-end gap-0 shrink-0">
                                            {/* Percentage Change (Standardized Position - Moved to Top) */}
                                            {metric.change && (
                                                <div className={`flex items-center gap-0.5 text-[9px] font-bold whitespace-nowrap ${metric.isPositive ? 'text-emerald-500' : 'text-rose-500'}`}>
                                                    {metric.isPositive
                                                        ? <TrendingUp size={10} className="arrow-shine-up" />
                                                        : <TrendingDown size={10} className="arrow-shine-down" />}
                                                    <span>({metric.change})</span>
                                                </div>
                                            )}

                                            {/* SALES COUNT - Moved Below Percentage */}
                                            {metric.title === 'VENDAS' && metric.rawSalesCount !== undefined && (
                                                <span className="text-[9px] text-emerald-400/80 font-medium tracking-wide mt-0.5 whitespace-nowrap">
                                                    {metric.rawSalesCount} vendas
                                                </span>
                                            )}

                                            {/* Risk Alert Label */}
                                            {metric.isAlert && (
                                                <div className="flex items-center gap-0.5 text-[9px] font-bold text-rose-500 mt-0.5">
                                                    <AlertTriangle size={10} className="pulse-alert" />
                                                    <span>Crítico</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {/* Divider & Bottom Breakdown Area */}
                                    <div className="border-t border-slate-800/50 pt-3">


                                        {/* VENDAS Breakdown */}
                                        {metric.title === 'VENDAS' && (
                                            <div className="flex flex-col gap-2">
                                                <div className="grid grid-cols-3 gap-1 w-full items-start">
                                                    {/* Ads Cost with ACOS */}
                                                    <div className="flex flex-col items-start min-w-0" title="Custo de Ads e ACOS (Custo de Publicidade sobre Vendas)">
                                                        <div className="flex items-center gap-0.5">
                                                            <span className="text-[8px] text-blue-400 font-bold uppercase tracking-wide">ADS</span>
                                                            {metric.rawValue > 0 && metric.rawAdsValue !== undefined && (
                                                                <span className="text-[7px] text-blue-400/60">({((metric.rawAdsValue / metric.rawValue) * 100 || 0).toFixed(1)}%)</span>
                                                            )}
                                                        </div>
                                                        <span className="text-[10px] text-blue-300 font-semibold truncate w-full">{metric.adsValue}</span>
                                                    </div>

                                                    {/* Net Profit */}
                                                    <div
                                                        className="flex flex-col items-start border-l border-slate-800 pl-1 min-w-0"
                                                        title={metric.hasMissingCosts ? `${metric.missingCostCount} produto(s) sem custo - margem estimada` : 'Lucro Líquido (Receita - Custos - Impostos - Ads)'}
                                                    >
                                                        <div className="flex items-center gap-0.5 flex-wrap">
                                                            <span className={`text-[8px] ${metric.hasMissingCosts ? 'text-amber-500' : 'text-emerald-500'} font-extrabold uppercase tracking-wide`}>LUCRO</span>
                                                            {metric.profitTrend !== undefined && (
                                                                <span className={`text-[7px] font-medium ${metric.profitTrend >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                                                    {metric.profitTrend > 0 ? '+' : ''}{metric.profitTrend}%
                                                                </span>
                                                            )}
                                                            {metric.hasMissingCosts && (
                                                                <AlertTriangle size={8} className="text-amber-500" />
                                                            )}
                                                        </div>
                                                        <span className={`text-[10px] ${metric.hasMissingCosts ? 'text-amber-400' : 'text-emerald-400'} font-bold truncate w-full`}>{metric.profitValue}</span>
                                                    </div>

                                                    {/* Margin % */}
                                                    <div className="flex flex-col items-end border-l border-slate-800 pl-1 min-w-0" title="Margem de Contribuição (Lucro Líq. / Receita)">
                                                        <span className="text-[8px] text-slate-500 font-bold uppercase">MARGEM</span>
                                                        <span className={`text-[10px] font-semibold ${(() => {
                                                            const margin = parseFloat(metric.marginValue?.replace('%', '') || '0');
                                                            if (margin < 5) return 'text-rose-500';
                                                            if (margin < 10) return 'text-orange-400';
                                                            if (margin <= 15) return 'text-yellow-400';
                                                            if (margin <= 20) return 'text-emerald-400';
                                                            return 'text-emerald-600';
                                                        })()}`}>{metric.marginValue}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                        {/* VISITAS Breakdown */}
                                        {metric.title === 'VISITAS' && (
                                            <div className="flex gap-4">
                                                <div className="flex flex-col">
                                                    <span className="text-[9px] text-slate-500 font-bold uppercase">Orgânico</span>
                                                    <span className="text-[11px] text-slate-300 font-semibold">{metric.organicValue}</span>
                                                </div>
                                                <div className="flex flex-col">
                                                    <span className="text-[9px] text-slate-500 font-bold uppercase">Ads</span>
                                                    <span className="text-[11px] text-blue-400 font-semibold">{metric.adsValue}</span>
                                                </div>
                                            </div>
                                        )}

                                        {/* CONVERSÃO Breakdown (Badges full-width, premium style) */}
                                        {metric.title === 'CONVERSÃO' && metric.badges && (
                                            <div className="flex gap-1 w-full">
                                                {metric.badges.map((b: any, idx: number) => {
                                                    let styleClass = 'bg-rose-500/10 border-rose-500/20 text-rose-500'; // RUIM - stronger

                                                    if (b.label === 'BONS') {
                                                        styleClass = 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500';
                                                    } else if (b.label === 'MÉD') {
                                                        styleClass = 'bg-amber-500/10 border-amber-500/20 text-amber-500';
                                                    }

                                                    return (
                                                        <Link key={idx} href={`/perform/analytics?filter=${b.label.toLowerCase()}`} className="flex-1">
                                                            <div className={`flex items-center justify-center gap-1 py-1 rounded border ${styleClass} cursor-pointer hover:opacity-100 hover:scale-[1.02] transition-all duration-200`}>
                                                                <span className="text-[9px] font-semibold">{b.val}</span>
                                                                <span className="text-[7px] font-medium uppercase opacity-70">{b.label}</span>
                                                            </div>
                                                        </Link>
                                                    )
                                                })}
                                            </div>
                                        )}

                                        {/* RISCO Breakdown */}
                                        {metric.title === 'RISCO ESTOQUE' && (
                                            <div className="flex flex-col">
                                                <span className="text-[9px] text-slate-500 font-bold uppercase">Em Risco Financeiro</span>
                                                <Link href="/supply/estoque">
                                                    <span className="group text-[11px] text-amber-500 font-semibold flex items-center gap-1 cursor-pointer hover:text-amber-400 transition-colors">
                                                        <span className="border-b border-transparent group-hover:border-amber-400 transition-colors pb-px inline-flex items-center gap-1">
                                                            <AnimatedCurrency
                                                                key={`risk-${refreshKey}`}
                                                                value={metric.rawRiskValue || 0}
                                                                duration={2000}
                                                                className=""
                                                            />
                                                            <span className="">em risco</span>
                                                        </span>
                                                    </span>
                                                </Link>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-in fade-in slide-in-from-bottom-8 duration-[1500ms] ease-out delay-1000 fill-mode-both">
                    {/* Main Chart Section */}
                    <div className="lg:col-span-2 bg-[#151520] border border-slate-800/60 rounded-2xl p-6 min-h-[400px] flex flex-col">
                        <div className="flex justify-between items-center mb-8 shrink-0">
                            <h2 className="text-sm font-bold text-white flex items-center gap-2">
                                Fluxo de Caixa (Vendas vs Custos)
                            </h2>
                            <div className="bg-[#1A1A2E] px-3 py-1 rounded text-xs text-slate-400 border border-slate-800/50">
                                {period === 'Hoje' ? 'Hoje' : period === 'Ontem' ? 'Ontem' : period === '7D' ? 'Últimos 7 dias' : period === 'current_month' ? 'Mês Atual' : period === 'last_month' ? 'Mês Passado' : period}
                            </div>
                        </div>
                        <div className="flex-1 min-h-0">
                            {!showLoader && dashboardData?.cash_flow ? (
                                <CashFlowChart data={dashboardData.cash_flow} isLive={period === 'Hoje'} />
                            ) : (
                                <div className="h-full border-2 border-dashed border-slate-800/50 rounded-xl flex flex-col items-center justify-center text-slate-600 gap-3">
                                    <TrendingUp size={32} className="opacity-20" />
                                    <div className="text-center">
                                        <p className="text-sm font-medium text-slate-500">Sem dados para este período</p>
                                        <p className="text-xs opacity-40">Necessário sincronizar custos do Tiny</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Pareto (Top 5) */}
                    <div className="bg-[#151520] border border-slate-800/60 rounded-2xl overflow-hidden flex flex-col">
                        <div className="p-5 border-b border-slate-800/50 flex justify-between items-center shrink-0">
                            <h2 className="font-bold text-white text-sm flex items-center gap-2">
                                <BarChart2 size={16} className="text-cyan-500" />
                                Pareto (Top 5)
                            </h2>
                            <span className="text-[10px] font-bold text-slate-500 tracking-wider bg-slate-800 px-1.5 py-0.5 rounded border border-slate-700">80/20</span>
                        </div>

                        <div className="flex-1 overflow-y-auto">
                            {(dashboardData?.pareto || []).map((item: any, i: number) => (
                                <div key={i} className="p-4 hover:bg-slate-800/20 transition-colors border-b border-slate-800/30 last:border-0 group relative">
                                    {/* Flex Container */}
                                    <div className="flex items-center gap-4 relative z-10">
                                        {/* Ranking */}
                                        <span className="text-xs font-bold text-slate-600 w-4 group-hover:text-slate-400 transition-colors">
                                            #{i + 1}
                                        </span>

                                        {/* Thumbnail */}
                                        <div className="w-10 h-10 bg-slate-800 rounded-lg shrink-0 flex items-center justify-center overflow-hidden border border-slate-700/30">
                                            {item.thumbnail ? (
                                                <img src={item.thumbnail} alt={item.title} className="w-full h-full object-cover" />
                                            ) : (
                                                <ShoppingCart size={14} className="text-slate-600 opacity-50" />
                                            )}
                                        </div>

                                        {/* Info */}
                                        <div className="flex-1 min-w-0 flex flex-col gap-1">
                                            <div className="flex justify-between items-start">
                                                <p className="text-xs font-bold text-slate-200 truncate leading-tight w-[90%]" title={item.title}>{item.title}</p>
                                                <span className="text-[10px] font-bold text-cyan-400">{item.percentage}%</span>
                                            </div>

                                            <div className="flex justify-between items-center text-[10px] mt-1">
                                                <div className="flex items-center gap-2">
                                                    <span className="text-slate-300 font-semibold">{new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(item.revenue)}</span>
                                                    {item.stock !== undefined && (
                                                        <span className={`text-[9px] font-medium ${item.stock < 10 ? 'text-red-400' : 'text-emerald-500/80'}`}>
                                                            • Est: {item.stock}
                                                        </span>
                                                    )}
                                                </div>

                                                <div className="flex items-center gap-2">
                                                    {/* Progress Bar Background */}
                                                    <div className="w-16 h-1 bg-slate-800 rounded-full overflow-hidden">
                                                        <div
                                                            className="h-full bg-cyan-500 rounded-full"
                                                            style={{ width: `${Math.min(item.percentage, 100)}%` }}
                                                        ></div>
                                                    </div>
                                                    <span className="text-slate-500">({item.quantity} un)</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}

                            {(!dashboardData?.pareto || dashboardData.pareto.length === 0) && (
                                <div className="p-8 text-center text-slate-500 text-xs">
                                    Sem dados para este período.
                                </div>
                            )}
                        </div>

                        <div className="p-3 bg-[#1A1A2E]/50 border-t border-slate-800/50 text-center shrink-0">
                            <span className="text-[10px] text-slate-400">
                                Top 5 = <span className="text-cyan-400 font-bold">{dashboardData?.pareto ? (dashboardData.pareto.reduce((acc: number, item: any) => acc + item.percentage, 0) || 0).toFixed(1) : 0}%</span> do faturamento
                            </span>
                        </div>
                    </div>
                </div>

                {/* Sales Detail Table */}
                <div className="mt-16 transition-all duration-[1500ms] animate-in fade-in slide-in-from-bottom-8 delay-[1500ms] fill-mode-both">
                    <SalesTable data={dashboardData?.sales_list || []} isLoading={isLoading} />
                </div>

            </div>

            {/* Sales Celebration - ONLY triggered by real SSE order_update webhook */}
            {showFireworks && (
                <SalesFireworks
                    productName={lastSaleProduct}
                    onComplete={() => {
                        setShowFireworks(false);
                        refetchMetrics();
                    }}
                />
            )}
        </div>
    );
}
