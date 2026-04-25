"use client";

import { Ad } from "@/types";
import { ArrowUpDown, ArrowUp, ArrowDown, Power, PauseCircle, AlertCircle, ShoppingCart } from "lucide-react";
import Link from "next/link";
import { Tooltip } from "@/components/ui/Tooltip";

interface Props {
    ads: Ad[];
    sort: string;
    sortOrder: string;
    onSort: (field: string) => void;
    loading: boolean;
    onAdSelect: (id: string) => void;
}

export function AdTable({ ads, sort, sortOrder, onSort, loading, onAdSelect }: Props) {
    if (loading) {
        return (
            <div className="w-full h-64 flex items-center justify-center text-slate-500">
                <div className="flex flex-col items-center gap-2">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-cyan-500"></div>
                    <span>Carregando dados...</span>
                </div>
            </div>
        );
    }

    if (ads.length === 0) {
        return <div className="p-8 text-center text-slate-500">Nenhum anúncio encontrado.</div>;
    }

    const SortIcon = ({ column }: { column: string }) => {
        if (sort !== column) return <ArrowUpDown size={14} className="text-slate-600 opacity-50" />;
        return sortOrder === 'asc'
            ? <ArrowUp size={14} className="text-white" />
            : <ArrowDown size={14} className="text-white" />;
    };

    const formatCurrency = (val: number) =>
        new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);

    return (<div className="w-full overflow-hidden">
        <div className="overflow-x-auto scroller-premium">
            <table className="w-full text-left border-separate border-spacing-y-1">
                <thead>
                    <tr className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                        <th className="px-3 py-2 text-left">Anúncio / SKU</th>
                        <th className="px-3 py-2 text-center cursor-pointer hover:text-slate-300 transition-colors" onClick={() => onSort('status')}>
                            <div className="flex items-center justify-center gap-1">Status <SortIcon column="status" /></div>
                        </th>
                        <th className="px-3 py-2 text-center">Tipo</th>
                        <th className="px-3 py-2 text-center">Logística</th>
                        <th className="px-3 py-2 text-center cursor-pointer hover:text-slate-300 transition-colors" onClick={() => onSort('available_quantity')}>
                            <div className="flex items-center justify-center gap-1">Estoque <SortIcon column="available_quantity" /></div>
                        </th>
                        <th className="px-3 py-2 text-right cursor-pointer hover:text-slate-300 transition-colors" onClick={() => onSort('price')}>
                            <div className="flex items-center justify-end gap-1">Preço <SortIcon column="price" /></div>
                        </th>
                        <th className="px-3 py-2 text-center cursor-pointer hover:text-slate-300 transition-colors" onClick={() => onSort('sold_quantity')}>
                            <div className="flex items-center justify-center gap-1">Vendas <SortIcon column="sold_quantity" /></div>
                        </th>
                        <th className="px-3 py-2 text-center cursor-pointer hover:text-slate-300 transition-colors" onClick={() => onSort('total_visits')}>
                            <div className="flex items-center justify-center gap-1">Visitas <SortIcon column="total_visits" /></div>
                        </th>
                        <th className="px-3 py-2 text-center">Conv.</th>
                        <th className="px-3 py-2 text-center cursor-pointer hover:text-slate-300 transition-colors" onClick={() => onSort('margin_percent')}>
                            <div className="flex items-center justify-center gap-1">Margem <SortIcon column="margin_percent" /></div>
                        </th>
                    </tr>
                </thead>
                <tbody className="space-y-1">
                    {ads.map((ad, index) => {


                        // Stock Logic
                        const stock = ad.available_quantity || 0;
                        const incoming = ad.stock_incoming || 0;
                        const isStockOut = stock === 0;
                        const isLowStock = stock < 5 && stock > 0;
                        const isIncoming = incoming > 0;

                        // Calculate conversion based on displayed totals for consistency
                        const conversion = ad.total_visits ? (ad.sold_quantity / ad.total_visits) * 100 : 0;

                        return (
                            <tr
                                key={ad.id}
                                className="group hover:bg-white/[0.02] transition-colors relative"
                            >
                                {/* ANÚNCIO */}
                                <td className="px-3 py-2 border-t border-b border-white/[0.03] first:border-l first:rounded-l-md last:border-r last:rounded-r-md group-hover:border-white/[0.08] transition-all bg-[#13141b]/50 group-hover:bg-[#1A1A23]">
                                    <div
                                        onClick={() => onAdSelect(ad.id)}
                                        className="flex items-center gap-3 group/link cursor-pointer"
                                    >
                                        <div className="relative w-9 h-9 shrink-0 rounded overflow-hidden border border-white/10 group-hover/link:border-blue-500/50 transition-all bg-white p-0.5">
                                            <img src={ad.thumbnail} alt="" className="w-full h-full object-contain" />
                                        </div>
                                        <div className="min-w-0 flex flex-col justify-center">
                                            <p className="font-medium text-xs truncate text-slate-200 group-hover/link:text-blue-400 transition-colors max-w-[220px]" title={ad.title}>
                                                {ad.title}
                                            </p>
                                            <div className="flex items-center gap-2">
                                                <span className="text-[9px] text-slate-500 font-mono bg-white/5 px-1 py-px rounded border border-white/5 group-hover/link:border-white/10 transition-colors">
                                                    {ad.id}
                                                </span>
                                                {ad.sku && (
                                                    <span className="text-[9px] text-emerald-500/80 font-mono font-bold tracking-wide flex items-center gap-1">
                                                        <span className="w-0.5 h-0.5 rounded-full bg-emerald-500/50"></span>
                                                        {ad.sku}
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </td>

                                {/* STATUS */}
                                <td className="px-3 py-2 border-t border-b border-white/[0.03] group-hover:border-white/[0.08] transition-all bg-[#13141b]/50 group-hover:bg-[#1A1A23] text-center">
                                    {ad.status === 'active' ? (
                                        <div className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 shadow-[0_0_8px_rgba(16,185,129,0.15)]" title="Ativo">
                                            <Power size={12} />
                                        </div>
                                    ) : (
                                        <div className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-slate-500/10 text-slate-500 border border-slate-500/20" title="Pausado">
                                            <PauseCircle size={12} />
                                        </div>
                                    )}
                                </td>

                                {/* TIPO */}
                                <td className="px-3 py-2 border-t border-b border-white/[0.03] group-hover:border-white/[0.08] transition-all bg-[#13141b]/50 group-hover:bg-[#1A1A23] text-center">
                                    {ad.listing_type_id === 'gold_pro' ? (
                                        <span className="text-[9px] font-bold text-amber-400 bg-amber-400/10 px-1 py-px rounded border border-amber-400/20 uppercase">Premium</span>
                                    ) : ad.listing_type_id === 'gold_special' ? (
                                        <span className="text-[9px] font-bold text-slate-400 bg-slate-400/10 px-1 py-px rounded border border-slate-400/20 uppercase">Clássico</span>
                                    ) : (
                                        <span className="text-[9px] text-slate-500 uppercase">{ad.listing_type_id || '-'}</span>
                                    )}
                                </td>

                                {/* LOGÍSTICA */}
                                <td className="px-3 py-2 border-t border-b border-white/[0.03] group-hover:border-white/[0.08] transition-all bg-[#13141b]/50 group-hover:bg-[#1A1A23] text-center">
                                    {ad.is_full ? (
                                        <div className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-[#00A650]/10 text-[#00A650] border border-[#00A650]/20">
                                            <span className="text-[9px] font-black italic uppercase tracking-tighter leading-none">FULL</span>
                                        </div>
                                    ) : ad.shipping_mode === 'me2' ? (
                                        <span className="text-slate-500 text-[10px] font-medium" title="Mercado Envios">Envios</span>
                                    ) : (
                                        <span className="text-slate-600 text-[10px]">-</span>
                                    )}
                                </td>

                                {/* ESTOQUE */}
                                <td className="px-3 py-2 border-t border-b border-white/[0.03] group-hover:border-white/[0.08] transition-all bg-[#13141b]/50 group-hover:bg-[#1A1A23] text-center">
                                    <div className="flex flex-col items-center">
                                        <span className={`text-xs font-bold ${isStockOut && isIncoming ? 'text-blue-500' :
                                            isStockOut ? 'text-rose-500' :
                                                isLowStock ? 'text-amber-500' :
                                                    'text-slate-200'}`}>
                                            {stock}
                                        </span>
                                        {isStockOut && !isIncoming && <span className="text-[8px] text-rose-500 font-bold uppercase tracking-wide leading-none mt-0.5">Esgotado</span>}
                                        {isIncoming && <span className="text-[8px] text-blue-400 font-bold uppercase tracking-wide leading-none mt-0.5">Transferência ({incoming})</span>}
                                        {isLowStock && !isIncoming && <span className="text-[8px] text-amber-500 font-bold uppercase tracking-wide leading-none mt-0.5">Baixo</span>}
                                    </div>
                                </td>

                                {/* PREÇO */}
                                <td className="px-3 py-2 border-t border-b border-white/[0.03] group-hover:border-white/[0.08] transition-all bg-[#13141b]/50 group-hover:bg-[#1A1A23] text-right">
                                    {ad.promotion_price && ad.promotion_price < (ad.price || 0) ? (
                                        <div className="flex flex-col items-end">
                                            <span className="text-[10px] text-slate-500 line-through">{formatCurrency(ad.price || 0)}</span>
                                            <span className="font-mono text-emerald-400 text-xs font-bold tracking-tight">{formatCurrency(ad.promotion_price)}</span>
                                        </div>
                                    ) : (
                                        <span className="font-mono text-slate-300 text-xs font-medium tracking-tight">{formatCurrency(ad.price || 0)}</span>
                                    )}
                                </td>

                                {/* VENDAS */}
                                <td className="px-3 py-2 border-t border-b border-white/[0.03] group-hover:border-white/[0.08] transition-all bg-[#13141b]/50 group-hover:bg-[#1A1A23] text-center">
                                    <span className={`text-xs font-bold ${(ad.sold_quantity || 0) > 0 ? 'text-white' : 'text-slate-600'}`}>{ad.sold_quantity || 0}</span>
                                </td>

                                {/* VISITAS */}
                                <td className="px-3 py-2 border-t border-b border-white/[0.03] group-hover:border-white/[0.08] transition-all bg-[#13141b]/50 group-hover:bg-[#1A1A23] text-center">
                                    <span className="text-[10px] font-mono text-slate-500">{ad.total_visits}</span>
                                </td>

                                {/* CONVERSÃO */}
                                <td className="px-3 py-2 border-t border-b border-white/[0.03] group-hover:border-white/[0.08] transition-all bg-[#13141b]/50 group-hover:bg-[#1A1A23] text-center">
                                    <span className={`text-[9px] font-black px-1.5 py-0.5 rounded uppercase tracking-tight ${conversion > 2 ? 'text-emerald-400 bg-emerald-400/10' :
                                        conversion > 1 ? 'text-yellow-400 bg-yellow-400/10' : 'text-slate-500'
                                        }`}>
                                        {conversion.toFixed(1)}%
                                    </span>
                                </td>

                                {/* MARGEM */}
                                <td className="px-3 py-2 border-t border-b border-white/[0.03] first:border-l last:border-r group-hover:border-white/[0.08] transition-all bg-[#13141b]/50 group-hover:bg-[#1A1A23] text-center rounded-r-md">
                                    {(ad.margin_percent !== undefined && ad.margin_percent !== null) ? (() => {
                                        const target = (ad.target_margin || 0.15) * 100;
                                        const isBelowTarget = ad.margin_percent < target;
                                        const isCritical = ad.margin_percent < 5;

                                        return (
                                            <Tooltip
                                                position="left"
                                                title="Raio-X da Margem"
                                                content={
                                                    <div className="space-y-2 w-80">
                                                        {/* Header: Meta & Sugestão */}
                                                        <div className="pb-2 border-b border-slate-700/50 space-y-1">
                                                            <div className="flex justify-between items-center text-[10px]">
                                                                <span className="text-slate-400">Meta Global:</span>
                                                                <span className="text-slate-200 font-bold">{target.toFixed(0)}%</span>
                                                            </div>
                                                            {ad.suggested_price && ad.suggested_price > 0 && isBelowTarget && (
                                                                <div className="flex justify-between items-center text-[10px] bg-blue-500/10 p-1 rounded">
                                                                    <span className="text-blue-400">Preço Sugerido:</span>
                                                                    <span className="text-blue-300 font-bold">{formatCurrency(ad.suggested_price)}</span>
                                                                </div>
                                                            )}
                                                        </div>

                                                        {/* Breakdown de Custos */}
                                                        <div className="space-y-1">
                                                            <div className="flex justify-between text-slate-400 text-[10px]">
                                                                <span>Venda:</span>
                                                                <span className="text-white font-medium">{formatCurrency(ad.price)}</span>
                                                            </div>

                                                            <div className="flex justify-between text-rose-400 text-[10px]">
                                                                <span>Produto:</span>
                                                                <div className="flex gap-1">
                                                                    <span>-{formatCurrency(ad.cost || 0)}</span>
                                                                    <span className="text-slate-600">({ad.price ? ((ad.cost! / ad.price) * 100).toFixed(0) : 0}%)</span>
                                                                </div>
                                                            </div>

                                                            <div className="flex justify-between text-rose-400 text-[10px]">
                                                                <span>Imposto:</span>
                                                                <div className="flex gap-1">
                                                                    <span>-{formatCurrency(ad.tax_cost || 0)}</span>
                                                                    <span className="text-slate-600">({ad.price ? ((ad.tax_cost! / ad.price) * 100).toFixed(0) : 0}%)</span>
                                                                </div>
                                                            </div>

                                                            <div className="flex justify-between text-rose-400 text-[10px]">
                                                                <span>Comissão:</span>
                                                                <div className="flex gap-1">
                                                                    <span>-{formatCurrency(ad.commission_cost || 0)}</span>
                                                                    <span className="text-slate-600">({ad.price ? ((ad.commission_cost! / ad.price) * 100).toFixed(0) : 0}%)</span>
                                                                </div>
                                                            </div>

                                                            <div className="flex justify-between text-rose-400 text-[10px]">
                                                                <span>Frete:</span>
                                                                <div className="flex gap-1">
                                                                    <span>-{formatCurrency(ad.shipping_cost || 0)}</span>
                                                                    <span className="text-slate-600">({ad.price ? ((ad.shipping_cost! / ad.price) * 100).toFixed(0) : 0}%)</span>
                                                                </div>
                                                            </div>

                                                            <div className="flex justify-between text-rose-400 text-[10px]">
                                                                <span>Rateio Fixo:</span>
                                                                <div className="flex gap-1">
                                                                    <span>-{formatCurrency(ad.fixed_cost_share || 0)}</span>
                                                                    <span className="text-slate-600">({ad.price ? (((ad.fixed_cost_share || 0) / ad.price) * 100).toFixed(1) : 0}%)</span>
                                                                </div>
                                                            </div>

                                                            <div className="flex justify-between text-rose-400 text-[10px]">
                                                                <span>Risco Dev.:</span>
                                                                <div className="flex gap-1">
                                                                    <span>-{formatCurrency(ad.return_risk_cost || 0)}</span>
                                                                    <span className="text-slate-600">
                                                                        {(() => {
                                                                            const pct = ad.price ? ((ad.return_risk_cost || 0) / ad.price) * 100 : 0;
                                                                            return pct < 0.1 ? pct.toFixed(2) : pct.toFixed(1);
                                                                        })()}%
                                                                    </span>
                                                                </div>
                                                            </div>

                                                            {(() => {
                                                                // Use robust values 
                                                                const inboundCost = ad.inbound_freight_cost || ad.financials?.inbound_freight_cost || 0;
                                                                const totalStorage = ad.storage_cost || ad.financials?.storage_cost || 0;

                                                                // Calculate Time Cost (Daily * Days) as residual
                                                                const timeCost = Math.max(0, totalStorage - inboundCost);

                                                                // Always show storage section

                                                                const totalPct = ad.price ? (totalStorage / ad.price) * 100 : 0;
                                                                const inboundPct = ad.price ? (inboundCost / ad.price) * 100 : 0;
                                                                const timePct = ad.price ? (timeCost / ad.price) * 100 : 0;

                                                                return (
                                                                    <div className="space-y-0.5">
                                                                        {/* Parent: Total Storage */}
                                                                        <div className="flex justify-between text-rose-400 text-[10px]">
                                                                            <span>Armazenagem:</span>
                                                                            <div className="flex gap-1">
                                                                                <span>-{formatCurrency(totalStorage)}</span>
                                                                                <span className="text-slate-600">
                                                                                    {totalPct < 0.1 ? totalPct.toFixed(2) : totalPct.toFixed(1)}%
                                                                                </span>
                                                                            </div>
                                                                        </div>

                                                                        {/* Children: Breakdown (Indented) */}
                                                                        <div className="pl-2 border-l border-white/5 ml-0.5 space-y-0.5">
                                                                            <div className="flex justify-between text-slate-500 text-[9px]">
                                                                                <span>↳ Envio Full:</span>
                                                                                <div className="flex gap-1">
                                                                                    <span>-{formatCurrency(inboundCost)}</span>
                                                                                    <span className="text-slate-700">
                                                                                        {inboundPct < 0.1 ? inboundPct.toFixed(2) : inboundPct.toFixed(1)}%
                                                                                    </span>
                                                                                </div>
                                                                            </div>
                                                                            <div className="flex justify-between text-slate-500 text-[9px]">
                                                                                <span>↳ Diária (Est.):</span>
                                                                                <div className="flex gap-1">
                                                                                    <span>-{formatCurrency(timeCost)}</span>
                                                                                    <span className="text-slate-700">
                                                                                        {timePct < 0.1 ? timePct.toFixed(2) : timePct.toFixed(1)}%
                                                                                    </span>
                                                                                </div>
                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                );
                                                            })()}
                                                        </div>

                                                        {/* Resultado Final */}
                                                        {(() => {
                                                            const margin = Number(ad.margin_percent);
                                                            const colorClass = margin < 5 ? 'text-rose-500' : margin < 10 ? 'text-orange-400' : margin <= 15 ? 'text-yellow-400' : margin <= 20 ? 'text-emerald-400' : 'text-emerald-600';
                                                            return (
                                                                <div className={`border-t border-slate-700/50 pt-2 flex justify-between items-center font-bold text-[11px] ${colorClass}`}>
                                                                    <span>Margem Líq:</span>
                                                                    <div className="flex flex-col items-end">
                                                                        <span>{formatCurrency(ad.margin_value || 0)}</span>
                                                                        <span className="text-[9px] opacity-80">{margin.toFixed(1)}%</span>
                                                                    </div>
                                                                </div>
                                                            );
                                                        })()}
                                                    </div>
                                                }
                                            >
                                                <div className="flex flex-col items-center cursor-help group/margin">
                                                    <span className={`font-black text-xs transition-all ${(() => {
                                                        const margin = Number(ad.margin_percent);
                                                        if (margin < 5) return 'text-rose-500 animate-pulse';
                                                        if (margin < 10) return 'text-orange-400';
                                                        if (margin <= 15) return 'text-yellow-400';
                                                        if (margin <= 20) return 'text-emerald-400';
                                                        return 'text-emerald-600';
                                                    })()}`}>
                                                        {Number(ad.margin_percent).toFixed(0)}%
                                                    </span>
                                                    <div className="h-0.5 w-6 bg-slate-800 rounded-full mt-1 overflow-hidden">
                                                        <div
                                                            className={`h-full transition-all duration-500 ${(() => {
                                                                const margin = Number(ad.margin_percent);
                                                                if (margin < 5) return 'bg-rose-500';
                                                                if (margin < 10) return 'bg-orange-400';
                                                                if (margin <= 15) return 'bg-yellow-400';
                                                                if (margin <= 20) return 'bg-emerald-400';
                                                                return 'bg-emerald-600';
                                                            })()}`}
                                                            style={{ width: `${Math.min(ad.margin_percent, 100)}%` }}
                                                        />
                                                    </div>
                                                    {(ad.margin_value !== undefined && ad.margin_value !== null) && (
                                                        <span className="text-[9px] text-slate-600 group-hover/margin:text-slate-400 transition-colors mt-0.5">
                                                            {formatCurrency(ad.margin_value)}
                                                        </span>
                                                    )}
                                                </div>
                                            </Tooltip>
                                        );
                                    })() : (
                                        <span className="text-[10px] text-slate-700">-</span>
                                    )}
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    </div>
    );
}
