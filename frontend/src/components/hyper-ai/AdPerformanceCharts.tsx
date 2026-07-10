
import React, { useMemo, useState } from 'react';
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from 'recharts';
import { TrendingUp, MousePointer2, Percent, DollarSign } from 'lucide-react';
import { Ad } from '@/types';

interface Props {
    ad: Ad;
}

export function AdPerformanceCharts({ ad }: Props) {
    const [dateRange, setDateRange] = useState<'30' | '60' | '90' | '365'>('30');

    // Filter and Transform history data
    const filteredData = useMemo(() => {
        if (!ad.history) return [];

        const sortedHistory = [...ad.history].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

        const daysToKeep = parseInt(dateRange);
        // We slice the last N days based on the selected filter
        return sortedHistory.slice(-daysToKeep).map(day => ({
            date: new Date(day.date).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
            fullDate: new Date(day.date).toLocaleDateString('pt-BR'),
            visits: day.visits,
            sales: day.sales,
            revenue: day.revenue || 0,
            conversion: day.visits > 0 ? (day.sales / day.visits * 100) : 0
        }));
    }, [ad, dateRange]);

    // Calculate Aggregates based on FILTERED data
    const stats = useMemo(() => {
        if (!filteredData.length) return null;

        const totalVisits = filteredData.reduce((acc, curr) => acc + curr.visits, 0);
        const totalSales = filteredData.reduce((acc, curr) => acc + curr.sales, 0);
        const totalRevenue = filteredData.reduce((acc, curr) => acc + curr.revenue, 0);
        const avgConversion = totalVisits > 0 ? (totalSales / totalVisits * 100) : 0;

        return { totalVisits, totalSales, totalRevenue, avgConversion };
    }, [filteredData]);

    // Tendência REAL: compara a metade final do período com a inicial (sem dados falsos)
    const trends = useMemo(() => {
        if (filteredData.length < 4) return null;
        const mid = Math.floor(filteredData.length / 2);
        const first = filteredData.slice(0, mid);
        const second = filteredData.slice(mid);
        const sum = (arr: typeof filteredData, k: 'visits' | 'sales' | 'revenue') => arr.reduce((a, c) => a + (c[k] || 0), 0);
        const pct = (now: number, before: number) => before > 0 ? ((now - before) / before * 100) : (now > 0 ? 100 : 0);
        const vNow = sum(second, 'visits'), vBefore = sum(first, 'visits');
        const sNow = sum(second, 'sales'), sBefore = sum(first, 'sales');
        const rNow = sum(second, 'revenue'), rBefore = sum(first, 'revenue');
        const cNow = vNow > 0 ? sNow / vNow * 100 : 0;
        const cBefore = vBefore > 0 ? sBefore / vBefore * 100 : 0;
        return {
            visits: pct(vNow, vBefore),
            sales: pct(sNow, sBefore),
            revenue: pct(rNow, rBefore),
            conversionPp: cNow - cBefore, // diferença em pontos percentuais
        };
    }, [filteredData]);

    // Badge de tendência reutilizável (verde sobe / vermelho cai / neutro estável)
    const TrendBadge = ({ value, suffix = '%', neutralBelow = 1 }: { value: number | undefined; suffix?: string; neutralBelow?: number }) => {
        if (value == null || !isFinite(value)) return <span className="text-[10px] text-slate-500 bg-slate-800 px-1.5 py-0.5 rounded font-bold">~</span>;
        const isNeutral = Math.abs(value) < neutralBelow;
        const cls = isNeutral ? 'text-slate-500 bg-slate-800' : value > 0 ? 'text-emerald-400 bg-emerald-500/10' : 'text-rose-400 bg-rose-500/10';
        const sign = value > 0 ? '+' : '';
        return <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${cls}`}>{isNeutral ? '~' : `${sign}${value.toFixed(value >= 100 ? 0 : 1)}${suffix}`}</span>;
    };

    if (!filteredData.length) return <div className="p-8 text-center text-slate-500">Sem dados para o período.</div>;

    return (
        <div className="space-y-6">

            {/* Header / Filter */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Performance</h3>
                    <div className="w-1 h-1 rounded-full bg-slate-700"></div>
                    <span className="text-xs text-slate-400">Últimos {dateRange} dias</span>
                </div>

                <div className="flex bg-[#13141b] rounded-lg p-1 border border-white/5">
                    {['30', '60', '90', '365'].map((range) => (
                        <button
                            key={range}
                            onClick={() => setDateRange(range as any)}
                            className={`px-3 py-1 text-[10px] font-bold rounded-md transition-all cursor-pointer ${dateRange === range
                                ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20'
                                : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'
                                }`}
                        >
                            {range === '365' ? '1A' : `${range}D`}
                        </button>
                    ))}
                </div>
            </div>

            {/* KPI Cards Row */}
            {stats && (
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-[#13141b] border border-white/5 p-4 rounded-xl flex flex-col justify-between">
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider">
                                <MousePointer2 size={14} /> Visitas
                            </div>
                            <TrendBadge value={trends?.visits} />
                        </div>
                        <div className="text-2xl font-bold text-white">{stats.totalVisits.toLocaleString('pt-BR')}</div>
                    </div>

                    <div className="bg-[#13141b] border border-white/5 p-4 rounded-xl flex flex-col justify-between">
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider">
                                <DollarSign size={14} /> Vendas (Un)
                            </div>
                            <TrendBadge value={trends?.sales} />
                        </div>
                        <div className="text-2xl font-bold text-white">{stats.totalSales}</div>
                    </div>

                    <div className="bg-[#13141b] border border-white/5 p-4 rounded-xl flex flex-col justify-between">
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider">
                                <Percent size={14} /> Conversão
                            </div>
                            <TrendBadge value={trends?.conversionPp} suffix="pp" neutralBelow={0.1} />
                        </div>
                        <div className="text-2xl font-bold text-white">{stats.avgConversion.toFixed(2)}%</div>
                    </div>

                    <div className="bg-[#13141b] border border-white/5 p-4 rounded-xl flex flex-col justify-between">
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider">
                                <TrendingUp size={14} /> Receita
                            </div>
                            <TrendBadge value={trends?.revenue} />
                        </div>
                        <div className="text-2xl font-bold text-white">{stats.totalRevenue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 })}</div>
                    </div>
                </div>
            )}

            {/* Main Chart (RESTORED) */}
            <div className="h-[300px] w-full bg-[#13141b] border border-white/5 rounded-xl p-4 relative group">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={filteredData}>
                        <defs>
                            <linearGradient id="colorVisits" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1} />
                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                            </linearGradient>
                            <linearGradient id="colorSales" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#10b981" stopOpacity={0.1} />
                                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                        <XAxis
                            dataKey="date"
                            stroke="#475569"
                            fontSize={10}
                            tickLine={false}
                            axisLine={false}
                            dy={10}
                        />
                        <YAxis
                            yAxisId="left"
                            stroke="#3b82f6"
                            fontSize={10}
                            tickLine={false}
                            axisLine={false}
                            dx={-10}
                            tickFormatter={(value) => value.toLocaleString('pt-BR')}
                        />
                        <YAxis
                            yAxisId="right"
                            orientation="right"
                            stroke="#10b981"
                            fontSize={10}
                            tickLine={false}
                            axisLine={false}
                            dx={10}
                            domain={[0, (dataMax: number) => (dataMax * 2) || 10]}
                            tickFormatter={(value) => value.toLocaleString('pt-BR')}
                        />
                        <Tooltip
                            content={({ active, payload, label }) => {
                                if (active && payload && payload.length) {
                                    return (
                                        <div className="bg-[#09090b] border border-white/10 rounded-lg p-3 shadow-xl">
                                            <p className="text-slate-400 text-[10px] font-mono mb-2 border-b border-white/5 pb-1">{label}</p>
                                            <div className="flex items-center gap-4">
                                                <div className="flex items-center gap-2">
                                                    <span className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]"></span>
                                                    <span className="text-xs text-slate-300">Visitas:</span>
                                                    <span className="text-sm font-bold text-white">{payload[0].value}</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></span>
                                                    <span className="text-xs text-slate-300">Vendas:</span>
                                                    <span className="text-sm font-bold text-white">{payload.find(p => p.dataKey === 'sales')?.value || 0}</span>
                                                </div>
                                            </div>
                                        </div>
                                    );
                                }
                                return null;
                            }}
                        />
                        <Area
                            yAxisId="left"
                            type="monotone"
                            dataKey="visits"
                            stroke="#3b82f6"
                            strokeWidth={2}
                            fillOpacity={1}
                            fill="url(#colorVisits)"
                            name="Visitas"
                        />
                        <Area
                            yAxisId="right"
                            type="monotone"
                            dataKey="sales"
                            stroke="#10b981"
                            strokeWidth={2}
                            fillOpacity={1}
                            fill="url(#colorSales)"
                            name="Vendas"
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>

            {/* Insights Panel — narrativa calculada da tendência real */}
            {(() => {
                const salesTrend = trends?.sales ?? 0;
                const visitsTrend = trends?.visits ?? 0;
                const convPp = trends?.conversionPp ?? 0;
                // Direção pela venda (sinal de negócio); tom e cor seguem ela
                const rising = salesTrend > 5;
                const falling = salesTrend < -5;
                const tone = rising ? 'emerald' : falling ? 'rose' : 'blue';
                const toneCls = {
                    emerald: { wrap: 'bg-emerald-500/5 border-emerald-500/10', icon: 'bg-emerald-500/10 text-emerald-400' },
                    rose: { wrap: 'bg-rose-500/5 border-rose-500/10', icon: 'bg-rose-500/10 text-rose-400' },
                    blue: { wrap: 'bg-blue-500/5 border-blue-500/10', icon: 'bg-blue-500/10 text-blue-400' },
                }[tone];
                const title = rising ? 'Em crescimento' : falling ? 'Em queda' : 'Estável';

                let narrative: React.ReactNode;
                if (!trends) {
                    narrative = <>Dados insuficientes no período de <span className="font-bold text-white">{dateRange} dias</span> para calcular tendência. Amplie a janela ou aguarde mais histórico.</>;
                } else if (rising || falling) {
                    // Diagnóstico demanda (visitas) vs eficiência (conversão)
                    const driver = Math.abs(visitsTrend) >= Math.abs(convPp) * 10
                        ? <>puxada principalmente por <span className="font-bold text-white">{visitsTrend >= 0 ? '+' : ''}{visitsTrend.toFixed(0)}% de visitas</span> (demanda/tráfego)</>
                        : <>puxada principalmente pela <span className="font-bold text-white">conversão ({convPp >= 0 ? '+' : ''}{convPp.toFixed(2)} pp)</span> (eficiência do anúncio)</>;
                    narrative = <>Nos últimos <span className="font-bold text-white">{dateRange} dias</span> as vendas estão <span className={`font-bold ${rising ? 'text-emerald-400' : 'text-rose-400'}`}>{salesTrend >= 0 ? '+' : ''}{salesTrend.toFixed(0)}%</span> (2ª metade vs 1ª), {driver}.</>;
                } else {
                    narrative = <>Nos últimos <span className="font-bold text-white">{dateRange} dias</span> as vendas estão estáveis (variação &lt;5%), com conversão média de <span className="font-bold text-white">{stats?.avgConversion.toFixed(2)}%</span>.</>;
                }

                return (
                    <div className="space-y-3">
                        <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-1">Análise Automática</h4>
                        <div className={`border rounded-xl p-4 flex items-start gap-4 ${toneCls.wrap}`}>
                            <div className={`p-2 rounded shrink-0 ${toneCls.icon}`}>
                                <TrendingUp size={18} className={falling ? 'rotate-180' : ''} />
                            </div>
                            <div>
                                <h5 className="text-sm font-bold text-slate-200">{title}</h5>
                                <p className="text-xs text-slate-400 mt-1 leading-relaxed">{narrative}</p>
                            </div>
                        </div>
                    </div>
                );
            })()}

        </div>
    );
}
