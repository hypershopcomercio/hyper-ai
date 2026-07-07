"use client";

import { useState, useEffect, useMemo } from 'react';
import { api } from '@/lib/api';
import {
    ResponsiveContainer, ComposedChart, Bar, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend
} from 'recharts';
import {
    Megaphone, Flame, TrendingUp, TrendingDown, AlertTriangle,
    CheckCircle2, Rocket, DollarSign, Target, MousePointerClick, ExternalLink
} from 'lucide-react';

interface AdsAction {
    code: string;
    label: string;
    reason: string;
    impact: string | null;
}

interface AdsItem {
    item_id: string;
    title: string | null;
    thumbnail: string | null;
    permalink: string | null;
    price: number | null;
    status: string | null;
    sku: string | null;
    spend: number;
    ads_revenue: number;
    clicks: number;
    prints: number;
    units: number;
    days_active: number;
    acos: number | null;
    roas: number | null;
    cpc: number | null;
    cvr: number | null;
    margin_percent: number | null;
    ads_profit: number | null;
    classification: string;
    action: AdsAction;
}

interface Overview {
    has_data: boolean;
    message?: string;
    period_days?: number;
    summary: {
        total_spend: number;
        total_ads_revenue: number;
        global_acos: number | null;
        global_roas: number | null;
        total_clicks: number;
        total_prints: number;
        total_units: number;
        items_count: number;
        class_counts: Record<string, number>;
        burn_total: number;
    };
    items: AdsItem[];
    daily_series: { date: string; spend: number; ads_revenue: number }[];
}

const CLASS_META: Record<string, { label: string; color: string; bg: string; icon: any }> = {
    queimando: { label: "Queimando", color: "text-red-400", bg: "bg-red-500/10 border-red-500/30", icon: Flame },
    prejuizo: { label: "Prejuízo", color: "text-orange-400", bg: "bg-orange-500/10 border-orange-500/30", icon: TrendingDown },
    atencao: { label: "Atenção", color: "text-yellow-400", bg: "bg-yellow-500/10 border-yellow-500/30", icon: AlertTriangle },
    saudavel: { label: "Saudável", color: "text-emerald-400", bg: "bg-emerald-500/10 border-emerald-500/30", icon: CheckCircle2 },
    escalar: { label: "Escalar", color: "text-sky-400", bg: "bg-sky-500/10 border-sky-500/30", icon: Rocket },
};

const fmtBRL = (v: number | null | undefined) =>
    (v ?? 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

export default function AdsIntelligencePage() {
    const [data, setData] = useState<Overview | null>(null);
    const [loading, setLoading] = useState(true);
    const [period, setPeriod] = useState(30);
    const [classFilter, setClassFilter] = useState<string | null>(null);

    useEffect(() => {
        let cancelled = false;
        setLoading(true);
        api.get(`/ads-intelligence/overview?days=${period}`)
            .then(res => { if (!cancelled) setData(res.data); })
            .catch(err => { console.error("Error loading ads intelligence", err); if (!cancelled) setData(null); })
            .finally(() => { if (!cancelled) setLoading(false); });
        return () => { cancelled = true; };
    }, [period]);

    const filteredItems = useMemo(() => {
        if (!data?.items) return [];
        if (!classFilter) return data.items;
        return data.items.filter(i => i.classification === classFilter);
    }, [data, classFilter]);

    if (loading) {
        return <div className="p-8 text-white">Carregando inteligência de Ads...</div>;
    }

    if (!data || !data.has_data) {
        return (
            <div className="min-h-screen bg-[#09090b] text-slate-100 p-8">
                <h1 className="text-2xl font-bold text-white flex items-center gap-3 mb-4">
                    <Megaphone className="text-violet-500" /> Ads Intelligence
                </h1>
                <div className="bg-[#121217] border border-white/5 rounded-2xl p-8 text-slate-400">
                    Sem dados de Ads para o período. {data?.message || "Verifique se o sync/backfill de ml_ads_item_daily já rodou."}
                </div>
            </div>
        );
    }

    const s = data.summary;
    const classCounts = s.class_counts || {};

    return (
        <div className="min-h-screen bg-[#09090b] text-slate-100 p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                        <Megaphone className="text-violet-500" />
                        Ads Intelligence
                    </h1>
                    <p className="text-slate-400 mt-1">Performance real de Product Ads por anúncio — onde investir, onde cortar</p>
                </div>
                <div className="flex bg-slate-800/50 rounded-lg p-1 border border-white/5">
                    {[7, 15, 30, 60].map(d => (
                        <button
                            key={d}
                            onClick={() => setPeriod(d)}
                            className={`px-4 py-1.5 rounded-md text-xs font-bold transition-all ${period === d ? 'bg-violet-500 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
                        >
                            {d} dias
                        </button>
                    ))}
                </div>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="bg-[#121217] border border-white/5 rounded-2xl p-5">
                    <div className="text-[10px] text-slate-500 uppercase tracking-widest flex items-center gap-1.5 mb-2">
                        <DollarSign size={12} /> Investimento
                    </div>
                    <div className="text-2xl font-black text-white font-mono">{fmtBRL(s.total_spend)}</div>
                    <div className="text-[11px] text-slate-500 mt-1">{s.items_count} anúncios ativos em Ads</div>
                </div>
                <div className="bg-[#121217] border border-white/5 rounded-2xl p-5">
                    <div className="text-[10px] text-slate-500 uppercase tracking-widest flex items-center gap-1.5 mb-2">
                        <TrendingUp size={12} /> Receita via Ads
                    </div>
                    <div className="text-2xl font-black text-emerald-400 font-mono">{fmtBRL(s.total_ads_revenue)}</div>
                    <div className="text-[11px] text-slate-500 mt-1">{s.total_units} unidades vendidas</div>
                </div>
                <div className="bg-[#121217] border border-white/5 rounded-2xl p-5">
                    <div className="text-[10px] text-slate-500 uppercase tracking-widest flex items-center gap-1.5 mb-2">
                        <Target size={12} /> ACOS Global
                    </div>
                    <div className="text-2xl font-black text-white font-mono">
                        {s.global_acos != null ? `${s.global_acos.toFixed(1)}%` : "—"}
                    </div>
                    <div className="text-[11px] text-slate-500 mt-1">ROAS {s.global_roas != null ? s.global_roas.toFixed(1) : "—"}x</div>
                </div>
                <div className="bg-[#121217] border border-white/5 rounded-2xl p-5">
                    <div className="text-[10px] text-slate-500 uppercase tracking-widest flex items-center gap-1.5 mb-2">
                        <MousePointerClick size={12} /> Cliques
                    </div>
                    <div className="text-2xl font-black text-white font-mono">{s.total_clicks.toLocaleString('pt-BR')}</div>
                    <div className="text-[11px] text-slate-500 mt-1">{s.total_prints.toLocaleString('pt-BR')} impressões</div>
                </div>
                <div className={`rounded-2xl p-5 border ${s.burn_total > 0 ? 'bg-red-500/5 border-red-500/20' : 'bg-[#121217] border-white/5'}`}>
                    <div className="text-[10px] text-slate-500 uppercase tracking-widest flex items-center gap-1.5 mb-2">
                        <Flame size={12} className={s.burn_total > 0 ? "text-red-400" : ""} /> Dinheiro Queimando
                    </div>
                    <div className={`text-2xl font-black font-mono ${s.burn_total > 0 ? 'text-red-400' : 'text-white'}`}>{fmtBRL(s.burn_total)}</div>
                    <div className="text-[11px] text-slate-500 mt-1">
                        {(classCounts["queimando"] || 0) + (classCounts["prejuizo"] || 0)} anúncios sem retorno
                    </div>
                </div>
            </div>

            {/* Daily Chart */}
            <div className="bg-[#121217] border border-white/5 rounded-2xl p-6">
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-4">Gasto vs Receita via Ads (por dia)</h3>
                <div className="h-[260px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart data={data.daily_series}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0d" />
                            <XAxis
                                dataKey="date"
                                tick={{ fill: '#64748b', fontSize: 11 }}
                                tickFormatter={(d: string) => d.slice(8, 10) + '/' + d.slice(5, 7)}
                            />
                            <YAxis yAxisId="left" tick={{ fill: '#64748b', fontSize: 11 }} />
                            <YAxis yAxisId="right" orientation="right" tick={{ fill: '#64748b', fontSize: 11 }} />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#121217', border: '1px solid #ffffff1a', borderRadius: 12 }}
                                formatter={(value: any, name: any) => [fmtBRL(Number(value)), name === 'spend' ? 'Gasto' : 'Receita Ads']}
                                labelFormatter={(d: string) => d.slice(8, 10) + '/' + d.slice(5, 7)}
                            />
                            <Legend formatter={(v) => v === 'spend' ? 'Gasto' : 'Receita via Ads'} />
                            <Bar yAxisId="left" dataKey="spend" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                            <Line yAxisId="right" dataKey="ads_revenue" stroke="#10b981" strokeWidth={2} dot={false} />
                        </ComposedChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Classification Filter Chips */}
            <div className="flex items-center gap-2 flex-wrap">
                <button
                    onClick={() => setClassFilter(null)}
                    className={`px-3 py-1.5 rounded-full text-xs font-bold border transition-all ${!classFilter ? 'bg-white/10 border-white/20 text-white' : 'border-white/5 text-slate-400 hover:text-white'}`}
                >
                    Todos ({data.items.length})
                </button>
                {Object.entries(CLASS_META).map(([key, meta]) => {
                    const count = classCounts[key] || 0;
                    if (count === 0) return null;
                    const Icon = meta.icon;
                    return (
                        <button
                            key={key}
                            onClick={() => setClassFilter(classFilter === key ? null : key)}
                            className={`px-3 py-1.5 rounded-full text-xs font-bold border transition-all flex items-center gap-1.5
                                ${classFilter === key ? meta.bg + ' ' + meta.color : 'border-white/5 text-slate-400 hover:text-white'}`}
                        >
                            <Icon size={12} /> {meta.label} ({count})
                        </button>
                    );
                })}
            </div>

            {/* Items Table */}
            <div className="bg-[#121217] border border-white/5 rounded-2xl overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="text-left text-[10px] text-slate-500 uppercase tracking-widest border-b border-white/5">
                                <th className="px-4 py-3">Anúncio</th>
                                <th className="px-4 py-3">Status</th>
                                <th className="px-4 py-3 text-right">Gasto</th>
                                <th className="px-4 py-3 text-right">Receita Ads</th>
                                <th className="px-4 py-3 text-right">ACOS</th>
                                <th className="px-4 py-3 text-right">ROAS</th>
                                <th className="px-4 py-3 text-right">Margem</th>
                                <th className="px-4 py-3 text-right">Lucro via Ads</th>
                                <th className="px-4 py-3">Ação Sugerida</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredItems.map(item => {
                                const meta = CLASS_META[item.classification] || CLASS_META["saudavel"];
                                const Icon = meta.icon;
                                return (
                                    <tr key={item.item_id} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                                        <td className="px-4 py-3">
                                            <div className="flex items-center gap-3 max-w-[340px]">
                                                {item.thumbnail ? (
                                                    <img src={item.thumbnail} alt="" className="w-10 h-10 rounded-lg object-cover border border-white/10 shrink-0" />
                                                ) : (
                                                    <div className="w-10 h-10 rounded-lg bg-slate-800 shrink-0" />
                                                )}
                                                <div className="min-w-0">
                                                    <div className="text-white text-xs font-medium truncate flex items-center gap-1.5">
                                                        {item.title || item.item_id}
                                                        {item.permalink && (
                                                            <a href={item.permalink} target="_blank" rel="noopener noreferrer" className="text-slate-500 hover:text-violet-400 shrink-0">
                                                                <ExternalLink size={11} />
                                                            </a>
                                                        )}
                                                    </div>
                                                    <div className="text-[10px] text-slate-500 truncate">{item.sku || item.item_id} · {item.clicks} cliques · {item.units} un via Ads</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-[10px] font-bold border ${meta.bg} ${meta.color}`}>
                                                <Icon size={11} /> {meta.label}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-right font-mono text-white">{fmtBRL(item.spend)}</td>
                                        <td className="px-4 py-3 text-right font-mono text-slate-300">{fmtBRL(item.ads_revenue)}</td>
                                        <td className="px-4 py-3 text-right font-mono">
                                            {item.acos != null ? (
                                                <span className={item.margin_percent != null && item.acos >= item.margin_percent ? 'text-red-400' : 'text-white'}>
                                                    {item.acos.toFixed(1)}%
                                                </span>
                                            ) : <span className="text-slate-600">—</span>}
                                        </td>
                                        <td className="px-4 py-3 text-right font-mono text-slate-300">{item.roas != null ? `${item.roas.toFixed(1)}x` : '—'}</td>
                                        <td className="px-4 py-3 text-right font-mono text-slate-300">{item.margin_percent != null ? `${item.margin_percent.toFixed(1)}%` : <span className="text-slate-600" title="Cadastre o custo do produto">?</span>}</td>
                                        <td className="px-4 py-3 text-right font-mono">
                                            {item.ads_profit != null ? (
                                                <span className={item.ads_profit >= 0 ? 'text-emerald-400' : 'text-red-400'}>{fmtBRL(item.ads_profit)}</span>
                                            ) : <span className="text-slate-600">—</span>}
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="max-w-[260px]">
                                                <div className={`text-xs font-bold ${meta.color}`}>{item.action?.label}</div>
                                                <div className="text-[10px] text-slate-500 leading-tight mt-0.5" title={item.action?.reason}>
                                                    {item.action?.reason}
                                                </div>
                                                {item.action?.impact && (
                                                    <div className="text-[10px] text-slate-400 font-medium mt-0.5">{item.action.impact}</div>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
                {filteredItems.length === 0 && (
                    <div className="p-8 text-center text-slate-500 text-sm">Nenhum anúncio nesta classificação.</div>
                )}
            </div>

            <p className="text-[11px] text-slate-600">
                Ações são <strong>sugestões read-only</strong> — nada é alterado no Mercado Livre automaticamente.
                Margem "?" = produto sem custo cadastrado (classificação usa faixas fixas de ACOS).
            </p>
        </div>
    );
}
