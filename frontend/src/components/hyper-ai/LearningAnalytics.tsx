"use client";

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import {
    TrendingUp,
    TrendingDown,
    BarChart2,
    Grid3X3,
    Sliders,
    RefreshCw,
    Save,
    ChevronDown,
    ChevronUp,
    Edit2,
    Check,
    X,
    Calendar,
    Lock,
    Activity,
    Target,
    Brain,
    Clock,
    ShoppingCart,
    Zap,
    Info
} from 'lucide-react';
import { translateFactorType, translateFactorKey, getFactorLabel } from '@/lib/translations';
import EventsManager from './EventsManager';
import {
    LineChart,
    Line,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip as RechartsTooltip,
    ResponsiveContainer,
    AreaChart,
    Area,
    ReferenceLine
} from 'recharts';
import { Tooltip } from '../ui/Tooltip';

interface EvolutionData {
    date: string;
    accuracy: number;
    avg_error: number;
    predictions: number;
    predicted_total: number;
    real_total: number;
    calibrations?: number;
    best_factor?: string;
    worst_factor?: string;
}

interface FactorData {
    type: string;
    key: string;
    value: number;
    confidence: number;
    source: string;
    change_24h: number;
    change_7d: number;
    avg_error: number | null;
    samples: number;
    updated_at: string | null;
}

interface HeatmapCell {
    day: string;
    day_index: number;
    hour: number;
    avg_error: number | null;
    samples: number;
    status: 'good' | 'medium' | 'bad' | 'no_data';
}

interface LearningAnalyticsProps {
    period?: string;
    startDate?: string;
    endDate?: string;
}

export default function LearningAnalytics({ period = '7D', startDate, endDate }: LearningAnalyticsProps) {
    const [activeSection, setActiveSection] = useState<'evolution' | 'heatmap' | 'factors' | 'events'>('evolution');
    const [evolution, setEvolution] = useState<EvolutionData[]>([]);
    const [heatmap, setHeatmap] = useState<HeatmapCell[]>([]);
    const [factors, setFactors] = useState<FactorData[]>([]);
    const [groupedFactors, setGroupedFactors] = useState<Record<string, FactorData[]>>({});
    const [loading, setLoading] = useState(false);
    const [editingFactor, setEditingFactor] = useState<string | null>(null);
    const [editValue, setEditValue] = useState<string>('');
    const [expandedTypes, setExpandedTypes] = useState<Record<string, boolean>>({});
    const [newFactorInputs, setNewFactorInputs] = useState<Record<string, string>>({});
    const [isAddingFactor, setIsAddingFactor] = useState<string | null>(null);

    // ... existing fetch functions ...

    const handleAddFactor = async (type: string) => {
        const key = newFactorInputs[type];
        if (!key) return;

        setIsAddingFactor(type);
        try {
            await api.post('/forecast/allowed-factors', {
                factor_type: type,
                factor_key: key,
                description: 'Adicionado manualmente via Dashboard'
            });

            // Clear input and refresh
            setNewFactorInputs(prev => ({ ...prev, [type]: '' }));
            await fetchFactors();

        } catch (e) {
            console.error('Error adding factor:', e);
            alert('Erro ao adicionar fator. Verifique se a chave já existe.');
        } finally {
            setIsAddingFactor(null);
        }
    };

    // Convert period to days and check if daily view
    const isDailyView = period === 'Hoje' || period === 'Ontem';
    const days = period === 'Hoje' || period === 'Ontem' ? 1 : period === '7D' ? 7 : period === '30D' ? 30 : 7;

    const fetchEvolution = async () => {
        try {
            let url = `/forecast/analytics/evolution?days=${days}`;
            if (startDate && endDate) {
                url += `&start_date=${startDate}&end_date=${endDate}`;
            }
            const res = await api.get(url);
            if (res.data.success) {
                setEvolution(res.data.data.evolution);
            }
        } catch (e) {
            console.error('Error fetching evolution:', e);
        }
    };

    const fetchHeatmap = async () => {
        try {
            const res = await api.get(`/forecast/analytics/heatmap?days=${days}`);
            if (res.data.success) {
                setHeatmap(res.data.data.heatmap);
            }
        } catch (e) {
            console.error('Error fetching heatmap:', e);
        }
    };

    const fetchFactors = async () => {
        try {
            const res = await api.get(`/forecast/analytics/factors?days=${days}`);
            if (res.data.success) {
                setFactors(res.data.data.factors);

                // Custom sort for day_of_week
                const grouped = res.data.data.grouped;
                if (grouped.day_of_week) {
                    const dayOrder = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo'];
                    grouped.day_of_week = grouped.day_of_week.sort((a: FactorData, b: FactorData) => {
                        const aIndex = dayOrder.indexOf(a.key.toLowerCase());
                        const bIndex = dayOrder.indexOf(b.key.toLowerCase());
                        return aIndex - bIndex;
                    });
                }

                setGroupedFactors(grouped);
            }
        } catch (e) {
            console.error('Error fetching factors:', e);
        }
    };

    const loadData = async () => {
        setLoading(true);
        await Promise.all([fetchEvolution(), fetchHeatmap(), fetchFactors()]);
        setLoading(false);
    };

    useEffect(() => {
        loadData();
    }, [period, startDate, endDate]);

    const updateFactor = async (type: string, key: string, value: number) => {
        try {
            const res = await api.put(`/forecast/analytics/factors/${type}/${key}`, { value });
            if (res.data.success) {
                fetchFactors();
                setEditingFactor(null);
            }
        } catch (e) {
            console.error('Error updating factor:', e);
        }
    };

    const toggleType = (type: string) => {
        setExpandedTypes(prev => ({
            ...prev,
            [type]: !prev[type]
        }));
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'good': return 'bg-emerald-500';
            case 'medium': return 'bg-yellow-500';
            case 'bad': return 'bg-red-500';
            default: return 'bg-slate-700';
        }
    };

    const formatPercent = (v: number | null) => v !== null ? `${v.toFixed(1)}%` : '-';

    const formatDateSafe = (dateStr: string) => {
        if (!dateStr) return '-';
        // Handle "YYYY-MM-DD" string manually to avoid timezone shift
        // If it comes as ISO with time, split it
        const cleanDate = dateStr.split('T')[0];
        const parts = cleanDate.split('-'); // [YYYY, MM, DD]
        if (parts.length === 3) {
            return `${parts[2]}/${parts[1]}/${parts[0]}`; // DD/MM/YYYY
        }
        return new Date(dateStr).toLocaleDateString('pt-BR'); // Fallback
    };

    // Also helper for month/day (DD/MM)
    const formatDaySafe = (dateStr: string) => {
        if (!dateStr) return '-';
        const cleanDate = dateStr.split('T')[0];
        const parts = cleanDate.split('-');
        if (parts.length === 3) {
            return `${parts[2]}/${parts[1]}`;
        }
        return new Date(dateStr).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
    };

    // Custom Tooltip for Recharts
    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-[#1A1A2E] border border-slate-700/50 p-3 rounded-lg shadow-xl text-xs z-50">
                    <p className="text-slate-400 font-medium mb-2">{formatDateSafe(label)}</p>
                    {payload.map((entry: any, index: number) => (
                        <div key={index} className="flex items-center gap-2 mb-1 last:mb-0">
                            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
                            <span className="text-slate-300 capitalize">
                                {entry.name === 'accuracy' ? 'Acurácia' :
                                    entry.name === 'predicted_total' ? 'Previsto' :
                                        entry.name === 'real_total' ? 'Real' :
                                            entry.name === 'avg_error' ? 'Erro Médio' : entry.name}:
                            </span>
                            <span className="font-mono text-white font-medium">
                                {entry.name.includes('total')
                                    ? `R$ ${entry.value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`
                                    : `${entry.value.toFixed(1)}%`
                                }
                            </span>
                        </div>
                    ))}
                </div>
            );
        }
        return null;
    };

    return (
        <div className="space-y-6">
            {/* Header with controls */}
            <div className="flex justify-between items-center">
                <div className="flex gap-2">
                    <button
                        onClick={() => setActiveSection('evolution')}
                        className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 cursor-pointer ${activeSection === 'evolution'
                            ? 'bg-purple-600 text-white'
                            : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                            }`}
                    >
                        <TrendingUp className="w-4 h-4" />
                        Evolução
                    </button>
                    <button
                        onClick={() => setActiveSection('heatmap')}
                        className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 cursor-pointer ${activeSection === 'heatmap'
                            ? 'bg-purple-600 text-white'
                            : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                            }`}
                    >
                        <Grid3X3 className="w-4 h-4" />
                        Heatmap
                    </button>
                    <button
                        onClick={() => setActiveSection('factors')}
                        className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 cursor-pointer ${activeSection === 'factors'
                            ? 'bg-purple-600 text-white'
                            : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                            }`}
                    >
                        <Sliders className="w-4 h-4" />
                        Sub-Fatores
                    </button>
                    <button
                        onClick={() => setActiveSection('events')}
                        className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 cursor-pointer ${activeSection === 'events'
                            ? 'bg-purple-600 text-white'
                            : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                            }`}
                    >
                        <Calendar className="w-4 h-4" />
                        Eventos
                    </button>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={loadData}
                        disabled={loading}
                        className="p-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </div>

            {/* Evolution Section - Rich Dashboard */}
            {activeSection === 'evolution' && (
                <div className="space-y-6">
                    {evolution.length === 0 ? (
                        <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                            <p className="text-slate-500">Nenhum dado de evolução disponível para o período selecionado.</p>
                        </div>
                    ) : (
                        <>
                            {/* Summary Cards Row */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-4">
                                    <div className="text-xs text-slate-500 uppercase flex items-center gap-1.5">
                                        Acurácia Média
                                        <Tooltip
                                            title="Precisão do Modelo"
                                            content="Média de acerto das previsões em relação aos valores reais processados."
                                        >
                                            <Info className="w-3.5 h-3.5 text-slate-600 hover:text-emerald-400 transition-colors cursor-help" />
                                        </Tooltip>
                                    </div>
                                    <div className="text-2xl font-bold text-white mt-1">
                                        {(evolution.reduce((sum, e) => sum + e.accuracy, 0) / evolution.length).toFixed(1)}%
                                    </div>
                                    <div className="text-xs text-slate-500 mt-1">{days} dias</div>
                                </div>
                                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-4">
                                    <div className="text-xs text-slate-500 uppercase flex items-center gap-1.5">
                                        Total Previsto
                                        <Tooltip
                                            title="Volume Projetado"
                                            content="Soma total do faturamento que o Hyper AI previu para o período selecionado."
                                        >
                                            <Info className="w-3.5 h-3.5 text-slate-600 hover:text-cyan-400 transition-colors cursor-help" />
                                        </Tooltip>
                                    </div>
                                    <div className="text-2xl font-bold text-cyan-400 mt-1">
                                        R$ {evolution.reduce((sum, e) => sum + e.predicted_total, 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                    </div>
                                </div>
                                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-4">
                                    <div className="text-xs text-slate-500 uppercase flex items-center gap-1.5">
                                        Total Real
                                        <Tooltip
                                            title="Faturamento Efivado"
                                            content="Soma total do faturamento real reconciliado no período selecionado."
                                        >
                                            <Info className="w-3.5 h-3.5 text-slate-600 hover:text-emerald-400 transition-colors cursor-help" />
                                        </Tooltip>
                                    </div>
                                    <div className="text-2xl font-bold text-emerald-400 mt-1">
                                        R$ {evolution.reduce((sum, e) => sum + e.real_total, 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                    </div>
                                </div>
                                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-4">
                                    <div className="text-xs text-slate-500 uppercase flex items-center gap-1.5">
                                        Calibrações
                                        <Tooltip
                                            title="Ajustes Automáticos"
                                            content="Número de vezes que o sistema recalibrou os multiplicadores para reduzir o erro nas previsões."
                                        >
                                            <Info className="w-3.5 h-3.5 text-slate-600 hover:text-purple-400 transition-colors cursor-help" />
                                        </Tooltip>
                                    </div>
                                    <div className="text-2xl font-bold text-purple-400 mt-1">
                                        {evolution.reduce((sum, e) => sum + (e.calibrations || 0), 0)}
                                    </div>
                                    <div className="text-xs text-slate-500 mt-1">ajustes automáticos</div>
                                </div>
                            </div>



                            {/* Charts Row 1: Accuracy Trend + Previsto vs Real */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                {/* Accuracy Trend Chart */}
                                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                                    <h4 className="text-md font-semibold text-white mb-4 flex items-center gap-2">
                                        <TrendingUp className="w-4 h-4 text-emerald-400" />
                                        Tendência de Acurácia
                                        <div className="group relative ml-1">
                                            <Info className="w-3.5 h-3.5 text-slate-500 cursor-help" />
                                            <div className="absolute top-0 left-full ml-2 w-72 p-3 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                                                <p className="mb-2">A <span className="text-white font-medium">Acurácia</span> mede a precisão do modelo em relação ao valor real.</p>
                                                <p className="mb-2">Se o modelo previu <span className="text-cyan-400">R$ 100</span> e o real foi <span className="text-emerald-400">R$ 105</span>, o erro foi de 5%.</p>
                                                <p className="font-medium text-white">Logo, a Acurácia seria de 95%.</p>
                                                <div className="mt-2 text-[10px] text-slate-500 border-t border-slate-800 pt-1">
                                                    Quanto maior, melhor a performance do modelo.
                                                </div>
                                            </div>
                                        </div>
                                    </h4>
                                    <div className="h-64 w-full">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <LineChart data={evolution}>
                                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                                <XAxis
                                                    dataKey="date"
                                                    tickFormatter={formatDaySafe}
                                                    stroke="#64748b"
                                                    fontSize={10}
                                                    tickLine={false}
                                                    axisLine={false}
                                                    padding={{ left: 10, right: 10 }}
                                                />
                                                <YAxis
                                                    stroke="#64748b"
                                                    fontSize={10}
                                                    tickLine={false}
                                                    axisLine={false}
                                                    domain={[0, 100]}
                                                    tickFormatter={(v) => `${v}%`}
                                                />
                                                <RechartsTooltip content={<CustomTooltip />} cursor={{ stroke: '#334155' }} />
                                                <Line
                                                    type="monotone"
                                                    dataKey="accuracy"
                                                    stroke="#10b981"
                                                    strokeWidth={2}
                                                    dot={{ r: 3, fill: '#10b981', strokeWidth: 0 }}
                                                    activeDot={{ r: 5, strokeWidth: 0 }}
                                                />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>

                                {/* Previsto vs Real Chart */}
                                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                                    <h4 className="text-md font-semibold text-white mb-4 flex items-center gap-2">
                                        <BarChart2 className="w-4 h-4 text-cyan-400" />
                                        Previsto vs Real (R$)
                                        <div className="group relative ml-1">
                                            <Info className="w-3.5 h-3.5 text-slate-500 cursor-help" />
                                            <div className="absolute top-0 right-full mr-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                                                Comparativo direto entre o volume financeiro <span className="text-cyan-400">Previsto</span> e o <span className="text-emerald-400">Real</span>.
                                                <div className="mt-2 text-[10px] text-slate-500 border-t border-slate-800 pt-1">
                                                    Útil para identificar dias com grandes desvios de volume (overprediction ou underprediction).
                                                </div>
                                            </div>
                                        </div>
                                    </h4>
                                    <div className="h-64 w-full">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <BarChart data={evolution} barGap={2}>
                                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                                <XAxis
                                                    dataKey="date"
                                                    tickFormatter={formatDaySafe}
                                                    stroke="#64748b"
                                                    fontSize={10}
                                                    tickLine={false}
                                                    axisLine={false}
                                                />
                                                <YAxis
                                                    stroke="#64748b"
                                                    fontSize={10}
                                                    tickLine={false}
                                                    axisLine={false}
                                                    tickFormatter={(v) => `R$ ${v / 1000}k`}
                                                />
                                                <RechartsTooltip content={<CustomTooltip />} cursor={{ fill: '#ffffff05' }} />
                                                <Bar dataKey="predicted_total" name="Previsto" fill="#06b6d4" radius={[4, 4, 0, 0]} maxBarSize={50} />
                                                <Bar dataKey="real_total" name="Real" fill="#10b981" radius={[4, 4, 0, 0]} maxBarSize={50} />
                                            </BarChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>
                            </div>

                            {/* Charts Row 2: Best/Worst Factors + Error Distribution */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                {/* Best/Worst Factors (Kept as list for now as it's text data) */}
                                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                                    <h4 className="text-md font-semibold text-white mb-4 flex items-center gap-2">
                                        <Sliders className="w-4 h-4 text-purple-400" />
                                        Fatores de Maior Impacto
                                        <div className="group relative ml-1">
                                            <Info className="w-3.5 h-3.5 text-slate-500 cursor-help" />
                                            <div className="absolute top-0 left-full ml-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                                                Analisa quais variáveis do modelo mais influenciaram o resultado.
                                                <ul className="mt-2 space-y-1 list-disc list-inside text-slate-400">
                                                    <li><span className="text-emerald-400">Top 3 Melhores:</span> Menor erro médio.</li>
                                                    <li><span className="text-red-400">Top 3 Piores:</span> Maior erro médio.</li>
                                                </ul>
                                            </div>
                                        </div>
                                    </h4>
                                    <div className="space-y-4">
                                        {(() => {
                                            // 1. Filter: Only show factors that have actually been used (samples > 0)
                                            // and have valid error data
                                            const activeFactors = factors.filter(f => (f.samples || 0) > 0 && f.avg_error !== null);

                                            const sorted = [...activeFactors].sort((a, b) => (a.avg_error || 0) - (b.avg_error || 0));
                                            const best = sorted.slice(0, 3);
                                            const worst = sorted.slice().reverse().slice(0, 3);

                                            if (activeFactors.length === 0) {
                                                return (
                                                    <div className="flex flex-col items-center justify-center h-48 text-slate-600 bg-slate-900/20 rounded-xl border border-dashed border-slate-800">
                                                        <Activity className="w-8 h-8 mb-2 opacity-30" />
                                                        <p className="text-sm font-medium">Análise em processamento</p>
                                                        <p className="text-[10px] opacity-70 px-8 text-center">Fatores aparecem aqui após as primeiras previsões serem reconciliadas e calibradas.</p>
                                                    </div>
                                                );
                                            }

                                            const renderFactorCard = (f: FactorData, isBest: boolean) => {
                                                const label = translateFactorKey(f.key, f.type);
                                                const typeLabel = translateFactorType(f.type);
                                                const error = f.avg_error || 0;
                                                const accuracy = Math.max(0, 100 - error);

                                                return (
                                                    <div key={`${f.type}.${f.key}`} className="bg-slate-900/40 border border-slate-800/50 rounded-lg p-3 hover:border-slate-700 transition-colors group">
                                                        <div className="flex justify-between items-start mb-2">
                                                            <div className="flex flex-col">
                                                                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">{typeLabel}</span>
                                                                <span className="text-sm font-bold text-white capitalize">{label}</span>
                                                            </div>
                                                            <div className="text-right">
                                                                <div className={`text-sm font-mono font-bold ${isBest ? 'text-emerald-400' : 'text-red-400'}`}>
                                                                    {accuracy.toFixed(1)}%
                                                                </div>
                                                                <div className="text-[10px] text-slate-500">
                                                                    {f.samples} {f.samples === 1 ? 'amostra' : 'amostras'}
                                                                </div>
                                                            </div>
                                                        </div>
                                                        <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden mt-1">
                                                            <div
                                                                className={`h-full rounded-full ${isBest ? 'bg-emerald-500' : 'bg-red-500'}`}
                                                                style={{ width: `${accuracy}%` }}
                                                            />
                                                        </div>
                                                    </div>
                                                );
                                            };

                                            return (
                                                <div className="grid grid-cols-2 gap-4">
                                                    <div>
                                                        <div className="text-xs font-semibold text-emerald-400 mb-2 uppercase tracking-wide border-b border-emerald-500/20 pb-1 flex justify-between">
                                                            <span>Mais Precisos</span>
                                                            <span className="text-[10px] text-emerald-400/50">Top 3</span>
                                                        </div>
                                                        <div className="space-y-2">
                                                            {best.map(f => renderFactorCard(f, true))}
                                                        </div>
                                                    </div>
                                                    <div>
                                                        <div className="text-xs font-semibold text-red-100/50 mb-2 uppercase tracking-wide border-b border-red-500/20 pb-1 flex justify-between">
                                                            <span className="text-red-400">Maior Desvio</span>
                                                            <span className="text-[10px] text-red-400/50">Top 3</span>
                                                        </div>
                                                        <div className="space-y-2">
                                                            {worst.map(f => renderFactorCard(f, false))}
                                                        </div>
                                                    </div>
                                                </div>
                                            );
                                        })()}
                                    </div>
                                </div>

                                {/* Error Trend */}
                                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                                    <h4 className="text-md font-semibold text-white mb-4 flex items-center gap-2">
                                        <TrendingDown className="w-4 h-4 text-red-400" />
                                        Erro Médio (%)
                                        <div className="group relative ml-1">
                                            <Info className="w-3.5 h-3.5 text-slate-500 cursor-help" />
                                            <div className="absolute top-0 right-full mr-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                                                Média absoluta dos erros percentuais (MAPE) por dia.
                                                <p className="mt-2 mb-1 text-slate-400">Indica a margem de erro média das previsões.</p>
                                                <div className="mt-1 text-[10px] text-slate-500 border-t border-slate-800 pt-1">
                                                    Ideal que se mantenha abaixo de 20-30% para previsões voláteis.
                                                </div>
                                            </div>
                                        </div>
                                    </h4>
                                    <div className="h-64 w-full">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <AreaChart data={evolution}>
                                                <defs>
                                                    <linearGradient id="colorError" x1="0" y1="0" x2="0" y2="1">
                                                        <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.3} />
                                                        <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                                                    </linearGradient>
                                                </defs>
                                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                                <XAxis
                                                    dataKey="date"
                                                    tickFormatter={formatDaySafe}
                                                    stroke="#64748b"
                                                    fontSize={10}
                                                    tickLine={false}
                                                    axisLine={false}
                                                />
                                                <YAxis
                                                    stroke="#64748b"
                                                    fontSize={10}
                                                    tickLine={false}
                                                    axisLine={false}
                                                    tickFormatter={(v) => `${v}%`}
                                                />
                                                <RechartsTooltip content={<CustomTooltip />} cursor={{ stroke: '#334155' }} />
                                                <Area
                                                    type="monotone"
                                                    dataKey="avg_error"
                                                    stroke="#f43f5e"
                                                    fillOpacity={1}
                                                    fill="url(#colorError)"
                                                />
                                            </AreaChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>
                            </div>

                            {/* Detailed Table */}
                            <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                                <h4 className="text-md font-semibold text-white mb-4 flex items-center gap-2">
                                    <BarChart2 className="w-4 h-4 text-purple-400" />
                                    Dados Completos por Dia
                                </h4>
                                <div className="overflow-x-auto">
                                    <table className="w-full text-sm">
                                        <thead>
                                            <tr className="text-left text-slate-500 border-b border-slate-800 text-[10px] uppercase tracking-widest">
                                                <th className="px-4 py-3 font-bold whitespace-nowrap border-r border-slate-800/30 last:border-r-0">
                                                    <div className="flex items-center gap-1.5">
                                                        <Calendar className="w-3 h-3" />
                                                        Data
                                                    </div>
                                                </th>
                                                <th className="px-4 py-3 font-bold whitespace-nowrap border-r border-slate-800/30 last:border-r-0">
                                                    <div className="flex items-center gap-1.5">
                                                        <Target className="w-3 h-3" />
                                                        Previsões
                                                    </div>
                                                </th>
                                                <th className="px-4 py-3 font-bold whitespace-nowrap border-r border-slate-800/30 last:border-r-0">
                                                    <div className="flex items-center gap-1.5">
                                                        <Check className="w-3 h-3" />
                                                        Acurácia
                                                    </div>
                                                </th>
                                                <th className="px-4 py-3 font-bold whitespace-nowrap border-r border-slate-800/30 last:border-r-0">
                                                    <div className="flex items-center gap-1.5">
                                                        <Activity className="w-3 h-3" />
                                                        Erro Médio
                                                    </div>
                                                </th>
                                                <th className="px-4 py-3 font-bold whitespace-nowrap border-r border-slate-800/30 last:border-r-0">
                                                    <div className="flex items-center gap-1.5">
                                                        <Zap className="w-3 h-3" />
                                                        Previsto
                                                    </div>
                                                </th>
                                                <th className="px-4 py-3 font-bold whitespace-nowrap border-r border-slate-800/30 last:border-r-0">
                                                    <div className="flex items-center gap-1.5">
                                                        <ShoppingCart className="w-3 h-3" />
                                                        Real
                                                    </div>
                                                </th>
                                                <th className="px-4 py-2 font-semibold whitespace-nowrap">
                                                    <div className="flex items-center gap-1.5">
                                                        <TrendingUp className="w-3 h-3" />
                                                        Diferença
                                                    </div>
                                                </th>
                                                <th className="px-4 py-2 font-semibold whitespace-nowrap">
                                                    <div className="flex items-center gap-1.5">
                                                        <Sliders className="w-3 h-3" />
                                                        Calibrações
                                                    </div>
                                                </th>
                                                <th className="px-4 py-2 font-semibold whitespace-nowrap">
                                                    <div className="flex items-center gap-1.5">
                                                        <Brain className="w-3 h-3" />
                                                        Melhor Fator
                                                    </div>
                                                </th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {evolution.slice().reverse().map((e, i) => {
                                                const diff = e.real_total - e.predicted_total;
                                                const diffPercent = e.predicted_total > 0 ? (diff / e.predicted_total) * 100 : 0;
                                                return (
                                                    <tr key={i} className="border-b border-slate-800/50 text-slate-300 hover:bg-slate-800/30">
                                                        <td className="py-2 pr-4">{formatDateSafe(e.date)}</td>
                                                        <td className="py-2 pr-4">{e.predictions}</td>
                                                        <td className="py-2 pr-4">
                                                            <span className={`font-medium ${e.accuracy >= 90 ? 'text-emerald-400' :
                                                                e.accuracy >= 70 ? 'text-yellow-400' : 'text-red-400'
                                                                }`}>
                                                                {e.accuracy.toFixed(1)}%
                                                            </span>
                                                        </td>
                                                        <td className="py-2 pr-4">{e.avg_error.toFixed(1)}%</td>
                                                        <td className="py-2 pr-4 text-cyan-400">
                                                            R$ {e.predicted_total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                                        </td>
                                                        <td className="py-2 pr-4 text-emerald-400">
                                                            R$ {e.real_total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                                        </td>
                                                        <td className="py-2 pr-4">
                                                            <span className={diff >= 0 ? 'text-emerald-400' : 'text-red-400'}>
                                                                {diff >= 0 ? '+' : ''}{diffPercent.toFixed(1)}%
                                                            </span>
                                                        </td>
                                                        <td className="py-2 pr-4 text-purple-400">{e.calibrations || '-'}</td>
                                                        <td className="py-2 text-xs">{e.best_factor || '-'}</td>
                                                    </tr>
                                                );
                                            })}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </>
                    )}
                </div>
            )}

            {/* Heatmap Section */}
            {activeSection === 'heatmap' && (
                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                    {/* Header with Legend aligned to the right */}
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                            <Grid3X3 className="w-5 h-5 text-purple-400" />
                            <span title="Mapa de calor mostrando erro médio das previsões por hora e dia da semana">Performance Hora × Dia</span>
                            <span className="text-slate-500 text-sm font-normal">({days} dias)</span>
                        </h3>

                        {/* Legend - Top Right */}
                        <div className="flex items-center gap-4 text-xs text-slate-400">
                            <div className="flex items-center gap-1 cursor-help" title="Previsões com erro menor que 10% - excelente precisão">
                                <div className="w-4 h-4 rounded bg-emerald-500"></div>
                                <span>Erro &lt; 10%</span>
                            </div>
                            <div className="flex items-center gap-1 cursor-help" title="Previsões com erro entre 10% e 20% - precisão aceitável">
                                <div className="w-4 h-4 rounded bg-yellow-500"></div>
                                <span>10-20%</span>
                            </div>
                            <div className="flex items-center gap-1 cursor-help" title="Previsões com erro maior que 20% - precisa melhorar">
                                <div className="w-4 h-4 rounded bg-red-500"></div>
                                <span>&gt; 20%</span>
                            </div>
                            <div className="flex items-center gap-1 cursor-help" title="Nenhuma previsão foi feita para este horário ainda">
                                <div className="w-4 h-4 rounded bg-slate-700"></div>
                                <span>Sem dados</span>
                            </div>
                        </div>
                    </div>

                    <div className="overflow-x-auto pb-4 [&::-webkit-scrollbar]:h-2 [&::-webkit-scrollbar-track]:bg-slate-800/30 [&::-webkit-scrollbar-track]:rounded-full [&::-webkit-scrollbar-thumb]:bg-purple-500/50 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:hover:bg-purple-500/70">
                        <div className="min-w-[800px]">
                            {/* Header - Hours */}
                            <div className="flex gap-1 mb-1">
                                <div className="w-12"></div>
                                {Array.from({ length: 24 }, (_, h) => (
                                    <div key={h} className="flex-1 text-center text-xs text-slate-500">
                                        {h}h
                                    </div>
                                ))}
                            </div>

                            {/* Days */}
                            {['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom'].map((day, di) => (
                                <div key={day} className="flex gap-1 mb-1">
                                    <div className="w-12 text-xs text-slate-400 flex items-center justify-end pr-2">
                                        {day}
                                    </div>
                                    {Array.from({ length: 24 }, (_, h) => {
                                        const cell = heatmap.find(c => c.day_index === di && c.hour === h);
                                        return (
                                            <div
                                                key={h}
                                                className={`flex-1 h-6 rounded ${getStatusColor(cell?.status || 'no_data')} 
                                                    transition-all hover:scale-110 cursor-pointer group relative`}
                                                title={cell ? `${cell.avg_error?.toFixed(1)}% erro (${cell.samples} amostras)` : 'Sem dados'}
                                            >
                                                {cell?.status !== 'no_data' && cell?.samples && cell.samples > 0 && (
                                                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-slate-900 text-white text-xs 
                                                        px-2 py-1 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap z-10">
                                                        {formatPercent(cell.avg_error)}
                                                    </div>
                                                )}
                                            </div>
                                        );
                                    })}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Sub-Factors Section */}
            {activeSection === 'factors' && (
                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <Sliders className="w-5 h-5 text-purple-400" />
                        Sub-Fatores e Multiplicadores
                    </h3>
                    <p className="text-slate-500 text-sm mb-4">
                        Cada fator tem múltiplos sub-valores. Clique para expandir e editar.
                    </p>

                    {Object.keys(groupedFactors).length === 0 ? (
                        <p className="text-slate-500">Nenhum multiplicador configurado ainda.</p>
                    ) : (
                        <div className="space-y-2">
                            {Object.entries(groupedFactors).map(([type, factors]) => (
                                <div key={type} className="border border-slate-800 rounded-lg overflow-hidden">
                                    {/* Type Header */}
                                    <button
                                        onClick={() => toggleType(type)}
                                        className="w-full px-4 py-3 bg-slate-900/50 flex justify-between items-center hover:bg-slate-800/50 cursor-pointer"
                                    >
                                        <span className="text-white font-medium capitalize">{translateFactorType(type)}</span>
                                        <div className="flex items-center gap-2">
                                            <span className="text-slate-500 text-sm">{factors.length} valores</span>
                                            {expandedTypes[type] ? (
                                                <ChevronUp className="w-4 h-4 text-slate-400" />
                                            ) : (
                                                <ChevronDown className="w-4 h-4 text-slate-400" />
                                            )}
                                        </div>
                                    </button>

                                    {/* Expanded Content */}
                                    {expandedTypes[type] && (
                                        <div className="divide-y divide-slate-800/50">
                                            {factors.map((f, i) => {
                                                const factorKey = `${f.type}.${f.key}`;
                                                const uniqueReactKey = `${factorKey}_${i}`;
                                                const isEditing = editingFactor === factorKey;

                                                return (
                                                    <div key={uniqueReactKey} className="px-4 py-3 flex items-center justify-between">
                                                        <div className="flex-1">
                                                            <div className="flex items-center gap-2">
                                                                <span className="text-white font-mono" title="Identificador único do sub-fator">{translateFactorKey(f.key, f.type)}</span>
                                                                <span
                                                                    className={`text-xs px-2 py-0.5 rounded cursor-help ${f.source === 'auto' ? 'bg-emerald-500/20 text-emerald-400' :
                                                                        f.source === 'manual' ? 'bg-purple-500/20 text-purple-400' :
                                                                            'bg-slate-600/30 text-slate-500'
                                                                        }`}
                                                                    title={
                                                                        f.source === 'auto' ? 'Calibrado automaticamente pelo sistema baseado em dados reais' :
                                                                            f.source === 'manual' ? 'Editado manualmente - sistema não sobrescreve' :
                                                                                'Valor padrão inicial - nunca foi calibrado'
                                                                    }
                                                                >
                                                                    {f.source === 'auto' ? '✓ Calibrado' : f.source === 'manual' ? '✎ Manual' : '○ Default'}
                                                                </span>
                                                            </div>
                                                            <div className="flex gap-4 mt-1 text-xs text-slate-500">
                                                                <span className="cursor-help" title="Erro médio percentual nas previsões quando este fator estava ativo">
                                                                    Erro: {f.avg_error !== null ? `${f.avg_error}%` : '-'}
                                                                </span>
                                                                <span className="cursor-help" title="Quantidade de previsões que usaram este fator - quanto mais, melhor">
                                                                    Amostras: {f.samples}
                                                                </span>
                                                                <span className="cursor-help" title="Nível de confiança estatística baseado em amostras e consistência">
                                                                    Confiança: {f.confidence}%
                                                                </span>
                                                                {f.change_24h !== 0 && (
                                                                    <span
                                                                        className={`cursor-help ${f.change_24h > 0 ? 'text-emerald-400' : 'text-red-400'}`}
                                                                        title={`Variação nas últimas 24h: ${f.change_24h > 0 ? 'aumentou' : 'diminuiu'} devido à calibração automática`}
                                                                    >
                                                                        24h: {f.change_24h > 0 ? '+' : ''}{(f.change_24h * 100).toFixed(1)}%
                                                                    </span>
                                                                )}
                                                            </div>
                                                        </div>

                                                        <div className="flex items-center gap-3">
                                                            {isEditing ? (
                                                                <div className="flex items-center gap-2">
                                                                    {/* Percentage adjustment buttons */}
                                                                    <div className="flex gap-1">
                                                                        <button
                                                                            onClick={() => {
                                                                                const currentVal = parseFloat(editValue);
                                                                                setEditValue((currentVal * 0.90).toFixed(3));
                                                                            }}
                                                                            className="px-2 py-1 bg-red-900/30 hover:bg-red-800/50 border border-red-700/50 rounded text-red-400 text-xs font-medium transition-colors"
                                                                            title="Reduzir 10%"
                                                                        >
                                                                            -10%
                                                                        </button>
                                                                        <button
                                                                            onClick={() => {
                                                                                const currentVal = parseFloat(editValue);
                                                                                setEditValue((currentVal * 0.95).toFixed(3));
                                                                            }}
                                                                            className="px-2 py-1 bg-red-900/30 hover:bg-red-800/50 border border-red-700/50 rounded text-red-400 text-xs font-medium transition-colors"
                                                                            title="Reduzir 5%"
                                                                        >
                                                                            -5%
                                                                        </button>
                                                                    </div>

                                                                    {/* Manual input */}
                                                                    <input
                                                                        type="number"
                                                                        step="0.001"
                                                                        value={editValue}
                                                                        onChange={(e) => setEditValue(e.target.value)}
                                                                        className="w-20 px-2 py-1 bg-slate-800 border border-slate-700 rounded text-white text-sm text-center font-mono"
                                                                        title="Valor exato do multiplicador"
                                                                    />

                                                                    {/* Percentage increase buttons */}
                                                                    <div className="flex gap-1">
                                                                        <button
                                                                            onClick={() => {
                                                                                const currentVal = parseFloat(editValue);
                                                                                setEditValue((currentVal * 1.05).toFixed(3));
                                                                            }}
                                                                            className="px-2 py-1 bg-emerald-900/30 hover:bg-emerald-800/50 border border-emerald-700/50 rounded text-emerald-400 text-xs font-medium transition-colors"
                                                                            title="Aumentar 5%"
                                                                        >
                                                                            +5%
                                                                        </button>
                                                                        <button
                                                                            onClick={() => {
                                                                                const currentVal = parseFloat(editValue);
                                                                                setEditValue((currentVal * 1.10).toFixed(3));
                                                                            }}
                                                                            className="px-2 py-1 bg-emerald-900/30 hover:bg-emerald-800/50 border border-emerald-700/50 rounded text-emerald-400 text-xs font-medium transition-colors"
                                                                            title="Aumentar 10%"
                                                                        >
                                                                            +10%
                                                                        </button>
                                                                    </div>

                                                                    {/* Action buttons */}
                                                                    <div className="flex gap-1 ml-1">
                                                                        <button
                                                                            onClick={() => updateFactor(f.type, f.key, parseFloat(editValue))}
                                                                            className="p-1.5 bg-emerald-900/30 hover:bg-emerald-800/50 border border-emerald-700/50 rounded text-emerald-400 cursor-pointer transition-colors"
                                                                            title="Salvar alteração"
                                                                        >
                                                                            <Check className="w-4 h-4" />
                                                                        </button>
                                                                        <button
                                                                            onClick={() => setEditingFactor(null)}
                                                                            className="p-1.5 bg-red-900/30 hover:bg-red-800/50 border border-red-700/50 rounded text-red-400 cursor-pointer transition-colors"
                                                                            title="Cancelar"
                                                                        >
                                                                            <X className="w-4 h-4" />
                                                                        </button>
                                                                    </div>
                                                                </div>
                                                            ) : (
                                                                <>
                                                                    <span
                                                                        className={`text-lg font-mono cursor-help ${f.value > 1.1 ? 'text-emerald-400' :
                                                                            f.value < 0.9 ? 'text-red-400' : 'text-white'
                                                                            }`}
                                                                        title={`MULTIPLICADOR ATIVO (${f.source === 'auto' ? 'Calibrado Automaticamente' : 'Valor Padrão'})
                                                                        
Impacto: ${f.value < 1 ? `reduz ${((1 - f.value) * 100).toFixed(1)}%` : f.value > 1 ? `aumenta ${((f.value - 1) * 100).toFixed(1)}%` : 'neutro (1.0 = sem impacto)'}

${f.source === 'auto' ? '✅ Este valor foi ajustado automaticamente pelo sistema baseado em erros reais das previsions.' : '⚙️ Este é o valor padrão inicial. Será calibrado automaticamente quando houver dados suficientes.'}

${f.change_24h !== 0 ? `📊 Mudança nas últimas 24h: ${(f.change_24h * 100).toFixed(1)}% (última calibração automática)` : ''}

Confiança: ${f.confidence}% (baseado em ${f.samples} amostras)
${f.updated_at ? `Última atualização: ${new Date(f.updated_at).toLocaleString('pt-BR')}` : ''}`}
                                                                    >
                                                                        {f.value === 1.0 ? '0.0%' :
                                                                            f.value > 1 ? `+${((f.value - 1) * 100).toFixed(1)}%` :
                                                                                `${((f.value - 1) * 100).toFixed(1)}%`}
                                                                        <span className="text-xs text-slate-500 ml-2 font-normal opacity-60">
                                                                            ({f.value.toFixed(3)})
                                                                        </span>
                                                                    </span>
                                                                    <button
                                                                        onClick={() => {
                                                                            setEditingFactor(factorKey);
                                                                            setEditValue(f.value.toFixed(3));
                                                                        }}
                                                                        className="p-1 text-slate-400 hover:text-white cursor-pointer"
                                                                        title="Clique para editar manualmente este multiplicador"
                                                                    >
                                                                        <Edit2 className="w-4 h-4" />
                                                                    </button>
                                                                </>
                                                            )}
                                                        </div>
                                                    </div>
                                                );
                                            })}


                                            {/* Add New Factor Row */}
                                            <div className="px-4 py-3 bg-slate-900/30 border-t border-slate-800/50 flex items-center justify-between">
                                                <div className="flex-1 max-w-md">
                                                    <div className="flex items-center gap-2">
                                                        <span className="text-xs text-slate-500 font-bold uppercase w-16">Novo Fator:</span>
                                                        <div className="flex-1 flex items-center gap-2">
                                                            <span className="text-slate-400 font-mono text-sm">{type}.</span>
                                                            <input
                                                                type="text"
                                                                placeholder="ex: new_key"
                                                                className="flex-1 bg-slate-800 border border-slate-700 rounded px-2 py-1 text-white text-sm font-mono placeholder-slate-600 focus:outline-none focus:border-purple-500 transition-colors"
                                                                value={newFactorInputs[type] || ''}
                                                                onChange={(e) => setNewFactorInputs(prev => ({
                                                                    ...prev,
                                                                    [type]: e.target.value.replace(/\s/g, '_').toLowerCase()
                                                                }))}
                                                                onKeyDown={(e) => {
                                                                    if (e.key === 'Enter') handleAddFactor(type);
                                                                }}
                                                            />
                                                        </div>
                                                    </div>
                                                </div>
                                                <button
                                                    onClick={() => handleAddFactor(type)}
                                                    disabled={!newFactorInputs[type] || isAddingFactor === type}
                                                    className="ml-4 px-3 py-1 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 disabled:text-slate-500 text-white text-xs font-medium rounded transition-colors flex items-center gap-1 cursor-pointer"
                                                >
                                                    {isAddingFactor === type ? (
                                                        <RefreshCw className="w-3 h-3 animate-spin" />
                                                    ) : (
                                                        <Check className="w-3 h-3" />
                                                    )}
                                                    Adicionar
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Events Section */}
            {activeSection === 'events' && (
                <EventsManager />
            )}
        </div>
    );
}
