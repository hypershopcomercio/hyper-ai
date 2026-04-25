"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import {
    ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend,
    LineChart, Line, ComposedChart, Area, CartesianGrid
} from 'recharts';
import {
    Wallet, TrendingUp, TrendingDown, DollarSign,
    Calendar, AlertTriangle, ArrowRight, PieChart
} from 'lucide-react';

interface OTBData {
    otb_value: number;
    projected_sales_value: number;
    projected_cogs: number;
    target_ending_inventory: number;
    current_inventory_value: number;
    on_order_value: number;
}

interface CashFlowItem {
    date: string;
    inflow: number;
    outflow: number;
    accumulated: number;
    details: any[];
}

export default function FinancialPage() {
    const [otbData, setOtbData] = useState<OTBData | null>(null);
    const [cashFlowData, setCashFlowData] = useState<CashFlowItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [period, setPeriod] = useState(30);

    useEffect(() => {
        loadData();
    }, [period]);

    const loadData = async () => {
        setLoading(true);
        try {
            const [otbRes, flowRes] = await Promise.all([
                api.get(`/financial/otb?days=${period}`),
                api.get(`/financial/cash-flow?days=${period}`)
            ]);
            setOtbData(otbRes.data);
            setCashFlowData(flowRes.data);
        } catch (error) {
            console.error("Error loading financial data", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="p-8 text-white">Carregando inteligência financeira...</div>;
    }

    return (
        <div className="min-h-screen bg-[#09090b] text-slate-100 p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                        <Wallet className="text-emerald-500" />
                        Inteligência Financeira
                    </h1>
                    <p className="text-slate-400 mt-1">Gestão de OTB (Open-to-Buy) e Fluxo de Caixa Projetado</p>
                </div>
                <div className="flex bg-slate-800/50 rounded-lg p-1 border border-white/5">
                    {[30, 60, 90].map(d => (
                        <button
                            key={d}
                            onClick={() => setPeriod(d)}
                            className={`px-4 py-1.5 rounded-md text-xs font-bold transition-all ${period === d ? 'bg-emerald-500 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
                        >
                            {d} dias
                        </button>
                    ))}
                </div>
            </div>

            {/* OTB Summary Cards */}
            {otbData && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    {/* OTB Main Card */}
                    <div className="col-span-1 md:col-span-2 bg-[#121217] border border-white/5 rounded-2xl p-6 relative overflow-hidden group hover:border-emerald-500/30 transition-colors">
                        <div className="absolute top-0 right-0 p-32 bg-emerald-500/5 rounded-full blur-3xl group-hover:bg-emerald-500/10 transition-all"></div>
                        <div className="relative z-10">
                            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-2 flex items-center gap-2">
                                <DollarSign size={16} /> Open-to-Buy (OTB)
                            </h3>
                            <div className="text-4xl font-black text-white font-mono tracking-tight">
                                {otbData.otb_value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                            </div>
                            <p className="text-emerald-400 text-xs font-medium mt-2 flex items-center gap-1">
                                <TrendingUp size={14} />
                                Verba disponível para compra imediata
                            </p>

                            <div className="grid grid-cols-2 gap-4 mt-6 pt-6 border-t border-white/5">
                                <div>
                                    <span className="text-[10px] text-slate-500 uppercase block">Vendas Previstas (Custo)</span>
                                    <span className="text-sm font-bold text-white font-mono">
                                        {otbData.projected_cogs.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                    </span>
                                </div>
                                <div>
                                    <span className="text-[10px] text-slate-500 uppercase block">Estoque Final Meta</span>
                                    <span className="text-sm font-bold text-white font-mono">
                                        {otbData.target_ending_inventory.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Pending Orders Card */}
                    <div className="bg-[#121217] border border-white/5 rounded-2xl p-6 hover:border-white/10 transition-colors">
                        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                            <Calendar size={14} /> Pedidos em Aberto
                        </h3>
                        <div className="text-2xl font-bold text-white font-mono">
                            {otbData.on_order_value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </div>
                        <p className="text-slate-400 text-xs mt-2">Comprometido no orçamento</p>
                    </div>

                    {/* Stock Value Card */}
                    <div className="bg-[#121217] border border-white/5 rounded-2xl p-6 hover:border-white/10 transition-colors">
                        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                            <PieChart size={14} /> Estoque Atual
                        </h3>
                        <div className="text-2xl font-bold text-white font-mono">
                            {otbData.current_inventory_value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </div>
                        <p className="text-slate-400 text-xs mt-2">Valuation (Custo)</p>
                    </div>
                </div>
            )}

            {/* Cash Flow Chart */}
            <div className="bg-[#121217] border border-white/5 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h2 className="text-lg font-bold text-white">Fluxo de Caixa Projetado</h2>
                        <p className="text-xs text-slate-400">Projeção diária baseada em Previsão de Vendas vs Contas a Pagar</p>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 text-xs">
                            <div className="w-3 h-3 rounded-full bg-emerald-500"></div> Entrada
                        </div>
                        <div className="flex items-center gap-2 text-xs">
                            <div className="w-3 h-3 rounded-full bg-rose-500"></div> Saída
                        </div>
                        <div className="flex items-center gap-2 text-xs">
                            <div className="w-3 h-3 rounded-full bg-blue-500"></div> Saldo Acumulado
                        </div>
                    </div>
                </div>

                <div className="h-[400px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart data={cashFlowData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                            <XAxis
                                dataKey="date"
                                tickFormatter={(val) => {
                                    const d = new Date(val);
                                    return `${d.getDate()}/${d.getMonth() + 1}`;
                                }}
                                stroke="#475569"
                                fontSize={10}
                                tickLine={false}
                                axisLine={false}
                                minTickGap={30}
                            />
                            <YAxis
                                yAxisId="left"
                                stroke="#475569"
                                fontSize={10}
                                tickLine={false}
                                axisLine={false}
                                tickFormatter={(val) => `R$ ${val / 1000}k`}
                            />
                            <YAxis
                                yAxisId="right"
                                orientation="right"
                                stroke="#475569"
                                fontSize={10}
                                tickLine={false}
                                axisLine={false}
                                tickFormatter={(val) => `R$ ${val / 1000}k`}
                            />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px' }}
                                itemStyle={{ fontSize: '12px' }}
                                labelStyle={{ color: '#94a3b8', marginBottom: '8px', fontSize: '10px' }}
                                formatter={(value: any) => value?.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                            />
                            <Bar yAxisId="left" dataKey="inflow" fill="#10b981" radius={[4, 4, 0, 0]} barSize={20} />
                            <Bar yAxisId="left" dataKey="outflow" fill="#f43f5e" radius={[4, 4, 0, 0]} barSize={20} />
                            <Line
                                yAxisId="right"
                                type="monotone"
                                dataKey="accumulated"
                                stroke="#3b82f6"
                                strokeWidth={2}
                                dot={false}
                            />
                        </ComposedChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* DRE (Demonstrative) Table Placeholder */}
            <div className="bg-[#121217] border border-white/5 rounded-2xl p-6">
                <h2 className="text-lg font-bold text-white mb-4">DRE Gerencial (Estimativa)</h2>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-white/10 text-slate-500">
                                <th className="text-left py-3 px-4 font-normal">Descrição</th>
                                <th className="text-right py-3 px-4 font-normal">Valor ({period} dias)</th>
                                <th className="text-right py-3 px-4 font-normal">%</th>
                            </tr>
                        </thead>
                        <tbody className="text-slate-300">
                            {/* Receita */}
                            <tr className="border-b border-white/5 hover:bg-white/5">
                                <td className="py-3 px-4 text-white font-bold">Receita Bruta</td>
                                <td className="py-3 px-4 text-right">
                                    {(otbData?.projected_sales_value || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                </td>
                                <td className="py-3 px-4 text-right text-slate-500">100%</td>
                            </tr>

                            {/* Impostos (Simulado) */}
                            <tr className="border-b border-white/5 hover:bg-white/5">
                                <td className="py-3 px-4 pl-8 text-rose-300">(-) Impostos (Est. 10%)</td>
                                <td className="py-3 px-4 text-right text-rose-300">
                                    - {((otbData?.projected_sales_value || 0) * 0.10).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                </td>
                                <td className="py-3 px-4 text-right text-slate-500">10%</td>
                            </tr>

                            {/* CMV */}
                            <tr className="border-b border-white/5 hover:bg-white/5">
                                <td className="py-3 px-4 pl-8 text-rose-300">(-) CMV (Custo Mercadoria)</td>
                                <td className="py-3 px-4 text-right text-rose-300">
                                    - {(otbData?.projected_cogs || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                </td>
                                <td className="py-3 px-4 text-right text-slate-500">
                                    {otbData?.projected_sales_value ? ((otbData.projected_cogs / otbData.projected_sales_value) * 100).toFixed(1) : 0}%
                                </td>
                            </tr>

                            {/* Lucro Bruto */}
                            <tr className="border-b border-white/5 hover:bg-white/5 bg-white/[0.02]">
                                <td className="py-3 px-4 font-bold text-white">(=) Lucro Bruto</td>
                                <td className="py-3 px-4 text-right font-bold text-white">
                                    {(
                                        ((otbData?.projected_sales_value || 0) * 0.90) - (otbData?.projected_cogs || 0)
                                    ).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                </td>
                                <td className="py-3 px-4 text-right text-slate-500">
                                    {otbData?.projected_sales_value ? (((otbData.projected_sales_value * 0.9 - otbData.projected_cogs) / otbData.projected_sales_value) * 100).toFixed(1) : 0}%
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
