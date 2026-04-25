/**
 * Gráfico de Análise de Impacto Competitivo
 * 
 * Mostra duas linhas:
 * - Nossas vendas (azul)
 * - Vendas do concorrente (vermelho)
 * 
 * Com marcadores de eventos críticos
 */

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine, Area, ComposedChart } from 'recharts';
import { TrendingDown, TrendingUp, AlertTriangle } from 'lucide-react';

interface ImpactChartProps {
    adId: string;
    competitorId: string;
}

interface TimelineData {
    timestamp: string;
    competitor_price: number | null;
    competitor_sales: number | null;
    our_sales: number | null;
}

interface ImpactEventMarker {
    timestamp: string;
    type: string;
    diagnosis: string;
    recommendation?: string;
    threat_score: number;
    estimated_sales_lost: number;
}

export function CompetitorImpactChart({ adId, competitorId }: ImpactChartProps) {
    const [data, setData] = useState<any[]>([]);
    const [events, setEvents] = useState<ImpactEventMarker[]>([]);
    const [loading, setLoading] = useState(true);
    const [totalLostSales, setTotalLostSales] = useState(0);

    useEffect(() => {
        loadTimelineData();
    }, [adId, competitorId]);

    const loadTimelineData = async () => {
        setLoading(true);
        try {
            const res = await api.get(`/competitor-intelligence/ads/${adId}/competitors/${competitorId}/timeline?days=30`);

            if (res.data && res.data.metrics) {
                // Processar dados para o gráfico
                const chartData = res.data.metrics.map((m: any) => ({
                    date: new Date(m.timestamp).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
                    timestamp: m.timestamp,
                    nossasVendas: m.our_sales || 0,
                    vendasConcorrente: m.competitor_sales || 0,
                    nossoPreco: m.our_price || 0,
                    precoConcorrente: m.competitor_price || 0
                }));

                setData(chartData);

                // Processar eventos
                if (res.data.events) {
                    setEvents(res.data.events);
                    const totalLost = res.data.events.reduce((sum: number, e: any) => sum + (e.estimated_sales_lost || 0), 0);
                    setTotalLostSales(totalLost);
                }
            }
        } catch (err) {
            console.error('Erro ao carregar timeline:', err);
        } finally {
            setLoading(false);
        }
    };

    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length > 0) {
            // Pegar dados originais do ponto
            const dataPoint = payload[0].payload;

            return (
                <div className="bg-[#13141b] border border-white/10 rounded-lg p-3 shadow-xl">
                    <p className="text-xs text-slate-400 mb-2">{label}</p>
                    <div className="space-y-1">
                        <p className="text-sm text-cyan-400 font-medium">
                            Nossas Vendas: {dataPoint.nossasVendas || 0}
                        </p>
                        <p className="text-sm text-red-400 font-medium">
                            Concorrente: {dataPoint.vendasConcorrente || 0}
                        </p>
                    </div>
                    <div className="mt-2 pt-2 border-t border-white/5">
                        <p className="text-xs text-slate-500">Preços:</p>
                        <p className="text-xs text-slate-400">Nosso: R$ {(dataPoint.nossoPreco || 0).toFixed(2)}</p>
                        <p className="text-xs text-slate-400">Deles: R$ {(dataPoint.precoConcorrente || 0).toFixed(2)}</p>
                    </div>
                </div>
            );
        }
        return null;
    };

    if (loading) {
        return (
            <div className="bg-[#13141b] rounded-xl p-6 border border-white/5">
                <div className="flex items-center justify-center h-64">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
                </div>
            </div>
        );
    }

    if (data.length === 0) {
        return (
            <div className="bg-[#13141b] rounded-xl p-6 border border-white/5">
                <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wide flex items-center gap-2 mb-4">
                    📈 Análise de Impacto
                </h3>
                <div className="text-center py-8 text-slate-500 text-sm">
                    Dados insuficientes para gráfico de impacto.
                    <br />
                    <span className="text-xs">Aguarde a coleta de métricas.</span>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-[#13141b] rounded-xl p-6 border border-white/5 space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wide flex items-center gap-2">
                    📈 Análise de Impacto Competitivo
                </h3>

                {totalLostSales > 0 && (
                    <div className="flex items-center gap-2 bg-red-500/10 px-3 py-1.5 rounded-lg border border-red-500/20">
                        <TrendingDown size={14} className="text-red-400" />
                        <span className="text-xs font-bold text-red-400">
                            {totalLostSales} vendas perdidas
                        </span>
                    </div>
                )}
            </div>

            {/* Eventos Críticos */}
            {events.length > 0 && (
                <div className="bg-[#09090b] rounded-lg p-3 border border-white/5">
                    <p className="text-[10px] text-slate-500 uppercase tracking-wide mb-2">Eventos Detectados</p>
                    <div className="flex flex-wrap gap-2">
                        {events.slice(0, 3).map((event, i) => (
                            <div key={i} className={`px-2 py-1 rounded text-[10px] font-medium ${event.threat_score >= 80 ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                                event.threat_score >= 60 ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                                    'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
                                }`}>
                                {event.type === 'price_drop' ? '💰 Redução de Preço' :
                                    event.type === 'sales_spike' ? '📈 Spike de Vendas' :
                                        event.type}
                                {event.estimated_sales_lost > 0 && ` (-${event.estimated_sales_lost})`}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Gráfico */}
            <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: 0 }}>
                        <defs>
                            <linearGradient id="ourSalesGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                            </linearGradient>
                            <linearGradient id="competitorSalesGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.2} />
                                <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                            </linearGradient>
                        </defs>

                        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />

                        <XAxis
                            dataKey="date"
                            stroke="#64748b"
                            style={{ fontSize: '10px' }}
                            tick={{ fill: '#64748b' }}
                        />

                        <YAxis
                            stroke="#64748b"
                            style={{ fontSize: '10px' }}
                            tick={{ fill: '#64748b' }}
                        />

                        <Tooltip content={<CustomTooltip />} />

                        <Legend
                            wrapperStyle={{ fontSize: '11px' }}
                            iconType="line"
                        />

                        {/* Área de vendas perdidas */}
                        <Area
                            type="monotone"
                            dataKey="nossasVendas"
                            fill="url(#ourSalesGradient)"
                            stroke="none"
                            hide={false}
                            legendType="none"
                        />

                        {/* Linhas principais */}
                        <Line
                            type="monotone"
                            dataKey="nossasVendas"
                            stroke="#06b6d4"
                            strokeWidth={2}
                            dot={{ fill: '#06b6d4', r: 3 }}
                            activeDot={{ r: 5 }}
                            name="Nossas Vendas"
                        />

                        <Line
                            type="monotone"
                            dataKey="vendasConcorrente"
                            stroke="#ef4444"
                            strokeWidth={2}
                            strokeDasharray="5 5"
                            dot={{ fill: '#ef4444', r: 3 }}
                            activeDot={{ r: 5 }}
                            name="Vendas Concorrente"
                        />

                        {/* Marcadores de eventos críticos */}
                        {events.map((event, i) => {
                            const eventDate = new Date(event.timestamp).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
                            return (
                                <ReferenceLine
                                    key={i}
                                    x={eventDate}
                                    stroke="#f59e0b"
                                    strokeDasharray="3 3"
                                    label={{ value: '⚠️', position: 'top', fill: '#f59e0b' }}
                                />
                            );
                        })}
                    </ComposedChart>
                </ResponsiveContainer>
            </div>

            {/* Legenda de Insights */}
            <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="bg-[#09090b] rounded-lg p-3 border border-cyan-500/20">
                    <div className="flex items-center gap-2 mb-1">
                        <div className="w-2 h-2 rounded-full bg-cyan-500"></div>
                        <span className="text-slate-400">Nossas Vendas</span>
                    </div>
                    <p className="text-lg font-bold text-white">
                        {data[data.length - 1]?.nossasVendas || 0}
                    </p>
                    <p className="text-[10px] text-slate-500 mt-1">Última medição</p>
                </div>

                <div className="bg-[#09090b] rounded-lg p-3 border border-red-500/20">
                    <div className="flex items-center gap-2 mb-1">
                        <div className="w-2 h-2 rounded-full bg-red-500"></div>
                        <span className="text-slate-400">Concorrente</span>
                    </div>
                    <p className="text-lg font-bold text-white">
                        {data[data.length - 1]?.vendasConcorrente || 0}
                    </p>
                    <p className="text-[10px] text-slate-500 mt-1">Última medição</p>
                </div>
            </div>

            {/* Plano de Ação / Recomendações */}
            {events.length > 0 && events[0].recommendation && (
                <div className="mt-2 bg-gradient-to-r from-amber-500/10 to-transparent border-l-2 border-amber-500 pl-4 py-2">
                    <h4 className="text-xs font-bold text-amber-500 uppercase flex items-center gap-2 mb-1">
                        <AlertTriangle size={12} />
                        Ação Recomendada
                    </h4>
                    <p className="text-sm text-slate-300 italic">
                        "{events[0].recommendation}"
                    </p>
                    <p className="text-[10px] text-slate-500 mt-1">
                        Diagnóstico: {events[0].diagnosis}
                    </p>
                </div>
            )}
        </div>
    );
}
