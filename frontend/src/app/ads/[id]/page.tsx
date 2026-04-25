"use client";
import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Ad } from "@/types";
import { ArrowLeft, ExternalLink, Package, Activity, Truck, BarChart3, Info } from "lucide-react";
import { PremiumLoader } from "@/components/ui/PremiumLoader";

export default function AdDetailsPage() {
    const params = useParams();
    const router = useRouter();
    const [ad, setAd] = useState<Ad | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchAd() {
            try {
                const response = await api.get(`/ads/${params.id}`);
                setAd(response.data);
            } catch (error) {
                console.error("Error fetching ad", error);
            } finally {
                setLoading(false);
            }
        }
        if (params.id) fetchAd();
    }, [params.id]);

    if (loading) return <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center"><PremiumLoader /></div>;
    if (!ad) return <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center text-slate-500">Anúncio não encontrado</div>;

    return (
        <div className="min-h-screen bg-[#0a0a0f] text-slate-200 p-8">
            <div className="max-w-5xl mx-auto">
                <button
                    onClick={() => router.back()}
                    className="flex items-center text-slate-500 hover:text-white mb-8 transition-colors group"
                >
                    <ArrowLeft className="w-4 h-4 mr-2 group-hover:-translate-x-1 transition-transform" /> Voltar
                </button>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

                    {/* Left Column: Image & Status (4 cols) */}
                    <div className="lg:col-span-4 space-y-6">
                        {/* Image Card */}
                        <div className="relative group rounded-2xl overflow-hidden border border-white/10 bg-[#13141b] p-2">
                            <div className="absolute inset-0 bg-gradient-to-tr from-blue-500/5 to-purple-500/5 opacity-50 transition-opacity group-hover:opacity-100" />
                            <div className="relative aspect-square rounded-xl overflow-hidden bg-white/5 flex items-center justify-center">
                                <img src={ad.thumbnail.replace('I.jpg', 'O.jpg')} alt={ad.title} className="w-full h-full object-contain mix-blend-normal hover:scale-105 transition-transform duration-500" />
                            </div>
                            <a
                                href={ad.permalink}
                                target="_blank"
                                className="absolute bottom-4 right-4 p-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-all translate-y-2 group-hover:translate-y-0"
                                title="Ver no Mercado Livre"
                            >
                                <ExternalLink size={16} />
                            </a>
                        </div>

                        {/* Status Panel */}
                        <div className="bg-[#13141b] rounded-2xl p-5 border border-white/5 space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-slate-400 font-medium">Status Atual</span>
                                {ad.status === 'active' ? (
                                    <span className="flex items-center gap-1.5 text-emerald-400 text-xs font-bold uppercase bg-emerald-400/10 px-2 py-1 rounded-full border border-emerald-400/20">
                                        <Activity size={12} /> Ativo
                                    </span>
                                ) : (
                                    <span className="flex items-center gap-1.5 text-slate-400 text-xs font-bold uppercase bg-slate-400/10 px-2 py-1 rounded-full border border-slate-400/20">
                                        <Activity size={12} /> Pausado
                                    </span>
                                )}
                            </div>

                            <div className="h-px bg-white/5" />

                            <div className="grid grid-cols-2 gap-3">
                                <div className="bg-white/5 rounded-xl p-3 border border-white/5">
                                    <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold block mb-1">Estoque</span>
                                    <div className="flex items-center gap-2">
                                        <Package size={16} className={ad.available_quantity > 0 ? "text-blue-400" : "text-rose-400"} />
                                        <span className="text-xl font-bold text-white">{ad.available_quantity}</span>
                                    </div>
                                </div>
                                <div className="bg-white/5 rounded-xl p-3 border border-white/5">
                                    <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold block mb-1">Logística</span>
                                    <div className="flex items-center gap-2">
                                        <Truck size={16} className="text-purple-400" />
                                        <span className="text-sm font-bold text-white capitalize">{ad.shipping_mode === 'me2' ? 'Envios' : 'Próprio'}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Right Column: Details & Analytics (8 cols) */}
                    <div className="lg:col-span-8 space-y-6">

                        {/* Header Info */}
                        <div>
                            <div className="flex items-center gap-3 mb-2">
                                <h1 className="text-2xl font-bold text-white leading-tight">{ad.title}</h1>
                                {ad.sku && (
                                    <span className="px-2 py-1 rounded bg-slate-800 border border-slate-700 text-xs font-mono text-slate-300">
                                        SKU: {ad.sku}
                                    </span>
                                )}
                            </div>
                            <p className="text-slate-500 text-sm">Atualizado em {ad.updated_at ? new Date(ad.updated_at).toLocaleString('pt-BR') : 'Recentemente'}</p>
                        </div>

                        {/* Key Metrics Grid */}
                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                            <div className="bg-[#13141b] p-4 rounded-2xl border border-white/5 relative overflow-hidden group">
                                <div className="absolute top-0 right-0 w-16 h-16 bg-emerald-500/10 rounded-full blur-2xl -mr-8 -mt-8 group-hover:bg-emerald-500/20 transition-all" />
                                <p className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-1">Preço Venda</p>
                                <p className="text-2xl font-bold text-white">R$ {ad.price.toFixed(2)}</p>
                            </div>
                            <div className="bg-[#13141b] p-4 rounded-2xl border border-white/5 relative overflow-hidden group">
                                <p className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-1">Vendas (30d)</p>
                                <p className="text-2xl font-bold text-white flex items-end gap-2">
                                    {ad.sales_30d}
                                    {(ad.sales_7d_change || 0) !== 0 && (
                                        <span className={`text-xs mb-1 font-bold ${(ad.sales_7d_change || 0) > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                            {(ad.sales_7d_change || 0) > 0 ? '+' : ''}{ad.sales_7d_change}%
                                        </span>
                                    )}
                                </p>
                            </div>
                            <div className="bg-[#13141b] p-4 rounded-2xl border border-white/5 relative overflow-hidden group">
                                <p className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-1">Visitas</p>
                                <p className="text-2xl font-bold text-white">{ad.total_visits}</p>
                            </div>
                            <div className="bg-[#13141b] p-4 rounded-2xl border border-white/5 relative overflow-hidden group">
                                <div className="absolute top-0 right-0 w-16 h-16 bg-purple-500/10 rounded-full blur-2xl -mr-8 -mt-8 group-hover:bg-purple-500/20 transition-all" />
                                <p className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-1">Margem</p>
                                <p className={`text-2xl font-bold ${(ad.margin_percent || 0) < 20 ? 'text-rose-400' : 'text-emerald-400'}`}>
                                    {(ad.margin_percent || 0).toFixed(0)}%
                                </p>
                            </div>
                        </div>

                        {/* Financial Breakdown Card */}
                        <div className="bg-[#13141b] rounded-2xl border border-white/5 overflow-hidden">
                            <div className="px-6 py-4 border-b border-white/5 flex items-center gap-2 bg-white/[0.02]">
                                <BarChart3 size={18} className="text-blue-400" />
                                <h3 className="font-bold text-white text-sm uppercase tracking-wide">Raio-X Financeiro</h3>
                            </div>
                            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-12">
                                <div className="space-y-3">
                                    <div className="flex justify-between items-center text-sm">
                                        <span className="text-slate-400">Preço Bruto</span>
                                        <span className="text-white font-mono font-medium">R$ {ad.price.toFixed(2)}</span>
                                    </div>
                                    <div className="h-px bg-white/5 my-2" />
                                    <div className="flex justify-between items-center text-sm text-rose-400/80">
                                        <span className="flex items-center gap-1.5"><Info size={12} /> Custo Produto</span>
                                        <span className="font-mono">- R$ {ad.cost?.toFixed(2) || '0.00'}</span>
                                    </div>
                                    <div className="flex justify-between items-center text-sm text-rose-400/80">
                                        <span className="flex items-center gap-1.5"><Info size={12} /> Taxa ML</span>
                                        <span className="font-mono">- R$ {ad.financials?.commission_cost.toFixed(2) || '0.00'}</span>
                                    </div>
                                    <div className="flex justify-between items-center text-sm text-rose-400/80">
                                        <span className="flex items-center gap-1.5"><Info size={12} /> Impostos (4%)</span>
                                        <span className="font-mono">- R$ {ad.financials?.tax_cost.toFixed(2) || '0.00'}</span>
                                    </div>
                                    <div className="flex justify-between items-center text-sm text-rose-400/80">
                                        <span className="flex items-center gap-1.5"><Info size={12} /> Frete</span>
                                        <span className="font-mono">- R$ {ad.financials?.shipping_cost.toFixed(2) || '0.00'}</span>
                                    </div>
                                </div>

                                <div className="flex flex-col justify-center items-center bg-white/[0.02] rounded-xl border border-white/5 p-6 relative">
                                    <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent opacity-50" />
                                    <span className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-2">Lucro Líquido</span>
                                    <span className="text-4xl font-black text-white tracking-tight mb-1">
                                        R$ {ad.margin_value?.toFixed(2) || '0.00'}
                                    </span>
                                    <span className={`text-sm font-bold px-2 py-0.5 rounded-full border ${(ad.margin_percent || 0) < 20
                                        ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                                        : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                                        }`}>
                                        Margem: {(ad.margin_percent || 0).toFixed(1)}%
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* Conversion Bar */}
                        <div className="bg-[#13141b] rounded-2xl border border-white/5 p-6">
                            <div className="flex justify-between items-end mb-2">
                                <div className="flex flex-col">
                                    <span className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Taxa de Conversão</span>
                                    <span className="text-2xl font-bold text-white">
                                        {ad.total_visits > 0 ? ((ad.sold_quantity / ad.total_visits) * 100).toFixed(2) : 0}%
                                    </span>
                                </div>
                                <span className="text-xs text-slate-400">Meta: 1.5%</span>
                            </div>
                            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-blue-600 to-cyan-400 rounded-full"
                                    style={{ width: `${Math.min(((ad.sold_quantity / (ad.total_visits || 1)) * 100) * 10, 100)}%` }}
                                />
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    );
}
