
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
            conversion: day.visits > 0 ? (day.sales / day.visits * 100) : 0
        }));
    }, [ad, dateRange]);

    // Calculate Aggregates based on FILTERED data
    const stats = useMemo(() => {
        if (!filteredData.length) return null;

        const totalVisits = filteredData.reduce((acc, curr) => acc + curr.visits, 0);
        const totalSales = filteredData.reduce((acc, curr) => acc + curr.sales, 0);
        const avgConversion = totalVisits > 0 ? (totalSales / totalVisits * 100) : 0;

        return { totalVisits, totalSales, avgConversion };
    }, [filteredData]);

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
                <div className="grid grid-cols-3 gap-4">
                    <div className="bg-[#13141b] border border-white/5 p-4 rounded-xl flex flex-col justify-between">
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider">
                                <MousePointer2 size={14} /> Visitas
                            </div>
                            <span className="text-[10px] text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded font-bold">+12%</span>
                        </div>
                        <div className="text-2xl font-bold text-white">{stats.totalVisits.toLocaleString('pt-BR')}</div>
                    </div>

                    <div className="bg-[#13141b] border border-white/5 p-4 rounded-xl flex flex-col justify-between">
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider">
                                <Percent size={14} /> Conversão
                            </div>
                            <span className="text-[10px] text-slate-500 bg-slate-800 px-1.5 py-0.5 rounded font-bold">~</span>
                        </div>
                        <div className="text-2xl font-bold text-white">{stats.avgConversion.toFixed(2)}%</div>
                    </div>

                    <div className="bg-[#13141b] border border-white/5 p-4 rounded-xl flex flex-col justify-between">
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider">
                                <DollarSign size={14} /> Vendas (Un)
                            </div>
                            <span className="text-[10px] text-rose-400 bg-rose-500/10 px-1.5 py-0.5 rounded font-bold">-5%</span>
                        </div>
                        <div className="text-2xl font-bold text-white">{stats.totalSales}</div>
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

            {/* Insights Panel (Kept, but Table REMOVED) */}
            <div className="space-y-3">
                <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-1">Análise Automática</h4>
                <div className="bg-blue-500/5 border border-blue-500/10 rounded-xl p-4 flex items-start gap-4">
                    <div className="p-2 rounded bg-blue-500/10 text-blue-400 shrink-0">
                        <TrendingUp size={18} />
                    </div>
                    <div>
                        <h5 className="text-sm font-bold text-slate-200">Tendência</h5>
                        <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                            Com base nos últimos {dateRange} dias, sua conversão de <span className="font-bold text-white">{stats?.avgConversion.toFixed(2)}%</span> indica estabilidade.
                        </p>
                    </div>
                </div>
            </div>

        </div>
    );
}
